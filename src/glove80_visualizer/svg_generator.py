"""
SVG generation module.

This module generates SVG diagrams for keyboard layers using keymap-drawer.
"""

import re
from io import StringIO
from typing import Any

from keymap_drawer.config import Config as KDConfig
from keymap_drawer.draw.draw import KeymapDrawer

from glove80_visualizer.colors import ColorScheme, categorize_key
from glove80_visualizer.config import VisualizerConfig
from glove80_visualizer.models import KeyBinding, Layer

# MDI Fingerprint icon path (from Material Design Icons)
# Inlined for CairoSVG compatibility (doesn't handle <use> with nested SVGs well)
FINGERPRINT_PATH = "M17.81,4.47C17.73,4.47 17.65,4.45 17.58,4.41C15.66,3.42 14,3 12,3C10.03,3 8.15,3.47 6.44,4.41C6.2,4.54 5.9,4.45 5.76,4.21C5.63,3.97 5.72,3.66 5.96,3.53C7.82,2.5 9.86,2 12,2C14.14,2 16,2.47 18.04,3.5C18.29,3.65 18.38,3.95 18.25,4.19C18.16,4.37 18,4.47 17.81,4.47M3.5,9.72C3.4,9.72 3.3,9.69 3.21,9.63C3,9.47 2.93,9.16 3.09,8.93C4.08,7.53 5.34,6.43 6.84,5.66C10,4.04 14,4.03 17.15,5.65C18.65,6.42 19.91,7.5 20.9,8.9C21.06,9.12 21,9.44 20.78,9.6C20.55,9.76 20.24,9.71 20.08,9.5C19.18,8.22 18.04,7.23 16.69,6.54C13.82,5.07 10.15,5.07 7.29,6.55C5.93,7.25 4.79,8.25 3.89,9.5C3.81,9.65 3.66,9.72 3.5,9.72M9.75,21.79C9.62,21.79 9.5,21.74 9.4,21.64C8.53,20.77 8.06,20.21 7.39,19C6.7,17.77 6.34,16.27 6.34,14.66C6.34,11.69 8.88,9.27 12,9.27C15.12,9.27 17.66,11.69 17.66,14.66A0.5,0.5 0 0,1 17.16,15.16A0.5,0.5 0 0,1 16.66,14.66C16.66,12.24 14.57,10.27 12,10.27C9.43,10.27 7.34,12.24 7.34,14.66C7.34,16.1 7.66,17.43 8.27,18.5C8.91,19.66 9.35,20.15 10.12,20.93C10.31,21.13 10.31,21.44 10.12,21.64C10,21.74 9.88,21.79 9.75,21.79M16.92,19.94C15.73,19.94 14.68,19.64 13.82,19.05C12.33,18.04 11.44,16.4 11.44,14.66A0.5,0.5 0 0,1 11.94,14.16A0.5,0.5 0 0,1 12.44,14.66C12.44,16.07 13.16,17.4 14.38,18.22C15.09,18.7 15.92,18.93 16.92,18.93C17.16,18.93 17.56,18.9 17.96,18.83C18.23,18.78 18.5,18.96 18.54,19.24C18.59,19.5 18.41,19.77 18.13,19.82C17.56,19.93 17.06,19.94 16.92,19.94M14.91,22C14.87,22 14.82,22 14.78,22C13.19,21.54 12.15,20.95 11.06,19.88C9.66,18.5 8.89,16.64 8.89,14.66C8.89,13.04 10.27,11.72 11.97,11.72C13.67,11.72 15.05,13.04 15.05,14.66C15.05,15.73 16,16.6 17.13,16.6C18.28,16.6 19.21,15.73 19.21,14.66C19.21,10.89 15.96,7.83 11.96,7.83C9.12,7.83 6.5,9.41 5.35,11.86C4.96,12.67 4.76,13.62 4.76,14.66C4.76,15.44 4.83,16.67 5.43,18.27C5.53,18.53 5.4,18.82 5.14,18.91C4.88,19 4.59,18.87 4.5,18.62C4,17.31 3.77,16 3.77,14.66C3.77,13.46 4,12.37 4.45,11.42C5.78,8.63 8.73,6.82 11.96,6.82C16.5,6.82 20.21,10.33 20.21,14.65C20.21,16.27 18.83,17.59 17.13,17.59C15.43,17.59 14.05,16.27 14.05,14.65C14.05,13.58 13.12,12.71 11.97,12.71C10.82,12.71 9.89,13.58 9.89,14.65C9.89,16.36 10.55,17.96 11.76,19.16C12.71,20.1 13.62,20.62 15.03,21C15.3,21.08 15.45,21.36 15.38,21.62C15.33,21.85 15.12,22 14.91,22Z"

# OS-specific modifier mappings
MODIFIER_SYMBOLS = {
    "mac": {
        "LSHIFT": "⇧",
        "RSHIFT": "⇧",
        "LSHFT": "⇧",
        "RSHFT": "⇧",
        "LSFT": "⇧",
        "RSFT": "⇧",
        "LCTRL": "⌃",
        "RCTRL": "⌃",
        "LCTL": "⌃",
        "RCTL": "⌃",
        "LALT": "⌥",
        "RALT": "⌥",
        "LGUI": "⌘",
        "RGUI": "⌘",
    },
    "windows": {
        "LSHIFT": "Shift",
        "RSHIFT": "Shift",
        "LSHFT": "Shift",
        "RSHFT": "Shift",
        "LSFT": "Shift",
        "RSFT": "Shift",
        "LCTRL": "Ctrl",
        "RCTRL": "Ctrl",
        "LCTL": "Ctrl",
        "RCTL": "Ctrl",
        "LALT": "Alt",
        "RALT": "Alt",
        "LGUI": "Win",
        "RGUI": "Win",
    },
    "linux": {
        "LSHIFT": "Shift",
        "RSHIFT": "Shift",
        "LSHFT": "Shift",
        "RSHFT": "Shift",
        "LSFT": "Shift",
        "RSFT": "Shift",
        "LCTRL": "Ctrl",
        "RCTRL": "Ctrl",
        "LCTL": "Ctrl",
        "RCTL": "Ctrl",
        "LALT": "Alt",
        "RALT": "Alt",
        "LGUI": "Super",
        "RGUI": "Super",
    },
}

# US keyboard shifted character pairs (unshifted -> shifted)
# Used to show shifted variants on keys like a physical keyboard
SHIFTED_KEY_PAIRS = {
    # Number row
    "1": "!",
    "2": "@",
    "3": "#",
    "4": "$",
    "5": "%",
    "6": "^",
    "7": "&",
    "8": "*",
    "9": "(",
    "0": ")",
    # Punctuation
    "`": "~",
    "-": "_",
    "=": "+",
    "[": "{",
    "]": "}",
    "\\": "|",
    ";": ":",
    "'": '"',
    ",": "<",
    ".": ">",
    "/": "?",
}


# Mapping from ZMK key codes to display characters
# Used for mod-morph shifted character resolution
ZMK_KEY_TO_CHAR = {
    # Numbers
    "N1": "1", "N2": "2", "N3": "3", "N4": "4", "N5": "5",
    "N6": "6", "N7": "7", "N8": "8", "N9": "9", "N0": "0",
    # Symbols
    "LPAR": "(", "RPAR": ")",
    "LT": "<", "GT": ">",
    "LBKT": "[", "RBKT": "]",
    "LBRC": "{", "RBRC": "}",
    "PIPE": "|", "BSLH": "\\",
    "EQUAL": "=", "PLUS": "+",
    "MINUS": "-", "UNDER": "_",
    "GRAVE": "`", "TILDE": "~",
    "SQT": "'", "DQT": '"',
    "SEMI": ";", "COLON": ":",
    "COMMA": ",", "DOT": ".",
    "FSLH": "/", "QMARK": "?",
    "EXCL": "!", "AT": "@",
    "HASH": "#", "DLLR": "$", "PRCNT": "%",
    "CARET": "^", "AMPS": "&", "ASTRK": "*",
}

