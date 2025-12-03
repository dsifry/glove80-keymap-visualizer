"""
Tests for the SVG generator module.

These tests define the expected behavior of SVG generation.
Write these tests FIRST (TDD), then implement the generator to pass them.
"""



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
        from glove80_visualizer.models import KeyBinding, Layer
        from glove80_visualizer.svg_generator import generate_layer_svg

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
        from glove80_visualizer.config import VisualizerConfig
        from glove80_visualizer.models import Layer
        from glove80_visualizer.svg_generator import generate_layer_svg

        config = VisualizerConfig(background_color="#000000", text_color="#ffffff")
        layer = Layer(name="Test", index=0, bindings=[])
        svg = generate_layer_svg(layer, config=config)
        # Custom colors should appear in the SVG
        assert "#000000" in svg.lower() or "background" in svg.lower()

    def test_svg_transparent_keys(self):
        """SPEC-S006: Generator correctly renders transparent keys."""
        from glove80_visualizer.models import KeyBinding, Layer
        from glove80_visualizer.svg_generator import generate_layer_svg

        layer = Layer(
            name="Test", index=0, bindings=[KeyBinding(position=0, tap="&trans")]
        )
        svg = generate_layer_svg(layer)
        assert svg is not None
        # Transparent keys should render without error

    def test_svg_hold_tap_display(self):
        """SPEC-S007: Generator shows both tap and hold for hold-tap keys."""
        from glove80_visualizer.models import KeyBinding, Layer
        from glove80_visualizer.svg_generator import generate_layer_svg

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
        """Simple keys format as their name or symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("A") == "A"
        # SPACE formats as symbol for better visual representation
        assert format_key_label("SPACE") == "␣"

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


class TestTransparentKeyDisplay:
    """Tests for transparent key display - should show 'trans' not triangle symbol."""

    def test_transparent_key_shows_trans_text(self):
        """SPEC-S009: Transparent keys should display 'trans' text, not triangle symbol."""
        from glove80_visualizer.models import KeyBinding, Layer
        from glove80_visualizer.svg_generator import generate_layer_svg

        layer = Layer(
            name="Test",
            index=0,
            bindings=[KeyBinding(position=0, tap="&trans")],
        )
        svg = generate_layer_svg(layer)

        # Should contain "trans" text, NOT the triangle symbol
        assert "trans" in svg.lower()
        assert "▽" not in svg  # Triangle symbol should NOT be present

    def test_transparent_key_has_trans_styling(self):
        """SPEC-S010: Transparent keys should have the 'trans' CSS class for styling."""
        from glove80_visualizer.models import KeyBinding, Layer
        from glove80_visualizer.svg_generator import generate_layer_svg

        layer = Layer(
            name="Test",
            index=0,
            bindings=[KeyBinding(position=0, tap="&trans")],
        )
        svg = generate_layer_svg(layer)

        # Should have trans class for lighter/greyed styling
        assert 'class="' in svg and "trans" in svg


class TestResolveTransparentKeys:
    """Tests for --resolve-trans feature that shows inherited keys."""

    def test_resolve_trans_shows_base_layer_key(self):
        """SPEC-S032: With resolve_trans, transparent keys show the base layer key."""
        from glove80_visualizer.models import KeyBinding, Layer
        from glove80_visualizer.svg_generator import generate_layer_svg

        # Base layer has 'A' at position 0
        base_layer = Layer(
            name="QWERTY",
            index=0,
            bindings=[KeyBinding(position=0, tap="A")],
        )

        # Upper layer has &trans at position 0
        upper_layer = Layer(
            name="Symbol",
            index=1,
            bindings=[KeyBinding(position=0, tap="&trans")],
        )

        # Without resolve_trans - should show "trans"
        svg_normal = generate_layer_svg(upper_layer)
        assert "trans" in svg_normal.lower()

        # With resolve_trans - should show "A" (inherited from base)
        svg_resolved = generate_layer_svg(
            upper_layer,
            resolve_trans=True,
            base_layer=base_layer
        )
        assert "A" in svg_resolved
        assert "trans" not in svg_resolved.lower() or "class" in svg_resolved  # trans might be in class name

    def test_resolve_trans_uses_inherited_styling(self):
        """SPEC-S033: Resolved transparent keys should have 'inherited' styling."""
        from glove80_visualizer.models import KeyBinding, Layer
        from glove80_visualizer.svg_generator import generate_layer_svg

        base_layer = Layer(
            name="QWERTY",
            index=0,
            bindings=[KeyBinding(position=0, tap="A")],
        )

        upper_layer = Layer(
            name="Symbol",
            index=1,
            bindings=[KeyBinding(position=0, tap="&trans")],
        )

        svg = generate_layer_svg(
            upper_layer,
            resolve_trans=True,
            base_layer=base_layer
        )

        # Should have some indication that the key is inherited
        # Either "inherited" class or lighter styling
        assert "inherited" in svg.lower() or "trans" in svg.lower()

    def test_resolve_trans_chains_through_multiple_trans(self):
        """SPEC-S034: resolve_trans should chain through multiple transparent layers."""
        from glove80_visualizer.models import KeyBinding, Layer
        from glove80_visualizer.svg_generator import generate_layer_svg

        # Base layer has 'Z' at position 0
        base_layer = Layer(
            name="QWERTY",
            index=0,
            bindings=[KeyBinding(position=0, tap="Z")],
        )

        # Middle layer also has &trans at position 0
        middle_layer = Layer(
            name="Lower",
            index=1,
            bindings=[KeyBinding(position=0, tap="&trans")],
        )

        # Top layer has &trans at position 0
        top_layer = Layer(
            name="Symbol",
            index=2,
            bindings=[KeyBinding(position=0, tap="&trans")],
        )

        # Should resolve all the way down to base layer's 'Z'
        # Note: We resolve against base layer, not through the chain
        svg = generate_layer_svg(
            top_layer,
            resolve_trans=True,
            base_layer=base_layer
        )
        assert "Z" in svg

    def test_resolve_trans_preserves_non_trans_keys(self):
        """SPEC-S035: Non-transparent keys should be unaffected by resolve_trans."""
        from glove80_visualizer.models import KeyBinding, Layer
        from glove80_visualizer.svg_generator import generate_layer_svg

        base_layer = Layer(
            name="QWERTY",
            index=0,
            bindings=[
                KeyBinding(position=0, tap="A"),
                KeyBinding(position=1, tap="B"),
            ],
        )

        upper_layer = Layer(
            name="Symbol",
            index=1,
            bindings=[
                KeyBinding(position=0, tap="&trans"),  # Should resolve to A
                KeyBinding(position=1, tap="!"),       # Should stay as !
            ],
        )

        svg = generate_layer_svg(
            upper_layer,
            resolve_trans=True,
            base_layer=base_layer
        )

        assert "A" in svg  # Resolved from trans
        assert "!" in svg  # Preserved as-is


class TestLongTextHandling:
    """Tests for handling long key labels - multi-line, smaller fonts, no overflow."""

    def test_long_label_does_not_overflow_key_boundary(self):
        """SPEC-S011: Long labels should not visually overflow the key rectangle."""
        from glove80_visualizer.models import KeyBinding, Layer
        from glove80_visualizer.svg_generator import generate_layer_svg

        # Create a layer with a very long label
        layer = Layer(
            name="Test",
            index=0,
            bindings=[KeyBinding(position=0, tap="PRINTSCREEN")],
        )
        svg = generate_layer_svg(layer)

        # Long labels should be abbreviated or use smaller font
        # PRINTSCREEN should become something shorter like "PrtSc" or "PSCRN"
        # OR it should have a font-size reduction
        has_abbreviation = "PrtSc" in svg or "PSCRN" in svg or "Print" in svg
        has_font_reduction = "font-size:" in svg or "style=" in svg
        assert has_abbreviation or has_font_reduction

    def test_very_long_behavior_name_is_truncated_or_abbreviated(self):
        """SPEC-S012: Very long behavior names like &sticky_key should be handled."""
        from glove80_visualizer.models import KeyBinding, Layer
        from glove80_visualizer.svg_generator import generate_layer_svg

        layer = Layer(
            name="Test",
            index=0,
            bindings=[KeyBinding(position=0, tap="&sticky_key LSFT")],
        )
        svg = generate_layer_svg(layer)

        # Should NOT show the ugly truncated "&sticky_ke…"
        # Should show something more readable
        assert "&sticky_ke…" not in svg

    def test_backspace_uses_abbreviation(self):
        """SPEC-S013: BACKSPACE should display as abbreviated form."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("BACKSPACE")
        # Should be abbreviated to fit in key
        assert result in ["Bksp", "BKSP", "⌫", "BkSp", "BS"]

    def test_printscreen_uses_abbreviation(self):
        """SPEC-S014: PRINTSCREEN should display as abbreviated form."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("PRINTSCREEN")
        # Should be abbreviated to fit in key
        assert result in ["PrtSc", "PSCRN", "PSc", "Print", "PrScr"]

    def test_scrolllock_uses_abbreviation(self):
        """SPEC-S015: SCROLLLOCK should display as abbreviated form."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("SCROLLLOCK")
        # Should be abbreviated to fit in key
        assert result in ["ScrLk", "SLCK", "ScLk", "Scroll"]


class TestKeyLabelAbbreviations:
    """Tests for common key label abbreviations."""

    def test_arrow_keys_use_symbols(self):
        """SPEC-S016: Arrow keys should use arrow symbols."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("LEFT") == "←"
        assert format_key_label("RIGHT") == "→"
        assert format_key_label("UP") == "↑"
        assert format_key_label("DOWN") == "↓"

    def test_page_navigation_abbreviated(self):
        """SPEC-S017: Page navigation keys should be abbreviated."""
        from glove80_visualizer.svg_generator import format_key_label

        result_pgup = format_key_label("PG_UP")
        result_pgdn = format_key_label("PG_DN")
        assert result_pgup in ["PgUp", "⇞", "PgU"]
        assert result_pgdn in ["PgDn", "⇟", "PgD"]

    def test_insert_delete_abbreviated(self):
        """SPEC-S018: INSERT and DELETE should be abbreviated."""
        from glove80_visualizer.svg_generator import format_key_label

        result_ins = format_key_label("INSERT")
        result_del = format_key_label("DELETE")
        assert result_ins in ["Ins", "INS", "⎀"]
        assert result_del in ["Del", "DEL", "⌦"]

    def test_modifier_keys_mac_symbols(self):
        """SPEC-S019a: Modifier keys should use Apple/Mac symbols when os_style='mac'."""
        from glove80_visualizer.svg_generator import format_key_label

        # Shift - Apple shift symbol ⇧
        assert format_key_label("LSHIFT", os_style="mac") == "⇧"
        assert format_key_label("RSHIFT", os_style="mac") == "⇧"
        assert format_key_label("LSHFT", os_style="mac") == "⇧"
        assert format_key_label("RSHFT", os_style="mac") == "⇧"

        # Control - Apple control symbol ⌃
        assert format_key_label("LCTRL", os_style="mac") == "⌃"
        assert format_key_label("RCTRL", os_style="mac") == "⌃"
        assert format_key_label("LCTL", os_style="mac") == "⌃"
        assert format_key_label("RCTL", os_style="mac") == "⌃"

        # Alt/Option - Apple option symbol ⌥
        assert format_key_label("LALT", os_style="mac") == "⌥"
        assert format_key_label("RALT", os_style="mac") == "⌥"

        # GUI/Command - Apple command symbol ⌘
        assert format_key_label("LGUI", os_style="mac") == "⌘"
        assert format_key_label("RGUI", os_style="mac") == "⌘"

    def test_modifier_keys_windows_symbols(self):
        """SPEC-S019b: Modifier keys should use Windows symbols when os_style='windows'."""
        from glove80_visualizer.svg_generator import format_key_label

        # Shift
        assert format_key_label("LSHIFT", os_style="windows") == "Shift"
        assert format_key_label("RSHIFT", os_style="windows") == "Shift"

        # Control
        assert format_key_label("LCTRL", os_style="windows") == "Ctrl"
        assert format_key_label("RCTRL", os_style="windows") == "Ctrl"

        # Alt
        assert format_key_label("LALT", os_style="windows") == "Alt"
        assert format_key_label("RALT", os_style="windows") == "Alt"

        # GUI/Win - Windows logo or "Win"
        assert format_key_label("LGUI", os_style="windows") in ["Win", "⊞"]
        assert format_key_label("RGUI", os_style="windows") in ["Win", "⊞"]

    def test_modifier_keys_linux_symbols(self):
        """SPEC-S019c: Modifier keys should use Linux symbols when os_style='linux'."""
        from glove80_visualizer.svg_generator import format_key_label

        # Shift
        assert format_key_label("LSHIFT", os_style="linux") == "Shift"
        assert format_key_label("RSHIFT", os_style="linux") == "Shift"

        # Control
        assert format_key_label("LCTRL", os_style="linux") == "Ctrl"
        assert format_key_label("RCTRL", os_style="linux") == "Ctrl"

        # Alt
        assert format_key_label("LALT", os_style="linux") == "Alt"
        assert format_key_label("RALT", os_style="linux") == "Alt"

        # GUI/Super
        assert format_key_label("LGUI", os_style="linux") == "Super"
        assert format_key_label("RGUI", os_style="linux") == "Super"

    def test_modifier_keys_default_is_mac(self):
        """SPEC-S019d: Default os_style should be 'mac'."""
        from glove80_visualizer.svg_generator import format_key_label

        # Without specifying os_style, should default to mac
        assert format_key_label("LGUI") == "⌘"
        assert format_key_label("LALT") == "⌥"
        assert format_key_label("LCTRL") == "⌃"
        assert format_key_label("LSHIFT") == "⇧"

    def test_function_key_passthrough(self):
        """SPEC-S020: Function keys should pass through unchanged."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("F1") == "F1"
        assert format_key_label("F12") == "F12"

    def test_common_keys_abbreviated(self):
        """SPEC-S021: Common long key names should be abbreviated."""
        from glove80_visualizer.svg_generator import format_key_label

        # These are commonly too long
        assert format_key_label("CAPSLOCK") in ["Caps", "CAPS", "CapsLk", "⇪"]
        assert format_key_label("NUMLOCK") in ["NumLk", "NUM", "NLck"]
        assert format_key_label("PAUSE_BREAK") in ["Pause", "PsBrk", "Brk"]


