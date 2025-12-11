# maintaining-mock-registry

Use when creating or modifying mocks and fixtures in `tests/conftest.py` - ensures all test infrastructure has proper docstrings and is registered in the mock registry.

## When to Activate

Activate this skill when ANY of these conditions are true:

- Creating a new pytest fixture
- Creating a new mock factory
- Modifying existing fixtures in `conftest.py`
- Moving fixtures between test files

## Announce at Start

"I'm using the maintaining-mock-registry skill to ensure proper documentation for test fixtures."

## Fixture Requirements

All fixtures in `tests/conftest.py` must have docstrings describing:

1. **Purpose** - What the fixture provides
2. **Returns** - What type of object is yielded/returned
3. **Usage** - How to use it in tests (if not obvious)

### Template

```python
@pytest.fixture
def fixture_name() -> ReturnType:
    """Short description of what the fixture provides.

    Returns:
        Description of the returned object

    Example:
        def test_something(fixture_name):
            result = fixture_name.do_something()
            assert result == expected
    """
```

### Examples

**Path fixture:**

```python
@pytest.fixture
def sample_keymap_path(fixtures_dir: Path) -> Path:
    """Return path to a sample keymap file for testing.

    Returns:
        Path to tests/fixtures/sample.keymap
    """
    return fixtures_dir / "sample.keymap"
```

**Object fixture:**

```python
@pytest.fixture
def sample_layer() -> Layer:
    """Create a sample Layer object for testing.

    Returns:
        Layer with index=0, name='Test', and sample bindings
    """
    return Layer(
        index=0,
        name="Test",
        bindings=[KeyBinding(position=0, tap="A")]
    )
```

**Mock fixture:**

```python
@pytest.fixture
def mock_subprocess(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Mock subprocess.run for testing CLI commands.

    Returns:
        MagicMock configured to return successful results
    """
    mock = MagicMock()
    mock.return_value = MagicMock(returncode=0, stdout="", stderr="")
    monkeypatch.setattr("subprocess.run", mock)
    return mock
```

## Fixture Organization Rules

1. **All shared fixtures go in `tests/conftest.py`** - Not scattered across test files
2. **File-specific fixtures stay in the test file** - Only if used by one file
3. **Group related fixtures** - Keep mock factories together

### Fixture Hierarchy

```text
tests/
  conftest.py          # Shared fixtures (registered in mock-registry.toon)
  test_parser.py       # Can have parser-specific fixtures if only used here
  test_cli.py          # Same - local fixtures if truly local
```

## Before Completing Any Test Change

1. **Check fixture docstrings** for any new/modified fixtures
2. **Run the generator** to validate:
   ```bash
   python scripts/generate_registries.py --check
   ```
3. **Regenerate if needed**:
   ```bash
   python scripts/generate_registries.py
   ```

## Mock Factory Pattern

For complex mocks that need setup/teardown or configuration, use a factory pattern:

```python
class MockFactory:
    """Factory for creating configured mock objects.

    Provides consistent mock setup for [what it mocks].
    """

    @staticmethod
    def create_mock() -> MagicMock:
        """Create a configured mock.

        Returns:
            MagicMock with standard configuration
        """
        ...


@pytest.fixture
def mock_from_factory() -> MagicMock:
    """Provide a mock from the factory.

    Returns:
        Configured MagicMock for testing
    """
    return MockFactory.create_mock()
```

## Verification Checklist

Before marking any task complete:

- [ ] All new fixtures have complete docstrings
- [ ] Shared fixtures are in `conftest.py`
- [ ] `python scripts/generate_registries.py --check` shows 0 errors
- [ ] Registry files are regenerated if fixtures changed
- [ ] Registry changes are committed with test changes