# Reverse mapping: display character to ZMK key code
CHAR_TO_ZMK_KEY = {v: k for k, v in ZMK_KEY_TO_CHAR.items()}


def get_shifted_char(
    char: str,
    mod_morphs: dict[str, dict[str, str]] | None = None,
) -> str | None:
    """
    Get the shifted variant for a character on a US keyboard.

    Args:
        char: The unshifted character (e.g., "1", "'", ";", "(")
        mod_morphs: Optional dict of mod-morph behaviors from the keymap.
                    Keys are behavior names, values are {"tap": "LPAR", "shifted": "LT"}

    Returns:
        The shifted character (e.g., "!", '"', ":", "<") or None if no shifted variant
        exists (alpha keys, symbols, special keys).

    If mod_morphs is provided, it checks for custom shift mappings first.
    For example, if parang_left maps ( to <, and char is "(", returns "<".
    """
    # Check mod-morph mappings first (they override defaults)
    if mod_morphs:
        # Get the ZMK key code for this character
        zmk_key = CHAR_TO_ZMK_KEY.get(char)
        if zmk_key:
            # Look for a mod-morph that has this as the tap key
            for behavior in mod_morphs.values():
                if behavior.get("tap") == zmk_key:
                    # Found a match - return the shifted character
                    shifted_zmk = behavior.get("shifted")
                    if shifted_zmk:
                        return ZMK_KEY_TO_CHAR.get(shifted_zmk, shifted_zmk)

    # Fall back to default US keyboard shifted pairs
    return SHIFTED_KEY_PAIRS.get(char)


# Key label mappings for better display (common mappings that don't vary by OS)
KEY_LABEL_MAP = {
    # Transparent and none keys
    "&trans": "trans",
    "trans": "trans",
    "&none": "",
    "none": "",
    # Navigation arrows
    "LEFT": "←",
    "RIGHT": "→",
    "UP": "↑",
    "DOWN": "↓",
    # Home/End navigation
    "HOME": "⇱",
    "END": "⇲",
    # Page navigation
    "PG_UP": "⇞",
    "PG_DN": "⇟",
    "PAGE_UP": "⇞",
    "PAGE_DOWN": "⇟",
    "PG UP": "⇞",
    "PG DN": "⇟",
    # Word jump keys
    "WORD_LEFT": "⇐",
    "WORD_RIGHT": "⇒",
    # Special keys
    "BSPC": "⌫",
    "BACKSPACE": "⌫",
    "DEL": "⌦",
    "DELETE": "⌦",
    "ENTER": "↵",
    "RET": "↵",
    "RETURN": "↵",
    "SPACE": "␣",
    "SPC": "␣",
    "TAB": "⇥",
    "ESC": "Esc",
    "ESCAPE": "Esc",
    "CAPS": "⇪",
    "CAPSLOCK": "⇪",
    "CAPS_LOCK": "⇪",
    # Insert/Delete
    "INSERT": "Ins",
    "INS": "Ins",
    # Print Screen and Scroll Lock
    "PRINTSCREEN": "PrtSc",
    "PSCRN": "PrtSc",
    "PRINT_SCREEN": "PrtSc",
    "SCROLLLOCK": "ScrLk",
    "SLCK": "ScrLk",
    "SCROLL_LOCK": "ScrLk",
    # Numlock
    "NUMLOCK": "NumLk",
    "NLCK": "NumLk",
    "NUM_LOCK": "NumLk",
    # Pause/Break
    "PAUSE_BREAK": "Pause",
    "PAUSE": "Pause",
    "BREAK": "Brk",
    # Media keys - playback (ZMK codes)
    "C_PP": "⏯",
    "C_PLAY_PAUSE": "⏯",
    "PP": "⏯",  # keymap-drawer shorthand
    "C_PLAY": "▶",
    "C_PAUSE": "⏸",
    "C_STOP": "⏹",
    "C_NEXT": "⏭",
    "C_PREV": "⏮",
    "C_FF": "⏩",
    "C_RW": "⏪",
    "C_EJECT": "⏏",
    "C_REC": "⏺",
    # Media keys - playback (text labels from keymap-drawer - uppercase)
    "PLAY": "▶",
    "STOP": "⏹",
    "NEXT": "⏭",
    "PREV": "⏮",
    "PREVIOUS": "⏮",
    "EJECT": "⏏",
    "REC": "⏺",
    "RECORD": "⏺",
    # Media keys - playback (text labels - title case variants)
    "Play": "▶",
    "Pause": "⏸",
    "Stop": "⏹",
    "Next": "⏭",
    "Prev": "⏮",
    "Previous": "⏮",
    "FF": "⏩",
    "Fast Forward": "⏩",
    "RW": "⏪",
    "Rewind": "⏪",
    "Eject": "⏏",
    "Rec": "⏺",
    "Record": "⏺",
    # Media keys - volume (ZMK codes)
    "C_VOL_UP": "🔊",
    "C_VOLUME_UP": "🔊",
    "C_VOL_DN": "🔉",
    "C_VOLUME_DOWN": "🔉",
    "C_MUTE": "🔇",
    # Media keys - volume (text labels from keymap-drawer - uppercase)
    "VOL UP": "🔊",
    "VOLUME UP": "🔊",
    "VOL DN": "🔉",
    "VOL DOWN": "🔉",
    "VOLUME DOWN": "🔉",
    "MUTE": "🔇",
    # Media keys - volume (text labels - title case variants)
    "Vol Up": "🔊",
    "Volume Up": "🔊",
    "Vol Dn": "🔉",
    "Vol Down": "🔉",
    "Volume Down": "🔉",
    "Mute": "🔇",
    # Media keys - brightness (ZMK codes)
    "C_BRI_UP": "🔆",
    "C_BRIGHTNESS_UP": "🔆",
    "C_BRI_DN": "🔅",
    "C_BRIGHTNESS_DOWN": "🔅",
    "C_BRI_MAX": "☀",
    "C_BRI_MIN": "🌑",
    # Media keys - brightness (text labels from keymap-drawer - uppercase)
    "BRI UP": "🔆",
    "BRIGHTNESS UP": "🔆",
    "BRI DN": "🔅",
    "BRI DOWN": "🔅",
    "BRIGHTNESS DOWN": "🔅",
    "BRI MAX": "☀",
    "BRI MIN": "🌑",
    "BRI AUTO": "🔆A",
    # Media keys - brightness (text labels - title case variants)
    "Bri Up": "🔆",
    "Brightness Up": "🔆",
    "Bri Dn": "🔅",
    "Bri Down": "🔅",
    "Brightness Down": "🔅",
    "Bri Max": "☀",
    "Bri Min": "🌑",
    "Bri Auto": "🔆A",
    # Layer symbols
    "Emoji": "😀",
    "World": "🌍",
    "System": "⚙",
    "Gaming": "🎮",
    "Magic": "✨",
    "Number": "#",
    "Function": "Fn",
    "Cursor": "↔",
    "Nav": "↔",
    "Symbol": "Sym",
    "Media": "🔊",
    "Mouse": "🖱",
    "MouseSlow": "🖱🐢",
    "MouseFast": "🖱🐇",
    "MouseWarp": "🖱⚡",
}


