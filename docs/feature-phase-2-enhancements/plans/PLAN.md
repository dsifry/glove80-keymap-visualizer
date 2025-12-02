# Phase 2 Enhancements - Implementation Plan

## Overview

This plan covers three major enhancements to the Glove80 Keymap Visualizer plus CI/CD infrastructure:

1. **PyPI Publishing** - Automated package publishing via GitHub Actions
2. **Key Combo Display** - Show modifier combinations (e.g., ⌘⇧K) inline
3. **Held Key Indicator** - Show thumbprint/icon for layer-activating keys
4. **Color Output** - Intelligent color coding inspired by sunaku's diagrams

## Goals

### Primary Goals
1. Enable `pip install glove80-keymap-visualizer` for easy installation
2. Display key combinations clearly (e.g., `Ctrl+Shift+K` → `⌃⇧K`)
3. Visually indicate which key activates each layer (held key indicator)
4. Add optional `--color` flag for semantically-colored output

### Non-Goals
- Interactive HTML output (future phase)
- Custom color theme files (keep it simple with preset themes)
- Per-key color customization (too complex)

## Architecture

### 1. PyPI Publishing (GitHub Actions)

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Push to main   │────▶│  Run tests      │────▶│  (optional)     │
│  or PR          │     │  lint, typecheck│     │  Build check    │
└─────────────────┘     └─────────────────┘     └─────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Create Release │────▶│  Build package  │────▶│  Publish to     │
│  (tag v*.*.*)   │     │  (wheel + sdist)│     │  PyPI           │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**Files to create:**
- `.github/workflows/ci.yml` - Run tests on PR/push
- `.github/workflows/publish.yml` - Publish to PyPI on release

### 2. Key Combo Display Enhancement

**Current behavior:**
```
Key shows: "LG(LS(K))"  or  "Gui+Shift+K"
```

**Enhanced behavior:**
```
Key shows: "⌘⇧K" (Mac) or "Win+Shift+K" (Windows)
```

**Data Flow:**
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Raw binding    │────▶│  Parse combo    │────▶│  Format with    │
│  "LG(LS(K))"    │     │  [LGUI, LSFT, K]│     │  OS symbols     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**ZMK Combo Patterns to Handle:**
| Pattern | Meaning | Display (Mac) |
|---------|---------|---------------|
| `LG(K)` | GUI + K | ⌘K |
| `LS(K)` | Shift + K | ⇧K |
| `LC(K)` | Ctrl + K | ⌃K |
| `LA(K)` | Alt + K | ⌥K |
| `LG(LS(K))` | GUI + Shift + K | ⌘⇧K |
| `LC(LA(K))` | Ctrl + Alt + K | ⌃⌥K |
| `MEH(K)` | Ctrl + Alt + Shift + K | ⌃⌥⇧K |
| `HYPER(K)` | All modifiers + K | ⌃⌥⇧⌘K |

**Implementation Location:** `svg_generator.py` - enhance `format_key_label()`

### 3. Held Key Indicator (Layer Activator)

**Problem:** When viewing a layer, users can't tell which key they're holding to access it.

**Solution:** Show a visual indicator (thumbprint icon or highlight) on the key that activates the current layer.

**Data Flow:**
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Layer binding  │────▶│  Find layer     │────▶│  Mark key with  │
│  "&lt 2 SPACE"  │     │  activator keys │     │  held indicator │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**Layer Activation Patterns:**
| Pattern | Meaning | Indicator |
|---------|---------|-----------|
| `&lt N KEY` | Layer-tap (hold for layer N) | Show on layer N |
| `&mo N` | Momentary layer N | Show on layer N |
| `&to N` | Toggle to layer N | Show on layer N |
| `&sl N` | Sticky layer N | Show on layer N |

**Visual Indicator Options:**
1. **Thumbprint icon** (👆 or custom SVG) - clear but adds visual noise
2. **Key highlight/border** - subtle, matches sunaku's style
3. **Background color** - distinguishes held keys
4. **"HELD" label** - explicit but verbose

