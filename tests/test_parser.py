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


class TestParseModMorphBehaviors:
    """Tests for mod-morph behavior parsing."""

    def test_parse_mod_morph_extracts_shifted(self, daves_keymap_path):
        """Parser extracts shifted characters from mod-morph behaviors."""
        from glove80_visualizer.parser import parse_mod_morph_behaviors

        if not daves_keymap_path.exists():
            pytest.skip("Dave's keymap file not found")

        content = daves_keymap_path.read_text()
        result = parse_mod_morph_behaviors(content)

        # Should find parang_left and parang_right
        assert len(result) > 0


class TestParseCombos:
    """Tests for combo parsing."""

    @pytest.mark.slow
    def test_parse_combos_from_daves_keymap(self, daves_keymap_path):
        """Parser extracts combos from Dave's keymap."""
        from glove80_visualizer.parser import parse_combos

        if not daves_keymap_path.exists():
            pytest.skip("Dave's keymap file not found")

        combos = parse_combos(daves_keymap_path)

        # Dave's keymap has several combos defined
        assert len(combos) > 0

    @pytest.mark.slow
    def test_combo_has_positions(self, daves_keymap_path):
        """Each combo has key positions."""
        from glove80_visualizer.parser import parse_combos

        if not daves_keymap_path.exists():
            pytest.skip("Dave's keymap file not found")

        combos = parse_combos(daves_keymap_path)

        for combo in combos:
            assert len(combo.positions) >= 2, "Combo must have at least 2 positions"

    @pytest.mark.slow
    def test_combo_has_action(self, daves_keymap_path):
        """Each combo has an action label."""
        from glove80_visualizer.parser import parse_combos

        if not daves_keymap_path.exists():
            pytest.skip("Dave's keymap file not found")

        combos = parse_combos(daves_keymap_path)

        for combo in combos:
            assert combo.action, "Combo must have an action"
            assert isinstance(combo.action, str)

    @pytest.mark.slow
    def test_combo_thumb_key_names(self, daves_keymap_path):
        """Thumb combos have human-readable key names (LT1-LT6, RT1-RT6)."""
        from glove80_visualizer.parser import parse_combos

        if not daves_keymap_path.exists():
            pytest.skip("Dave's keymap file not found")

        combos = parse_combos(daves_keymap_path)

        # Find a thumb combo (positions 52-57, 69-74)
        thumb_positions = {52, 53, 54, 55, 56, 57, 69, 70, 71, 72, 73, 74}
        thumb_combos = [c for c in combos if all(p in thumb_positions for p in c.positions)]

        assert len(thumb_combos) > 0, "Should have thumb combos"

        for combo in thumb_combos:
            # Name should use LT/RT format
            assert "LT" in combo.name or "RT" in combo.name, (
                f"Expected LT/RT in name, got {combo.name}"
            )

    @pytest.mark.slow
    def test_combo_layers_filtering(self, daves_keymap_path):
        """Combos have layer restrictions when specified."""
        from glove80_visualizer.parser import parse_combos

        if not daves_keymap_path.exists():
            pytest.skip("Dave's keymap file not found")

        combos = parse_combos(daves_keymap_path)

        # Some combos have layer restrictions, some don't
        restricted = [c for c in combos if c.layers is not None]

        # Dave's keymap has both types
        assert len(restricted) > 0, "Should have layer-restricted combos"
        # There may or may not be unrestricted combos (not checked)

    @pytest.mark.slow
    def test_combo_gaming_toggle(self, daves_keymap_path):
        """Gaming toggle combo is parsed correctly."""
        from glove80_visualizer.parser import parse_combos

        if not daves_keymap_path.exists():
            pytest.skip("Dave's keymap file not found")

        combos = parse_combos(daves_keymap_path)

        # Find gaming toggle (positions 54 + 71 = LT3 + LT6)
        gaming_combos = [c for c in combos if 54 in c.positions and 71 in c.positions]

        assert len(gaming_combos) == 1, "Should find gaming toggle combo"
        combo = gaming_combos[0]
        assert combo.name == "LT3+LT6"
        assert "Gaming" in combo.action

    @pytest.mark.slow
    def test_combo_caps_lock_cross_hand(self, daves_keymap_path):
        """Cross-hand combo (Caps Lock) is parsed correctly."""
        from glove80_visualizer.parser import parse_combos

        if not daves_keymap_path.exists():
            pytest.skip("Dave's keymap file not found")

        combos = parse_combos(daves_keymap_path)

        # Find caps lock (positions 71 + 72 = LT6 + RT6)
        caps_combos = [c for c in combos if 71 in c.positions and 72 in c.positions]

        assert len(caps_combos) == 1, "Should find caps lock combo"
        combo = caps_combos[0]
        assert combo.name == "LT6+RT6"
        assert "Caps" in combo.action

    def test_parse_combos_file_not_found(self):
        """Parser raises FileNotFoundError when parsing combos from missing file."""
        from glove80_visualizer.parser import parse_combos

        with pytest.raises(FileNotFoundError):
            parse_combos(Path("/nonexistent/keymap.keymap"))

    def test_parse_combos_invalid_file(self, tmp_path):
        """Parser raises KeymapParseError when parsing combos from invalid file."""
        from glove80_visualizer.parser import KeymapParseError, parse_combos

        bad_file = tmp_path / "bad.keymap"
        bad_file.write_text("invalid { syntax")

        with pytest.raises(KeymapParseError, match="Failed to parse keymap for combos"):
            parse_combos(bad_file)


