"""
Color scheme and key categorization for semantic coloring.

This module provides color schemes and functions for categorizing keys
to apply semantic colors in visualizations.
"""

from dataclasses import dataclass


@dataclass
class ColorScheme:
    """
    Color scheme for visualization.

    Uses Everforest-inspired colors by default for semantic key coloring.

    Attributes:
        name: Name of the color scheme
        modifier_color: Color for modifier keys (Shift, Ctrl, Alt, GUI)
        layer_color: Color for layer activators and held keys
        navigation_color: Color for navigation keys (arrows, Home, End, etc.)
        symbol_color: Color for symbol keys (!@#$%^&*())
        number_color: Color for numbers and function keys
        media_color: Color for media keys (play, volume, brightness)
        mouse_color: Color for mouse keys
        system_color: Color for system keys (Reset, Boot)
        transparent_color: Color for transparent keys (dimmed)
        held_key_color: Color for held key indicators
        default_color: Color for regular alpha keys
    """

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
    default_color: str = "#d3c6aa"


# Sets of keys by category for efficient lookup
MODIFIER_KEYS = {
    # Mac symbols
    "⌘",
    "⌥",
    "⌃",
    "⇧",
    # Windows/Linux style
    "Shift",
    "Ctrl",
    "Alt",
    "Win",
    "Super",
    "Meta",
    "LShift",
    "RShift",
    "LCtrl",
    "RCtrl",
    "LAlt",
    "RAlt",
    "LGui",
    "RGui",
    "LWin",
    "RWin",
    # Meh/Hyper
    "Meh",
    "Hypr",
}

NAVIGATION_KEYS = {
    # Arrow symbols
    "←",
    "→",
    "↑",
    "↓",
    # Text labels
    "Left",
    "Right",
    "Up",
    "Down",
    "Home",
    "End",
    "PgUp",
    "PgDn",
    "PageUp",
    "PageDown",
    "Ins",
    "Insert",
    "Del",
    "Delete",
}

NUMBER_KEYS = {
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "F1",
    "F2",
    "F3",
    "F4",
    "F5",
    "F6",
    "F7",
    "F8",
    "F9",
    "F10",
    "F11",
    "F12",
}

SYMBOL_KEYS = {
    "!",
    "@",
    "#",
    "$",
    "%",
    "^",
    "&",
    "*",
    "(",
    ")",
    "[",
    "]",
    "{",
    "}",
    "<",
    ">",
    "-",
    "_",
    "=",
    "+",
    "\\",
    "|",
    "/",
    "?",
    "`",
    "~",
    "'",
    '"',
    ";",
    ":",
    ",",
    ".",
}

MEDIA_KEYS = {
    # Media control symbols
    "⏯",
    "⏭",
    "⏮",
    "⏹",
    "⏺",
    "⏪",
    "⏩",
    # Volume symbols
    "🔇",
    "🔊",
    "🔉",
    "🔈",
    # Brightness symbols
    "🔆",
    "🔅",
    "☀",
    "🌑",
    # Text labels
    "Play",
    "Pause",
    "Stop",
    "Next",
    "Prev",
    "Vol+",
    "Vol-",
    "Mute",
    "Bri+",
    "Bri-",
}

MOUSE_KEYS = {
    "🖱↑",
    "🖱↓",
    "🖱←",
    "🖱→",
    "🖱L",
    "🖱R",
    "🖱M",
    "🖱",
    "Mouse",
}

SYSTEM_KEYS = {
    "Reset",
    "Boot",
    "Bootloader",
    "BT1",
    "BT2",
    "BT3",
    "BT4",
    "BT5",
    "BT Clr",
    "BT Clear",
    "USB",
    "Out USB",
    "Out BT",
}

TRANSPARENT_KEYS = {
    "▽",
    "trans",
    "&trans",
    "Trans",
}


def categorize_key(label: str, is_hold: bool = False) -> str:
    """
    Categorize a key for color coding.

    Args:
        label: The formatted key label (e.g., "⌘", "A", "←")
        is_hold: Whether this key is from a hold behavior (affects layer detection)

    Returns:
        Category string: "modifier", "navigation", "number", "symbol",
        "media", "mouse", "system", "transparent", "layer", or "default"
    """
    # Check transparent first (most distinctive)
    if label in TRANSPARENT_KEYS:
        return "transparent"

    # Check specific categories
    if label in MODIFIER_KEYS:
        return "modifier"

    if label in NAVIGATION_KEYS:
        return "navigation"

    if label in NUMBER_KEYS:
        return "number"

    if label in SYMBOL_KEYS:
        return "symbol"

    if label in MEDIA_KEYS:
        return "media"

    # Mouse keys - also check if label starts with 🖱
    if label in MOUSE_KEYS or label.startswith("🖱"):
        return "mouse"

    if label in SYSTEM_KEYS:
        return "system"

    # Layer names are only colored when they appear as hold behaviors
    if is_hold:
        return "layer"

    return "default"


def get_key_color(label: str, scheme: ColorScheme, is_hold: bool = False) -> str:
    """
    Get the color for a key based on its category.

    Args:
        label: The formatted key label
        scheme: The color scheme to use
        is_hold: Whether this key is from a hold behavior

    Returns:
        Hex color string (e.g., "#7fbbb3")
    """
    category = categorize_key(label, is_hold)

    color_map = {
        "modifier": scheme.modifier_color,
        "navigation": scheme.navigation_color,
        "number": scheme.number_color,
        "symbol": scheme.symbol_color,
        "media": scheme.media_color,
        "mouse": scheme.mouse_color,
        "system": scheme.system_color,
        "transparent": scheme.transparent_color,
        "layer": scheme.layer_color,
        "default": scheme.default_color,
    }

    return color_map.get(category, scheme.default_color)
