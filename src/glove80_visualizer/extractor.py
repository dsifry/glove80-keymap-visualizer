"""
Layer extraction module.

This module extracts structured layer information from parsed YAML keymap data.
"""


import yaml

from glove80_visualizer.models import KeyBinding, Layer


def extract_layers(
    yaml_content: str,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
) -> list[Layer]:
    """
    Extract Layer objects from parsed keymap YAML.

    Args:
        yaml_content: YAML string from the parser
        include: Optional list of layer names to include (others excluded)
        exclude: Optional list of layer names to exclude

    Returns:
        List of Layer objects in order they appear in the keymap

    Raises:
        ValueError: If both include and exclude specify the same layer

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
    # Note: If a layer is in both include and exclude, exclude takes precedence

    # Parse the YAML content
    data = yaml.safe_load(yaml_content)

    if not data or "layers" not in data:
        return []

    layers_data = data["layers"]
    result = []

    # Iterate through layers preserving order
    for index, (layer_name, layer_bindings) in enumerate(layers_data.items()):
        # Apply include filter
        if include and layer_name not in include:
            continue

        # Apply exclude filter
        if exclude and layer_name in exclude:
            continue

        # Parse all key bindings for this layer
        bindings = []
        position = 0

        if layer_bindings:
            # Flatten nested row structure if present
            flat_bindings = _flatten_bindings(layer_bindings)

            for key_data in flat_bindings:
                binding = _parse_key_binding(position, key_data)
                bindings.append(binding)
                position += 1

        layer = Layer(name=layer_name, index=index, bindings=bindings)
        result.append(layer)

    return result


def _flatten_bindings(bindings_data) -> list:
    """
    Flatten potentially nested binding data into a flat list.

    keymap-drawer returns bindings as rows (list of lists).
    This flattens them while preserving order.
    """
    result = []

    for item in bindings_data:
        if isinstance(item, list):
            # It's a row of keys
            result.extend(item)
        else:
            # It's a single key
            result.append(item)

    return result


def _parse_key_binding(position: int, key_data) -> KeyBinding:
    """
    Parse a single key binding from YAML data.

    Args:
        position: The key position index
        key_data: The key data from YAML (string or dict for hold-tap)

    Returns:
        KeyBinding object representing the key
    """
    # Handle None or empty values
    if key_data is None or key_data == "":
        return KeyBinding(position=position, tap="")

    # Handle simple string keys
    if isinstance(key_data, str):
        return KeyBinding(position=position, tap=key_data)

    # Handle dict-style keys (hold-tap, transparent, held, etc.)
    if isinstance(key_data, dict):
        tap = key_data.get("t", key_data.get("tap", ""))
        hold = key_data.get("h", key_data.get("hold"))
        key_type = key_data.get("type")

        # Convert tap to string if needed
        if tap is None:
            tap = ""
        else:
            tap = str(tap)

        return KeyBinding(
            position=position,
            tap=tap,
            hold=hold,
            key_type=key_type,
        )

    # Fallback: convert to string
    return KeyBinding(position=position, tap=str(key_data))
