"""
Tests for KLE (Keyboard Layout Editor) renderer.

These tests use mock factories from conftest.py to achieve 100% coverage
without launching actual browsers or processing real images.
"""

from pathlib import Path

import pytest

from glove80_visualizer.kle_renderer import (
    _png_to_pdf,
    create_combined_pdf_kle,
    render_all_layers_kle,
    render_kle_to_pdf,
    render_kle_to_png,
    render_layer_kle,
)
from glove80_visualizer.models import Combo, KeyBinding, Layer


class TestRenderKleToPng:
    """Tests for render_kle_to_png function."""

    def test_render_kle_to_png_success(
        self, tmp_path: Path, playwright_mocks: tuple, mocker
    ) -> None:
        """Should render KLE JSON to PNG with mocked browser."""
        mock_playwright, mock_browser, mock_page = playwright_mocks

        mocker.patch(
            "glove80_visualizer.kle_renderer.sync_playwright",
            return_value=mock_playwright,
        )

        output_path = tmp_path / "test.png"
        result = render_kle_to_png('["A", "B", "C"]', output_path)

        assert result == output_path
        mock_browser.close.assert_called_once()

    def test_render_kle_to_png_with_custom_dimensions(
        self, tmp_path: Path, playwright_mocks: tuple, mocker
    ) -> None:
        """Should pass custom viewport dimensions to browser."""
        mock_playwright, mock_browser, mock_page = playwright_mocks

        mocker.patch(
            "glove80_visualizer.kle_renderer.sync_playwright",
            return_value=mock_playwright,
        )

        output_path = tmp_path / "test.png"
        render_kle_to_png('["A"]', output_path, width=1280, height=720, scale=1.5)

        # Verify viewport was set
        mock_browser.new_context.assert_called_once()
        call_kwargs = mock_browser.new_context.call_args[1]
        assert call_kwargs["viewport"] == {"width": 1280, "height": 720}
        assert call_kwargs["device_scale_factor"] == 1.5

    def test_render_kle_to_png_timeout_error(
        self, tmp_path: Path, playwright_mocks: tuple, mocker
    ) -> None:
        """Should raise RuntimeError on Playwright timeout."""
        mock_playwright, mock_browser, mock_page = playwright_mocks

        # Import the timeout error class for mocking
        from playwright.sync_api import TimeoutError as PlaywrightTimeout

        mock_page.goto.side_effect = PlaywrightTimeout("Page load timed out")

        mocker.patch(
            "glove80_visualizer.kle_renderer.sync_playwright",
            return_value=mock_playwright,
        )

        output_path = tmp_path / "test.png"
        with pytest.raises(RuntimeError, match="Timeout rendering KLE"):
            render_kle_to_png('["A"]', output_path)

        mock_browser.close.assert_called_once()

    def test_render_kle_to_png_generic_error(
        self, tmp_path: Path, playwright_mocks: tuple, mocker
    ) -> None:
        """Should raise RuntimeError on generic browser error."""
        mock_playwright, mock_browser, mock_page = playwright_mocks

        mock_page.goto.side_effect = Exception("Network error")

        mocker.patch(
            "glove80_visualizer.kle_renderer.sync_playwright",
            return_value=mock_playwright,
        )

        output_path = tmp_path / "test.png"
        with pytest.raises(RuntimeError, match="Error rendering KLE"):
            render_kle_to_png('["A"]', output_path)

        mock_browser.close.assert_called_once()

    def test_render_kle_to_png_cleans_temp_file(
        self, tmp_path: Path, playwright_mocks: tuple, mocker
    ) -> None:
        """Should clean up temporary JSON file after rendering."""
        mock_playwright, mock_browser, mock_page = playwright_mocks

        mocker.patch(
            "glove80_visualizer.kle_renderer.sync_playwright",
            return_value=mock_playwright,
        )

        # Track temp files created
        temp_files_created = []
        original_named_temp = __import__("tempfile").NamedTemporaryFile

        def tracking_temp(*args, **kwargs):
            result = original_named_temp(*args, **kwargs)
            temp_files_created.append(Path(result.name))
            return result

        mocker.patch("tempfile.NamedTemporaryFile", tracking_temp)

        output_path = tmp_path / "test.png"
        render_kle_to_png('["A"]', output_path)

        # Temp file should be cleaned up
        for temp_file in temp_files_created:
            assert not temp_file.exists(), f"Temp file {temp_file} was not cleaned up"

    def test_render_kle_to_png_string_path(
        self, tmp_path: Path, playwright_mocks: tuple, mocker
    ) -> None:
        """Should accept string path and convert to Path."""
        mock_playwright, mock_browser, mock_page = playwright_mocks

        mocker.patch(
            "glove80_visualizer.kle_renderer.sync_playwright",
            return_value=mock_playwright,
        )

        output_path = str(tmp_path / "test.png")
        result = render_kle_to_png('["A"]', output_path)

        assert isinstance(result, Path)
        assert str(result) == output_path


