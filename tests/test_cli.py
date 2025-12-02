"""
Tests for the CLI module.

These tests define the expected behavior of the command-line interface.
Write these tests FIRST (TDD), then implement the CLI to pass them.
"""


import pytest


class TestCliBasic:
    """Tests for basic CLI functionality."""

    def test_cli_basic(self, runner, simple_keymap_path, tmp_path):
        """SPEC-C001: CLI generates PDF from keymap file."""
        from glove80_visualizer.cli import main

        output = tmp_path / "output.pdf"
        result = runner.invoke(main, [str(simple_keymap_path), "-o", str(output)])

        assert result.exit_code == 0
        assert output.exists()

    def test_cli_list_layers(self, runner, multi_layer_keymap_path):
        """SPEC-C002: CLI can list available layers without generating PDF."""
        from glove80_visualizer.cli import main

        result = runner.invoke(main, [str(multi_layer_keymap_path), "--list-layers"])

        assert result.exit_code == 0
        # Should show layer names in output
        assert "Base" in result.output or "layer" in result.output.lower()

    def test_cli_select_layers(self, runner, multi_layer_keymap_path, tmp_path):
        """SPEC-C003: CLI can generate PDF for specific layers only."""
        from glove80_visualizer.cli import main

        output = tmp_path / "output.pdf"
        result = runner.invoke(
            main,
            [str(multi_layer_keymap_path), "-o", str(output), "--layers", "Base,Lower"],
        )

        assert result.exit_code == 0

    def test_cli_svg_output(self, runner, simple_keymap_path, tmp_path):
        """SPEC-C004: CLI can output SVG files instead of PDF."""
        from glove80_visualizer.cli import main

        output_dir = tmp_path / "svgs"
        result = runner.invoke(
            main,
            [str(simple_keymap_path), "-o", str(output_dir), "--format", "svg"],
        )

        assert result.exit_code == 0
        assert any(output_dir.glob("*.svg"))


class TestCliHelp:
    """Tests for CLI help and documentation."""

    def test_cli_help(self, runner):
        """SPEC-C005: CLI shows help message."""
        from glove80_visualizer.cli import main

        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "keymap" in result.output.lower()
        assert "output" in result.output.lower()

    def test_cli_version(self, runner):
        """CLI shows version information."""
        from glove80_visualizer.cli import main

        result = runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        assert "0." in result.output  # Version number


