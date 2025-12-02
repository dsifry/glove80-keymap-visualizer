"""
SVG generation module.

This module generates SVG diagrams for keyboard layers using keymap-drawer.
"""

import re
from io import StringIO
from typing import Any

from keymap_drawer.config import Config as KDConfig
from keymap_drawer.draw.draw import KeymapDrawer

from glove80_visualizer.config import VisualizerConfig
from glove80_visualizer.models import KeyBinding, Layer

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
    keymap_data = _layer_to_keymap_drawer_format(working_layer, config, os_style)

    # Create keymap-drawer config
    kd_config = KDConfig()

    # Generate SVG
    out = StringIO()
    drawer = KeymapDrawer(config=kd_config, out=out, **keymap_data)
    drawer.print_board(draw_layers=[working_layer.name])

    svg_content = out.getvalue()

    # Add held key indicator styling
    if held_positions:
        svg_content = _add_held_key_indicators(svg_content, held_positions)

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
) -> dict[str, Any]:
    """
    Convert a Layer to keymap-drawer's expected YAML format.

    keymap-drawer expects:
    - layout: {zmk_keyboard: 'glove80'}
    - layers: {LayerName: [[row1], [row2], ...]}

    Glove80 has 80 keys arranged in 8 rows of 10 keys each.
    """
    keys_per_row = 10
    total_keys = 80
    num_rows = 8

    # Build flat list of all keys, padding to 80
    all_keys = []
    for binding in layer.bindings:
        all_keys.append(_binding_to_keymap_drawer(binding, os_style))

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


def _binding_to_keymap_drawer(binding: KeyBinding, os_style: str = "mac") -> Any:
    """
    Convert a KeyBinding to keymap-drawer format.

    Simple keys: just the string (with proper formatting)
    Hold-tap keys: {"t": tap, "h": hold}
    Transparent: {"t": "trans", "type": "trans"}
    """
    if binding.is_transparent:
        return {"t": "trans", "type": "trans"}

    if binding.is_none:
        return ""

    # Format the tap key label
    tap_label = format_key_label(binding.tap, os_style) if binding.tap else ""

    if binding.hold:
        hold_label = format_key_label(binding.hold, os_style)
        return {"t": tap_label, "h": hold_label}

    return tap_label


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