class TestSpecialLayerSymbols:
    """Tests for special layer and key symbols like emoji and world."""

    def test_emoji_layer_uses_unicode_symbol(self):
        """SPEC-S022: Emoji layer reference should use emoji symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        # When a key activates "Emoji" layer, show emoji symbol
        assert format_key_label("Emoji") in ["😀", "🙂", "😊", "🎉"]

    def test_world_layer_uses_unicode_symbol(self):
        """SPEC-S023: World layer reference should use globe symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        # When a key activates "World" layer, show globe symbol
        assert format_key_label("World") in ["🌍", "🌎", "🌏", "🌐"]

    def test_mouse_layer_uses_unicode_symbol(self):
        """SPEC-S024: Mouse layer reference should use mouse/pointer symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        # When a key activates "Mouse" layer, show mouse symbol
        assert format_key_label("Mouse") in ["🖱", "🖱️", "🐭", "Mouse"]

    def test_symbol_layer_uses_unicode_symbol(self):
        """SPEC-S025: Symbol layer reference should use symbol icon."""
        from glove80_visualizer.svg_generator import format_key_label

        # When a key activates "Symbol" layer, show symbol icon
        assert format_key_label("Symbol") in ["#", "⌨", "※", "Symbol", "Sym"]

    def test_number_layer_uses_unicode_symbol(self):
        """SPEC-S026: Number layer reference should use number symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        # When a key activates "Number" layer, show number icon
        assert format_key_label("Number") in ["#", "123", "№", "Number"]

    def test_function_layer_uses_unicode_symbol(self):
        """SPEC-S027: Function layer reference should use function symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        # When a key activates "Function" layer, show function icon
        assert format_key_label("Function") in ["Fn", "ƒ", "F1-12"]

    def test_cursor_layer_uses_unicode_symbol(self):
        """SPEC-S028: Cursor layer reference should use cursor/arrow symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        # When a key activates "Cursor" layer, show cursor icon
        assert format_key_label("Cursor") in ["↔", "⇄", "🔀", "Nav"]

    def test_system_layer_uses_unicode_symbol(self):
        """SPEC-S029: System layer reference should use gear/settings symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        # When a key activates "System" layer, show system/gear icon
        assert format_key_label("System") in ["⚙", "⚙️", "🔧", "Sys"]

    def test_gaming_layer_uses_unicode_symbol(self):
        """SPEC-S030: Gaming layer reference should use game controller symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        # When a key activates "Gaming" layer, show game icon
        assert format_key_label("Gaming") in ["🎮", "🕹", "🕹️", "Game"]

    def test_magic_layer_uses_unicode_symbol(self):
        """SPEC-S031: Magic layer reference should use magic/sparkle symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        # When a key activates "Magic" layer (Glove80 special), show magic icon
        assert format_key_label("Magic") in ["✨", "🪄", "⚡", "Magic"]


class TestArrowKeyIcons:
    """Tests for arrow key icon display."""

    def test_left_arrow_uses_symbol(self):
        """SPEC-S033: Left arrow key should display ← symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("LEFT") == "←"
        assert format_key_label("left") == "←"  # Case insensitive
        assert format_key_label("Left") == "←"

    def test_right_arrow_uses_symbol(self):
        """SPEC-S034: Right arrow key should display → symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("RIGHT") == "→"
        assert format_key_label("right") == "→"
        assert format_key_label("Right") == "→"

    def test_up_arrow_uses_symbol(self):
        """SPEC-S035: Up arrow key should display ↑ symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("UP") == "↑"
        assert format_key_label("up") == "↑"
        assert format_key_label("Up") == "↑"

    def test_down_arrow_uses_symbol(self):
        """SPEC-S036: Down arrow key should display ↓ symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("DOWN") == "↓"
        assert format_key_label("down") == "↓"
        assert format_key_label("Down") == "↓"

    def test_arrow_keys_in_svg_output(self):
        """SPEC-S037: Arrow keys in layer should render with arrow symbols in SVG."""
        from glove80_visualizer.models import KeyBinding, Layer
        from glove80_visualizer.svg_generator import generate_layer_svg

        layer = Layer(
            name="NavLayer",
            index=0,
            bindings=[
                KeyBinding(position=0, tap="LEFT"),
                KeyBinding(position=1, tap="DOWN"),
                KeyBinding(position=2, tap="UP"),
                KeyBinding(position=3, tap="RIGHT"),
            ] + [KeyBinding(position=i, tap="X") for i in range(4, 80)],
        )
        svg = generate_layer_svg(layer)

        # SVG should contain arrow symbols, not text like "LEFT"
        assert "←" in svg
        assert "↓" in svg
        assert "↑" in svg
        assert "→" in svg

    def test_home_end_keys_use_symbols(self):
        """SPEC-S038: Home and End keys should use appropriate symbols."""
        from glove80_visualizer.svg_generator import format_key_label

        result_home = format_key_label("HOME")
        result_end = format_key_label("END")

        # Home can use ⇱ or ↖ or "Home"
        assert result_home in ["⇱", "↖", "Home", "⤒"]
        # End can use ⇲ or ↘ or "End"
        assert result_end in ["⇲", "↘", "End", "⤓"]

    def test_page_up_down_use_symbols(self):
        """SPEC-S039: Page Up and Page Down keys should use appropriate symbols."""
        from glove80_visualizer.svg_generator import format_key_label

        result_pgup = format_key_label("PG_UP")
        result_pgdn = format_key_label("PG_DN")
        result_pgup2 = format_key_label("PAGE_UP")
        result_pgdn2 = format_key_label("PAGE_DOWN")

        # Page Up - double up arrow or abbreviated
        assert result_pgup in ["⇞", "PgUp", "PgU", "⇑"]
        assert result_pgdn in ["⇟", "PgDn", "PgD", "⇓"]
        # Alternative formats should also work
        assert result_pgup2 in ["⇞", "PgUp", "PgU", "⇑"]
        assert result_pgdn2 in ["⇟", "PgDn", "PgD", "⇓"]

    def test_arrow_key_with_modifier_combo(self):
        """SPEC-S040: Arrow keys with modifiers should show both symbols."""
        from glove80_visualizer.svg_generator import format_key_label

        # Shift+Arrow should combine symbols
        result_shift_left = format_key_label("LS(LEFT)", os_style="mac")
        result_cmd_right = format_key_label("LG(RIGHT)", os_style="mac")

        # Should contain both the modifier and arrow symbols
        assert "←" in result_shift_left or "⇧" in result_shift_left
        assert "→" in result_cmd_right or "⌘" in result_cmd_right

    def test_double_arrow_symbols(self):
        """SPEC-S041: Word-jump arrows (Opt+Arrow on Mac) should use double arrows when possible."""
        from glove80_visualizer.svg_generator import format_key_label

        # These are common navigation shortcuts
        # Option+Left jumps word left, Option+Right jumps word right
        # Some keymaps may have dedicated bindings for these
        result = format_key_label("WORD_LEFT")
        result2 = format_key_label("WORD_RIGHT")

        # If these keys exist, they could use double arrows
        # ⇐ for word left, ⇒ for word right, or regular arrows
        assert result in ["⇐", "←←", "←", "WORD_LEFT", "W←"]
        assert result2 in ["⇒", "→→", "→", "WORD_RIGHT", "W→"]


class TestMediaKeyIcons:
    """Tests for media key icon display."""

    def test_play_pause_uses_symbol(self):
        """SPEC-S042: Play/Pause key should display ⏯ or ▶⏸ symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("C_PP") in ["⏯", "▶⏸", "▶️⏸️", "⏵⏸"]
        assert format_key_label("C_PLAY_PAUSE") in ["⏯", "▶⏸", "▶️⏸️", "⏵⏸"]

    def test_play_uses_symbol(self):
        """SPEC-S043: Play key should display ▶ symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("C_PLAY") in ["▶", "▶️", "⏵"]

    def test_pause_uses_symbol(self):
        """SPEC-S044: Pause key should display ⏸ symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("C_PAUSE") in ["⏸", "⏸️", "||"]

    def test_stop_uses_symbol(self):
        """SPEC-S045: Stop key should display ⏹ symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("C_STOP") in ["⏹", "⏹️", "◼"]

    def test_next_track_uses_symbol(self):
        """SPEC-S046: Next track key should display ⏭ symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("C_NEXT") in ["⏭", "⏭️", ">>|", "⏩"]

    def test_prev_track_uses_symbol(self):
        """SPEC-S047: Previous track key should display ⏮ symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("C_PREV") in ["⏮", "⏮️", "|<<", "⏪"]

    def test_volume_up_uses_symbol(self):
        """SPEC-S048: Volume up key should display 🔊 or 🔉+ symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("C_VOL_UP") in ["🔊", "🔉+", "Vol+", "🔈+"]
        assert format_key_label("C_VOLUME_UP") in ["🔊", "🔉+", "Vol+", "🔈+"]

    def test_volume_down_uses_symbol(self):
        """SPEC-S049: Volume down key should display 🔉 or 🔈- symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("C_VOL_DN") in ["🔉", "🔈-", "Vol-", "🔈−"]
        assert format_key_label("C_VOLUME_DOWN") in ["🔉", "🔈-", "Vol-", "🔈−"]

    def test_mute_uses_symbol(self):
        """SPEC-S050: Mute key should display 🔇 symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("C_MUTE") in ["🔇", "🔈✕", "Mute", "🔈×"]

    def test_brightness_up_uses_symbol(self):
        """SPEC-S051: Brightness up key should display ☀+ or 🔆 symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("C_BRI_UP") in ["🔆", "☀+", "☀️+", "Bri+"]
        assert format_key_label("C_BRIGHTNESS_UP") in ["🔆", "☀+", "☀️+", "Bri+"]

    def test_brightness_down_uses_symbol(self):
        """SPEC-S052: Brightness down key should display ☀- or 🔅 symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("C_BRI_DN") in ["🔅", "☀-", "☀️-", "Bri-"]
        assert format_key_label("C_BRIGHTNESS_DOWN") in ["🔅", "☀-", "☀️-", "Bri-"]

    def test_brightness_max_uses_symbol(self):
        """SPEC-S053: Brightness max key should display 🔆 or ☀ symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        # Full brightness
        result = format_key_label("C_BRI_MAX")
        assert result in ["☀", "☀️", "🔆", "BriMax"]

    def test_brightness_min_uses_symbol(self):
        """SPEC-S054: Brightness min key should display dim symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("C_BRI_MIN")
        assert result in ["🌑", "○", "🔅", "BriMin"]

    def test_fast_forward_uses_symbol(self):
        """SPEC-S055: Fast forward key should display ⏩ symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("C_FF") in ["⏩", ">>", "▶▶"]

    def test_rewind_uses_symbol(self):
        """SPEC-S056: Rewind key should display ⏪ symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("C_RW") in ["⏪", "<<", "◀◀"]

    def test_eject_uses_symbol(self):
        """SPEC-S057: Eject key should display ⏏ symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("C_EJECT") in ["⏏", "⏏️", "Eject"]

    def test_record_uses_symbol(self):
        """SPEC-S058: Record key should display ⏺ symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("C_REC") in ["⏺", "⏺️", "●", "Rec"]


