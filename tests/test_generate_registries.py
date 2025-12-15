"""
Tests for the registry generator script.

TDD: These tests are written BEFORE the implementation.
"""

import tempfile
from pathlib import Path

import pytest


class TestParseGoogleDocstring:
    """Tests for parsing Google-style docstrings."""

    def test_empty_docstring_returns_empty_info(self):
        """Empty or None docstring returns empty DocstringInfo."""
        from scripts.generate_registries import parse_google_docstring

        result = parse_google_docstring(None)
        assert result.description == ""
        assert result.args == {}
        assert result.returns == ""
        assert result.raises == []

        result = parse_google_docstring("")
        assert result.description == ""

    def test_description_only(self):
        """Docstring with only description is parsed correctly."""
        from scripts.generate_registries import parse_google_docstring

        result = parse_google_docstring("This is a simple description.")
        assert result.description == "This is a simple description."
        assert result.args == {}
        assert result.returns == ""
        assert result.raises == []

    def test_description_with_args(self):
        """Docstring with Args section is parsed correctly."""
        from scripts.generate_registries import parse_google_docstring

        docstring = """Parse a file into structured data.

        Args:
            file_path: Path to the file to parse
            encoding: Character encoding to use
        """
        result = parse_google_docstring(docstring)
        assert result.description == "Parse a file into structured data."
        assert result.args == {
            "file_path": "Path to the file to parse",
            "encoding": "Character encoding to use",
        }

    def test_description_with_returns(self):
        """Docstring with Returns section is parsed correctly."""
        from scripts.generate_registries import parse_google_docstring

        docstring = """Get the current value.

        Returns:
            The current integer value
        """
        result = parse_google_docstring(docstring)
        assert result.description == "Get the current value."
        assert result.returns == "The current integer value"

    def test_description_with_raises(self):
        """Docstring with Raises section is parsed correctly."""
        from scripts.generate_registries import parse_google_docstring

        docstring = """Open a file for reading.

        Raises:
            FileNotFoundError: If the file does not exist
            PermissionError: If read permission is denied
        """
        result = parse_google_docstring(docstring)
        assert result.description == "Open a file for reading."
        assert len(result.raises) == 2
        assert "FileNotFoundError: If the file does not exist" in result.raises
        assert "PermissionError: If read permission is denied" in result.raises

    def test_complete_docstring(self):
        """Complete docstring with all sections is parsed correctly."""
        from scripts.generate_registries import parse_google_docstring

        docstring = """Parse a ZMK keymap file into YAML representation.

        Args:
            keymap_path: Path to the ZMK .keymap file
            keyboard: Keyboard type for physical layout

        Returns:
            YAML string containing the parsed keymap data

        Raises:
            FileNotFoundError: If the keymap file does not exist
            KeymapParseError: If the keymap cannot be parsed
        """
        result = parse_google_docstring(docstring)
        assert result.description == "Parse a ZMK keymap file into YAML representation."
        assert result.args == {
            "keymap_path": "Path to the ZMK .keymap file",
            "keyboard": "Keyboard type for physical layout",
        }
        assert result.returns == "YAML string containing the parsed keymap data"
        assert len(result.raises) == 2


class TestGetFunctionSignature:
    """Tests for extracting function signatures from AST nodes."""

    def test_no_args_no_return(self):
        """Function with no arguments and no return type."""
        import ast

        from scripts.generate_registries import get_function_signature

        code = "def foo(): pass"
        tree = ast.parse(code)
        func = tree.body[0]
        assert get_function_signature(func) == "()"

    def test_simple_args(self):
        """Function with simple arguments."""
        import ast

        from scripts.generate_registries import get_function_signature

        code = "def foo(a, b): pass"
        tree = ast.parse(code)
        func = tree.body[0]
        assert get_function_signature(func) == "(a, b)"

    def test_typed_args(self):
        """Function with typed arguments."""
        import ast

        from scripts.generate_registries import get_function_signature

        code = "def foo(a: int, b: str): pass"
        tree = ast.parse(code)
        func = tree.body[0]
        assert get_function_signature(func) == "(a: int, b: str)"

    def test_return_type(self):
        """Function with return type annotation."""
        import ast

        from scripts.generate_registries import get_function_signature

        code = "def foo() -> int: pass"
        tree = ast.parse(code)
        func = tree.body[0]
        assert get_function_signature(func) == "() -> int"

    def test_default_values(self):
        """Function with default argument values."""
        import ast

        from scripts.generate_registries import get_function_signature

        code = 'def foo(a: int = 1, b: str = "x"): pass'
        tree = ast.parse(code)
        func = tree.body[0]
        result = get_function_signature(func)
        assert "a: int = 1" in result
        assert "b: str = 'x'" in result

    def test_args_kwargs(self):
        """Function with *args and **kwargs."""
        import ast

        from scripts.generate_registries import get_function_signature

        code = "def foo(*args, **kwargs): pass"
        tree = ast.parse(code)
        func = tree.body[0]
        assert get_function_signature(func) == "(*args, **kwargs)"

    def test_complex_signature(self):
        """Function with complex signature."""
        import ast

        from scripts.generate_registries import get_function_signature

        code = (
            "def foo(a: int, b: str = 'default', *args, c: bool = True, **kwargs) "
            "-> list[str]: pass"
        )
        tree = ast.parse(code)
        func = tree.body[0]
        result = get_function_signature(func)
        assert "a: int" in result
        assert "*args" in result
        assert "**kwargs" in result
        assert "-> list[str]" in result