class TestPngToPdf:
    """Tests for _png_to_pdf helper function."""

    def test_png_to_pdf_rgba_image(self, tmp_path: Path) -> None:
        """Should convert RGBA image to RGB for PDF."""
        from PIL import Image

        png_path = tmp_path / "test.png"
        pdf_path = tmp_path / "test.pdf"

        # Create RGBA image with transparency
        img = Image.new("RGBA", (100, 100), (255, 0, 0, 128))
        img.save(png_path)

        _png_to_pdf(png_path, pdf_path)

        assert pdf_path.exists()

    def test_png_to_pdf_rgb_image(self, tmp_path: Path) -> None:
        """Should handle RGB image directly."""
        from PIL import Image

        png_path = tmp_path / "test.png"
        pdf_path = tmp_path / "test.pdf"

        # Create RGB image
        img = Image.new("RGB", (100, 100), (255, 0, 0))
        img.save(png_path)

        _png_to_pdf(png_path, pdf_path)

        assert pdf_path.exists()

    def test_png_to_pdf_grayscale_image(self, tmp_path: Path) -> None:
        """Should convert grayscale to RGB for PDF."""
        from PIL import Image

        png_path = tmp_path / "test.png"
        pdf_path = tmp_path / "test.pdf"

        # Create grayscale image (mode "L")
        img = Image.new("L", (100, 100), 128)
        img.save(png_path)

        _png_to_pdf(png_path, pdf_path)

        assert pdf_path.exists()

    def test_png_to_pdf_with_path_conversion(self, tmp_path: Path) -> None:
        """Should handle Path objects correctly."""
        from PIL import Image

        png_path = tmp_path / "test_path.png"
        pdf_path = tmp_path / "test_path.pdf"

        # Create simple image
        img = Image.new("RGB", (50, 50), (0, 255, 0))
        img.save(png_path)

        # Call with Path objects
        _png_to_pdf(png_path, pdf_path)

        assert pdf_path.exists()
        # Verify it's a valid PDF (starts with %PDF)
        with open(pdf_path, "rb") as f:
            header = f.read(4)
            assert header == b"%PDF"


class TestRenderKleToPdf:
    """Tests for render_kle_to_pdf function."""

    def test_render_kle_to_pdf_success(
        self, tmp_path: Path, playwright_mocks: tuple, mocker
    ) -> None:
        """Should render KLE JSON to PDF via PNG intermediate."""
        mock_playwright, mock_browser, mock_page = playwright_mocks

        mocker.patch(
            "glove80_visualizer.kle_renderer.sync_playwright",
            return_value=mock_playwright,
        )

        # Create a real PNG for the conversion step
        from PIL import Image

        def create_png_side_effect(kle_json, png_path, **kwargs):
            img = Image.new("RGB", (100, 100), (255, 0, 0))
            img.save(png_path)
            return png_path

        mocker.patch(
            "glove80_visualizer.kle_renderer.render_kle_to_png",
            side_effect=create_png_side_effect,
        )

        output_path = tmp_path / "test.pdf"
        result = render_kle_to_pdf('["A", "B"]', output_path)

        assert result == output_path
        assert output_path.exists()

    def test_render_kle_to_pdf_cleans_temp_png(self, tmp_path: Path, mocker) -> None:
        """Should clean up temporary PNG file after conversion."""
        from PIL import Image

        # Track which temp files exist
        temp_png_path = None

        def create_png_side_effect(kle_json, png_path, **kwargs):
            nonlocal temp_png_path
            temp_png_path = png_path
            img = Image.new("RGB", (100, 100), (255, 0, 0))
            img.save(png_path)
            return png_path

        mocker.patch(
            "glove80_visualizer.kle_renderer.render_kle_to_png",
            side_effect=create_png_side_effect,
        )

        output_path = tmp_path / "test.pdf"
        render_kle_to_pdf('["A"]', output_path)

        # Temp PNG should be cleaned up
        assert temp_png_path is not None
        assert not temp_png_path.exists()

    def test_render_kle_to_pdf_string_path(self, tmp_path: Path, mocker) -> None:
        """Should accept string path."""
        from PIL import Image

        def create_png_side_effect(kle_json, png_path, **kwargs):
            img = Image.new("RGB", (100, 100), (255, 0, 0))
            img.save(png_path)
            return png_path

        mocker.patch(
            "glove80_visualizer.kle_renderer.render_kle_to_png",
            side_effect=create_png_side_effect,
        )

        output_path = str(tmp_path / "test.pdf")
        result = render_kle_to_pdf('["A"]', output_path)

        assert isinstance(result, Path)


