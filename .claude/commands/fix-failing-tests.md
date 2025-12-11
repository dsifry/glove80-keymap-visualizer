---
description: Systematically fix failing tests using proper debugging and testing patterns
---

# Fix Failing Tests

Systematically fix failing tests using proper debugging and testing patterns.

## Usage

```bash
/project:fix-failing-tests
```

## Steps

### 1. Run Test Suite

```bash
make test
```

Identify failing tests from the output.

### 2. Analyze Failures

Review error messages and stack traces:

```bash
# Run specific test with verbose output
.venv/bin/pytest tests/test_specific.py -v

# Run with more detailed output
.venv/bin/pytest tests/test_specific.py -v --tb=long
```

### 3. Check Testing Patterns

Reference existing test files for proper patterns:

- `tests/conftest.py` - Fixture definitions
- `tests/fixtures/*.keymap` - Test keymap files
- Existing `tests/test_*.py` files for patterns

### 4. Debug Systematically

```bash
# Run individual test file
.venv/bin/pytest tests/test_parser.py -v

# Run specific test function
.venv/bin/pytest tests/test_parser.py::test_parse_layer -v

# Run with print output visible
.venv/bin/pytest tests/test_parser.py -v -s

# Run with debugger on failure
.venv/bin/pytest tests/test_parser.py -v --pdb
```

### 5. Common Fix Patterns

#### Mock External Dependencies

```python
from unittest.mock import patch, MagicMock

@patch('glove80_visualizer.parser.subprocess.run')
def test_with_mocked_subprocess(mock_run):
    mock_run.return_value = MagicMock(stdout="yaml output", returncode=0)
    # ... test logic
```

#### Handle File I/O

```python
import tempfile
from pathlib import Path

def test_file_operation(tmp_path):
    test_file = tmp_path / "test.keymap"
    test_file.write_text("test content")
    # ... test logic
```

#### Proper Async Handling (if needed)

```python
import pytest

@pytest.mark.asyncio
async def test_async_operation():
    result = await async_function()
    assert result == expected
```

### 6. Type Safety in Tests

```python
from typing import cast
from glove80_visualizer.types import LayerConfig

# Use cast for complex type assertions
config = cast(LayerConfig, mock_config)
```

### 7. Verify Fixes

```bash
# Run full test suite
make test

# Run with coverage
make test-cov

# Ensure no regressions
make lint && make typecheck && make test
```

## Anti-Patterns to Avoid

- **NEVER** remove tests to fix errors
- **NEVER** skip tests without justification
- **NEVER** weaken assertions (e.g., removing specific checks)
- **NEVER** use `# type: ignore` without understanding why

## Checklist Before Marking Complete

- [ ] All tests pass
- [ ] No tests were removed or skipped
- [ ] Test coverage maintained or improved
- [ ] Type checking passes
- [ ] Linting passes

Always follow the testing patterns documented in existing test files and avoid common pitfalls like real file system operations in unit tests.
