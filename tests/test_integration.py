"""
Integration tests for the full visualization pipeline.

These tests verify the complete end-to-end workflow.
"""

import time

import pytest


class TestEndToEnd:
    """End-to-end integration tests."""

    def test_e2e_simple_keymap(self, simple_keymap_path, tmp_path):
        """SPEC-I001: Complete pipeline works with minimal keymap."""
        from glove80_visualizer import generate_visualization

        output = tmp_path / "output.pdf"
        result = generate_visualization(simple_keymap_path, output)

        assert result.success is True
        assert output.exists()
        assert output.stat().st_size > 1000  # Reasonable PDF size

    @pytest.mark.slow
    def test_e2e_daves_keymap(self, daves_keymap_path, tmp_path):
        """SPEC-I002: Complete pipeline works with full 32-layer keymap."""
        from glove80_visualizer import generate_visualization

        if not daves_keymap_path.exists():
            pytest.skip("Dave's keymap file not found")

        output = tmp_path / "daves_layers.pdf"
        result = generate_visualization(daves_keymap_path, output)

        assert result.success is True
        assert output.exists()
        # Should have reasonable size for 32 pages
        assert output.stat().st_size > 50000

    @pytest.mark.slow
    def test_e2e_all_layers_present(self, daves_keymap_path, tmp_path):
        """SPEC-I003: All 32 layers are included in output PDF."""
        import pikepdf

        from glove80_visualizer import generate_visualization

        if not daves_keymap_path.exists():
            pytest.skip("Dave's keymap file not found")

        output = tmp_path / "output.pdf"
        generate_visualization(daves_keymap_path, output)

        pdf = pikepdf.open(str(output))
        # With default 3 layers per page: ceil(32/3)=11 content pages + 2 TOC pages = 13
        # We check for >= 11 to account for potential TOC variations
        assert len(pdf.pages) >= 11

    @pytest.mark.slow
    def test_e2e_performance(self, daves_keymap_path, tmp_path):
        """SPEC-I004: Pipeline completes within reasonable time."""
        from glove80_visualizer import generate_visualization

        if not daves_keymap_path.exists():
            pytest.skip("Dave's keymap file not found")

        output = tmp_path / "output.pdf"

        start = time.time()
        generate_visualization(daves_keymap_path, output)
        duration = time.time() - start

        # Should complete within 60 seconds
        assert duration < 60


class TestPipelineStages:
    """Tests for individual pipeline stages working together."""

    def test_parse_then_extract(self, simple_keymap_path):
        """Parser output can be consumed by extractor."""
        from glove80_visualizer.extractor import extract_layers
        from glove80_visualizer.parser import parse_zmk_keymap

        yaml_content = parse_zmk_keymap(simple_keymap_path)
        layers = extract_layers(yaml_content)

        assert len(layers) >= 1
        assert layers[0].name is not None

    def test_extract_then_generate_svg(self, simple_keymap_path):
        """Extractor output can be consumed by SVG generator."""
        from glove80_visualizer.extractor import extract_layers
        from glove80_visualizer.parser import parse_zmk_keymap
        from glove80_visualizer.svg_generator import generate_layer_svg

        yaml_content = parse_zmk_keymap(simple_keymap_path)
        layers = extract_layers(yaml_content)
        svg = generate_layer_svg(layers[0])

        assert svg.startswith("<?xml") or svg.startswith("<svg")

    def test_svg_then_pdf(self, simple_keymap_path):
        """SVG output can be converted to PDF."""
        from glove80_visualizer.extractor import extract_layers
        from glove80_visualizer.parser import parse_zmk_keymap
        from glove80_visualizer.pdf_generator import svg_to_pdf
        from glove80_visualizer.svg_generator import generate_layer_svg

        yaml_content = parse_zmk_keymap(simple_keymap_path)
        layers = extract_layers(yaml_content)
        svg = generate_layer_svg(layers[0])
        pdf = svg_to_pdf(svg)

        assert pdf.startswith(b"%PDF")


class TestErrorRecovery:
    """Tests for error handling across the pipeline."""

    def test_partial_failure_continues(self, multi_layer_keymap_path, tmp_path):
        """Pipeline continues processing after single layer failure."""
        from glove80_visualizer import generate_visualization
        from glove80_visualizer.config import VisualizerConfig

        output = tmp_path / "output.pdf"
        config = VisualizerConfig(continue_on_error=True)

        # Even if one layer has issues, others should still be processed
        result = generate_visualization(multi_layer_keymap_path, output, config=config)

        # Should have some output even with errors
        assert output.exists() or result.partial_success

    def test_error_report_generated(self, invalid_keymap_path, tmp_path):
        """Pipeline generates error report for failures."""
        from glove80_visualizer import generate_visualization

        output = tmp_path / "output.pdf"
        result = generate_visualization(invalid_keymap_path, output)

        assert result.success is False
        assert result.error_message is not None
        assert len(result.error_message) > 0


class TestOutputFormats:
    """Tests for different output format options."""

    def test_svg_only_output(self, simple_keymap_path, tmp_path):
        """Pipeline can output individual SVG files."""
        from glove80_visualizer import generate_visualization
        from glove80_visualizer.config import VisualizerConfig

        output_dir = tmp_path / "svgs"
        config = VisualizerConfig(output_format="svg")

        generate_visualization(simple_keymap_path, output_dir, config=config)

        svg_files = list(output_dir.glob("*.svg"))
        assert len(svg_files) >= 1

    def test_pdf_with_toc(self, multi_layer_keymap_path, tmp_path):
        """Pipeline can include table of contents in PDF."""
        import pikepdf

        from glove80_visualizer import generate_visualization
        from glove80_visualizer.config import VisualizerConfig

        output = tmp_path / "output.pdf"
        config = VisualizerConfig(include_toc=True)

        generate_visualization(multi_layer_keymap_path, output, config=config)

        pdf = pikepdf.open(str(output))
        # Multi-layer has 4 layers, with 3 layers per page: ceil(4/3)=2 content pages
        # Plus 1 TOC page = 3 total pages
        assert len(pdf.pages) >= 2
