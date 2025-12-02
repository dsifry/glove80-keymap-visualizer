"""
PDF generation module.

This module converts SVG diagrams to PDF and combines them into a single document.
"""

from pathlib import Path
from typing import List, Optional
from io import BytesIO

import cairosvg
from PyPDF2 import PdfReader, PdfWriter

from glove80_visualizer.models import Layer
from glove80_visualizer.config import VisualizerConfig


def svg_to_pdf(
    svg_content: str,
    config: Optional[VisualizerConfig] = None,
    header: Optional[str] = None,
) -> bytes:
    """
    Convert an SVG string to PDF bytes.

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

    # Convert SVG to PDF using CairoSVG
    pdf_bytes = cairosvg.svg2pdf(bytestring=svg_content.encode("utf-8"))

    return pdf_bytes


def svg_to_pdf_file(
    svg_content: str,
    output_path: Path,
    config: Optional[VisualizerConfig] = None,
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


def merge_pdfs(pdf_pages: List[bytes]) -> bytes:
    """
    Merge multiple PDF pages into a single document.

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

    writer = PdfWriter()

    for pdf_bytes in pdf_pages:
        reader = PdfReader(BytesIO(pdf_bytes))
        for page in reader.pages:
            writer.add_page(page)

    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def generate_pdf_with_toc(
    layers: List[Layer],
    svgs: List[str],
    config: Optional[VisualizerConfig] = None,
    include_toc: bool = True,
) -> bytes:
    """
    Generate a complete PDF with optional table of contents.

    Args:
        layers: List of Layer objects (for names/metadata)
        svgs: List of SVG content strings (one per layer)
        config: Optional configuration
        include_toc: Whether to include a table of contents page

    Returns:
        Complete PDF content as bytes
    """
    if config is None:
        config = VisualizerConfig()

    pdf_pages = []

    # Generate TOC page if requested
    if include_toc and layers:
        toc_pdf = _generate_toc_page(layers, config)
        pdf_pages.append(toc_pdf)

    # Convert each SVG to PDF
    # Replace keymap-drawer's default label with our formatted header
    for i, (layer, svg) in enumerate(zip(layers, svgs)):
        header = config.layer_title_format.format(index=layer.index, name=layer.name)
        svg_with_header = _replace_layer_label(svg, header)
        pdf_bytes = svg_to_pdf(svg_with_header, config)
        pdf_pages.append(pdf_bytes)

    # Merge all pages
    if not pdf_pages:
        # Return empty PDF if no pages
        return _create_empty_pdf()

    return merge_pdfs(pdf_pages)


def _replace_layer_label(svg_content: str, new_label: str) -> str:
    """
    Replace keymap-drawer's layer label with our own formatted label.

    keymap-drawer generates labels like: <text x="0" y="28" class="label" id="Base">Base:</text>
    We replace the content to use our format (e.g., "Layer 0: Base")
    """
    import re

    # Pattern to match keymap-drawer's label: <text ... class="label" ...>LayerName:</text>
    pattern = r'(<text[^>]*class="label"[^>]*>)[^<]*(</text>)'

    replacement = rf'\g<1>{new_label}\g<2>'

    new_svg = re.sub(pattern, replacement, svg_content, count=1)

    return new_svg


def _add_header_to_svg(svg_content: str, header: str) -> str:
    """
    Add a header text element to an SVG.

    The header is inserted inside the SVG element, after the opening tag.
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
    if style_end != -1 and style_end > svg_tag_end:
        insert_pos = style_end + len("</style>")

    svg_content = (
        svg_content[:insert_pos] + "\n" + header_element + svg_content[insert_pos:]
    )

    return svg_content


def _generate_toc_page(layers: List[Layer], config: VisualizerConfig) -> bytes:
    """
    Generate a table of contents page.

    Args:
        layers: List of layers to include in TOC
        config: Configuration for styling

    Returns:
        PDF content for the TOC page
    """
    # Create a simple SVG TOC page
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append(
        '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">'
    )
    lines.append("<style>")
    lines.append("  text { font-family: sans-serif; fill: #24292e; }")
    lines.append("  .title { font-size: 24px; font-weight: bold; }")
    lines.append("  .entry { font-size: 14px; }")
    lines.append("</style>")

    # Title
    lines.append('<text x="40" y="50" class="title">Table of Contents</text>')

    # Layer entries
    y = 100
    for i, layer in enumerate(layers):
        page_num = i + 2 if config.include_toc else i + 1  # +2 because TOC is page 1
        entry_text = f"{layer.index}: {layer.name}"
        lines.append(f'<text x="60" y="{y}" class="entry">{entry_text}</text>')
        lines.append(
            f'<text x="700" y="{y}" class="entry" text-anchor="end">{page_num}</text>'
        )
        y += 25

        # Start new column if needed
        if y > 550:
            y = 100
            # Note: For simplicity, we don't handle multi-page TOC here

    lines.append("</svg>")

    svg_content = "\n".join(lines)
    return svg_to_pdf(svg_content, config)


def _create_empty_pdf() -> bytes:
    """Create a minimal empty PDF."""
    writer = PdfWriter()
    # Add a blank page
    writer.add_blank_page(width=612, height=792)  # Letter size
    output = BytesIO()
    writer.write(output)
    return output.getvalue()
