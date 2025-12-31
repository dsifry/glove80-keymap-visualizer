# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Page orientation control** (`--portrait`, `--landscape`): Choose page orientation for PDF output
- Portrait orientation is now the default (changed from landscape)
- TOC pages remain in portrait orientation regardless of content orientation

## [0.5.0] - 2025-12-30

### Added
- **Layers per page control** (`--layers-per-page`): Choose 1, 2, or 3 layers per PDF page (default: 3)
- **Configurable DPI** (`--dpi`): Adjust output resolution from 72-600 DPI (default: 300)
- Validation for `layers_per_page` parameter to prevent invalid configurations

### Fixed
- Consistent scaling for multi-layer pages: Final pages with fewer layers now maintain the same scale as full pages
- Dynamic page dimension derivation from source PDFs instead of hard-coded Letter size
- Replaced emoji/media symbols (⏯, 🔊, etc.) with text labels for better font compatibility

### Changed
- PDF compositing now uses pikepdf XObjects for proper font rendering in multi-layer layouts
- Improved error messages for invalid configuration values

## [0.4.1] - 2025-12-02

### Fixed
- Fixed CairoSVG rendering bug causing dark artifacts in PNG output when ZMK behavior references (e.g., `&select_line_left`, `&extend_word_right`) appeared in shifted key positions
- All binding fields (tap, hold, shifted) are now properly formatted to prevent raw `&behavior` strings from reaching the SVG renderer

### Added
- Comprehensive test suite for CairoSVG compatibility to prevent regression of the ampersand rendering bug
- Tests verify that no raw `&` prefixed behaviors leak through any binding field

## [0.4.0] - 2025-12-02

### Added
- Shifted character display on keys (! above 1, @ above 2, etc.) - enabled by default
- Custom mod-morph detection from keymap files
- `--no-shifted` flag to hide shifted characters
- Refined typography with balanced key label positioning
- Held key indicators with fingerprint icon showing layer activators

### Changed
- Improved visual hierarchy for key labels
- Enhanced modifier symbol rendering

## [0.3.0] - 2025-12-01

### Added
- Semantic color coding with `--color` flag
- Color legend (can be hidden with `--no-legend`)
- OS-specific modifier symbols (`--mac`, `--windows`, `--linux`)
- Transparent key resolution with `--resolve-trans`

## [0.2.0] - 2025-12-01

### Added
- PDF generation with table of contents
- Layer filtering with `--layers` and `--exclude-layers`
- SVG output format support
- Configuration file support

## [0.1.0] - 2025-12-01

### Added
- Initial release
- ZMK keymap parsing via keymap-drawer
- Basic PDF visualization of Glove80 layers
