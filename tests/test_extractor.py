"""
Tests for the layer extractor module.

These tests define the expected behavior of extracting layer information.
Write these tests FIRST (TDD), then implement the extractor to pass them.
"""


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

    def test_extract_empty_yaml_returns_empty_list(self):
        """Extractor returns empty list for empty YAML."""
        from glove80_visualizer.extractor import extract_layers

        layers = extract_layers("")
        assert layers == []

    def test_extract_no_layers_key_returns_empty_list(self):
        """Extractor returns empty list when layers key is missing."""
        from glove80_visualizer.extractor import extract_layers

        yaml_content = """
other_key: value
"""
        layers = extract_layers(yaml_content)
        assert layers == []

    def test_extract_single_key_not_list(self):
        """Extractor handles single key that's not in a list."""
        from glove80_visualizer.extractor import extract_layers

        yaml_content = """
layers:
  Test:
    - A
    - B
    - C
"""
        layers = extract_layers(yaml_content)
        # Non-list items are appended directly
        assert len(layers[0].bindings) == 3

    def test_extract_numeric_key_data(self):
        """Extractor handles numeric key data (fallback to string)."""
        from glove80_visualizer.extractor import extract_layers

        yaml_content = """
layers:
  Test:
    - [123, 456]
"""
        layers = extract_layers(yaml_content)
        assert layers[0].bindings[0].tap == "123"
        assert layers[0].bindings[1].tap == "456"

    def test_extract_dict_with_tap_key(self):
        """Extractor handles dict with 'tap' key instead of 't'."""
        from glove80_visualizer.extractor import extract_layers

        yaml_content = """
layers:
  Test:
    - [{tap: A, hold: LSHIFT}]
"""
        layers = extract_layers(yaml_content)
        binding = layers[0].bindings[0]
        assert binding.tap == "A"
        assert binding.hold == "LSHIFT"

    def test_extract_dict_with_none_tap(self):
        """Extractor handles dict with None tap value."""
        from glove80_visualizer.extractor import extract_layers

        yaml_content = """
layers:
  Test:
    - [{t: null, h: LSHIFT}]
"""
        layers = extract_layers(yaml_content)
        binding = layers[0].bindings[0]
        assert binding.tap == ""

    def test_extract_dict_with_type_field(self):
        """Extractor handles dict with type field."""
        from glove80_visualizer.extractor import extract_layers

        yaml_content = """
layers:
  Test:
    - [{t: trans, type: trans}]
"""
        layers = extract_layers(yaml_content)
        binding = layers[0].bindings[0]
        assert binding.key_type == "trans"


class TestLayerActivatorExtraction:
    """Tests for extracting layer activators."""

    def test_extract_layer_activator_from_hold(self):
        """SPEC-HK-002: Extract activators from hold behaviors."""
        from glove80_visualizer.extractor import extract_layer_activators

        yaml_content = """
layers:
  Base:
    - [{t: BACKSPACE, h: Cursor}, {t: SPACE, h: Symbol}]
  Cursor:
    - [{type: held}, A]
  Symbol:
    - [B, {type: held}]
"""
        activators = extract_layer_activators(yaml_content)

        assert len(activators) == 2
        cursor_activator = next(a for a in activators if a.target_layer_name == "Cursor")
        assert cursor_activator.source_layer_name == "Base"
        assert cursor_activator.tap_key == "BACKSPACE"

    def test_multiple_activators_same_layer(self):
        """SPEC-HK-003: Multiple activators for one layer."""
        from glove80_visualizer.extractor import extract_layer_activators

        yaml_content = """
layers:
  Base:
    - [{t: TAB, h: Mouse}, {t: ENTER, h: Mouse}]
  Mouse:
    - [{type: held}, {type: held}]
"""
        activators = extract_layer_activators(yaml_content)
        mouse_activators = [a for a in activators if a.target_layer_name == "Mouse"]

        assert len(mouse_activators) == 2

    def test_layer_without_activator(self):
        """SPEC-HK-004: Layers without activators handled gracefully."""
        from glove80_visualizer.extractor import extract_layer_activators

        yaml_content = """
layers:
  Base:
    - [A, B, C]
  Orphan:
    - [X, Y, Z]
"""
        activators = extract_layer_activators(yaml_content)
        # Should not raise, just return empty or no activator for Orphan
        orphan_activators = [a for a in activators if a.target_layer_name == "Orphan"]
        assert len(orphan_activators) == 0

    def test_extract_activators_empty_yaml(self):
        """Extract activators returns empty list for empty YAML."""
        from glove80_visualizer.extractor import extract_layer_activators

        activators = extract_layer_activators("")
        assert activators == []

    def test_extract_activators_no_hold_behaviors(self):
        """Extract activators returns empty list when no hold behaviors exist."""
        from glove80_visualizer.extractor import extract_layer_activators

        yaml_content = """
layers:
  Base:
    - [A, B, C]
"""
        activators = extract_layer_activators(yaml_content)
        assert activators == []

    def test_extract_activators_no_layers_key(self):
        """Extract activators returns empty list when no layers key exists."""
        from glove80_visualizer.extractor import extract_layer_activators

        yaml_content = "other_key: value"
        activators = extract_layer_activators(yaml_content)
        assert activators == []

    def test_extract_activators_empty_layer(self):
        """Extract activators handles empty layers gracefully."""
        from glove80_visualizer.extractor import extract_layer_activators

        yaml_content = """
layers:
  Base:
  Cursor:
    - [{type: held}]
"""
        activators = extract_layer_activators(yaml_content)
        # Should not raise, Base layer is empty
        assert activators == []

    def test_extract_activators_null_tap(self):
        """Extract activators handles null tap key."""
        from glove80_visualizer.extractor import extract_layer_activators

        yaml_content = """
layers:
  Base:
    - [{t: null, h: Cursor}]
  Cursor:
    - [{type: held}]
"""
        activators = extract_layer_activators(yaml_content)
        assert len(activators) == 1
        assert activators[0].tap_key is None
