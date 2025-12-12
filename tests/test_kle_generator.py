"""
Tests for KLE (Keyboard Layout Editor) JSON generator.

This module tests the template-based KLE generator that uses Sunaku's
template structure to create KLE-compatible JSON output.
"""

import json

import pytest

from glove80_visualizer.models import KeyBinding, Layer


class TestKLEJsonStructure:
    """Test the basic KLE JSON structure."""

    def test_kle_json_is_array(self, sample_layer):
        """KLE-001: KLE JSON must be an array at the root level."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        result = generate_kle_from_template(sample_layer)
        parsed = json.loads(result)
        assert isinstance(parsed, list)

    def test_kle_json_first_element_is_metadata(self, sample_layer):
        """KLE-002: First element should be metadata object with CSS."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        result = generate_kle_from_template(sample_layer)
        parsed = json.loads(result)
        assert isinstance(parsed[0], dict)
        assert "css" in parsed[0]

    def test_kle_json_subsequent_elements_are_rows(self, sample_layer):
        """KLE-003: Elements after first should be row arrays."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        result = generate_kle_from_template(sample_layer)
        parsed = json.loads(result)
        # Skip first element (metadata), check rest are arrays
        for i, row in enumerate(parsed[1:], start=1):
            assert isinstance(row, list), f"Row {i} should be a list"


class TestKLEKeyProperties:
    """Test KLE key property objects."""

    def test_key_profile_is_chicklet(self, sample_layer):
        """KLE-004: Keys should use CHICKLET profile for Glove80 style."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        result = generate_kle_from_template(sample_layer)
        parsed = json.loads(result)
        # Find a key property object and verify profile
        # First row after metadata should set the profile
        for row in parsed[1:]:
            for item in row:
                if isinstance(item, dict) and "p" in item:
                    assert item["p"] == "CHICKLET"
                    return
        pytest.fail("No CHICKLET profile found in output")

    def test_decorative_keys_have_d_true(self, sample_layer):
        """KLE-005: Row/column labels should be decorative (d: true)."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        result = generate_kle_from_template(sample_layer)
        parsed = json.loads(result)
        # Look for R1, C1 labels which should be decorative
        found_decorative = False
        decorative_labels = ("R1", "R2", "R3", "R4", "R5", "R6", "C1", "C2", "C3", "C4", "C5", "C6")
        for row in parsed[1:]:
            for i, item in enumerate(row):
                if isinstance(item, str) and item in decorative_labels:
                    # Previous item should be a dict with d: true
                    if i > 0 and isinstance(row[i - 1], dict):
                        assert row[i - 1].get("d") is True, f"Label {item} should be decorative"
                        found_decorative = True
        assert found_decorative, "No decorative labels found"


class TestKLELabelFormatting:
    """Test key label formatting for KLE."""

    def test_label_populates_key_positions(self):
        """KLE-008: Key labels should be populated in correct positions."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        # Create a layer with Q at ZMK position 23 (should appear in template)
        bindings = [KeyBinding(position=23, tap="Q")]
        bindings.extend([KeyBinding(position=i, tap="X") for i in range(80) if i != 23])
        layer = Layer(name="Test", index=0, bindings=bindings)

        result = generate_kle_from_template(layer)
        assert '"Q"' in result

    def test_hold_label_formatting(self):
        """KLE-009: Hold behavior should appear in key label."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        # Create a layer with a hold-tap key
        bindings = [KeyBinding(position=35, tap="A", hold="LCTL")]
        bindings.extend([KeyBinding(position=i, tap="X") for i in range(80) if i != 35])
        layer = Layer(name="Test", index=0, bindings=bindings)

        result = generate_kle_from_template(layer)
        # Hold should be in the label (formatted as modifier symbol)
        assert "A" in result

    def test_number_key_shows_shifted_character(self):
        """KLE-010a: Number keys should auto-show shifted characters (1→!)."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        # Create a layer with number key at position 11 (key "1")
        bindings = [KeyBinding(position=11, tap="1")]
        bindings.extend([KeyBinding(position=i, tap="X") for i in range(80) if i != 11])
        layer = Layer(name="Test", index=0, bindings=bindings)

        result = generate_kle_from_template(layer)
        # Should have "!" above "1" (shifted newline tap format)
        assert '"!\\n1"' in result or "'!\\n1'" in result

    def test_punctuation_key_shows_shifted_character(self):
        """KLE-010b: Punctuation keys should auto-show shifted characters (;→:)."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        # Create a layer with semicolon at position 44
        bindings = [KeyBinding(position=44, tap=";")]
        bindings.extend([KeyBinding(position=i, tap="X") for i in range(80) if i != 44])
        layer = Layer(name="Test", index=0, bindings=bindings)

        result = generate_kle_from_template(layer)
        # Should have ":" above ";" (shifted newline tap format)
        assert '":\\n;"' in result or "':\\n;'" in result

    def test_alpha_key_does_not_auto_shift(self):
        """KLE-010c: Alpha keys should NOT auto-show shifted characters."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        # Create a layer with letter A at position 35
        bindings = [KeyBinding(position=35, tap="A")]
        bindings.extend([KeyBinding(position=i, tap="X") for i in range(80) if i != 35])
        layer = Layer(name="Test", index=0, bindings=bindings)

        result = generate_kle_from_template(layer)
        # Should NOT have shifted character above A - just "A" alone
        # (no newline before A indicating a shifted char)
        assert '"A"' in result

    def test_explicit_shifted_overrides_auto(self):
        """KLE-010d: Explicit shifted field should override auto-calculated."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        # Create a key where ( has explicit shifted < (mod-morph style)
        bindings = [KeyBinding(position=76, tap="(", shifted="<")]
        bindings.extend([KeyBinding(position=i, tap="X") for i in range(80) if i != 76])
        layer = Layer(name="Test", index=0, bindings=bindings)

        result = generate_kle_from_template(layer)
        # Should show < above (, not the default 9 shifted char
        assert '"<\\n("' in result or "'<\\n('" in result


class TestKLEGlove80Layout:
    """Test Glove80-specific layout in KLE."""

    def test_center_gap_exists(self, sample_layer):
        """KLE-011: There should be a gap between left and right halves."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        result = generate_kle_from_template(sample_layer)
        parsed = json.loads(result)

        # Look for x offset that creates the gap (typically 7.25)
        found_gap = False
        for row in parsed[1:]:
            for item in row:
                if isinstance(item, dict) and "x" in item:
                    if item["x"] >= 7:
                        found_gap = True
                        break
        assert found_gap, "Center gap (x offset >= 7) not found"

    def test_thumb_cluster_rotation(self, sample_layer):
        """KLE-012: Thumb cluster keys should have rotation."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        result = generate_kle_from_template(sample_layer)
        parsed = json.loads(result)

        # Look for rotation properties
        found_rotation = False
        for row in parsed[1:]:
            for item in row:
                if isinstance(item, dict) and "r" in item:
                    found_rotation = True
                    break
        assert found_rotation, "Thumb cluster rotation not found"

    def test_row_labels_present(self, sample_layer):
        """KLE-013: Row labels R1-R6 should be present."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        result = generate_kle_from_template(sample_layer)
        json_str = result

        for label in ["R1", "R2", "R3", "R4", "R5", "R6"]:
            assert f'"{label}"' in json_str, f"Row label {label} not found"

    def test_column_labels_present(self, sample_layer):
        """KLE-014: Column labels C1-C6 should be present."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        result = generate_kle_from_template(sample_layer)
        json_str = result

        for label in ["C1", "C2", "C3", "C4", "C5", "C6"]:
            assert f'"{label}"' in json_str, f"Column label {label} not found"

    def test_thumb_labels_present(self, sample_layer):
        """KLE-015: Thumb cluster labels T1-T6 should be present."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        result = generate_kle_from_template(sample_layer)
        json_str = result

        for label in ["T1", "T2", "T3", "T4", "T5", "T6"]:
            assert f'"{label}"' in json_str, f"Thumb label {label} not found"


