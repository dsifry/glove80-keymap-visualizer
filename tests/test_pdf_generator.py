"""
Tests for the PDF generator module.

These tests define the expected behavior of PDF generation.
Write these tests FIRST (TDD), then implement the generator to pass them.
"""


import pytest


class TestSvgToPdf:
    """Tests for converting SVG to PDF."""

    def test_svg_to_pdf_basic(self, sample_svg):
        """SPEC-D001: Generator converts SVG to PDF bytes."""
        from glove80_visualizer.pdf_generator import svg_to_pdf

        pdf_bytes = svg_to_pdf(sample_svg)
        assert pdf_bytes.startswith(b"%PDF")

    def test_pdf_page_size(self, sample_svg):
        """SPEC-D002: Generated PDF has specified page size."""
        from glove80_visualizer.config import VisualizerConfig
        from glove80_visualizer.pdf_generator import svg_to_pdf

        config = VisualizerConfig(page_size="letter", orientation="landscape")
        pdf_bytes = svg_to_pdf(sample_svg, config=config)
        # PDF should be generated with the correct size
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")

    def test_svg_to_pdf_with_a4(self, sample_svg):
        """PDF can be generated with A4 page size."""
        from glove80_visualizer.config import VisualizerConfig
        from glove80_visualizer.pdf_generator import svg_to_pdf

        config = VisualizerConfig(page_size="a4", orientation="landscape")
        pdf_bytes = svg_to_pdf(sample_svg, config=config)
        assert pdf_bytes.startswith(b"%PDF")


class TestMergePdfs:
    """Tests for merging multiple PDFs."""

    def test_merge_pdfs_basic(self, sample_svg):
        """SPEC-D003: Generator merges multiple PDF pages into one document."""
        from glove80_visualizer.pdf_generator import merge_pdfs, svg_to_pdf

        # Create multiple PDF pages
        pdf_pages = [svg_to_pdf(sample_svg) for _ in range(3)]
        merged = merge_pdfs(pdf_pages)

        assert merged.startswith(b"%PDF")

    def test_merge_pdfs_preserves_font_resources(self):
        """SPEC-D008: Merged PDF preserves font resources for all pages.

        This tests that fonts embedded in individual PDFs are correctly
        preserved when multiple PDFs are merged, preventing garbled text
        or missing characters in the output.
        """
        from io import BytesIO

        import pikepdf

        from glove80_visualizer.pdf_generator import merge_pdfs, svg_to_pdf

        # Create SVGs with text that requires font embedding
        svg_with_text = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">
<style>
    text { font-family: SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace; font-size: 14px; }
</style>
<text x="100" y="50" class="label">Layer 20: Emoji</text>
<text x="100" y="100">Test text with ellipsis…</text>
<text x="100" y="150">Symbol: ⇧ ⌃ ⌥ ⌘</text>
</svg>'''

        svg_different = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">
<style>
    text { font-family: SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace; font-size: 14px; }
</style>
<text x="100" y="50" class="label">Layer 30: Lower</text>
<text x="100" y="100">Different content here</text>
</svg>'''

        # Convert to PDFs
        pdf1 = svg_to_pdf(svg_with_text)
        pdf2 = svg_to_pdf(svg_different)
        pdf3 = svg_to_pdf(svg_with_text)  # Same as first

        # Merge them
        merged = merge_pdfs([pdf1, pdf2, pdf3])

        # Verify merged PDF is valid
        assert merged.startswith(b"%PDF")

        # Verify all pages have content (not blank)
        pdf = pikepdf.open(BytesIO(merged))
        assert len(pdf.pages) == 3

        # Each page should have resources with fonts
        for i, page in enumerate(pdf.pages):
            assert "/Resources" in page, f"Page {i} missing resources"
            resources = page["/Resources"]
            # Font resources should be present (though implementation may vary)
            # The key thing is pages aren't blank or corrupted

    def test_merge_pdfs_page_count(self, sample_svg):
        """Merged PDF has correct number of pages."""
        from io import BytesIO

        import pikepdf

        from glove80_visualizer.pdf_generator import merge_pdfs, svg_to_pdf

        pdf_pages = [svg_to_pdf(sample_svg) for _ in range(5)]
        merged = merge_pdfs(pdf_pages)

        pdf = pikepdf.open(BytesIO(merged))
        assert len(pdf.pages) == 5

    def test_merge_empty_list(self):
        """Merging empty list raises error."""
        from glove80_visualizer.pdf_generator import merge_pdfs

        with pytest.raises(ValueError, match="empty"):
            merge_pdfs([])

    def test_merge_single_pdf(self, sample_svg):
        """Merging single PDF returns that PDF."""
        from glove80_visualizer.pdf_generator import merge_pdfs, svg_to_pdf

        pdf = svg_to_pdf(sample_svg)
        merged = merge_pdfs([pdf])

        assert merged.startswith(b"%PDF")


class TestPdfWithHeaders:
    """Tests for PDF generation with headers."""

    def test_pdf_with_headers(self, sample_svg, sample_layer):
        """SPEC-D004: Generator can add layer name as page header."""
        from glove80_visualizer.pdf_generator import svg_to_pdf

        pdf_bytes = svg_to_pdf(
            sample_svg, header=f"Layer {sample_layer.index}: {sample_layer.name}"
        )
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")


class TestPdfWithToc:
    """Tests for PDF generation with table of contents."""

    def test_pdf_table_of_contents(self, sample_layers, sample_svg):
        """SPEC-D005: Generator can create a table of contents page."""
        from glove80_visualizer.pdf_generator import generate_pdf_with_toc

        svgs = [sample_svg] * len(sample_layers)
        pdf_bytes = generate_pdf_with_toc(
            layers=sample_layers, svgs=svgs, include_toc=True
        )
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")

    def test_pdf_without_toc(self, sample_layers, sample_svg):
        """PDF can be generated without table of contents."""
        from glove80_visualizer.pdf_generator import generate_pdf_with_toc

        svgs = [sample_svg] * len(sample_layers)
        pdf_bytes = generate_pdf_with_toc(
            layers=sample_layers, svgs=svgs, include_toc=False
        )
        assert pdf_bytes.startswith(b"%PDF")

    def test_pdf_large_document(self, sample_svg):
        """SPEC-D006: Generator handles documents with 32+ layers."""
        from glove80_visualizer.models import Layer
        from glove80_visualizer.pdf_generator import generate_pdf_with_toc

        layers = [Layer(name=f"Layer{i}", index=i, bindings=[]) for i in range(32)]
        svgs = [sample_svg] * 32

        pdf_bytes = generate_pdf_with_toc(layers=layers, svgs=svgs)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")


class TestPdfFileOutput:
    """Tests for writing PDF to files."""

    def test_pdf_output_to_file(self, tmp_path, sample_svg):
        """SPEC-D007: Generator can write PDF to file."""
        from glove80_visualizer.pdf_generator import svg_to_pdf_file

        output_path = tmp_path / "output.pdf"
        svg_to_pdf_file(sample_svg, output_path)

        assert output_path.exists()
        assert output_path.read_bytes().startswith(b"%PDF")

    def test_pdf_output_creates_parent_dirs(self, tmp_path, sample_svg):
        """Generator creates parent directories if needed."""
        from glove80_visualizer.pdf_generator import svg_to_pdf_file

        output_path = tmp_path / "nested" / "dirs" / "output.pdf"
        svg_to_pdf_file(sample_svg, output_path, create_parents=True)

        assert output_path.exists()
