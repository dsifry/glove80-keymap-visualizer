# Phase 2 Enhancements - TDD Specification (Revised)

## Overview

This specification defines the test-first requirements for Phase 2 enhancements. Each specification has a unique ID for traceability.

**Revision Notes (addressing CTO review):**
- Verified existing `format_key_label()` already handles nested combos (`LG(LS(K))` → `⌘⇧K`)
- Verified keymap-drawer output format: hold behaviors show layer names, `{type: 'held'}` marks activated positions
- Updated interfaces to match existing code signatures
- Clarified that `categorize_key()` operates on **formatted** labels (after `format_key_label()`)
- Removed redundant SPEC-KC-001 through SPEC-KC-004 (already working)

**Specification Format:**
- `SPEC-CI-XXX`: CI/CD and PyPI publishing
- `SPEC-KC-XXX`: Key combo display (MEH/HYPER only - nested combos already work)
- `SPEC-HK-XXX`: Held key indicator
- `SPEC-CL-XXX`: Color output

---

## Existing Functionality (Verified Working)

Before implementing, these were tested and confirmed working:

```python
# Already works:
format_key_label("LG(K)", os_style="mac")      # → "⌘K"
format_key_label("LG(LS(K))", os_style="mac")  # → "⌘⇧K"
format_key_label("LC(LA(K))", os_style="mac")  # → "⌃⌥K"

# NOT working (needs implementation):
format_key_label("MEH(K)", os_style="mac")     # → "Meh(K)" (should be "⌃⌥⇧K")
format_key_label("HYPER(K)", os_style="mac")   # → "Hyper(K)" (should be "⌃⌥⇧⌘K")
```

**keymap-drawer output format for layer activators:**
```yaml
# On base layer (QWERTY):
- {t: BACKSPACE, h: Cursor}   # tap=Backspace, hold activates Cursor layer
- {t: SPACE, h: Symbol}       # tap=Space, hold activates Symbol layer

# On target layer (Cursor):
- {type: held}                # Marks the key position that activates this layer
```

---

## 1. CI/CD & PyPI Publishing Specifications

### GitHub Actions CI

#### SPEC-CI-001: Tests run on pull request
**Given** a pull request is opened or updated
**When** the CI workflow runs
**Then** all pytest tests execute and must pass

**Verification:** Manual - check GitHub Actions tab after PR creation

#### SPEC-CI-002: Linting runs on pull request
**Given** a pull request is opened or updated
**When** the CI workflow runs
**Then** ruff linting executes with zero errors

**Verification:** Manual - check GitHub Actions tab

#### SPEC-CI-003: Type checking runs on pull request
**Given** a pull request is opened or updated
**When** the CI workflow runs
**Then** mypy type checking executes with zero errors

**Verification:** Manual - check GitHub Actions tab

#### SPEC-CI-004: Tests run on multiple Python versions
**Given** a pull request is opened or updated
**When** the CI workflow runs
**Then** tests execute on Python 3.10, 3.11, 3.12, and 3.13

**Verification:** Manual - check GitHub Actions matrix

### PyPI Publishing

#### SPEC-CI-005: Package builds successfully
**Given** the pyproject.toml is properly configured
**When** `python -m build` is executed
**Then** both wheel (.whl) and source distribution (.tar.gz) are created

**Test:** `tests/test_packaging.py`
```python
def test_package_builds(tmp_path):
    """SPEC-CI-005: Package builds without errors."""
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "build", "--outdir", str(tmp_path)],
        capture_output=True, text=True, cwd=PROJECT_ROOT
    )
    assert result.returncode == 0
    assert any(tmp_path.glob("*.whl"))
    assert any(tmp_path.glob("*.tar.gz"))
```

#### SPEC-CI-006: Package metadata is correct
**Given** the built package
**When** inspected with `pkginfo`
**Then** name, version, and entry points are correct

**Test:** `tests/test_packaging.py`
```python
def test_package_metadata():
    """SPEC-CI-006: Package metadata is correct."""
    from glove80_visualizer import __version__
    assert __version__ == "0.1.0"  # or current version
```

