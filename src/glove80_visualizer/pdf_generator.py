"""
PDF generation module.

This module converts SVG diagrams to PDF and combines them into a single document.
"""

import shutil
import subprocess
import tempfile
from io import BytesIO
from pathlib import Path

import pikepdf

from glove80_visualizer.config import VisualizerConfig
from glove80_visualizer.models import Layer


def svg_to_pdf(
    svg_content: str,
    config: VisualizerConfig | None = None,
    header: str | None = None,
) -> bytes:
    """
    Convert an SVG string to PDF bytes.

    Uses rsvg-convert (from librsvg) if available, falls back to CairoSVG.
    rsvg-convert produces better results for complex SVGs with text styling.

    Args:
        svg_content: The SVG content as a string
        config: Optional configuration for page size/orientation
        header: Optional header text to add to the page

    Returns:
        PDF content as bytes
    """
    if config is None:
        config = VisualizerConfig()

    # If header is requested, add it to the SVG before conversion
    if header:
        svg_content = _add_header_to_svg(svg_content, header)

    # Try rsvg-convert first (better rendering for complex SVGs)
    dpi = config.dpi
    if shutil.which("rsvg-convert"):
        return _svg_to_pdf_rsvg(svg_content, dpi)
    else:
        # Fall back to CairoSVG
        return _svg_to_pdf_cairosvg(svg_content, dpi)