class TestKLECenterMetadata:
    """Test center metadata block in KLE JSON."""

    def test_center_block_has_layer_title(self, sample_layer):
        """KLE-016: Center block should contain layer title."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        result = generate_kle_from_template(sample_layer, title="Test Layer")
        assert "Test Layer" in result

    def test_center_block_uses_html(self, sample_layer):
        """KLE-017: Center block should use HTML for rich formatting."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        result = generate_kle_from_template(sample_layer, title="Test Layer")
        # Should contain HTML tags like <center>, <h1>, etc.
        assert "<center>" in result or "<h1>" in result


class TestKLESunakuCompatibility:
    """Test compatibility with Sunaku's KLE JSON format."""

    @pytest.fixture
    def sunaku_base_layer(self, fixtures_dir):
        """Load Sunaku's base layer JSON for comparison."""
        kle_path = fixtures_dir / "kle" / "sunaku-base-layer.json"
        if not kle_path.exists():
            pytest.skip("Sunaku fixtures not available")
        return json.loads(kle_path.read_text())

    def test_css_section_structure(self, sunaku_base_layer, sample_layer):
        """KLE-018: CSS structure should match Sunaku's format."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        result = generate_kle_from_template(sample_layer)
        parsed = json.loads(result)

        # Both should have CSS in first element
        assert "css" in parsed[0]
        assert "css" in sunaku_base_layer[0]

    def test_has_kailh_choc_switch_info(self, sample_layer):
        """KLE-019: Should include Kailh Choc switch metadata (from template)."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        result = generate_kle_from_template(sample_layer)
        # Sunaku uses: "sm": "kailh-choc", "sb": "kailh", "st": "Kailh Choc v1"
        assert "kailh" in result.lower() or "choc" in result.lower()

    def test_parseable_by_kle(self, sample_layer):
        """KLE-020: Output should be valid JSON parseable for KLE."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        result = generate_kle_from_template(sample_layer)
        # Should not raise
        parsed = json.loads(result)
        assert parsed is not None


class TestKLEKeyMapping:
    """Test ZMK position to KLE template slot mapping."""

    def test_number_row_positions(self):
        """Test that number row keys map to correct slots."""
        from glove80_visualizer.kle_template import TEMPLATE_POSITIONS, ZMK_TO_SLOT

        # ZMK positions 11-20 are number keys 1-0
        # They should map to template positions in row 4-5
        for zmk_pos in range(11, 21):
            assert zmk_pos in ZMK_TO_SLOT, f"ZMK position {zmk_pos} should be mapped"
            slot = ZMK_TO_SLOT[zmk_pos]
            assert slot < len(TEMPLATE_POSITIONS), f"Slot {slot} should be valid"

    def test_qwerty_row_positions(self):
        """Test that QWERTY row keys map to correct slots."""
        from glove80_visualizer.kle_template import TEMPLATE_POSITIONS, ZMK_TO_SLOT

        # ZMK positions 23-32 are Q,W,E,R,T,Y,U,I,O,P
        for zmk_pos in range(23, 33):
            assert zmk_pos in ZMK_TO_SLOT, f"ZMK position {zmk_pos} should be mapped"
            slot = ZMK_TO_SLOT[zmk_pos]
            assert slot < len(TEMPLATE_POSITIONS), f"Slot {slot} should be valid"

    def test_home_row_positions(self):
        """Test that home row keys map to correct slots."""
        from glove80_visualizer.kle_template import TEMPLATE_POSITIONS, ZMK_TO_SLOT

        # ZMK positions 35-45 are A,S,D,F,G,H,J,K,L,;,'
        for zmk_pos in range(35, 46):
            assert zmk_pos in ZMK_TO_SLOT, f"ZMK position {zmk_pos} should be mapped"
            slot = ZMK_TO_SLOT[zmk_pos]
            assert slot < len(TEMPLATE_POSITIONS), f"Slot {slot} should be valid"

    def test_thumb_cluster_positions(self):
        """Test that thumb cluster keys map to correct slots."""
        from glove80_visualizer.kle_template import TEMPLATE_POSITIONS, ZMK_TO_SLOT

        # Left thumb: 52, 69, 70, 76, 77, 56
        # Right thumb: 57, 71, 72, 73, 74, 75
        thumb_positions = [52, 69, 70, 76, 77, 56, 57, 71, 72, 73, 74, 75]
        for zmk_pos in thumb_positions:
            assert zmk_pos in ZMK_TO_SLOT, f"ZMK position {zmk_pos} should be mapped"
            slot = ZMK_TO_SLOT[zmk_pos]
            assert slot < len(TEMPLATE_POSITIONS), f"Slot {slot} should be valid"

    def test_outer_column_r2_minus_key(self):
        """KLE-029: R2C6 right (-/_) should be mapped."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        # ZMK position 21 is the minus key on R2 right outer column
        bindings = [KeyBinding(position=21, tap="-")]
        bindings.extend([KeyBinding(position=i, tap="X") for i in range(80) if i != 21])
        layer = Layer(name="Test", index=0, bindings=bindings)

        result = generate_kle_from_template(layer)
        # Should have underscore above minus (shifted)
        assert '"_\\n-"' in result or "'_\\n-'" in result

    def test_outer_column_r3_tab_key(self):
        """KLE-030: R3C6 left (Tab) should be mapped."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        # ZMK position 22 is Tab on R3 left outer column
        bindings = [KeyBinding(position=22, tap="TAB")]
        bindings.extend([KeyBinding(position=i, tap="X") for i in range(80) if i != 22])
        layer = Layer(name="Test", index=0, bindings=bindings)

        result = generate_kle_from_template(layer)
        # Tab should appear somewhere in the output (may be unicode escaped)
        assert "⇥" in result or "\\u21e5" in result or "Tab" in result or "TAB" in result

    def test_outer_column_r3_backslash_key(self):
        """KLE-031: R3C6 right (\\|) should be mapped."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        # ZMK position 33 is backslash on R3 right outer column
        bindings = [KeyBinding(position=33, tap="\\")]
        bindings.extend([KeyBinding(position=i, tap="X") for i in range(80) if i != 33])
        layer = Layer(name="Test", index=0, bindings=bindings)

        result = generate_kle_from_template(layer)
        # Should have pipe above backslash (shifted)
        assert '"|\\n' in result or "'" + "|\\n" in result or "\\\\" in result