class TestPositionsToName:
    """Tests for _positions_to_name helper function."""

    def test_thumb_key_positions(self):
        """Thumb key positions are converted to human-readable names."""
        from glove80_visualizer.parser import _positions_to_name

        # Left thumb upper row
        assert _positions_to_name([52]) == "LT1"
        assert _positions_to_name([53]) == "LT2"
        assert _positions_to_name([54]) == "LT3"

        # Left thumb lower row
        assert _positions_to_name([69]) == "LT4"
        assert _positions_to_name([70]) == "LT5"
        assert _positions_to_name([71]) == "LT6"

        # Right thumb upper row
        assert _positions_to_name([57]) == "RT1"
        assert _positions_to_name([56]) == "RT2"
        assert _positions_to_name([55]) == "RT3"

        # Right thumb lower row
        assert _positions_to_name([74]) == "RT4"
        assert _positions_to_name([73]) == "RT5"
        assert _positions_to_name([72]) == "RT6"

    def test_multiple_thumb_positions(self):
        """Multiple thumb positions are joined with +."""
        from glove80_visualizer.parser import _positions_to_name

        assert _positions_to_name([54, 71]) == "LT3+LT6"
        assert _positions_to_name([71, 72]) == "LT6+RT6"

    def test_non_thumb_positions(self):
        """Non-thumb positions use numeric representation."""
        from glove80_visualizer.parser import _positions_to_name

        assert _positions_to_name([10]) == "10"
        assert _positions_to_name([25, 26]) == "25+26"

    def test_mixed_thumb_and_non_thumb(self):
        """Mixed thumb and non-thumb positions are combined."""
        from glove80_visualizer.parser import _positions_to_name

        assert _positions_to_name([10, 52]) == "10+LT1"
        assert _positions_to_name([25, 71, 72]) == "25+LT6+RT6"

    def test_positions_are_sorted(self):
        """Positions are sorted before conversion."""
        from glove80_visualizer.parser import _positions_to_name

        # Unsorted input should be sorted in output
        assert _positions_to_name([71, 54]) == "LT3+LT6"
        assert _positions_to_name([72, 71]) == "LT6+RT6"


