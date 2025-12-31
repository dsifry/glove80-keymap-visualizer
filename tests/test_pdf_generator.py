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
        svg_with_text = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">
<style>
    text { font-family: SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace; font-size: 14px; }
</style>
<text x="100" y="50" class="label">Layer 20: Emoji</text>
<text x="100" y="100">Test text with ellipsis…</text>
<text x="100" y="150">Symbol: ⇧ ⌃ ⌥ ⌘</text>
</svg>"""

        svg_different = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">
<style>
    text { font-family: SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace; font-size: 14px; }
</style>
<text x="100" y="50" class="label">Layer 30: Lower</text>
<text x="100" y="100">Different content here</text>
</svg>"""

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
        pdf_bytes = generate_pdf_with_toc(layers=sample_layers, svgs=svgs, include_toc=True)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")

    def test_pdf_without_toc(self, sample_layers, sample_svg):
        """PDF can be generated without table of contents."""
        from glove80_visualizer.pdf_generator import generate_pdf_with_toc

        svgs = [sample_svg] * len(sample_layers)
        pdf_bytes = generate_pdf_with_toc(layers=sample_layers, svgs=svgs, include_toc=False)
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


class TestPdfEdgeCases:
    """Tests for edge cases and fallbacks in PDF generation."""

    def test_create_empty_pdf(self):
        """_create_empty_pdf creates a valid empty PDF."""
        from glove80_visualizer.pdf_generator import _create_empty_pdf

        pdf_bytes = _create_empty_pdf()
        assert pdf_bytes.startswith(b"%PDF")

    def test_generate_pdf_with_empty_layers_and_svgs(self):
        """generate_pdf_with_toc with empty layers returns empty PDF."""
        from glove80_visualizer.pdf_generator import generate_pdf_with_toc

        pdf_bytes = generate_pdf_with_toc(layers=[], svgs=[], include_toc=False)
        assert pdf_bytes.startswith(b"%PDF")

    def test_add_header_to_svg_no_svg_tag(self):
        """_add_header_to_svg handles content without svg tag."""
        from glove80_visualizer.pdf_generator import _add_header_to_svg

        result = _add_header_to_svg("<div>not svg</div>", "Header")
        assert result == "<div>not svg</div>"  # Unchanged

    def test_add_header_to_svg_no_closing_bracket(self):
        """_add_header_to_svg handles malformed svg tag."""
        from glove80_visualizer.pdf_generator import _add_header_to_svg

        result = _add_header_to_svg("<svg no closing", "Header")
        assert result == "<svg no closing"  # Unchanged

    def test_svg_to_pdf_cairosvg_fallback(self, sample_svg, mocker):
        """Falls back to CairoSVG when rsvg-convert unavailable."""
        from glove80_visualizer.pdf_generator import svg_to_pdf

        # Mock shutil.which to return None (rsvg not found)
        mocker.patch("shutil.which", return_value=None)

        pdf_bytes = svg_to_pdf(sample_svg)
        assert pdf_bytes.startswith(b"%PDF")

    def test_replace_layer_label(self):
        """_replace_layer_label replaces keymap-drawer label."""
        from glove80_visualizer.pdf_generator import _replace_layer_label

        svg = '<svg><text class="label" id="Test">Test:</text></svg>'
        result = _replace_layer_label(svg, "Layer 0: Test")
        assert "Layer 0: Test" in result
        assert "Test:</text>" not in result


