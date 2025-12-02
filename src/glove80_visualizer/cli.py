"""
Command-line interface for the Glove80 keymap visualizer.

This module provides the main CLI entry point using Click.
"""

import click
import sys
from pathlib import Path
from typing import Optional, List

from glove80_visualizer import __version__
from glove80_visualizer.config import VisualizerConfig
from glove80_visualizer.parser import parse_zmk_keymap, KeymapParseError
from glove80_visualizer.extractor import extract_layers
from glove80_visualizer.svg_generator import generate_layer_svg
from glove80_visualizer.pdf_generator import svg_to_pdf, merge_pdfs, generate_pdf_with_toc


@click.command()
@click.argument("keymap", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-o",
    "--output",
    type=click.Path(path_type=Path),
    help="Output file path (PDF) or directory (SVG)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["pdf", "svg"]),
    default="pdf",
    help="Output format (default: pdf)",
)
@click.option(
    "--layers",
    type=str,
    help="Comma-separated list of layer names to include",
)
@click.option(
    "--exclude-layers",
    type=str,
    help="Comma-separated list of layer names to exclude",
)
@click.option(
    "--list-layers",
    is_flag=True,
    help="List available layers and exit",
)
@click.option(
    "--config",
    "config_file",
    type=click.Path(exists=True, path_type=Path),
    help="Path to YAML configuration file",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output",
)
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    help="Suppress all output except errors",
)
@click.option(
    "--no-toc",
    is_flag=True,
    help="Disable table of contents in PDF output",
)
@click.option(
    "--continue-on-error",
    is_flag=True,
    help="Continue processing if a layer fails to render",
)
@click.version_option(version=__version__)
def main(
    keymap: Path,
    output: Optional[Path],
    output_format: str,
    layers: Optional[str],
    exclude_layers: Optional[str],
    list_layers: bool,
    config_file: Optional[Path],
    verbose: bool,
    quiet: bool,
    no_toc: bool,
    continue_on_error: bool,
) -> None:
    """
    Generate PDF/SVG visualizations of Glove80 keyboard layers.

    KEYMAP is the path to a ZMK .keymap file.

    Examples:

        # Generate PDF with all layers
        glove80-viz my-keymap.keymap -o layers.pdf

        # Generate SVG files
        glove80-viz my-keymap.keymap -o ./svgs --format svg

        # Generate specific layers only
        glove80-viz my-keymap.keymap -o layers.pdf --layers QWERTY,Symbol,Cursor

        # List available layers
        glove80-viz my-keymap.keymap --list-layers
    """
    # Helper for output
    def log(msg: str, force: bool = False) -> None:
        if (verbose or force) and not quiet:
            click.echo(msg)

    def error(msg: str) -> None:
        click.echo(f"Error: {msg}", err=True)

    # Load config
    if config_file:
        config = VisualizerConfig.from_file(str(config_file))
    else:
        config = VisualizerConfig()

    config.include_toc = not no_toc
    config.continue_on_error = continue_on_error

    # Parse keymap file
    log(f"Parsing keymap: {keymap}")
    try:
        yaml_content = parse_zmk_keymap(keymap)
    except KeymapParseError as e:
        error(str(e))
        sys.exit(1)

    # Parse include/exclude filters
    include_list = [l.strip() for l in layers.split(",")] if layers else None
    exclude_list = [l.strip() for l in exclude_layers.split(",")] if exclude_layers else None

    # Extract layers
    extracted_layers = extract_layers(yaml_content, include=include_list, exclude=exclude_list)

    if not extracted_layers:
        error("No layers found in keymap")
        sys.exit(1)

    # List layers mode
    if list_layers:
        click.echo("Available layers:")
        for layer in extracted_layers:
            click.echo(f"  {layer.index}: {layer.name}")
        return

    # Check output path
    if not output:
        # Default output name based on input
        if output_format == "pdf":
            output = keymap.with_suffix(".pdf")
        else:
            output = keymap.parent / f"{keymap.stem}_svgs"

    log(f"Found {len(extracted_layers)} layers")

    # Generate SVGs
    svgs: List[str] = []
    failed_layers: List[str] = []

    for layer in extracted_layers:
        log(f"  Generating SVG for layer: {layer.name}")
        try:
            svg = generate_layer_svg(layer, config)
            svgs.append(svg)
        except Exception as e:
            if continue_on_error:
                failed_layers.append(layer.name)
                log(f"  Warning: Failed to render layer {layer.name}: {e}", force=True)
                svgs.append(None)  # Placeholder
            else:
                error(f"Failed to render layer {layer.name}: {e}")
                sys.exit(1)

    # Filter out failed layers
    if continue_on_error:
        valid_pairs = [(l, s) for l, s in zip(extracted_layers, svgs) if s is not None]
        if not valid_pairs:
            error("All layers failed to render")
            sys.exit(1)
        if failed_layers:
            click.echo(f"Warning: Skipped {len(failed_layers)} layer(s): {', '.join(failed_layers)}")
        extracted_layers = [p[0] for p in valid_pairs]
        svgs = [p[1] for p in valid_pairs]

    # Output based on format
    if output_format == "svg":
        # Create output directory
        output.mkdir(parents=True, exist_ok=True)
        for layer, svg in zip(extracted_layers, svgs):
            svg_path = output / f"{layer.name}.svg"
            svg_path.write_text(svg)
            log(f"  Wrote: {svg_path}")
        if not quiet:
            click.echo(f"Generated {len(svgs)} SVG files in {output}")
    else:
        # Generate PDF
        log("Generating PDF...")
        pdf_bytes = generate_pdf_with_toc(
            layers=extracted_layers,
            svgs=svgs,
            config=config,
            include_toc=config.include_toc,
        )

        # Write output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(pdf_bytes)
        if not quiet:
            click.echo(f"Generated PDF: {output}")


if __name__ == "__main__":
    main()