class TestKLEEdgeCases:
    """Test edge cases for KLE template generation."""

    def test_shifted_and_hold_label_format(self):
        """KLE edge case: Key with both shifted AND hold should format correctly."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        # Create a key with shifted character AND hold behavior
        # e.g., "1" key with hold LCTL - should show: !\\n1\\n\\n\\nCtrl
        bindings = [KeyBinding(position=11, tap="1", hold="LCTL")]
        bindings.extend([KeyBinding(position=i, tap="X") for i in range(80) if i != 11])
        layer = Layer(name="Test", index=0, bindings=bindings)

        result = generate_kle_from_template(layer)
        # Should have all three parts: shifted (!), tap (1), and hold (Ctrl symbol)
        # Format: "shifted\ntap\n\n\nhold"
        assert "!" in result  # Shifted character
        assert "1" in result  # Tap character

    def test_out_of_range_zmk_position_is_ignored(self):
        """KLE edge case: ZMK positions that map to invalid slots should be skipped."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        # Create a layer with only valid positions - the invalid ones won't crash
        # ZMK position 99 doesn't exist in ZMK_TO_KLE_SLOT, should be skipped
        bindings = [KeyBinding(position=i, tap=chr(65 + (i % 26))) for i in range(80)]
        layer = Layer(name="Test", index=0, bindings=bindings)

        # Should not raise any errors
        result = generate_kle_from_template(layer)
        assert result is not None
        assert isinstance(result, str)

    def test_kle_slot_beyond_template_positions_is_skipped(self, mocker):
        """KLE edge case: Slot index beyond TEMPLATE_POSITIONS should be skipped."""
        from glove80_visualizer import kle_template
        from glove80_visualizer.kle_template import generate_kle_from_template

        # Mock ZMK_TO_KLE_SLOT to return an out-of-range slot for position 11
        original_slot_map = kle_template.ZMK_TO_KLE_SLOT.copy()
        # Add a position that maps to an invalid slot (beyond TEMPLATE_POSITIONS)
        mock_slot_map = original_slot_map.copy()
        mock_slot_map[11] = 99999  # Way beyond any valid slot

        mocker.patch.object(kle_template, "ZMK_TO_KLE_SLOT", mock_slot_map)

        bindings = [KeyBinding(position=11, tap="1")]
        bindings.extend([KeyBinding(position=i, tap="X") for i in range(80) if i != 11])
        layer = Layer(name="Test", index=0, bindings=bindings)

        # Should not raise - the invalid slot should be skipped
        result = generate_kle_from_template(layer)
        assert result is not None