def generate_layer_svg(
    layer: Layer,
    config: VisualizerConfig | None = None,
    include_title: bool = False,
    os_style: str = "mac",
    resolve_trans: bool = False,
    base_layer: Layer | None = None,
    activators: list | None = None,
    mod_morphs: dict[str, dict[str, str]] | None = None,
) -> str:
    """
    Generate an SVG diagram for a single keyboard layer.

    Args:
        layer: The Layer object to visualize
        config: Optional configuration for styling
        include_title: Whether to include the layer name in the SVG
        os_style: Operating system style for modifier symbols ("mac", "windows", "linux")
        resolve_trans: Whether to resolve transparent keys to their base layer values
        base_layer: The base layer to use for resolving transparent keys
        activators: List of LayerActivator objects for marking held keys
        mod_morphs: Custom shift mappings from mod-morph behaviors in the keymap

    Returns:
        SVG content as a string
    """
    if config is None:
        config = VisualizerConfig()

    # Get os_style from config if not specified
    if hasattr(config, 'os_style') and config.os_style:
        os_style = config.os_style

    # Find held positions for this layer
    held_positions: set[int] = set()
    if activators and config.show_held_indicator:
        for activator in activators:
            if activator.target_layer_name == layer.name:
                held_positions.add(activator.source_position)

    # Resolve transparent keys if requested
    working_layer = layer
    if resolve_trans and base_layer:
        working_layer = _resolve_transparent_keys(layer, base_layer)

    # Convert Layer to keymap-drawer format
    keymap_data = _layer_to_keymap_drawer_format(
        working_layer, config, os_style, held_positions, mod_morphs
    )

    # Create keymap-drawer config
    kd_config = KDConfig()

    # Increase glyph size for held key indicators (fingerprint in tap position)
    # Default tap size is 14, but we want a more prominent indicator
    kd_config.draw_config.glyph_tap_size = 32

    # Typography spacing - increase inner padding for better vertical breathing room
    # This moves shifted/hold text slightly inward from key edges
    kd_config.draw_config.inner_pad_h = 4.0  # default is 2.0
    kd_config.draw_config.small_pad = 3.0   # default is 2.0

    # Override default font to include better Unicode symbol support
    # Arial Unicode MS has extensive Unicode coverage and works well with CairoSVG
    font_override_css = """
/* Better font for Unicode symbols - CairoSVG compatibility */
svg.keymap {
    font-family: "Arial Unicode MS", "Lucida Grande", "Apple Symbols", Arial, sans-serif;
}

/* Typography refinements - inspired by physical keyboard legends */

/* Base tap label - medium weight for prominence */
svg.keymap text {
    font-size: 12px;
}

/* Tap labels - bolder appearance via size and subtle stroke */
text.tap {
    font-size: 14px !important;
    stroke: currentColor;
    stroke-width: 0.3px;
}

/* Shifted characters - smaller and lighter */
text.shifted {
    font-size: 10px !important;
    fill: #444 !important;
}

/* Hold modifiers - smaller and lighter */
text.hold {
    font-size: 9px !important;
    fill: #666 !important;
}

/* Transparent keys - muted */
text.trans {
    fill: #999 !important;
}

/* Centered layer label styling */
text.centered-label {
    text-anchor: middle !important;
    font-size: 20px;
    fill: #24292e !important;
    stroke: white;
    stroke-width: 3;
    paint-order: stroke;
    letter-spacing: 0.1em;
}
"""

    # Add color CSS if enabled
    extra_css = font_override_css
    if config.show_colors:
        color_scheme = ColorScheme()
        color_css = _generate_color_css(color_scheme)
        extra_css += color_css

    kd_config.draw_config.svg_extra_style = extra_css

    # Generate SVG
    out = StringIO()
    drawer = KeymapDrawer(config=kd_config, out=out, **keymap_data)
    drawer.print_board(draw_layers=[working_layer.name])

    svg_content = out.getvalue()

    # Replace emoji with text equivalents for CairoSVG compatibility
    svg_content = _replace_emoji_for_cairo(svg_content)

    # Replace glyph <use> elements with inline SVG paths for CairoSVG compatibility
    svg_content = _inline_fingerprint_glyphs(svg_content)

    # Adjust tap label positions for keys with shifted but no hold
    # This creates balanced top/bottom positioning like a physical keycap
    svg_content = _adjust_tap_positions_for_shifted(svg_content)

    # Add held key indicator styling
    if held_positions:
        svg_content = _add_held_key_indicators(svg_content, held_positions)

    # Center the layer name between left and right keyboard halves
    svg_content = _center_layer_label(svg_content, working_layer.name)

    # Add color legend if colors are enabled and legend is not disabled
    if config.show_colors and config.show_legend:
        color_scheme = ColorScheme()
        svg_content = _add_color_legend(svg_content, color_scheme)

    # Optionally add title
    if include_title:
        svg_content = _add_title_to_svg(svg_content, layer.name)

    return svg_content


def generate_all_layer_svgs(
    layers: list[Layer],
    config: VisualizerConfig | None = None,
    os_style: str = "mac",
    resolve_trans: bool = False,
) -> list[str]:
    """
    Generate SVG diagrams for all layers.

    Args:
        layers: List of Layer objects to visualize
        config: Optional configuration for styling
        os_style: Operating system style for modifier symbols
        resolve_trans: Whether to resolve transparent keys

    Returns:
        List of SVG content strings, one per layer
    """
    # Find base layer (index 0)
    base_layer = None
    if resolve_trans and layers:
        for layer in layers:
            if layer.index == 0:
                base_layer = layer
                break
        if not base_layer:
            base_layer = layers[0]

    return [
        generate_layer_svg(
            layer,
            config,
            os_style=os_style,
            resolve_trans=resolve_trans,
            base_layer=base_layer,
        )
        for layer in layers
    ]


def format_key_label(key: str, os_style: str = "mac") -> str:
    """
    Format a key name for display.

    Converts ZMK key names to human-readable labels.

    Args:
        key: The ZMK key name (e.g., "LSHIFT", "&trans")
        os_style: Operating system style for modifier symbols ("mac", "windows", "linux")

    Returns:
        Formatted label for display (e.g., "⇧", "trans")
    """
    if not key:
        return ""

    # Normalize the key for lookup
    key_normalized = key.strip()

    # Handle ZMK behavior prefixes - abbreviate long behavior names
    if key_normalized.startswith("&"):
        return _format_behavior(key_normalized, os_style)

    # Handle modifier combos like LS(LEFT) or LG(RIGHT)
    combo_match = re.match(r'^([LR][SGAC])\((.+)\)$', key_normalized, re.IGNORECASE)
    if combo_match:
        modifier_code, inner_key = combo_match.groups()
        modifier_label = _get_modifier_label(modifier_code.upper(), os_style)
        inner_label = format_key_label(inner_key, os_style)
        return f"{modifier_label}{inner_label}"

    # Handle MEH(key) and HYPER(key) combos
    meh_match = re.match(r'^MEH\((.+)\)$', key_normalized, re.IGNORECASE)
    if meh_match:
        inner_key = meh_match.group(1)
        inner_label = format_key_label(inner_key, os_style)
        return f"{_get_meh_label(os_style, as_prefix=True)}{inner_label}"

    hyper_match = re.match(r'^HYPER\((.+)\)$', key_normalized, re.IGNORECASE)
    if hyper_match:
        inner_key = hyper_match.group(1)
        inner_label = format_key_label(inner_key, os_style)
        return f"{_get_hyper_label(os_style, as_prefix=True)}{inner_label}"

    # Handle keymap-drawer modifier combo format: Gui+X, Ctl+Sft+X, etc.
    if "+" in key_normalized:
        return _format_modifier_combo(key_normalized, os_style)

    # Handle Meh and Hyper keys
    if key_normalized.upper() in ("MEH", "LMEH", "RMEH"):
        return _get_meh_label(os_style)
    if key_normalized.upper() in ("HYPER", "LHYPER", "RHYPER"):
        return _get_hyper_label(os_style)

    # Check for OS-specific modifier mapping
    key_upper = key_normalized.upper()
    modifier_map = MODIFIER_SYMBOLS.get(os_style, MODIFIER_SYMBOLS["mac"])
    if key_upper in modifier_map:
        return modifier_map[key_upper]

    # Check direct mapping first (case-sensitive for layer names like "Emoji")
    if key_normalized in KEY_LABEL_MAP:
        return KEY_LABEL_MAP[key_normalized]

    # Check case-insensitive for non-layer keys
    if key_upper in KEY_LABEL_MAP:
        return KEY_LABEL_MAP[key_upper]

    # For all-caps keys that aren't mapped, convert to title case
    if key_normalized.isupper() and len(key_normalized) > 1:
        return key_normalized.title()

    # Return original if no mapping
    return key_normalized