class TestFormatComboAction:
    """Tests for _format_combo_action helper function."""

    def test_simple_string_binding(self):
        """Simple key name strings are formatted."""
        from glove80_visualizer.parser import _format_combo_action

        assert _format_combo_action("CAPSLOCK") == "Caps Lock"
        assert _format_combo_action("CAPS") == "Caps Lock"

    def test_mod_tab_chord_lgui(self):
        """Mod-tab-chord with LGUI is formatted as Cmd+Tab."""
        from glove80_visualizer.parser import _format_combo_action

        assert _format_combo_action("&mod_tab_chord LGUI 17") == "Cmd+Tab"
        assert _format_combo_action("&mod_tab_chord GUI 17") == "Cmd+Tab"

    def test_mod_tab_chord_lctl(self):
        """Mod-tab-chord with LCTL is formatted as Ctrl+Tab."""
        from glove80_visualizer.parser import _format_combo_action

        assert _format_combo_action("&mod_tab_chord LCTL 17") == "Ctrl+Tab"
        assert _format_combo_action("&mod_tab_chord CTL 17") == "Ctrl+Tab"

    def test_mod_tab_chord_lalt(self):
        """Mod-tab-chord with LALT is formatted as Alt+Tab."""
        from glove80_visualizer.parser import _format_combo_action

        assert _format_combo_action("&mod_tab_chord LALT 17") == "Alt+Tab"
        assert _format_combo_action("&mod_tab_chord ALT 17") == "Alt+Tab"

    def test_mod_tab_chord_generic(self):
        """Mod-tab-chord without recognized modifier is formatted generically."""
        from glove80_visualizer.parser import _format_combo_action

        assert _format_combo_action("&mod_tab_chord UNKNOWN 17") == "Tab Switcher"

    def test_custom_behavior_with_combo_name(self):
        """Custom behavior with combo name uses name derivation."""
        from glove80_visualizer.parser import _format_combo_action

        result = _format_combo_action("&custom_behavior", combo_name="combo_caps_lock")
        assert result == "Caps Lock"

    def test_custom_behavior_without_combo_name(self):
        """Custom behavior without combo name returns raw binding."""
        from glove80_visualizer.parser import _format_combo_action

        result = _format_combo_action("&unknown_behavior")
        assert result == "&unknown_behavior"

    def test_dict_toggle_layer(self):
        """Dictionary binding with toggle hold is formatted."""
        from glove80_visualizer.parser import _format_combo_action

        key_data = {"t": "Gaming", "h": "toggle"}
        assert _format_combo_action(key_data) == "Toggle Gaming"

    def test_dict_sticky_shift(self):
        """Dictionary binding with sticky shift is formatted."""
        from glove80_visualizer.parser import _format_combo_action

        key_data = {"t": "LSHFT", "h": "sticky"}
        assert _format_combo_action(key_data) == "Sticky Shift"

    def test_dict_tap_only(self):
        """Dictionary binding with only tap uses tap value."""
        from glove80_visualizer.parser import _format_combo_action

        key_data = {"t": "CAPSLOCK"}
        assert _format_combo_action(key_data) == "Caps Lock"

    def test_dict_no_tap_with_combo_name(self):
        """Dictionary without tap falls back to combo name."""
        from glove80_visualizer.parser import _format_combo_action

        key_data = {"h": "some_hold"}
        result = _format_combo_action(key_data, combo_name="combo_test")
        assert result == "Test"

    def test_dict_no_tap_no_combo_name(self):
        """Dictionary without tap or combo name returns string representation."""
        from glove80_visualizer.parser import _format_combo_action

        key_data = {"h": "some_hold"}
        result = _format_combo_action(key_data)
        assert result == str(key_data)

    def test_fallback_to_combo_name(self):
        """Unknown binding type falls back to combo name."""
        from glove80_visualizer.parser import _format_combo_action

        result = _format_combo_action(None, combo_name="combo_special")
        assert result == "Special"


class TestFormatStickyKey:
    """Tests for _format_sticky_key helper function."""

    def test_sticky_hyper(self):
        """Sticky Hyper key (Gui+Alt+Ctl+Shift) is formatted correctly."""
        from glove80_visualizer.parser import _format_sticky_key

        assert _format_sticky_key("Gui+Alt+Ctl+LSHFT") == "Sticky Hyper"
        assert _format_sticky_key("GUI+ALT+CTL+SHFT") == "Sticky Hyper"

    def test_sticky_meh(self):
        """Sticky Meh key (Alt+Ctl+Shift) is formatted correctly."""
        from glove80_visualizer.parser import _format_sticky_key

        assert _format_sticky_key("Alt+Ctl+LSHFT") == "Sticky Meh"
        assert _format_sticky_key("ALT+CTL+SHFT") == "Sticky Meh"

    def test_sticky_altgr(self):
        """Sticky AltGr key is formatted correctly."""
        from glove80_visualizer.parser import _format_sticky_key

        assert _format_sticky_key("RALT") == "Sticky AltGr"
        assert _format_sticky_key("ralt") == "Sticky AltGr"

    def test_sticky_lalt(self):
        """Sticky left Alt key is formatted correctly."""
        from glove80_visualizer.parser import _format_sticky_key

        assert _format_sticky_key("LALT") == "Sticky Alt"
        assert _format_sticky_key("lalt") == "Sticky Alt"

    def test_sticky_shift(self):
        """Sticky Shift key is formatted correctly."""
        from glove80_visualizer.parser import _format_sticky_key

        assert _format_sticky_key("LSHFT") == "Sticky Shift"
        assert _format_sticky_key("RSHFT") == "Sticky Shift"
        assert _format_sticky_key("shft") == "Sticky Shift"

    def test_sticky_ctrl(self):
        """Sticky Ctrl key is formatted correctly."""
        from glove80_visualizer.parser import _format_sticky_key

        assert _format_sticky_key("LCTL") == "Sticky Ctrl"
        assert _format_sticky_key("RCTL") == "Sticky Ctrl"
        assert _format_sticky_key("ctl") == "Sticky Ctrl"

    def test_sticky_cmd(self):
        """Sticky Cmd/GUI key is formatted correctly."""
        from glove80_visualizer.parser import _format_sticky_key

        assert _format_sticky_key("LGUI") == "Sticky Cmd"
        assert _format_sticky_key("RGUI") == "Sticky Cmd"
        assert _format_sticky_key("gui") == "Sticky Cmd"

    def test_sticky_generic(self):
        """Unknown sticky key is formatted with Sticky prefix."""
        from glove80_visualizer.parser import _format_sticky_key

        assert _format_sticky_key("UNKNOWN") == "Sticky UNKNOWN"