class TestMediaKeyTextToSymbol:
    """Tests for converting keymap-drawer text labels to proper media symbols.

    keymap-drawer transforms ZMK codes like C_PLAY_PAUSE into human-readable
    text like "Play" or "PLAY". We need to convert these text labels back to proper symbols.
    """

    def test_play_text_becomes_symbol(self):
        """SPEC-S059: 'Play' or 'PLAY' text should display ▶ symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("Play") in ["▶", "▶️", "⏵", "⏯"]
        assert format_key_label("PLAY") in ["▶", "▶️", "⏵", "⏯"]

    def test_pause_text_becomes_symbol(self):
        """SPEC-S060: 'Pause' text should display ⏸ symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("Pause") in ["⏸", "⏸️", "||"]

    def test_stop_text_becomes_symbol(self):
        """SPEC-S061: 'Stop' or 'STOP' text should display ⏹ symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("Stop") in ["⏹", "⏹️", "◼"]
        assert format_key_label("STOP") in ["⏹", "⏹️", "◼"]

    def test_next_text_becomes_symbol(self):
        """SPEC-S062: 'Next' or 'NEXT' text should display ⏭ symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("Next") in ["⏭", "⏭️", ">>|", "⏩"]
        assert format_key_label("NEXT") in ["⏭", "⏭️", ">>|", "⏩"]

    def test_prev_text_becomes_symbol(self):
        """SPEC-S063: 'Prev', 'PREV', or 'Previous' text should display ⏮ symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("Prev") in ["⏮", "⏮️", "|<<", "⏪"]
        assert format_key_label("PREV") in ["⏮", "⏮️", "|<<", "⏪"]
        assert format_key_label("Previous") in ["⏮", "⏮️", "|<<", "⏪"]

    def test_vol_up_text_becomes_symbol(self):
        """SPEC-S064: 'Vol Up', 'VOL UP', or 'Volume Up' text should display 🔊 symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("Vol Up") in ["🔊", "🔉+", "Vol+"]
        assert format_key_label("VOL UP") in ["🔊", "🔉+", "Vol+"]
        assert format_key_label("Volume Up") in ["🔊", "🔉+", "Vol+"]

    def test_vol_dn_text_becomes_symbol(self):
        """SPEC-S065: 'Vol Dn', 'VOL DN', or 'Volume Down' text should display 🔉 symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("Vol Dn") in ["🔉", "🔈-", "Vol-"]
        assert format_key_label("VOL DN") in ["🔉", "🔈-", "Vol-"]
        assert format_key_label("Vol Down") in ["🔉", "🔈-", "Vol-"]
        assert format_key_label("Volume Down") in ["🔉", "🔈-", "Vol-"]

    def test_mute_text_becomes_symbol(self):
        """SPEC-S066: 'Mute' or 'MUTE' text should display 🔇 symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("Mute") in ["🔇", "🔈✕", "🔈×"]
        assert format_key_label("MUTE") in ["🔇", "🔈✕", "🔈×"]

    def test_bri_up_text_becomes_symbol(self):
        """SPEC-S067: 'Bri Up', 'BRI UP', or 'Brightness Up' text should display 🔆 symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("Bri Up") in ["🔆", "☀+", "Bri+"]
        assert format_key_label("BRI UP") in ["🔆", "☀+", "Bri+"]
        assert format_key_label("Brightness Up") in ["🔆", "☀+", "Bri+"]

    def test_bri_dn_text_becomes_symbol(self):
        """SPEC-S068: 'Bri Dn', 'BRI DN', or 'Brightness Down' text should display 🔅 symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("Bri Dn") in ["🔅", "☀-", "Bri-"]
        assert format_key_label("BRI DN") in ["🔅", "☀-", "Bri-"]
        assert format_key_label("Bri Down") in ["🔅", "☀-", "Bri-"]
        assert format_key_label("Brightness Down") in ["🔅", "☀-", "Bri-"]

    def test_bri_max_text_becomes_symbol(self):
        """SPEC-S069: 'Bri Max' or 'BRI MAX' text should display ☀ symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("Bri Max") in ["☀", "☀️", "🔆"]
        assert format_key_label("BRI MAX") in ["☀", "☀️", "🔆"]

    def test_bri_min_text_becomes_symbol(self):
        """SPEC-S070: 'Bri Min' or 'BRI MIN' text should display dim symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("Bri Min") in ["🌑", "○", "🔅"]
        assert format_key_label("BRI MIN") in ["🌑", "○", "🔅"]

    def test_bri_auto_text_becomes_symbol(self):
        """SPEC-S070b: 'Bri Auto' or 'BRI AUTO' text should display brightness auto symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("Bri Auto") in ["🔆A", "☀A", "Auto"]
        assert format_key_label("BRI AUTO") in ["🔆A", "☀A", "Auto"]

    def test_fast_forward_text_becomes_symbol(self):
        """SPEC-S071: 'FF' or 'Fast Forward' text should display ⏩ symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("FF") in ["⏩", ">>", "▶▶"]
        assert format_key_label("Fast Forward") in ["⏩", ">>", "▶▶"]

    def test_rewind_text_becomes_symbol(self):
        """SPEC-S072: 'RW' or 'Rewind' text should display ⏪ symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("RW") in ["⏪", "<<", "◀◀"]
        assert format_key_label("Rewind") in ["⏪", "<<", "◀◀"]

    def test_eject_text_becomes_symbol(self):
        """SPEC-S073: 'Eject' or 'EJECT' text should display ⏏ symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("Eject") in ["⏏", "⏏️"]
        assert format_key_label("EJECT") in ["⏏", "⏏️"]

    def test_record_text_becomes_symbol(self):
        """SPEC-S074: 'Rec', 'REC', or 'Record' text should display ⏺ symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("Rec") in ["⏺", "⏺️", "●"]
        assert format_key_label("REC") in ["⏺", "⏺️", "●"]
        assert format_key_label("Record") in ["⏺", "⏺️", "●"]

    def test_pp_shorthand_becomes_symbol(self):
        """SPEC-S075: 'PP' shorthand should display ⏯ symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("PP") == "⏯"


class TestModifierComboFormatting:
    """Tests for formatting keymap-drawer modifier combos like Gui+Z."""

    def test_gui_combo_mac(self):
        """SPEC-S076: Gui+X combos should use ⌘ on Mac."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("Gui+Z", os_style="mac") == "⌘Z"
        assert format_key_label("Gui+A", os_style="mac") == "⌘A"
        assert format_key_label("Gui+C", os_style="mac") == "⌘C"

    def test_gui_combo_windows(self):
        """SPEC-S077: Gui+X combos should use Win on Windows."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("Gui+Z", os_style="windows") == "WinZ"
        assert format_key_label("Gui+A", os_style="windows") == "WinA"

    def test_ctl_combo_mac(self):
        """SPEC-S078: Ctl+X combos should use ⌃ on Mac."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("Ctl+F16", os_style="mac") == "⌃F16"
        assert format_key_label("Ctrl+C", os_style="mac") == "⌃C"

    def test_sft_combo_mac(self):
        """SPEC-S079: Sft+X combos should use ⇧ on Mac."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("Sft+A", os_style="mac") == "⇧A"
        assert format_key_label("Shift+B", os_style="mac") == "⇧B"

    def test_alt_combo_mac(self):
        """SPEC-S080: Alt+X combos should use ⌥ on Mac."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("Alt+Tab", os_style="mac") == "⌥⇥"

    def test_multi_modifier_combo_mac(self):
        """SPEC-S081: Multi-modifier combos like Gui+Sft+Z should combine symbols."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("Gui+Sft+Z", os_style="mac")
        assert "⌘" in result
        assert "⇧" in result
        assert "Z" in result


class TestMehHyperKeys:
    """Tests for Meh and Hyper key formatting."""

    def test_meh_key_mac(self):
        """SPEC-S082: Meh key should show ⌃⌥⇧ on Mac."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("MEH", os_style="mac") == "⌃⌥⇧"
        assert format_key_label("Meh", os_style="mac") == "⌃⌥⇧"

    def test_meh_key_windows(self):
        """SPEC-S083: Meh key should show 'Meh' on Windows."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("MEH", os_style="windows") == "Meh"

    def test_hyper_key_mac(self):
        """SPEC-S084: Hyper key should show ⌃⌥⇧⌘ on Mac."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("HYPER", os_style="mac") == "⌃⌥⇧⌘"
        assert format_key_label("Hyper", os_style="mac") == "⌃⌥⇧⌘"

    def test_hyper_key_windows(self):
        """SPEC-S085: Hyper key should show 'Hypr' on Windows."""
        from glove80_visualizer.svg_generator import format_key_label

        assert format_key_label("HYPER", os_style="windows") == "Hypr"


class TestBehaviorAbbreviations:
    """Tests for ZMK behavior abbreviation."""

    def test_sticky_key_oneshot_abbreviated(self):
        """SPEC-S086: &sticky_key_oneshot should be abbreviated."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&sticky_key_oneshot LSFT", os_style="mac")
        # Should be short and include shift symbol
        assert len(result) < 15
        assert "⇧" in result or "sticky" in result.lower()

    def test_rgb_macro_abbreviated(self):
        """SPEC-S087: &rgb_ug_status_macro should be abbreviated to RGB."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&rgb_ug_status_macro")
        assert result == "RGB"

    def test_kp_behavior_shows_key(self):
        """SPEC-S088: &kp X should just show the key."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&kp A")
        assert result == "A"

    def test_unknown_behavior_truncated(self):
        """SPEC-S089: Unknown long behaviors should be truncated."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&very_long_behavior_name")
        assert len(result) <= 8
        assert "…" in result or len(result) <= 7


class TestEscapeKeyDisplay:
    """Tests for escape key display - should be readable, not obscure symbol."""

    def test_esc_shows_readable_text(self):
        """SPEC-S090: ESC should display as 'Esc', not obscure symbol ⎋."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("ESC")
        assert result == "Esc"

    def test_escape_shows_readable_text(self):
        """SPEC-S091: ESCAPE should display as 'Esc'."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("ESCAPE")
        assert result == "Esc"


class TestCapsWordDisplay:
    """Tests for caps_word behavior display."""

    def test_caps_word_shows_symbol(self):
        """SPEC-S092: &caps_word should display as CapsWord symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&caps_word")
        # Should be short and recognizable
        assert result in ["⇪W", "CW", "CapsWd", "CAPS"]
        assert len(result) <= 6


class TestStickyKeyDisplay:
    """Tests for sticky key behavior display."""

    def test_sticky_shift_shows_oneshot_symbol(self):
        """SPEC-S093: &sticky_key_oneshot LSFT should show one-shot shift symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&sticky_key_oneshot LSFT", os_style="mac")
        # Should show sticky/one-shot indicator with shift
        assert "⇧" in result or "Sft" in result
        assert len(result) <= 6


class TestSelectExtendBehaviors:
    """Tests for select_* and extend_* behavior display."""

    def test_select_word_right_shows_symbol(self):
        """SPEC-S094: &select_word_right should show select word symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&select_word_right")
        # Should be short, show selection + direction
        assert "→" in result or "R" in result or "right" in result.lower()
        assert len(result) <= 8

    def test_select_line_right_shows_symbol(self):
        """SPEC-S095: &select_line_right should show select line symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&select_line_right")
        assert len(result) <= 8

    def test_select_none_shows_symbol(self):
        """SPEC-S096: &select_none should show deselect symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&select_none")
        assert len(result) <= 6

    def test_extend_word_right_shows_symbol(self):
        """SPEC-S097: &extend_word_right should show extend word symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&extend_word_right")
        assert len(result) <= 8

    def test_extend_line_right_shows_symbol(self):
        """SPEC-S098: &extend_line_right should show extend line symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&extend_line_right")
        assert len(result) <= 8