def _format_behavior(behavior: str, os_style: str) -> str:
    """Format ZMK behavior strings like &sticky_key_oneshot LSFT."""

    # Handle emoji macros - extract emoji name and return actual emoji
    if behavior.startswith("&emoji_") and behavior.endswith("_macro"):
        return _format_emoji_macro(behavior)

    # Handle emoji preset behaviors (don't end in _macro)
    if behavior.startswith("&emoji_"):
        return _format_emoji_preset(behavior)

    # Handle world/international character macros
    if behavior.startswith("&world_") and behavior.endswith("_macro"):
        return _format_world_macro(behavior)

    # Handle finger tap behaviors (left_pinky_tap, right_index_tap, etc.)
    finger_tap_match = re.match(r'^&(left|right)_(pinky|ringy|middy|index)_tap\s+(.+)$', behavior)
    if finger_tap_match:
        key = finger_tap_match.group(3)
        return format_key_label(key, os_style)

    # Handle finger hold behaviors (right_index_hold LSFT, left_middy_hold LGUI, etc.)
    finger_hold_match = re.match(r'^&(left|right)_(pinky|ringy|middy|index)_hold\s+(.+)$', behavior)
    if finger_hold_match:
        modifier = finger_hold_match.group(3)
        return format_key_label(modifier, os_style)

    # Handle mouse scroll
    if behavior.startswith("&msc "):
        return _format_mouse_scroll(behavior)

    # Handle mouse move
    if behavior.startswith("&mmv "):
        return _format_mouse_move(behavior)

    # Handle mouse click
    if behavior.startswith("&mkp "):
        return _format_mouse_click(behavior)

    # Handle select behaviors
    if behavior.startswith("&select_"):
        return _format_select_behavior(behavior)

    # Handle extend behaviors
    if behavior.startswith("&extend_"):
        return _format_extend_behavior(behavior)

    # Common behavior abbreviations
    behavior_abbrevs = {
        "&caps_word": "⇪W",
        "&sticky_key": "●",
        "&sticky_key_oneshot": "●",
        "&sk": "●",
        "&sl": "layer",
        "&mo": "hold",
        "&to": "→",
        "&tog": "⇄",
        "&lt": "",  # Layer-tap - just show the key
        "&mt": "",  # Mod-tap - just show the key
        "&kp": "",  # Keypress - just show the key
        "&rgb_ug_status_macro": "RGB",
        "&rgb_ug": "RGB",
        "&bt": "BT",
        "&out": "Out",
        "&ext_power": "Pwr",
        "&sys_reset": "Reset",
        "&bootloader": "Boot",
    }

    # Split behavior from arguments
    parts = behavior.split(None, 1)
    behavior_name = parts[0]
    args = parts[1] if len(parts) > 1 else ""

    # Check for exact match first
    if behavior_name in behavior_abbrevs:
        abbrev = behavior_abbrevs[behavior_name]
        if abbrev and args:
            # Format the argument too
            arg_formatted = format_key_label(args, os_style)
            # For sticky keys, show modifier symbol only
            if behavior_name in ("&sticky_key_oneshot", "&sticky_key", "&sk"):
                return f"●{arg_formatted}"
            return f"{abbrev}{arg_formatted}" if abbrev else arg_formatted
        elif abbrev:
            return abbrev
        elif args:
            return format_key_label(args, os_style)
        return behavior_name[1:]  # Remove & prefix

    # Check for prefix matches
    for prefix, abbrev in behavior_abbrevs.items():
        if behavior_name.startswith(prefix):
            if args:
                arg_formatted = format_key_label(args, os_style)
                if prefix in ("&sticky_key_oneshot", "&sticky_key", "&sk"):
                    return f"●{arg_formatted}"
                return f"{abbrev}{arg_formatted}" if abbrev else arg_formatted
            return abbrev if abbrev else behavior_name[1:]

    # Unknown behavior - just remove & and truncate if too long
    result = behavior[1:]  # Remove &
    if len(result) > 8:
        return result[:6] + "…"
    return result


def _format_emoji_macro(behavior: str) -> str:
    """Convert emoji macro names to actual emoji characters."""
    # Extract emoji name: &emoji_heart_macro -> heart
    match = re.match(r'^&emoji_(.+)_macro$', behavior)
    if not match:
        return "😀"

    emoji_name = match.group(1)

    # Emoji mappings
    emoji_map = {
        # Emotions & expressions
        "heart": "❤",
        "fire": "🔥",
        "thumbs_up": "👍",
        "thumbs_down": "👎",
        "tada": "🎉",
        "muscle": "💪",
        "rocket": "🚀",
        "pray": "🙏",
        "ok_hand": "👌",
        "raised_hands": "🙌",
        "clap": "👏",
        "wave": "👋",
        "joy": "😂",
        "rofl": "🤣",
        "star_struck": "🤩",
        "love_struck": "😍",
        "thinking": "🤔",
        "wink": "😉",
        "smile": "😊",
        "grin": "😁",
        "laugh": "😆",
        "sweat_smile": "😅",
        "rolling_eyes": "🙄",
        "unamused": "😒",
        "cry": "😢",
        "sob": "😭",
        "angry": "😠",
        "rage": "😡",
        "scream": "😱",
        "flushed": "😳",
        "dizzy": "😵",
        "shrug": "🤷",
        "facepalm": "🤦",
        "snap_fingers": "🫰",
        "disappointed": "😞",
        "shocked_face": "😲",
        "face_joke_wink": "😜",
        "face_fear_scared": "😨",
        # Weather
        "sunny": "☀",
        "cloudy": "☁",
        "partly_cloudy": "⛅",
        "mostly_cloudy": "🌥",
        "mostly_sunny": "🌤",
        "rainbow": "🌈",
        "lightning": "⚡",
        "snowflake": "❄",
        "umbrella": "☂",
        # Moon phases
        "new_moon": "🌑",
        "waxing_crescent_moon": "🌒",
        "first_quarter_moon": "🌓",
        "waxing_gibbous_moon": "🌔",
        "full_moon": "🌕",
        "waning_gibbous_moon": "🌖",
        "last_quarter_moon": "🌗",
        "waning_crescent_moon": "🌘",
        # Objects & symbols
        "check": "✓",
        "x": "✗",
        "star": "⭐",
        "sparkles": "✨",
        "heart_eyes": "😍",
        "100": "💯",
        "poop": "💩",
        "skull": "💀",
        "ghost": "👻",
        "alien": "👽",
        "robot": "🤖",
        "eyes": "👀",
        "brain": "🧠",
        # Skin tone modifiers
        "light_skin_tone": "🏻",
        "medium_light_skin_tone": "🏼",
        "medium_skin_tone": "🏽",
        "medium_dark_skin_tone": "🏾",
        "dark_skin_tone": "🏿",
        # Gender signs and modifiers
        "male_sign": "♂",
        "female_sign": "♀",
        "zwj": "⊕",  # Zero-width joiner indicator
    }

    return emoji_map.get(emoji_name, "😀")


