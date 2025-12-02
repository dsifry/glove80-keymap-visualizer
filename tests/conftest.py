"""
Pytest fixtures for glove80-keymap-visualizer tests.
"""

import pytest
from pathlib import Path


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
    from glove80_visualizer.models import Layer, KeyBinding

    bindings = [
        KeyBinding(position=i, tap=chr(65 + (i % 26)))  # A-Z cycling
        for i in range(80)
    ]
    return Layer(name="TestLayer", index=0, bindings=bindings)


@pytest.fixture
def sample_layers():
    """Create multiple sample Layer objects for testing."""
    from glove80_visualizer.models import Layer, KeyBinding

    layers = []
    for layer_idx in range(4):
        bindings = [
            KeyBinding(position=i, tap=chr(65 + ((i + layer_idx) % 26)))
            for i in range(80)
        ]
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
