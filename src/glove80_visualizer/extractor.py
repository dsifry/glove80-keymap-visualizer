"""
Layer extraction module.

This module extracts structured layer information from parsed YAML keymap data.
"""

from typing import List, Optional
import yaml

from glove80_visualizer.models import Layer, KeyBinding


def extract_layers(
    yaml_content: str,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
) -> List[Layer]:
    """
    Extract Layer objects from parsed keymap YAML.

    Args:
        yaml_content: YAML string from the parser
        include: Optional list of layer names to include (others excluded)
        exclude: Optional list of layer names to exclude

    Returns:
        List of Layer objects in order they appear in the keymap

    Example:
        >>> yaml = '''
        ... layers:
        ...   QWERTY:
        ...     - [Q, W, E, R, T]
        ...   Symbol:
        ...     - [!, @, #, $, %]
        ... '''
        >>> layers = extract_layers(yaml)
        >>> print(layers[0].name)
        QWERTY
    """
    # TODO: Implement layer extraction
    # 1. Parse the YAML content
    # 2. Iterate through layers
    # 3. Apply include/exclude filters
    # 4. Create KeyBinding objects for each key
    # 5. Create Layer objects with bindings
    raise NotImplementedError()


def _parse_key_binding(position: int, key_data) -> KeyBinding:
    """
    Parse a single key binding from YAML data.

    Args:
        position: The key position index
        key_data: The key data from YAML (string or dict for hold-tap)

    Returns:
        KeyBinding object representing the key
    """
    # TODO: Implement key binding parsing
    # Handle simple strings: "A" -> KeyBinding(tap="A")
    # Handle hold-tap dicts: {t: A, h: LSHIFT} -> KeyBinding(tap="A", hold="LSHIFT")
    raise NotImplementedError()
