"""
Command-line interface for the Glove80 keymap visualizer.

This module provides the main CLI entry point using Click.
"""

import sys
from pathlib import Path

import click

from glove80_visualizer import __version__
from glove80_visualizer.config import VisualizerConfig
from glove80_visualizer.extractor import extract_layer_activators, extract_layers
from glove80_visualizer.models import Combo
from glove80_visualizer.parser import KeymapParseError, parse_combos, parse_zmk_keymap
from glove80_visualizer.pdf_generator import generate_pdf_with_toc
from glove80_visualizer.svg_generator import generate_layer_svg


class MutuallyExclusiveOption(click.Option):
    """Custom option class that enforces mutual exclusivity."""

    mutually_exclusive: set[str]

    def __init__(self, *args: object, **kwargs: object) -> None:
        mutex_arg = kwargs.pop("mutually_exclusive", [])
        # Cast to list[str] - we know the caller passes string lists
        mutex_list: list[str] = (
            list(mutex_arg) if mutex_arg else []  # type: ignore[call-overload]
        )
        self.mutually_exclusive = set(mutex_list)
        super().__init__(*args, **kwargs)  # type: ignore[arg-type]

    def handle_parse_result(  # type: ignore[override]
        self, ctx: click.Context, opts: dict[str, object], args: list[str]
    ) -> tuple[object, list[str]]:
        """Handle parse result and check for mutually exclusive options.

        Args:
            ctx: Click context object
            opts: Dictionary of parsed options
            args: Remaining command line arguments

        Returns:
            Tuple of (parsed value, remaining args)

        Raises:
            click.UsageError: If mutually exclusive options are both set
        """
        current_opt = self.name in opts and opts[self.name]

        for mutex_opt in self.mutually_exclusive:
            if mutex_opt in opts and opts[mutex_opt]:
                if current_opt:
                    name = self.name or "unknown"
                    raise click.UsageError(
                        f"Options --{name.replace('_', '-')} and "
                        f"--{mutex_opt.replace('_', '-')} are mutually exclusive."
                    )

        return super().handle_parse_result(ctx, opts, args)  # type: ignore[return-value]


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
    type=click.Choice(["pdf", "svg", "kle", "kle-png", "kle-pdf"]),
    default="pdf",
    help="Output format: pdf (default), svg, kle (JSON), kle-png, kle-pdf",
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
@click.option(
    "--mac",
    is_flag=True,
    cls=MutuallyExclusiveOption,
    mutually_exclusive=["windows", "linux"],
    help="Use Mac/Apple modifier symbols (⌘, ⌥, ⌃, ⇧) - this is the default",
)
@click.option(
    "--windows",
    is_flag=True,
    cls=MutuallyExclusiveOption,
    mutually_exclusive=["mac", "linux"],
    help="Use Windows modifier symbols (Win, Ctrl, Alt, Shift)",
)
@click.option(
    "--linux",
    is_flag=True,
    cls=MutuallyExclusiveOption,
    mutually_exclusive=["mac", "windows"],
    help="Use Linux modifier symbols (Super, Ctrl, Alt, Shift)",
)
@click.option(
    "--resolve-trans",
    is_flag=True,
    help="Show inherited keys instead of 'trans' for transparent keys",
)
@click.option(
    "--base-layer",
    type=str,
    default=None,
    help="Base layer name for --resolve-trans (default: first layer)",
)
@click.option(
    "--color",
    is_flag=True,
    help="Apply semantic colors to keys (modifiers, navigation, etc.)",
)
@click.option(
    "--no-legend",
    is_flag=True,
    help="Hide color legend when using --color",
)
@click.option(
    "--no-shifted",
    is_flag=True,
    help="Hide shifted characters on keys (shown by default)",
)
# TODO: Wire up color scheme to KLE generation (currently only sunaku template exists)
@click.option(
    "--kle-color-scheme",
    type=click.Choice(["sunaku", "everforest"]),
    default="sunaku",
    help="Color scheme for KLE output (default: sunaku) [WIP - not yet implemented]",
)
@click.option(
    "--layers-per-page",
    type=click.IntRange(1, 3),
    default=3,
    help="Number of layers per PDF page (1, 2, or 3) [default: 3]",
)
@click.option(
    "--dpi",
    type=int,
    default=300,
    help="Output resolution for PDF rendering [default: 300]",
)
@click.version_option(version=__version__)
def main(
    keymap: Path,
    output: Path | None,
    output_format: str,
    layers: str | None,
    exclude_layers: str | None,
    list_layers: bool,
    config_file: Path | None,
    verbose: bool,
    quiet: bool,
    no_toc: bool,
    continue_on_error: bool,
    mac: bool,
    windows: bool,
    linux: bool,
    resolve_trans: bool,
    base_layer: str | None,
    color: bool,
    no_legend: bool,
    no_shifted: bool,
    kle_color_scheme: str,
    layers_per_page: int,
    dpi: int,
) -> None:
    """
    Generate PDF/SVG visualizations of Glove80 keyboard layers.

    KEYMAP is the path to a ZMK .keymap file.

    Examples:

        # Generate PDF with all layers
        glove80-viz my-keymap.keymap -o layers.pdf

        # Generate SVG files
        glove80-viz my-keymap.keymap -o ./svgs --format svg

        # Generate KLE JSON files (for keyboard-layout-editor.com)
        glove80-viz my-keymap.keymap -o ./kle --format kle

        # Generate Sunaku-style PNG via headless browser
        glove80-viz my-keymap.keymap -o ./pngs --format kle-png

        # Generate specific layers only
        glove80-viz my-keymap.keymap -o layers.pdf --layers QWERTY,Symbol,Cursor

        # Use Windows modifier symbols
        glove80-viz my-keymap.keymap -o layers.pdf --windows

        # Show inherited keys instead of transparent markers
        glove80-viz my-keymap.keymap -o layers.pdf --resolve-trans

        # List available layers
        glove80-viz my-keymap.keymap --list-layers
    """

    # Helper for output
    def log(msg: str, force: bool = False) -> None:
        if (verbose or force) and not quiet:
            click.echo(msg)

    def error(msg: str) -> None:
        click.echo(f"Error: {msg}", err=True)

    # Determine OS style (default to mac)
    os_style = "mac"
    if windows:
        os_style = "windows"
    elif linux:
        os_style = "linux"

    # Load config
    if config_file:
        config = VisualizerConfig.from_file(str(config_file))
    else:
        config = VisualizerConfig()

    config.include_toc = not no_toc
    config.continue_on_error = continue_on_error
    config.os_style = os_style
    config.resolve_trans = resolve_trans
    config.show_colors = color
    config.show_legend = not no_legend
    config.show_shifted = not no_shifted
    config.layers_per_page = layers_per_page
    config.dpi = dpi

    # Parse keymap file
    log(f"Parsing keymap: {keymap}")
    try:
        yaml_content = parse_zmk_keymap(keymap)
    except KeymapParseError as e:
        error(str(e))
        sys.exit(1)

    # Parse include/exclude filters
    include_list = [name.strip() for name in layers.split(",")] if layers else None
    exclude_list = [name.strip() for name in exclude_layers.split(",")] if exclude_layers else None

    # Extract all layers first (for layer name lookup), then filter
    all_layers = extract_layers(yaml_content)
    all_layer_names = {layer.name for layer in all_layers}

    # Apply filtering
    extracted_layers = extract_layers(yaml_content, include=include_list, exclude=exclude_list)

    if not extracted_layers:  # pragma: no cover
        # Parser catches most "no layers" cases first with keymap detection
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
        elif output_format == "svg":
            output = keymap.parent / f"{keymap.stem}_svgs"
        elif output_format == "kle":
            output = keymap.parent / f"{keymap.stem}_kle"
        elif output_format == "kle-png":
            output = keymap.parent / f"{keymap.stem}_kle_pngs"
        elif output_format == "kle-pdf":
            output = keymap.with_name(f"{keymap.stem}_kle.pdf")

    # At this point output should be set (Click validates output_format choices)
    assert output is not None, "Output path should be set"

    log(f"Found {len(extracted_layers)} layers")

    # Find base layer for resolve_trans
    base_layer_obj = None
    if resolve_trans:
        if base_layer:
            # Find the specified base layer
            for layer in extracted_layers:
                if layer.name == base_layer:
                    base_layer_obj = layer
                    break
            if not base_layer_obj:
                error(f"Base layer '{base_layer}' not found")
                sys.exit(1)
        else:
            # Use first layer (index 0) as default
            for layer in extracted_layers:
                if layer.index == 0:
                    base_layer_obj = layer
                    break
            if not base_layer_obj and extracted_layers:  # pragma: no cover
                # Extractor always assigns index 0 to first layer
                base_layer_obj = extracted_layers[0]

    # Extract layer activators for held key indicators
    activators = extract_layer_activators(yaml_content)
    if activators and verbose:
        log(f"Found {len(activators)} layer activators")

    # Parse combos for KLE output
    combos: list[Combo] = []
    try:
        combos = parse_combos(keymap)
        if combos and verbose:
            log(f"Found {len(combos)} combos")
    except KeymapParseError as e:
        # Combos are optional, log warning and continue
        log(f"Warning: Could not parse combos: {e}", force=True)

    # Generate SVGs
    svgs: list[str | None] = []
    failed_layers: list[str] = []

    for layer in extracted_layers:
        log(f"  Generating SVG for layer: {layer.name}")
        try:
            svg = generate_layer_svg(
                layer,
                config,
                os_style=os_style,
                resolve_trans=resolve_trans,
                base_layer=base_layer_obj,
                activators=activators,
            )
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
        valid_pairs = [(lyr, s) for lyr, s in zip(extracted_layers, svgs) if s is not None]
        if not valid_pairs:
            error("All layers failed to render")
            sys.exit(1)
        if failed_layers:
            click.echo(
                f"Warning: Skipped {len(failed_layers)} layer(s): {', '.join(failed_layers)}"
            )
        extracted_layers = [p[0] for p in valid_pairs]
        # After filtering, we know all values are str (not None)
        filtered_svgs: list[str] = [p[1] for p in valid_pairs]
    else:
        # No filtering needed, all svgs should be strings
        filtered_svgs = [s for s in svgs if s is not None]

    # Use all layer names for KLE formatting (distinguishes layer names from modifiers)
    # This ensures layer toggles display correctly even when filtering layers
    layer_names = all_layer_names

    # Output based on format
    if output_format == "svg":
        # Create output directory
        output.mkdir(parents=True, exist_ok=True)
        for layer, svg in zip(extracted_layers, filtered_svgs):
            svg_path = output / f"{layer.name}.svg"
            svg_path.write_text(svg)
            log(f"  Wrote: {svg_path}")
        if not quiet:
            click.echo(f"Generated {len(filtered_svgs)} SVG files in {output}")
    elif output_format == "kle":
        # Generate KLE JSON files using Sunaku's template
        from glove80_visualizer.kle_template import generate_kle_from_template

        output.mkdir(parents=True, exist_ok=True)
        for layer in extracted_layers:
            log(f"  Generating KLE JSON for layer: {layer.name}")
            kle_json = generate_kle_from_template(
                layer,
                title=layer.name,
                combos=combos,
                os_style=os_style,
                activators=activators,
                layer_names=layer_names,
            )
            json_path = output / f"{layer.name}.json"
            json_path.write_text(kle_json)
            log(f"  Wrote: {json_path}")
        if not quiet:
            click.echo(f"Generated {len(extracted_layers)} KLE JSON files in {output}")
    elif output_format == "kle-png":
        # Generate KLE PNG files via headless browser using Sunaku's template
        from glove80_visualizer.kle_renderer import render_kle_to_png
        from glove80_visualizer.kle_template import generate_kle_from_template

        output.mkdir(parents=True, exist_ok=True)
        for layer in extracted_layers:
            log(f"  Rendering KLE PNG for layer: {layer.name}")
            kle_json = generate_kle_from_template(
                layer,
                title=layer.name,
                combos=combos,
                os_style=os_style,
                activators=activators,
                layer_names=layer_names,
            )
            png_path = output / f"{layer.name}.png"
            try:
                render_kle_to_png(kle_json, png_path)
                log(f"  Wrote: {png_path}")
            except Exception as e:
                if continue_on_error:
                    log(f"  Warning: Failed to render {layer.name}: {e}", force=True)
                else:
                    error(f"Failed to render layer {layer.name}: {e}")
                    sys.exit(1)
        if not quiet:
            click.echo(f"Generated KLE PNG files in {output}")
    elif output_format == "kle-pdf":
        # Generate combined PDF via KLE headless browser
        from glove80_visualizer.kle_renderer import create_combined_pdf_kle

        log("Generating KLE PDF via headless browser...")
        try:
            create_combined_pdf_kle(
                extracted_layers,
                output,
                combos=combos,
                os_style=os_style,
                activators=activators,
                layer_names=layer_names,
            )
            if not quiet:
                click.echo(f"Generated KLE PDF: {output}")
        except Exception as e:
            error(f"Failed to generate KLE PDF: {e}")
            sys.exit(1)
    else:
        # Generate PDF (default)
        log("Generating PDF...")
        pdf_bytes = generate_pdf_with_toc(
            layers=extracted_layers,
            svgs=filtered_svgs,
            config=config,
            include_toc=config.include_toc,
        )

        # Write output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(pdf_bytes)
        if not quiet:
            click.echo(f"Generated PDF: {output}")


if __name__ == "__main__":  # pragma: no cover
    main()