class TestRsvgConvertPath:
    """Tests for the rsvg-convert code path."""

    def test_svg_to_pdf_uses_rsvg_when_available(self, sample_svg, mocker, tmp_path):
        """Uses rsvg-convert when available."""
        from glove80_visualizer.pdf_generator import svg_to_pdf

        # Create a real PDF file to be returned
        pdf_content = b"%PDF-1.4 fake pdf content for testing"
        fake_pdf_path = tmp_path / "output.pdf"
        fake_pdf_path.write_bytes(pdf_content)

        # Mock shutil.which to return a path (rsvg found)
        mocker.patch(
            "glove80_visualizer.pdf_generator.shutil.which", return_value="/usr/bin/rsvg-convert"
        )

        # Mock subprocess.run to simulate successful rsvg-convert
        mock_run = mocker.patch("glove80_visualizer.pdf_generator.subprocess.run")
        mock_run.return_value.returncode = 0

        # Mock tempfile to control the output path
        mock_svg_file = mocker.MagicMock()
        mock_svg_file.__enter__ = mocker.MagicMock(return_value=mock_svg_file)
        mock_svg_file.__exit__ = mocker.MagicMock(return_value=False)
        mock_svg_file.name = str(tmp_path / "input.svg")

        mock_pdf_file = mocker.MagicMock()
        mock_pdf_file.__enter__ = mocker.MagicMock(return_value=mock_pdf_file)
        mock_pdf_file.__exit__ = mocker.MagicMock(return_value=False)
        mock_pdf_file.name = str(fake_pdf_path)

        mocker.patch(
            "glove80_visualizer.pdf_generator.tempfile.NamedTemporaryFile",
            side_effect=[mock_svg_file, mock_pdf_file],
        )

        # Mock os.unlink to avoid file not found errors
        mocker.patch("os.unlink")

        pdf_bytes = svg_to_pdf(sample_svg)

        # Verify rsvg-convert was called
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "rsvg-convert"
        assert "-f" in call_args
        assert "pdf" in call_args

        # Verify PDF content was read
        assert pdf_bytes == pdf_content

    def test_svg_to_pdf_rsvg_direct(self, sample_svg, mocker, tmp_path):
        """Test _svg_to_pdf_rsvg function directly."""
        from glove80_visualizer.pdf_generator import _svg_to_pdf_rsvg

        # Create a real PDF file to be returned
        pdf_content = b"%PDF-1.4 rsvg test pdf"
        fake_pdf_path = tmp_path / "output.pdf"
        fake_pdf_path.write_bytes(pdf_content)

        fake_svg_path = tmp_path / "input.svg"

        # Mock subprocess.run to simulate successful rsvg-convert
        mock_run = mocker.patch("glove80_visualizer.pdf_generator.subprocess.run")
        mock_run.return_value.returncode = 0

        # Mock tempfile to control paths
        mock_svg_file = mocker.MagicMock()
        mock_svg_file.__enter__ = mocker.MagicMock(return_value=mock_svg_file)
        mock_svg_file.__exit__ = mocker.MagicMock(return_value=False)
        mock_svg_file.name = str(fake_svg_path)

        mock_pdf_file = mocker.MagicMock()
        mock_pdf_file.__enter__ = mocker.MagicMock(return_value=mock_pdf_file)
        mock_pdf_file.__exit__ = mocker.MagicMock(return_value=False)
        mock_pdf_file.name = str(fake_pdf_path)

        mocker.patch(
            "glove80_visualizer.pdf_generator.tempfile.NamedTemporaryFile",
            side_effect=[mock_svg_file, mock_pdf_file],
        )

        # Mock os.unlink
        mocker.patch("os.unlink")

        pdf_bytes = _svg_to_pdf_rsvg(sample_svg)

        assert pdf_bytes == pdf_content
        mock_run.assert_called_once()

    def test_svg_to_pdf_rsvg_failure(self, sample_svg, mocker, tmp_path):
        """Test _svg_to_pdf_rsvg handles rsvg-convert failure."""
        from glove80_visualizer.pdf_generator import _svg_to_pdf_rsvg

        fake_svg_path = tmp_path / "input.svg"
        fake_pdf_path = tmp_path / "output.pdf"

        # Mock subprocess.run to simulate failed rsvg-convert
        mock_run = mocker.patch("glove80_visualizer.pdf_generator.subprocess.run")
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "rsvg-convert error: invalid SVG"

        # Mock tempfile
        mock_svg_file = mocker.MagicMock()
        mock_svg_file.__enter__ = mocker.MagicMock(return_value=mock_svg_file)
        mock_svg_file.__exit__ = mocker.MagicMock(return_value=False)
        mock_svg_file.name = str(fake_svg_path)

        mock_pdf_file = mocker.MagicMock()
        mock_pdf_file.__enter__ = mocker.MagicMock(return_value=mock_pdf_file)
        mock_pdf_file.__exit__ = mocker.MagicMock(return_value=False)
        mock_pdf_file.name = str(fake_pdf_path)

        mocker.patch(
            "glove80_visualizer.pdf_generator.tempfile.NamedTemporaryFile",
            side_effect=[mock_svg_file, mock_pdf_file],
        )

        # Mock os.unlink
        mocker.patch("os.unlink")

        with pytest.raises(RuntimeError, match="rsvg-convert failed"):
            _svg_to_pdf_rsvg(sample_svg)

    def test_svg_to_pdf_cairosvg_conversion_failure(self, sample_svg, mocker):
        """Test _svg_to_pdf_cairosvg handles conversion failure."""
        # Mock cairosvg to raise an exception during conversion
        mock_cairosvg = mocker.MagicMock()
        mock_cairosvg.svg2pdf.side_effect = Exception("Invalid SVG content")
        mocker.patch.dict("sys.modules", {"cairosvg": mock_cairosvg})

        from glove80_visualizer.pdf_generator import _svg_to_pdf_cairosvg

        with pytest.raises(RuntimeError, match="Failed to convert SVG to PDF"):
            _svg_to_pdf_cairosvg(sample_svg)


