# Glove80 Keymap Visualizer

Generate beautiful PDF visualizations of your Glove80 keyboard layers from ZMK keymap files.

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
[![PyPI version](https://img.shields.io/pypi/v/glove80-keymap-visualizer.svg)](https://pypi.org/project/glove80-keymap-visualizer/)
[![CI](https://github.com/dsifry/glove80-keymap-visualizer/actions/workflows/ci.yml/badge.svg)](https://github.com/dsifry/glove80-keymap-visualizer/actions/workflows/ci.yml)
[![CodeRabbit](https://img.shields.io/badge/CodeRabbit-AI%20Reviews-blue?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMTggMTBhNiA2IDAgMCAwLTYtNiA2IDYgMCAwIDAtNiA2djNhNiA2IDAgMCAwIDYgNiA2IDYgMCAwIDAgNi02di0zeiIvPjwvc3ZnPg==)](https://coderabbit.ai)
![Test Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)

## What It Does

This tool takes your ZMK `.keymap` file (exported from the [MoErgo Glove80 Layout Editor](https://my.glove80.com/)) and generates a PDF document with a visual diagram for each layer—similar to [sunaku's layer diagrams](https://sunaku.github.io/moergo-glove80-keyboard-layers.pdf).

## Example Output

**Default output** — Shows shifted characters above keys (! above 1, @ above 2, etc.):

![Example plain output](docs/images/example-plain.png)

**With `--color` flag** — Semantic coloring by key category with legend:

![Example with color coding](docs/images/example-color.png)

**Layer with held key indicator** — Fingerprint icon shows which key activates this layer:

![Example Cursor layer with held key](docs/images/example-cursor.png)

**With `--no-shifted` flag** — Hide shifted characters for a cleaner look:

![Example without shifted characters](docs/images/example-no-shifted.png)

## Getting Started

### Step 1: Install System Dependencies

**macOS:**
```bash
brew install cairo
```

**Ubuntu/Debian:**
```bash
sudo apt-get install libcairo2-dev
```

**Windows:**
See [CairoSVG installation docs](https://cairosvg.org/documentation/#installation) for Windows instructions.

### Step 2: Install the Tool

**Option A: Install from PyPI (recommended)**
```bash
pip install glove80-keymap-visualizer
```

**Option B: Install from source**
```bash
git clone https://github.com/dsifry/glove80-keymap-visualizer.git
cd glove80-keymap-visualizer
pip install .
```

### Step 2.5: Install Browser for KLE Output (Optional)

For KLE PNG/PDF output (using keyboard-layout-editor.com styling), install Chromium:
```bash
playwright install chromium
```

This is only needed if you want to use `--format kle-png` or `--format kle-pdf`.

### Step 3: Export Your Keymap

1. Go to [my.glove80.com](https://my.glove80.com/)
2. Load your layout
3. Click **Export** → **Download ZMK Keymap**
4. Save the `.keymap` file

### Step 4: Generate Your PDF

```bash
# Basic usage - generates a PDF with all layers
glove80-viz your-keymap.keymap -o my-layers.pdf

# With color coding (recommended!)
glove80-viz your-keymap.keymap -o my-layers.pdf --color
```

That's it! Open `my-layers.pdf` to see your keyboard layout.

## Common Options

```bash
# Color-coded keys by category (modifiers, navigation, etc.)
glove80-viz keymap.keymap -o output.pdf --color

# Color-coded without the legend
glove80-viz keymap.keymap -o output.pdf --color --no-legend

# Windows modifier symbols (Win, Ctrl, Alt, Shift) instead of Mac symbols
glove80-viz keymap.keymap -o output.pdf --windows

# Show what keys do on transparent layers (instead of "trans")
glove80-viz keymap.keymap -o output.pdf --resolve-trans

# Generate only specific layers
glove80-viz keymap.keymap -o output.pdf --layers Base,Symbol,Cursor

# Generate SVG files instead of PDF
glove80-viz keymap.keymap -o ./svg-folder --format svg

# Generate KLE JSON (for keyboard-layout-editor.com)
glove80-viz keymap.keymap -o ./kle-folder --format kle

# Generate KLE-style PNG via headless browser (requires Chromium)
glove80-viz keymap.keymap -o ./png-folder --format kle-png

# Generate KLE-style combined PDF via headless browser
glove80-viz keymap.keymap -o output.pdf --format kle-pdf

# List all available layers in your keymap
glove80-viz keymap.keymap --list-layers
```

## Features

- **Shifted character display** — Shows shifted characters above keys (! above 1, " above ') like a physical keyboard
- **Custom mod-morph support** — Automatically detects custom shift mappings (e.g., `(` → `<`) from your keymap
- **Refined typography** — Balanced key label positioning inspired by physical keycaps, with clear visual hierarchy
- **OS-specific modifier symbols** — Mac (⌘⌥⌃⇧), Windows (Win+Ctrl+Alt+Shift), or Linux (Super+Ctrl+Alt+Shift)
- **Semantic coloring** — Color-code keys by category: modifiers, navigation, numbers, symbols, media, layers, system
- **Color legend** — Shows what each color means (can be hidden with `--no-legend`)
- **Held key indicators** — Fingerprint icon shows which key you hold to activate each layer
- **MEH/HYPER expansion** — `MEH(K)` displays as `⌃⌥⇧K` on Mac
- **Transparent key resolution** — Optionally show inherited keys instead of "trans" markers
- **Table of contents** — PDF includes clickable TOC for easy navigation
- **Layer filtering** — Generate only the layers you want
- **KLE output** — Export to keyboard-layout-editor.com JSON or render via headless browser to PNG/PDF

## All CLI Options

| Option | Description |
|--------|-------------|
| `-o, --output` | Output file (PDF) or directory (SVG/KLE) |
| `--format` | Output format: `pdf` (default), `svg`, `kle`, `kle-png`, `kle-pdf` |
| `--layers` | Comma-separated list of layers to include |
| `--exclude-layers` | Comma-separated list of layers to exclude |
| `--list-layers` | List available layers and exit |
| `--config` | Path to YAML configuration file |
| `--mac` | Use Mac modifier symbols (⌘⌥⌃⇧) — default |
| `--windows` | Use Windows modifier symbols |
| `--linux` | Use Linux modifier symbols |
| `--color` | Apply semantic colors to keys |
| `--no-legend` | Hide color legend (use with `--color`) |
| `--no-shifted` | Hide shifted characters on keys (shown by default) |
| `--resolve-trans` | Show inherited keys instead of "trans" |
| `--base-layer` | Base layer for `--resolve-trans` (default: first layer) |
| `--no-toc` | Disable table of contents in PDF |
| `--continue-on-error` | Continue if a layer fails to render |
| `-v, --verbose` | Show detailed output |
| `-q, --quiet` | Suppress all output except errors |

## Color Scheme

When using `--color`, keys are colored by category using an Everforest-inspired palette:

| Category | Color | Example Keys |
|----------|-------|--------------|
| Modifiers | Teal | ⌘, ⌥, ⌃, ⇧, Shift, Ctrl, Alt |
| Navigation | Green | ←, →, ↑, ↓, Home, End, PgUp, PgDn |
| Numbers | Yellow | 0-9, F1-F12 |
| Symbols | Orange | !@#$%^&*() etc. |
| Media | Light Green | ⏯, ⏭, 🔊, 🔇, brightness |
| Layer | Purple | Layer activators (held keys) |
| System | Red | Reset, Boot, Bluetooth keys |
| Mouse | Teal | Mouse movement and clicks |
| Transparent | Gray | Transparent/pass-through keys |

## Configuration File

For persistent settings, create a YAML config file:

```yaml
# my-config.yaml
os_style: mac          # "mac", "windows", or "linux"
show_colors: true
show_legend: true
show_shifted: true     # show shifted chars (default: true)
resolve_trans: false
include_toc: true
page_size: letter      # or "a4"
orientation: landscape
```

Then use it:
```bash
glove80-viz keymap.keymap -o output.pdf --config my-config.yaml
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Install browsers for KLE rendering tests
playwright install chromium

# Run tests
pytest

# Run tests with coverage
pytest --cov

# Run fast tests only (skip slow browser tests)
pytest -m "not slow"

# Format code
ruff format .

# Lint
ruff check .
```

## How It Works

1. **Parse** — Uses [keymap-drawer](https://github.com/caksoylar/keymap-drawer) to parse ZMK keymap files
2. **Extract** — Extracts layer info, key bindings, hold behaviors, and layer activators
3. **Generate SVG** — Creates SVG diagrams with keymap-drawer's layout engine
4. **Convert to PDF** — Combines SVGs into a PDF with TOC using CairoSVG and pikepdf

## Developer Resources

### Developer FAQ

For questions about development setup, testing, CI/CD, and common troubleshooting, see **[DEVELOPER-FAQ.md](DEVELOPER-FAQ.md)**.

Topics covered:
- Setting up your development environment
- Running tests and achieving coverage
- Understanding the codebase architecture
- Common issues and solutions

### Superpowers (AI-Assisted Development)

This project uses Claude Code with custom skills for AI-assisted development. See **[SUPERPOWERS.md](SUPERPOWERS.md)** for details on:

- Using Claude Code effectively with this codebase
- Available AI skills and workflows
- TDD and debugging patterns
- Code review and PR processes

## Credits

- [keymap-drawer](https://github.com/caksoylar/keymap-drawer) — ZMK keymap parsing and SVG generation
- [sunaku's Glove80 keymaps](https://github.com/sunaku/glove80-keymaps) — Inspiration for visualization format
- [MoErgo Glove80](https://www.moergo.com/) — The keyboard this tool is built for
- [Everforest](https://github.com/sainnhe/everforest) — Color palette inspiration

## License

MIT License — see [LICENSE](LICENSE) file for details.