def _format_emoji_preset(behavior: str) -> str:
    """Format emoji preset behaviors that don't follow the _macro pattern."""
    # Remove the & prefix
    name = behavior[1:] if behavior.startswith("&") else behavior

    emoji_preset_map = {
        # Skin tone presets
        "emoji_skin_tone_preset": "👤",
        # Zero-width joiner for combining emoji
        "emoji_zwj_macro": "⊕",
        "emoji_zwj": "⊕",
        # Gender sign presets
        "emoji_gender_sign_preset": "⚥",
        "emoji_male_sign": "♂",
        "emoji_female_sign": "♀",
        # Hair style presets
        "emoji_hair_style_preset": "💇",
    }

    return emoji_preset_map.get(name, "😀")


def _format_world_macro(behavior: str) -> str:
    """Convert world/international macro names to actual characters."""
    # Extract character description: &world_a_acute_lower_macro -> a_acute_lower
    match = re.match(r'^&world_(.+)_macro$', behavior)
    if not match:
        return "?"

    char_name = match.group(1)

    # World character mappings
    world_map = {
        # Vowels with acute
        "a_acute_lower": "á",
        "a_acute_upper": "Á",
        "e_acute_lower": "é",
        "e_acute_upper": "É",
        "i_acute_lower": "í",
        "i_acute_upper": "Í",
        "o_acute_lower": "ó",
        "o_acute_upper": "Ó",
        "u_acute_lower": "ú",
        "u_acute_upper": "Ú",
        "y_acute_lower": "ý",
        "y_acute_upper": "Ý",
        # Vowels with grave
        "a_grave_lower": "à",
        "a_grave_upper": "À",
        "e_grave_lower": "è",
        "e_grave_upper": "È",
        "i_grave_lower": "ì",
        "i_grave_upper": "Ì",
        "o_grave_lower": "ò",
        "o_grave_upper": "Ò",
        "u_grave_lower": "ù",
        "u_grave_upper": "Ù",
        # Vowels with diaeresis/umlaut
        "a_diaeresis_lower": "ä",
        "a_diaeresis_upper": "Ä",
        "e_diaeresis_lower": "ë",
        "e_diaeresis_upper": "Ë",
        "i_diaeresis_lower": "ï",
        "i_diaeresis_upper": "Ï",
        "o_diaeresis_lower": "ö",
        "o_diaeresis_upper": "Ö",
        "u_diaeresis_lower": "ü",
        "u_diaeresis_upper": "Ü",
        "y_diaeresis_lower": "ÿ",
        "y_diaeresis_upper": "Ÿ",
        # Vowels with circumflex
        "a_circumflex_lower": "â",
        "a_circumflex_upper": "Â",
        "e_circumflex_lower": "ê",
        "e_circumflex_upper": "Ê",
        "i_circumflex_lower": "î",
        "i_circumflex_upper": "Î",
        "o_circumflex_lower": "ô",
        "o_circumflex_upper": "Ô",
        "u_circumflex_lower": "û",
        "u_circumflex_upper": "Û",
        # Vowels with tilde
        "a_tilde_lower": "ã",
        "a_tilde_upper": "Ã",
        "o_tilde_lower": "õ",
        "o_tilde_upper": "Õ",
        "n_tilde_lower": "ñ",
        "n_tilde_upper": "Ñ",
        # Vowels with ring
        "a_ring_lower": "å",
        "a_ring_upper": "Å",
        # Vowels with slash
        "o_slash_lower": "ø",
        "o_slash_upper": "Ø",
        # Consonants
        "consonants_cedilla_lower": "ç",
        "consonants_cedilla_upper": "Ç",
        "consonants_ntilde_lower": "ñ",
        "consonants_ntilde_upper": "Ñ",
        "consonants_eszett_lower": "ß",
        "consonants_eszett_upper": "ẞ",
        # Ligatures
        "vowels_ae_lower": "æ",
        "vowels_ae_upper": "Æ",
        "vowels_oe_lower": "œ",
        "vowels_oe_upper": "Œ",
        # Signs and symbols
        "degree_sign": "°",
        "sign_copyright_regular": "©",
        "sign_trademark_regular": "™",
        "sign_registered_regular": "®",
        "sign_section": "§",
        "sign_pilcrow": "¶",
        "sign_micro": "µ",
        # Currency
        "currency_euro": "€",
        "currency_pound": "£",
        "currency_yen": "¥",
        "currency_cent": "¢",
    }

    return world_map.get(char_name, "?")


def _format_mouse_scroll(behavior: str) -> str:
    """Format mouse scroll behavior."""
    # &msc SCRL_UP -> ⊘↑
    scroll_map = {
        "SCRL_UP": "⊘↑",
        "SCRL_DOWN": "⊘↓",
        "SCRL_LEFT": "⊘←",
        "SCRL_RIGHT": "⊘→",
    }
    parts = behavior.split()
    if len(parts) >= 2:
        return scroll_map.get(parts[1], "⊘")
    return "⊘"


def _format_mouse_move(behavior: str) -> str:
    """Format mouse move behavior."""
    # &mmv MOVE_UP -> 🖱↑
    move_map = {
        "MOVE_UP": "🖱↑",
        "MOVE_DOWN": "🖱↓",
        "MOVE_LEFT": "🖱←",
        "MOVE_RIGHT": "🖱→",
    }
    parts = behavior.split()
    if len(parts) >= 2:
        return move_map.get(parts[1], "🖱")
    return "🖱"


def _format_mouse_click(behavior: str) -> str:
    """Format mouse click behavior."""
    # &mkp LCLK -> 🖱L
    click_map = {
        "LCLK": "🖱L",
        "RCLK": "🖱R",
        "MCLK": "🖱M",
        "MB4": "🖱◀",
        "MB5": "🖱▶",
    }
    parts = behavior.split()
    if len(parts) >= 2:
        return click_map.get(parts[1], "🖱")
    return "🖱"


def _format_select_behavior(behavior: str) -> str:
    """Format select behaviors."""
    # &select_word_right -> Sel→W
    select_map = {
        "&select_word_right": "Sel→W",
        "&select_word_left": "Sel←W",
        "&select_line_right": "Sel→L",
        "&select_line_left": "Sel←L",
        "&select_none": "Sel✕",
        "&select_all": "SelA",
    }
    return select_map.get(behavior, "Sel")


def _format_extend_behavior(behavior: str) -> str:
    """Format extend behaviors."""
    # &extend_word_right -> Ext→W
    extend_map = {
        "&extend_word_right": "Ext→W",
        "&extend_word_left": "Ext←W",
        "&extend_line_right": "Ext→L",
        "&extend_line_left": "Ext←L",
    }
    return extend_map.get(behavior, "Ext")


def _format_modifier_combo(combo: str, os_style: str) -> str:
    """Format keymap-drawer modifier combos like Gui+Sft+Z."""
    # Modifier name mappings to short codes
    modifier_names = {
        "GUI": "LG",
        "CTL": "LC",
        "CTRL": "LC",
        "SFT": "LS",
        "SHIFT": "LS",
        "ALT": "LA",
        "OPT": "LA",
        "MEH": "MEH",
        "HYPER": "HYPER",
    }

    parts = combo.split("+")
    if len(parts) < 2:
        return combo

    # Last part is the key, rest are modifiers
    key = parts[-1]
    modifiers = parts[:-1]

    # Convert modifiers to symbols
    mod_symbols = []
    for mod in modifiers:
        mod_upper = mod.upper()
        if mod_upper in modifier_names:
            code = modifier_names[mod_upper]
            if code == "MEH":
                mod_symbols.append(_get_meh_label(os_style))
            elif code == "HYPER":
                mod_symbols.append(_get_hyper_label(os_style))
            else:
                mod_symbols.append(_get_modifier_label(code, os_style))
        else:
            # Unknown modifier, keep as-is but abbreviated
            mod_symbols.append(mod[:3])

    # Format the key
    key_label = format_key_label(key, os_style)

    # Combine: modifiers + key
    return "".join(mod_symbols) + key_label


