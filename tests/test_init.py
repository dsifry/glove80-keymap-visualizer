"""
Tests for the main module's generate_visualization function.

Tests error recovery paths and edge cases.
"""


class TestGenerateVisualization:
    """Tests for the generate_visualization function."""

    def test_generate_visualization_basic(self, simple_keymap_path, tmp_path):
        """Basic visualization generation works."""
        from glove80_visualizer import generate_visualization

        output = tmp_path / "output.pdf"
        result = generate_visualization(simple_keymap_path, output)

        assert result.success is True
        assert output.exists()

    def test_generate_visualization_no_layers_returns_error(self, tmp_path):
        """Returns error when keymap has no layers."""
        from glove80_visualizer import generate_visualization

        # Create a keymap with no layers
        keymap = tmp_path / "empty.keymap"
        keymap.write_text("// Empty keymap\n")

        output = tmp_path / "output.pdf"
        result = generate_visualization(keymap, output)

        assert result.success is False
        # Error could be "no layers" or "no keymap" depending on parser
        assert "no" in result.error_message.lower()

    def test_generate_visualization_no_layers_after_extraction(self, tmp_path, mocker):
        """Returns error when extractor returns empty layers."""
        from glove80_visualizer import generate_visualization

        # Mock extract_layers to return empty list after successful parse
        mocker.patch("glove80_visualizer.extract_layers", return_value=[])
        mocker.patch("glove80_visualizer.parse_zmk_keymap", return_value="layers: {}")

        keymap = tmp_path / "test.keymap"
        keymap.write_text("// test")
        output = tmp_path / "output.pdf"
        result = generate_visualization(keymap, output)

        assert result.success is False
        assert "no layers" in result.error_message.lower()

    def test_generate_visualization_invalid_keymap_returns_error(
        self, invalid_keymap_path, tmp_path
    ):
        """Returns error for invalid keymap."""
        from glove80_visualizer import generate_visualization

        output = tmp_path / "output.pdf"
        result = generate_visualization(invalid_keymap_path, output)

        assert result.success is False
        assert result.error_message is not None

    def test_generate_visualization_continue_on_error_partial_success(
        self, multi_layer_keymap_path, tmp_path, mocker
    ):
        """Continue on error allows partial success."""
        from glove80_visualizer import generate_visualization
        from glove80_visualizer.config import VisualizerConfig

        # Mock SVG generator to fail on second layer
        call_count = [0]
        valid_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">
