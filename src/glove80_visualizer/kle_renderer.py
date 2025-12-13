"""
KLE (Keyboard Layout Editor) renderer using headless browser.

This module takes KLE JSON and renders it to PNG/PDF using
keyboard-layout-editor.com via a headless browser (Playwright).
"""

import tempfile
from pathlib import Path
from typing import Any

from playwright.sync_api import TimeoutError as PlaywrightTimeout  # type: ignore[import-not-found]
from playwright.sync_api import sync_playwright  # type: ignore[import-not-found]

from glove80_visualizer.models import Combo, Layer

# The KLE website URL
KLE_URL = "https://www.keyboard-layout-editor.com/"


def render_kle_to_png(
    kle_json: str,
    output_path: Path | str,
    width: int = 1920,
    height: int = 1200,
    scale: float = 2.0,
    timeout: int = 60000,
) -> Path:
    """
    Render KLE JSON to a PNG image using headless browser.

    This function:
    1. Opens keyboard-layout-editor.com in headless Chromium
    2. Uploads the KLE JSON via the "Upload JSON" button (simulates file upload)
    3. Takes a screenshot of the rendered keyboard

    Args:
        kle_json: KLE-format JSON string
        output_path: Path to save the PNG image
        width: Browser viewport width
        height: Browser viewport height
        scale: Device scale factor for higher resolution
        timeout: Timeout in milliseconds for page operations

    Returns:
        Path to the saved PNG file

    Raises:
        RuntimeError: If rendering fails
    """
    output_path = Path(output_path)

    # Write JSON to a temporary file for upload
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        tmp.write(kle_json)
        tmp_path = Path(tmp.name)

    try:
        with sync_playwright() as p:
            # Launch headless browser
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": width, "height": height},
                device_scale_factor=scale,
            )
            page = context.new_page()

            try:
                # Navigate to KLE
                page.goto(KLE_URL, wait_until="networkidle", timeout=timeout)

                # Wait for the page to be ready
                page.wait_for_selector("#keyboard-bg", timeout=timeout)
                page.wait_for_timeout(2000)  # Let Angular initialize

                # Click on Raw data tab to access Upload JSON button
                page.click("text=Raw data")
                page.wait_for_timeout(500)

                # Use the Upload JSON button with file chooser
                with page.expect_file_chooser() as fc_info:
                    page.click("text=Upload JSON")
                file_chooser = fc_info.value
                file_chooser.set_files(str(tmp_path))

                # Wait for the keyboard to render
                page.wait_for_timeout(2000)

                # Take screenshot of just the keyboard element
                keyboard_element = page.locator("#keyboard-bg")
                keyboard_element.screenshot(path=str(output_path))

            except PlaywrightTimeout as e:
                raise RuntimeError(f"Timeout rendering KLE: {e}")
            except Exception as e:
                raise RuntimeError(f"Error rendering KLE: {e}")
            finally:
                browser.close()
    finally:
        # Clean up temp file
        if tmp_path.exists():
            tmp_path.unlink()

    return output_path


def render_kle_to_pdf(
    kle_json: str,
    output_path: Path | str,
    width: int = 1920,
    height: int = 1200,
    timeout: int = 30000,
) -> Path:
    """
    Render KLE JSON to a PDF file.

    This creates a PNG first, then converts to PDF using the existing
    PDF generation infrastructure.

    Args:
        kle_json: KLE-format JSON string
        output_path: Path to save the PDF
        width: Browser viewport width
        height: Browser viewport height
        timeout: Timeout for rendering

    Returns:
        Path to the saved PDF file
    """
    output_path = Path(output_path)

    # Create temporary PNG
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        png_path = Path(tmp.name)

    try:
        # Render to PNG first
        render_kle_to_png(kle_json, png_path, width=width, height=height, timeout=timeout)

        # Convert PNG to PDF
        _png_to_pdf(png_path, output_path)
    finally:
        # Clean up temp file
        if png_path.exists():
            png_path.unlink()

    return output_path


