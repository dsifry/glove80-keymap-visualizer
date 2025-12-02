"""
ZMK keymap parser module.

This module handles parsing ZMK .keymap files into intermediate YAML
representation using keymap-drawer.
"""

from pathlib import Path
import warnings
import yaml

from keymap_drawer.parse.zmk import ZmkKeymapParser
from keymap_drawer.config import ParseConfig


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
        with open(keymap_path, "r") as f:
            result = parser.parse(f)
    except Exception as e:
        # Wrap any parsing errors in our custom exception
        error_msg = str(e)
        if "keymap" in error_msg.lower() or "compatible" in error_msg.lower():
            raise KeymapParseError(
                f"No keymap found - is this a valid ZMK file? {error_msg}"
            ) from e
        raise KeymapParseError(f"Failed to parse keymap: {error_msg}") from e

    # Override the keyboard type in the result
    if "layout" not in result:
        result["layout"] = {}
    result["layout"]["zmk_keyboard"] = keyboard

    # Convert to YAML string, preserving key order (sort_keys=False is critical!)
    return yaml.dump(result, default_flow_style=False, allow_unicode=True, sort_keys=False)