class TestFingerTapBehaviors:
    """Tests for left_*/right_* finger tap behaviors."""

    def test_left_pinky_tap_shows_key(self):
        """SPEC-S099: &left_pinky_tap X should show the key X."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&left_pinky_tap A")
        assert result == "A"

    def test_left_ringy_tap_shows_key(self):
        """SPEC-S100: &left_ringy_tap shows the key."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&left_ringy_tap TAB")
        assert result == "⇥"  # Tab symbol

    def test_right_pinky_tap_shows_key(self):
        """SPEC-S101: &right_pinky_tap shows the key."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&right_pinky_tap ENTER")
        assert result == "↵"  # Enter symbol

    def test_left_middy_tap_shows_key(self):
        """SPEC-S102: &left_middy_tap shows the key."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&left_middy_tap UP")
        assert result == "↑"

    def test_left_index_tap_shows_key(self):
        """SPEC-S103: &left_index_tap shows the key."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&left_index_tap SPACE")
        assert result == "␣"


class TestMouseKeyDisplay:
    """Tests for mouse key display - msc, mmv, mkp behaviors."""

    def test_mouse_scroll_up_shows_symbol(self):
        """SPEC-S104: &msc SCRL_UP should show scroll up symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&msc SCRL_UP")
        # Should show scroll + direction
        assert "↑" in result or "U" in result.upper()
        assert len(result) <= 6

    def test_mouse_scroll_down_shows_symbol(self):
        """SPEC-S105: &msc SCRL_DOWN should show scroll down symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&msc SCRL_DOWN")
        assert "↓" in result or "D" in result.upper()
        assert len(result) <= 6

    def test_mouse_scroll_left_shows_symbol(self):
        """SPEC-S106: &msc SCRL_LEFT should show scroll left symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&msc SCRL_LEFT")
        assert "←" in result or "L" in result.upper()
        assert len(result) <= 6

    def test_mouse_scroll_right_shows_symbol(self):
        """SPEC-S107: &msc SCRL_RIGHT should show scroll right symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&msc SCRL_RIGHT")
        assert "→" in result or "R" in result.upper()
        assert len(result) <= 6

    def test_mouse_move_up_shows_symbol(self):
        """SPEC-S108: &mmv MOVE_UP should show mouse move up symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&mmv MOVE_UP")
        assert "↑" in result or "U" in result.upper()
        assert len(result) <= 6

    def test_mouse_move_down_shows_symbol(self):
        """SPEC-S109: &mmv MOVE_DOWN should show mouse move down symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&mmv MOVE_DOWN")
        assert "↓" in result or "D" in result.upper()
        assert len(result) <= 6

    def test_mouse_click_left_shows_symbol(self):
        """SPEC-S110: &mkp LCLK should show left click symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&mkp LCLK")
        # Should show mouse + left click
        assert len(result) <= 6

    def test_mouse_click_right_shows_symbol(self):
        """SPEC-S111: &mkp RCLK should show right click symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&mkp RCLK")
        assert len(result) <= 6

    def test_mouse_click_middle_shows_symbol(self):
        """SPEC-S112: &mkp MCLK should show middle click symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&mkp MCLK")
        assert len(result) <= 6

    def test_mouse_button_4_shows_symbol(self):
        """SPEC-S113: &mkp MB4 should show back button symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&mkp MB4")
        assert len(result) <= 6

    def test_mouse_button_5_shows_symbol(self):
        """SPEC-S114: &mkp MB5 should show forward button symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&mkp MB5")
        assert len(result) <= 6


class TestEmojiMacroDisplay:
    """Tests for emoji macro display - should show actual emoji."""

    def test_emoji_heart_shows_emoji(self):
        """SPEC-S115: &emoji_heart_macro should show ❤ emoji."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&emoji_heart_macro")
        assert result == "❤" or result == "❤️"

    def test_emoji_fire_shows_emoji(self):
        """SPEC-S116: &emoji_fire_macro should show 🔥 emoji."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&emoji_fire_macro")
        assert result == "🔥"

    def test_emoji_thumbs_up_shows_emoji(self):
        """SPEC-S117: &emoji_thumbs_up_macro should show 👍 emoji."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&emoji_thumbs_up_macro")
        assert result == "👍"

    def test_emoji_tada_shows_emoji(self):
        """SPEC-S118: &emoji_tada_macro should show 🎉 emoji."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&emoji_tada_macro")
        assert result == "🎉"

    def test_emoji_sunny_shows_emoji(self):
        """SPEC-S119: &emoji_sunny_macro should show ☀ emoji."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&emoji_sunny_macro")
        assert result in ["☀", "☀️"]

    def test_emoji_cloudy_shows_emoji(self):
        """SPEC-S120: &emoji_cloudy_macro should show ☁ emoji."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&emoji_cloudy_macro")
        assert result in ["☁", "☁️"]

    def test_emoji_rainbow_shows_emoji(self):
        """SPEC-S121: &emoji_rainbow_macro should show 🌈 emoji."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&emoji_rainbow_macro")
        assert result == "🌈"

    def test_emoji_muscle_shows_emoji(self):
        """SPEC-S122: &emoji_muscle_macro should show 💪 emoji."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&emoji_muscle_macro")
        assert result == "💪"

    def test_emoji_rocket_shows_emoji(self):
        """SPEC-S123: &emoji_rocket_macro should show 🚀 emoji."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&emoji_rocket_macro")
        assert result == "🚀"

    def test_emoji_moon_shows_emoji(self):
        """SPEC-S124: &emoji_full_moon_macro should show 🌕 emoji."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&emoji_full_moon_macro")
        assert result in ["🌕", "🌝"]


class TestWorldMacroDisplay:
    """Tests for world/international character macros."""

    def test_world_degree_sign_shows_symbol(self):
        """SPEC-S125: &world_degree_sign_macro should show ° symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&world_degree_sign_macro")
        assert result == "°"

    def test_world_a_acute_lower_shows_char(self):
        """SPEC-S126: &world_a_acute_lower_macro should show á."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&world_a_acute_lower_macro")
        assert result == "á"

    def test_world_e_acute_lower_shows_char(self):
        """SPEC-S127: &world_e_acute_lower_macro should show é."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&world_e_acute_lower_macro")
        assert result == "é"

    def test_world_i_acute_lower_shows_char(self):
        """SPEC-S128: &world_i_acute_lower_macro should show í."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&world_i_acute_lower_macro")
        assert result == "í"

    def test_world_o_acute_lower_shows_char(self):
        """SPEC-S129: &world_o_acute_lower_macro should show ó."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&world_o_acute_lower_macro")
        assert result == "ó"

    def test_world_u_acute_lower_shows_char(self):
        """SPEC-S130: &world_u_acute_lower_macro should show ú."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&world_u_acute_lower_macro")
        assert result == "ú"

    def test_world_cedilla_lower_shows_char(self):
        """SPEC-S131: &world_consonants_cedilla_lower_macro should show ç."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&world_consonants_cedilla_lower_macro")
        assert result == "ç"

    def test_world_copyright_shows_symbol(self):
        """SPEC-S132: &world_sign_copyright_regular_macro should show ©."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&world_sign_copyright_regular_macro")
        assert result == "©"

    def test_world_ntilde_shows_char(self):
        """SPEC-S133: &world_consonants_ntilde_lower_macro should show ñ."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&world_consonants_ntilde_lower_macro")
        assert result == "ñ"


class TestMouseLayerNames:
    """Tests for mouse layer name display."""

    def test_mouse_slow_layer_shows_symbol(self):
        """SPEC-S134: MouseSlow layer reference should show slow mouse symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("MouseSlow")
        # Should be abbreviated
        assert len(result) <= 6
        assert "🐢" in result or "Slow" in result or "🖱" in result

    def test_mouse_fast_layer_shows_symbol(self):
        """SPEC-S135: MouseFast layer reference should show fast mouse symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("MouseFast")
        assert len(result) <= 6
        assert "🐇" in result or "Fast" in result or "🖱" in result

    def test_mouse_warp_layer_shows_symbol(self):
        """SPEC-S136: MouseWarp layer reference should show warp symbol."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("MouseWarp")
        assert len(result) <= 6


class TestEmojiPresetMacros:
    """Tests for emoji preset/modifier macros."""

    def test_skin_tone_preset_shows_symbol(self):
        """SPEC-S137: &emoji_skin_tone_preset should show skin tone indicator."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&emoji_skin_tone_preset")
        assert len(result) <= 4
        assert result in ["🏻", "👤", "ST", "skin"]

    def test_zwj_macro_shows_symbol(self):
        """SPEC-S138: &emoji_zwj_macro should show ZWJ indicator."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&emoji_zwj_macro")
        assert len(result) <= 4
        assert result in ["ZWJ", "⊕", "+"]

    def test_gender_sign_preset_shows_symbol(self):
        """SPEC-S139: &emoji_gender_sign_preset should show gender indicator."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&emoji_gender_sign_preset")
        assert len(result) <= 4
        assert result in ["⚥", "♂♀", "Gen"]

    def test_hair_style_preset_shows_symbol(self):
        """SPEC-S140: &emoji_hair_style_preset should show hair style indicator."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&emoji_hair_style_preset")
        assert len(result) <= 4
        assert result in ["🦰", "Hair", "💇"]

    def test_male_sign_shows_symbol(self):
        """SPEC-S141: &emoji_male_sign_macro should show ♂."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&emoji_male_sign_macro")
        assert result == "♂"

    def test_female_sign_shows_symbol(self):
        """SPEC-S142: &emoji_female_sign_macro should show ♀."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&emoji_female_sign_macro")
        assert result == "♀"


class TestHoldBehaviors:
    """Tests for hold behavior formatting (HRM modifiers)."""

    def test_right_index_hold_shows_modifier(self):
        """SPEC-S143: &right_index_hold LSFT should show just the modifier."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&right_index_hold LSFT", os_style="mac")
        assert result == "⇧"

    def test_right_middy_hold_shows_modifier(self):
        """SPEC-S144: &right_middy_hold LGUI should show just the modifier."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&right_middy_hold LGUI", os_style="mac")
        assert result == "⌘"

    def test_right_ringy_hold_shows_modifier(self):
        """SPEC-S145: &right_ringy_hold LALT should show just the modifier."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&right_ringy_hold LALT", os_style="mac")
        assert result == "⌥"

    def test_right_pinky_hold_shows_modifier(self):
        """SPEC-S146: &right_pinky_hold LCTL should show just the modifier."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&right_pinky_hold LCTL", os_style="mac")
        assert result == "⌃"

    def test_left_index_hold_shows_modifier(self):
        """SPEC-S147: &left_index_hold RSFT should show just the modifier."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&left_index_hold RSFT", os_style="mac")
        assert result == "⇧"

    def test_left_middy_hold_shows_modifier(self):
        """SPEC-S148: &left_middy_hold RGUI should show just the modifier."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&left_middy_hold RGUI", os_style="mac")
        assert result == "⌘"


