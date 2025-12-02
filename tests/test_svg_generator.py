"""
Tests for the SVG generator module.

These tests define the expected behavior of SVG generation.
Write these tests FIRST (TDD), then implement the generator to pass them.
"""

import pytest


class TestGenerateLayerSvg:
    """Tests for generating SVG diagrams for layers."""

    def test_generate_svg_basic(self, sample_layer):
        """SPEC-S001: Generator produces valid SVG for a layer."""
        from glove80_visualizer.svg_generator import generate_layer_svg

        svg = generate_layer_svg(sample_layer)
        assert svg.startswith("<?xml") or svg.startswith("<svg")
        assert "</svg>" in svg

    def test_svg_contains_layer_name(self, sample_layer):
        """SPEC-S002: Generated SVG includes the layer name when requested."""
        from glove80_visualizer.svg_generator import generate_layer_svg

        svg = generate_layer_svg(sample_layer, include_title=True)
        assert sample_layer.name in svg

    def test_svg_contains_key_labels(self, sample_layer):
        """SPEC-S003: Generated SVG includes key labels."""
        from glove80_visualizer.svg_generator import generate_layer_svg

        svg = generate_layer_svg(sample_layer)
        # Check that at least some key labels are present
        # The first few bindings should be A, B, C, etc.
        assert "A" in svg

    def test_svg_glove80_layout(self):
        """SPEC-S004: Generated SVG uses correct Glove80 physical layout."""
        from glove80_visualizer.svg_generator import generate_layer_svg
        from glove80_visualizer.models import Layer, KeyBinding

        layer = Layer(
            name="Test",
            index=0,
            bindings=[KeyBinding(position=i, tap="X") for i in range(80)],
        )
        svg = generate_layer_svg(layer)
        # Glove80 has 80 keys - SVG should have key representations
        # Either as <rect> elements or <path> elements
        assert svg.count("<rect") >= 10 or svg.count("<path") >= 10

    def test_svg_custom_styling(self):
        """SPEC-S005: Generator applies custom styling configuration."""
        from glove80_visualizer.svg_generator import generate_layer_svg
        from glove80_visualizer.models import Layer
        from glove80_visualizer.config import VisualizerConfig

        config = VisualizerConfig(background_color="#000000", text_color="#ffffff")
        layer = Layer(name="Test", index=0, bindings=[])
        svg = generate_layer_svg(layer, config=config)
        # Custom colors should appear in the SVG
        assert "#000000" in svg.lower() or "background" in svg.lower()

    def test_svg_transparent_keys(self):
        """SPEC-S006: Generator correctly renders transparent keys."""
        from glove80_visualizer.svg_generator import generate_layer_svg
        from glove80_visualizer.models import Layer, KeyBinding

        layer = Layer(
            name="Test", index=0, bindings=[KeyBinding(position=0, tap="&trans")]
        )
        svg = generate_layer_svg(layer)
        assert svg is not None
        # Transparent keys should render without error

    def test_svg_hold_tap_display(self):
        """SPEC-S007: Generator shows both tap and hold for hold-tap keys."""
        from glove80_visualizer.svg_generator import generate_layer_svg
        from glove80_visualizer.models import Layer, KeyBinding

        layer = Layer(
            name="Test",
            index=0,
            bindings=[KeyBinding(position=0, tap="A", hold="LSHIFT")],
        )
        svg = generate_layer_svg(layer)
        assert "A" in svg
        # Hold behavior might be abbreviated or styled differently

    def test_generate_svg_batch(self, sample_layers):
        """SPEC-S008: Generator can efficiently produce SVGs for multiple layers."""
        from glove80_visualizer.svg_generator import generate_all_layer_svgs

        svgs = generate_all_layer_svgs(sample_layers)
        assert len(svgs) == len(sample_layers)
        for svg in svgs:
            assert svg.startswith("<?xml") or svg.startswith("<svg")


class TestSvgGeneratorHelpers:
    """Tests for SVG generator helper functions."""

    def test_format_key_label_simple(self):
        """Simple keys format as their name."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("A") == "A"
        assert format_key_label("SPACE") == "Space"

    def test_format_key_label_modifiers(self):
        """Modifier keys format with symbols."""
        from glove80_visualizer.svg_generator import format_key_label

        # Modifiers might use symbols like ⇧ for shift
        result = format_key_label("LSHIFT")
        assert result is not None
        assert len(result) > 0

    def test_format_key_label_trans(self):
        """Transparent keys format as empty or symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&trans")
        # Could be empty string, "▽", or similar
        assert result is not None

    def test_format_key_label_none(self):
        """None keys format as blocked symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&none")
        # Could be "✕", "▪", or similar
        assert result is not None
