"""
ZMK keymap parser module.

This module handles parsing ZMK .keymap files into intermediate YAML
representation using keymap-drawer.
"""

import re
import warnings
from pathlib import Path

import yaml
from keymap_drawer.config import ParseConfig
from keymap_drawer.parse.zmk import ZmkKeymapParser

from glove80_visualizer.models import Combo


class KeymapParseError(Exception):
    """Raised when a keymap file cannot be parsed."""

    pass


def validate_keymap_path(path: Path) -> None:
    """
    Validate that a keymap file path is valid.

    Args:
        path: Path to the keymap file

    Raises:
        FileNotFoundError: If the file does not exist
        UserWarning: If the file has an unexpected extension
    """
    if not path.exists():
        raise FileNotFoundError(f"Keymap file not found: {path}")

    if path.suffix != ".keymap":
        warnings.warn(
            f"Keymap file has unexpected extension '{path.suffix}', expected '.keymap'",
            UserWarning,
        )


def parse_zmk_keymap(
    keymap_path: Path,
    keyboard: str = "glove80",
    columns: int = 10,
) -> str:
    """
    Parse a ZMK keymap file into YAML representation.

    Uses keymap-drawer's parser to convert the .keymap file into an
    intermediate YAML format that can be used for SVG generation.

    Args:
        keymap_path: Path to the ZMK .keymap file
        keyboard: Keyboard type for physical layout (default: "glove80")
        columns: Number of columns for layout (used by keymap-drawer)

    Returns:
        YAML string containing the parsed keymap data with layers

    Raises:
        FileNotFoundError: If the keymap file does not exist
        KeymapParseError: If the keymap cannot be parsed

    Example:
        >>> yaml_content = parse_zmk_keymap(Path("my-keymap.keymap"))
        >>> print(yaml_content)
        layout:
          zmk_keyboard: glove80
        layers:
          QWERTY:
            - [Q, W, E, R, T, ...]
    """
    # Validate the path exists
    validate_keymap_path(keymap_path)

    # Create parser with default config
    config = ParseConfig()
    parser = ZmkKeymapParser(config=config, columns=columns)

    try:
        with open(keymap_path) as f:
            result = parser.parse(f)
    except Exception as e:
        # Wrap any parsing errors in our custom exception
        error_msg = str(e)
        if "keymap" in error_msg.lower() or "compatible" in error_msg.lower():
            raise KeymapParseError(
                f"No keymap found - is this a valid ZMK file? {error_msg}"
            ) from e
        raise KeymapParseError(f"Failed to parse keymap: {error_msg}") from e  # pragma: no cover

    # Override the keyboard type in the result
    if "layout" not in result:  # pragma: no cover
        # keymap-drawer always returns a layout section
        result["layout"] = {}
    result["layout"]["zmk_keyboard"] = keyboard

    # Convert to YAML string, preserving key order (sort_keys=False is critical!)
    return yaml.dump(result, default_flow_style=False, allow_unicode=True, sort_keys=False)