class TestCliErrors:
    """Tests for CLI error handling."""

    def test_cli_missing_file(self, runner):
        """SPEC-C006: CLI shows error for missing input file."""
        from glove80_visualizer.cli import main

        result = runner.invoke(main, ["/nonexistent/file.keymap"])

        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "error" in result.output.lower()

    def test_cli_invalid_keymap(self, runner, invalid_keymap_path, tmp_path):
        """CLI shows error for invalid keymap file."""
        from glove80_visualizer.cli import main

        output = tmp_path / "output.pdf"
        result = runner.invoke(main, [str(invalid_keymap_path), "-o", str(output)])

        assert result.exit_code != 0
        assert "error" in result.output.lower()

    def test_cli_missing_output(self, runner, simple_keymap_path):
        """CLI requires output path."""
        from glove80_visualizer.cli import main

        result = runner.invoke(main, [str(simple_keymap_path)])

        # Should either error or use default output
        # The exact behavior depends on implementation choice

    def test_cli_continue_on_error(self, runner, multi_layer_keymap_path, tmp_path, mocker):
        """SPEC-C009: CLI continues processing when --continue-on-error is set and a layer fails."""
        from glove80_visualizer.cli import main

        output = tmp_path / "output.pdf"
        # Mock svg_generator to fail on one specific layer
        call_count = [0]

        def mock_generate(layer, config=None, **kwargs):
            call_count[0] += 1
            if call_count[0] == 2:  # Fail on second layer
                raise ValueError("Simulated render failure")
            return "<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100'></svg>"

        mocker.patch(
            "glove80_visualizer.cli.generate_layer_svg",
            side_effect=mock_generate,
        )

        result = runner.invoke(
            main,
            [str(multi_layer_keymap_path), "-o", str(output), "--continue-on-error"],
        )

        # Should succeed (exit 0) if at least one layer rendered
        assert result.exit_code == 0
        assert output.exists()
        # Should warn about skipped layer
        assert "skipped" in result.output.lower() or "failed" in result.output.lower()

    def test_cli_continue_on_error_all_fail(self, runner, simple_keymap_path, tmp_path, mocker):
        """SPEC-C010: CLI exits with error if --continue-on-error is set but ALL layers fail."""
        from glove80_visualizer.cli import main

        output = tmp_path / "output.pdf"

        def mock_fail(layer, config=None, **kwargs):
            raise ValueError("All layers fail")

        mocker.patch(
            "glove80_visualizer.cli.generate_layer_svg",
            side_effect=mock_fail,
        )

        result = runner.invoke(
            main,
            [str(simple_keymap_path), "-o", str(output), "--continue-on-error"],
        )

        assert result.exit_code != 0
        assert "error" in result.output.lower()

    def test_cli_fail_fast_default(self, runner, simple_keymap_path, tmp_path, mocker):
        """SPEC-C011: CLI fails immediately on first error by default (no --continue-on-error)."""
        from glove80_visualizer.cli import main

        output = tmp_path / "output.pdf"

        def mock_fail(layer, config=None, **kwargs):
            raise ValueError("Render failed")

        mocker.patch(
            "glove80_visualizer.cli.generate_layer_svg",
            side_effect=mock_fail,
        )

        result = runner.invoke(
            main,
            [str(simple_keymap_path), "-o", str(output)],
        )

        assert result.exit_code != 0
        assert not output.exists()


class TestCliOptions:
    """Tests for CLI options and configuration."""

    def test_cli_verbose(self, runner, simple_keymap_path, tmp_path):
        """SPEC-C007: CLI shows progress in verbose mode."""
        from glove80_visualizer.cli import main

        output = tmp_path / "output.pdf"
        result = runner.invoke(
            main, [str(simple_keymap_path), "-o", str(output), "-v"]
        )

        assert result.exit_code == 0
        # Should show some progress information
        assert len(result.output) > 0

    def test_cli_config_file(self, runner, simple_keymap_path, tmp_path):
        """SPEC-C008: CLI can load configuration from file."""
        from glove80_visualizer.cli import main

        config_file = tmp_path / "config.yaml"
        config_file.write_text("page_size: a4\n")

        output = tmp_path / "output.pdf"
        result = runner.invoke(
            main,
            [
                str(simple_keymap_path),
                "-o",
                str(output),
                "--config",
                str(config_file),
            ],
        )

        assert result.exit_code == 0

    def test_cli_quiet_mode(self, runner, simple_keymap_path, tmp_path):
        """CLI can run in quiet mode with minimal output."""
        from glove80_visualizer.cli import main

        output = tmp_path / "output.pdf"
        result = runner.invoke(
            main, [str(simple_keymap_path), "-o", str(output), "-q"]
        )

        assert result.exit_code == 0
        # Output should be minimal
        assert len(result.output.strip()) == 0 or "error" not in result.output.lower()


