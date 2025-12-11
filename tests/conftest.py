"""
Pytest fixtures for glove80-keymap-visualizer tests.

This module provides common fixtures and mock factories for testing.
Mock factories ensure consistent, fast tests without external dependencies.
"""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the path to the test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def simple_keymap_path(fixtures_dir: Path) -> Path:
    """Return path to the simple single-layer keymap fixture."""
    return fixtures_dir / "simple.keymap"


@pytest.fixture
def multi_layer_keymap_path(fixtures_dir: Path) -> Path:
    """Return path to the multi-layer keymap fixture."""
    return fixtures_dir / "multi_layer.keymap"


@pytest.fixture
def hold_tap_keymap_path(fixtures_dir: Path) -> Path:
    """Return path to the keymap with hold-tap behaviors fixture."""
    return fixtures_dir / "hold_tap.keymap"


@pytest.fixture
def invalid_keymap_path(fixtures_dir: Path) -> Path:
    """Return path to the intentionally invalid keymap fixture."""
    return fixtures_dir / "invalid.keymap"


@pytest.fixture
def daves_keymap_path() -> Path:
    """Return path to Dave's full 32-layer keymap."""
    return Path(__file__).parent.parent / "daves-current-glove80-keymap.keymap"


@pytest.fixture
def sample_layer():
    """Create a sample Layer object for testing."""
    from glove80_visualizer.models import KeyBinding, Layer

    bindings = [KeyBinding(position=i, tap=chr(65 + (i % 26))) for i in range(80)]  # A-Z cycling
    return Layer(name="TestLayer", index=0, bindings=bindings)


@pytest.fixture
def sample_layers():
    """Create multiple sample Layer objects for testing."""
    from glove80_visualizer.models import KeyBinding, Layer

    layers = []
    for layer_idx in range(4):
        bindings = [KeyBinding(position=i, tap=chr(65 + ((i + layer_idx) % 26))) for i in range(80)]
        layers.append(Layer(name=f"Layer{layer_idx}", index=layer_idx, bindings=bindings))
    return layers


@pytest.fixture
def sample_svg() -> str:
    """Return a minimal valid SVG for testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400" viewBox="0 0 800 400">
  <rect x="10" y="10" width="780" height="380" fill="#f0f0f0" stroke="#000"/>
  <text x="400" y="200" text-anchor="middle" font-size="24">Test Layer</text>
</svg>"""


@pytest.fixture
def sample_pdf_pages(sample_svg) -> list:
    """Return a list of sample PDF bytes for testing merging."""
    # Note: This will be implemented when pdf_generator is available
    # For now, return empty list as placeholder
    return []


@pytest.fixture
def runner():
    """Return a Click CLI test runner."""
    from click.testing import CliRunner

    return CliRunner()


@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for test outputs."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


# =============================================================================
# Mock Factories for External Dependencies
# =============================================================================


class PlaywrightMockFactory:
    """
    Factory for creating Playwright browser mocks.

    Use this to test code that uses headless browsers without actually
    launching a browser. All browser operations are mocked.

    Example:
        def test_render_kle(playwright_mocks):
            mock_playwright, mock_browser, mock_page = playwright_mocks
            # Test code that uses sync_playwright()
    """

    @staticmethod
    def create_page_mock() -> MagicMock:
        """Create a mock Playwright page with all expected methods."""
        mock_page = MagicMock()
        mock_page.goto = MagicMock()
        mock_page.wait_for_selector = MagicMock()
        mock_page.wait_for_timeout = MagicMock()
        mock_page.click = MagicMock()

        # File chooser mock
        mock_file_chooser = MagicMock()
        mock_fc_context = MagicMock()
        mock_fc_context.__enter__ = MagicMock(return_value=mock_fc_context)
        mock_fc_context.__exit__ = MagicMock(return_value=False)
        mock_fc_context.value = mock_file_chooser
        mock_page.expect_file_chooser = MagicMock(return_value=mock_fc_context)

        # Locator mock for screenshots
        mock_locator = MagicMock()
        mock_locator.screenshot = MagicMock()
        mock_page.locator = MagicMock(return_value=mock_locator)

        return mock_page

    @staticmethod
    def create_browser_mock(page_mock: MagicMock | None = None) -> MagicMock:
        """Create a mock Playwright browser."""
        mock_browser = MagicMock()
        mock_context = MagicMock()

        if page_mock is None:
            page_mock = PlaywrightMockFactory.create_page_mock()

        mock_context.new_page = MagicMock(return_value=page_mock)
        mock_browser.new_context = MagicMock(return_value=mock_context)
        mock_browser.close = MagicMock()

        return mock_browser

    @staticmethod
    def create_playwright_mock(browser_mock: MagicMock | None = None) -> MagicMock:
        """Create the full sync_playwright() context manager mock."""
        mock_playwright = MagicMock()

        if browser_mock is None:
            browser_mock = PlaywrightMockFactory.create_browser_mock()

        mock_chromium = MagicMock()
        mock_chromium.launch = MagicMock(return_value=browser_mock)
        mock_playwright.chromium = mock_chromium

        # Context manager support
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_playwright)
        mock_context.__exit__ = MagicMock(return_value=False)

        return mock_context


