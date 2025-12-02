# Glove80 Keymap Visualizer - TDD Specifications

This document contains detailed specifications for test-driven development. Each module has its specifications defined before implementation.

## Testing Philosophy

1. **Red-Green-Refactor**: Write failing tests first, then implement to pass, then refactor
2. **Unit Tests**: Each module tested in isolation with mocked dependencies
3. **Integration Tests**: End-to-end tests with real keymap files
4. **Fixtures**: Minimal keymap files that exercise specific features

---

## Module: `models.py`

### Purpose
Define data structures used throughout the application.

### Specifications

#### `KeyBinding` dataclass

```python
# SPEC-M001: KeyBinding stores tap behavior
def test_key_binding_tap_only():
    """A KeyBinding can represent a simple key tap."""
    binding = KeyBinding(position=0, tap="A")
    assert binding.position == 0
    assert binding.tap == "A"
    assert binding.hold is None

# SPEC-M002: KeyBinding stores hold-tap behavior
def test_key_binding_hold_tap():
    """A KeyBinding can represent a hold-tap behavior."""
    binding = KeyBinding(position=5, tap="A", hold="LSHIFT")
    assert binding.tap == "A"
    assert binding.hold == "LSHIFT"

# SPEC-M003: KeyBinding stores layer-tap behavior
def test_key_binding_layer_tap():
    """A KeyBinding can represent a layer-tap behavior."""
    binding = KeyBinding(position=10, tap="SPACE", hold="LAYER_Symbol")
    assert binding.hold == "LAYER_Symbol"

# SPEC-M004: KeyBinding handles transparent keys
def test_key_binding_transparent():
    """A KeyBinding can represent a transparent key."""
    binding = KeyBinding(position=0, tap="&trans")
    assert binding.tap == "&trans"
    assert binding.is_transparent is True

# SPEC-M005: KeyBinding handles none keys
def test_key_binding_none():
    """A KeyBinding can represent a none/blocked key."""
    binding = KeyBinding(position=0, tap="&none")
    assert binding.is_none is True
```

#### `Layer` dataclass

```python
# SPEC-M010: Layer has name and index
def test_layer_basic():
    """A Layer has a name, index, and list of bindings."""
    layer = Layer(name="QWERTY", index=0, bindings=[])
    assert layer.name == "QWERTY"
    assert layer.index == 0
    assert layer.bindings == []

# SPEC-M011: Layer validates binding count for Glove80
def test_layer_binding_count():
    """A Glove80 layer should have exactly 80 key bindings."""
    bindings = [KeyBinding(position=i, tap="X") for i in range(80)]
    layer = Layer(name="Test", index=0, bindings=bindings)
    assert len(layer.bindings) == 80

# SPEC-M012: Layer allows partial bindings during construction
def test_layer_partial_bindings():
    """Layers can be constructed with partial bindings for flexibility."""
    layer = Layer(name="Test", index=0, bindings=[])
    assert layer.is_complete is False
```

#### `VisualizerConfig` dataclass

```python
# SPEC-M020: Config has sensible defaults
def test_config_defaults():
    """VisualizerConfig has sensible default values."""
    config = VisualizerConfig()
    assert config.keyboard == "glove80"
    assert config.page_size == "letter"
    assert config.orientation == "landscape"

# SPEC-M021: Config can be customized
def test_config_custom():
    """VisualizerConfig can be customized."""
    config = VisualizerConfig(page_size="a4", font_size=14)
    assert config.page_size == "a4"
    assert config.font_size == 14

# SPEC-M022: Config can load from YAML file
def test_config_from_yaml():
    """VisualizerConfig can be loaded from a YAML file."""
    yaml_content = "page_size: a4\nfont_size: 16"
    config = VisualizerConfig.from_yaml(yaml_content)
    assert config.page_size == "a4"
    assert config.font_size == 16
```

---

## Module: `parser.py`

### Purpose
Parse ZMK `.keymap` files into intermediate YAML representation using keymap-drawer.

### Specifications

