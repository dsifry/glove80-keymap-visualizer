# Glove80 Keymap Visualizer

Generate PDF visualizations of Glove80 keyboard layers from ZMK keymap files.

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
[![CI](https://github.com/dsifry/glove80-keymap-visualizer/actions/workflows/ci.yml/badge.svg)](https://github.com/dsifry/glove80-keymap-visualizer/actions/workflows/ci.yml)

## Overview

This tool parses ZMK `.keymap` files (as exported from the MoErgo Glove80 Layout Editor) and generates beautiful PDF documents showing each keyboard layer, similar to [sunaku's layer diagrams](https://sunaku.github.io/moergo-glove80-keyboard-layers.pdf).

## Features

- Parse ZMK keymap files with support for complex behaviors (hold-tap, layer-tap, etc.)
- Generate SVG diagrams for each layer
- Combine layers into a single PDF with optional table of contents
- **OS-specific modifier symbols** - Mac (⌘⌥⌃⇧), Windows (Win+Ctrl+Alt+Shift), or Linux
- **MEH/HYPER key expansion** - `MEH(K)` displays as `⌃⌥⇧K` on Mac
- **Held key indicators** - Shows which key activates each layer
- **Semantic coloring** - Optional color coding for modifiers, navigation, media keys, etc.
- **Transparent key resolution** - Show inherited keys instead of "trans" markers
- Filter to specific layers or exclude unwanted ones

## Quick Start

### 1. Install Prerequisites

**macOS:**
```bash
brew install cairo python@3.12
```

**Ubuntu/Debian:**
```bash
sudo apt-get install libcairo2-dev python3.12
```

### 2. Install the Package

```bash
# Clone and install
git clone https://github.com/dsifry/glove80-keymap-visualizer.git
cd glove80-keymap-visualizer
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .
```

### 3. Generate Your First Visualization

```bash
# Basic PDF generation
glove80-viz your-keymap.keymap -o layers.pdf

# With Mac symbols (default)
glove80-viz your-keymap.keymap -o layers.pdf --mac

# With Windows symbols
glove80-viz your-keymap.keymap -o layers.pdf --windows

# With semantic colors
glove80-viz your-keymap.keymap -o layers.pdf --color

# Show inherited keys instead of transparent markers
glove80-viz your-keymap.keymap -o layers.pdf --resolve-trans
```

## Usage

### Basic Commands

```bash
# Generate PDF with all layers
glove80-viz my-keymap.keymap -o my-layers.pdf

# Generate SVG files instead
glove80-viz my-keymap.keymap -o ./svgs --format svg

# List available layers
glove80-viz my-keymap.keymap --list-layers

# Get help
glove80-viz --help
```

### Advanced Options

```bash
# Generate specific layers only
glove80-viz my-keymap.keymap -o layers.pdf --layers QWERTY,Symbol,Cursor

# Exclude specific layers
glove80-viz my-keymap.keymap -o layers.pdf --exclude-layers Factory,Magic

# Use custom configuration
glove80-viz my-keymap.keymap -o layers.pdf --config my-config.yaml

# Verbose output
glove80-viz my-keymap.keymap -o layers.pdf -v

# Resolve transparent keys using a specific base layer
glove80-viz my-keymap.keymap -o layers.pdf --resolve-trans --base-layer QWERTY
```

### All CLI Options

| Option | Description |
|--------|-------------|
| `-o, --output` | Output file path (PDF) or directory (SVG) |
| `--format` | Output format: `pdf` (default) or `svg` |
| `--layers` | Comma-separated list of layer names to include |
| `--exclude-layers` | Comma-separated list of layer names to exclude |
| `--list-layers` | List available layers and exit |
| `--config` | Path to YAML configuration file |
| `--mac` | Use Mac modifier symbols (⌘⌥⌃⇧) - default |
| `--windows` | Use Windows modifier symbols |
| `--linux` | Use Linux modifier symbols |
| `--resolve-trans` | Show inherited keys instead of transparent markers |
| `--base-layer` | Base layer name for `--resolve-trans` |
| `--color` | Apply semantic colors to keys |
| `--no-toc` | Disable table of contents in PDF |
| `--continue-on-error` | Continue if a layer fails to render |
| `-v, --verbose` | Enable verbose output |
| `-q, --quiet` | Suppress all output except errors |

### Configuration File

Create a YAML configuration file for persistent customization:

```yaml
# config.yaml
page_size: a4          # or "letter"
orientation: landscape
font_size: 14
background_color: "#ffffff"
key_color: "#f0f0f0"
text_color: "#000000"
include_toc: true
os_style: mac          # "mac", "windows", or "linux"
resolve_trans: false
show_colors: false
show_held_indicator: true
```

## Color Scheme

When using `--color`, keys are colored by category using an Everforest-inspired palette:

| Category | Color | Keys |
|----------|-------|------|
| Modifiers | Teal | ⌘, ⌥, ⌃, ⇧, Shift, Ctrl, Alt |
| Navigation | Green | ←, →, ↑, ↓, Home, End, PgUp, PgDn |
| Numbers | Yellow | 0-9, F1-F12 |
| Symbols | Orange | !@#$%^&*() etc. |
| Media | Light Green | ⏯, ⏭, 🔊, 🔇 |
| Mouse | Teal | 🖱↑, 🖱L, 🖱R |
| System | Red | Reset, Boot, BT keys |
| Layers | Purple | Layer activators (when held) |
| Transparent | Gray | ▽, trans |
| Default | Beige | Regular alpha keys |

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/dsifry/glove80-keymap-visualizer.git
cd glove80-keymap-visualizer

# Create virtual environment and install dev dependencies
make install-dev

# Or manually:
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run specific test file
pytest tests/test_cli.py -v

# Skip slow tests
pytest -m "not slow"
```

### Code Quality

```bash
# Format code
make format

# Run linter
make lint

# Run type checker
make typecheck
```

### Project Structure

```
glove80-keymap-visualizer/
├── .github/workflows/    # CI/CD workflows
│   ├── ci.yml           # Test on PR/push
│   └── publish.yml      # Publish to PyPI on release
├── src/glove80_visualizer/
│   ├── cli.py           # Command-line interface
│   ├── parser.py        # ZMK keymap parsing
│   ├── extractor.py     # Layer extraction
│   ├── svg_generator.py # SVG generation
│   ├── pdf_generator.py # PDF conversion/merging
│   ├── config.py        # Configuration handling
│   ├── colors.py        # Color schemes and categorization
│   └── models.py        # Data models
├── tests/               # Test files (348+ tests, 100% coverage)
└── docs/                # Documentation and specs
```

## How It Works

1. **Parse** - Uses [keymap-drawer](https://github.com/caksoylar/keymap-drawer) to parse ZMK keymap files into YAML
2. **Extract** - Extracts layer information and key bindings, including hold behaviors and layer activators
3. **Generate SVG** - Creates SVG diagrams using keymap-drawer's layout engine with custom formatting
4. **Convert to PDF** - Combines SVGs into a single PDF with table of contents using CairoSVG and pikepdf

## Credits

- [keymap-drawer](https://github.com/caksoylar/keymap-drawer) - ZMK keymap parsing and SVG generation
- [sunaku's Glove80 keymaps](https://github.com/sunaku/glove80-keymaps) - Inspiration for the visualization format and color schemes
- [MoErgo Glove80](https://www.moergo.com/) - The amazing keyboard this is built for
- [Everforest](https://github.com/sainnhe/everforest) - Color palette inspiration

## License

MIT License - see LICENSE file for details.