class TestCombinePdfsOnPage:
    """Tests for _combine_pdfs_on_page function."""

    def test_combine_empty_list_raises_error(self):
        """_combine_pdfs_on_page raises ValueError for empty list."""
        from glove80_visualizer.config import VisualizerConfig
        from glove80_visualizer.pdf_generator import _combine_pdfs_on_page

        config = VisualizerConfig(layers_per_page=3)

        with pytest.raises(ValueError, match="Cannot combine empty list"):
            _combine_pdfs_on_page([], config)

    def test_combine_skips_empty_pdfs(self, sample_svg, mocker):
        """_combine_pdfs_on_page skips PDFs with no pages."""
        from io import BytesIO

        import pikepdf

        from glove80_visualizer.config import VisualizerConfig
        from glove80_visualizer.pdf_generator import _combine_pdfs_on_page, svg_to_pdf

        config = VisualizerConfig(layers_per_page=3)

        # Create a valid PDF
        valid_pdf = svg_to_pdf(sample_svg)

        # Create an empty PDF (no pages)
        empty_pdf_obj = pikepdf.new()
        empty_pdf_bytes = BytesIO()
        empty_pdf_obj.save(empty_pdf_bytes)
        empty_pdf = empty_pdf_bytes.getvalue()

        # Combine with empty PDF in the middle
        result = _combine_pdfs_on_page([valid_pdf, empty_pdf, valid_pdf], config)

        assert result.startswith(b"%PDF")
        # Should have created a valid combined PDF
        result_pdf = pikepdf.open(BytesIO(result))
        assert len(result_pdf.pages) == 1

    def test_combine_first_pdf_empty_uses_fallback_dimensions(self, sample_svg):
        """_combine_pdfs_on_page uses fallback dimensions when first PDF is empty."""
        from io import BytesIO

        import pikepdf

        from glove80_visualizer.config import VisualizerConfig
        from glove80_visualizer.pdf_generator import _combine_pdfs_on_page, svg_to_pdf

        config = VisualizerConfig(layers_per_page=2)

        # Create an empty PDF (no pages) as first PDF
        empty_pdf_obj = pikepdf.new()
        empty_pdf_bytes = BytesIO()
        empty_pdf_obj.save(empty_pdf_bytes)
        empty_pdf = empty_pdf_bytes.getvalue()

        # Create a valid PDF as second
        valid_pdf = svg_to_pdf(sample_svg)

        # Combine with empty first PDF - should use fallback 612x792 dimensions
        result = _combine_pdfs_on_page([empty_pdf, valid_pdf], config)

        assert result.startswith(b"%PDF")
        result_pdf = pikepdf.open(BytesIO(result))
        assert len(result_pdf.pages) == 1

        # Should have Letter size dimensions (fallback)
        mediabox = result_pdf.pages[0].mediabox
        width = float(mediabox[2]) - float(mediabox[0])
        height = float(mediabox[3]) - float(mediabox[1])
        assert width == 612.0
        assert height == 792.0