def parse_mod_morph_behaviors(keymap_content: str) -> dict[str, dict[str, str]]:
    """
    Parse mod-morph behaviors from a ZMK keymap file to extract custom shifted characters.

    Mod-morph behaviors allow keys to output different characters when shift is held.
    For example:
        parang_left: tap=( shifted=<
        parang_right: tap=) shifted=>

    Args:
        keymap_content: Raw content of a .keymap file

    Returns:
        Dictionary mapping behavior name to {tap: str, shifted: str}
        Only includes behaviors that use shift modifiers (MOD_LSFT or MOD_RSFT)

    Example:
        >>> content = '''
        ... parang_left: left_paren {
        ...     compatible = "zmk,behavior-mod-morph";
        ...     bindings = <&kp LPAR>, <&kp LT>;
        ...     mods = <(MOD_LSFT|MOD_RSFT)>;
        ... };
        ... '''
        >>> parse_mod_morph_behaviors(content)
        {'parang_left': {'tap': 'LPAR', 'shifted': 'LT'}}
    """
    result: dict[str, dict[str, str]] = {}

    # Pattern to match mod-morph behavior blocks
    # Captures: behavior_name, block_content
    behavior_pattern = re.compile(
        r"(\w+):\s*\w*\s*\{\s*"  # behavior_name: optional_label {
        r'compatible\s*=\s*"zmk,behavior-mod-morph"[^}]*'  # must be mod-morph
        r"\}",
        re.DOTALL,
    )

    # Pattern to extract bindings (tap and shifted)
    bindings_pattern = re.compile(r"bindings\s*=\s*<&kp\s+(\w+)>\s*,\s*<&kp\s+(\w+)>")

    # Pattern to check for shift modifiers
    shift_mods_pattern = re.compile(r"mods\s*=\s*<[^>]*MOD_[LR]SFT[^>]*>")

    for match in behavior_pattern.finditer(keymap_content):
        behavior_name = match.group(1)
        block_content = match.group(0)

        # Check if this is a shift-based morph
        if not shift_mods_pattern.search(block_content):
            continue

        # Extract the tap and shifted bindings
        bindings_match = bindings_pattern.search(block_content)
        if bindings_match:
            tap_key = bindings_match.group(1)
            shifted_key = bindings_match.group(2)
            result[behavior_name] = {
                "tap": tap_key,
                "shifted": shifted_key,
            }

    return result


# ZMK position → thumb key name mapping
THUMB_KEY_NAMES: dict[int, str] = {
    # Left thumb (upper row: T1-T3, lower row: T4-T6)
    52: "LT1",
    53: "LT2",
    54: "LT3",
    69: "LT4",
    70: "LT5",
    71: "LT6",
    # Right thumb (upper row: T1-T3, lower row: T4-T6)
    57: "RT1",
    56: "RT2",
    55: "RT3",
    74: "RT4",
    73: "RT5",
    72: "RT6",
}


def _positions_to_name(positions: list[int]) -> str:
    """
    Convert ZMK positions to human-readable thumb key names.

    Args:
        positions: List of ZMK key positions

    Returns:
        String like "LT3+LT6" or "RT1+RT4" or "25+26" for non-thumb keys
    """
    names = []
    for pos in sorted(positions):
        if pos in THUMB_KEY_NAMES:
            names.append(THUMB_KEY_NAMES[pos])
        else:
            names.append(str(pos))
    return "+".join(names)


def _format_combo_action(key_data: dict | str, combo_name: str = "") -> str:
    """
    Format a combo binding into a human-readable action label.

    Args:
        key_data: The key binding data from keymap-drawer
        combo_name: Optional combo node name for fallback

    Returns:
        Human-readable action string
    """
    # Handle string bindings (e.g., "CAPSLOCK", "]", "[")
    if isinstance(key_data, str):
        # Clean up raw binding strings
        if key_data.startswith("&"):
            # Custom behavior - try to parse known patterns
            # &mod_tab_chord LGUI 17 -> Cmd+Tab
            # &mod_tab_chord LCTL 17 -> Ctrl+Tab
            if "mod_tab_chord" in key_data:
                if "LGUI" in key_data or "GUI" in key_data:
                    return "Cmd+Tab"
                if "LCTL" in key_data or "CTL" in key_data:
                    return "Ctrl+Tab"
                if "LALT" in key_data or "ALT" in key_data:
                    return "Alt+Tab"
                return "Tab Switcher"

            # Fallback to combo name if available
            if combo_name:
                return _derive_action_from_name(combo_name)
            return key_data

        # Format common key names
        return _format_key_name(key_data)

    # Handle dict bindings with tap/hold
    if isinstance(key_data, dict):
        tap = key_data.get("t", "")
        hold = key_data.get("h", "")

        # Handle toggle layer
        if hold == "toggle":
            return f"Toggle {tap}"

        # Handle sticky keys
        if hold == "sticky":
            return _format_sticky_key(tap)

        # Just return tap if no special handling
        if tap:
            return _format_key_name(tap)

    # Fallback to combo name
    if combo_name:
        return _derive_action_from_name(combo_name)

    return str(key_data)