class TestRenderLayerKle:
    """Tests for render_layer_kle convenience function."""

    @pytest.fixture
    def test_layer(self) -> Layer:
        """Create a test layer."""
        bindings = [KeyBinding(position=i, tap=chr(65 + i)) for i in range(10)]
        return Layer(name="Test", index=0, bindings=bindings)

    def test_render_layer_kle_png(self, tmp_path: Path, test_layer: Layer, mocker) -> None:
        """Should render layer to PNG format."""
        mock_render_png = mocker.patch(
            "glove80_visualizer.kle_renderer.render_kle_to_png",
            return_value=tmp_path / "test.png",
        )
        mocker.patch(
            "glove80_visualizer.kle_template.generate_kle_from_template",
            return_value='["test"]',
        )

        output_path = tmp_path / "test.png"
        result = render_layer_kle(test_layer, output_path, output_format="png")

        assert result == output_path
        mock_render_png.assert_called_once()

    def test_render_layer_kle_pdf(self, tmp_path: Path, test_layer: Layer, mocker) -> None:
        """Should render layer to PDF format."""
        mock_render_pdf = mocker.patch(
            "glove80_visualizer.kle_renderer.render_kle_to_pdf",
            return_value=tmp_path / "test.pdf",
        )
        mocker.patch(
            "glove80_visualizer.kle_template.generate_kle_from_template",
            return_value='["test"]',
        )

        output_path = tmp_path / "test.pdf"
        result = render_layer_kle(test_layer, output_path, output_format="pdf")

        assert result == output_path
        mock_render_pdf.assert_called_once()

    def test_render_layer_kle_with_combos(self, tmp_path: Path, test_layer: Layer, mocker) -> None:
        """Should pass combos to template generator."""
        mocker.patch(
            "glove80_visualizer.kle_renderer.render_kle_to_png",
            return_value=tmp_path / "test.png",
        )
        mock_template = mocker.patch(
            "glove80_visualizer.kle_template.generate_kle_from_template",
            return_value='["test"]',
        )

        combos = [Combo(name="C1", positions=[0, 1], action="test", layers=None)]
        output_path = tmp_path / "test.png"
        render_layer_kle(test_layer, output_path, combos=combos)

        mock_template.assert_called_once()
        assert mock_template.call_args[1]["combos"] == combos

    def test_render_layer_kle_with_os_style(
        self, tmp_path: Path, test_layer: Layer, mocker
    ) -> None:
        """Should pass os_style to template generator."""
        mocker.patch(
            "glove80_visualizer.kle_renderer.render_kle_to_png",
            return_value=tmp_path / "test.png",
        )
        mock_template = mocker.patch(
            "glove80_visualizer.kle_template.generate_kle_from_template",
            return_value='["test"]',
        )

        output_path = tmp_path / "test.png"
        render_layer_kle(test_layer, output_path, os_style="windows")

        mock_template.assert_called_once()
        assert mock_template.call_args[1]["os_style"] == "windows"

    def test_render_layer_kle_passes_kwargs(
        self, tmp_path: Path, test_layer: Layer, mocker
    ) -> None:
        """Should pass extra kwargs to render function."""
        mock_render_png = mocker.patch(
            "glove80_visualizer.kle_renderer.render_kle_to_png",
            return_value=tmp_path / "test.png",
        )
        mocker.patch(
            "glove80_visualizer.kle_template.generate_kle_from_template",
            return_value='["test"]',
        )

        output_path = tmp_path / "test.png"
        render_layer_kle(test_layer, output_path, width=1280, timeout=5000)

        call_kwargs = mock_render_png.call_args[1]
        assert call_kwargs.get("width") == 1280
        assert call_kwargs.get("timeout") == 5000