class TestMoreEmojiMacros:
    """Tests for additional emoji macros found in keymap."""

    def test_snap_fingers_shows_emoji(self):
        """SPEC-S149: &emoji_snap_fingers_macro should show emoji."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&emoji_snap_fingers_macro")
        assert result in ["🫰", "👌", "✌"]

    def test_disappointed_shows_emoji(self):
        """SPEC-S150: &emoji_disappointed_macro should show emoji."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&emoji_disappointed_macro")
        assert result in ["😞", "😔", "☹"]

    def test_shocked_face_shows_emoji(self):
        """SPEC-S151: &emoji_shocked_face_macro should show emoji."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&emoji_shocked_face_macro")
        assert result in ["😲", "😱", "😮"]

    def test_face_joke_wink_shows_emoji(self):
        """SPEC-S152: &emoji_face_joke_wink_macro should show emoji."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&emoji_face_joke_wink_macro")
        assert result in ["😜", "😉", "😏"]

    def test_face_fear_scared_shows_emoji(self):
        """SPEC-S153: &emoji_face_fear_scared_macro should show emoji."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&emoji_face_fear_scared_macro")
        assert result in ["😨", "😰", "😱"]


class TestFallbackBranches:
    """Tests for fallback/default branches to achieve 100% coverage."""

    def test_emoji_macro_no_match_returns_default(self):
        """Emoji macro without proper pattern returns default emoji."""
        from glove80_visualizer.svg_generator import _format_emoji_macro

        # Missing _macro suffix - won't match regex
        result = _format_emoji_macro("&emoji_heart")
        assert result == "😀"

    def test_emoji_macro_unknown_name_returns_default(self):
        """Unknown emoji name returns default emoji."""
        from glove80_visualizer.svg_generator import _format_emoji_macro

        result = _format_emoji_macro("&emoji_nonexistent_thing_macro")
        assert result == "😀"

    def test_world_macro_no_match_returns_default(self):
        """World macro without proper pattern returns ?."""
        from glove80_visualizer.svg_generator import _format_world_macro

        # Missing _macro suffix
        result = _format_world_macro("&world_a_acute")
        assert result == "?"

    def test_world_macro_unknown_name_returns_default(self):
        """Unknown world character returns ?."""
        from glove80_visualizer.svg_generator import _format_world_macro

        result = _format_world_macro("&world_nonexistent_char_macro")
        assert result == "?"

    def test_mouse_scroll_no_args_returns_default(self):
        """Mouse scroll without direction returns default symbol."""
        from glove80_visualizer.svg_generator import _format_mouse_scroll

        result = _format_mouse_scroll("&msc")
        assert result == "⊘"

    def test_mouse_scroll_unknown_direction_returns_default(self):
        """Mouse scroll with unknown direction returns default."""
        from glove80_visualizer.svg_generator import _format_mouse_scroll

        result = _format_mouse_scroll("&msc UNKNOWN_DIR")
        assert result == "⊘"

    def test_mouse_move_no_args_returns_default(self):
        """Mouse move without direction returns default symbol."""
        from glove80_visualizer.svg_generator import _format_mouse_move

        result = _format_mouse_move("&mmv")
        assert result == "🖱"

    def test_mouse_move_unknown_direction_returns_default(self):
        """Mouse move with unknown direction returns default."""
        from glove80_visualizer.svg_generator import _format_mouse_move

        result = _format_mouse_move("&mmv UNKNOWN_DIR")
        assert result == "🖱"

    def test_mouse_click_no_args_returns_default(self):
        """Mouse click without button returns default symbol."""
        from glove80_visualizer.svg_generator import _format_mouse_click

        result = _format_mouse_click("&mkp")
        assert result == "🖱"

    def test_mouse_click_unknown_button_returns_default(self):
        """Mouse click with unknown button returns default."""
        from glove80_visualizer.svg_generator import _format_mouse_click

        result = _format_mouse_click("&mkp UNKNOWN_BTN")
        assert result == "🖱"

    def test_select_behavior_unknown_returns_default(self):
        """Unknown select behavior returns Sel."""
        from glove80_visualizer.svg_generator import _format_select_behavior

        result = _format_select_behavior("&select_unknown")
        assert result == "Sel"

    def test_extend_behavior_unknown_returns_default(self):
        """Unknown extend behavior returns Ext."""
        from glove80_visualizer.svg_generator import _format_extend_behavior

        result = _format_extend_behavior("&extend_unknown")
        assert result == "Ext"

    def test_modifier_combo_single_part_returns_as_is(self):
        """Modifier combo without + returns as-is."""
        from glove80_visualizer.svg_generator import _format_modifier_combo

        result = _format_modifier_combo("A", "mac")
        assert result == "A"

    def test_modifier_combo_meh_in_combo(self):
        """Modifier combo with Meh works correctly."""
        from glove80_visualizer.svg_generator import _format_modifier_combo

        result = _format_modifier_combo("Meh+A", "mac")
        assert result == "⌃⌥⇧A"

    def test_modifier_combo_hyper_in_combo(self):
        """Modifier combo with Hyper works correctly."""
        from glove80_visualizer.svg_generator import _format_modifier_combo

        result = _format_modifier_combo("Hyper+A", "mac")
        assert result == "⌃⌥⇧⌘A"

    def test_modifier_combo_unknown_modifier(self):
        """Unknown modifier in combo gets truncated."""
        from glove80_visualizer.svg_generator import _format_modifier_combo

        result = _format_modifier_combo("Unknown+A", "mac")
        assert result == "UnkA"  # First 3 chars + key

    def test_behavior_with_args_but_empty_abbrev(self):
        """Behavior with empty abbreviation just shows the arg."""
        from glove80_visualizer.svg_generator import format_key_label

        # &kp has empty abbrev, so just shows the key
        result = format_key_label("&kp A")
        assert result == "A"

    def test_behavior_exact_match_with_args_no_abbrev(self):
        """Behavior exact match with args but no abbrev returns formatted arg."""
        from glove80_visualizer.svg_generator import format_key_label

        # &lt has empty abbrev
        result = format_key_label("&lt 1 A")
        assert "A" in result or "1" in result

    def test_behavior_exact_match_no_args_no_abbrev(self):
        """Behavior exact match with no args and no abbrev returns name."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("&kp")
        assert result == "kp"

    def test_emoji_preset_unknown_returns_default(self):
        """Unknown emoji preset returns default emoji."""
        from glove80_visualizer.svg_generator import _format_emoji_preset

        result = _format_emoji_preset("&emoji_unknown_preset")
        assert result == "😀"

    def test_generate_all_layer_svgs_uses_first_layer_as_base(self):
        """generate_all_layer_svgs uses first layer as base if no index 0."""
        from glove80_visualizer.svg_generator import generate_all_layer_svgs
        from glove80_visualizer.models import Layer, KeyBinding

        # Create layers without index 0
        layer1 = Layer(name="Layer1", index=1, bindings=[
            KeyBinding(position=0, tap="A")
        ])
        layer2 = Layer(name="Layer2", index=2, bindings=[
            KeyBinding(position=0, tap="&trans")
        ])

        # Should not raise, uses layer1 as fallback base
        result = generate_all_layer_svgs([layer1, layer2], resolve_trans=True)
        assert len(result) == 2

    def test_generate_all_layer_svgs_finds_index_0_layer(self):
        """generate_all_layer_svgs finds layer with index 0 as base."""
        from glove80_visualizer.svg_generator import generate_all_layer_svgs
        from glove80_visualizer.models import Layer, KeyBinding

        # Create layers with index 0 not first in list
        layer0 = Layer(name="Base", index=0, bindings=[
            KeyBinding(position=0, tap="B")
        ])
        layer1 = Layer(name="Layer1", index=1, bindings=[
            KeyBinding(position=0, tap="&trans")
        ])

        # Should find index 0 even if it's second in list
        result = generate_all_layer_svgs([layer1, layer0], resolve_trans=True)
        assert len(result) == 2

    def test_behavior_with_abbrev_and_args(self):
        """Behavior with abbreviation and args combines them."""
        from glove80_visualizer.svg_generator import format_key_label

        # &bt with args should show BT prefix
        result = format_key_label("&bt BT_SEL 0")
        assert "BT" in result

    def test_behavior_prefix_match_sticky_key(self):
        """Prefix match for sticky key variations."""
        from glove80_visualizer.svg_generator import format_key_label

        # sticky_key prefix match
        result = format_key_label("&sticky_key_variant LSFT", os_style="mac")
        assert "●" in result or "⇧" in result


class TestResolveTransparentKeys:
    """Tests for transparent key resolution edge cases."""

    def test_resolve_trans_base_layer_also_transparent(self):
        """When base layer key is also transparent, keep it transparent."""
        from glove80_visualizer.svg_generator import _resolve_transparent_keys
        from glove80_visualizer.models import Layer, KeyBinding

        base_layer = Layer(name="Base", index=0, bindings=[
            KeyBinding(position=0, tap="&trans"),  # Base is also transparent
        ])
        overlay = Layer(name="Overlay", index=1, bindings=[
            KeyBinding(position=0, tap="&trans"),
        ])

        result = _resolve_transparent_keys(overlay, base_layer)
        assert result.bindings[0].tap == "&trans"

    def test_resolve_trans_missing_position_in_base(self):
        """When position doesn't exist in base, keep transparent."""
        from glove80_visualizer.svg_generator import _resolve_transparent_keys
        from glove80_visualizer.models import Layer, KeyBinding

        base_layer = Layer(name="Base", index=0, bindings=[
            KeyBinding(position=0, tap="A"),
        ])
        overlay = Layer(name="Overlay", index=1, bindings=[
            KeyBinding(position=0, tap="&trans"),
            KeyBinding(position=1, tap="&trans"),  # No position 1 in base
        ])

        result = _resolve_transparent_keys(overlay, base_layer)
        assert result.bindings[0].tap == "A"  # Resolved
        assert result.bindings[1].tap == "&trans"  # Kept transparent


class TestHeldKeyIndicator:
    """Tests for held key indicator in layer diagrams."""

    def test_held_key_has_fingerprint_glyph(self):
        """SPEC-HK-006: Held key position shows inlined fingerprint SVG."""
        from glove80_visualizer.svg_generator import generate_layer_svg
        from glove80_visualizer.models import Layer, KeyBinding, LayerActivator
        from glove80_visualizer.config import VisualizerConfig

        layer = Layer(name="Cursor", index=1, bindings=[
            KeyBinding(position=i, tap="A") for i in range(80)
        ])
        # Position 69 is the held key
        activators = [LayerActivator(
            source_layer_name="QWERTY",
            source_position=69,
            target_layer_name="Cursor",
            tap_key="BACKSPACE"
        )]
        config = VisualizerConfig(show_held_indicator=True)

        svg = generate_layer_svg(layer, config=config, activators=activators)

        # Should contain inlined fingerprint SVG path (for CairoSVG compatibility)
        # The path starts with M17.81 from the MDI fingerprint icon
        assert "M17.81" in svg
        # Should NOT contain <use> element (replaced with inline)
        assert '<use href="#mdi:fingerprint"' not in svg

    def test_inline_fingerprint_glyphs_function(self):
        """SPEC-HK-015: _inline_fingerprint_glyphs replaces use elements with paths."""
        from glove80_visualizer.svg_generator import _inline_fingerprint_glyphs

        # Simulated SVG with <use> element
        svg_input = '''<svg>
<svg id="mdi:fingerprint"><path d="test"/></svg>
<use href="#mdi:fingerprint" xlink:href="#mdi:fingerprint" x="-16" y="-16" height="32" width="32.0" class="test"/>
</svg>'''

        result = _inline_fingerprint_glyphs(svg_input)

        # Should have inline path
        assert "M17.81" in result
        # Should not have <use> element
        assert '<use href="#mdi:fingerprint"' not in result
        # Should not have nested SVG definition
        assert 'id="mdi:fingerprint"' not in result

    def test_held_key_has_held_type(self):
        """SPEC-HK-008: Held key gets type='held' for red shading."""
        from glove80_visualizer.svg_generator import _binding_to_keymap_drawer
        from glove80_visualizer.models import KeyBinding
        from glove80_visualizer.config import VisualizerConfig

        binding = KeyBinding(position=69, tap="A")
        config = VisualizerConfig(show_held_indicator=True)
        held_positions = {69}

        result = _binding_to_keymap_drawer(binding, "mac", config, held_positions)

        assert isinstance(result, dict)
        assert result.get("type") == "held"

    def test_held_key_shows_fingerprint_tap_and_layer_hold(self):
        """SPEC-HK-009: Held key shows fingerprint as tap and 'Layer' as hold."""
        from glove80_visualizer.svg_generator import _binding_to_keymap_drawer
        from glove80_visualizer.models import KeyBinding
        from glove80_visualizer.config import VisualizerConfig

        binding = KeyBinding(position=69, tap="A")
        config = VisualizerConfig(show_held_indicator=True)
        held_positions = {69}

        result = _binding_to_keymap_drawer(binding, "mac", config, held_positions)

        assert isinstance(result, dict)
        # Fingerprint glyph should be the main tap content
        assert "$$mdi:fingerprint$$" in result.get("t", "")
        # "Layer" text should be in hold position (below)
        assert result.get("h") == "Layer"

    def test_held_indicator_disabled(self):
        """SPEC-HK-007: Held indicator can be disabled."""
        from glove80_visualizer.svg_generator import _binding_to_keymap_drawer
        from glove80_visualizer.models import KeyBinding
        from glove80_visualizer.config import VisualizerConfig

        binding = KeyBinding(position=69, tap="A")
        config = VisualizerConfig(show_held_indicator=False)
        held_positions = {69}

        result = _binding_to_keymap_drawer(binding, "mac", config, held_positions)

        # Should NOT have held type or fingerprint when disabled
        if isinstance(result, dict):
            assert result.get("type") != "held"
            assert "fingerprint" not in result.get("t", "")
        else:
            # Simple string without held indicator
            assert result == "A"

    def test_non_held_key_no_fingerprint(self):
        """SPEC-HK-010: Non-held keys don't get fingerprint."""
        from glove80_visualizer.svg_generator import _binding_to_keymap_drawer
        from glove80_visualizer.models import KeyBinding
        from glove80_visualizer.config import VisualizerConfig

        binding = KeyBinding(position=10, tap="B")  # Not position 69
        config = VisualizerConfig(show_held_indicator=True)
        held_positions = {69}  # Only 69 is held

        result = _binding_to_keymap_drawer(binding, "mac", config, held_positions)

        # Should NOT have held type or fingerprint
        if isinstance(result, dict):
            assert result.get("type") != "held"
            assert "fingerprint" not in result.get("t", "")
        else:
            # Simple string is fine for non-held keys
            assert result == "B"

    def test_held_indicator_no_activators(self):
        """SVG generates without activators parameter."""
        from glove80_visualizer.svg_generator import generate_layer_svg
        from glove80_visualizer.models import Layer, KeyBinding

        layer = Layer(name="Test", index=0, bindings=[
            KeyBinding(position=i, tap="X") for i in range(80)
        ])

        # Should not raise
        svg = generate_layer_svg(layer)
        assert "</svg>" in svg

    def test_multiple_held_keys(self):
        """SPEC-HK-011: Multiple held positions all get indicators."""
        from glove80_visualizer.svg_generator import _binding_to_keymap_drawer
        from glove80_visualizer.models import KeyBinding
        from glove80_visualizer.config import VisualizerConfig

        config = VisualizerConfig(show_held_indicator=True)
        held_positions = {10, 20, 30}

        # Check each held position
        for pos in held_positions:
            binding = KeyBinding(position=pos, tap="X")
            result = _binding_to_keymap_drawer(binding, "mac", config, held_positions)
            assert isinstance(result, dict)
            assert result.get("type") == "held"
            assert "$$mdi:fingerprint$$" in result.get("t", "")
            assert result.get("h") == "Layer"

    def test_held_key_with_hold_behavior(self):
        """SPEC-HK-012: Held key with hold behavior still gets fingerprint."""
        from glove80_visualizer.svg_generator import _binding_to_keymap_drawer
        from glove80_visualizer.models import KeyBinding
        from glove80_visualizer.config import VisualizerConfig

        # Key with both tap and hold, and it's a held position
        binding = KeyBinding(position=69, tap="BACKSPACE", hold="Cursor")
        config = VisualizerConfig(show_held_indicator=True)
        held_positions = {69}

        result = _binding_to_keymap_drawer(binding, "mac", config, held_positions)

        assert isinstance(result, dict)
        assert result.get("type") == "held"
        # Fingerprint replaces normal tap content
        assert "$$mdi:fingerprint$$" in result.get("t", "")
        # "Layer" replaces original hold content
        assert result.get("h") == "Layer"

    def test_held_key_transparent_shows_fingerprint(self):
        """SPEC-HK-013: Held key that is transparent still shows fingerprint."""
        from glove80_visualizer.svg_generator import _binding_to_keymap_drawer
        from glove80_visualizer.models import KeyBinding
        from glove80_visualizer.config import VisualizerConfig

        # Transparent key at held position
        binding = KeyBinding(position=69, tap="&trans")
        config = VisualizerConfig(show_held_indicator=True)
        held_positions = {69}

        result = _binding_to_keymap_drawer(binding, "mac", config, held_positions)

        assert isinstance(result, dict)
        assert result.get("type") == "held"
        assert "$$mdi:fingerprint$$" in result.get("t", "")
        assert result.get("h") == "Layer"

    def test_held_key_none_shows_fingerprint(self):
        """SPEC-HK-014: Held key that is &none still shows fingerprint."""
        from glove80_visualizer.svg_generator import _binding_to_keymap_drawer
        from glove80_visualizer.models import KeyBinding
        from glove80_visualizer.config import VisualizerConfig

        # &none key at held position
        binding = KeyBinding(position=69, tap="")
        config = VisualizerConfig(show_held_indicator=True)
        held_positions = {69}

        result = _binding_to_keymap_drawer(binding, "mac", config, held_positions)

        assert isinstance(result, dict)
        assert result.get("type") == "held"
        assert "$$mdi:fingerprint$$" in result.get("t", "")
        assert result.get("h") == "Layer"


