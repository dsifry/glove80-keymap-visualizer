"""
Tests for the layer extractor module.

These tests define the expected behavior of extracting layer information.
Write these tests FIRST (TDD), then implement the extractor to pass them.
"""

import pytest


class TestExtractLayers:
    """Tests for extracting layers from parsed YAML."""

    def test_extract_layers_basic(self):
        """SPEC-E001: Extractor creates Layer objects from YAML."""
        from glove80_visualizer.extractor import extract_layers

        yaml_content = """
layers:
  QWERTY:
    - [A, B, C]
"""
        layers = extract_layers(yaml_content)
        assert len(layers) == 1
        assert layers[0].name == "QWERTY"

    def test_extract_layers_order(self):
        """SPEC-E002: Extractor preserves the order of layers."""
        from glove80_visualizer.extractor import extract_layers

        yaml_content = """
layers:
  First:
    - [A]
  Second:
    - [B]
  Third:
    - [C]
"""
        layers = extract_layers(yaml_content)
        assert [layer.name for layer in layers] == ["First", "Second", "Third"]

    def test_extract_layers_indices(self):
        """SPEC-E003: Extractor assigns correct indices to layers."""
        from glove80_visualizer.extractor import extract_layers

        yaml_content = """
layers:
  Base:
    - [A]
  Upper:
    - [B]
"""
        layers = extract_layers(yaml_content)
        assert layers[0].index == 0
        assert layers[1].index == 1

    def test_extract_key_bindings(self):
        """SPEC-E004: Extractor creates KeyBinding objects for each key."""
        from glove80_visualizer.extractor import extract_layers

        yaml_content = """
layers:
  Test:
    - [Q, W, E, R, T]
"""
        layers = extract_layers(yaml_content)
        assert layers[0].bindings[0].tap == "Q"
        assert layers[0].bindings[4].tap == "T"

    def test_extract_hold_tap(self):
        """SPEC-E005: Extractor parses hold-tap representations."""
        from glove80_visualizer.extractor import extract_layers

        yaml_content = """
layers:
  Test:
    - [{t: A, h: LSHIFT}]
"""
        layers = extract_layers(yaml_content)
        binding = layers[0].bindings[0]
        assert binding.tap == "A"
        assert binding.hold == "LSHIFT"

    def test_extract_empty_layer(self):
        """SPEC-E006: Extractor handles layers with no bindings."""
        from glove80_visualizer.extractor import extract_layers

        yaml_content = """
layers:
  Empty: []
"""
        layers = extract_layers(yaml_content)
        assert layers[0].bindings == []

    def test_extract_filter_by_name(self):
        """SPEC-E007: Extractor can filter to specific layers."""
        from glove80_visualizer.extractor import extract_layers

        yaml_content = """
layers:
  Keep:
    - [A]
  Skip:
    - [B]
"""
        layers = extract_layers(yaml_content, include=["Keep"])
        assert len(layers) == 1
        assert layers[0].name == "Keep"

    def test_extract_exclude_by_name(self):
        """SPEC-E008: Extractor can exclude specific layers."""
        from glove80_visualizer.extractor import extract_layers

        yaml_content = """
layers:
  Keep:
    - [A]
  Skip:
    - [B]
"""
        layers = extract_layers(yaml_content, exclude=["Skip"])
        assert len(layers) == 1
        assert layers[0].name == "Keep"


class TestExtractorEdgeCases:
    """Tests for edge cases in layer extraction."""

    def test_extract_with_trans_keys(self):
        """Extractor handles transparent keys."""
        from glove80_visualizer.extractor import extract_layers

        yaml_content = """
layers:
  Test:
    - [A, trans, B]
"""
        layers = extract_layers(yaml_content)
        assert layers[0].bindings[1].is_transparent is True

    def test_extract_with_none_keys(self):
        """Extractor handles none/blocked keys."""
        from glove80_visualizer.extractor import extract_layers

        yaml_content = """
layers:
  Test:
    - [A, none, B]
"""
        layers = extract_layers(yaml_content)
        assert layers[0].bindings[1].is_none is True

    def test_extract_nested_rows(self):
        """Extractor handles nested row structure."""
        from glove80_visualizer.extractor import extract_layers

        yaml_content = """
layers:
  Test:
    - [A, B, C]
    - [D, E, F]
    - [G, H, I]
"""
        layers = extract_layers(yaml_content)
        # All rows should be flattened into bindings
        assert len(layers[0].bindings) == 9
        assert layers[0].bindings[0].tap == "A"
        assert layers[0].bindings[3].tap == "D"
        assert layers[0].bindings[6].tap == "G"

    def test_extract_include_and_exclude_conflict(self):
        """Extractor handles conflicting include/exclude (include takes precedence)."""
        from glove80_visualizer.extractor import extract_layers

        yaml_content = """
layers:
  A:
    - [X]
  B:
    - [Y]
  C:
    - [Z]
"""
        # Include takes precedence - only A should be included
        layers = extract_layers(yaml_content, include=["A", "B"], exclude=["B"])
        names = [layer.name for layer in layers]
        assert "A" in names
        assert "B" not in names  # Excluded even though in include