```python
# SPEC-P001: Parse simple keymap file
def test_parse_simple_keymap(simple_keymap_path):
    """Parser can parse a minimal ZMK keymap file."""
    result = parse_zmk_keymap(simple_keymap_path)
    assert result is not None
    assert isinstance(result, str)  # YAML string
    assert "layers:" in result

# SPEC-P002: Parse keymap with multiple layers
def test_parse_multiple_layers(multi_layer_keymap_path):
    """Parser extracts all layers from a keymap."""
    result = parse_zmk_keymap(multi_layer_keymap_path)
    yaml_data = yaml.safe_load(result)
    assert len(yaml_data["layers"]) >= 2

# SPEC-P003: Handle keymap with custom behaviors
def test_parse_custom_behaviors(keymap_with_behaviors_path):
    """Parser handles keymaps with custom ZMK behaviors."""
    result = parse_zmk_keymap(keymap_with_behaviors_path)
    assert result is not None
    # Custom behaviors should be preserved or mapped

# SPEC-P004: Handle missing file gracefully
def test_parse_missing_file():
    """Parser raises FileNotFoundError for missing files."""
    with pytest.raises(FileNotFoundError):
        parse_zmk_keymap(Path("/nonexistent/keymap.keymap"))

# SPEC-P005: Handle invalid keymap syntax
def test_parse_invalid_keymap(invalid_keymap_path):
    """Parser raises ParseError for invalid keymap syntax."""
    with pytest.raises(KeymapParseError):
        parse_zmk_keymap(invalid_keymap_path)

# SPEC-P006: Parse keymap with hold-tap behaviors
def test_parse_hold_tap(keymap_with_hold_tap_path):
    """Parser correctly identifies hold-tap key bindings."""
    result = parse_zmk_keymap(keymap_with_hold_tap_path)
    yaml_data = yaml.safe_load(result)
    # Verify hold-tap is represented in output
    layer_data = yaml_data["layers"]["layer_0"]
    assert any("t" in str(key) and "h" in str(key) for key in layer_data)

# SPEC-P007: Specify Glove80 as keyboard type
def test_parse_specifies_glove80():
    """Parser uses Glove80 as the keyboard type."""
    result = parse_zmk_keymap(simple_keymap_path, keyboard="glove80")
    yaml_data = yaml.safe_load(result)
    assert yaml_data.get("layout", {}).get("zmk_keyboard") == "glove80"

# SPEC-P008: Parse real-world complex keymap
def test_parse_daves_keymap(daves_keymap_path):
    """Parser can handle Dave's full keymap with 32 layers."""
    result = parse_zmk_keymap(daves_keymap_path)
    yaml_data = yaml.safe_load(result)
    assert len(yaml_data["layers"]) == 32
```

---

## Module: `extractor.py`

### Purpose
Extract structured layer information from parsed YAML.

### Specifications

```python
# SPEC-E001: Extract layers from YAML
def test_extract_layers_basic():
    """Extractor creates Layer objects from YAML."""
    yaml_content = """
    layers:
      QWERTY:
        - [A, B, C]
    """
    layers = extract_layers(yaml_content)
    assert len(layers) == 1
    assert layers[0].name == "QWERTY"

# SPEC-E002: Preserve layer order
def test_extract_layers_order():
    """Extractor preserves the order of layers."""
    yaml_content = """
    layers:
      First:
        - [A]
      Second:
        - [B]
      Third:
        - [C]
    """
    layers = extract_layers(yaml_content)
    assert [l.name for l in layers] == ["First", "Second", "Third"]

# SPEC-E003: Assign correct indices
def test_extract_layers_indices():
    """Extractor assigns correct indices to layers."""
    yaml_content = """
    layers:
      Base:
        - [A]
      Upper:
        - [B]
    """
    layers = extract_layers(yaml_content)
    assert layers[0].index == 0
    assert layers[1].index == 1

# SPEC-E004: Extract key bindings
def test_extract_key_bindings():
    """Extractor creates KeyBinding objects for each key."""
    yaml_content = """
    layers:
      Test:
        - [Q, W, E, R, T]
    """
    layers = extract_layers(yaml_content)
    assert layers[0].bindings[0].tap == "Q"
    assert layers[0].bindings[4].tap == "T"

# SPEC-E005: Extract hold-tap bindings
def test_extract_hold_tap():
    """Extractor parses hold-tap representations."""
    yaml_content = """
    layers:
      Test:
        - [{t: A, h: LSHIFT}]
    """
    layers = extract_layers(yaml_content)
    binding = layers[0].bindings[0]
    assert binding.tap == "A"
    assert binding.hold == "LSHIFT"

# SPEC-E006: Handle empty layers
def test_extract_empty_layer():
    """Extractor handles layers with no bindings."""
    yaml_content = """
    layers:
      Empty: []
    """
    layers = extract_layers(yaml_content)
    assert layers[0].bindings == []

# SPEC-E007: Filter layers by name
def test_extract_filter_by_name():
    """Extractor can filter to specific layers."""
    yaml_content = """
    layers:
      Keep:
        - [A]
      Skip:
        - [B]
    """
    layers = extract_layers(yaml_content, include=["Keep"])
    assert len(layers) == 1
    assert layers[0].name == "Keep"

# SPEC-E008: Exclude layers by name
def test_extract_exclude_by_name():
    """Extractor can exclude specific layers."""
    yaml_content = """
    layers:
      Keep:
        - [A]
      Skip:
        - [B]
    """
    layers = extract_layers(yaml_content, exclude=["Skip"])
    assert len(layers) == 1
    assert layers[0].name == "Keep"
```