class TestParseModule:
    """Tests for parsing Python modules."""

    def test_module_with_docstring(self):
        """Module docstring is captured."""
        from scripts.generate_registries import parse_module

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            test_file = tmpdir_path / "test_mod.py"
            test_file.write_text('"""Module description here."""\n\ndef foo(): pass\n')

            mod_info, funcs, classes = parse_module(test_file, tmpdir_path)

            assert mod_info.name == "test_mod"
            assert mod_info.description == "Module description here."

    def test_module_functions(self):
        """Module-level functions are extracted."""
        from scripts.generate_registries import parse_module

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            test_file = tmpdir_path / "test_mod.py"
            test_file.write_text('''
def public_func():
    """A public function."""
    pass

def _private_func():
    """A private function."""
    pass
''')

            mod_info, funcs, classes = parse_module(test_file, tmpdir_path)

            func_names = [f.name for f in funcs]
            assert "public_func" in func_names
            assert "_private_func" in func_names

            # Check private flag
            private_func = next(f for f in funcs if f.name == "_private_func")
            assert private_func.is_private is True

            public_func = next(f for f in funcs if f.name == "public_func")
            assert public_func.is_private is False

    def test_module_classes(self):
        """Classes and their methods are extracted."""
        from scripts.generate_registries import parse_module

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            test_file = tmpdir_path / "test_mod.py"
            test_file.write_text('''
class MyClass:
    """A test class."""

    def method_one(self):
        """First method."""
        pass

    def method_two(self, x: int) -> str:
        """Second method."""
        return str(x)
''')

            mod_info, funcs, classes = parse_module(test_file, tmpdir_path)

            assert len(classes) == 1
            assert classes[0].name == "MyClass"
            assert classes[0].description == "A test class."
            assert "method_one" in classes[0].methods
            assert "method_two" in classes[0].methods

            # Methods should also appear in functions list
            method_funcs = [f for f in funcs if f.is_method]
            assert len(method_funcs) == 2


class TestGenerateServiceRegistry:
    """Tests for generating the service registry."""

    def test_generates_registry_structure(self):
        """Registry has expected structure with meta, modules, functions, classes."""
        from scripts.generate_registries import generate_service_registry

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            src_dir = tmpdir_path / "src"
            src_dir.mkdir()
            (src_dir / "example.py").write_text('''
"""Example module."""

def example_func(x: int) -> str:
    """Convert int to string.

    Args:
        x: The integer to convert

    Returns:
        String representation
    """
    return str(x)
''')

            registry, errors = generate_service_registry(src_dir, tmpdir_path)

            assert "meta" in registry
            assert "modules" in registry
            assert "functions" in registry
            assert "classes" in registry
            assert registry["meta"]["version"] == "1.0"

    def test_captures_function_details(self):
        """Function details are captured correctly."""
        from scripts.generate_registries import generate_service_registry

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            src_dir = tmpdir_path / "src"
            src_dir.mkdir()
            (src_dir / "example.py").write_text('''
"""Example module."""

def example_func(x: int) -> str:
    """Convert int to string.

    Args:
        x: The integer to convert

    Returns:
        String representation
    """
    return str(x)
''')

            registry, errors = generate_service_registry(src_dir, tmpdir_path)

            funcs = registry["functions"]
            assert len(funcs) == 1
            func = funcs[0]
            assert func["name"] == "example_func"
            assert func["description"] == "Convert int to string."
            assert "x: int" in func["signature"]
            assert "-> str" in func["signature"]


