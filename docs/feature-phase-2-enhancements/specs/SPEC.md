# Phase 2 Enhancements - TDD Specification

## Overview

This specification defines the test-first requirements for Phase 2 enhancements. Each specification has a unique ID for traceability.

**Specification Format:**
- `SPEC-CI-XXX`: CI/CD and PyPI publishing
- `SPEC-KC-XXX`: Key combo display
- `SPEC-HK-XXX`: Held key indicator
- `SPEC-CL-XXX`: Color output

---

## 1. CI/CD & PyPI Publishing Specifications

### GitHub Actions CI

#### SPEC-CI-001: Tests run on pull request
**Given** a pull request is opened or updated
**When** the CI workflow runs
**Then** all pytest tests execute and must pass

**Test file:** `tests/test_ci.py` (integration test, can be manual verification)

#### SPEC-CI-002: Linting runs on pull request
**Given** a pull request is opened or updated
**When** the CI workflow runs
**Then** ruff linting executes with zero errors

#### SPEC-CI-003: Type checking runs on pull request
**Given** a pull request is opened or updated
**When** the CI workflow runs
**Then** mypy type checking executes with zero errors

#### SPEC-CI-004: Tests run on multiple Python versions
**Given** a pull request is opened or updated
**When** the CI workflow runs
**Then** tests execute on Python 3.10, 3.11, 3.12, and 3.13

### PyPI Publishing

#### SPEC-CI-005: Package builds successfully
**Given** the pyproject.toml is properly configured
**When** `python -m build` is executed
**Then** both wheel (.whl) and source distribution (.tar.gz) are created

**Test:**
```python
def test_package_builds(tmp_path):
    """Package builds without errors."""
    import subprocess
    result = subprocess.run(
        ["python", "-m", "build", "--outdir", str(tmp_path)],
        capture_output=True, text=True
    )
    assert result.returncode == 0
    assert any(tmp_path.glob("*.whl"))
    assert any(tmp_path.glob("*.tar.gz"))
```

#### SPEC-CI-006: Package version matches tag
**Given** a GitHub release is created with tag `v0.2.0`
**When** the publish workflow runs
**Then** the published package version is `0.2.0`

#### SPEC-CI-007: Release triggers PyPI publish
**Given** a GitHub release is created
**When** the release is published
**Then** the package is uploaded to PyPI automatically

---

## 2. Key Combo Display Specifications

### ZMK Modifier Parsing

#### SPEC-KC-001: Parse single modifier combo
**Given** a key binding `LG(K)`
**When** `format_key_label` is called with `os_style="mac"`
**Then** the result is `⌘K`

**Test:**
```python
def test_single_modifier_combo_mac():
    """SPEC-KC-001: Single modifier combo displays correctly on Mac."""
    from glove80_visualizer.svg_generator import format_key_label

    assert format_key_label("LG(K)", os_style="mac") == "⌘K"
    assert format_key_label("LS(K)", os_style="mac") == "⇧K"
    assert format_key_label("LC(K)", os_style="mac") == "⌃K"
    assert format_key_label("LA(K)", os_style="mac") == "⌥K"
```

#### SPEC-KC-002: Parse single modifier combo (Windows)
**Given** a key binding `LG(K)`
**When** `format_key_label` is called with `os_style="windows"`
**Then** the result is `Win+K`

**Test:**
```python
def test_single_modifier_combo_windows():
    """SPEC-KC-002: Single modifier combo displays correctly on Windows."""
    from glove80_visualizer.svg_generator import format_key_label

    assert format_key_label("LG(K)", os_style="windows") == "Win+K"
    assert format_key_label("LS(K)", os_style="windows") == "Shift+K"
    assert format_key_label("LC(K)", os_style="windows") == "Ctrl+K"
    assert format_key_label("LA(K)", os_style="windows") == "Alt+K"
```

#### SPEC-KC-003: Parse nested modifier combo
**Given** a key binding `LG(LS(K))`
**When** `format_key_label` is called with `os_style="mac"`
**Then** the result is `⌘⇧K`

