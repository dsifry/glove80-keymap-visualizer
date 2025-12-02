"""
Command-line interface for the Glove80 keymap visualizer.

This module provides the main CLI entry point using Click.
"""

import click
from pathlib import Path
from typing import Optional

from glove80_visualizer import __version__
from glove80_visualizer.config import VisualizerConfig


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
    # TODO: Implement CLI logic
    # 1. Load config from file if provided
    # 2. Parse keymap file
    # 3. If --list-layers, print layer names and exit
    # 4. Extract layers (with filtering)
    # 5. Generate SVGs
    # 6. Generate PDF or save SVGs
    raise NotImplementedError("CLI not yet implemented")


if __name__ == "__main__":
    main()
