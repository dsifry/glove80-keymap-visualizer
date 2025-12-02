# Glove80 Keymap Visualizer

Generate PDF visualizations of Glove80 keyboard layers from ZMK keymap files.

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## Overview

This tool parses ZMK `.keymap` files (as exported from the MoErgo Glove80 Layout Editor) and generates beautiful PDF documents showing each keyboard layer, similar to [sunaku's layer diagrams](https://sunaku.github.io/moergo-glove80-keyboard-layers.pdf).

## Features

- Parse ZMK keymap files with support for complex behaviors (hold-tap, layer-tap, etc.)
- Generate SVG diagrams for each layer
- Combine layers into a single PDF with optional table of contents
- Customizable styling (colors, fonts, page size)
- Filter to specific layers or exclude unwanted ones

## Installation

### Prerequisites

- Python 3.10 or higher
- Cairo graphics library (for PDF generation)

**macOS:**
```bash
brew install cairo
```

**Ubuntu/Debian:**
```bash
sudo apt-get install libcairo2-dev
```

### Install from source

```bash
# Clone the repository
git clone https://github.com/dsifry/glove80-keymap-visualizer.git
cd glove80-keymap-visualizer

# Create virtual environment and install
make install-dev
```

## Usage

### Basic Usage

```bash
# Generate PDF with all layers
glove80-viz my-keymap.keymap -o my-layers.pdf

# Generate SVG files instead
glove80-viz my-keymap.keymap -o ./svgs --format svg

# List available layers
glove80-viz my-keymap.keymap --list-layers
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
```

### Configuration File

Create a YAML configuration file to customize the output:

```yaml
# config.yaml
page_size: a4          # or "letter"
orientation: landscape
font_size: 14
background_color: "#ffffff"
key_color: "#f0f0f0"
text_color: "#000000"
include_toc: true
```

## Development

### Setup

```bash
# Install development dependencies
make install-dev

# Run tests
make test

# Run tests with coverage
make test-cov

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
├── src/glove80_visualizer/
│   ├── cli.py           # Command-line interface
│   ├── parser.py        # ZMK keymap parsing
│   ├── extractor.py     # Layer extraction
│   ├── svg_generator.py # SVG generation
│   ├── pdf_generator.py # PDF conversion/merging
│   ├── config.py        # Configuration handling
│   └── models.py        # Data models
├── tests/               # Test files
├── docs/
│   ├── PLAN.md         # Project plan
│   └── SPEC.md         # TDD specifications
└── ...
```

### TDD Approach

This project follows test-driven development. See `docs/SPEC.md` for detailed test specifications. The workflow is:

1. Read the specification for a module
2. Run the failing tests: `make test`
3. Implement the module to make tests pass
4. Refactor as needed

## Credits

- [keymap-drawer](https://github.com/caksoylar/keymap-drawer) - ZMK keymap parsing and SVG generation
- [sunaku's Glove80 keymaps](https://github.com/sunaku/glove80-keymaps) - Inspiration for the visualization format
- [MoErgo Glove80](https://www.moergo.com/) - The amazing keyboard this is built for

## License

MIT License - see LICENSE file for details.