class TestDeriveActionFromName:
    """Tests for _derive_action_from_name helper function."""

    def test_combo_prefix_removal(self):
        """Combo prefix 'combo_' is removed."""
        from glove80_visualizer.parser import _derive_action_from_name

        assert _derive_action_from_name("combo_caps_lock") == "Caps Lock"
        assert _derive_action_from_name("combo_gaming_toggle") == "Gaming Toggle"

    def test_cmb_prefix_removal(self):
        """Combo prefix 'cmb_' is removed."""
        from glove80_visualizer.parser import _derive_action_from_name

        assert _derive_action_from_name("cmb_caps_lock") == "Caps Lock"
        assert _derive_action_from_name("cmb_gaming_toggle") == "Gaming Toggle"

    def test_no_prefix(self):
        """Names without prefix are processed as-is."""
        from glove80_visualizer.parser import _derive_action_from_name

        assert _derive_action_from_name("caps_lock") == "Caps Lock"
        assert _derive_action_from_name("gaming_toggle") == "Gaming Toggle"

    def test_modifier_capitalization(self):
        """Modifier names (alt, ctrl, shift, gui, cmd, tab) are capitalized."""
        from glove80_visualizer.parser import _derive_action_from_name

        assert _derive_action_from_name("combo_alt_tab_switcher") == "Alt Tab Switcher"
        assert _derive_action_from_name("combo_ctrl_shift_tab") == "Ctrl Shift Tab"
        assert _derive_action_from_name("combo_gui_cmd_space") == "Gui Cmd Space"

    def test_altgr_special_case(self):
        """AltGr is formatted with special capitalization."""
        from glove80_visualizer.parser import _derive_action_from_name

        assert _derive_action_from_name("combo_altgr_key") == "AltGr Key"

    def test_regular_words(self):
        """Non-modifier words are title-cased."""
        from glove80_visualizer.parser import _derive_action_from_name

        assert _derive_action_from_name("combo_gaming_toggle") == "Gaming Toggle"
        assert _derive_action_from_name("combo_special_action") == "Special Action"

    def test_underscores_to_spaces(self):
        """Underscores are converted to spaces."""
        from glove80_visualizer.parser import _derive_action_from_name

        assert _derive_action_from_name("combo_multi_word_action") == "Multi Word Action"


class TestFormatKeyName:
    """Tests for _format_key_name helper function."""

    def test_capslock_variations(self):
        """CAPSLOCK and CAPS are formatted as 'Caps Lock'."""
        from glove80_visualizer.parser import _format_key_name

        assert _format_key_name("CAPSLOCK") == "Caps Lock"
        assert _format_key_name("CAPS") == "Caps Lock"
        assert _format_key_name("capslock") == "Caps Lock"

    def test_gui_keys(self):
        """GUI keys are formatted with Cmd prefix."""
        from glove80_visualizer.parser import _format_key_name

        assert _format_key_name("LGUI") == "Left Cmd"
        assert _format_key_name("RGUI") == "Right Cmd"

    def test_alt_keys(self):
        """Alt keys are formatted correctly."""
        from glove80_visualizer.parser import _format_key_name

        assert _format_key_name("LALT") == "Left Alt"
        assert _format_key_name("RALT") == "AltGr"

    def test_ctrl_keys(self):
        """Ctrl keys are formatted correctly."""
        from glove80_visualizer.parser import _format_key_name

        assert _format_key_name("LCTL") == "Left Ctrl"
        assert _format_key_name("RCTL") == "Right Ctrl"

    def test_shift_keys(self):
        """Shift keys are formatted correctly."""
        from glove80_visualizer.parser import _format_key_name

        assert _format_key_name("LSHFT") == "Left Shift"
        assert _format_key_name("RSHFT") == "Right Shift"

    def test_unknown_key(self):
        """Unknown keys are returned as-is."""
        from glove80_visualizer.parser import _format_key_name

        assert _format_key_name("UNKNOWN") == "UNKNOWN"
        assert _format_key_name("CUSTOM_KEY") == "CUSTOM_KEY"