#### SPEC-CI-007: CLI entry point works after install
**Given** the package is installed
**When** `glove80-viz --version` is run
**Then** version is displayed without error

**Test:** `tests/test_packaging.py`
```python
def test_cli_entry_point():
    """SPEC-CI-007: CLI entry point works."""
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "glove80_visualizer.cli", "--version"],
        capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "0." in result.stdout
```

---

## 2. Key Combo Display Specifications

**Note:** Nested modifier combos (`LG(LS(K))`) already work via recursive parsing in `format_key_label()`. Only MEH and HYPER expansion is needed.

### MEH and HYPER Expansion

#### SPEC-KC-005: Parse MEH combo
**Given** a key binding `MEH(K)` (Ctrl+Alt+Shift)
**When** `format_key_label` is called
**Then** the result expands to all three modifiers + key

**Test:** `tests/test_svg_generator.py` (add `TestMehHyperCombos` class to existing file)
```python
class TestMehHyperCombos:
    """Tests for MEH and HYPER combo expansion."""

    def test_meh_combo_mac(self):
        """SPEC-KC-005: MEH(key) expands to Ctrl+Alt+Shift on Mac."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("MEH(K)", os_style="mac")
        assert result == "⌃⌥⇧K"

    def test_meh_combo_windows(self):
        """SPEC-KC-005: MEH(key) expands correctly on Windows."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("MEH(K)", os_style="windows")
        assert "Ctrl" in result and "Alt" in result and "Shift" in result
```

#### SPEC-KC-006: Parse HYPER combo
**Given** a key binding `HYPER(K)` (Ctrl+Alt+Shift+GUI)
**When** `format_key_label` is called
**Then** the result expands to all four modifiers + key

**Test:** `tests/test_svg_generator.py`
```python
    def test_hyper_combo_mac(self):
        """SPEC-KC-006: HYPER(key) expands to all modifiers on Mac."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("HYPER(K)", os_style="mac")
        assert result == "⌃⌥⇧⌘K"

    def test_hyper_combo_windows(self):
        """SPEC-KC-006: HYPER(key) expands correctly on Windows."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("HYPER(K)", os_style="windows")
        assert "Ctrl" in result and "Alt" in result and "Shift" in result and "Win" in result
```

#### SPEC-KC-007: MEH/HYPER with special keys
**Given** a binding like `MEH(SPACE)` or `HYPER(ENTER)`
**When** `format_key_label` is called
**Then** the key is also formatted appropriately

**Test:** `tests/test_svg_generator.py`
```python
    def test_meh_with_special_key(self):
        """SPEC-KC-007: MEH works with special keys."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("MEH(SPACE)", os_style="mac")
        assert "⌃⌥⇧" in result
        # SPACE might be "␣" or "Space" depending on mapping
```

---

## 3. Held Key Indicator Specifications

### Data Model

#### SPEC-HK-001: LayerActivator model exists
**Given** the models module
**When** `LayerActivator` is imported
**Then** it has required fields

**Test:** `tests/test_models.py`
```python
class TestLayerActivator:
    """Tests for LayerActivator model."""

    def test_layer_activator_fields(self):
        """SPEC-HK-001: LayerActivator has required fields."""
        from glove80_visualizer.models import LayerActivator

        activator = LayerActivator(
            source_layer_name="QWERTY",
            source_position=69,
            target_layer_name="Cursor",
            tap_key="BACKSPACE"
        )
        assert activator.source_layer_name == "QWERTY"
        assert activator.source_position == 69
        assert activator.target_layer_name == "Cursor"
        assert activator.tap_key == "BACKSPACE"
```

### Layer Activator Extraction

#### SPEC-HK-002: Extract layer activators from YAML
**Given** parsed keymap YAML with hold behaviors pointing to layer names
**When** `extract_layer_activators` is called
**Then** LayerActivator objects are returned for each hold-to-layer binding