**Test:**
```python
def test_nested_modifier_combo():
    """SPEC-KC-003: Nested modifier combos parse correctly."""
    from glove80_visualizer.svg_generator import format_key_label

    assert format_key_label("LG(LS(K))", os_style="mac") == "⌘⇧K"
    assert format_key_label("LC(LA(K))", os_style="mac") == "⌃⌥K"
    assert format_key_label("LG(LC(LS(K)))", os_style="mac") == "⌘⌃⇧K"
```

#### SPEC-KC-004: Parse triple modifier combo
**Given** a key binding `LG(LC(LS(K)))`
**When** `format_key_label` is called
**Then** all three modifiers are shown in consistent order

**Test:**
```python
def test_triple_modifier_combo():
    """SPEC-KC-004: Triple modifier combos display correctly."""
    from glove80_visualizer.svg_generator import format_key_label

    result = format_key_label("LG(LC(LS(K)))", os_style="mac")
    assert "⌘" in result
    assert "⌃" in result
    assert "⇧" in result
    assert "K" in result
```

#### SPEC-KC-005: Parse MEH combo
**Given** a key binding `MEH(K)` (Ctrl+Alt+Shift)
**When** `format_key_label` is called
**Then** the result shows all three modifiers

**Test:**
```python
def test_meh_combo():
    """SPEC-KC-005: MEH macro expands to Ctrl+Alt+Shift."""
    from glove80_visualizer.svg_generator import format_key_label

    result = format_key_label("MEH(K)", os_style="mac")
    assert result == "⌃⌥⇧K"
```

#### SPEC-KC-006: Parse HYPER combo
**Given** a key binding `HYPER(K)` (Ctrl+Alt+Shift+GUI)
**When** `format_key_label` is called
**Then** the result shows all four modifiers

**Test:**
```python
def test_hyper_combo():
    """SPEC-KC-006: HYPER macro expands to all modifiers."""
    from glove80_visualizer.svg_generator import format_key_label

    result = format_key_label("HYPER(K)", os_style="mac")
    assert result == "⌃⌥⇧⌘K"
```

#### SPEC-KC-007: Handle right-side modifiers
**Given** a key binding `RG(K)` (Right GUI)
**When** `format_key_label` is called
**Then** the result is the same as left-side modifier

**Test:**
```python
def test_right_side_modifiers():
    """SPEC-KC-007: Right-side modifiers display same as left."""
    from glove80_visualizer.svg_generator import format_key_label

    assert format_key_label("RG(K)", os_style="mac") == "⌘K"
    assert format_key_label("RS(K)", os_style="mac") == "⇧K"
    assert format_key_label("RC(K)", os_style="mac") == "⌃K"
    assert format_key_label("RA(K)", os_style="mac") == "⌥K"
```

#### SPEC-KC-008: Modifier order is consistent
**Given** multiple modifier combos with different nesting orders
**When** displayed
**Then** modifiers appear in canonical order: Ctrl, Alt, Shift, GUI

**Test:**
```python
def test_modifier_order_consistent():
    """SPEC-KC-008: Modifiers display in consistent order."""
    from glove80_visualizer.svg_generator import format_key_label

    # Different nesting orders should produce same display order
    result1 = format_key_label("LG(LC(K))", os_style="mac")
    result2 = format_key_label("LC(LG(K))", os_style="mac")
    # Both should have ⌃ before ⌘
    assert result1 == result2  # or both contain same symbols
```

---

## 3. Held Key Indicator Specifications

### Layer Activator Extraction

#### SPEC-HK-001: Extract layer-tap activator
**Given** a keymap with `&lt 2 SPACE` on layer 0
**When** layers are extracted
**Then** a `LayerActivator` is created showing position activates layer 2

**Test:**
```python
def test_extract_layer_tap_activator():
    """SPEC-HK-001: Layer-tap keys are identified as activators."""
    from glove80_visualizer.extractor import extract_layers, extract_layer_activators

    yaml_content = '''
layers:
  Base:
    - [{t: SPC, h: Layer2}]
  Layer2:
    - [A]
'''
    layers = extract_layers(yaml_content)
    activators = extract_layer_activators(yaml_content)

    assert len(activators) >= 1
    activator = activators[0]
    assert activator.source_layer == 0
    assert activator.target_layer == 2  # or "Layer2"
    assert activator.activation_type == "layer-tap"
```

