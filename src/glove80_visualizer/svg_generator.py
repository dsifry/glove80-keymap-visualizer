"""
SVG generation module.

This module generates SVG diagrams for keyboard layers using keymap-drawer.
"""

from typing import List, Optional, Dict, Any
from io import StringIO
import yaml

from keymap_drawer.draw.draw import KeymapDrawer
from keymap_drawer.config import Config as KDConfig

from glove80_visualizer.models import Layer, KeyBinding
from glove80_visualizer.config import VisualizerConfig


# Key label mappings for better display
KEY_LABEL_MAP = {
    # Modifiers
    "LSHIFT": "⇧",
    "RSHIFT": "⇧",
    "LSHFT": "⇧",
    "RSHFT": "⇧",
    "LCTRL": "⌃",
    "RCTRL": "⌃",
    "LALT": "⌥",
    "RALT": "⌥",
    "LGUI": "⌘",
    "RGUI": "⌘",
    # Special keys
    "&trans": "▽",
    "trans": "▽",
    "&none": "",
    "none": "",
    # Navigation
    "BSPC": "⌫",
    "DEL": "⌦",
    "ENTER": "↵",
    "SPACE": "␣",
    "TAB": "⇥",
    "ESC": "⎋",
    "LEFT": "←",
    "RIGHT": "→",
    "UP": "↑",
    "DOWN": "↓",
    "HOME": "⇱",
    "END": "⇲",
    "PG UP": "⇞",
    "PG DN": "⇟",
    "CAPS": "⇪",
}


def generate_layer_svg(
    layer: Layer,
    config: Optional[VisualizerConfig] = None,
    include_title: bool = False,
) -> str:
    """
    Generate an SVG diagram for a single keyboard layer.

    Args:
        layer: The Layer object to visualize
        config: Optional configuration for styling
        include_title: Whether to include the layer name in the SVG

    Returns:
        SVG content as a string
    """
    if config is None:
        config = VisualizerConfig()

    # Convert Layer to keymap-drawer format
    keymap_data = _layer_to_keymap_drawer_format(layer, config)

    # Create keymap-drawer config
    kd_config = KDConfig()

    # Generate SVG
    out = StringIO()
    drawer = KeymapDrawer(config=kd_config, out=out, **keymap_data)
    drawer.print_board(draw_layers=[layer.name])

    svg_content = out.getvalue()

    # Optionally add title
    if include_title:
        svg_content = _add_title_to_svg(svg_content, layer.name)

    return svg_content


def generate_all_layer_svgs(
    layers: List[Layer],
    config: Optional[VisualizerConfig] = None,
) -> List[str]:
    """
    Generate SVG diagrams for all layers.

    Args:
        layers: List of Layer objects to visualize
        config: Optional configuration for styling

    Returns:
        List of SVG content strings, one per layer
    """
    return [generate_layer_svg(layer, config) for layer in layers]


def format_key_label(key: str) -> str:
    """
    Format a key name for display.

    Converts ZMK key names to human-readable labels.

    Args:
        key: The ZMK key name (e.g., "LSHIFT", "&trans")

    Returns:
        Formatted label for display (e.g., "⇧", "▽")
    """
    if not key:
        return ""

    # Check direct mapping first
    if key in KEY_LABEL_MAP:
        return KEY_LABEL_MAP[key]

    # Check case-insensitive for symbol mappings
    key_upper = key.upper()
    if key_upper in KEY_LABEL_MAP:
        return KEY_LABEL_MAP[key_upper]

    # For all-caps keys that aren't mapped, convert to title case
    if key.isupper() and len(key) > 1:
        return key.title()

    # Return original if no mapping
    return key


def _layer_to_keymap_drawer_format(
    layer: Layer,
    config: VisualizerConfig,
) -> Dict[str, Any]:
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
        all_keys.append(_binding_to_keymap_drawer(binding))

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


def _binding_to_keymap_drawer(binding: KeyBinding) -> Any:
    """
    Convert a KeyBinding to keymap-drawer format.

    Simple keys: just the string
    Hold-tap keys: {"t": tap, "h": hold}
    Transparent: {"t": "▽", "type": "trans"}
    """
    if binding.is_transparent:
        return {"t": "▽", "type": "trans"}

    if binding.is_none:
        return ""

    if binding.hold:
        return {"t": binding.tap, "h": binding.hold}

    return binding.tap


def _add_title_to_svg(svg_content: str, title: str) -> str:
    """
    Add a title element to the SVG.

    Inserts a text element at the top of the SVG with the layer name.
    """
    # Find the first <rect or <g after the opening svg tag
    import re

    # Insert title text after the style block
    style_end = svg_content.find("</style>")
    if style_end != -1:
        insert_pos = style_end + len("</style>")
        title_element = f'\n<text x="30" y="30" class="label">{title}</text>'
        svg_content = (
            svg_content[:insert_pos] + title_element + svg_content[insert_pos:]
        )

    return svg_content
