# Glove80 Keymap Visualizer - Project Plan

## Overview

This project creates a tool that generates PDF visualizations of Glove80 keyboard layers from ZMK keymap files, similar to [sunaku's layer diagrams](https://sunaku.github.io/moergo-glove80-keyboard-layers.pdf).

## Goals

1. **Primary Goal**: Generate a multi-page PDF where each page displays one keyboard layer with all key bindings visualized
2. **Input**: Standard ZMK `.keymap` files (as exported from MoErgo Glove80 Layout Editor)
3. **Output**: A single PDF file with one page per layer, showing the Glove80 keyboard layout with key labels

## Architecture

### High-Level Pipeline

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  ZMK Keymap     │     │  Keymap YAML    │     │  SVG Diagrams   │     │  PDF Document   │
│  (.keymap)      │────▶│  (intermediate) │────▶│  (per layer)    │────▶│  (combined)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │                       │
        ▼                       ▼                       ▼                       ▼
   keymap-drawer           keymap-drawer           CairoSVG              PyPDF2
     (parse)                 (draw)               (convert)             (merge)
```

### Component Breakdown

#### 1. Keymap Parser (`parser.py`)
- **Responsibility**: Parse ZMK `.keymap` files and extract layer information
- **Approach**: Leverage `keymap-drawer`'s built-in ZMK parser
- **Output**: Structured representation of layers and key bindings

#### 2. Layer Extractor (`extractor.py`)
- **Responsibility**: Extract individual layers from parsed keymap data
- **Input**: Parsed keymap YAML
- **Output**: List of layer definitions with names and bindings

#### 3. SVG Generator (`svg_generator.py`)
- **Responsibility**: Generate SVG diagrams for each layer
- **Approach**: Use `keymap-drawer`'s draw functionality with Glove80 physical layout
- **Customization**: Apply styling (colors, fonts, key labels)
- **Output**: SVG content for each layer

#### 4. PDF Generator (`pdf_generator.py`)
- **Responsibility**: Convert SVGs to PDF pages and combine
- **Approach**:
  - Use CairoSVG to convert each SVG to PDF
  - Use PyPDF2 to merge individual PDFs into one document
- **Features**:
  - Add layer name as page header
  - Optional table of contents
  - Configurable page size and orientation

#### 5. CLI Interface (`cli.py`)
- **Responsibility**: Command-line interface for the tool
- **Framework**: Click
- **Commands**:
  - `glove80-viz <keymap-file> -o <output.pdf>` - Generate full PDF
  - `glove80-viz <keymap-file> --layers <layer1,layer2>` - Generate specific layers
  - `glove80-viz <keymap-file> --list-layers` - List available layers
  - `glove80-viz <keymap-file> --format svg` - Output SVGs instead of PDF

#### 6. Configuration (`config.py`)
- **Responsibility**: Handle configuration and styling options
- **Features**:
  - Default Glove80 physical layout
  - Customizable color schemes
  - Key label formatting rules
  - Page layout options

### Data Flow

```python
# Conceptual data flow
keymap_file: Path = "my-keymap.keymap"

# Step 1: Parse keymap to intermediate YAML
keymap_yaml: str = parser.parse_zmk_keymap(keymap_file)

# Step 2: Extract layer information
layers: List[Layer] = extractor.extract_layers(keymap_yaml)

# Step 3: Generate SVG for each layer
svgs: List[SVGContent] = [
    svg_generator.generate_layer_svg(layer, config)
    for layer in layers
]

# Step 4: Convert to PDF
pdf_pages: List[bytes] = [
    pdf_generator.svg_to_pdf(svg)
    for svg in svgs
]

# Step 5: Combine into single PDF
final_pdf: bytes = pdf_generator.merge_pdfs(pdf_pages)
```

### keymap-drawer Integration Details

**Tested and verified** on 2025-12-01 with keymap-drawer 0.22.1.

#### Parser Invocation
```bash
keymap parse -z <keymap-file>
# Returns YAML to stdout, errors to stderr with exit code 1
```

#### YAML Output Format

**Simple keys** (single string):
```yaml
layers:
  Base: [F1, F2, Q, W, E, R, T]  # Flat list for simple layers
```

**Hold-tap keys** (dict with `t` and `h`):
```yaml
- {t: A, h: LGUI}     # tap: A, hold: LGUI (left GUI/Cmd)
- {t: BSPC, h: Symbol}  # tap: Backspace, hold: Symbol layer
```

**Transparent keys**:
```yaml
- {t: ▽, type: trans}   # Transparent - inherits from layer below
```

**Held keys** (layer activator):
```yaml
- {type: held}          # This key activates this layer
```

**None/blocked keys**:
```yaml
- ''                    # Empty string = &none in ZMK
```

#### Error Handling

keymap-drawer raises `ParseError` for invalid keymaps:
```
keymap_drawer.parse.parse.ParseError: Could not find any keymap nodes with "zmk,keymap" compatible property
```

We must catch this and provide actionable error messages.

## Key Data Structures

### Layer
```python
@dataclass
class Layer:
    name: str                    # e.g., "QWERTY", "Cursor", "Symbol"
    index: int                   # Layer number (0-31)
    bindings: List[KeyBinding]   # 80 key bindings for Glove80
```

### KeyBinding
```python
@dataclass
class KeyBinding:
    position: int                # Key position (0-79)
    tap: str                     # Tap behavior label
    hold: Optional[str]          # Hold behavior label (for hold-tap)
    tap_dance: Optional[List[str]]  # Tap dance sequence
```

### VisualizerConfig
```python
@dataclass
class VisualizerConfig:
    # Physical layout
    keyboard: str = "glove80"

    # Styling
    key_width: int = 60
    key_height: int = 56
    font_size: int = 12
    background_color: str = "#ffffff"
    key_color: str = "#f0f0f0"
    text_color: str = "#000000"
    hold_text_color: str = "#666666"

    # PDF options
    page_size: str = "letter"  # or "a4"
    orientation: str = "landscape"
    include_toc: bool = True
    layer_title_format: str = "Layer {index}: {name}"
```

## Dependencies

### Runtime Dependencies
| Package | Purpose | Version |
|---------|---------|---------|
| keymap-drawer | Parse ZMK keymaps, generate SVG | >=0.18.0 |
| cairosvg | Convert SVG to PDF | >=2.7.0 |
| PyPDF2 | Merge PDF pages | >=3.0.0 |
| pyyaml | Parse/generate YAML | >=6.0 |
| click | CLI framework | >=8.0.0 |

### Development Dependencies
| Package | Purpose |
|---------|---------|
| pytest | Testing framework |
| pytest-cov | Coverage reporting |
| pytest-mock | Mocking support |
| black | Code formatting |
| ruff | Linting |
| mypy | Type checking |

### System Dependencies
- **Cairo**: Required by CairoSVG for PDF rendering
  - macOS: `brew install cairo`
  - Ubuntu: `apt-get install libcairo2-dev`

## File Structure

```
glove80-keymap-visualizer/
├── src/
│   └── glove80_visualizer/
│       ├── __init__.py
│       ├── cli.py              # CLI entry point
│       ├── parser.py           # ZMK keymap parsing
│       ├── extractor.py        # Layer extraction
│       ├── svg_generator.py    # SVG generation
│       ├── pdf_generator.py    # PDF conversion/merging
│       ├── config.py           # Configuration handling
│       └── models.py           # Data models
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── test_parser.py
│   ├── test_extractor.py
│   ├── test_svg_generator.py
│   ├── test_pdf_generator.py
│   ├── test_cli.py
│   ├── test_integration.py
│   └── fixtures/               # Test keymap files
│       ├── simple.keymap
│       ├── multi_layer.keymap
│       ├── hold_tap.keymap
│       └── invalid.keymap
├── docs/
│   └── {git-branch-name}/      # Branch-specific docs
│       ├── plans/
│       │   └── PLAN.md         # This document
│       ├── specs/
│       │   └── SPEC.md         # TDD specifications
│       └── reviews/            # CTO review history
├── .claude/
│   └── commands/
│       └── review-this.md      # CTO review command
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── Makefile
├── CLAUDE.md
├── README.md
└── .gitignore
```

## Implementation Phases

### Phase 1: Foundation ✅ Complete
- [x] Project structure and packaging
- [x] Development environment setup
- [x] Plan and specifications
- [x] Test fixtures and TDD specs

### Phase 2: Core Pipeline (Current)
- [ ] Implement parser module with tests
- [ ] Implement extractor module with tests
- [ ] Implement SVG generator with tests
- [ ] Implement PDF generator with tests

### Phase 3: Integration
- [ ] End-to-end pipeline integration
- [ ] CLI implementation
- [ ] Integration tests with real keymap files

### Phase 4: Polish
- [ ] Error handling and validation
- [ ] Configuration file support
- [ ] Documentation and examples
- [ ] Performance optimization for large keymaps

## Success Criteria

1. **Functional**: Generate readable PDF from `daves-current-glove80-keymap.keymap`
2. **Complete**: All 32 layers rendered correctly
3. **Accurate**: Key labels match actual keymap bindings
4. **Readable**: Clear typography, appropriate sizing
5. **Maintainable**: >80% test coverage, type-annotated code

## Error Handling Matrix

Every external dependency has defined failure modes and recovery strategies.

| Component | Failure Mode | Error Type | User Message | Recovery |
|-----------|--------------|------------|--------------|----------|
| **File I/O** | File not found | `FileNotFoundError` | "Keymap file not found: {path}" | Exit with code 1 |
| **File I/O** | Permission denied | `PermissionError` | "Cannot read keymap file: {path}" | Exit with code 1 |
| **File I/O** | File too large | `ValueError` | "Keymap file exceeds 10MB limit" | Exit with code 1 |
| **keymap-drawer** | Invalid syntax | `KeymapParseError` | "Invalid keymap syntax: {detail}" | Exit with code 1 |
| **keymap-drawer** | Missing keymap node | `KeymapParseError` | "No keymap found - is this a valid ZMK file?" | Exit with code 1 |
| **keymap-drawer** | Unsupported behavior | N/A | Log warning, use raw name | Continue with fallback |
| **CairoSVG** | Cairo not installed | `OSError` | "Cairo library not found. Install: brew install cairo" | Exit with code 1 |
| **CairoSVG** | Invalid SVG | `ValueError` | "Failed to render layer {name}: {detail}" | Skip layer, warn user |
| **PyPDF2** | Merge failure | `PdfReadError` | "Failed to combine PDFs" | Exit with code 1 |
| **Disk** | Output write failed | `IOError` | "Cannot write to {path}: {reason}" | Exit with code 1 |

### Error Handling Principles

1. **Fail fast for blocking errors**: Invalid input, missing dependencies
2. **Continue with warnings for recoverable errors**: Single layer fails, use fallback for unknown behaviors
3. **Always provide actionable messages**: Include what went wrong AND how to fix it
4. **Include context**: File paths, layer names, line numbers where available

### Partial Success Mode

When `--continue-on-error` is passed:
- Skip layers that fail to render
- Generate PDF with successful layers
- Report which layers were skipped and why
- Exit code 0 if any layers succeeded, 1 if all failed

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| keymap-drawer API changes | High | Pin version, add integration tests |
| Complex ZMK macros not rendering | Medium | Fallback to raw behavior names |
| Large keymaps slow to process | Low | Add progress indicators, optimize |
| Cairo installation issues | Medium | Document system deps, add Docker option |

## References

- [keymap-drawer documentation](https://github.com/caksoylar/keymap-drawer)
- [sunaku's Glove80 keymaps](https://github.com/sunaku/glove80-keymaps)
- [ZMK keymap format](https://zmk.dev/docs/config)
- [Glove80 Layout Editor](https://my.glove80.com/)