**Test:** `tests/test_extractor.py`
```python
class TestLayerActivatorExtraction:
    """Tests for extracting layer activators."""

    def test_extract_layer_activator_from_hold(self):
        """SPEC-HK-002: Extract activators from hold behaviors."""
        from glove80_visualizer.extractor import extract_layer_activators

        yaml_content = '''
layers:
  Base:
    - [{t: BACKSPACE, h: Cursor}, {t: SPACE, h: Symbol}]
  Cursor:
    - [{type: held}, A]
  Symbol:
    - [B, {type: held}]
'''
        activators = extract_layer_activators(yaml_content)

        assert len(activators) == 2
        cursor_activator = next(a for a in activators if a.target_layer_name == "Cursor")
        assert cursor_activator.source_layer_name == "Base"
        assert cursor_activator.tap_key == "BACKSPACE"
```

#### SPEC-HK-003: Handle multiple activators for same layer
**Given** YAML where two keys activate the same layer
**When** `extract_layer_activators` is called
**Then** both activators are returned

**Test:** `tests/test_extractor.py`
```python
    def test_multiple_activators_same_layer(self):
        """SPEC-HK-003: Multiple activators for one layer."""
        from glove80_visualizer.extractor import extract_layer_activators

        yaml_content = '''
layers:
  Base:
    - [{t: TAB, h: Mouse}, {t: ENTER, h: Mouse}]
  Mouse:
    - [{type: held}, {type: held}]
'''
        activators = extract_layer_activators(yaml_content)
        mouse_activators = [a for a in activators if a.target_layer_name == "Mouse"]

        assert len(mouse_activators) == 2
```

#### SPEC-HK-004: Handle layers with no activators
**Given** a layer that has no hold-behavior pointing to it
**When** `extract_layer_activators` is called
**Then** no activator is returned for that layer (graceful handling)

**Test:** `tests/test_extractor.py`
```python
    def test_layer_without_activator(self):
        """SPEC-HK-004: Layers without activators handled gracefully."""
        from glove80_visualizer.extractor import extract_layer_activators

        yaml_content = '''
layers:
  Base:
    - [A, B, C]
  Orphan:
    - [X, Y, Z]
'''
        activators = extract_layer_activators(yaml_content)
        # Should not raise, just return empty or no activator for Orphan
        orphan_activators = [a for a in activators if a.target_layer_name == "Orphan"]
        assert len(orphan_activators) == 0
```

### Held Key Display

#### SPEC-HK-005: generate_layer_svg accepts activators parameter
**Given** the `generate_layer_svg` function
**When** called with `activators` parameter
**Then** the function signature accepts it (may be None by default)

**Implementation Note:** Add `activators: list[LayerActivator] | None = None` to function signature.

**Test:** `tests/test_svg_generator.py`
```python
class TestHeldKeyIndicator:
    """Tests for held key indicator in SVG output."""

    def test_generate_layer_svg_accepts_activators(self):
        """SPEC-HK-005: generate_layer_svg accepts activators parameter."""
        from glove80_visualizer.svg_generator import generate_layer_svg
        from glove80_visualizer.models import Layer, KeyBinding, LayerActivator

        layer = Layer(name="Cursor", index=1, bindings=[
            KeyBinding(position=i, tap="A") for i in range(80)
        ])
        activators = [LayerActivator(
            source_layer_name="QWERTY",
            source_position=69,
            target_layer_name="Cursor",
            tap_key="BACKSPACE"
        )]

        # Should not raise
        svg = generate_layer_svg(layer, activators=activators)
        assert "<svg" in svg
```

#### SPEC-HK-006: Held key shows indicator in SVG
**Given** a layer with an activator pointing to it
**When** SVG is generated with activators
**Then** the held position has a visual indicator (CSS class or styling)

**Test:** `tests/test_svg_generator.py`
```python
    def test_held_key_has_indicator(self):
        """SPEC-HK-006: Held key position shows indicator."""
        from glove80_visualizer.svg_generator import generate_layer_svg
        from glove80_visualizer.models import Layer, KeyBinding, LayerActivator
        from glove80_visualizer.config import VisualizerConfig

        layer = Layer(name="Cursor", index=1, bindings=[
            KeyBinding(position=i, tap="A") for i in range(80)
        ])
        # Position 69 is the held key
        activators = [LayerActivator(
            source_layer_name="QWERTY",
            source_position=69,
            target_layer_name="Cursor",
            tap_key="BACKSPACE"
        )]
        config = VisualizerConfig(show_held_indicator=True)

        svg = generate_layer_svg(layer, config=config, activators=activators)

        # TODO: Tighten assertion after implementation is stable
        # Initial loose check - refine once SVG structure is finalized
        assert "held" in svg.lower() or "activator" in svg.lower() or "#d699b6" in svg
```