def _format_key_name(key: str) -> str:
    """Format a key name for display."""
    # Common key name mappings
    key_names = {
        "CAPSLOCK": "Caps Lock",
        "CAPS": "Caps Lock",
        "LGUI": "Left Cmd",
        "RGUI": "Right Cmd",
        "LALT": "Left Alt",
        "RALT": "AltGr",
        "LCTL": "Left Ctrl",
        "RCTL": "Right Ctrl",
        "LSHFT": "Left Shift",
        "RSHFT": "Right Shift",
    }
    return key_names.get(key.upper(), key)


def _format_sticky_key(tap: str) -> str:
    """Format a sticky key modifier combo."""
    # Handle combined modifiers like "Gui+Alt+Ctl+LSHFT"
    tap_upper = tap.upper()

    if "GUI" in tap_upper and "ALT" in tap_upper and "CTL" in tap_upper and "SHFT" in tap_upper:
        return "Sticky Hyper"
    if "ALT" in tap_upper and "CTL" in tap_upper and "SHFT" in tap_upper:
        return "Sticky Meh"
    if tap_upper == "RALT":
        return "Sticky AltGr"
    if tap_upper == "LALT":
        return "Sticky Alt"
    if "SHFT" in tap_upper:
        return "Sticky Shift"
    if "CTL" in tap_upper:
        return "Sticky Ctrl"
    if "GUI" in tap_upper:
        return "Sticky Cmd"

    return f"Sticky {tap}"


def _derive_action_from_name(combo_name: str) -> str:
    """
    Derive a human-readable action from the combo node name.

    Args:
        combo_name: The ZMK combo node name (e.g., "combo_alt_tab_switcher")

    Returns:
        Human-readable action (e.g., "Alt+Tab Switcher")
    """
    # Remove common prefixes
    name = combo_name
    for prefix in ("combo_", "cmb_"):
        if name.startswith(prefix):
            name = name[len(prefix) :]
            break

    # Replace underscores with spaces and title case
    words = name.replace("_", " ").split()

    # Capitalize each word, handling special cases
    result = []
    for word in words:
        word_lower = word.lower()
        # Keep modifier names intact
        if word_lower in ("alt", "ctrl", "shift", "gui", "cmd", "tab"):
            result.append(word.capitalize())
        elif word_lower == "altgr":
            result.append("AltGr")
        else:
            result.append(word.capitalize())

    return " ".join(result)


def parse_combos(
    keymap_path: Path,
    columns: int = 10,
) -> list[Combo]:
    """
    Parse combos from a ZMK keymap file.

    Uses keymap-drawer's parser which handles C preprocessing (via pcpp)
    to expand #ifdef, #define, and #include directives.

    Args:
        keymap_path: Path to the ZMK .keymap file
        columns: Number of columns for layout (used by keymap-drawer)

    Returns:
        List of Combo objects

    Raises:
        FileNotFoundError: If the keymap file does not exist
        KeymapParseError: If the keymap cannot be parsed
    """
    validate_keymap_path(keymap_path)

    config = ParseConfig()
    parser = ZmkKeymapParser(config=config, columns=columns)

    try:
        with open(keymap_path) as f:
            result = parser.parse(f)
    except Exception as e:
        raise KeymapParseError(f"Failed to parse keymap for combos: {e}") from e

    combos = []
    for combo_data in result.get("combos", []):
        positions = combo_data["p"]
        key_data = combo_data["k"]
        layers = combo_data.get("l")  # None if not specified (all layers)

        # Generate human-readable name from positions
        name = _positions_to_name(positions)

        # Format the action label
        # Note: combo node names aren't exposed by keymap-drawer,
        # so we can't use them as fallback
        action = _format_combo_action(key_data)

        combo = Combo(
            name=name,
            positions=positions,
            action=action,
            layers=layers,
        )
        combos.append(combo)

    return combos