class TestCliOsStyleOptions:
    """Tests for OS-specific modifier symbol options."""

    def test_cli_mac_option(self, runner, simple_keymap_path, tmp_path):
        """SPEC-C010: CLI accepts --mac option for Apple modifier symbols."""
        from glove80_visualizer.cli import main

        output = tmp_path / "output.pdf"
        result = runner.invoke(
            main, [str(simple_keymap_path), "-o", str(output), "--mac"]
        )

        assert result.exit_code == 0
        assert output.exists()

    def test_cli_windows_option(self, runner, simple_keymap_path, tmp_path):
        """SPEC-C011: CLI accepts --windows option for Windows modifier symbols."""
        from glove80_visualizer.cli import main

        output = tmp_path / "output.pdf"
        result = runner.invoke(
            main, [str(simple_keymap_path), "-o", str(output), "--windows"]
        )

        assert result.exit_code == 0
        assert output.exists()

    def test_cli_linux_option(self, runner, simple_keymap_path, tmp_path):
        """SPEC-C012: CLI accepts --linux option for Linux modifier symbols."""
        from glove80_visualizer.cli import main

        output = tmp_path / "output.pdf"
        result = runner.invoke(
            main, [str(simple_keymap_path), "-o", str(output), "--linux"]
        )

        assert result.exit_code == 0
        assert output.exists()

    def test_cli_os_options_mutually_exclusive(self, runner, simple_keymap_path, tmp_path):
        """SPEC-C013: Only one OS style option can be specified at a time."""
        from glove80_visualizer.cli import main

        output = tmp_path / "output.pdf"
        result = runner.invoke(
            main, [str(simple_keymap_path), "-o", str(output), "--mac", "--windows"]
        )

        # Should fail or warn when multiple OS options are given
        assert result.exit_code != 0 or "error" in result.output.lower() or "conflict" in result.output.lower()

    def test_cli_default_is_mac(self, runner, simple_keymap_path, tmp_path):
        """SPEC-C014: Default OS style is Mac when no option specified."""
        from glove80_visualizer.cli import main

        output = tmp_path / "output.pdf"
        result = runner.invoke(
            main, [str(simple_keymap_path), "-o", str(output)]
        )

        assert result.exit_code == 0
        # Default should work without any OS flag


class TestCliResolveTransOption:
    """Tests for --resolve-trans CLI option."""

    def test_cli_resolve_trans_option(self, runner, multi_layer_keymap_path, tmp_path):
        """SPEC-C015: CLI accepts --resolve-trans option."""
        from glove80_visualizer.cli import main

        output = tmp_path / "output.pdf"
        result = runner.invoke(
            main, [str(multi_layer_keymap_path), "-o", str(output), "--resolve-trans"]
        )

        assert result.exit_code == 0
        assert output.exists()

    def test_cli_resolve_trans_with_base_layer(self, runner, multi_layer_keymap_path, tmp_path):
        """SPEC-C016: CLI --resolve-trans can specify base layer name."""
        from glove80_visualizer.cli import main

        output = tmp_path / "output.pdf"
        result = runner.invoke(
            main, [
                str(multi_layer_keymap_path),
                "-o", str(output),
                "--resolve-trans",
                "--base-layer", "Base"
            ]
        )

        assert result.exit_code == 0
        assert output.exists()


class TestCliColorOption:
    """Tests for --color CLI option."""

    def test_cli_color_option(self, runner, simple_keymap_path, tmp_path):
        """SPEC-CL-012: CLI accepts --color option."""
        from glove80_visualizer.cli import main

        output = tmp_path / "output.pdf"
        result = runner.invoke(
            main, [str(simple_keymap_path), "-o", str(output), "--color"]
        )

        assert result.exit_code == 0
        assert output.exists()