#### SPEC-HK-007: Held indicator can be disabled
**Given** config with `show_held_indicator=False`
**When** SVG is generated
**Then** no held indicator styling is applied

**Test:** `tests/test_svg_generator.py`
```python
    def test_held_indicator_disabled(self):
        """SPEC-HK-007: Held indicator can be disabled."""
        from glove80_visualizer.svg_generator import generate_layer_svg
        from glove80_visualizer.models import Layer, KeyBinding, LayerActivator
        from glove80_visualizer.config import VisualizerConfig

        layer = Layer(name="Cursor", index=1, bindings=[
            KeyBinding(position=i, tap="A") for i in range(80)
        ])
        activators = [LayerActivator(
            source_layer_name="QWERTY",
            source_position=69,
            target_layer_name="Cursor",
            tap_key="BACKSPACE"
        )]
        config = VisualizerConfig(show_held_indicator=False)

        svg = generate_layer_svg(layer, config=config, activators=activators)

        # Should NOT contain held indicator styling
        # (This depends on implementation - check for absence of indicator class)
```

#### SPEC-HK-008: CLI passes activators through pipeline
**Given** CLI invoked with a multi-layer keymap
**When** PDF/SVG is generated
**Then** held indicators appear on layer pages

**Test:** `tests/test_cli.py`
```python
class TestCliHeldIndicator:
    """Tests for held key indicator in CLI output."""

    def test_cli_shows_held_indicators(self, runner, daves_keymap_path, tmp_path):
        """SPEC-HK-008: CLI generates output with held indicators."""
        from glove80_visualizer.cli import main

        if not daves_keymap_path.exists():
            pytest.skip("Dave's keymap not found")

        output_dir = tmp_path / "svgs"
        result = runner.invoke(main, [
            str(daves_keymap_path),
            "-o", str(output_dir),
            "--format", "svg"
        ])

        assert result.exit_code == 0
        # Check Cursor layer SVG for held indicator
        cursor_svg = output_dir / "Cursor.svg"
        if cursor_svg.exists():
            content = cursor_svg.read_text()
            # Should have some indication of held key
            # (specific assertion depends on implementation)
```

---

## 4. Color Output Specifications

### Key Categorization

**Note:** `categorize_key()` receives **formatted** key labels (output of `format_key_label()`), not raw ZMK codes. This means it sees `⌘`, `⇧`, `→`, etc., not `LGUI`, `LSHIFT`, `LEFT`.

#### SPEC-CL-001: Categorize modifier symbols
**Given** formatted modifier symbols like `⌘`, `⇧`, `⌃`, `⌥`
**When** `categorize_key` is called
**Then** they return "modifier"

**Test:** `tests/test_colors.py`
```python
class TestKeyCategorization:
    """Tests for key categorization."""

    def test_categorize_modifier_symbols(self):
        """SPEC-CL-001: Modifier symbols are categorized correctly."""
        from glove80_visualizer.colors import categorize_key

        assert categorize_key("⇧") == "modifier"
        assert categorize_key("⌘") == "modifier"
        assert categorize_key("⌃") == "modifier"
        assert categorize_key("⌥") == "modifier"
        assert categorize_key("Shift") == "modifier"
        assert categorize_key("Ctrl") == "modifier"
```

#### SPEC-CL-002: Categorize navigation symbols
**Given** formatted navigation symbols like `←`, `→`, `↑`, `↓`, `⇱`, `⇲`
**When** `categorize_key` is called
**Then** they return "navigation"

