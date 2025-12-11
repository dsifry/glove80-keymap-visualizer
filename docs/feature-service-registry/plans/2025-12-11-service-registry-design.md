# Service Registry Design

**Date:** 2025-12-11
**Branch:** feature/service-registry
**Issue:** #7

## Overview

Auto-generated registries that document all functions, classes, mocks, and fixtures in the codebase. CI/CD validation ensures registries stay current and all code has complete documentation.

## Decisions

| Decision | Choice |
|----------|--------|
| Format | TOON (`.toon` extension) using `toon-format` library |
| Docstring style | Google-style with Args, Returns, Raises |
| Generator location | `scripts/generate_registries.py` |
| Registry files | `service-registry.toon`, `mock-registry.toon` in project root |
| CI validation | Strict - fails on missing functions, incomplete docstrings, or out-of-sync registry |
| Existing code | Fix all docstrings first, then enable CI |
| Scope | All functions, classes, and methods (including private) |
| Skills location | `.claude/plugins/glove80-viz/skills/` |

## Registry File Structure

### service-registry.toon

Located in project root. Contains all functions, classes, and services from `src/`.

```toon
meta:
  generated: 2025-12-11T10:30:00Z
  generator: scripts/generate_registries.py
  version: 1.0

modules[11]:
  name,path,description
  cli,src/glove80_visualizer/cli.py,Command-line interface for glove80-viz
  parser,src/glove80_visualizer/parser.py,ZMK keymap parsing using keymap-drawer
  ...

functions[]:
  module,name,signature,description,args,returns,raises
  cli,main,() -> None,Main entry point for CLI,...
  parser,parse_keymap,(keymap_path: Path) -> ParsedKeymap,Parse a ZMK keymap file,...
  ...

classes[]:
  module,name,description,methods
  models,Layer,Represents a keyboard layer,[__init__|from_dict|to_dict]
  ...
```

### mock-registry.toon

Located in project root. Contains all mock factories and fixtures from `tests/conftest.py`.

```toon
meta:
  generated: 2025-12-11T10:30:00Z
  generator: scripts/generate_registries.py
  version: 1.0

factories[3]:
  name,purpose,location,fixtures
  PlaywrightMockFactory,Mock headless browser operations,tests/conftest.py,[playwright_mocks]
  PILMockFactory,Mock PIL/Pillow image operations,tests/conftest.py,[pil_image_mock|pil_module_mock]
  PdfMergerMockFactory,Mock PyPDF2 PDF merging,tests/conftest.py,[pdf_merger_mock]

fixtures[]:
  name,factory,description,returns
  playwright_mocks,PlaywrightMockFactory,Complete Playwright mock set,tuple[MagicMock MagicMock MagicMock]
  ...
```

## Docstring Standard

All functions must use Google-style docstrings:

```python
def parse_keymap(keymap_path: Path) -> ParsedKeymap:
    """Parse a ZMK keymap file into structured data.

    Args:
        keymap_path: Path to the .keymap file

    Returns:
        ParsedKeymap with layers and bindings extracted

    Raises:
        ParserError: If keymap syntax is invalid
    """
```

Required sections:
- **Description** (first line) - Always required
- **Args** - Required if function has parameters
- **Returns** - Required if function returns non-None
- **Raises** - Required if function raises exceptions

## Generator Script

### Location

```
scripts/
  generate_registries.py    # Main generator script
```

### Architecture

```python
#!/usr/bin/env python3
"""Auto-generate service and mock registries from source code."""

import ast
import sys
from pathlib import Path
from toon import dumps

def main():
    """Generate both registries, exit non-zero if validation fails."""
    root = Path(__file__).parent.parent

    # Generate service registry from src/
    service_registry = generate_service_registry(root / "src")

    # Generate mock registry from tests/conftest.py
    mock_registry = generate_mock_registry(root / "tests/conftest.py")

    # Validate completeness (all functions have docstrings)
    errors = validate_registries(service_registry, mock_registry)

    if errors:
        print("Registry validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)

    # Write registries
    write_toon(root / "service-registry.toon", service_registry)
    write_toon(root / "mock-registry.toon", mock_registry)

    print("Registries generated successfully.")
```