<text class="label">Test</text>
</svg>"""

        def mock_generate(layer, config=None, **kwargs):
            call_count[0] += 1
            if call_count[0] == 2:
                raise ValueError("Simulated failure")
            return valid_svg

        mocker.patch(
            "glove80_visualizer.generate_layer_svg",
            side_effect=mock_generate,
        )

        config = VisualizerConfig(continue_on_error=True)
        output = tmp_path / "output.pdf"
        result = generate_visualization(multi_layer_keymap_path, output, config)

        # Should succeed with partial results
        assert result.success is True

    def test_generate_visualization_continue_on_error_all_fail(
        self, simple_keymap_path, tmp_path, mocker
    ):
        """All layers failing returns error even with continue_on_error."""
        from glove80_visualizer import generate_visualization
        from glove80_visualizer.config import VisualizerConfig

        def mock_fail(layer, config=None, **kwargs):
            raise ValueError("All layers fail")

        mocker.patch(
            "glove80_visualizer.generate_layer_svg",
            side_effect=mock_fail,
        )

        config = VisualizerConfig(continue_on_error=True)
        output = tmp_path / "output.pdf"
        result = generate_visualization(simple_keymap_path, output, config)

        assert result.success is False
        assert "all layers failed" in result.error_message.lower()

    def test_generate_visualization_fail_fast_without_continue_on_error(
        self, simple_keymap_path, tmp_path, mocker
    ):
        """Without continue_on_error, first failure stops processing."""
        from glove80_visualizer import generate_visualization

        def mock_fail(layer, config=None, **kwargs):
            raise ValueError("Render failed")

        mocker.patch(
            "glove80_visualizer.generate_layer_svg",
            side_effect=mock_fail,
        )

        output = tmp_path / "output.pdf"
        result = generate_visualization(simple_keymap_path, output)

        assert result.success is False
        assert "failed to render" in result.error_message.lower()

    def test_generate_visualization_svg_output(self, simple_keymap_path, tmp_path):
        """SVG output format creates directory with SVG files."""
        from glove80_visualizer import generate_visualization
        from glove80_visualizer.config import VisualizerConfig

        config = VisualizerConfig(output_format="svg")
        output_dir = tmp_path / "svgs"
        result = generate_visualization(simple_keymap_path, output_dir, config)

        assert result.success is True
        assert output_dir.exists()
        assert any(output_dir.glob("*.svg"))

    def test_generate_visualization_unexpected_error(self, simple_keymap_path, tmp_path, mocker):
        """Unexpected errors are caught and returned."""
        from glove80_visualizer import generate_visualization

        # Mock to raise an unexpected error type
        mocker.patch(
            "glove80_visualizer.extract_layers",
            side_effect=RuntimeError("Unexpected!"),
        )

        output = tmp_path / "output.pdf"
        result = generate_visualization(simple_keymap_path, output)

        assert result.success is False
        assert "unexpected error" in result.error_message.lower()


class TestVisualizationResult:
    """Tests for VisualizationResult model."""

    def test_visualization_result_fields(self):
        """VisualizationResult has expected fields."""
        from glove80_visualizer.models import VisualizationResult

        result = VisualizationResult(
            success=True,
            layers_processed=5,
            output_path="/tmp/output.pdf",
        )
        assert result.success is True
        assert result.layers_processed == 5
        assert result.output_path == "/tmp/output.pdf"

    def test_visualization_result_error(self):
        """VisualizationResult can represent errors."""
        from glove80_visualizer.models import VisualizationResult

        result = VisualizationResult(
            success=False,
            error_message="Something went wrong",
            layers_processed=0,
        )
        assert result.success is False
        assert result.error_message == "Something went wrong"

    def test_visualization_result_partial_success(self):
        """VisualizationResult can indicate partial success."""
        from glove80_visualizer.models import VisualizationResult

        result = VisualizationResult(
            success=True,
            partial_success=True,
            layers_processed=3,
        )
        assert result.success is True
        assert result.partial_success is True


class TestModMorphIntegration:
    """Tests for mod-morph integration in generate_visualization."""

    def test_mod_morphs_passed_to_svg_generator(self, tmp_path, mocker):
        """Mod-morph behaviors are parsed and passed to SVG generator."""
        from glove80_visualizer import generate_visualization
        from glove80_visualizer.models import KeyBinding, Layer

        # Create a keymap with mod-morph behavior
        keymap_content = """
        / {
            behaviors {
                parang_left: left_paren {
                    compatible = "zmk,behavior-mod-morph";
                    bindings = <&kp LPAR>, <&kp LT>;
                    mods = <(MOD_LSFT|MOD_RSFT)>;
                };
            };
            keymap {
                compatible = "zmk,keymap";
                layer_Base {
                    bindings = <&kp A>;
                };
            };
        };
        """
        keymap_path = tmp_path / "test.keymap"
        keymap_path.write_text(keymap_content)

        # Track what mod_morphs are passed to generate_layer_svg
        captured_mod_morphs = []

        def mock_generate(layer, config=None, mod_morphs=None, **kwargs):
            captured_mod_morphs.append(mod_morphs)
            return """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">
<text class="label">Test</text>
</svg>"""

        mocker.patch(
            "glove80_visualizer.generate_layer_svg",
            side_effect=mock_generate,
        )
        # Mock extract_layers to return a simple layer
        mocker.patch(
            "glove80_visualizer.extract_layers",
            return_value=[Layer(name="Base", index=0, bindings=[KeyBinding(tap="A", position=0)])],
        )

        output = tmp_path / "output.pdf"
        result = generate_visualization(keymap_path, output)

        assert result.success is True
        # Check that mod_morphs were passed
        assert len(captured_mod_morphs) == 1
        assert captured_mod_morphs[0] is not None
        assert "parang_left" in captured_mod_morphs[0]
        assert captured_mod_morphs[0]["parang_left"]["tap"] == "LPAR"
        assert captured_mod_morphs[0]["parang_left"]["shifted"] == "LT"