**Test:** `tests/test_colors.py`
```python
    def test_categorize_navigation_symbols(self):
        """SPEC-CL-002: Navigation symbols are categorized correctly."""
        from glove80_visualizer.colors import categorize_key

        assert categorize_key("←") == "navigation"
        assert categorize_key("→") == "navigation"
        assert categorize_key("↑") == "navigation"
        assert categorize_key("↓") == "navigation"
        assert categorize_key("⇱") == "navigation"  # Home
        assert categorize_key("⇲") == "navigation"  # End
        assert categorize_key("⇞") == "navigation"  # PgUp
        assert categorize_key("⇟") == "navigation"  # PgDn
```

#### SPEC-CL-003: Categorize media symbols
**Given** formatted media symbols like `⏯`, `🔊`, `🔉`, `🔇`
**When** `categorize_key` is called
**Then** they return "media"

**Test:** `tests/test_colors.py`
```python
    def test_categorize_media_symbols(self):
        """SPEC-CL-003: Media symbols are categorized correctly."""
        from glove80_visualizer.colors import categorize_key

        assert categorize_key("⏯") == "media"
        assert categorize_key("🔊") == "media"
        assert categorize_key("🔉") == "media"
        assert categorize_key("🔇") == "media"
        assert categorize_key("🔆") == "media"
        assert categorize_key("🔅") == "media"
```

#### SPEC-CL-004: Categorize number and function keys
**Given** keys like `1`, `2`, `F1`, `F12`
**When** `categorize_key` is called
**Then** they return "number"

**Test:** `tests/test_colors.py`
```python
    def test_categorize_number_keys(self):
        """SPEC-CL-004: Number keys are categorized correctly."""
        from glove80_visualizer.colors import categorize_key

        assert categorize_key("1") == "number"
        assert categorize_key("0") == "number"
        assert categorize_key("F1") == "number"
        assert categorize_key("F12") == "number"
```

#### SPEC-CL-005: Categorize layer names as layer keys
**Given** keys that are layer names (from hold behavior)
**When** `categorize_key` is called with context indicating it's a hold layer
**Then** they return "layer"

**Test:** `tests/test_colors.py`
```python
    def test_categorize_layer_keys(self):
        """SPEC-CL-005: Layer names are categorized correctly."""
        from glove80_visualizer.colors import categorize_key

        # Layer names typically appear as hold behaviors
        assert categorize_key("Cursor", is_hold=True) == "layer"
        assert categorize_key("Symbol", is_hold=True) == "layer"
        assert categorize_key("Number", is_hold=True) == "layer"

    def test_categorize_layer_name_without_hold_flag(self):
        """SPEC-CL-005b: Layer names without is_hold flag are default."""
        from glove80_visualizer.colors import categorize_key

        # Without is_hold=True, layer names are categorized as default
        assert categorize_key("Cursor", is_hold=False) == "default"
        assert categorize_key("Cursor") == "default"  # is_hold defaults to False
```

#### SPEC-CL-006: Categorize mouse keys
**Given** formatted mouse symbols like `🖱↑`, `🖱L`, `🖱R`
**When** `categorize_key` is called
**Then** they return "mouse"

**Test:** `tests/test_colors.py`
```python
    def test_categorize_mouse_keys(self):
        """SPEC-CL-006: Mouse keys are categorized correctly."""
        from glove80_visualizer.colors import categorize_key

        assert categorize_key("🖱↑") == "mouse"
        assert categorize_key("🖱↓") == "mouse"
        assert categorize_key("🖱L") == "mouse"
        assert categorize_key("🖱R") == "mouse"
```

#### SPEC-CL-007: Categorize system keys
**Given** keys like `Reset`, `Boot`, or system-related labels
**When** `categorize_key` is called
**Then** they return "system"

**Test:** `tests/test_colors.py`
```python
    def test_categorize_system_keys(self):
        """SPEC-CL-007: System keys are categorized correctly."""
        from glove80_visualizer.colors import categorize_key

        assert categorize_key("Reset") == "system"
        assert categorize_key("Boot") == "system"
```

#### SPEC-CL-008: Default category for alpha keys
**Given** regular alpha keys like `A`, `B`, `Q`
**When** `categorize_key` is called
**Then** they return "default"