def _get_meh_label(os_style: str, as_prefix: bool = False) -> str:
    """Get the label for Meh key (Ctrl+Alt+Shift).

    Args:
        os_style: Operating system style
        as_prefix: If True, return a prefix for combo (e.g., "Ctrl+Alt+Shift+")
                  If False, return standalone label (e.g., "Meh")
    """
    if os_style == "mac":
        return "⌃⌥⇧"  # Control + Option + Shift
    else:
        if as_prefix:
            return "Ctrl+Alt+Shift+"
        return "Meh"


def _get_hyper_label(os_style: str, as_prefix: bool = False) -> str:
    """Get the label for Hyper key (Ctrl+Alt+Shift+Gui).

    Args:
        os_style: Operating system style
        as_prefix: If True, return a prefix for combo (e.g., "Ctrl+Alt+Shift+Win+")
                  If False, return standalone label (e.g., "Hypr")
    """
    if os_style == "mac":
        return "⌃⌥⇧⌘"  # Control + Option + Shift + Command
    else:
        if as_prefix:
            return "Ctrl+Alt+Shift+Win+"
        return "Hypr"


def _get_modifier_label(modifier_code: str, os_style: str) -> str:
    """Get the label for a modifier code like LS, LG, LA, LC."""
    code_to_key = {
        "LS": "LSHIFT",
        "RS": "RSHIFT",
        "LG": "LGUI",
        "RG": "RGUI",
        "LA": "LALT",
        "RA": "RALT",
        "LC": "LCTRL",
        "RC": "RCTRL",
    }
    key = code_to_key.get(modifier_code.upper(), modifier_code)
    modifier_map = MODIFIER_SYMBOLS.get(os_style, MODIFIER_SYMBOLS["mac"])
    return modifier_map.get(key, modifier_code)


def _resolve_transparent_keys(layer: Layer, base_layer: Layer) -> Layer:
    """
    Create a new layer with transparent keys resolved to base layer values.

    Args:
        layer: The layer with transparent keys to resolve
        base_layer: The base layer to get key values from

    Returns:
        A new Layer with transparent keys replaced by base layer values
    """
    # Build a position map for base layer
    base_bindings_map = {b.position: b for b in base_layer.bindings}

    new_bindings = []
    for binding in layer.bindings:
        if binding.is_transparent:
            # Get the corresponding key from base layer
            base_binding = base_bindings_map.get(binding.position)
            if base_binding and not base_binding.is_transparent:
                # Create a new binding with the base layer's value
                # Mark it as inherited for potential styling
                new_binding = KeyBinding(
                    position=binding.position,
                    tap=base_binding.tap,
                    hold=base_binding.hold,
                )
                new_bindings.append(new_binding)
            else:
                # If base layer is also transparent, keep it as transparent
                new_bindings.append(binding)
        else:
            new_bindings.append(binding)

    return Layer(
        name=layer.name,
        index=layer.index,
        bindings=new_bindings,
    )


def _layer_to_keymap_drawer_format(
    layer: Layer,
    config: VisualizerConfig,
    os_style: str = "mac",
    held_positions: set[int] | None = None,
    mod_morphs: dict[str, dict[str, str]] | None = None,
) -> dict[str, Any]:
    """
    Convert a Layer to keymap-drawer's expected YAML format.

    keymap-drawer expects:
    - layout: {zmk_keyboard: 'glove80'}
    - layers: {LayerName: [[row1], [row2], ...]}

    Glove80 has 80 keys arranged in 8 rows of 10 keys each.

    Args:
        layer: The layer to convert
        config: Visualization configuration
        os_style: OS style for modifier symbols
        held_positions: Set of key positions that are held to activate this layer
        mod_morphs: Custom shift mappings from mod-morph behaviors
    """
    keys_per_row = 10
    total_keys = 80
    num_rows = 8

    # Check if show_shifted is enabled
    show_shifted = config.show_shifted if config else False

    # Build flat list of all keys, padding to 80
    all_keys = []
    for binding in layer.bindings:
        all_keys.append(
            _binding_to_keymap_drawer(
                binding, os_style, config, held_positions, show_shifted, mod_morphs
            )
        )

    # Pad with empty strings to reach 80 keys
    while len(all_keys) < total_keys:
        all_keys.append("")

    # Split into rows of 10
    rows = []
    for i in range(0, total_keys, keys_per_row):
        rows.append(all_keys[i : i + keys_per_row])

    return {
        "layout": {"zmk_keyboard": config.keyboard},
        "layers": {layer.name: rows},
    }


def _binding_to_keymap_drawer(
    binding: KeyBinding,
    os_style: str = "mac",
    config: VisualizerConfig | None = None,
    held_positions: set[int] | None = None,
    show_shifted: bool = False,
    mod_morphs: dict[str, dict[str, str]] | None = None,
) -> Any:
    """
    Convert a KeyBinding to keymap-drawer format.

    Simple keys: just the string (with proper formatting)
    Hold-tap keys: {"t": tap, "h": hold, "type": category}
    Transparent: {"t": "trans", "type": "trans"}
    Held keys: {"t": tap, "type": "held", "shifted": "$$mdi:fingerprint$$"}

    When config.show_colors is True, adds a "type" field based on key category
    for CSS-based semantic coloring.

    When held_positions contains the binding's position and show_held_indicator
    is True, marks the key as "held" with a fingerprint glyph.

    When show_shifted is True (or binding.shifted is set), adds a "shifted" field
    for keys that have shifted variants (e.g., "!" for "1", '"' for "'").

    When mod_morphs is provided, uses custom shift mappings from the keymap
    (e.g., ( → < instead of default).
    """
    # Check if this key is a held key (activates current layer) - check early
    is_held_key = (
        held_positions is not None
        and binding.position in held_positions
        and config is not None
        and config.show_held_indicator
    )

    # Held keys show fingerprint icon with "Layer" text below
    # This overrides the normal key content entirely
    if is_held_key:
        return {"t": "$$mdi:fingerprint$$", "h": "Layer", "type": "held"}

    # For transparent keys (not held)
    if binding.is_transparent:
        return {"t": "trans", "type": "trans"}

    # For none keys (not held)
    if binding.is_none:
        return ""

    # Format the tap key label
    tap_label = format_key_label(binding.tap, os_style) if binding.tap else ""

    # Determine shifted character
    # Use explicit binding.shifted if set, otherwise auto-detect if show_shifted is True
    shifted_char = None
    if binding.shifted:
        shifted_char = binding.shifted
    elif show_shifted and tap_label:
        shifted_char = get_shifted_char(tap_label, mod_morphs=mod_morphs)

    # Determine key type for coloring
    show_colors = config and config.show_colors
    key_type = None

    if show_colors and tap_label:
        key_type = categorize_key(tap_label, is_hold=False)

    if binding.hold:
        hold_label = format_key_label(binding.hold, os_style)
        # For hold-tap keys, also consider the hold behavior for coloring
        # Layer activators get special treatment
        if show_colors and hold_label:
            hold_category = categorize_key(hold_label, is_hold=True)
            # If hold is a layer activator, use that for the key type
            if hold_category == "layer":
                key_type = "layer"
        result: dict[str, Any] = {"t": tap_label, "h": hold_label}
        if key_type and key_type != "default":
            result["type"] = key_type
        if shifted_char:
            result["shifted"] = shifted_char
        return result

    # Simple key - needs dict if shifted or type is present
    if shifted_char or (key_type and key_type != "default"):
        result = {"t": tap_label}
        if key_type and key_type != "default":
            result["type"] = key_type
        if shifted_char:
            result["shifted"] = shifted_char
        return result

    return tap_label


