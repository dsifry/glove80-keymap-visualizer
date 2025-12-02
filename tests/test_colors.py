"""
Tests for color scheme and key categorization.

These tests define the expected behavior for semantic color coding.
"""


class TestColorScheme:
    """Tests for ColorScheme dataclass."""

    def test_color_scheme_defaults(self):
        """SPEC-CL-001: ColorScheme has Everforest-inspired defaults."""
        from glove80_visualizer.colors import ColorScheme

        scheme = ColorScheme()
        assert scheme.name == "everforest"
        assert scheme.modifier_color == "#7fbbb3"
        assert scheme.layer_color == "#d699b6"
        assert scheme.navigation_color == "#83c092"

    def test_color_scheme_custom(self):
        """ColorScheme can be customized."""
        from glove80_visualizer.colors import ColorScheme

        scheme = ColorScheme(modifier_color="#ff0000")
        assert scheme.modifier_color == "#ff0000"


class TestKeyCategorization:
    """Tests for categorize_key function."""

    def test_categorize_modifier_symbols(self):
        """SPEC-CL-002: Modifier symbols are categorized correctly."""
        from glove80_visualizer.colors import categorize_key

        assert categorize_key("⌘") == "modifier"
        assert categorize_key("⌥") == "modifier"
        assert categorize_key("⌃") == "modifier"
        assert categorize_key("⇧") == "modifier"
        assert categorize_key("Shift") == "modifier"
        assert categorize_key("Ctrl") == "modifier"

    def test_categorize_navigation_keys(self):
        """SPEC-CL-003: Navigation symbols are categorized correctly."""
        from glove80_visualizer.colors import categorize_key

        assert categorize_key("←") == "navigation"
        assert categorize_key("→") == "navigation"
        assert categorize_key("↑") == "navigation"
        assert categorize_key("↓") == "navigation"
        assert categorize_key("Home") == "navigation"
        assert categorize_key("End") == "navigation"
        assert categorize_key("PgUp") == "navigation"
        assert categorize_key("PgDn") == "navigation"

    def test_categorize_number_keys(self):
        """SPEC-CL-004: Numbers and function keys are categorized correctly."""
        from glove80_visualizer.colors import categorize_key

        assert categorize_key("1") == "number"
        assert categorize_key("0") == "number"
        assert categorize_key("F1") == "number"
        assert categorize_key("F12") == "number"

    def test_categorize_layer_keys(self):
        """SPEC-CL-005: Layer names are categorized correctly."""
        from glove80_visualizer.colors import categorize_key

        # Layer names typically appear as hold behaviors
        assert categorize_key("Cursor", is_hold=True) == "layer"
        assert categorize_key("Symbol", is_hold=True) == "layer"
        assert categorize_key("Number", is_hold=True) == "layer"

    def test_categorize_layer_name_without_hold_flag(self):
        """SPEC-CL-005b: Layer names without is_hold flag are default."""
        from glove80_visualizer.colors import categorize_key

        # Without is_hold=True, layer names are categorized as default
        assert categorize_key("Cursor", is_hold=False) == "default"
        assert categorize_key("Cursor") == "default"  # is_hold defaults to False

    def test_categorize_mouse_keys(self):
        """SPEC-CL-006: Mouse keys are categorized correctly."""
        from glove80_visualizer.colors import categorize_key

        assert categorize_key("🖱↑") == "mouse"
        assert categorize_key("🖱↓") == "mouse"
        assert categorize_key("🖱L") == "mouse"
        assert categorize_key("🖱R") == "mouse"

    def test_categorize_system_keys(self):
        """SPEC-CL-007: System keys are categorized correctly."""
        from glove80_visualizer.colors import categorize_key

        assert categorize_key("Reset") == "system"
        assert categorize_key("Boot") == "system"

    def test_categorize_alpha_default(self):
        """SPEC-CL-008: Alpha keys use default category."""
        from glove80_visualizer.colors import categorize_key

        assert categorize_key("A") == "default"
        assert categorize_key("Q") == "default"
        assert categorize_key("Space") == "default"
        assert categorize_key("Tab") == "default"

    def test_categorize_transparent_keys(self):
        """SPEC-CL-009: Transparent keys are categorized correctly."""
        from glove80_visualizer.colors import categorize_key

        assert categorize_key("▽") == "transparent"
        assert categorize_key("trans") == "transparent"

    def test_categorize_symbol_keys(self):
        """SPEC-CL-010: Symbol keys are categorized correctly."""
        from glove80_visualizer.colors import categorize_key

        assert categorize_key("!") == "symbol"
        assert categorize_key("@") == "symbol"
        assert categorize_key("#") == "symbol"
        assert categorize_key("$") == "symbol"
        assert categorize_key("%") == "symbol"
        assert categorize_key("^") == "symbol"
        assert categorize_key("&") == "symbol"
        assert categorize_key("*") == "symbol"
        assert categorize_key("(") == "symbol"
        assert categorize_key(")") == "symbol"

    def test_categorize_media_keys(self):
        """SPEC-CL-011: Media keys are categorized correctly."""
        from glove80_visualizer.colors import categorize_key

        assert categorize_key("⏯") == "media"
        assert categorize_key("⏭") == "media"
        assert categorize_key("⏮") == "media"
        assert categorize_key("🔇") == "media"
        assert categorize_key("🔊") == "media"
        assert categorize_key("🔉") == "media"


class TestGetKeyColor:
    """Tests for get_key_color function."""

    def test_get_key_color_modifier(self):
        """Get color for modifier key."""
        from glove80_visualizer.colors import ColorScheme, get_key_color

        scheme = ColorScheme()
        color = get_key_color("⌘", scheme)
        assert color == scheme.modifier_color

    def test_get_key_color_default(self):
        """Get color for default key."""
        from glove80_visualizer.colors import ColorScheme, get_key_color

        scheme = ColorScheme()
        color = get_key_color("A", scheme)
        assert color == scheme.default_color