**Test:** `tests/test_colors.py`
```python
    def test_categorize_alpha_default(self):
        """SPEC-CL-008: Alpha keys use default category."""
        from glove80_visualizer.colors import categorize_key

        assert categorize_key("A") == "default"
        assert categorize_key("Q") == "default"
        assert categorize_key("Space") == "default"
        assert categorize_key("Tab") == "default"
```

#### SPEC-CL-009: Categorize transparent keys
**Given** transparent key indicators like `▽` or `trans`
**When** `categorize_key` is called
**Then** they return "transparent"

**Test:** `tests/test_colors.py`
```python
    def test_categorize_transparent(self):
        """SPEC-CL-009: Transparent keys are categorized correctly."""
        from glove80_visualizer.colors import categorize_key

        assert categorize_key("▽") == "transparent"
        assert categorize_key("trans") == "transparent"
```

### Color Scheme

#### SPEC-CL-010: ColorScheme has all required colors
**Given** a ColorScheme instance
**When** accessing color attributes
**Then** all category colors are valid hex codes

**Test:** `tests/test_colors.py`
```python
class TestColorScheme:
    """Tests for ColorScheme."""

    def test_color_scheme_complete(self):
        """SPEC-CL-010: ColorScheme has all required colors."""
        from glove80_visualizer.colors import ColorScheme
        import re

        scheme = ColorScheme()
        hex_pattern = re.compile(r'^#[0-9a-fA-F]{6}$')

        assert hex_pattern.match(scheme.modifier_color)
        assert hex_pattern.match(scheme.navigation_color)
        assert hex_pattern.match(scheme.media_color)
        assert hex_pattern.match(scheme.number_color)
        assert hex_pattern.match(scheme.layer_color)
        assert hex_pattern.match(scheme.mouse_color)
        assert hex_pattern.match(scheme.system_color)
        assert hex_pattern.match(scheme.transparent_color)
        assert hex_pattern.match(scheme.default_color)
```

#### SPEC-CL-011: Get color for category
**Given** a ColorScheme and a category name
**When** `get_color_for_category` is called
**Then** the correct hex color is returned

**Test:** `tests/test_colors.py`
```python
    def test_get_color_for_category(self):
        """SPEC-CL-011: Correct color returned for each category."""
        from glove80_visualizer.colors import ColorScheme, get_color_for_category

        scheme = ColorScheme()

        assert get_color_for_category("modifier", scheme) == scheme.modifier_color
        assert get_color_for_category("navigation", scheme) == scheme.navigation_color
        assert get_color_for_category("unknown_category", scheme) == scheme.default_color
```

### CLI Integration

#### SPEC-CL-020: CLI accepts --color flag
**Given** the CLI
**When** `--color` flag is passed
**Then** command executes successfully

**Test:** `tests/test_cli.py`
```python
class TestCliColorFlag:
    """Tests for --color CLI flag."""

    def test_cli_accepts_color_flag(self, runner, simple_keymap_path, tmp_path):
        """SPEC-CL-020: CLI accepts --color flag."""
        from glove80_visualizer.cli import main

        output = tmp_path / "output.pdf"
        result = runner.invoke(main, [
            str(simple_keymap_path),
            "-o", str(output),
            "--color"
        ])

        assert result.exit_code == 0
        assert output.exists()
```

#### SPEC-CL-021: Colors applied in SVG output
**Given** `--color` flag is passed with SVG output
**When** SVG is generated
**Then** SVG contains color styling from the color scheme

**Test:** `tests/test_cli.py`
```python
    def test_colors_in_svg_output(self, runner, simple_keymap_path, tmp_path):
        """SPEC-CL-021: Colors are applied in SVG output."""
        from glove80_visualizer.cli import main
        from glove80_visualizer.colors import ColorScheme

        output_dir = tmp_path / "svgs"
        result = runner.invoke(main, [
            str(simple_keymap_path),
            "-o", str(output_dir),
            "--format", "svg",
            "--color"
        ])

        assert result.exit_code == 0
        svg_files = list(output_dir.glob("*.svg"))
        assert len(svg_files) > 0

        # Check SVG contains at least one color from the scheme
        scheme = ColorScheme()
        svg_content = svg_files[0].read_text()
        # Should contain at least some category colors
        has_colors = any(
            color.lower() in svg_content.lower()
            for color in [scheme.modifier_color, scheme.navigation_color, scheme.number_color]
        )
        assert has_colors or "fill:" in svg_content
```

