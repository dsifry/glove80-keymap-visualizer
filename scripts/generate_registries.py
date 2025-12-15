#!/usr/bin/env python3
"""
Auto-generate service and mock registries from source code.

This script parses Python source files using the AST module to extract
function signatures, class definitions, and docstrings. It then generates
TOON-format registry files for documentation and CI/CD validation.

Usage:
    python scripts/generate_registries.py [--check] [--verbose]

Options:
    --check     Validate registries without writing (exit 1 if invalid)
    --verbose   Print detailed progress information
"""

from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import toon_python
except ImportError:
    print("Error: toon-python package is required. Install with: pip install toon-python")
    sys.exit(1)


@dataclass
class DocstringInfo:
    """Parsed Google-style docstring information.

    Args:
        description: The first line description of the docstring
        args: Dictionary mapping parameter names to their descriptions
        returns: Description of the return value
        raises: List of exceptions that can be raised
    """

    description: str = ""
    args: dict[str, str] = field(default_factory=dict)
    returns: str = ""
    raises: list[str] = field(default_factory=list)


@dataclass
class FunctionInfo:
    """Information about a function or method.

    Args:
        module: Module name where the function is defined
        name: Function name
        signature: Full function signature with types
        description: First line of docstring
        args: Formatted arguments description
        returns: Return value description
        raises: Exceptions that can be raised
        is_private: Whether the function name starts with underscore
        is_method: Whether this is a class method
        class_name: Name of containing class (if method)
    """

    module: str
    name: str
    signature: str
    description: str = ""
    args: str = ""
    returns: str = ""
    raises: str = ""
    is_private: bool = False
    is_method: bool = False
    class_name: str = ""


@dataclass
class ClassInfo:
    """Information about a class definition.

    Args:
        module: Module name where the class is defined
        name: Class name
        description: First line of docstring
        methods: List of method names
        is_private: Whether the class name starts with underscore
    """

    module: str
    name: str
    description: str = ""
    methods: list[str] = field(default_factory=list)
    is_private: bool = False


@dataclass
class ModuleInfo:
    """Information about a module.

    Args:
        name: Module name (e.g., 'cli')
        path: Relative path to the module file
        description: First line of module docstring
    """

    name: str
    path: str
    description: str = ""


@dataclass
class FixtureInfo:
    """Information about a pytest fixture.

    Args:
        name: Fixture name
        description: First line of docstring
        returns: Return type or description
        location: File path where fixture is defined
    """

    name: str
    description: str = ""
    returns: str = ""
    location: str = ""


@dataclass
class FactoryInfo:
    """Information about a mock factory class.

    Args:
        name: Factory class name
        purpose: Description of what the factory mocks
        location: File path where factory is defined
        fixtures: List of fixtures this factory provides
    """

    name: str
    purpose: str = ""
    location: str = ""
    fixtures: list[str] = field(default_factory=list)


@dataclass
class ValidationError:
    """A validation error for registry completeness.

    Args:
        location: File path and line number
        message: Description of the error
        severity: Error severity ('error' or 'warning')
    """

    location: str
    message: str
    severity: str = "error"


def parse_google_docstring(docstring: str | None) -> DocstringInfo:
    """Parse a Google-style docstring into structured components.

    Args:
        docstring: The raw docstring text

    Returns:
        DocstringInfo with parsed sections
    """
    if not docstring:
        return DocstringInfo()

    lines = docstring.strip().split("\n")
    if not lines:
        return DocstringInfo()

    info = DocstringInfo()

    # First line is always the description
    info.description = lines[0].strip()

    # Parse sections
    current_section: str | None = None
    current_content: list[str] = []

    for line in lines[1:]:
        stripped = line.strip()

        # Check for section headers
        if stripped in ("Args:", "Arguments:"):
            if current_section and current_content:
                _process_section(info, current_section, current_content)
            current_section = "args"
            current_content = []
        elif stripped in ("Returns:", "Return:"):
            if current_section and current_content:
                _process_section(info, current_section, current_content)
            current_section = "returns"
            current_content = []
        elif stripped in ("Raises:", "Raise:"):
            if current_section and current_content:
                _process_section(info, current_section, current_content)
            current_section = "raises"
            current_content = []
        elif stripped in ("Example:", "Examples:"):
            if current_section and current_content:
                _process_section(info, current_section, current_content)
            current_section = "example"
            current_content = []
        elif current_section:
            current_content.append(line)

    # Process final section
    if current_section and current_content:
        _process_section(info, current_section, current_content)

    return info