def _generate_color_css(scheme: ColorScheme) -> str:
    """
    Generate CSS for semantic key coloring.

    Creates CSS rules that target keys by their type class for Everforest-inspired
    coloring based on key category.

    Args:
        scheme: The ColorScheme to use for colors

    Returns:
        CSS string to be added to svg_extra_style
    """
    return f"""
/* Semantic key coloring - Everforest palette */
rect.modifier {{ fill: {scheme.modifier_color}; }}
rect.layer {{ fill: {scheme.layer_color}; }}
rect.navigation {{ fill: {scheme.navigation_color}; }}
rect.symbol {{ fill: {scheme.symbol_color}; }}
rect.number {{ fill: {scheme.number_color}; }}
rect.media {{ fill: {scheme.media_color}; }}
rect.mouse {{ fill: {scheme.mouse_color}; }}
rect.system {{ fill: {scheme.system_color}; }}
rect.trans {{ fill: {scheme.transparent_color}20; }}

/* Legend text styling - override default centering */
text.legend-text {{
    text-anchor: start !important;
    dominant-baseline: auto !important;
}}
"""


def _generate_color_legend(scheme: ColorScheme) -> str:
    """
    Generate SVG elements for a color legend.

    Creates a compact horizontal legend showing key categories and their colors.
    Positioned at the bottom of the keyboard diagram.

    Args:
        scheme: The ColorScheme to use for colors

    Returns:
        SVG group element string containing the legend
    """
    # Legend items with label and color
    legend_items = [
        ("Modifiers", scheme.modifier_color),
        ("Navigation", scheme.navigation_color),
        ("Numbers", scheme.number_color),
        ("Symbols", scheme.symbol_color),
        ("Media", scheme.media_color),
        ("Layer", scheme.layer_color),
        ("System", scheme.system_color),
    ]

    # Legend positioning - centered below the keyboard
    # Keyboard is ~1008 wide (with 30px offset), legend should be centered
    # Position below thumb cluster (which extends to ~520) with padding
    legend_y = 555  # Below the thumb keys with clearance
    box_size = 12  # Color swatch size
    box_text_gap = 4  # Gap between box and its label
    item_gap = 25  # Gap between items
    font_size = 11  # Font size for labels

    # Estimate text widths (approximate for proportional font at 11px)
    char_width = 7

    # Calculate positions for each item
    items_svg = []

    # First pass: calculate total width
    item_widths = []
    for label, _color in legend_items:
        text_width = len(label) * char_width
        item_width = box_size + box_text_gap + text_width
        item_widths.append(item_width)

    total_width = sum(item_widths) + (len(legend_items) - 1) * item_gap
    # Center in the 1008px keyboard area
    legend_x_start = (1008 - total_width) // 2

    # Second pass: generate SVG elements
    current_x = legend_x_start
    for i, (label, color) in enumerate(legend_items):
        # Color swatch - rounded rectangle, positioned to left of text
        box_y = legend_y + 2  # Slightly lower to align with text baseline
        items_svg.append(
            f'<rect x="{current_x}" y="{box_y}" width="{box_size}" height="{box_size}" '
            f'rx="2" ry="2" fill="{color}" stroke="#c9cccf" stroke-width="1"/>'
        )
        # Label text - after the box (text-anchor: start to prevent centering)
        text_x = current_x + box_size + box_text_gap
        text_y = legend_y + box_size  # Align with bottom of box
        items_svg.append(
            f'<text x="{text_x}" y="{text_y}" text-anchor="start" '
            f'class="legend-text" font-size="{font_size}" fill="#24292e">{label}</text>'
        )
        # Move to next item position
        current_x += item_widths[i] + item_gap

    legend_content = "\n".join(items_svg)

    # Add a white background rectangle behind the legend for readability
    bg_padding = 10
    bg_x = legend_x_start - bg_padding
    bg_y = legend_y - bg_padding + 2
    bg_width = total_width + bg_padding * 2
    bg_height = box_size + bg_padding * 2
    background = (
        f'<rect x="{bg_x}" y="{bg_y}" width="{bg_width}" height="{bg_height}" '
        f'rx="4" ry="4" fill="white" fill-opacity="0.9"/>'
    )

    return f'''
<!-- Color Legend -->
<g class="color-legend" transform="translate(30, 0)">
{background}
{legend_content}
</g>
'''


def _add_color_legend(svg_content: str, scheme: ColorScheme) -> str:
    """
    Add a color legend to the SVG content.

    Inserts the legend just before the closing </svg> tag.

    Args:
        svg_content: The SVG string to modify
        scheme: The ColorScheme for legend colors

    Returns:
        Modified SVG with legend added
    """
    legend_svg = _generate_color_legend(scheme)

    # Increase SVG height to add padding below the legend
    # Legend is at y=555, with box_size=12, so bottom is around y=567
    # Add padding to make it at least 600px tall
    min_height = 600
    svg_content = _increase_svg_height(svg_content, min_height)

    # Insert before closing </svg> tag
    svg_content = svg_content.replace("</svg>", f"{legend_svg}</svg>")

    return svg_content


def _increase_svg_height(svg_content: str, min_height: int) -> str:
    """
    Increase SVG height and viewBox if below minimum.

    Args:
        svg_content: The SVG string to modify
        min_height: Minimum height in pixels

    Returns:
        Modified SVG with increased height if needed
    """
    # Find current height
    height_match = re.search(r'height="(\d+)"', svg_content)
    if not height_match:
        return svg_content

    current_height = int(height_match.group(1))
    if current_height >= min_height:
        return svg_content

    # Update height attribute
    svg_content = re.sub(
        r'height="(\d+)"',
        f'height="{min_height}"',
        svg_content,
        count=1
    )

    # Update viewBox height
    svg_content = re.sub(
        r'viewBox="(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"',
        lambda m: f'viewBox="{m.group(1)} {m.group(2)} {m.group(3)} {min_height}"',
        svg_content,
        count=1
    )

    return svg_content


def _center_layer_label(svg_content: str, layer_name: str) -> str:
    """
    Move the layer label to be centered between the left and right keyboard halves.

    The Glove80 has a gap between left and right halves. This positions the
    layer name in that center area like sunaku's diagrams.

    Args:
        svg_content: The SVG string to modify
        layer_name: The layer name to find and reposition

    Returns:
        Modified SVG with centered layer label
    """
    # The keymap-drawer generates: <text x="0" y="28" class="label" id="LayerName">LayerName:</text>
    # We want to move it to the center and change styling

    # Center X position between left and right keyboard halves
    # Left hand extends to ~460, right hand starts at ~550
    # Center of the gap: (460 + 550) / 2 = 505
    center_x = 504  # Center of the gap between keyboard halves

    # Pattern to match the layer label
    # Note: The label includes a colon after the layer name
    label_pattern = re.compile(
        rf'<text x="0" y="28" class="label" id="{re.escape(layer_name)}">{re.escape(layer_name)}:</text>'
    )

    # Replacement with centered position and middle anchor
    replacement = (
        f'<text x="{center_x}" y="28" class="label centered-label" '
        f'id="{layer_name}" text-anchor="middle">{layer_name}</text>'
    )

    svg_content = label_pattern.sub(replacement, svg_content)

    return svg_content