---

## Module: `svg_generator.py`

### Purpose
Generate SVG diagrams for keyboard layers using keymap-drawer.

### Specifications

```python
# SPEC-S001: Generate SVG for single layer
def test_generate_svg_basic(sample_layer):
    """Generator produces valid SVG for a layer."""
    svg = generate_layer_svg(sample_layer)
    assert svg.startswith("<?xml") or svg.startswith("<svg")
    assert "</svg>" in svg

# SPEC-S002: SVG contains layer name
def test_svg_contains_layer_name(sample_layer):
    """Generated SVG includes the layer name."""
    svg = generate_layer_svg(sample_layer, include_title=True)
    assert sample_layer.name in svg

# SPEC-S003: SVG contains key labels
def test_svg_contains_key_labels(sample_layer):
    """Generated SVG includes key labels."""
    svg = generate_layer_svg(sample_layer)
    for binding in sample_layer.bindings[:5]:  # Check first 5
        if binding.tap and binding.tap not in ("&trans", "&none"):
            assert binding.tap in svg

# SPEC-S004: SVG uses Glove80 layout
def test_svg_glove80_layout():
    """Generated SVG uses correct Glove80 physical layout."""
    layer = Layer(name="Test", index=0, bindings=[
        KeyBinding(position=i, tap="X") for i in range(80)
    ])
    svg = generate_layer_svg(layer)
    # Glove80 has 80 keys - verify reasonable SVG size
    assert svg.count("<rect") >= 80 or svg.count("<path") >= 80

# SPEC-S005: Apply custom styling
def test_svg_custom_styling():
    """Generator applies custom styling configuration."""
    config = VisualizerConfig(
        background_color="#000000",
        text_color="#ffffff"
    )
    layer = Layer(name="Test", index=0, bindings=[])
    svg = generate_layer_svg(layer, config=config)
    assert "#000000" in svg or "background" in svg.lower()

# SPEC-S006: Handle transparent keys
def test_svg_transparent_keys():
    """Generator correctly renders transparent keys."""
    layer = Layer(name="Test", index=0, bindings=[
        KeyBinding(position=0, tap="&trans")
    ])
    svg = generate_layer_svg(layer)
    # Transparent keys should have specific styling or be blank
    assert svg is not None

# SPEC-S007: Handle hold-tap display
def test_svg_hold_tap_display():
    """Generator shows both tap and hold for hold-tap keys."""
    layer = Layer(name="Test", index=0, bindings=[
        KeyBinding(position=0, tap="A", hold="LSHIFT")
    ])
    svg = generate_layer_svg(layer)
    assert "A" in svg
    # Hold behavior should be shown (possibly abbreviated)

# SPEC-S008: Generate SVG batch efficiently
def test_generate_svg_batch(sample_layers):
    """Generator can efficiently produce SVGs for multiple layers."""
    svgs = generate_all_layer_svgs(sample_layers)
    assert len(svgs) == len(sample_layers)
    assert all(svg.startswith("<?xml") or svg.startswith("<svg") for svg in svgs)
```

---

## Module: `pdf_generator.py`

### Purpose
Convert SVG diagrams to PDF pages and combine into a single document.

### Specifications