@pytest.fixture
def playwright_mocks() -> tuple[MagicMock, MagicMock, MagicMock]:
    """
    Create a complete set of Playwright mocks for browser testing.

    Returns:
        Tuple of (playwright_context, browser_mock, page_mock)

    Usage:
        def test_browser_render(playwright_mocks, mocker):
            mock_playwright, mock_browser, mock_page = playwright_mocks
            mocker.patch(
                "glove80_visualizer.kle_renderer.sync_playwright",
                return_value=mock_playwright
            )
            # Test browser-based rendering
    """
    mock_page = PlaywrightMockFactory.create_page_mock()
    mock_browser = PlaywrightMockFactory.create_browser_mock(mock_page)
    mock_playwright = PlaywrightMockFactory.create_playwright_mock(mock_browser)

    return mock_playwright, mock_browser, mock_page


class PILMockFactory:
    """
    Factory for creating PIL/Pillow Image mocks.

    Use this to test image processing code without actual image files.
    """

    @staticmethod
    def create_image_mock(
        mode: str = "RGBA",
        size: tuple[int, int] = (1920, 1200),
    ) -> MagicMock:
        """Create a mock PIL Image with specified mode and size."""
        mock_img = MagicMock()
        mock_img.mode = mode
        mock_img.size = size
        mock_img.save = MagicMock()
        mock_img.convert = MagicMock(return_value=mock_img)

        # For RGBA mode, mock the alpha channel split
        if mode == "RGBA":
            mock_alpha = MagicMock()
            mock_img.split = MagicMock(return_value=(None, None, None, mock_alpha))

        return mock_img

    @staticmethod
    def create_image_module_mock(image_mock: MagicMock | None = None) -> MagicMock:
        """Create a mock PIL.Image module."""
        mock_module = MagicMock()

        if image_mock is None:
            image_mock = PILMockFactory.create_image_mock()

        mock_module.open = MagicMock(return_value=image_mock)
        mock_module.new = MagicMock(return_value=image_mock)

        return mock_module


@pytest.fixture
def pil_image_mock() -> MagicMock:
    """Create a mock PIL Image for testing image operations."""
    return PILMockFactory.create_image_mock()


@pytest.fixture
def pil_module_mock(pil_image_mock: MagicMock) -> MagicMock:
    """Create a mock PIL.Image module for patching."""
    return PILMockFactory.create_image_module_mock(pil_image_mock)


# =============================================================================
# Composite Fixtures for Common Test Scenarios
# =============================================================================


@pytest.fixture
def kle_renderer_mocks(
    playwright_mocks: tuple[MagicMock, MagicMock, MagicMock],
    pil_module_mock: MagicMock,
) -> dict[str, Any]:
    """
    Complete set of mocks for testing kle_renderer.py.

    Returns a dict with all mocks needed for KLE rendering tests:
    - playwright: The sync_playwright context manager mock
    - browser: The browser mock
    - page: The page mock
    - pil_image: The PIL.Image module mock

    Usage:
        def test_kle_render(kle_renderer_mocks, mocker):
            mocker.patch(
                "glove80_visualizer.kle_renderer.sync_playwright",
                return_value=kle_renderer_mocks["playwright"]
            )
    """
    mock_playwright, mock_browser, mock_page = playwright_mocks

    return {
        "playwright": mock_playwright,
        "browser": mock_browser,
        "page": mock_page,
        "pil_image": pil_module_mock,
    }