**Recommended:** Use a subtle **purple/magenta border or background** (following sunaku's Everforest-inspired palette) with optional thumbprint icon.

**Implementation:**
1. In `extractor.py`: Track which keys activate which layers
2. In `svg_generator.py`: Add CSS class for held keys
3. New data structure:
```python
@dataclass
class LayerActivator:
    source_layer: int      # Layer where the key lives
    source_position: int   # Key position (0-79)
    target_layer: int      # Layer this key activates
    activation_type: str   # "momentary", "toggle", "sticky", "layer-tap"
```

### 4. Color Output (`--color` flag)

**Inspiration:** Sunaku's Everforest-based color scheme with semantic meaning.

**Color Categories:**
| Category | Color | Hex | Used For |
|----------|-------|-----|----------|
| Alpha | Default (no color) | - | Letters A-Z |
| Modifiers | Blue | `#7fbbb3` | Shift, Ctrl, Alt, GUI |
| Layers | Purple/Magenta | `#d699b6` | Layer activators, held keys |
| Navigation | Teal | `#83c092` | Arrows, Home, End, PgUp/Dn |
| Symbols | Orange | `#e69875` | !@#$%^&*() etc. |
| Numbers | Yellow | `#dbbc7f` | 0-9, F1-F12 |
| Media | Green | `#a7c080` | Play, Vol, Brightness |
| Mouse | Cyan | `#7fbbb3` | Mouse keys |
| System | Red | `#e67e80` | Reset, Bootloader |
| Transparent | Gray | `#859289` | Trans keys (dimmed) |

**CLI Interface:**
```bash
# Default: no color
glove80-viz keymap.keymap -o output.pdf

# With color
glove80-viz keymap.keymap -o output.pdf --color

# With color and specific theme (future)
glove80-viz keymap.keymap -o output.pdf --color --theme everforest
```

**Implementation:**
1. Add `--color` flag to CLI
2. Add `color_scheme` to `VisualizerConfig`
3. In `svg_generator.py`: Categorize keys and apply colors
4. Generate CSS with color definitions

**Key Categorization Logic:**
```python
def categorize_key(key_label: str) -> str:
    """Categorize a key for color coding."""
    if key_label in MODIFIER_KEYS:
        return "modifier"
    if key_label in NAVIGATION_KEYS:
        return "navigation"
    if key_label in MEDIA_KEYS:
        return "media"
    # ... etc
    return "default"
```

## Data Structures

### LayerActivator
```python
@dataclass
class LayerActivator:
    """Tracks which key activates a layer."""
    source_layer: int          # Layer containing the activator key
    source_position: int       # Key position (0-79)
    target_layer: int          # Layer being activated
    activation_type: str       # "momentary" | "toggle" | "sticky" | "layer-tap"
    tap_key: str | None        # For layer-tap: the tap behavior
```

### ColorScheme
```python
@dataclass
class ColorScheme:
    """Color scheme for visualization."""
    name: str = "everforest"
    modifier_color: str = "#7fbbb3"
    layer_color: str = "#d699b6"
    navigation_color: str = "#83c092"
    symbol_color: str = "#e69875"
    number_color: str = "#dbbc7f"
    media_color: str = "#a7c080"
    mouse_color: str = "#7fbbb3"
    system_color: str = "#e67e80"
    transparent_color: str = "#859289"
    held_key_color: str = "#d699b6"
    default_color: str = "#d3c6aa"  # Everforest foreground
```

### Enhanced VisualizerConfig
```python
@dataclass
class VisualizerConfig:
    # ... existing fields ...

    # New fields
    show_colors: bool = False
    color_scheme: ColorScheme = field(default_factory=ColorScheme)
    show_held_indicator: bool = True  # Show which key activates current layer
    held_indicator_style: str = "border"  # "border" | "background" | "icon"
```

## File Changes

### New Files
| File | Purpose |
|------|---------|
| `.github/workflows/ci.yml` | CI pipeline (test, lint, typecheck) |
| `.github/workflows/publish.yml` | PyPI publishing on release |
| `src/glove80_visualizer/colors.py` | Color scheme definitions and categorization |

### Modified Files
| File | Changes |
|------|---------|
| `cli.py` | Add `--color` flag |
| `config.py` | Add `ColorScheme`, `show_colors`, held indicator fields |
| `extractor.py` | Extract layer activator information |
| `svg_generator.py` | Apply colors, render held indicators, enhance combo display |
| `models.py` | Add `LayerActivator` model |

## Dependencies

### New Dependencies
None required - all features use existing dependencies.

### System Dependencies
No changes - Cairo still required.

## Implementation Phases

### Phase 2a: CI/CD & PyPI Publishing
- [ ] Create `.github/workflows/ci.yml`
- [ ] Create `.github/workflows/publish.yml`
- [ ] Verify package builds correctly
- [ ] Test publish to Test PyPI
- [ ] Publish v0.1.0 to PyPI

### Phase 2b: Key Combo Display
- [ ] Write tests for combo parsing
- [ ] Enhance `_parse_zmk_combo()` function
- [ ] Handle nested modifiers (`LG(LS(K))`)
- [ ] Verify all combo patterns render correctly

### Phase 2c: Held Key Indicator
- [ ] Write tests for layer activator extraction
- [ ] Add `LayerActivator` model
- [ ] Modify extractor to track activators
- [ ] Add CSS/styling for held keys
- [ ] Pass activator info to SVG generator

### Phase 2d: Color Output
- [ ] Write tests for key categorization
- [ ] Create `colors.py` module
- [ ] Add `--color` CLI flag
- [ ] Implement key categorization
- [ ] Generate colored SVG output
- [ ] Verify PDF renders colors correctly

## Error Handling

### CI/CD Errors
| Error | Handling |
|-------|----------|
| Tests fail | Block merge/release |
| Build fails | Block release |
| PyPI auth fails | Alert, manual retry |

### Color Output Errors
| Error | Handling |
|-------|----------|
| Unknown key category | Use default color |
| Invalid color hex | Use fallback, warn |

### Held Key Indicator Errors
| Error | Handling |
|-------|----------|
| No activator found for layer | Don't show indicator |
| Multiple activators | Show all of them |

## Success Criteria

1. **PyPI**: `pip install glove80-keymap-visualizer` works
2. **Combos**: `LG(LS(K))` displays as `⌘⇧K` on Mac
3. **Held indicator**: Layer pages show which thumb key is held
4. **Colors**: `--color` produces semantically-colored PDF
5. **Tests**: All new features have >95% test coverage
6. **Backwards compatible**: Existing CLI commands work unchanged

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| PyPI name taken | High | Check availability first, have backup name |
| Color categories incomplete | Low | Default color fallback, iterate based on feedback |
| Held key indicator clutters output | Medium | Make it subtle, toggleable |
| CI/CD flaky tests | Medium | Use pytest-retry, fix flaky tests |

## Timeline Estimate

| Phase | Effort | Dependencies |
|-------|--------|--------------|
| 2a: CI/CD | 2-3 hours | None |
| 2b: Key Combos | 2-3 hours | None |
| 2c: Held Indicator | 3-4 hours | 2b (needs combo parsing) |
| 2d: Colors | 3-4 hours | None |

**Total: ~12-14 hours of implementation**

## References

- [sunaku's Glove80 keymaps](https://sunaku.github.io/moergo-glove80-keyboard.html)
- [Everforest color palette](https://github.com/sainnhe/everforest)
- [PyPI publishing guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [GitHub Actions for Python](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)
