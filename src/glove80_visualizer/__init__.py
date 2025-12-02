"""
Glove80 Keymap Visualizer

Generate PDF visualizations of Glove80 keyboard layers from ZMK keymap files.
"""

from glove80_visualizer.models import KeyBinding, Layer
from glove80_visualizer.config import VisualizerConfig

__version__ = "0.1.0"
__all__ = [
    "KeyBinding",
    "Layer",
    "VisualizerConfig",
    "generate_visualization",
]


def generate_visualization(keymap_path, output_path, config=None):
    """
    Generate a PDF visualization of a Glove80 keymap.

    Args:
        keymap_path: Path to the ZMK .keymap file
        output_path: Path for the output PDF (or directory for SVG output)
        config: Optional VisualizerConfig for customization

    Returns:
        Result object with success status and any error information
    """
    # TODO: Implement the full pipeline
    # 1. Parse keymap using parser.parse_zmk_keymap()
    # 2. Extract layers using extractor.extract_layers()
    # 3. Generate SVGs using svg_generator.generate_all_layer_svgs()
    # 4. Generate PDF using pdf_generator.generate_pdf_with_toc()
    raise NotImplementedError("Pipeline not yet implemented")