def _svg_to_pdf_rsvg(svg_content: str, dpi: int = 300) -> bytes:
    """Convert SVG to PDF using rsvg-convert.

    Args:
        svg_content: The SVG content as a string
        dpi: Output resolution in dots per inch

    Returns:
        PDF content as bytes
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".svg", delete=False) as svg_file:
        svg_file.write(svg_content)
        svg_path = svg_file.name

    pdf_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as pdf_file:
            pdf_path = pdf_file.name

        result = subprocess.run(
            ["rsvg-convert", "-f", "pdf", "-d", str(dpi), "-p", str(dpi), "-o", pdf_path, svg_path],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:  # pragma: no cover
            raise RuntimeError(f"rsvg-convert failed: {result.stderr}")

        with open(pdf_path, "rb") as f:
            return f.read()
    finally:
        # Clean up temp files - OSError handling is defensive
        import os

        try:
            os.unlink(svg_path)
        except OSError:  # pragma: no cover
            pass
        if pdf_path is not None:
            try:
                os.unlink(pdf_path)
            except OSError:  # pragma: no cover
                pass


def _svg_to_pdf_cairosvg(svg_content: str, dpi: int = 300) -> bytes:
    """Convert SVG to PDF using CairoSVG (fallback).

    Args:
        svg_content: The SVG content as a string
        dpi: Output resolution in dots per inch

    Returns:
        PDF content as bytes
    """
    try:
        import cairosvg  # type: ignore[import-untyped]
    except ImportError as e:  # pragma: no cover
        raise RuntimeError(
            "CairoSVG is required to convert SVG to PDF but is not installed. "
            "Install it with 'pip install cairosvg' or ensure it is available "
            "in your environment."
        ) from e

    try:
        result: bytes = cairosvg.svg2pdf(bytestring=svg_content.encode("utf-8"), dpi=dpi)
        return result
    except Exception as e:
        raise RuntimeError(
            "Failed to convert SVG to PDF using CairoSVG. "
            "Verify that the SVG content is valid and that CairoSVG is functioning "
            "correctly."
        ) from e


def svg_to_pdf_file(
    svg_content: str,
    output_path: Path,
    config: VisualizerConfig | None = None,
    create_parents: bool = False,
) -> None:
    """
    Convert an SVG string to a PDF file.

    Args:
        svg_content: The SVG content as a string
        output_path: Path where the PDF should be written
        config: Optional configuration for page size/orientation
        create_parents: Whether to create parent directories if needed
    """
    if create_parents:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    pdf_bytes = svg_to_pdf(svg_content, config)

    with open(output_path, "wb") as f:
        f.write(pdf_bytes)


def merge_pdfs(pdf_pages: list[bytes]) -> bytes:
    """
    Merge multiple PDF pages into a single document.

    Uses pikepdf for merging to properly handle font resources and prevent
    font corruption or missing glyphs in the merged output.

    Args:
        pdf_pages: List of PDF content as bytes

    Returns:
        Combined PDF content as bytes

    Raises:
        ValueError: If the input list is empty
    """
    if not pdf_pages:
        raise ValueError("Cannot merge empty list of PDFs")

    if len(pdf_pages) == 1:
        return pdf_pages[0]

    # Use pikepdf for merging - it handles font resources correctly
    merged = pikepdf.new()

    for pdf_bytes in pdf_pages:
        src = pikepdf.open(BytesIO(pdf_bytes))
        merged.pages.extend(src.pages)

    output = BytesIO()
    merged.save(output)
    return output.getvalue()


def generate_pdf_with_toc(
    layers: list[Layer],
    svgs: list[str],
    config: VisualizerConfig | None = None,
    include_toc: bool = True,
) -> bytes:
    """
    Generate a complete PDF with optional table of contents.

    Supports multiple layers per page via config.layers_per_page (1, 2, or 3).
    Layers are stacked vertically and scaled to fit the page.

    Args:
        layers: List of Layer objects (for names/metadata)
        svgs: List of SVG content strings (one per layer)
        config: Optional configuration
        include_toc: Whether to include a table of contents page(s)

    Returns:
        Complete PDF content as bytes
    """
    if config is None:
        config = VisualizerConfig()

    if config.layers_per_page < 1:
        raise ValueError("layers_per_page must be >= 1")

    layers_per_page = config.layers_per_page
    pdf_pages = []

    # Generate TOC pages if requested (may be multiple for many layers)
    if include_toc and layers:
        toc_pdfs = _generate_toc_pages(layers, config)
        pdf_pages.extend(toc_pdfs)

    # Prepare SVGs with headers and convert each to PDF
    layer_pdfs = []
    for layer, svg in zip(layers, svgs):
        header = config.layer_title_format.format(index=layer.index, name=layer.name)
        svg_with_header = _replace_layer_label(svg, header)
        pdf_bytes = svg_to_pdf(svg_with_header, config)
        layer_pdfs.append(pdf_bytes)

    # Group PDFs by layers_per_page and combine onto single pages
    for i in range(0, len(layer_pdfs), layers_per_page):
        chunk = layer_pdfs[i : i + layers_per_page]
        if layers_per_page == 1:
            # 1 layer per page - use original PDF at full scale
            pdf_pages.append(chunk[0])
        else:
            # Multiple layers per page layout - always use combine for consistent scaling
            # This ensures the last page (with fewer layers) maintains the same scale
            combined_pdf = _combine_pdfs_on_page(chunk, config)
            pdf_pages.append(combined_pdf)

    # Merge all pages
    if not pdf_pages:
        # Return empty PDF if no pages
        return _create_empty_pdf()

    return merge_pdfs(pdf_pages)


def _combine_pdfs_on_page(
    pdf_bytes_list: list[bytes],
    config: VisualizerConfig,
) -> bytes:
    """
    Combine multiple PDFs onto a single page, stacked vertically.

    Converts each SVG to PDF first (preserving fonts), then scales and
    positions the PDF content onto a single page using pikepdf.

    Args:
        pdf_bytes_list: List of PDF content as bytes (1-3 PDFs)
        config: Configuration with page dimensions and layers_per_page

    Returns:
        Combined PDF content as bytes
    """
    if not pdf_bytes_list:
        raise ValueError("Cannot combine empty list of PDFs")

    # Derive page dimensions from first source PDF instead of hard-coding
    # This ensures combined pages match the source page size/orientation
    first_pdf = pikepdf.open(BytesIO(pdf_bytes_list[0]))
    if len(first_pdf.pages) == 0:
        # Fallback to Letter portrait if first PDF is empty
        page_width = 612.0
        page_height = 792.0
    else:
        first_box = first_pdf.pages[0].mediabox
        page_width = float(first_box[2]) - float(first_box[0])
        page_height = float(first_box[3]) - float(first_box[1])

    # Use configured layers_per_page for consistent scaling across all pages
    # This ensures the last page with fewer layers maintains the same scale
    target_layers = config.layers_per_page
    slot_height = page_height / target_layers

    # Create output PDF and build the combined page manually
    output_pdf = pikepdf.new()

    # Create page dictionary with proper structure
    xobject_dict = pikepdf.Dictionary()
    content_streams = []

    for i, pdf_bytes in enumerate(pdf_bytes_list):
        src_pdf = pikepdf.open(BytesIO(pdf_bytes))
        if len(src_pdf.pages) == 0:
            continue

        src_page = src_pdf.pages[0]

        # Get source page dimensions
        src_box = src_page.mediabox
        src_width = float(src_box[2]) - float(src_box[0])
        src_height = float(src_box[3]) - float(src_box[1])

        # Calculate scale to fit in slot
        scale_x = page_width / src_width
        scale_y = slot_height / src_height
        scale = min(scale_x, scale_y)

        # Calculate positioning (center horizontally, stack from top)
        scaled_width = src_width * scale
        x_offset = (page_width - scaled_width) / 2
        # PDF coordinates are from bottom, so we need to flip
        y_offset = page_height - (i + 1) * slot_height

        # Create Form XObject from source page
        xobj_name = f"Layer{i}"
        form_xobj = src_page.as_form_xobject()
        # Copy to output PDF and add to XObject dictionary
        xobject_dict[pikepdf.Name(f"/{xobj_name}")] = output_pdf.copy_foreign(form_xobj)

        # Build content stream to place this XObject
        # q = save state, cm = transformation matrix, Do = draw XObject, Q = restore
        xf = f"{x_offset:.2f}"
        yf = f"{y_offset:.2f}"
        content = f"q {scale:.6f} 0 0 {scale:.6f} {xf} {yf} cm /{xobj_name} Do Q\n"
        content_streams.append(content)

    # Create the combined content stream
    content_stream = output_pdf.make_stream("".join(content_streams).encode())

    # Create page with all components
    page_dict = pikepdf.Dictionary(
        Type=pikepdf.Name.Page,
        MediaBox=pikepdf.Array([0, 0, page_width, page_height]),
        Resources=pikepdf.Dictionary(XObject=xobject_dict),
        Contents=content_stream,
    )

    # Wrap in Page object and add to document
    page = pikepdf.Page(page_dict)
    output_pdf.pages.append(page)

    output = BytesIO()
    output_pdf.save(output)
    return output.getvalue()


def _replace_layer_label(svg_content: str, new_label: str) -> str:
    """
    Replace keymap-drawer's layer label with our own formatted label.

    keymap-drawer generates labels like: <text x="0" y="28" class="label" id="Base">Base:</text>
    We replace the content to use our format (e.g., "Layer 0: Base")

    Args:
        svg_content: The SVG content as a string
        new_label: The new label to use for the layer

    Returns:
        Modified SVG content with the new label
    """
    import re

    # Pattern to match keymap-drawer's label: <text ... class="label" ...>LayerName:</text>
    pattern = r'(<text[^>]*class="label"[^>]*>)[^<]*(</text>)'

    replacement = rf"\g<1>{new_label}\g<2>"

    return re.sub(pattern, replacement, svg_content, count=1)


def _add_header_to_svg(svg_content: str, header: str) -> str:
    """
    Add a header text element to an SVG.

    The header is inserted inside the SVG element, after the opening tag.

    Args:
        svg_content: The SVG content as a string
        header: The header text to add

    Returns:
        Modified SVG content with header added
    """
    header_element = f'<text x="30" y="30" font-size="18" font-weight="bold">{header}</text>\n'

    # Find the opening svg tag and insert after it
    # Look for the end of <svg ...> tag
    svg_start = svg_content.find("<svg")
    if svg_start == -1:
        return svg_content

    # Find the closing > of the svg tag
    svg_tag_end = svg_content.find(">", svg_start)
    if svg_tag_end == -1:
        return svg_content

    insert_pos = svg_tag_end + 1

    # If there's a style block, insert after it instead
    style_end = svg_content.find("</style>")
    if style_end != -1 and style_end > svg_tag_end:  # pragma: no cover
        # All keymap-drawer SVGs have style blocks
        insert_pos = style_end + len("</style>")

    svg_content = svg_content[:insert_pos] + "\n" + header_element + svg_content[insert_pos:]

    return svg_content


def _generate_toc_pages(layers: list[Layer], config: VisualizerConfig) -> list[bytes]:
    """
    Generate table of contents pages (may be multiple if many layers).

    Args:
        layers: List of layers to include in TOC
        config: Configuration for styling

    Returns:
        List of PDF content bytes for each TOC page
    """
    # Layout constants
    page_width = 800
    page_height = 600
    title_y = 50
    first_entry_y = 100
    entry_height = 25
    max_y = 550  # Leave room at bottom
    entries_per_page = (max_y - first_entry_y) // entry_height

    # Calculate how many TOC pages we need
    num_toc_pages = max(1, (len(layers) + entries_per_page - 1) // entries_per_page)

    toc_pdfs = []

    for toc_page_num in range(num_toc_pages):
        start_idx = toc_page_num * entries_per_page
        end_idx = min(start_idx + entries_per_page, len(layers))
        page_layers = layers[start_idx:end_idx]

        lines = []
        lines.append('<?xml version="1.0" encoding="UTF-8"?>')
        svg_attrs = (
            f'xmlns="http://www.w3.org/2000/svg" width="{page_width}" '
            f'height="{page_height}" viewBox="0 0 {page_width} {page_height}"'
        )
        lines.append(f"<svg {svg_attrs}>")
        lines.append("<style>")
        lines.append("  text { font-family: sans-serif; fill: #24292e; }")
        lines.append("  .title { font-size: 24px; font-weight: bold; }")
        lines.append("  .entry { font-size: 14px; }")
        lines.append("</style>")

        # Title (with page indicator if multi-page)
        if num_toc_pages > 1:
            title = f"Table of Contents ({toc_page_num + 1}/{num_toc_pages})"
        else:
            title = "Table of Contents"
        lines.append(f'<text x="40" y="{title_y}" class="title">{title}</text>')

        # Layer entries for this page
        layers_per_page = config.layers_per_page
        y = first_entry_y
        for i, layer in enumerate(page_layers):
            # Calculate page number: TOC pages + content page (with layers_per_page)
            actual_layer_idx = start_idx + i
            content_page = actual_layer_idx // layers_per_page
            page_num = num_toc_pages + content_page + 1
            entry_text = f"{layer.index}: {layer.name}"
            lines.append(f'<text x="60" y="{y}" class="entry">{entry_text}</text>')
            lines.append(f'<text x="700" y="{y}" class="entry" text-anchor="end">{page_num}</text>')
            y += entry_height

        lines.append("</svg>")

        svg_content = "\n".join(lines)
        toc_pdfs.append(svg_to_pdf(svg_content, config))

    return toc_pdfs


def _create_empty_pdf() -> bytes:
    """Create a minimal empty PDF with a blank page.

    Returns:
        PDF content as bytes containing a single blank page
    """
    # Create a minimal SVG to convert to PDF
    empty_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="612" height="792" viewBox="0 0 612 792">
</svg>"""
    return svg_to_pdf(empty_svg)