class TestEmojiReplacement:
    """Tests for emoji to text replacement for CairoSVG compatibility."""

    def test_emoji_replaced_with_text(self):
        """SPEC-ER-001: Emoji characters are replaced with text equivalents."""
        from glove80_visualizer.svg_generator import _replace_emoji_for_cairo

        svg = '<text>😀</text><text>🌍</text><text>⚙</text>'
        result = _replace_emoji_for_cairo(svg)

        assert "😀" not in result
        assert "🌍" not in result
        assert "⚙" not in result
        assert "Emoji" in result
        assert "World" in result
        assert "Sys" in result

    def test_mouse_emoji_replaced(self):
        """SPEC-ER-002: Mouse emoji is replaced with text."""
        from glove80_visualizer.svg_generator import _replace_emoji_for_cairo

        svg = '<text>🖱</text>'
        result = _replace_emoji_for_cairo(svg)

        assert "🖱" not in result
        assert "Mouse" in result

    def test_magic_emoji_replaced(self):
        """SPEC-ER-003: Magic/sparkles emoji is replaced with text."""
        from glove80_visualizer.svg_generator import _replace_emoji_for_cairo

        svg = '<text>✨</text>'
        result = _replace_emoji_for_cairo(svg)

        assert "✨" not in result
        assert "Magic" in result

    def test_volume_emoji_replaced(self):
        """SPEC-ER-004: Volume emoji characters are replaced with text."""
        from glove80_visualizer.svg_generator import _replace_emoji_for_cairo

        svg = '<text>🔊</text><text>🔇</text>'
        result = _replace_emoji_for_cairo(svg)

        assert "🔊" not in result
        assert "🔇" not in result
        assert "Vol+" in result
        assert "Mute" in result

    def test_non_emoji_text_unchanged(self):
        """SPEC-ER-005: Regular text is not modified."""
        from glove80_visualizer.svg_generator import _replace_emoji_for_cairo

        svg = '<text>Hello World</text><text>ABC</text>'
        result = _replace_emoji_for_cairo(svg)

        assert result == svg


class TestColorLegendBackground:
    """Tests for color legend background and positioning."""

    def test_legend_has_white_background(self):
        """SPEC-LB-001: Legend has a white background for readability."""
        from glove80_visualizer.svg_generator import _generate_color_legend
        from glove80_visualizer.colors import ColorScheme

        scheme = ColorScheme()
        legend_svg = _generate_color_legend(scheme)

        # Should have a background rect with white fill
        assert 'fill="white"' in legend_svg or "fill='white'" in legend_svg

    def test_legend_positioned_below_keyboard(self):
        """SPEC-LB-002: Legend is positioned below the keyboard keys (y > 545)."""
        from glove80_visualizer.svg_generator import _generate_color_legend
        from glove80_visualizer.colors import ColorScheme
        import re

        scheme = ColorScheme()
        legend_svg = _generate_color_legend(scheme)

        # Find y coordinates in the legend (exclude ry= which is corner radius)
        # Match y="..." but not ry="..."
        y_matches = re.findall(r'(?<!r)y="(\d+)"', legend_svg)
        y_values = [int(y) for y in y_matches]

        # All y values should be greater than 545 to be below the thumb cluster
        # (thumb keys extend to about 520, legend should have clearance)
        assert all(y >= 545 for y in y_values), f"Legend y values {y_values} should all be >= 545"

    def test_svg_height_increased_for_legend_padding(self):
        """SPEC-LB-003: SVG height is increased to provide padding below legend."""
        from glove80_visualizer.svg_generator import generate_layer_svg
        from glove80_visualizer.models import Layer, KeyBinding
        from glove80_visualizer.config import VisualizerConfig
        import re

        layer = Layer(name="Test", index=0, bindings=[
            KeyBinding(position=i, tap="A") for i in range(80)
        ])
        config = VisualizerConfig(show_colors=True)

        svg = generate_layer_svg(layer, config=config)

        # Extract height from SVG
        height_match = re.search(r'height="(\d+)"', svg)
        assert height_match, "SVG should have height attribute"
        height = int(height_match.group(1))

        # Height should be increased to at least 600 for legend padding
        assert height >= 600, f"SVG height {height} should be >= 600 for legend padding"

    def test_increase_svg_height_no_height_attribute(self):
        """SPEC-LB-004: _increase_svg_height handles SVG without height attribute."""
        from glove80_visualizer.svg_generator import _increase_svg_height

        svg = '<svg viewBox="0 0 100 100"></svg>'
        result = _increase_svg_height(svg, 200)

        # Should return unchanged
        assert result == svg

    def test_increase_svg_height_already_sufficient(self):
        """SPEC-LB-005: _increase_svg_height doesn't change if height already sufficient."""
        from glove80_visualizer.svg_generator import _increase_svg_height

        svg = '<svg width="100" height="700" viewBox="0 0 100 700"></svg>'
        result = _increase_svg_height(svg, 600)

        # Should return unchanged
        assert result == svg
        assert 'height="700"' in result


class TestColorLegend:
    """Tests for color legend in layer diagrams."""

    def test_color_legend_added_when_colors_enabled(self):
        """SPEC-CL-020: SVG includes color legend when show_colors is True."""
        from glove80_visualizer.svg_generator import generate_layer_svg
        from glove80_visualizer.models import Layer, KeyBinding
        from glove80_visualizer.config import VisualizerConfig

        layer = Layer(name="Test", index=0, bindings=[
            KeyBinding(position=i, tap="A") for i in range(80)
        ])
        config = VisualizerConfig(show_colors=True)

        svg = generate_layer_svg(layer, config=config)

        # Should include legend
        assert "legend" in svg.lower() or "Modifiers" in svg

    def test_color_legend_shows_categories(self):
        """SPEC-CL-021: Color legend shows all key categories."""
        from glove80_visualizer.svg_generator import generate_layer_svg
        from glove80_visualizer.models import Layer, KeyBinding
        from glove80_visualizer.config import VisualizerConfig

        layer = Layer(name="Test", index=0, bindings=[
            KeyBinding(position=i, tap="A") for i in range(80)
        ])
        config = VisualizerConfig(show_colors=True)

        svg = generate_layer_svg(layer, config=config)

        # Should show category names
        assert "Modifiers" in svg
        assert "Navigation" in svg
        assert "Layer" in svg

    def test_color_legend_not_shown_when_disabled(self):
        """SPEC-CL-022: No legend when show_colors is False."""
        from glove80_visualizer.svg_generator import generate_layer_svg
        from glove80_visualizer.models import Layer, KeyBinding
        from glove80_visualizer.config import VisualizerConfig

        layer = Layer(name="Test", index=0, bindings=[
            KeyBinding(position=i, tap="A") for i in range(80)
        ])
        config = VisualizerConfig(show_colors=False)

        svg = generate_layer_svg(layer, config=config)

        # Should NOT have legend elements
        assert "Modifiers" not in svg
        assert "Navigation" not in svg


class TestCenteredLayerName:
    """Tests for centered layer name display."""

    def test_layer_name_centered_between_hands(self):
        """SPEC-LN-001: Layer name appears centered between keyboard halves."""
        from glove80_visualizer.svg_generator import generate_layer_svg
        from glove80_visualizer.models import Layer, KeyBinding
        from glove80_visualizer.config import VisualizerConfig

        layer = Layer(name="Cursor", index=1, bindings=[
            KeyBinding(position=i, tap="A") for i in range(80)
        ])
        config = VisualizerConfig()

        svg = generate_layer_svg(layer, config=config)

        # Should have layer name in center area
        assert "Cursor" in svg
        # Should have text-anchor middle for centering
        assert 'text-anchor' in svg.lower() or 'middle' in svg.lower()

    def test_layer_label_x_position_centered(self):
        """SPEC-LN-002: Layer label x position is truly centered (around 504 for 1068px)."""
        from glove80_visualizer.svg_generator import _center_layer_label
        import re

        # Simulate input from keymap-drawer
        svg_input = '<text x="0" y="28" class="label" id="Test">Test:</text>'
        result = _center_layer_label(svg_input, "Test")

        # Extract the x value from the result
        x_match = re.search(r'x="(\d+)"', result)
        assert x_match, "Should have x coordinate in centered label"
        x_value = int(x_match.group(1))

        # True center of 1068px keyboard (minus 30px left margin) is (1068-30)/2 = 519
        # But the group already has translate(30,0), so we want 504 within the group
        # Allow tolerance for different approaches
        assert 490 <= x_value <= 540, f"Label x={x_value} should be centered (490-540)"


class TestColorOutput:
    """Tests for --color semantic coloring output."""

    def test_color_css_added_when_enabled(self):
        """SPEC-CL-013: SVG includes color CSS when show_colors is True."""
        from glove80_visualizer.svg_generator import generate_layer_svg
        from glove80_visualizer.models import Layer, KeyBinding
        from glove80_visualizer.config import VisualizerConfig

        layer = Layer(name="Test", index=0, bindings=[
            KeyBinding(position=i, tap="A") for i in range(80)
        ])
        config = VisualizerConfig(show_colors=True)

        svg = generate_layer_svg(layer, config=config)

        # Should include semantic coloring CSS
        assert "rect.modifier" in svg
        assert "rect.navigation" in svg
        assert "rect.symbol" in svg
        assert "#7fbbb3" in svg  # Modifier color

    def test_color_css_not_added_when_disabled(self):
        """SPEC-CL-014: SVG does NOT include color CSS when show_colors is False."""
        from glove80_visualizer.svg_generator import generate_layer_svg
        from glove80_visualizer.models import Layer, KeyBinding
        from glove80_visualizer.config import VisualizerConfig

        layer = Layer(name="Test", index=0, bindings=[
            KeyBinding(position=i, tap="A") for i in range(80)
        ])
        config = VisualizerConfig(show_colors=False)

        svg = generate_layer_svg(layer, config=config)

        # Should NOT include semantic coloring CSS
        assert "rect.modifier" not in svg
        assert "rect.navigation" not in svg

    def test_modifier_key_gets_modifier_type(self):
        """SPEC-CL-015: Modifier keys get type='modifier' when colors enabled."""
        from glove80_visualizer.svg_generator import _binding_to_keymap_drawer
        from glove80_visualizer.models import KeyBinding
        from glove80_visualizer.config import VisualizerConfig

        binding = KeyBinding(position=0, tap="LSHIFT")
        config = VisualizerConfig(show_colors=True)

        result = _binding_to_keymap_drawer(binding, "mac", config)

        # Should have modifier type for shift key (⇧)
        assert isinstance(result, dict)
        assert result.get("type") == "modifier"

    def test_navigation_key_gets_navigation_type(self):
        """SPEC-CL-016: Navigation keys get type='navigation' when colors enabled."""
        from glove80_visualizer.svg_generator import _binding_to_keymap_drawer
        from glove80_visualizer.models import KeyBinding
        from glove80_visualizer.config import VisualizerConfig

        binding = KeyBinding(position=0, tap="LEFT")
        config = VisualizerConfig(show_colors=True)

        result = _binding_to_keymap_drawer(binding, "mac", config)

        assert isinstance(result, dict)
        assert result.get("type") == "navigation"

    def test_alpha_key_no_type_when_colors_enabled(self):
        """SPEC-CL-017: Regular alpha keys don't get a type (default color)."""
        from glove80_visualizer.svg_generator import _binding_to_keymap_drawer
        from glove80_visualizer.models import KeyBinding
        from glove80_visualizer.config import VisualizerConfig

        binding = KeyBinding(position=0, tap="A")
        config = VisualizerConfig(show_colors=True)

        result = _binding_to_keymap_drawer(binding, "mac", config)

        # Simple string - no type field for default keys
        assert result == "A"

    def test_layer_hold_gets_layer_type(self):
        """SPEC-CL-018: Layer activator hold keys get type='layer' when colors enabled."""
        from glove80_visualizer.svg_generator import _binding_to_keymap_drawer
        from glove80_visualizer.models import KeyBinding
        from glove80_visualizer.config import VisualizerConfig

        binding = KeyBinding(position=0, tap="BACKSPACE", hold="Cursor")
        config = VisualizerConfig(show_colors=True)

        result = _binding_to_keymap_drawer(binding, "mac", config)

        assert isinstance(result, dict)
        assert result.get("type") == "layer"

    def test_generate_color_css_function(self):
        """SPEC-CL-019: _generate_color_css creates proper CSS rules."""
        from glove80_visualizer.svg_generator import _generate_color_css
        from glove80_visualizer.colors import ColorScheme

        scheme = ColorScheme()
        css = _generate_color_css(scheme)

        # Should have rules for all categories
        assert "rect.modifier" in css
        assert "rect.layer" in css
        assert "rect.navigation" in css
        assert "rect.symbol" in css
        assert "rect.number" in css
        assert "rect.media" in css
        assert "rect.mouse" in css
        assert "rect.system" in css
        assert "rect.trans" in css

        # Should use scheme colors
        assert scheme.modifier_color in css
        assert scheme.navigation_color in css