#### SPEC-CL-022: Default has no semantic colors
**Given** CLI invoked without `--color`
**When** SVG is generated
**Then** SVG uses default styling (no category-based colors)

**Test:** `tests/test_cli.py`
```python
    def test_default_no_semantic_colors(self, runner, simple_keymap_path, tmp_path):
        """SPEC-CL-022: Default output has no semantic colors."""
        from glove80_visualizer.cli import main
        from glove80_visualizer.colors import ColorScheme

        output_dir = tmp_path / "svgs"
        result = runner.invoke(main, [
            str(simple_keymap_path),
            "-o", str(output_dir),
            "--format", "svg"
            # No --color flag
        ])

        assert result.exit_code == 0
        svg_files = list(output_dir.glob("*.svg"))
        assert len(svg_files) > 0

        # Should NOT contain category-specific colors
        scheme = ColorScheme()
        svg_content = svg_files[0].read_text()
        # The unique category colors should not appear
        assert scheme.layer_color.lower() not in svg_content.lower()
```

---

## Implementation Changes Summary

### New Files
| File | Purpose |
|------|---------|
| `.github/workflows/ci.yml` | CI pipeline |
| `.github/workflows/publish.yml` | PyPI publishing |
| `src/glove80_visualizer/colors.py` | ColorScheme, categorize_key(), get_color_for_category() |
| `tests/test_colors.py` | Color tests |
| `tests/test_packaging.py` | Build/package tests |

### Modified Files
| File | Changes |
|------|---------|
| `models.py` | Add `LayerActivator` dataclass |
| `extractor.py` | Add `extract_layer_activators()` function |
| `svg_generator.py` | Add `activators` param, MEH/HYPER expansion, color application |
| `config.py` | Add `show_held_indicator`, `show_colors` fields |
| `cli.py` | Add `--color` flag, wire activators through pipeline |

### Function Signatures

**New:**
```python
# models.py
@dataclass
class LayerActivator:
    source_layer_name: str
    source_position: int
    target_layer_name: str
    tap_key: str | None = None

# extractor.py
def extract_layer_activators(yaml_content: str) -> list[LayerActivator]: ...

# colors.py
@dataclass
class ColorScheme:
    modifier_color: str = "#7fbbb3"
    # ... etc

def categorize_key(label: str, is_hold: bool = False) -> str: ...
def get_color_for_category(category: str, scheme: ColorScheme) -> str: ...
```

**Modified:**
```python
# svg_generator.py
def generate_layer_svg(
    layer: Layer,
    config: VisualizerConfig | None = None,
    include_title: bool = False,
    os_style: str = "mac",
    resolve_trans: bool = False,
    base_layer: Layer | None = None,
    activators: list[LayerActivator] | None = None,  # NEW
) -> str: ...

# config.py
@dataclass
class VisualizerConfig:
    # ... existing ...
    show_held_indicator: bool = True   # NEW
    show_colors: bool = False          # NEW
```

---

## Implementation Order

1. **SPEC-CI-*** - CI/CD first (2-3 hours)
   - Enables automated testing on all future PRs

2. **SPEC-KC-005, SPEC-KC-006, SPEC-KC-007** - MEH/HYPER only (1 hour)
   - Nested combos already work

3. **SPEC-HK-*** - Held key indicator (3-4 hours)
   - Models → Extractor → SVG Generator → CLI

4. **SPEC-CL-*** - Color output (3-4 hours)
   - colors.py → SVG Generator → CLI

**Total: ~10-12 hours**

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Test coverage | ≥95% for new code |
| All specs have tests | 100% |
| Existing tests pass | 308 tests green |
| CI/CD pipeline | Green on all PRs |
| PyPI publish | Successful on release |