class TestRenderAllLayersKle:
    """Tests for render_all_layers_kle function."""

    @pytest.fixture
    def test_layers(self) -> list[Layer]:
        """Create test layers."""
        layers = []
        for i in range(3):
            bindings = [KeyBinding(position=j, tap=chr(65 + j)) for j in range(10)]
            layers.append(Layer(name=f"Layer{i}", index=i, bindings=bindings))
        return layers

    def test_render_all_layers_png(self, tmp_path: Path, test_layers: list[Layer], mocker) -> None:
        """Should render all layers to PNG files."""

        def mock_render(layer, output_path, **kwargs):
            Path(output_path).touch()
            return Path(output_path)

        mocker.patch(
            "glove80_visualizer.kle_renderer.render_layer_kle",
            side_effect=mock_render,
        )

        output_dir = tmp_path / "output"
        results = render_all_layers_kle(test_layers, output_dir)

        assert len(results) == 3
        assert output_dir.exists()
        for i, result in enumerate(results):
            assert result.suffix == ".png"
            assert f"Layer{i}" in result.name

    def test_render_all_layers_pdf(self, tmp_path: Path, test_layers: list[Layer], mocker) -> None:
        """Should render all layers to PDF files."""

        def mock_render(layer, output_path, **kwargs):
            Path(output_path).touch()
            return Path(output_path)

        mocker.patch(
            "glove80_visualizer.kle_renderer.render_layer_kle",
            side_effect=mock_render,
        )

        output_dir = tmp_path / "output"
        results = render_all_layers_kle(test_layers, output_dir, output_format="pdf")

        assert len(results) == 3
        for result in results:
            assert result.suffix == ".pdf"

    def test_render_all_layers_creates_dir(
        self, tmp_path: Path, test_layers: list[Layer], mocker
    ) -> None:
        """Should create output directory if it doesn't exist."""
        mocker.patch(
            "glove80_visualizer.kle_renderer.render_layer_kle",
            side_effect=lambda layer, path, **kwargs: Path(path),
        )

        output_dir = tmp_path / "nested" / "output"
        assert not output_dir.exists()

        render_all_layers_kle(test_layers, output_dir)

        assert output_dir.exists()

    def test_render_all_layers_passes_combos(
        self, tmp_path: Path, test_layers: list[Layer], mocker
    ) -> None:
        """Should pass combos to each layer render."""
        mock_render = mocker.patch(
            "glove80_visualizer.kle_renderer.render_layer_kle",
            side_effect=lambda layer, path, **kwargs: Path(path),
        )

        combos = [Combo(name="C1", positions=[0, 1], action="test", layers=None)]
        output_dir = tmp_path / "output"
        render_all_layers_kle(test_layers, output_dir, combos=combos)

        for call in mock_render.call_args_list:
            assert call[1]["combos"] == combos

    def test_render_all_layers_passes_os_style(
        self, tmp_path: Path, test_layers: list[Layer], mocker
    ) -> None:
        """Should pass os_style to each layer render."""
        mock_render = mocker.patch(
            "glove80_visualizer.kle_renderer.render_layer_kle",
            side_effect=lambda layer, path, **kwargs: Path(path),
        )

        output_dir = tmp_path / "output"
        render_all_layers_kle(test_layers, output_dir, os_style="linux")

        for call in mock_render.call_args_list:
            assert call[1]["os_style"] == "linux"

    def test_render_all_layers_empty_list(self, tmp_path: Path, mocker) -> None:
        """Should handle empty layer list."""
        mock_render = mocker.patch(
            "glove80_visualizer.kle_renderer.render_layer_kle",
        )

        output_dir = tmp_path / "output"
        results = render_all_layers_kle([], output_dir)

        assert results == []
        mock_render.assert_not_called()