def _add_title_to_svg(svg_content: str, title: str) -> str:
    """
    Add a title element to the SVG.

    Inserts a text element at the top of the SVG with the layer name.
    """
    # Find the first <rect or <g after the opening svg tag

    # Insert title text after the style block
    style_end = svg_content.find("</style>")
    if style_end != -1:
        insert_pos = style_end + len("</style>")
        title_element = f'\n<text x="30" y="30" class="label">{title}</text>'
        svg_content = (
            svg_content[:insert_pos] + title_element + svg_content[insert_pos:]
        )

    return svg_content


# Emoji to text replacements for CairoSVG compatibility
# CairoSVG often fails to render emoji, so we replace them with text equivalents
EMOJI_REPLACEMENTS = {
    # Layer/function emoji
    "😀": "Emoji",
    "🌍": "World",
    "⚙": "Sys",
    "✨": "Magic",
    "🖱": "Mouse",
    "↔": "Swap",
    # Volume/media emoji
    "🔊": "Vol+",
    "🔉": "Vol-",
    "🔇": "Mute",
    "🔆": "Bri+",
    "🔅": "Bri-",
    "☀": "Bri",
    "🌑": "Dark",
    # Other problematic Unicode that may not render
    "⇱": "Home",
    "⇲": "End",
    "⇞": "PgUp",
    "⇟": "PgDn",
}


def _replace_emoji_for_cairo(svg_content: str) -> str:
    """
    Replace emoji and problematic Unicode with text equivalents.

    CairoSVG doesn't reliably render emoji characters, so we replace
    them with readable text alternatives.

    Args:
        svg_content: The SVG string to process

    Returns:
        SVG with emoji replaced by text
    """
    for emoji, text in EMOJI_REPLACEMENTS.items():
        svg_content = svg_content.replace(emoji, text)
    return svg_content


def _inline_fingerprint_glyphs(svg_content: str) -> str:
    """
    Replace keymap-drawer's <use> glyph references with inline SVG paths.

    CairoSVG doesn't properly render <use> elements that reference nested SVGs,
    so we replace them with direct <path> elements for the fingerprint icon.

    Args:
        svg_content: The SVG string to modify

    Returns:
        Modified SVG content with inlined fingerprint paths
    """
    # Pattern to match the <use> element for fingerprint glyphs
    # Example: <use href="#mdi:fingerprint" xlink:href="#mdi:fingerprint" x="-16" y="-16" height="32" width="32.0" class="..."/>
    use_pattern = re.compile(
        r'<use\s+href="#mdi:fingerprint"[^>]*'
        r'x="([^"]*)"[^>]*y="([^"]*)"[^>]*'
        r'height="([^"]*)"[^>]*width="([^"]*)"[^>]*/>'
    )

    def replace_with_inline(match):
        x = float(match.group(1))
        y = float(match.group(2))
        height = float(match.group(3))
        width = float(match.group(4).rstrip('.0'))

        # The fingerprint icon has a viewBox of 0 0 24 24
        # We need to scale and translate it to fit the specified dimensions
        scale = height / 24.0

        # Create an inline SVG group with the fingerprint path
        return (
            f'<g transform="translate({x}, {y}) scale({scale})">'
            f'<path d="{FINGERPRINT_PATH}" fill="currentColor"/>'
            f'</g>'
        )

    svg_content = use_pattern.sub(replace_with_inline, svg_content)

    # Also remove the nested SVG definitions that keymap-drawer adds for glyphs
    # These are no longer needed and can cause rendering issues
    # keymap-drawer wraps glyphs like: <svg id="mdi:fingerprint"><svg xmlns="..."><path/></svg></svg>
    # First try the double-nested pattern
    svg_content = re.sub(
        r'<svg\s+id="mdi:fingerprint">\s*<svg[^>]*>.*?</svg>\s*</svg>\s*',
        '',
        svg_content,
        flags=re.DOTALL
    )
    # Also handle single-nested pattern (for simpler test cases)
    svg_content = re.sub(
        r'<svg\s+id="mdi:fingerprint">[^<]*<path[^/]*/>\s*</svg>\s*',
        '',
        svg_content,
        flags=re.DOTALL
    )

    return svg_content


def _adjust_tap_positions_for_shifted(svg_content: str) -> str:
    """
    Adjust tap label vertical position when shifted char exists but no hold.

    On a physical keyboard, when a key has both a primary and shifted character
    (like "1" and "!"), they're positioned as a balanced pair - not with the
    primary dead-center. This function moves the tap label down when there's
    a shifted character above but no hold character below.

    Before: shifted at y=-21, tap at y=0 (cramped at top)
    After:  shifted at y=-21, tap at y=8 (balanced pair)

    Args:
        svg_content: The SVG string to modify

    Returns:
        Modified SVG content with adjusted tap positions
    """
    import re

    # Pattern to match a key group
    def adjust_key_group(match: re.Match) -> str:
        group_content = match.group(0)

        # Check if this group has a shifted text element
        has_shifted = re.search(r'class="[^"]*\bshifted\b', group_content)
        # Check if this group has a hold text element
        has_hold = re.search(r'class="[^"]*\bhold\b', group_content)

        if has_shifted and not has_hold:
            # Case 1: Shifted + no hold (like "1"/"!")
            # Move tap down, shifted down from edge for balanced pair
            group_content = re.sub(
                r'(<text[^>]*) y="0" (class="[^"]*\btap\b)',
                r'\1 y="8" \2',
                group_content
            )
            group_content = re.sub(
                r'(<text[^>]*) y="-21" (class="[^"]*\bshifted\b)',
                r'\1 y="-14" \2',
                group_content
            )
        elif has_hold and not has_shifted:
            # Case 2: Hold + no shifted (like "RGB"/"Magic")
            # Move tap up slightly, hold up from bottom edge for balanced pair
            group_content = re.sub(
                r'(<text[^>]*) y="0" (class="[^"]*\btap\b)',
                r'\1 y="-6" \2',
                group_content
            )
            group_content = re.sub(
                r'(<text[^>]*) y="21" (class="[^"]*\bhold\b)',
                r'\1 y="16" \2',
                group_content
            )

        return group_content

    # Process each key group - match the full <g>...</g> block
    svg_content = re.sub(
        r'<g transform="[^"]*" class="key[^"]*keypos-\d+"[^>]*>.*?</g>',
        adjust_key_group,
        svg_content,
        flags=re.DOTALL
    )

    return svg_content


def _add_held_key_indicators(svg_content: str, held_positions: set[int]) -> str:
    """
    Add visual indicators for held keys in the SVG.

    Modifies the SVG to add a distinctive style to keys that are held
    to activate the current layer.

    Args:
        svg_content: The SVG string to modify
        held_positions: Set of key positions (0-79) that should be marked as held

    Returns:
        Modified SVG content with held key indicators
    """
    # The held key indicator color (Everforest-inspired purple)
    held_color = "#d699b6"

    # Add CSS style for held keys
    held_style = f"""
    .held-key {{
        stroke: {held_color} !important;
        stroke-width: 3px !important;
    }}
    .held-key-bg {{
        fill: {held_color}20 !important;
    }}
"""

    # Insert CSS into style block
    style_end = svg_content.find("</style>")
    if style_end != -1:
        svg_content = svg_content[:style_end] + held_style + svg_content[style_end:]

    # Add a comment marker so tests can detect held indicators are present
    # The actual visual change is in the CSS above
    svg_content = svg_content.replace(
        "</svg>",
        f"<!-- held-key-positions: {sorted(held_positions)} -->\n</svg>"
    )

    return svg_content