### Key Components

- `generate_service_registry()` - Uses Python `ast` module to parse source files
- `generate_mock_registry()` - Parses `conftest.py` for factories and fixtures
- `validate_registries()` - Checks all functions have complete docstrings
- `parse_google_docstring()` - Extracts Args, Returns, Raises sections

### Dependencies

- `toon-format` (for TOON serialization)
- Standard library only otherwise (`ast`, `pathlib`, `inspect`)

## CI/CD Integration

### New Job in `.github/workflows/ci.yml`

```yaml
registry:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.12"

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install toon-format
        pip install -e ".[dev]"

    - name: Generate registries
      run: python scripts/generate_registries.py

    - name: Check registries are up-to-date
      run: |
        if ! git diff --exit-code service-registry.toon mock-registry.toon; then
          echo "::error::Registry files are out of date. Run 'python scripts/generate_registries.py' and commit the changes."
          exit 1
        fi
```

### Failure Scenarios

| Scenario | Result |
|----------|--------|
| Function missing docstring | Generator exits with error listing functions |
| Incomplete docstring (missing Args/Returns) | Generator exits with error |
| Registry out of sync | Git diff check fails with instructions |

## Skills

Three new skills in `.claude/plugins/glove80-viz/skills/`:

### maintaining-service-registry.md

**Triggers:** When creating or modifying functions in `src/`

**Actions:**
1. Reminds to add Google-style docstring with Args, Returns, Raises
2. Shows docstring template for the function signature
3. Reminds to run `python scripts/generate_registries.py` before committing

### maintaining-mock-registry.md

**Triggers:** When creating or modifying mocks/fixtures in `tests/conftest.py`

**Actions:**
1. Reminds to add docstring describing the mock's purpose
2. Ensures new mocks go in `conftest.py` (not scattered across test files)
3. Reminds to run the generator before committing

### registry-verification.md

**Triggers:** Before completing any task (integrates with `verification-before-completion`)

**Actions:**
1. Runs `python scripts/generate_registries.py`
2. Reports any missing/incomplete docstrings
3. Checks if registry files need committing
4. Blocks task completion until registries are valid and committed

## CLAUDE.md Updates

Add non-auto-loading reference:

```markdown
## Service & Mock Registries

This project maintains auto-generated registries of all functions and mocks:

- **Service Registry**: `service-registry.toon` - All functions, classes, and services in `src/`
- **Mock Registry**: `mock-registry.toon` - All mock factories and fixtures in `tests/conftest.py`

### Requirements

- All functions must have Google-style docstrings with Args, Returns, Raises sections
- All mocks/fixtures must have docstrings describing their purpose
- Registries are auto-generated - run `python scripts/generate_registries.py`
- CI fails if registries are out of date or docstrings are incomplete

### Updating Registries

After adding or modifying functions/mocks:

\`\`\`bash
python scripts/generate_registries.py
git add service-registry.toon mock-registry.toon
\`\`\`
```

Update task completion checklist to include registry verification step.

## Implementation Order

1. **Add `toon-format` dependency** to `requirements-dev.txt`
2. **Audit and fix existing docstrings** in all source files
3. **Create generator script** `scripts/generate_registries.py`
4. **Generate initial registries** and commit them
5. **Add CI workflow job** for registry validation
6. **Create three skills** for registry maintenance
7. **Update CLAUDE.md** with registry documentation
8. **Update task completion checklist**

## Acceptance Criteria

- [ ] All functions in `src/` have complete Google-style docstrings
- [ ] All mocks/fixtures in `tests/conftest.py` have docstrings
- [ ] `scripts/generate_registries.py` generates valid TOON files
- [ ] `service-registry.toon` contains all functions and classes
- [ ] `mock-registry.toon` contains all factories and fixtures
- [ ] CI job validates registries on every push/PR
- [ ] Three skills created and functional
- [ ] CLAUDE.md updated with registry documentation
- [ ] Task completion checklist includes registry verification