class TestMehHyperCombos:
    """Tests for MEH and HYPER combo expansion."""

    def test_meh_combo_mac(self):
        """SPEC-KC-005: MEH(key) expands to Ctrl+Alt+Shift on Mac."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("MEH(K)", os_style="mac")
        assert result == "⌃⌥⇧K"

    def test_meh_combo_windows(self):
        """SPEC-KC-005: MEH(key) expands correctly on Windows."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("MEH(K)", os_style="windows")
        assert "Ctrl" in result and "Alt" in result and "Shift" in result

    def test_hyper_combo_mac(self):
        """SPEC-KC-006: HYPER(key) expands to all modifiers on Mac."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("HYPER(K)", os_style="mac")
        assert result == "⌃⌥⇧⌘K"

    def test_hyper_combo_windows(self):
        """SPEC-KC-006: HYPER(key) expands correctly on Windows."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("HYPER(K)", os_style="windows")
        assert "Ctrl" in result and "Alt" in result and "Shift" in result and "Win" in result

    def test_meh_with_special_key(self):
        """SPEC-KC-007: MEH works with special keys."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("MEH(SPACE)", os_style="mac")
        assert "⌃⌥⇧" in result
        # SPACE should be formatted as ␣
        assert "␣" in result

    def test_hyper_with_special_key(self):
        """SPEC-KC-007: HYPER works with special keys."""
        from glove80_visualizer.svg_generator import format_key_label

        result = format_key_label("HYPER(ENTER)", os_style="mac")
        assert "⌃⌥⇧⌘" in result
        # ENTER should be formatted as ↵
        assert "↵" in result


class TestShiftedKeyPairs:
    """Tests for showing shifted character variants on keys.

    When enabled, non-alpha keys show both their unshifted and shifted
    characters, e.g., ' shows as " above ' (like a physical keyboard).
    """

    def test_get_shifted_char_single_quote(self):
        """SPEC-SK-001: Single quote returns double quote as shifted variant."""
        from glove80_visualizer.svg_generator import get_shifted_char

        assert get_shifted_char("'") == '"'

    def test_get_shifted_char_number_1(self):
        """SPEC-SK-002: Number 1 returns ! as shifted variant."""
        from glove80_visualizer.svg_generator import get_shifted_char

        assert get_shifted_char("1") == "!"

    def test_get_shifted_char_number_2(self):
        """SPEC-SK-003: Number 2 returns @ as shifted variant."""
        from glove80_visualizer.svg_generator import get_shifted_char

        assert get_shifted_char("2") == "@"

    def test_get_shifted_char_semicolon(self):
        """SPEC-SK-004: Semicolon returns colon as shifted variant."""
        from glove80_visualizer.svg_generator import get_shifted_char

        assert get_shifted_char(";") == ":"

    def test_get_shifted_char_comma(self):
        """SPEC-SK-005: Comma returns < as shifted variant."""
        from glove80_visualizer.svg_generator import get_shifted_char

        assert get_shifted_char(",") == "<"

    def test_get_shifted_char_period(self):
        """SPEC-SK-006: Period returns > as shifted variant."""
        from glove80_visualizer.svg_generator import get_shifted_char

        assert get_shifted_char(".") == ">"

    def test_get_shifted_char_slash(self):
        """SPEC-SK-007: Slash returns ? as shifted variant."""
        from glove80_visualizer.svg_generator import get_shifted_char

        assert get_shifted_char("/") == "?"

    def test_get_shifted_char_backtick(self):
        """SPEC-SK-008: Backtick returns ~ as shifted variant."""
        from glove80_visualizer.svg_generator import get_shifted_char

        assert get_shifted_char("`") == "~"

    def test_get_shifted_char_minus(self):
        """SPEC-SK-009: Minus returns underscore as shifted variant."""
        from glove80_visualizer.svg_generator import get_shifted_char

        assert get_shifted_char("-") == "_"

    def test_get_shifted_char_equals(self):
        """SPEC-SK-010: Equals returns + as shifted variant."""
        from glove80_visualizer.svg_generator import get_shifted_char

        assert get_shifted_char("=") == "+"

    def test_get_shifted_char_left_bracket(self):
        """SPEC-SK-011: Left bracket returns { as shifted variant."""
        from glove80_visualizer.svg_generator import get_shifted_char

        assert get_shifted_char("[") == "{"

    def test_get_shifted_char_right_bracket(self):
        """SPEC-SK-012: Right bracket returns } as shifted variant."""
        from glove80_visualizer.svg_generator import get_shifted_char

        assert get_shifted_char("]") == "}"

    def test_get_shifted_char_backslash(self):
        """SPEC-SK-013: Backslash returns | as shifted variant."""
        from glove80_visualizer.svg_generator import get_shifted_char

        assert get_shifted_char("\\") == "|"

    def test_get_shifted_char_alpha_returns_none(self):
        """SPEC-SK-014: Alpha characters return None (no shifted display)."""
        from glove80_visualizer.svg_generator import get_shifted_char

        assert get_shifted_char("a") is None
        assert get_shifted_char("A") is None
        assert get_shifted_char("z") is None

    def test_get_shifted_char_unknown_returns_none(self):
        """SPEC-SK-015: Unknown characters return None."""
        from glove80_visualizer.svg_generator import get_shifted_char

        assert get_shifted_char("⌘") is None
        assert get_shifted_char("↵") is None
        assert get_shifted_char("trans") is None

    def test_get_shifted_char_all_numbers(self):
        """SPEC-SK-016: All number keys have correct shifted variants."""
        from glove80_visualizer.svg_generator import get_shifted_char

        expected = {
            "1": "!",
            "2": "@",
            "3": "#",
            "4": "$",
            "5": "%",
            "6": "^",
            "7": "&",
            "8": "*",
            "9": "(",
            "0": ")",
        }
        for num, symbol in expected.items():
            assert get_shifted_char(num) == symbol, f"Expected {num} -> {symbol}"


class TestShiftedKeyInSvg:
    """Tests for rendering shifted characters in SVG output."""

    def test_binding_with_shifted_field(self):
        """SPEC-SK-020: KeyBinding with shifted field passes to keymap-drawer."""
        from glove80_visualizer.models import KeyBinding
        from glove80_visualizer.svg_generator import _binding_to_keymap_drawer

        binding = KeyBinding(position=0, tap="'", shifted='"')
        result = _binding_to_keymap_drawer(binding, os_style="mac")

        assert isinstance(result, dict)
        assert result.get("t") == "'"
        assert result.get("shifted") == '"'

    def test_binding_with_shifted_and_hold(self):
        """SPEC-SK-021: KeyBinding with shifted AND hold fields renders both."""
        from glove80_visualizer.models import KeyBinding
        from glove80_visualizer.svg_generator import _binding_to_keymap_drawer

        binding = KeyBinding(position=0, tap="1", hold="LSHIFT", shifted="!")
        result = _binding_to_keymap_drawer(binding, os_style="mac")

        assert isinstance(result, dict)
        assert result.get("t") == "1"
        assert result.get("h") == "⇧"
        assert result.get("shifted") == "!"

    def test_binding_without_shifted_no_shifted_field(self):
        """SPEC-SK-022: KeyBinding without shifted doesn't add shifted field."""
        from glove80_visualizer.models import KeyBinding
        from glove80_visualizer.svg_generator import _binding_to_keymap_drawer

        binding = KeyBinding(position=0, tap="A")
        result = _binding_to_keymap_drawer(binding, os_style="mac")

        # Simple string or dict without shifted
        if isinstance(result, dict):
            assert "shifted" not in result
        else:
            assert isinstance(result, str)

    def test_auto_shifted_for_number_key(self):
        """SPEC-SK-023: With show_shifted=True, number keys auto-populate shifted."""
        from glove80_visualizer.models import KeyBinding
        from glove80_visualizer.svg_generator import _binding_to_keymap_drawer

        binding = KeyBinding(position=0, tap="1")
        result = _binding_to_keymap_drawer(binding, os_style="mac", show_shifted=True)

        assert isinstance(result, dict)
        assert result.get("t") == "1"
        assert result.get("shifted") == "!"

    def test_auto_shifted_for_punctuation(self):
        """SPEC-SK-024: With show_shifted=True, punctuation auto-populates shifted."""
        from glove80_visualizer.models import KeyBinding
        from glove80_visualizer.svg_generator import _binding_to_keymap_drawer

        binding = KeyBinding(position=0, tap=";")
        result = _binding_to_keymap_drawer(binding, os_style="mac", show_shifted=True)

        assert isinstance(result, dict)
        assert result.get("t") == ";"
        assert result.get("shifted") == ":"

    def test_auto_shifted_skips_alpha(self):
        """SPEC-SK-025: With show_shifted=True, alpha keys don't get shifted field."""
        from glove80_visualizer.models import KeyBinding
        from glove80_visualizer.svg_generator import _binding_to_keymap_drawer

        binding = KeyBinding(position=0, tap="A")
        result = _binding_to_keymap_drawer(binding, os_style="mac", show_shifted=True)

        # Alpha keys shouldn't have shifted (uppercase is obvious)
        if isinstance(result, dict):
            assert "shifted" not in result
        else:
            assert result == "A"

    def test_svg_contains_shifted_character(self):
        """SPEC-SK-026: Generated SVG contains shifted character text."""
        from glove80_visualizer.config import VisualizerConfig
        from glove80_visualizer.models import KeyBinding, Layer
        from glove80_visualizer.svg_generator import generate_layer_svg

        config = VisualizerConfig(show_shifted=True)
        layer = Layer(
            name="Test",
            index=0,
            bindings=[KeyBinding(position=i, tap="'" if i == 0 else "X") for i in range(80)],
        )
        svg = generate_layer_svg(layer, config=config)

        # Both the tap (') and shifted (") should appear
        assert "'" in svg or "&#39;" in svg  # single quote or escaped
        assert '"' in svg or "&quot;" in svg  # double quote or escaped


class TestShiftedKeyCli:
    """Tests for --no-shifted CLI flag (shifted is on by default)."""

    def test_cli_no_shifted_flag_exists(self):
        """SPEC-SK-030: CLI has --no-shifted flag."""
        from click.testing import CliRunner

        from glove80_visualizer.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        assert "--no-shifted" in result.output

    def test_config_show_shifted_default_true(self):
        """SPEC-SK-031: VisualizerConfig.show_shifted defaults to True."""
        from glove80_visualizer.config import VisualizerConfig

        config = VisualizerConfig()
        assert hasattr(config, "show_shifted")
        assert config.show_shifted is True  # Default on

    def test_config_show_shifted_can_be_disabled(self):
        """SPEC-SK-032: VisualizerConfig.show_shifted can be set to False."""
        from glove80_visualizer.config import VisualizerConfig

        config = VisualizerConfig(show_shifted=False)
        assert config.show_shifted is False