class TestCreateCombinedPdfKle:
    """Tests for create_combined_pdf_kle function."""

    @pytest.fixture
    def test_layers(self) -> list[Layer]:
        """Create test layers."""
        layers = []
        for i in range(3):
            bindings = [KeyBinding(position=j, tap=chr(65 + j)) for j in range(10)]
            layers.append(Layer(name=f"Layer{i}", index=i, bindings=bindings))
        return layers

    def test_create_combined_pdf_success(
        self, tmp_path: Path, test_layers: list[Layer], mocker
    ) -> None:
        """Should create combined PDF from multiple layers."""
        # Create actual PDF files that can be merged
        from PIL import Image

        def mock_render_all(layers, output_dir, **kwargs):
            paths = []
            for layer in layers:
                pdf_path = Path(output_dir) / f"{layer.name}.pdf"
                img = Image.new("RGB", (100, 100), (255, 0, 0))
                img.save(pdf_path, "PDF")
                paths.append(pdf_path)
            return paths

        mocker.patch(
            "glove80_visualizer.kle_renderer.render_all_layers_kle",
            side_effect=mock_render_all,
        )

        output_path = tmp_path / "combined.pdf"
        result = create_combined_pdf_kle(test_layers, output_path)

        assert result == output_path
        assert output_path.exists()

    def test_create_combined_pdf_passes_combos(
        self, tmp_path: Path, test_layers: list[Layer], mocker
    ) -> None:
        """Should pass combos to render_all_layers_kle."""
        from PIL import Image

        def mock_render_all(layers, output_dir, **kwargs):
            paths = []
            for layer in layers:
                pdf_path = Path(output_dir) / f"{layer.name}.pdf"
                img = Image.new("RGB", (100, 100), (255, 0, 0))
                img.save(pdf_path, "PDF")
                paths.append(pdf_path)
            return paths

        mock_render = mocker.patch(
            "glove80_visualizer.kle_renderer.render_all_layers_kle",
            side_effect=mock_render_all,
        )

        combos = [Combo(name="C1", positions=[0, 1], action="test", layers=None)]
        output_path = tmp_path / "combined.pdf"
        create_combined_pdf_kle(test_layers, output_path, combos=combos)

        mock_render.assert_called_once()
        assert mock_render.call_args[1]["combos"] == combos

    def test_create_combined_pdf_passes_os_style(
        self, tmp_path: Path, test_layers: list[Layer], mocker
    ) -> None:
        """Should pass os_style to render_all_layers_kle."""
        from PIL import Image

        def mock_render_all(layers, output_dir, **kwargs):
            paths = []
            for layer in layers:
                pdf_path = Path(output_dir) / f"{layer.name}.pdf"
                img = Image.new("RGB", (100, 100), (255, 0, 0))
                img.save(pdf_path, "PDF")
                paths.append(pdf_path)
            return paths

        mock_render = mocker.patch(
            "glove80_visualizer.kle_renderer.render_all_layers_kle",
            side_effect=mock_render_all,
        )

        output_path = tmp_path / "combined.pdf"
        create_combined_pdf_kle(test_layers, output_path, os_style="windows")

        mock_render.assert_called_once()
        assert mock_render.call_args[1]["os_style"] == "windows"

    def test_create_combined_pdf_string_path(
        self, tmp_path: Path, test_layers: list[Layer], mocker
    ) -> None:
        """Should accept string path."""
        from PIL import Image

        def mock_render_all(layers, output_dir, **kwargs):
            paths = []
            for layer in layers:
                pdf_path = Path(output_dir) / f"{layer.name}.pdf"
                img = Image.new("RGB", (100, 100), (255, 0, 0))
                img.save(pdf_path, "PDF")
                paths.append(pdf_path)
            return paths

        mocker.patch(
            "glove80_visualizer.kle_renderer.render_all_layers_kle",
            side_effect=mock_render_all,
        )

        output_path = str(tmp_path / "combined.pdf")
        result = create_combined_pdf_kle(test_layers, output_path)

        assert isinstance(result, Path)

    def test_create_combined_pdf_single_layer(self, tmp_path: Path, mocker) -> None:
        """Should handle single layer."""
        from PIL import Image

        layer = Layer(
            name="Single",
            index=0,
            bindings=[KeyBinding(position=0, tap="A")],
        )

        def mock_render_all(layers, output_dir, **kwargs):
            pdf_path = Path(output_dir) / f"{layers[0].name}.pdf"
            img = Image.new("RGB", (100, 100), (255, 0, 0))
            img.save(pdf_path, "PDF")
            return [pdf_path]

        mocker.patch(
            "glove80_visualizer.kle_renderer.render_all_layers_kle",
            side_effect=mock_render_all,
        )

        output_path = tmp_path / "single.pdf"
        result = create_combined_pdf_kle([layer], output_path)

        assert result == output_path
        assert output_path.exists()