class TestValidation:
    """Tests for validation of docstring completeness."""

    def test_missing_docstring_is_error(self):
        """Function without docstring generates validation error."""
        from scripts.generate_registries import generate_service_registry

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            src_dir = tmpdir_path / "src"
            src_dir.mkdir()
            (src_dir / "example.py").write_text("""
def undocumented_func():
    pass
""")

            registry, errors = generate_service_registry(src_dir, tmpdir_path)

            assert len(errors) > 0
            assert any("undocumented_func" in e.message for e in errors)
            assert any("missing" in e.message.lower() for e in errors)

    def test_dunder_methods_not_validated(self):
        """Dunder methods like __init__ don't require docstrings."""
        from scripts.generate_registries import generate_service_registry

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            src_dir = tmpdir_path / "src"
            src_dir.mkdir()
            (src_dir / "example.py").write_text('''
"""Example module."""

class MyClass:
    """A class."""

    def __init__(self):
        pass

    def __str__(self):
        return "MyClass"
''')

            registry, errors = generate_service_registry(src_dir, tmpdir_path)

            # Should not have errors for __init__ or __str__
            dunder_errors = [e for e in errors if "__" in e.message]
            assert len(dunder_errors) == 0


class TestMockRegistry:
    """Tests for generating the mock registry."""

    def test_parses_fixtures(self):
        """Pytest fixtures are extracted from conftest.py."""
        from scripts.generate_registries import generate_mock_registry

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            conftest = tmpdir_path / "conftest.py"
            conftest.write_text('''
import pytest

@pytest.fixture
def sample_data():
    """Provide sample test data."""
    return {"key": "value"}

@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file for testing."""
    return tmp_path / "test.txt"
''')

            registry, errors = generate_mock_registry(conftest)

            fixtures = registry["fixtures"]
            assert len(fixtures) == 2
            fixture_names = [f["name"] for f in fixtures]
            assert "sample_data" in fixture_names
            assert "temp_file" in fixture_names

    def test_fixtures_without_docstring_generate_error(self):
        """Fixtures without docstrings generate validation errors."""
        from scripts.generate_registries import generate_mock_registry

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            conftest = tmpdir_path / "conftest.py"
            conftest.write_text("""
import pytest

@pytest.fixture
def undocumented_fixture():
    return 42
""")

            registry, errors = generate_mock_registry(conftest)

            assert len(errors) > 0
            assert any("undocumented_fixture" in e.message for e in errors)

    def test_nonexistent_conftest(self):
        """Nonexistent conftest.py returns empty registry."""
        from scripts.generate_registries import generate_mock_registry

        registry, errors = generate_mock_registry(Path("/nonexistent/conftest.py"))

        assert registry["fixtures"] == []
        assert registry["factories"] == []
        assert len(errors) == 0


class TestToonOutput:
    """Tests for TOON format output."""

    def test_write_toon_creates_file(self):
        """write_toon creates a valid TOON file."""
        from scripts.generate_registries import write_toon

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            output_path = tmpdir_path / "test.toon"

            data = {
                "meta": {"version": "1.0"},
                "items": [{"name": "test", "value": 42}],
            }

            write_toon(output_path, data)

            assert output_path.exists()
            content = output_path.read_text()
            assert "version" in content
            assert "1.0" in content


class TestMainFunction:
    """Tests for the main CLI entry point."""

    def test_main_returns_zero_on_success(self):
        """main() returns 0 when all functions are documented."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create minimal src directory
            src_dir = tmpdir_path / "src"
            src_dir.mkdir()
            (src_dir / "example.py").write_text('''
"""Example module."""

def documented_func():
    """A documented function."""
    pass
''')

            # Create minimal conftest
            tests_dir = tmpdir_path / "tests"
            tests_dir.mkdir()
            (tests_dir / "conftest.py").write_text('''
"""Test fixtures."""

import pytest

@pytest.fixture
def sample():
    """A sample fixture."""
    return 42
''')

            # Temporarily change to tmpdir and patch __file__ location
            # This is tricky - we may need to refactor main() to accept paths
            # For now, skip this test until implementation allows path injection
            pytest.skip("Need to refactor main() to accept paths for testing")

    def test_main_returns_one_on_validation_failure(self):
        """main() returns 1 when validation errors exist."""
        pytest.skip("Need to refactor main() to accept paths for testing")