#### SPEC-HK-002: Extract momentary layer activator
**Given** a keymap with `&mo 1` on layer 0
**When** layers are extracted
**Then** a `LayerActivator` is created for momentary layer 1

**Test:**
```python
def test_extract_momentary_activator():
    """SPEC-HK-002: Momentary layer keys are identified."""
    from glove80_visualizer.extractor import extract_layer_activators

    yaml_content = '''
layers:
  Base:
    - [{t: Layer1, type: held}]
  Layer1:
    - [A]
'''
    activators = extract_layer_activators(yaml_content)

    assert any(a.activation_type == "momentary" for a in activators)
```

#### SPEC-HK-003: Extract toggle layer activator
**Given** a keymap with `&to 1` on layer 0
**When** layers are extracted
**Then** a `LayerActivator` is created for toggle layer 1

**Test:**
```python
def test_extract_toggle_activator():
    """SPEC-HK-003: Toggle layer keys are identified."""
    from glove80_visualizer.extractor import extract_layer_activators

    # Test with toggle binding
    # Implementation depends on how keymap-drawer represents &to
```

#### SPEC-HK-004: Multiple activators for same layer
**Given** a keymap where two different keys activate layer 2
**When** layers are extracted
**Then** both activators are recorded

**Test:**
```python
def test_multiple_activators_same_layer():
    """SPEC-HK-004: Multiple activators for one layer are all tracked."""
    from glove80_visualizer.extractor import extract_layer_activators

    yaml_content = '''
layers:
  Base:
    - [{t: SPC, h: Layer2}, {t: TAB, h: Layer2}]
  Layer2:
    - [A, B]
'''
    activators = extract_layer_activators(yaml_content)
    layer2_activators = [a for a in activators if a.target_layer == 2]

    assert len(layer2_activators) == 2
```

### Held Key Display

#### SPEC-HK-005: Show held indicator on layer page
**Given** a layer that is activated by holding a key
**When** that layer is rendered to SVG
**Then** the activating key position shows a held indicator

**Test:**
```python
def test_held_indicator_in_svg():
    """SPEC-HK-005: Held keys are visually indicated in SVG."""
    from glove80_visualizer.svg_generator import generate_layer_svg
    from glove80_visualizer.models import Layer, KeyBinding, LayerActivator

    layer = Layer(name="Test", index=2, bindings=[
        KeyBinding(position=0, tap="A")
    ])
    activator = LayerActivator(
        source_layer=0,
        source_position=5,
        target_layer=2,
        activation_type="layer-tap"
    )

    svg = generate_layer_svg(layer, activators=[activator])

    # Should contain held indicator class or element
    assert "held" in svg.lower() or "activator" in svg.lower()
```

#### SPEC-HK-006: Held indicator uses correct style
**Given** config with `held_indicator_style="border"`
**When** layer with held key is rendered
**Then** SVG contains border styling for that key

**Test:**
```python
def test_held_indicator_border_style():
    """SPEC-HK-006: Border style held indicator renders correctly."""
    from glove80_visualizer.svg_generator import generate_layer_svg
    from glove80_visualizer.config import VisualizerConfig

    config = VisualizerConfig(held_indicator_style="border")
    # ... generate SVG ...
    # Assert border styling present
```

#### SPEC-HK-007: Disable held indicator
**Given** config with `show_held_indicator=False`
**When** layer is rendered
**Then** no held indicator appears

**Test:**
```python
def test_held_indicator_disabled():
    """SPEC-HK-007: Held indicator can be disabled."""
    from glove80_visualizer.svg_generator import generate_layer_svg
    from glove80_visualizer.config import VisualizerConfig

    config = VisualizerConfig(show_held_indicator=False)
    # ... generate SVG ...
    # Assert no held indicator present
```

---

## 4. Color Output Specifications

### Key Categorization

#### SPEC-CL-001: Categorize modifier keys
**Given** key labels like "LSHIFT", "LCTRL", "LGUI", "LALT"
**When** `categorize_key` is called
**Then** they return "modifier"