def _png_to_pdf(png_path: Path, pdf_path: Path) -> None:
    """Convert a PNG image to PDF using CairoSVG/PIL."""
    try:
        from PIL import Image

        img: Any = Image.open(png_path)
        # Convert to RGB if necessary (PDF doesn't support alpha)
        if img.mode == "RGBA":
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        img.save(pdf_path, "PDF", resolution=150.0)
    except ImportError:  # pragma: no cover
        raise RuntimeError("PIL/Pillow is required for PDF conversion")


def render_layer_kle(
    layer: Layer,
    output_path: Path | str,
    output_format: str = "png",
    combos: list[Combo] | None = None,
    os_style: str = "mac",
    **kwargs: Any,
) -> Path:
    """
    Convenience function to render a Layer object to KLE output.

    Args:
        layer: Layer object to render
        output_path: Path for output file
        output_format: "png" or "pdf"
        combos: Optional list of Combo objects to display in text blocks
        os_style: OS style for modifier symbols ("mac", "windows", or "linux")
        **kwargs: Additional arguments passed to render functions

    Returns:
        Path to the output file
    """
    from glove80_visualizer.kle_template import generate_kle_from_template

    # Separate template kwargs from render kwargs
    template_kwargs = {k: v for k, v in kwargs.items() if k in ("activators", "layer_names")}
    render_kwargs = {k: v for k, v in kwargs.items() if k in ("width", "height", "timeout")}

    kle_json = generate_kle_from_template(
        layer, combos=combos, os_style=os_style, **template_kwargs
    )

    if output_format.lower() == "pdf":
        return render_kle_to_pdf(kle_json, output_path, **render_kwargs)
    else:
        return render_kle_to_png(kle_json, output_path, **render_kwargs)


def render_all_layers_kle(
    layers: list[Layer],
    output_dir: Path | str,
    output_format: str = "png",
    combos: list[Combo] | None = None,
    os_style: str = "mac",
    **kwargs: Any,
) -> list[Path]:
    """
    Render all layers to KLE output files.

    Args:
        layers: List of Layer objects
        output_dir: Directory to save output files
        output_format: "png" or "pdf"
        combos: Optional list of Combo objects to display in text blocks
        os_style: OS style for modifier symbols ("mac", "windows", or "linux")
        **kwargs: Additional arguments passed to render functions

    Returns:
        List of paths to output files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_paths = []
    for layer in layers:
        suffix = ".pdf" if output_format.lower() == "pdf" else ".png"
        output_path = output_dir / f"{layer.name}{suffix}"
        render_layer_kle(
            layer,
            output_path,
            output_format=output_format,
            combos=combos,
            os_style=os_style,
            **kwargs,
        )
        output_paths.append(output_path)

    return output_paths


def create_combined_pdf_kle(
    layers: list[Layer],
    output_path: Path | str,
    combos: list[Combo] | None = None,
    os_style: str = "mac",
    **kwargs: Any,
) -> Path:
    """
    Render all layers and combine into a single PDF.

    Args:
        layers: List of Layer objects
        output_path: Path for combined PDF
        combos: Optional list of Combo objects to display in text blocks
        os_style: OS style for modifier symbols ("mac", "windows", or "linux")
        **kwargs: Additional arguments passed to render functions

    Returns:
        Path to the combined PDF
    """
    import tempfile

    from glove80_visualizer.pdf_generator import merge_pdfs

    output_path = Path(output_path)

    # Create temporary directory for individual PDFs
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Render each layer to PDF
        pdf_paths = render_all_layers_kle(
            layers,
            tmp_path,
            output_format="pdf",
            combos=combos,
            os_style=os_style,
            **kwargs,
        )

        # Read all PDFs as bytes and merge using pikepdf
        pdf_bytes_list = [path.read_bytes() for path in pdf_paths]
        merged_pdf = merge_pdfs(pdf_bytes_list)

        # Write merged PDF to output
        output_path.write_bytes(merged_pdf)

    return output_path