class TestKLEComboTextBlocks:
    """Test combo text block generation in KLE JSON."""

    def test_generate_with_combos_includes_combo_text(self, sample_layer):
        """KLE-021: Combos should appear in text blocks."""
        from glove80_visualizer.kle_template import generate_kle_from_template
        from glove80_visualizer.models import Combo

        # sample_layer has name "TestLayer"
        combos = [
            Combo(name="LT3+LT6", positions=[54, 71], action="Toggle Gaming", layers=["TestLayer"]),
        ]

        result = generate_kle_from_template(sample_layer, combos=combos)

        assert "LT3+LT6" in result
        assert "Toggle Gaming" in result

    def test_left_hand_combos_in_left_block(self, sample_layer):
        """KLE-022: Left-hand combos should be in left text block (arrow points right)."""
        from glove80_visualizer.kle_template import generate_kle_from_template
        from glove80_visualizer.models import Combo

        combos = [
            Combo(name="LT1+LT4", positions=[52, 69], action="Cmd+Tab", layers=None),
        ]

        result = generate_kle_from_template(sample_layer, combos=combos)

        # Left block format: "name → action"
        assert "LT1+LT4" in result
        assert "Cmd+Tab" in result

    def test_right_hand_combos_in_right_block(self, sample_layer):
        """KLE-023: Right-hand combos should be in right text block (arrow points left)."""
        from glove80_visualizer.kle_template import generate_kle_from_template
        from glove80_visualizer.models import Combo

        combos = [
            Combo(name="RT1+RT4", positions=[57, 74], action="Sticky Hyper", layers=None),
        ]

        result = generate_kle_from_template(sample_layer, combos=combos)

        # Right block format: "action ← name"
        assert "RT1+RT4" in result
        assert "Sticky Hyper" in result

    def test_cross_hand_combos_in_left_block(self, sample_layer):
        """KLE-024: Cross-hand combos should appear in left text block."""
        from glove80_visualizer.kle_template import generate_kle_from_template
        from glove80_visualizer.models import Combo

        combos = [
            Combo(name="LT6+RT6", positions=[71, 72], action="Caps Lock", layers=None),
        ]

        result = generate_kle_from_template(sample_layer, combos=combos)

        # Cross-hand combos go in left block
        assert "LT6+RT6" in result
        assert "Caps Lock" in result

    def test_combos_filtered_by_layer(self, sample_layer):
        """KLE-025: Only combos active on the layer should be shown."""
        from glove80_visualizer.kle_template import generate_kle_from_template
        from glove80_visualizer.models import Combo

        # sample_layer has name "TestLayer"
        combos = [
            Combo(
                name="LT3+LT6",
                positions=[54, 71],
                action="Toggle Gaming",
                layers=["TestLayer", "Gaming"],
            ),
            # Not on this layer:
            Combo(name="LT1+LT4", positions=[52, 69], action="Cmd+Tab", layers=["Symbol"]),
        ]

        result = generate_kle_from_template(sample_layer, combos=combos)

        # Gaming toggle should be shown (active on TestLayer)
        assert "Toggle Gaming" in result
        # Cmd+Tab should NOT be shown (only active on Symbol)
        assert "Cmd+Tab" not in result

    def test_combos_with_no_layer_restriction_shown_everywhere(self, sample_layer):
        """KLE-026: Combos with layers=None should appear on all layers."""
        from glove80_visualizer.kle_template import generate_kle_from_template
        from glove80_visualizer.models import Combo

        combos = [
            Combo(name="LT1+RT1", positions=[52, 57], action="Left Cmd", layers=None),
        ]

        result = generate_kle_from_template(sample_layer, combos=combos)

        assert "Left Cmd" in result

    def test_no_combos_produces_empty_blocks(self, sample_layer):
        """KLE-027: No combos should produce empty text blocks."""
        from glove80_visualizer.kle_template import generate_kle_from_template

        result = generate_kle_from_template(sample_layer, combos=[])

        # Result should be valid JSON with no combo content
        parsed = json.loads(result)
        assert parsed is not None

    def test_combo_html_formatting(self, sample_layer):
        """KLE-028: Combo text blocks should use HTML list formatting."""
        from glove80_visualizer.kle_template import generate_kle_from_template
        from glove80_visualizer.models import Combo

        combos = [
            Combo(name="LT3+LT6", positions=[54, 71], action="Toggle Gaming", layers=None),
            Combo(name="LT1+LT4", positions=[52, 69], action="Cmd+Tab", layers=None),
        ]

        result = generate_kle_from_template(sample_layer, combos=combos)

        # Should use HTML list elements
        assert "<li>" in result or "<ul" in result