**Test:**
```python
def test_categorize_modifier_keys():
    """SPEC-CL-001: Modifier keys are categorized correctly."""
    from glove80_visualizer.colors import categorize_key

    assert categorize_key("LSHIFT") == "modifier"
    assert categorize_key("LCTRL") == "modifier"
    assert categorize_key("LGUI") == "modifier"
    assert categorize_key("LALT") == "modifier"
    assert categorize_key("⇧") == "modifier"
    assert categorize_key("⌘") == "modifier"
```

#### SPEC-CL-002: Categorize navigation keys
**Given** key labels like "LEFT", "RIGHT", "UP", "DOWN", "HOME", "END"
**When** `categorize_key` is called
**Then** they return "navigation"

**Test:**
```python
def test_categorize_navigation_keys():
    """SPEC-CL-002: Navigation keys are categorized correctly."""
    from glove80_visualizer.colors import categorize_key

    assert categorize_key("LEFT") == "navigation"
    assert categorize_key("→") == "navigation"
    assert categorize_key("HOME") == "navigation"
    assert categorize_key("PG_UP") == "navigation"
```

#### SPEC-CL-003: Categorize media keys
**Given** key labels like "C_PLAY", "C_VOL_UP", "C_BRI_DN"
**When** `categorize_key` is called
**Then** they return "media"

**Test:**
```python
def test_categorize_media_keys():
    """SPEC-CL-003: Media keys are categorized correctly."""
    from glove80_visualizer.colors import categorize_key

    assert categorize_key("C_PLAY") == "media"
    assert categorize_key("⏯") == "media"
    assert categorize_key("🔊") == "media"
```

#### SPEC-CL-004: Categorize number keys
**Given** key labels like "N1", "N2", "F1", "F12"
**When** `categorize_key` is called
**Then** they return "number"

**Test:**
```python
def test_categorize_number_keys():
    """SPEC-CL-004: Number keys are categorized correctly."""
    from glove80_visualizer.colors import categorize_key

    assert categorize_key("N1") == "number"
    assert categorize_key("1") == "number"
    assert categorize_key("F1") == "number"
    assert categorize_key("F12") == "number"
```

#### SPEC-CL-005: Categorize layer keys
**Given** key labels that activate layers
**When** `categorize_key` is called
**Then** they return "layer"

**Test:**
```python
def test_categorize_layer_keys():
    """SPEC-CL-005: Layer activation keys are categorized correctly."""
    from glove80_visualizer.colors import categorize_key

    assert categorize_key("Layer1") == "layer"
    assert categorize_key("&mo 1") == "layer"
    assert categorize_key("Symbol") == "layer"
```

#### SPEC-CL-006: Categorize system keys
**Given** key labels like "RESET", "BOOTLOADER"
**When** `categorize_key` is called
**Then** they return "system"

**Test:**
```python
def test_categorize_system_keys():
    """SPEC-CL-006: System keys are categorized correctly."""
    from glove80_visualizer.colors import categorize_key

    assert categorize_key("RESET") == "system"
    assert categorize_key("BOOTLOADER") == "system"
    assert categorize_key("&sys_reset") == "system"
```

#### SPEC-CL-007: Default category for alpha keys
**Given** key labels like "A", "B", "Q", "W"
**When** `categorize_key` is called
**Then** they return "default"

**Test:**
```python
def test_categorize_alpha_keys():
    """SPEC-CL-007: Alpha keys use default category."""
    from glove80_visualizer.colors import categorize_key

    assert categorize_key("A") == "default"
    assert categorize_key("Q") == "default"
    assert categorize_key("SPACE") == "default"
```

### Color Scheme

#### SPEC-CL-010: ColorScheme has all required colors
**Given** a ColorScheme instance
**When** accessing color attributes
**Then** all category colors are defined

**Test:**
```python
def test_color_scheme_complete():
    """SPEC-CL-010: ColorScheme has all required colors."""
    from glove80_visualizer.colors import ColorScheme

    scheme = ColorScheme()

    assert scheme.modifier_color
    assert scheme.navigation_color
    assert scheme.media_color
    assert scheme.number_color
    assert scheme.layer_color
    assert scheme.system_color
    assert scheme.transparent_color
    assert scheme.held_key_color
    assert scheme.default_color
```

