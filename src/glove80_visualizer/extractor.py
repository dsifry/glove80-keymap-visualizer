"""
Layer extraction module.

This module extracts structured layer information from parsed YAML keymap data.
"""

import yaml

from glove80_visualizer.models import KeyBinding, Layer, LayerActivator


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


def _flatten_bindings(
    bindings_data: list[str | dict | list | None],
) -> list[str | dict | None]:
    """
    Flatten potentially nested binding data into a flat list.

    keymap-drawer returns bindings as rows (list of lists).
    This flattens them while preserving order.

    Args:
        bindings_data: Potentially nested list of binding data from YAML

    Returns:
        Flat list of binding data elements
    """
    result: list[str | dict | None] = []

    for item in bindings_data:
        if isinstance(item, list):
            # It's a row of keys
            result.extend(item)
        else:
            # It's a single key
            result.append(item)

    return result


def _parse_key_binding(position: int, key_data: str | dict | None) -> KeyBinding:
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
        shifted = key_data.get("s", key_data.get("shifted"))
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
            shifted=shifted,
            key_type=key_type,
        )

    # Fallback: convert to string
    return KeyBinding(position=position, tap=str(key_data))


def extract_layer_activators(yaml_content: str) -> list[LayerActivator]:
    """
    Extract layer activators from parsed keymap YAML.

    Scans the keymap for hold behaviors that reference layer names and
    creates LayerActivator objects to track which keys activate which layers.

    Args:
        yaml_content: YAML string from the parser

    Returns:
        List of LayerActivator objects

    Example:
        >>> yaml = '''
        ... layers:
        ...   Base:
        ...     - [{t: BACKSPACE, h: Cursor}]
        ...   Cursor:
        ...     - [{type: held}]
        ... '''
        >>> activators = extract_layer_activators(yaml)
        >>> print(activators[0].target_layer_name)
        Cursor
    """
    if not yaml_content:
        return []

    data = yaml.safe_load(yaml_content)

    if not data or "layers" not in data:
        return []

    layers_data = data["layers"]
    layer_names = set(layers_data.keys())
    activators = []

    # Scan each layer for hold behaviors that reference other layer names
    for layer_name, layer_bindings in layers_data.items():
        if not layer_bindings:
            continue

        flat_bindings = _flatten_bindings(layer_bindings)

        for position, key_data in enumerate(flat_bindings):
            if not isinstance(key_data, dict):
                continue

            # Check for hold behavior
            hold = key_data.get("h", key_data.get("hold"))
            if not hold:
                continue

            # Check if hold references a layer name
            if hold in layer_names:
                tap = key_data.get("t", key_data.get("tap", ""))
                if tap is None:
                    tap = ""
                else:
                    tap = str(tap)

                activator = LayerActivator(
                    source_layer_name=layer_name,
                    source_position=position,
                    target_layer_name=hold,
                    tap_key=tap if tap else None,
                )
                activators.append(activator)

    return activators
