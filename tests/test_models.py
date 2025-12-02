"""
Tests for data models.

These tests define the expected behavior of our data structures.
Write these tests FIRST (TDD), then implement the models to pass them.
"""

import pytest


class TestKeyBinding:
    """Tests for the KeyBinding dataclass."""

    def test_key_binding_tap_only(self):
        """SPEC-M001: A KeyBinding can represent a simple key tap."""
        from glove80_visualizer.models import KeyBinding

        binding = KeyBinding(position=0, tap="A")
        assert binding.position == 0
        assert binding.tap == "A"
        assert binding.hold is None

    def test_key_binding_hold_tap(self):
        """SPEC-M002: A KeyBinding can represent a hold-tap behavior."""
        from glove80_visualizer.models import KeyBinding

        binding = KeyBinding(position=5, tap="A", hold="LSHIFT")
        assert binding.tap == "A"
        assert binding.hold == "LSHIFT"

    def test_key_binding_layer_tap(self):
        """SPEC-M003: A KeyBinding can represent a layer-tap behavior."""
        from glove80_visualizer.models import KeyBinding

        binding = KeyBinding(position=10, tap="SPACE", hold="LAYER_Symbol")
        assert binding.hold == "LAYER_Symbol"

    def test_key_binding_transparent(self):
        """SPEC-M004: A KeyBinding can represent a transparent key."""
        from glove80_visualizer.models import KeyBinding

        binding = KeyBinding(position=0, tap="&trans")
        assert binding.tap == "&trans"
        assert binding.is_transparent is True

    def test_key_binding_none(self):
        """SPEC-M005: A KeyBinding can represent a none/blocked key."""
        from glove80_visualizer.models import KeyBinding

        binding = KeyBinding(position=0, tap="&none")
        assert binding.is_none is True

    def test_key_binding_not_transparent_for_normal_key(self):
        """A normal key should not be marked as transparent."""
        from glove80_visualizer.models import KeyBinding

        binding = KeyBinding(position=0, tap="A")
        assert binding.is_transparent is False

    def test_key_binding_not_none_for_normal_key(self):
        """A normal key should not be marked as none."""
        from glove80_visualizer.models import KeyBinding

        binding = KeyBinding(position=0, tap="A")
        assert binding.is_none is False


class TestLayer:
    """Tests for the Layer dataclass."""

    def test_layer_basic(self):
        """SPEC-M010: A Layer has a name, index, and list of bindings."""
        from glove80_visualizer.models import Layer

        layer = Layer(name="QWERTY", index=0, bindings=[])
        assert layer.name == "QWERTY"
        assert layer.index == 0
        assert layer.bindings == []

    def test_layer_binding_count(self):
        """SPEC-M011: A Glove80 layer should have exactly 80 key bindings."""
        from glove80_visualizer.models import Layer, KeyBinding

        bindings = [KeyBinding(position=i, tap="X") for i in range(80)]
        layer = Layer(name="Test", index=0, bindings=bindings)
        assert len(layer.bindings) == 80

    def test_layer_partial_bindings(self):
        """SPEC-M012: Layers can be constructed with partial bindings."""
        from glove80_visualizer.models import Layer

        layer = Layer(name="Test", index=0, bindings=[])
        assert layer.is_complete is False

    def test_layer_complete_with_80_bindings(self):
        """A layer with 80 bindings should be marked complete."""
        from glove80_visualizer.models import Layer, KeyBinding

        bindings = [KeyBinding(position=i, tap="X") for i in range(80)]
        layer = Layer(name="Test", index=0, bindings=bindings)
        assert layer.is_complete is True


class TestVisualizerConfig:
    """Tests for the VisualizerConfig dataclass."""

    def test_config_defaults(self):
        """SPEC-M020: VisualizerConfig has sensible default values."""
        from glove80_visualizer.config import VisualizerConfig

        config = VisualizerConfig()
        assert config.keyboard == "glove80"
        assert config.page_size == "letter"
        assert config.orientation == "landscape"

    def test_config_custom(self):
        """SPEC-M021: VisualizerConfig can be customized."""
        from glove80_visualizer.config import VisualizerConfig

        config = VisualizerConfig(page_size="a4", font_size=14)
        assert config.page_size == "a4"
        assert config.font_size == 14

    def test_config_from_yaml(self, tmp_path):
        """SPEC-M022: VisualizerConfig can be loaded from a YAML string."""
        from glove80_visualizer.config import VisualizerConfig

        yaml_content = "page_size: a4\nfont_size: 16"
        config = VisualizerConfig.from_yaml(yaml_content)
        assert config.page_size == "a4"
        assert config.font_size == 16