#### SPEC-CL-011: Get color for category
**Given** a ColorScheme and a key category
**When** `get_color_for_category` is called
**Then** the correct hex color is returned

**Test:**
```python
def test_get_color_for_category():
    """SPEC-CL-011: Correct color returned for each category."""
    from glove80_visualizer.colors import ColorScheme, get_color_for_category

    scheme = ColorScheme()

    assert get_color_for_category("modifier", scheme) == scheme.modifier_color
    assert get_color_for_category("navigation", scheme) == scheme.navigation_color
    assert get_color_for_category("unknown", scheme) == scheme.default_color
```

### CLI Integration

#### SPEC-CL-020: CLI accepts --color flag
**Given** the CLI
**When** `--color` flag is passed
**Then** output is generated with colors

**Test:**
```python
def test_cli_color_flag(runner, simple_keymap_path, tmp_path):
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
**Given** `--color` flag is passed
**When** SVG is generated
**Then** CSS contains color definitions for categories

**Test:**
```python
def test_colors_in_svg_output(runner, simple_keymap_path, tmp_path):
    """SPEC-CL-021: Colors are applied in SVG output."""
    from glove80_visualizer.cli import main

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

    # Check SVG contains color styling
    svg_content = svg_files[0].read_text()
    assert "#" in svg_content  # Hex colors present
```

#### SPEC-CL-022: Default is no color
**Given** CLI is invoked without `--color`
**When** output is generated
**Then** no semantic colors are applied (uses default styling)

**Test:**
```python
def test_default_no_color(runner, simple_keymap_path, tmp_path):
    """SPEC-CL-022: Default output has no semantic colors."""
    from glove80_visualizer.cli import main

    output = tmp_path / "output.pdf"
    result = runner.invoke(main, [
        str(simple_keymap_path),
        "-o", str(output)
    ])

    assert result.exit_code == 0
    # Color-specific assertions would go here
```

---

## Test File Organization

### New Test Files
| File | Specifications |
|------|----------------|
| `tests/test_colors.py` | SPEC-CL-001 through SPEC-CL-011 |
| `tests/test_key_combos.py` | SPEC-KC-001 through SPEC-KC-008 |
| `tests/test_held_indicator.py` | SPEC-HK-001 through SPEC-HK-007 |

### Modified Test Files
| File | New Tests |
|------|-----------|
| `tests/test_cli.py` | SPEC-CL-020 through SPEC-CL-022 |
| `tests/test_extractor.py` | SPEC-HK-001 through SPEC-HK-004 |
| `tests/test_svg_generator.py` | SPEC-HK-005 through SPEC-HK-007 |

---

## Implementation Order

1. **SPEC-CI-*** - CI/CD first (enables automated testing)
2. **SPEC-KC-*** - Key combos (foundational for display)
3. **SPEC-CL-*** - Colors (categorization used by held indicator)
4. **SPEC-HK-*** - Held indicator (depends on extraction and colors)

---

## Fixtures Required

### New Fixtures (tests/conftest.py)

```python
@pytest.fixture
def combo_keymap_path(tmp_path):
    """Keymap with modifier combos."""
    keymap = tmp_path / "combo.keymap"
    keymap.write_text('''
/ {
    keymap {
        compatible = "zmk,keymap";
        Base {
            bindings = <&kp LG(K) &kp LG(LS(K)) &kp MEH(K)>;
        };
    };
};
''')
    return keymap

@pytest.fixture
def multi_activator_keymap_path(tmp_path):
    """Keymap with multiple layer activators."""
    keymap = tmp_path / "multi_activator.keymap"
    keymap.write_text('''
/ {
    keymap {
        compatible = "zmk,keymap";
        Base {
            bindings = <&lt 1 SPACE &lt 1 TAB &mo 2>;
        };
        Layer1 {
            bindings = <&kp A &kp B &kp C>;
        };
        Layer2 {
            bindings = <&kp X &kp Y &kp Z>;
        };
    };
};
''')
    return keymap
```

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Test coverage | ≥95% for new code |
| All specs have tests | 100% |
| CI/CD pipeline | Green on all PRs |
| PyPI publish | Successful v0.2.0 release |
