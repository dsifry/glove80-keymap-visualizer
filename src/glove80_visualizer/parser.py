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