class TestCliNoLegendOption:
    """Tests for --no-legend CLI option."""

    def test_cli_no_legend_option_accepted(self, runner, simple_keymap_path, tmp_path):
        """SPEC-NL-001: CLI accepts --no-legend option."""
        from glove80_visualizer.cli import main

        output = tmp_path / "output.pdf"
        result = runner.invoke(
            main, [str(simple_keymap_path), "-o", str(output), "--color", "--no-legend"]
        )

        assert result.exit_code == 0
        assert output.exists()

    def test_cli_no_legend_svg_output(self, runner, simple_keymap_path, tmp_path):
        """SPEC-NL-002: --no-legend suppresses legend in SVG output."""
        from glove80_visualizer.cli import main

        output_dir = tmp_path / "svgs"
        result = runner.invoke(
            main,
            [str(simple_keymap_path), "-o", str(output_dir), "--format", "svg", "--color", "--no-legend"],
        )

        assert result.exit_code == 0
        svg_files = list(output_dir.glob("*.svg"))
        assert len(svg_files) > 0

        # Read the SVG and verify no legend
        svg_content = svg_files[0].read_text()
        assert "color-legend" not in svg_content
        assert "Modifiers" not in svg_content

    def test_cli_color_without_no_legend_shows_legend(self, runner, simple_keymap_path, tmp_path):
        """SPEC-NL-003: --color without --no-legend shows legend by default."""
        from glove80_visualizer.cli import main

        output_dir = tmp_path / "svgs"
        result = runner.invoke(
            main,
            [str(simple_keymap_path), "-o", str(output_dir), "--format", "svg", "--color"],
        )

        assert result.exit_code == 0
        svg_files = list(output_dir.glob("*.svg"))
        assert len(svg_files) > 0

        # Read the SVG and verify legend is present
        svg_content = svg_files[0].read_text()
        assert "color-legend" in svg_content
        assert "Modifiers" in svg_content

    def test_cli_no_legend_in_help(self, runner):
        """SPEC-NL-004: --no-legend option appears in help output."""
        from glove80_visualizer.cli import main

        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "--no-legend" in result.output


class TestCliEdgeCases:
    """Tests for CLI edge cases to achieve full coverage."""

    def test_cli_no_layers_found(self, runner, tmp_path):
        """CLI shows error when keymap has no layers."""
        from glove80_visualizer.cli import main

        # Create empty keymap
        keymap = tmp_path / "empty.keymap"
        keymap.write_text("// Empty keymap\n")

        result = runner.invoke(main, [str(keymap), "-o", str(tmp_path / "out.pdf")])

        # Should fail with error
        assert result.exit_code != 0

    def test_cli_svg_default_output_path(self, runner, simple_keymap_path, tmp_path, mocker):
        """CLI generates default SVG output directory name."""
        from glove80_visualizer.cli import main

        # Invoke without -o but with --format svg
        # Use the keymap from fixtures directory
        result = runner.invoke(
            main,
            [str(simple_keymap_path), "--format", "svg"],
        )

        # Should succeed and create default _svgs directory
        assert result.exit_code == 0

    def test_cli_base_layer_not_found(self, runner, multi_layer_keymap_path, tmp_path):
        """CLI shows error when specified base layer is not found."""
        from glove80_visualizer.cli import main

        output = tmp_path / "output.pdf"
        result = runner.invoke(
            main,
            [
                str(multi_layer_keymap_path),
                "-o", str(output),
                "--resolve-trans",
                "--base-layer", "NonexistentLayer"
            ]
        )

        assert result.exit_code != 0
        assert "not found" in result.output.lower()

    def test_cli_resolve_trans_fallback_to_first_layer(self, runner, tmp_path, mocker):
        """CLI uses first layer when no layer has index 0."""
        from glove80_visualizer.cli import main
        from glove80_visualizer.models import Layer, KeyBinding

        # Create test keymap
        keymap = tmp_path / "test.keymap"
        keymap.write_text("""
/ {
    keymap {
        compatible = "zmk,keymap";
        Test {
            bindings = <&kp A>;
        };
    };
};
""")

        output = tmp_path / "output.pdf"
        result = runner.invoke(
            main,
            [str(keymap), "-o", str(output), "--resolve-trans"]
        )

        # Should succeed
        assert result.exit_code == 0


class TestCliIntegration:
    """Integration tests for the CLI."""

    @pytest.mark.slow
    def test_cli_full_workflow(self, runner, daves_keymap_path, tmp_path):
        """CLI can process Dave's full keymap end-to-end."""
        from glove80_visualizer.cli import main

        if not daves_keymap_path.exists():
            pytest.skip("Dave's keymap file not found")

        output = tmp_path / "daves_layers.pdf"
        result = runner.invoke(main, [str(daves_keymap_path), "-o", str(output), "-v"])

        assert result.exit_code == 0
        assert output.exists()
        assert output.stat().st_size > 10000  # Should be a reasonable PDF size