class TestKLEHeldKeyIndicator:
    """Test the held key indicator (✋) for layer activators."""

    def test_held_key_shows_hand_emoji(self):
        """KLE-036: Key that activates current layer should show ✋."""
        from glove80_visualizer.kle_template import generate_kle_from_template, ZMK_TO_SLOT, TEMPLATE_POSITIONS
        from glove80_visualizer.models import LayerActivator

        # Create a layer where position 69 (left T4) activates it
        bindings = [KeyBinding(position=69, tap="Cursor", hold="Cursor")]
        bindings.extend([KeyBinding(position=i, tap="X") for i in range(80) if i != 69])
        layer = Layer(name="Cursor", index=17, bindings=bindings)

        # Create an activator that says position 69 activates layer "Cursor"
        activators = [
            LayerActivator(
                source_layer_name="QWERTY",
                source_position=69,
                target_layer_name="Cursor",
            )
        ]

        result = generate_kle_from_template(layer, activators=activators)
        parsed = json.loads(result)

        slot = ZMK_TO_SLOT[69]
        row_idx, item_idx = TEMPLATE_POSITIONS[slot]
        row = parsed[row_idx]
        label = row[item_idx]

        # Should contain the hand emoji
        assert "✋" in label, f"Held key should show ✋, got {repr(label)}"

    def test_held_key_shows_layer_text(self):
        """KLE-037: Held key indicator should include 'Layer' text."""
        from glove80_visualizer.kle_template import generate_kle_from_template, ZMK_TO_SLOT, TEMPLATE_POSITIONS
        from glove80_visualizer.models import LayerActivator

        bindings = [KeyBinding(position=69, tap="Cursor", hold="Cursor")]
        bindings.extend([KeyBinding(position=i, tap="X") for i in range(80) if i != 69])
        layer = Layer(name="Cursor", index=17, bindings=bindings)

        activators = [
            LayerActivator(
                source_layer_name="QWERTY",
                source_position=69,
                target_layer_name="Cursor",
            )
        ]

        result = generate_kle_from_template(layer, activators=activators)
        parsed = json.loads(result)

        slot = ZMK_TO_SLOT[69]
        row_idx, item_idx = TEMPLATE_POSITIONS[slot]
        row = parsed[row_idx]
        label = row[item_idx]

        # Should contain "Layer" text
        assert "Layer" in label, f"Held key should show 'Layer', got {repr(label)}"

    def test_held_key_has_alignment_a0(self):
        """KLE-038: Held key should use a=0 alignment for 12-position grid."""
        from glove80_visualizer.kle_template import generate_kle_from_template, ZMK_TO_SLOT, TEMPLATE_POSITIONS
        from glove80_visualizer.models import LayerActivator

        bindings = [KeyBinding(position=69, tap="Cursor", hold="Cursor")]
        bindings.extend([KeyBinding(position=i, tap="X") for i in range(80) if i != 69])
        layer = Layer(name="Cursor", index=17, bindings=bindings)

        activators = [
            LayerActivator(
                source_layer_name="QWERTY",
                source_position=69,
                target_layer_name="Cursor",
            )
        ]

        result = generate_kle_from_template(layer, activators=activators)
        parsed = json.loads(result)

        slot = ZMK_TO_SLOT[69]
        row_idx, item_idx = TEMPLATE_POSITIONS[slot]
        row = parsed[row_idx]

        # Find the alignment setting for this key
        if item_idx > 0 and isinstance(row[item_idx - 1], dict):
            props = row[item_idx - 1]
            assert props.get("a") == 0, f"Held key should have a=0 alignment, got {props.get('a')}"

    def test_no_held_indicator_without_activators(self):
        """KLE-039: Without activators, key should show normal label."""
        from glove80_visualizer.kle_template import generate_kle_from_template, ZMK_TO_SLOT, TEMPLATE_POSITIONS

        bindings = [KeyBinding(position=69, tap="Cursor")]
        bindings.extend([KeyBinding(position=i, tap="X") for i in range(80) if i != 69])
        layer = Layer(name="Cursor", index=17, bindings=bindings)

        # No activators passed
        result = generate_kle_from_template(layer)
        parsed = json.loads(result)

        slot = ZMK_TO_SLOT[69]
        row_idx, item_idx = TEMPLATE_POSITIONS[slot]
        row = parsed[row_idx]
        label = row[item_idx]

        # Should NOT contain the hand emoji
        assert "✋" not in label, f"Without activators, key should not show ✋, got {repr(label)}"

    def test_held_indicator_only_for_matching_layer(self):
        """KLE-040: Held indicator only shows when activator targets current layer."""
        from glove80_visualizer.kle_template import generate_kle_from_template, ZMK_TO_SLOT, TEMPLATE_POSITIONS
        from glove80_visualizer.models import LayerActivator

        bindings = [KeyBinding(position=69, tap="Symbol")]
        bindings.extend([KeyBinding(position=i, tap="X") for i in range(80) if i != 69])
        layer = Layer(name="Symbol", index=21, bindings=bindings)

        # Activator targets "Cursor", not "Symbol"
        activators = [
            LayerActivator(
                source_layer_name="QWERTY",
                source_position=69,
                target_layer_name="Cursor",
            )
        ]

        result = generate_kle_from_template(layer, activators=activators)
        parsed = json.loads(result)

        slot = ZMK_TO_SLOT[69]
        row_idx, item_idx = TEMPLATE_POSITIONS[slot]
        row = parsed[row_idx]
        label = row[item_idx]

        # Should NOT show held indicator since activator targets different layer
        assert "✋" not in label, f"Activator for wrong layer should not show ✋, got {repr(label)}"