```python
# SPEC-D001: Convert SVG to PDF
def test_svg_to_pdf_basic(sample_svg):
    """Generator converts SVG to PDF bytes."""
    pdf_bytes = svg_to_pdf(sample_svg)
    assert pdf_bytes.startswith(b"%PDF")

# SPEC-D002: PDF has correct page size
def test_pdf_page_size():
    """Generated PDF has specified page size."""
    config = VisualizerConfig(page_size="letter", orientation="landscape")
    pdf_bytes = svg_to_pdf(sample_svg, config=config)
    # Verify dimensions (letter landscape: 792x612 points)
    assert len(pdf_bytes) > 0

# SPEC-D003: Merge multiple PDFs
def test_merge_pdfs(sample_pdf_pages):
    """Generator merges multiple PDF pages into one document."""
    merged = merge_pdfs(sample_pdf_pages)
    assert merged.startswith(b"%PDF")
    # Verify page count matches input

# SPEC-D004: Add page headers
def test_pdf_with_headers(sample_svg, sample_layer):
    """Generator can add layer name as page header."""
    pdf_bytes = svg_to_pdf(
        sample_svg,
        header=f"Layer {sample_layer.index}: {sample_layer.name}"
    )
    assert len(pdf_bytes) > 0

# SPEC-D005: Generate table of contents
def test_pdf_table_of_contents(sample_layers, sample_svgs):
    """Generator can create a table of contents page."""
    pdf_bytes = generate_pdf_with_toc(
        layers=sample_layers,
        svgs=sample_svgs,
        include_toc=True
    )
    # TOC should be first page
    assert len(pdf_bytes) > 0

# SPEC-D006: Handle large documents
def test_pdf_large_document():
    """Generator handles documents with 32+ layers."""
    layers = [Layer(name=f"Layer{i}", index=i, bindings=[]) for i in range(32)]
    svgs = ["<svg></svg>"] * 32
    pdf_bytes = generate_pdf_with_toc(layers=layers, svgs=svgs)
    assert len(pdf_bytes) > 0

# SPEC-D007: Output to file
def test_pdf_output_to_file(tmp_path, sample_svg):
    """Generator can write PDF to file."""
    output_path = tmp_path / "output.pdf"
    svg_to_pdf_file(sample_svg, output_path)
    assert output_path.exists()
    assert output_path.read_bytes().startswith(b"%PDF")
```

---

## Module: `cli.py`

### Purpose
Command-line interface for the visualizer.

### Specifications

```python
# SPEC-C001: Basic invocation
def test_cli_basic(runner, simple_keymap_path, tmp_path):
    """CLI generates PDF from keymap file."""
    output = tmp_path / "output.pdf"
    result = runner.invoke(main, [str(simple_keymap_path), "-o", str(output)])
    assert result.exit_code == 0
    assert output.exists()

# SPEC-C002: List layers option
def test_cli_list_layers(runner, simple_keymap_path):
    """CLI can list available layers without generating PDF."""
    result = runner.invoke(main, [str(simple_keymap_path), "--list-layers"])
    assert result.exit_code == 0
    assert "QWERTY" in result.output or "layer" in result.output.lower()

# SPEC-C003: Select specific layers
def test_cli_select_layers(runner, multi_layer_keymap_path, tmp_path):
    """CLI can generate PDF for specific layers only."""
    output = tmp_path / "output.pdf"
    result = runner.invoke(main, [
        str(multi_layer_keymap_path),
        "-o", str(output),
        "--layers", "QWERTY,Symbol"
    ])
    assert result.exit_code == 0

# SPEC-C004: Output format option
def test_cli_svg_output(runner, simple_keymap_path, tmp_path):
    """CLI can output SVG files instead of PDF."""
    output_dir = tmp_path / "svgs"
    result = runner.invoke(main, [
        str(simple_keymap_path),
        "-o", str(output_dir),
        "--format", "svg"
    ])
    assert result.exit_code == 0
    assert any(output_dir.glob("*.svg"))

# SPEC-C005: Help message
def test_cli_help(runner):
    """CLI shows help message."""
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "keymap" in result.output.lower()
    assert "output" in result.output.lower()

# SPEC-C006: Missing file error
def test_cli_missing_file(runner):
    """CLI shows error for missing input file."""
    result = runner.invoke(main, ["/nonexistent/file.keymap"])
    assert result.exit_code != 0
    assert "not found" in result.output.lower() or "error" in result.output.lower()

# SPEC-C007: Verbose output
def test_cli_verbose(runner, simple_keymap_path, tmp_path):
    """CLI shows progress in verbose mode."""
    output = tmp_path / "output.pdf"
    result = runner.invoke(main, [
        str(simple_keymap_path),
        "-o", str(output),
        "-v"
    ])
    assert result.exit_code == 0
    assert "layer" in result.output.lower() or "generating" in result.output.lower()

# SPEC-C008: Config file option
def test_cli_config_file(runner, simple_keymap_path, tmp_path):
    """CLI can load configuration from file."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("page_size: a4\n")
    output = tmp_path / "output.pdf"
    result = runner.invoke(main, [
        str(simple_keymap_path),
        "-o", str(output),
        "--config", str(config_file)
    ])
    assert result.exit_code == 0

# SPEC-C009: Continue on error flag
def test_cli_continue_on_error(runner, multi_layer_keymap_path, tmp_path, mocker):
    """CLI continues processing when --continue-on-error is set and a layer fails."""
    output = tmp_path / "output.pdf"
    # Mock svg_generator to fail on one specific layer
    mocker.patch(
        'glove80_visualizer.svg_generator.generate_layer_svg',
        side_effect=lambda layer, **kwargs: (
            ValueError("Simulated render failure")
            if layer.name == "FailLayer"
            else "<svg></svg>"
        )
    )
    result = runner.invoke(main, [
        str(multi_layer_keymap_path),
        "-o", str(output),
        "--continue-on-error"
    ])
    # Should succeed (exit 0) if at least one layer rendered
    assert result.exit_code == 0
    assert output.exists()
    # Should warn about skipped layer
    assert "skipped" in result.output.lower() or "failed" in result.output.lower()

# SPEC-C010: Continue on error - all fail
def test_cli_continue_on_error_all_fail(runner, simple_keymap_path, tmp_path, mocker):
    """CLI exits with error if --continue-on-error is set but ALL layers fail."""
    output = tmp_path / "output.pdf"
    mocker.patch(
        'glove80_visualizer.svg_generator.generate_layer_svg',
        side_effect=ValueError("All layers fail")
    )
    result = runner.invoke(main, [
        str(simple_keymap_path),
        "-o", str(output),
        "--continue-on-error"
    ])
    assert result.exit_code != 0
    assert "error" in result.output.lower()

# SPEC-C011: Default behavior without continue-on-error
def test_cli_fail_fast_default(runner, simple_keymap_path, tmp_path, mocker):
    """CLI fails immediately on first error by default (no --continue-on-error)."""
    output = tmp_path / "output.pdf"
    mocker.patch(
        'glove80_visualizer.svg_generator.generate_layer_svg',
        side_effect=ValueError("Render failed")
    )
    result = runner.invoke(main, [
        str(simple_keymap_path),
        "-o", str(output),
    ])
    assert result.exit_code != 0
    assert not output.exists()
```

