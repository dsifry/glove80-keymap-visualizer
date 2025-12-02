"""
Glove80 Keymap Visualizer

Generate PDF visualizations of Glove80 keyboard layers from ZMK keymap files.
"""

from pathlib import Path
from typing import Optional, Union

from glove80_visualizer.models import KeyBinding, Layer, VisualizationResult
from glove80_visualizer.config import VisualizerConfig
from glove80_visualizer.parser import parse_zmk_keymap, KeymapParseError
from glove80_visualizer.extractor import extract_layers
from glove80_visualizer.svg_generator import generate_layer_svg
from glove80_visualizer.pdf_generator import generate_pdf_with_toc

__version__ = "0.1.0"
__all__ = [
    "KeyBinding",
    "Layer",
    "VisualizerConfig",
    "VisualizationResult",
    "generate_visualization",
]


def generate_visualization(
    keymap_path: Union[str, Path],
    output_path: Union[str, Path],
    config: Optional[VisualizerConfig] = None,
) -> VisualizationResult:
    """
    Generate a PDF visualization of a Glove80 keymap.

    Args:
        keymap_path: Path to the ZMK .keymap file
        output_path: Path for the output PDF (or directory for SVG output)
        config: Optional VisualizerConfig for customization

    Returns:
        VisualizationResult with success status and any error information
    """
    keymap_path = Path(keymap_path)
    output_path = Path(output_path)

    if config is None:
        config = VisualizerConfig()

    try:
        # 1. Parse keymap
        yaml_content = parse_zmk_keymap(keymap_path)

        # 2. Extract layers
        layers = extract_layers(yaml_content)

        if not layers:
            return VisualizationResult(
                success=False,
                error_message="No layers found in keymap",
                layers_processed=0,
            )

        # 3. Generate SVGs
        svgs = []
        failed_layers = []

        for layer in layers:
            try:
                svg = generate_layer_svg(layer, config)
                svgs.append(svg)
            except Exception as e:
                if config.continue_on_error:
                    failed_layers.append(layer.name)
                    svgs.append(None)
                else:
                    return VisualizationResult(
                        success=False,
                        error_message=f"Failed to render layer {layer.name}: {e}",
                        layers_processed=len(svgs),
                    )

        # Filter out failed layers
        if config.continue_on_error:
            valid_pairs = [(l, s) for l, s in zip(layers, svgs) if s is not None]
            if not valid_pairs:
                return VisualizationResult(
                    success=False,
                    error_message="All layers failed to render",
                    layers_processed=0,
                )
            layers = [p[0] for p in valid_pairs]
            svgs = [p[1] for p in valid_pairs]

        # 4. Generate output
        if config.output_format == "svg":
            # Output SVG files
            output_path.mkdir(parents=True, exist_ok=True)
            for layer, svg in zip(layers, svgs):
                svg_path = output_path / f"{layer.name}.svg"
                svg_path.write_text(svg)
            return VisualizationResult(
                success=True,
                layers_processed=len(layers),
                output_path=str(output_path),
            )
        else:
            # Generate PDF
            pdf_bytes = generate_pdf_with_toc(
                layers=layers,
                svgs=svgs,
                config=config,
                include_toc=config.include_toc,
            )

            # Write output
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(pdf_bytes)

            return VisualizationResult(
                success=True,
                partial_success=len(failed_layers) > 0,
                layers_processed=len(layers),
                output_path=str(output_path),
            )

    except KeymapParseError as e:
        return VisualizationResult(
            success=False,
            error_message=str(e),
            layers_processed=0,
        )
    except Exception as e:
        return VisualizationResult(
            success=False,
            error_message=f"Unexpected error: {e}",
            layers_processed=0,
        )
