# maintaining-service-registry

Use when creating or modifying functions in `src/` - ensures all code has proper Google-style docstrings and reminds to regenerate the service registry.

## When to Activate

Activate this skill when ANY of these conditions are true:

- Creating a new function or method in `src/`
- Modifying an existing function signature in `src/`
- Adding a new module to `src/glove80_visualizer/`
- User asks about docstring requirements

## Announce at Start

"I'm using the maintaining-service-registry skill to ensure proper documentation for the service registry."

## Docstring Requirements

All functions in `src/` must have Google-style docstrings with these sections:

### Required Sections

| Section | When Required |
|---------|---------------|
| Description | Always (first line) |
| Args | If function has parameters |
| Returns | If function returns non-None |
| Raises | If function can raise exceptions |

### Template

```python
def function_name(param1: str, param2: int = 0) -> ReturnType:
    """Short description of what the function does.

    Longer description if needed, explaining behavior,
    edge cases, or important details.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter (defaults to 0)

    Returns:
        Description of what is returned

    Raises:
        ValueError: When param1 is empty
        IOError: When file cannot be read
    """
```

### Examples for Common Patterns

**Simple function:**

```python
def process_layer(layer: Layer) -> str:
    """Process a layer into SVG format.

    Args:
        layer: The Layer object to process

    Returns:
        SVG content as a string
    """
```

**Function with no return:**

```python
def validate_config(config: Config) -> None:
    """Validate configuration settings.

    Args:
        config: Configuration to validate

    Raises:
        ConfigError: If configuration is invalid
    """
```

**Private function (still needs docstring):**

```python
def _format_binding(binding: KeyBinding) -> str:
    """Format a key binding for display.

    Args:
        binding: The key binding to format

    Returns:
        Formatted string representation
    """
```

## Before Completing Any Code Change

1. **Check docstring completeness** for any new/modified functions
2. **Run the generator** to validate:
   ```bash
   python scripts/generate_registries.py --check
   ```
3. **Fix any errors** - errors fail CI, warnings are acceptable
4. **Regenerate if needed**:
   ```bash
   python scripts/generate_registries.py
   ```

## Common Mistakes

**Missing Args section when function has parameters:**

```python
# BAD - missing Args
def parse_file(path: Path) -> dict:
    """Parse a file."""
    ...

# GOOD
def parse_file(path: Path) -> dict:
    """Parse a file.

    Args:
        path: Path to the file to parse

    Returns:
        Parsed content as a dictionary
    """
```

**Missing Returns for property getters:**

```python
# BAD
@property
def is_valid(self) -> bool:
    """Check if valid."""
    ...

# GOOD
@property
def is_valid(self) -> bool:
    """Check if valid.

    Returns:
        True if valid, False otherwise
    """
```

## Verification Checklist

Before marking any task complete:

- [ ] All new functions have complete docstrings
- [ ] `python scripts/generate_registries.py --check` shows 0 errors
- [ ] Registry files are regenerated if code changed
- [ ] Registry changes are committed with code changes