---

## Integration Tests

### Purpose
Test the complete pipeline with real keymap files.

### Specifications

```python
# SPEC-I001: End-to-end with simple keymap
def test_e2e_simple_keymap(simple_keymap_path, tmp_path):
    """Complete pipeline works with minimal keymap."""
    output = tmp_path / "output.pdf"
    result = generate_visualization(simple_keymap_path, output)
    assert result.success
    assert output.exists()
    assert output.stat().st_size > 1000  # Reasonable PDF size

# SPEC-I002: End-to-end with Dave's keymap
def test_e2e_daves_keymap(daves_keymap_path, tmp_path):
    """Complete pipeline works with full 32-layer keymap."""
    output = tmp_path / "daves_layers.pdf"
    result = generate_visualization(daves_keymap_path, output)
    assert result.success
    assert output.exists()
    # Should have reasonable size for 32 pages
    assert output.stat().st_size > 50000

# SPEC-I003: Verify all layers present
def test_e2e_all_layers_present(daves_keymap_path, tmp_path):
    """All 32 layers are included in output PDF."""
    output = tmp_path / "output.pdf"
    generate_visualization(daves_keymap_path, output)

    from PyPDF2 import PdfReader
    reader = PdfReader(str(output))
    # 32 layers + optional TOC page
    assert len(reader.pages) >= 32

# SPEC-I004: Performance benchmark
def test_e2e_performance(daves_keymap_path, tmp_path):
    """Pipeline completes within reasonable time."""
    import time
    output = tmp_path / "output.pdf"

    start = time.time()
    generate_visualization(daves_keymap_path, output)
    duration = time.time() - start

    # Should complete within 60 seconds
    assert duration < 60
```

---

## Test Fixtures

### Fixture Files to Create

1. **`fixtures/simple.keymap`**: Minimal valid keymap with 1-2 layers
2. **`fixtures/multi_layer.keymap`**: Keymap with 4+ layers
3. **`fixtures/hold_tap.keymap`**: Keymap demonstrating hold-tap behaviors
4. **`fixtures/invalid.keymap`**: Invalid keymap for error testing
5. **`fixtures/behaviors.keymap`**: Keymap with custom ZMK behaviors

### Pytest Fixtures (`conftest.py`)

```python
import pytest
from pathlib import Path

@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent / "fixtures"

@pytest.fixture
def simple_keymap_path(fixtures_dir):
    return fixtures_dir / "simple.keymap"

@pytest.fixture
def daves_keymap_path():
    return Path("daves-current-glove80-keymap.keymap")

@pytest.fixture
def sample_layer():
    from glove80_visualizer.models import Layer, KeyBinding
    return Layer(
        name="TestLayer",
        index=0,
        bindings=[KeyBinding(position=i, tap=chr(65 + i % 26)) for i in range(80)]
    )

@pytest.fixture
def runner():
    from click.testing import CliRunner
    return CliRunner()
```