def _process_section(
    info: DocstringInfo,
    section: str,
    content: list[str],
) -> None:
    """Process a docstring section and update info.

    Args:
        info: DocstringInfo to update
        section: Section name ('args', 'returns', 'raises')
        content: Lines of content for this section
    """
    if section == "args":
        # Parse args format: param_name: description
        current_param: str | None = None
        for line in content:
            # Check for new parameter (starts with word followed by colon)
            match = re.match(r"^\s*(\w+):\s*(.*)$", line)
            if match:
                current_param = match.group(1)
                info.args[current_param] = match.group(2).strip()
            elif current_param and line.strip():
                # Continuation of previous parameter
                info.args[current_param] += " " + line.strip()
    elif section == "returns":
        info.returns = " ".join(line.strip() for line in content if line.strip())
    elif section == "raises":
        # Parse raises format: ExceptionType: description
        for line in content:
            match = re.match(r"^\s*(\w+):\s*(.*)$", line)
            if match:
                info.raises.append(f"{match.group(1)}: {match.group(2)}")
            elif line.strip() and info.raises:
                info.raises[-1] += " " + line.strip()


def get_function_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Extract the function signature as a string.

    Args:
        node: AST node for the function definition

    Returns:
        Formatted signature string like '(arg1: type, arg2) -> ReturnType'
    """
    args_parts: list[str] = []

    # Handle positional-only parameters (Python 3.8+)
    posonlyargs = getattr(node.args, "posonlyargs", [])
    for arg in posonlyargs:
        arg_str = arg.arg
        if arg.annotation:
            arg_str += f": {ast.unparse(arg.annotation)}"
        args_parts.append(arg_str)

    if posonlyargs:
        args_parts.append("/")

    # Regular arguments
    num_defaults = len(node.args.defaults)
    num_args = len(node.args.args)

    for i, arg in enumerate(node.args.args):
        arg_str = arg.arg
        if arg.annotation:
            arg_str += f": {ast.unparse(arg.annotation)}"

        # Check if this arg has a default value
        default_idx = i - (num_args - num_defaults)
        if default_idx >= 0:
            default_val = node.args.defaults[default_idx]
            arg_str += f" = {ast.unparse(default_val)}"

        args_parts.append(arg_str)

    # *args
    if node.args.vararg:
        vararg_str = f"*{node.args.vararg.arg}"
        if node.args.vararg.annotation:
            vararg_str += f": {ast.unparse(node.args.vararg.annotation)}"
        args_parts.append(vararg_str)
    elif node.args.kwonlyargs:
        args_parts.append("*")

    # Keyword-only arguments
    for i, arg in enumerate(node.args.kwonlyargs):
        arg_str = arg.arg
        if arg.annotation:
            arg_str += f": {ast.unparse(arg.annotation)}"
        if node.args.kw_defaults[i] is not None:
            arg_str += f" = {ast.unparse(node.args.kw_defaults[i])}"
        args_parts.append(arg_str)

    # **kwargs
    if node.args.kwarg:
        kwarg_str = f"**{node.args.kwarg.arg}"
        if node.args.kwarg.annotation:
            kwarg_str += f": {ast.unparse(node.args.kwarg.annotation)}"
        args_parts.append(kwarg_str)

    signature = f"({', '.join(args_parts)})"

    # Return type
    if node.returns:
        signature += f" -> {ast.unparse(node.returns)}"

    return signature


def parse_module(
    file_path: Path,
    root_dir: Path,
) -> tuple[ModuleInfo, list[FunctionInfo], list[ClassInfo]]:
    """Parse a Python module and extract functions and classes.

    Args:
        file_path: Path to the Python file
        root_dir: Root directory for calculating relative paths

    Returns:
        Tuple of (ModuleInfo, list of FunctionInfo, list of ClassInfo)
    """
    relative_path = file_path.relative_to(root_dir)
    module_name = file_path.stem

    with open(file_path) as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"Warning: Syntax error in {file_path}: {e}")
        return ModuleInfo(module_name, str(relative_path)), [], []

    # Get module docstring
    module_doc = ast.get_docstring(tree) or ""
    module_info = ModuleInfo(
        name=module_name,
        path=str(relative_path),
        description=module_doc.split("\n")[0] if module_doc else "",
    )

    functions: list[FunctionInfo] = []
    classes: list[ClassInfo] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Skip if it's a method (will be processed with class)
            if _is_top_level_function(tree, node):
                func_info = _parse_function(node, module_name)
                functions.append(func_info)

        elif isinstance(node, ast.ClassDef):
            class_info = _parse_class(node, module_name)
            classes.append(class_info)

            # Also add methods as functions
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_info = _parse_function(item, module_name, class_name=node.name)
                    functions.append(method_info)

    return module_info, functions, classes


def _is_top_level_function(
    tree: ast.Module,
    func_node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> bool:
    """Check if a function is at module level (not a method).

    Args:
        tree: The module AST
        func_node: The function node to check

    Returns:
        True if the function is at module level
    """
    for node in tree.body:
        if node is func_node:
            return True
    return False


def _parse_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    module_name: str,
    class_name: str = "",
) -> FunctionInfo:
    """Parse a function definition into FunctionInfo.

    Args:
        node: AST node for the function
        module_name: Name of the containing module
        class_name: Name of containing class if this is a method

    Returns:
        FunctionInfo with parsed details
    """
    docstring = ast.get_docstring(node)
    doc_info = parse_google_docstring(docstring)

    signature = get_function_signature(node)

    # Format args for registry
    args_str = ", ".join(f"{k}: {v}" for k, v in doc_info.args.items()) if doc_info.args else ""

    # Format raises for registry
    raises_str = " | ".join(doc_info.raises) if doc_info.raises else ""

    return FunctionInfo(
        module=module_name,
        name=node.name,
        signature=signature,
        description=doc_info.description,
        args=args_str,
        returns=doc_info.returns,
        raises=raises_str,
        is_private=node.name.startswith("_"),
        is_method=bool(class_name),
        class_name=class_name,
    )


def _parse_class(node: ast.ClassDef, module_name: str) -> ClassInfo:
    """Parse a class definition into ClassInfo.

    Args:
        node: AST node for the class
        module_name: Name of the containing module

    Returns:
        ClassInfo with parsed details
    """
    docstring = ast.get_docstring(node)
    doc_info = parse_google_docstring(docstring)

    methods: list[str] = []
    for item in node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            methods.append(item.name)

    return ClassInfo(
        module=module_name,
        name=node.name,
        description=doc_info.description,
        methods=methods,
        is_private=node.name.startswith("_"),
    )


def parse_conftest_fixtures(
    conftest_path: Path,
    root_dir: Path | None = None,
) -> tuple[list[FixtureInfo], list[FactoryInfo]]:
    """Parse pytest fixtures and mock factories from conftest.py.

    Args:
        conftest_path: Path to conftest.py file
        root_dir: Optional root directory for relative path calculation

    Returns:
        Tuple of (list of FixtureInfo, list of FactoryInfo)
    """
    if not conftest_path.exists():
        return [], []

    with open(conftest_path) as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"Warning: Syntax error in {conftest_path}: {e}")
        return [], []

    # Use relative path if root_dir provided
    if root_dir:
        location_path = str(conftest_path.relative_to(root_dir))
    else:
        location_path = str(conftest_path)

    fixtures: list[FixtureInfo] = []
    factories: list[FactoryInfo] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check if this is a pytest fixture
            for decorator in node.decorator_list:
                decorator_name = ""
                if isinstance(decorator, ast.Name):
                    decorator_name = decorator.id
                elif isinstance(decorator, ast.Attribute):
                    decorator_name = decorator.attr
                elif isinstance(decorator, ast.Call):
                    if isinstance(decorator.func, ast.Name):
                        decorator_name = decorator.func.id
                    elif isinstance(decorator.func, ast.Attribute):
                        decorator_name = decorator.func.attr

                if decorator_name == "fixture":
                    docstring = ast.get_docstring(node)
                    doc_info = parse_google_docstring(docstring)

                    # Get return annotation if present
                    returns = ""
                    if node.returns:
                        returns = ast.unparse(node.returns)
                    elif doc_info.returns:
                        returns = doc_info.returns

                    fixture = FixtureInfo(
                        name=node.name,
                        description=doc_info.description,
                        returns=returns,
                        location=location_path,
                    )
                    fixtures.append(fixture)
                    break

        elif isinstance(node, ast.ClassDef):
            # Check if this looks like a mock factory class
            if "Factory" in node.name or "Mock" in node.name:
                docstring = ast.get_docstring(node)
                doc_info = parse_google_docstring(docstring)

                factory = FactoryInfo(
                    name=node.name,
                    purpose=doc_info.description,
                    location=location_path,
                    fixtures=[],  # Would need more analysis to determine
                )
                factories.append(factory)

    return fixtures, factories


def validate_function(
    func: FunctionInfo,
    file_path: Path,
    lineno: int = 0,
) -> list[ValidationError]:
    """Validate that a function has complete documentation.

    Args:
        func: FunctionInfo to validate
        file_path: Path to the source file
        lineno: Line number of the function (if known)

    Returns:
        List of validation errors
    """
    errors: list[ValidationError] = []
    location = f"{file_path}:{lineno}" if lineno else str(file_path)

    # Skip dunder methods like __init__, __str__, etc.
    if func.name.startswith("__") and func.name.endswith("__"):
        return errors

    # Check for missing description
    if not func.description:
        errors.append(
            ValidationError(
                location=location,
                message=f"Function '{func.name}' is missing a docstring description",
            )
        )

    # Check for missing Args section (if function has parameters)
    # We need to check signature for parameters
    sig = func.signature
    # Simple heuristic: if signature has more than just 'self'/'cls' or is non-empty
    # Check for params beyond self/cls - signatures like "(self, x)" have real params
    has_params = sig and sig not in ("()", "(self)", "(cls)")
    # Methods with additional params start with "(self," or "(cls,"
    if sig and (sig.startswith("(self,") or sig.startswith("(cls,")):
        has_params = True
    if has_params and func.args == "":
        # Check if all params are documented
        # This is a simplified check - could be more rigorous
        errors.append(
            ValidationError(
                location=location,
                message=f"Function '{func.name}' has parameters but no Args section",
                severity="warning",
            )
        )

    # Check for missing Returns section (if function returns non-None)
    if "-> None" not in sig and "->" in sig and not func.returns:
        errors.append(
            ValidationError(
                location=location,
                message=f"Function '{func.name}' has return type but no Returns section",
                severity="warning",
            )
        )

    return errors


def generate_service_registry(
    src_dir: Path,
    root_dir: Path,
) -> tuple[dict[str, Any], list[ValidationError]]:
    """Generate service registry from source files.

    Args:
        src_dir: Path to the source directory (e.g., src/)
        root_dir: Root directory for relative paths

    Returns:
        Tuple of (registry dict for TOON, list of validation errors)
    """
    modules: list[ModuleInfo] = []
    functions: list[FunctionInfo] = []
    classes: list[ClassInfo] = []
    errors: list[ValidationError] = []

    # Find all Python files in src
    for py_file in sorted(src_dir.rglob("*.py")):
        mod_info, mod_funcs, mod_classes = parse_module(py_file, root_dir)
        modules.append(mod_info)
        functions.extend(mod_funcs)
        classes.extend(mod_classes)

        # Validate each function
        for func in mod_funcs:
            func_errors = validate_function(func, py_file)
            errors.extend(func_errors)

    # Build registry structure
    registry: dict[str, Any] = {
        "meta": {
            "generated": datetime.now(timezone.utc).isoformat(),
            "generator": "scripts/generate_registries.py",
            "version": "1.0",
        },
        "modules": [
            {
                "name": m.name,
                "path": m.path,
                "description": m.description,
            }
            for m in modules
        ],
        "functions": [
            {
                "module": f.module,
                "name": f.name,
                "signature": f.signature,
                "description": f.description,
                "args": f.args,
                "returns": f.returns,
                "raises": f.raises,
                "is_private": f.is_private,
                "is_method": f.is_method,
                "class_name": f.class_name,
            }
            for f in functions
        ],
        "classes": [
            {
                "module": c.module,
                "name": c.name,
                "description": c.description,
                "methods": c.methods,
                "is_private": c.is_private,
            }
            for c in classes
        ],
    }

    return registry, errors


def generate_mock_registry(
    conftest_path: Path,
    root_dir: Path | None = None,
) -> tuple[dict[str, Any], list[ValidationError]]:
    """Generate mock registry from conftest.py.

    Args:
        conftest_path: Path to tests/conftest.py
        root_dir: Optional root directory for relative path calculation

    Returns:
        Tuple of (registry dict for TOON, list of validation errors)
    """
    fixtures, factories = parse_conftest_fixtures(conftest_path, root_dir)
    errors: list[ValidationError] = []

    # Validate fixtures have docstrings
    for fixture in fixtures:
        if not fixture.description:
            errors.append(
                ValidationError(
                    location=fixture.location,
                    message=f"Fixture '{fixture.name}' is missing a docstring description",
                )
            )

    # Build registry structure
    registry: dict[str, Any] = {
        "meta": {
            "generated": datetime.now(timezone.utc).isoformat(),
            "generator": "scripts/generate_registries.py",
            "version": "1.0",
        },
        "factories": [
            {
                "name": f.name,
                "purpose": f.purpose,
                "location": f.location,
                "fixtures": f.fixtures,
            }
            for f in factories
        ],
        "fixtures": [
            {
                "name": f.name,
                "description": f.description,
                "returns": f.returns,
                "location": f.location,
            }
            for f in fixtures
        ],
    }

    return registry, errors


def write_toon(path: Path, data: dict[str, Any]) -> None:
    """Write a registry to a TOON file.

    Args:
        path: Path to write the TOON file
        data: Dictionary data to serialize
    """
    content = toon_python.encode(data)
    path.write_text(content)


def main() -> int:
    """Main entry point for registry generation.

    Returns:
        Exit code (0 for success, 1 for validation failure)
    """
    import argparse

    parser = argparse.ArgumentParser(description="Generate service and mock registries")
    parser.add_argument("--check", action="store_true", help="Validate without writing")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    root = Path(__file__).parent.parent
    src_dir = root / "src"
    conftest_path = root / "tests" / "conftest.py"

    all_errors: list[ValidationError] = []

    # Generate service registry
    if args.verbose:
        print("Generating service registry...")
    service_registry, service_errors = generate_service_registry(src_dir, root)
    all_errors.extend(service_errors)

    if args.verbose:
        print(f"  Found {len(service_registry['modules'])} modules")
        print(f"  Found {len(service_registry['functions'])} functions")
        print(f"  Found {len(service_registry['classes'])} classes")

    # Generate mock registry
    if args.verbose:
        print("Generating mock registry...")
    mock_registry, mock_errors = generate_mock_registry(conftest_path, root)
    all_errors.extend(mock_errors)

    if args.verbose:
        print(f"  Found {len(mock_registry['factories'])} factories")
        print(f"  Found {len(mock_registry['fixtures'])} fixtures")

    # Report errors
    error_count = sum(1 for e in all_errors if e.severity == "error")
    warning_count = sum(1 for e in all_errors if e.severity == "warning")

    if all_errors:
        print(f"\nValidation issues ({error_count} errors, {warning_count} warnings):")
        for error in all_errors:
            marker = "ERROR" if error.severity == "error" else "WARNING"
            print(f"  [{marker}] {error.location}: {error.message}")

    # Write registries (unless check mode)
    if not args.check:
        service_path = root / "service-registry.toon"
        mock_path = root / "mock-registry.toon"

        write_toon(service_path, service_registry)
        write_toon(mock_path, mock_registry)

        print(f"\nRegistries generated:")
        print(f"  {service_path}")
        print(f"  {mock_path}")

    # Exit with error if validation failed
    if error_count > 0:
        print(f"\n{error_count} validation error(s) found.")
        return 1

    print("\nRegistry generation completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
