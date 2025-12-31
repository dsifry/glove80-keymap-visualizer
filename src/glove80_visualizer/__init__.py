"""
Glove80 Keymap Visualizer

Generate PDF visualizations of Glove80 keyboard layers from ZMK keymap files.
"""

from pathlib import Path

from glove80_visualizer.config import VisualizerConfig
from glove80_visualizer.extractor import extract_layers
from glove80_visualizer.models import KeyBinding, Layer, VisualizationResult
from glove80_visualizer.parser import KeymapParseError, parse_mod_morph_behaviors, parse_zmk_keymap
from glove80_visualizer.pdf_generator import generate_pdf_with_toc
from glove80_visualizer.svg_generator import generate_layer_svg

__version__ = "0.5.0"
__all__ = [
    "KeyBinding",
    "Layer",
    "VisualizerConfig",
    "VisualizationResult",
    "generate_visualization",
]


def generate_visualization(
    keymap_path: str | Path,
    output_path: str | Path,
    config: VisualizerConfig | None = None,
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

        # 1b. Parse mod-morph behaviors from raw keymap content
        raw_keymap_content = keymap_path.read_text()
        mod_morphs = parse_mod_morph_behaviors(raw_keymap_content)

        # 2. Extract layers
        layers = extract_layers(yaml_content)

        if not layers:
            return VisualizationResult(
                success=False,
                error_message="No layers found in keymap",
                layers_processed=0,
            )

        # 3. Generate SVGs
        svgs: list[str | None] = []
        failed_layers: list[str] = []

        for layer in layers:
            try:
                svg = generate_layer_svg(layer, config, mod_morphs=mod_morphs)
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
            valid_pairs = [(lyr, s) for lyr, s in zip(layers, svgs) if s is not None]
            if not valid_pairs:
                return VisualizationResult(
                    success=False,
                    error_message="All layers failed to render",
                    layers_processed=0,
                )
            layers = [p[0] for p in valid_pairs]
            # After filtering, we know all values are str (not None)
            filtered_svgs: list[str] = [p[1] for p in valid_pairs]
        else:
            # No failures possible, all svgs are strings
            filtered_svgs = [s for s in svgs if s is not None]

        # 4. Generate output
        if config.output_format == "svg":
            # Output SVG files
            output_path.mkdir(parents=True, exist_ok=True)
            for layer, svg in zip(layers, filtered_svgs):
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
                svgs=filtered_svgs,
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