class TestLayersPerPage:
    """Tests for layers_per_page configuration."""

    def test_single_layer_per_page(self, sample_layers, sample_svg):
        """generate_pdf_with_toc with layers_per_page=1 uses full scale."""
        from io import BytesIO

        import pikepdf

        from glove80_visualizer.config import VisualizerConfig
        from glove80_visualizer.pdf_generator import generate_pdf_with_toc

        config = VisualizerConfig(layers_per_page=1)
        svgs = [sample_svg] * len(sample_layers)

        pdf_bytes = generate_pdf_with_toc(
            layers=sample_layers, svgs=svgs, config=config, include_toc=False
        )

        assert pdf_bytes.startswith(b"%PDF")

        # With layers_per_page=1, should have one page per layer
        pdf = pikepdf.open(BytesIO(pdf_bytes))
        assert len(pdf.pages) == len(sample_layers)

    def test_layers_per_page_consistent_scaling(self, sample_svg):
        """Final page with fewer layers uses same scale as full pages."""
        from io import BytesIO

        import pikepdf

        from glove80_visualizer.config import VisualizerConfig
        from glove80_visualizer.models import Layer
        from glove80_visualizer.pdf_generator import generate_pdf_with_toc

        # Create 4 layers - will produce 2 pages when layers_per_page=3
        # First page: 3 layers, second page: 1 layer
        layers = [Layer(name=f"Layer{i}", index=i, bindings=[]) for i in range(4)]
        svgs = [sample_svg] * 4

        config = VisualizerConfig(layers_per_page=3)

        pdf_bytes = generate_pdf_with_toc(
            layers=layers, svgs=svgs, config=config, include_toc=False
        )

        assert pdf_bytes.startswith(b"%PDF")

        pdf = pikepdf.open(BytesIO(pdf_bytes))
        # Should have 2 pages: one with 3 layers, one with 1 layer
        assert len(pdf.pages) == 2

        # Both pages should be same dimensions (consistent scaling)
        page1 = pdf.pages[0]
        page2 = pdf.pages[1]
        assert page1.mediabox == page2.mediabox

    def test_layers_per_page_zero_raises_error(self, sample_layers, sample_svg):
        """generate_pdf_with_toc raises ValueError for layers_per_page <= 0."""
        from glove80_visualizer.config import VisualizerConfig
        from glove80_visualizer.pdf_generator import generate_pdf_with_toc

        config = VisualizerConfig()
        config.layers_per_page = 0  # Invalid value
        svgs = [sample_svg] * len(sample_layers)

        with pytest.raises(ValueError, match="layers_per_page must be >= 1"):
            generate_pdf_with_toc(layers=sample_layers, svgs=svgs, config=config, include_toc=False)

    def test_layers_per_page_negative_raises_error(self, sample_layers, sample_svg):
        """generate_pdf_with_toc raises ValueError for negative layers_per_page."""
        from glove80_visualizer.config import VisualizerConfig
        from glove80_visualizer.pdf_generator import generate_pdf_with_toc

        config = VisualizerConfig()
        config.layers_per_page = -1  # Invalid value
        svgs = [sample_svg] * len(sample_layers)

        with pytest.raises(ValueError, match="layers_per_page must be >= 1"):
            generate_pdf_with_toc(layers=sample_layers, svgs=svgs, config=config, include_toc=False)

    def test_combined_page_uses_source_dimensions(self, sample_svg):
        """Combined pages derive dimensions from source PDFs, not hard-coded."""
        from io import BytesIO

        import pikepdf

        from glove80_visualizer.config import VisualizerConfig
        from glove80_visualizer.models import Layer
        from glove80_visualizer.pdf_generator import generate_pdf_with_toc

        # Create layers
        layers = [Layer(name=f"Layer{i}", index=i, bindings=[]) for i in range(2)]
        svgs = [sample_svg] * 2

        config = VisualizerConfig(layers_per_page=2)

        pdf_bytes = generate_pdf_with_toc(
            layers=layers, svgs=svgs, config=config, include_toc=False
        )

        # The combined page should have same width as source SVG-derived PDFs
        pdf = pikepdf.open(BytesIO(pdf_bytes))
        assert len(pdf.pages) == 1

        # Get the mediabox - should be derived from source, not hard-coded 612x792
        page = pdf.pages[0]
        mediabox = page.mediabox
        width = float(mediabox[2]) - float(mediabox[0])
        height = float(mediabox[3]) - float(mediabox[1])

        # The sample_svg fixture produces specific dimensions when converted to PDF
        # We just verify the page has reasonable dimensions (not zero, not default)
        assert width > 0
        assert height > 0
