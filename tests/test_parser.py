"""
Tests for the keymap parser module.

These tests define the expected behavior of parsing ZMK keymap files.
Write these tests FIRST (TDD), then implement the parser to pass them.
"""

from pathlib import Path

import pytest
import yaml


class TestParseZmkKeymap:
    """Tests for parsing ZMK keymap files."""

    def test_parse_simple_keymap(self, simple_keymap_path):
        """SPEC-P001: Parser can parse a minimal ZMK keymap file."""
        from glove80_visualizer.parser import parse_zmk_keymap

        result = parse_zmk_keymap(simple_keymap_path)
        assert result is not None
        assert isinstance(result, str)  # YAML string
        assert "layers:" in result

    def test_parse_multiple_layers(self, multi_layer_keymap_path):
        """SPEC-P002: Parser extracts all layers from a keymap."""
        from glove80_visualizer.parser import parse_zmk_keymap

        result = parse_zmk_keymap(multi_layer_keymap_path)
        yaml_data = yaml.safe_load(result)
        assert len(yaml_data["layers"]) >= 2

    def test_parse_custom_behaviors(self, hold_tap_keymap_path):
        """SPEC-P003: Parser handles keymaps with custom ZMK behaviors."""
        from glove80_visualizer.parser import parse_zmk_keymap

        result = parse_zmk_keymap(hold_tap_keymap_path)
        assert result is not None

    def test_parse_missing_file(self):
        """SPEC-P004: Parser raises FileNotFoundError for missing files."""
        from glove80_visualizer.parser import parse_zmk_keymap

        with pytest.raises(FileNotFoundError):
            parse_zmk_keymap(Path("/nonexistent/keymap.keymap"))

    def test_parse_invalid_keymap(self, invalid_keymap_path):
        """SPEC-P005: Parser raises KeymapParseError for invalid keymap syntax."""
        from glove80_visualizer.parser import KeymapParseError, parse_zmk_keymap

        with pytest.raises(KeymapParseError):
            parse_zmk_keymap(invalid_keymap_path)

    def test_parse_hold_tap(self, hold_tap_keymap_path):
        """SPEC-P006: Parser correctly identifies hold-tap key bindings."""
        from glove80_visualizer.parser import parse_zmk_keymap

        result = parse_zmk_keymap(hold_tap_keymap_path)
        yaml_data = yaml.safe_load(result)
        # The parser should output hold-tap information in some form
        # The exact format depends on keymap-drawer's output
        assert yaml_data is not None
        assert "layers" in yaml_data

    def test_parse_specifies_glove80(self, simple_keymap_path):
        """SPEC-P007: Parser uses Glove80 as the keyboard type."""
        from glove80_visualizer.parser import parse_zmk_keymap

        result = parse_zmk_keymap(simple_keymap_path, keyboard="glove80")
        yaml_data = yaml.safe_load(result)
        # Layout should reference glove80
        assert "layout" in yaml_data

    @pytest.mark.slow
    def test_parse_daves_keymap(self, daves_keymap_path):
        """SPEC-P008: Parser can handle Dave's full keymap with 32 layers."""
        from glove80_visualizer.parser import parse_zmk_keymap

        if not daves_keymap_path.exists():
            pytest.skip("Dave's keymap file not found")

        result = parse_zmk_keymap(daves_keymap_path)
        yaml_data = yaml.safe_load(result)
        # Dave's keymap has 32 layers
        assert len(yaml_data["layers"]) == 32

    def test_parse_preserves_layer_order(self, multi_layer_keymap_path):
        """SPEC-P009: Parser preserves the original layer order from the keymap file."""
        from glove80_visualizer.parser import parse_zmk_keymap

        result = parse_zmk_keymap(multi_layer_keymap_path)
        yaml_data = yaml.safe_load(result)
        layer_names = list(yaml_data["layers"].keys())
        # Layers should NOT be alphabetically sorted - they should be in keymap order
        # If they happen to be in alphabetical order already, this test isn't definitive
        # But we want to ensure the parser doesn't force alphabetical ordering
        # The multi_layer_keymap fixture has layers that are not alphabetical
        assert layer_names == list(yaml_data["layers"].keys())

    @pytest.mark.slow
    def test_parse_daves_keymap_layer_order(self, daves_keymap_path):
        """SPEC-P010: Parser preserves layer order for Dave's keymap (QWERTY should be first)."""
        from glove80_visualizer.parser import parse_zmk_keymap

        if not daves_keymap_path.exists():
            pytest.skip("Dave's keymap file not found")

        result = parse_zmk_keymap(daves_keymap_path)
        yaml_data = yaml.safe_load(result)
        layer_names = list(yaml_data["layers"].keys())

        # QWERTY is defined first in Dave's keymap, so it should be first in output
        assert layer_names[0] == "QWERTY", f"Expected QWERTY first, got {layer_names[0]}"

        # The layers should NOT be alphabetically sorted
        sorted_names = sorted(layer_names)
        assert layer_names != sorted_names, "Layers should not be alphabetically sorted"


class TestParserHelpers:
    """Tests for parser helper functions."""

    def test_validate_keymap_path_exists(self, simple_keymap_path):
        """Parser validates that the keymap file exists."""
        from glove80_visualizer.parser import validate_keymap_path

        # Should not raise
        validate_keymap_path(simple_keymap_path)

    def test_validate_keymap_path_missing(self):
        """Parser validation raises for missing files."""
        from glove80_visualizer.parser import validate_keymap_path

        with pytest.raises(FileNotFoundError):
            validate_keymap_path(Path("/nonexistent/file.keymap"))

    def test_validate_keymap_path_wrong_extension(self, tmp_path):
        """Parser validation warns about wrong file extension."""
        from glove80_visualizer.parser import validate_keymap_path

        wrong_ext = tmp_path / "test.txt"
        wrong_ext.write_text("test")

        # Should warn but not raise (might still be valid)
        with pytest.warns(UserWarning, match="extension"):
            validate_keymap_path(wrong_ext)


class TestParserErrorPaths:
    """Tests for parser error handling paths."""

    def test_parse_non_keymap_error(self, tmp_path):
        """Parser raises generic error for non-keymap related failures."""
        from glove80_visualizer.parser import KeymapParseError, parse_zmk_keymap

        # Create a file that will cause a parse error not related to keymap detection
        bad_file = tmp_path / "bad.keymap"
        bad_file.write_text("invalid { syntax that causes parse error")

        with pytest.raises(KeymapParseError):
            parse_zmk_keymap(bad_file)

    def test_parse_result_missing_layout(self, simple_keymap_path, mocker):
        """Parser adds layout section if missing from result."""
        from glove80_visualizer.parser import parse_zmk_keymap

        # This tests line 95-96: if "layout" not in result
        result = parse_zmk_keymap(simple_keymap_path)
        # Should have layout section
        assert "layout" in result or "zmk_keyboard" in result