class TestModMorphShiftedExtraction:
    """Tests for extracting shifted characters from ZMK mod-morph behaviors.

    Mod-morph behaviors define custom shift behavior, e.g.:
    - parang_left: tap=( shifted=<
    - parang_right: tap=) shifted=>
    """

    def test_parse_mod_morph_simple(self):
        """SPEC-MM-001: Parse a simple mod-morph behavior with shift modifier."""
        from glove80_visualizer.parser import parse_mod_morph_behaviors

        keymap_content = '''
        parang_left: left_parenthesis_and_less_than {
            compatible = "zmk,behavior-mod-morph";
            #binding-cells = <0>;
            bindings = <&kp LPAR>, <&kp LT>;
            mods = <(MOD_LSFT|MOD_RSFT)>;
        };
        '''
        result = parse_mod_morph_behaviors(keymap_content)

        assert "parang_left" in result
        assert result["parang_left"]["tap"] == "LPAR"
        assert result["parang_left"]["shifted"] == "LT"

    def test_parse_mod_morph_right_paren(self):
        """SPEC-MM-002: Parse mod-morph for right parenthesis."""
        from glove80_visualizer.parser import parse_mod_morph_behaviors

        keymap_content = '''
        parang_right: right_parenthesis_and_greater_than {
            compatible = "zmk,behavior-mod-morph";
            #binding-cells = <0>;
            bindings = <&kp RPAR>, <&kp GT>;
            mods = <(MOD_LSFT|MOD_RSFT)>;
        };
        '''
        result = parse_mod_morph_behaviors(keymap_content)

        assert "parang_right" in result
        assert result["parang_right"]["tap"] == "RPAR"
        assert result["parang_right"]["shifted"] == "GT"

    def test_parse_mod_morph_multiple(self):
        """SPEC-MM-003: Parse multiple mod-morph behaviors."""
        from glove80_visualizer.parser import parse_mod_morph_behaviors

        keymap_content = '''
        parang_left: left_paren {
            compatible = "zmk,behavior-mod-morph";
            #binding-cells = <0>;
            bindings = <&kp LPAR>, <&kp LT>;
            mods = <(MOD_LSFT|MOD_RSFT)>;
        };
        parang_right: right_paren {
            compatible = "zmk,behavior-mod-morph";
            #binding-cells = <0>;
            bindings = <&kp RPAR>, <&kp GT>;
            mods = <(MOD_LSFT|MOD_RSFT)>;
        };
        '''
        result = parse_mod_morph_behaviors(keymap_content)

        assert len(result) == 2
        assert "parang_left" in result
        assert "parang_right" in result

    def test_parse_mod_morph_ignores_non_shift(self):
        """SPEC-MM-004: Ignore mod-morph behaviors that don't use shift."""
        from glove80_visualizer.parser import parse_mod_morph_behaviors

        keymap_content = '''
        ctrl_morph: ctrl_behavior {
            compatible = "zmk,behavior-mod-morph";
            #binding-cells = <0>;
            bindings = <&kp A>, <&kp B>;
            mods = <(MOD_LCTL|MOD_RCTL)>;
        };
        '''
        result = parse_mod_morph_behaviors(keymap_content)

        # Should not include ctrl-based morphs
        assert "ctrl_morph" not in result

    def test_parse_mod_morph_empty_content(self):
        """SPEC-MM-005: Handle empty or no mod-morph content."""
        from glove80_visualizer.parser import parse_mod_morph_behaviors

        result = parse_mod_morph_behaviors("")
        assert result == {}

        result = parse_mod_morph_behaviors("some random content")
        assert result == {}

    def test_parse_mod_morph_real_keymap_file(self):
        """SPEC-MM-006: Parse mod-morph from real keymap file."""
        from pathlib import Path

        from glove80_visualizer.parser import parse_mod_morph_behaviors

        keymap_path = Path("daves-current-glove80-keymap.keymap")
        if keymap_path.exists():
            content = keymap_path.read_text()
            result = parse_mod_morph_behaviors(content)

            # Should find parang_left and parang_right
            assert "parang_left" in result
            assert "parang_right" in result
            assert result["parang_left"]["tap"] == "LPAR"
            assert result["parang_left"]["shifted"] == "LT"


class TestModMorphInSvgGeneration:
    """Tests for applying mod-morph shifted chars in SVG output."""

    def test_get_shifted_char_with_mod_morph(self):
        """SPEC-MM-010: get_shifted_char uses mod-morph mappings."""
        from glove80_visualizer.svg_generator import get_shifted_char

        mod_morphs = {
            "parang_left": {"tap": "LPAR", "shifted": "LT"},
        }
        # When tap is "(", should return "<" from mod-morph
        result = get_shifted_char("(", mod_morphs=mod_morphs)
        assert result == "<"

    def test_get_shifted_char_mod_morph_overrides_default(self):
        """SPEC-MM-011: Mod-morph mappings override default SHIFTED_KEY_PAIRS."""
        from glove80_visualizer.svg_generator import get_shifted_char

        # Default for "1" is "!"
        assert get_shifted_char("1") == "!"

        # But mod-morph can override it
        mod_morphs = {
            "custom_1": {"tap": "N1", "shifted": "PIPE"},
        }
        result = get_shifted_char("1", mod_morphs=mod_morphs)
        assert result == "|"

    def test_get_shifted_char_falls_back_to_default(self):
        """SPEC-MM-012: Falls back to default when no mod-morph match."""
        from glove80_visualizer.svg_generator import get_shifted_char

        mod_morphs = {
            "parang_left": {"tap": "LPAR", "shifted": "LT"},
        }
        # "1" is not in mod_morphs, should use default
        result = get_shifted_char("1", mod_morphs=mod_morphs)
        assert result == "!"

    def test_binding_with_mod_morph_shifted(self):
        """SPEC-MM-013: KeyBinding for mod-morph key shows custom shifted."""
        from glove80_visualizer.models import KeyBinding
        from glove80_visualizer.svg_generator import _binding_to_keymap_drawer

        mod_morphs = {
            "parang_left": {"tap": "LPAR", "shifted": "LT"},
        }
        # Key displays "(" but shifted should be "<"
        binding = KeyBinding(position=0, tap="(")
        result = _binding_to_keymap_drawer(
            binding, os_style="mac", show_shifted=True, mod_morphs=mod_morphs
        )

        assert isinstance(result, dict)
        assert result.get("t") == "("
        assert result.get("shifted") == "<"

    def test_svg_generation_with_mod_morphs(self):
        """SPEC-MM-014: SVG generation uses mod-morph mappings."""
        from glove80_visualizer.config import VisualizerConfig
        from glove80_visualizer.models import KeyBinding, Layer
        from glove80_visualizer.svg_generator import generate_layer_svg

        mod_morphs = {
            "parang_left": {"tap": "LPAR", "shifted": "LT"},
        }
        config = VisualizerConfig(show_shifted=True)
        layer = Layer(
            name="Test",
            index=0,
            bindings=[KeyBinding(position=i, tap="(" if i == 0 else "X") for i in range(80)],
        )
        svg = generate_layer_svg(layer, config=config, mod_morphs=mod_morphs)

        # Should contain "<" as the shifted char for "("
        assert "<" in svg or "&lt;" in svg


class TestTypographyPositioning:
    """Tests for typography positioning adjustments.

    These tests verify that tap/shifted/hold labels are positioned correctly
    based on which elements are present on a key.
    """

    def test_shifted_only_tap_moves_down(self):
        """SPEC-TYPO-001: Keys with shifted but no hold move tap to y=8."""
        from glove80_visualizer.svg_generator import _adjust_tap_positions_for_shifted

        # SVG with shifted but no hold
        svg = '''<g transform="translate(140, 84)" class="key number keypos-12">
<rect rx="6" ry="6" x="-26" y="-24" width="52" height="48" class="key number"/>
<text x="0" y="0" class="key number tap">2</text>
<text x="0" y="-21" class="key number shifted">@</text>
</g>'''

        result = _adjust_tap_positions_for_shifted(svg)

        # Tap should move from y="0" to y="8"
        assert 'y="8" class="key number tap"' in result
        # Shifted should move from y="-21" to y="-14"
        assert 'y="-14" class="key number shifted"' in result

    def test_hold_only_tap_moves_up(self):
        """SPEC-TYPO-002: Keys with hold but no shifted move tap to y=-6."""
        from glove80_visualizer.svg_generator import _adjust_tap_positions_for_shifted

        # SVG with hold but no shifted
        svg = '''<g transform="translate(28, 336)" class="key layer keypos-64">
<rect rx="6" ry="6" x="-26" y="-24" width="52" height="48" class="key layer"/>
<text x="0" y="0" class="key layer tap">RGB</text>
<text x="0" y="21" class="key layer hold">Magic</text>
</g>'''

        result = _adjust_tap_positions_for_shifted(svg)

        # Tap should move from y="0" to y="-6"
        assert 'y="-6" class="key layer tap"' in result
        # Hold should move from y="21" to y="16"
        assert 'y="16" class="key layer hold"' in result

    def test_shifted_and_hold_unchanged(self):
        """SPEC-TYPO-003: Keys with both shifted and hold keep tap at y=0."""
        from glove80_visualizer.svg_generator import _adjust_tap_positions_for_shifted

        # SVG with both shifted and hold
        svg = '''<g transform="translate(924, 224)" class="key symbol keypos-44">
<rect rx="6" ry="6" x="-26" y="-24" width="52" height="48" class="key symbol"/>
<text x="0" y="0" class="key symbol tap">;</text>
<text x="0" y="21" class="key symbol hold">⌃</text>
<text x="0" y="-21" class="key symbol shifted">:</text>
</g>'''

        result = _adjust_tap_positions_for_shifted(svg)

        # Tap should stay at y="0"
        assert 'y="0" class="key symbol tap"' in result
        # Hold should stay at y="21"
        assert 'y="21" class="key symbol hold"' in result
        # Shifted should stay at y="-21"
        assert 'y="-21" class="key symbol shifted"' in result

    def test_no_shifted_no_hold_unchanged(self):
        """SPEC-TYPO-004: Keys with neither shifted nor hold stay at y=0."""
        from glove80_visualizer.svg_generator import _adjust_tap_positions_for_shifted

        # SVG with just tap
        svg = '''<g transform="translate(140, 140)" class="key keypos-24">
<rect rx="6" ry="6" x="-26" y="-26" width="52" height="52" class="key"/>
<text x="0" y="0" class="key tap">W</text>
</g>'''

        result = _adjust_tap_positions_for_shifted(svg)

        # Tap should stay at y="0"
        assert 'y="0" class="key tap"' in result


class TestTypographyCSS:
    """Tests for typography CSS styling."""

    def test_tap_font_size_is_14px(self):
        """SPEC-TYPO-010: Tap labels use 14px font size."""
        from glove80_visualizer.config import VisualizerConfig
        from glove80_visualizer.models import KeyBinding, Layer
        from glove80_visualizer.svg_generator import generate_layer_svg

        layer = Layer(
            name="Test",
            index=0,
            bindings=[KeyBinding(position=i, tap="A") for i in range(80)],
        )
        svg = generate_layer_svg(layer, config=VisualizerConfig())

        assert "text.tap" in svg
        assert "font-size: 14px" in svg

    def test_tap_has_stroke_for_weight(self):
        """SPEC-TYPO-011: Tap labels use stroke for bolder appearance."""
        from glove80_visualizer.config import VisualizerConfig
        from glove80_visualizer.models import KeyBinding, Layer
        from glove80_visualizer.svg_generator import generate_layer_svg

        layer = Layer(
            name="Test",
            index=0,
            bindings=[KeyBinding(position=i, tap="A") for i in range(80)],
        )
        svg = generate_layer_svg(layer, config=VisualizerConfig())

        assert "stroke-width: 0.3px" in svg

    def test_shifted_font_size_is_10px(self):
        """SPEC-TYPO-012: Shifted labels use 10px font size."""
        from glove80_visualizer.config import VisualizerConfig
        from glove80_visualizer.models import KeyBinding, Layer
        from glove80_visualizer.svg_generator import generate_layer_svg

        layer = Layer(
            name="Test",
            index=0,
            bindings=[KeyBinding(position=i, tap="1", shifted="!") for i in range(80)],
        )
        svg = generate_layer_svg(layer, config=VisualizerConfig())

        assert "text.shifted" in svg
        assert "font-size: 10px" in svg

    def test_hold_font_size_is_9px(self):
        """SPEC-TYPO-013: Hold labels use 9px font size."""
        from glove80_visualizer.config import VisualizerConfig
        from glove80_visualizer.models import KeyBinding, Layer
        from glove80_visualizer.svg_generator import generate_layer_svg

        layer = Layer(
            name="Test",
            index=0,
            bindings=[KeyBinding(position=i, tap="A", hold="⌘") for i in range(80)],
        )
        svg = generate_layer_svg(layer, config=VisualizerConfig())

        assert "text.hold" in svg
        assert "font-size: 9px" in svg
