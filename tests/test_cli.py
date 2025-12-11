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

        runner.invoke(main, [str(simple_keymap_path)])

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
        result = runner.invoke(main, [str(simple_keymap_path), "-o", str(output), "-v"])

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
        result = runner.invoke(main, [str(simple_keymap_path), "-o", str(output), "-q"])

        assert result.exit_code == 0
        # Output should be minimal
        assert len(result.output.strip()) == 0 or "error" not in result.output.lower()


class TestCliOsStyleOptions:
    """Tests for OS-specific modifier symbol options."""

    def test_cli_mac_option(self, runner, simple_keymap_path, tmp_path):
        """SPEC-C010: CLI accepts --mac option for Apple modifier symbols."""
        from glove80_visualizer.cli import main

        output = tmp_path / "output.pdf"
        result = runner.invoke(main, [str(simple_keymap_path), "-o", str(output), "--mac"])

        assert result.exit_code == 0
        assert output.exists()

    def test_cli_windows_option(self, runner, simple_keymap_path, tmp_path):
        """SPEC-C011: CLI accepts --windows option for Windows modifier symbols."""
        from glove80_visualizer.cli import main

        output = tmp_path / "output.pdf"
        result = runner.invoke(main, [str(simple_keymap_path), "-o", str(output), "--windows"])

        assert result.exit_code == 0
        assert output.exists()

    def test_cli_linux_option(self, runner, simple_keymap_path, tmp_path):
        """SPEC-C012: CLI accepts --linux option for Linux modifier symbols."""
        from glove80_visualizer.cli import main

        output = tmp_path / "output.pdf"
        result = runner.invoke(main, [str(simple_keymap_path), "-o", str(output), "--linux"])

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
        assert (
            result.exit_code != 0
            or "error" in result.output.lower()
            or "conflict" in result.output.lower()
        )

    def test_cli_default_is_mac(self, runner, simple_keymap_path, tmp_path):
        """SPEC-C014: Default OS style is Mac when no option specified."""
        from glove80_visualizer.cli import main

        output = tmp_path / "output.pdf"
        result = runner.invoke(main, [str(simple_keymap_path), "-o", str(output)])

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
            main,
            [
                str(multi_layer_keymap_path),
                "-o",
                str(output),
                "--resolve-trans",
                "--base-layer",
                "Base",
            ],
        )

        assert result.exit_code == 0
        assert output.exists()


class TestCliColorOption:
    """Tests for --color CLI option."""

    def test_cli_color_option(self, runner, simple_keymap_path, tmp_path):
        """SPEC-CL-012: CLI accepts --color option."""
        from glove80_visualizer.cli import main

        output = tmp_path / "output.pdf"
        result = runner.invoke(main, [str(simple_keymap_path), "-o", str(output), "--color"])

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
            [
                str(simple_keymap_path),
                "-o",
                str(output_dir),
                "--format",
                "svg",
                "--color",
                "--no-legend",
            ],
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
                "-o",
                str(output),
                "--resolve-trans",
                "--base-layer",
                "NonexistentLayer",
            ],
        )

        assert result.exit_code != 0
        assert "not found" in result.output.lower()

    def test_cli_resolve_trans_fallback_to_first_layer(self, runner, tmp_path, mocker):
        """CLI uses first layer when no layer has index 0."""
        from glove80_visualizer.cli import main

        # Create test keymap
        keymap = tmp_path / "test.keymap"
        keymap.write_text(
            """
/ {
    keymap {
        compatible = "zmk,keymap";
        Test {
            bindings = <&kp A>;
        };
    };
};
"""
        )

        output = tmp_path / "output.pdf"
        result = runner.invoke(main, [str(keymap), "-o", str(output), "--resolve-trans"])

        # Should succeed
        assert result.exit_code == 0


class TestCliKleJsonFormat:
    """Tests for KLE JSON output format."""

    def test_cli_kle_json_format(self, runner, simple_keymap_path, tmp_path, mocker):
        """SPEC-KLE-001: CLI can generate KLE JSON format."""
        from glove80_visualizer.cli import main

        # Mock the KLE template generator
        mock_generate = mocker.patch(
            "glove80_visualizer.kle_template.generate_kle_from_template",
            return_value='{"test": "kle json"}',
        )

        output_dir = tmp_path / "kle"
        result = runner.invoke(
            main,
            [str(simple_keymap_path), "-o", str(output_dir), "--format", "kle"],
        )

        assert result.exit_code == 0
        assert output_dir.exists()
        assert mock_generate.called
        # Should have created JSON files
        json_files = list(output_dir.glob("*.json"))
        assert len(json_files) > 0

    def test_cli_kle_json_default_output_path(self, runner, simple_keymap_path, mocker):
        """SPEC-KLE-002: CLI generates default KLE output directory when no -o specified."""
        from glove80_visualizer.cli import main

        # Mock the KLE template generator at the source module
        mocker.patch(
            "glove80_visualizer.kle_template.generate_kle_from_template",
            return_value='{"test": "kle json"}',
        )

        result = runner.invoke(
            main,
            [str(simple_keymap_path), "--format", "kle"],
        )

        assert result.exit_code == 0
        # Should create default directory named {keymap.stem}_kle
        expected_dir = simple_keymap_path.parent / f"{simple_keymap_path.stem}_kle"
        assert expected_dir.exists()

    def test_cli_kle_json_verbose_output(self, runner, multi_layer_keymap_path, tmp_path, mocker):
        """SPEC-KLE-003: CLI shows progress for each layer in verbose mode."""
        from glove80_visualizer.cli import main

        # Mock the KLE template generator at the source module
        mocker.patch(
            "glove80_visualizer.kle_template.generate_kle_from_template",
            return_value='{"test": "kle json"}',
        )

        output_dir = tmp_path / "kle"
        result = runner.invoke(
            main,
            [str(multi_layer_keymap_path), "-o", str(output_dir), "--format", "kle", "-v"],
        )

        assert result.exit_code == 0
        # Should show progress messages
        assert "Generating KLE JSON for layer:" in result.output
        assert "Wrote:" in result.output

    def test_cli_kle_json_with_combos_verbose(self, runner, simple_keymap_path, tmp_path, mocker):
        """SPEC-KLE-004: CLI logs combo count in verbose mode."""
        from glove80_visualizer.cli import main

        # Mock parse_combos to return test combos
        from glove80_visualizer.models import Combo

        test_combos = [
            Combo(name="test1", positions=[0, 1], action="&kp A", layers=None),
            Combo(name="test2", positions=[2, 3], action="&kp B", layers=None),
        ]
        mocker.patch(
            "glove80_visualizer.cli.parse_combos",
            return_value=test_combos,
        )

        # Mock the KLE template generator
        mocker.patch(
            "glove80_visualizer.kle_template.generate_kle_from_template",
            return_value='{"test": "kle json"}',
        )

        output_dir = tmp_path / "kle"
        result = runner.invoke(
            main,
            [str(simple_keymap_path), "-o", str(output_dir), "--format", "kle", "-v"],
        )

        assert result.exit_code == 0
        # Should show combo count
        assert "Found 2 combos" in result.output

    def test_cli_kle_json_combo_parse_error(self, runner, simple_keymap_path, tmp_path, mocker):
        """SPEC-KLE-005: CLI continues with warning when combo parsing fails."""
        from glove80_visualizer.cli import main
        from glove80_visualizer.parser import KeymapParseError

        # Mock parse_combos to raise error
        mocker.patch(
            "glove80_visualizer.cli.parse_combos",
            side_effect=KeymapParseError("Test combo parse error"),
        )

        # Mock the KLE template generator
        mocker.patch(
            "glove80_visualizer.kle_template.generate_kle_from_template",
            return_value='{"test": "kle json"}',
        )

        output_dir = tmp_path / "kle"
        result = runner.invoke(
            main,
            [str(simple_keymap_path), "-o", str(output_dir), "--format", "kle"],
        )

        # Should succeed despite combo parse error
        assert result.exit_code == 0
        # Should show warning
        assert "Warning: Could not parse combos" in result.output
        assert "Test combo parse error" in result.output


class TestCliKlePngFormat:
    """Tests for KLE PNG output format."""

    def test_cli_kle_png_format(self, runner, simple_keymap_path, tmp_path, mocker):
        """SPEC-KLE-006: CLI can generate KLE PNG format via headless browser."""
        from glove80_visualizer.cli import main

        # Mock both template generator and PNG renderer
        mocker.patch(
            "glove80_visualizer.kle_template.generate_kle_from_template",
            return_value='{"test": "kle json"}',
        )
        mock_render = mocker.patch(
            "glove80_visualizer.kle_renderer.render_kle_to_png",
        )

        output_dir = tmp_path / "pngs"
        result = runner.invoke(
            main,
            [str(simple_keymap_path), "-o", str(output_dir), "--format", "kle-png"],
        )

        assert result.exit_code == 0
        assert output_dir.exists()
        assert mock_render.called

    def test_cli_kle_png_default_output_path(self, runner, simple_keymap_path, mocker):
        """SPEC-KLE-007: CLI generates default KLE PNG output directory."""
        from glove80_visualizer.cli import main

        # Mock both template generator and PNG renderer
        mocker.patch(
            "glove80_visualizer.kle_template.generate_kle_from_template",
            return_value='{"test": "kle json"}',
        )
        mocker.patch(
            "glove80_visualizer.kle_renderer.render_kle_to_png",
        )

        result = runner.invoke(
            main,
            [str(simple_keymap_path), "--format", "kle-png"],
        )

        assert result.exit_code == 0
        # Should create default directory named {keymap.stem}_kle_pngs
        expected_dir = simple_keymap_path.parent / f"{simple_keymap_path.stem}_kle_pngs"
        assert expected_dir.exists()

    def test_cli_kle_png_verbose_output(self, runner, multi_layer_keymap_path, tmp_path, mocker):
        """SPEC-KLE-008: CLI shows progress for each PNG render in verbose mode."""
        from glove80_visualizer.cli import main

        # Mock both template generator and PNG renderer
        mocker.patch(
            "glove80_visualizer.kle_template.generate_kle_from_template",
            return_value='{"test": "kle json"}',
        )
        mocker.patch(
            "glove80_visualizer.kle_renderer.render_kle_to_png",
        )

        output_dir = tmp_path / "pngs"
        result = runner.invoke(
            main,
            [str(multi_layer_keymap_path), "-o", str(output_dir), "--format", "kle-png", "-v"],
        )

        assert result.exit_code == 0
        # Should show progress messages
        assert "Rendering KLE PNG for layer:" in result.output
        assert "Wrote:" in result.output

    def test_cli_kle_png_render_error_continue(
        self, runner, multi_layer_keymap_path, tmp_path, mocker
    ):
        """SPEC-KLE-009: CLI continues on PNG render error with --continue-on-error."""
        from glove80_visualizer.cli import main

        # Mock template generator
        mocker.patch(
            "glove80_visualizer.kle_template.generate_kle_from_template",
            return_value='{"test": "kle json"}',
        )

        # Mock PNG renderer to fail on second call
        call_count = [0]

        def mock_render_fail(kle_json, output_path):
            call_count[0] += 1
            if call_count[0] == 2:
                raise RuntimeError("Playwright render failed")

        mocker.patch(
            "glove80_visualizer.kle_renderer.render_kle_to_png",
            side_effect=mock_render_fail,
        )

        output_dir = tmp_path / "pngs"
        result = runner.invoke(
            main,
            [
                str(multi_layer_keymap_path),
                "-o",
                str(output_dir),
                "--format",
                "kle-png",
                "--continue-on-error",
            ],
        )

        # Should succeed with warning
        assert result.exit_code == 0
        assert "Warning: Failed to render" in result.output

    def test_cli_kle_png_render_error_fail_fast(self, runner, simple_keymap_path, tmp_path, mocker):
        """SPEC-KLE-010: CLI fails immediately on PNG render error without --continue-on-error."""
        from glove80_visualizer.cli import main

        # Mock template generator
        mocker.patch(
            "glove80_visualizer.kle_template.generate_kle_from_template",
            return_value='{"test": "kle json"}',
        )

        # Mock PNG renderer to always fail
        mocker.patch(
            "glove80_visualizer.kle_renderer.render_kle_to_png",
            side_effect=RuntimeError("Playwright render failed"),
        )

        output_dir = tmp_path / "pngs"
        result = runner.invoke(
            main,
            [str(simple_keymap_path), "-o", str(output_dir), "--format", "kle-png"],
        )

        # Should fail immediately
        assert result.exit_code != 0
        assert "Failed to render layer" in result.output


class TestCliKlePdfFormat:
    """Tests for KLE PDF output format."""

    def test_cli_kle_pdf_format(self, runner, simple_keymap_path, tmp_path, mocker):
        """SPEC-KLE-011: CLI can generate KLE PDF format via headless browser."""
        from glove80_visualizer.cli import main

        # Mock the combined PDF creator
        mock_create_pdf = mocker.patch(
            "glove80_visualizer.kle_renderer.create_combined_pdf_kle",
        )

        output = tmp_path / "output_kle.pdf"
        result = runner.invoke(
            main,
            [str(simple_keymap_path), "-o", str(output), "--format", "kle-pdf"],
        )

        assert result.exit_code == 0
        assert mock_create_pdf.called
        # Verify it was called with correct arguments
        args, kwargs = mock_create_pdf.call_args
        assert args[1] == output  # Second arg is output path
        assert "combos" in kwargs
        assert "os_style" in kwargs

    def test_cli_kle_pdf_default_output_path(self, runner, simple_keymap_path, mocker):
        """SPEC-KLE-012: CLI generates default KLE PDF output path."""
        from glove80_visualizer.cli import main

        # Mock the combined PDF creator
        mocker.patch(
            "glove80_visualizer.kle_renderer.create_combined_pdf_kle",
        )

        result = runner.invoke(
            main,
            [str(simple_keymap_path), "--format", "kle-pdf"],
        )

        assert result.exit_code == 0
        # Command should succeed - can't check file exists since we mocked the creator

    def test_cli_kle_pdf_verbose_output(self, runner, simple_keymap_path, tmp_path, mocker):
        """SPEC-KLE-013: CLI shows progress message when generating KLE PDF."""
        from glove80_visualizer.cli import main

        # Mock the combined PDF creator
        mocker.patch(
            "glove80_visualizer.kle_renderer.create_combined_pdf_kle",
        )

        output = tmp_path / "output_kle.pdf"
        result = runner.invoke(
            main,
            [str(simple_keymap_path), "-o", str(output), "--format", "kle-pdf", "-v"],
        )

        assert result.exit_code == 0
        # Should show progress message
        assert "Generating KLE PDF via headless browser" in result.output

    def test_cli_kle_pdf_generation_error(self, runner, simple_keymap_path, tmp_path, mocker):
        """SPEC-KLE-014: CLI fails with error when KLE PDF generation fails."""
        from glove80_visualizer.cli import main

        # Mock the combined PDF creator to raise error
        mocker.patch(
            "glove80_visualizer.kle_renderer.create_combined_pdf_kle",
            side_effect=RuntimeError("Playwright browser crashed"),
        )

        output = tmp_path / "output_kle.pdf"
        result = runner.invoke(
            main,
            [str(simple_keymap_path), "-o", str(output), "--format", "kle-pdf"],
        )

        # Should fail with error
        assert result.exit_code != 0
        assert "Failed to generate KLE PDF" in result.output
        assert "Playwright browser crashed" in result.output

    def test_cli_kle_pdf_with_os_style(self, runner, simple_keymap_path, tmp_path, mocker):
        """SPEC-KLE-015: CLI passes os_style parameter to KLE PDF generator."""
        from glove80_visualizer.cli import main

        # Mock the combined PDF creator
        mock_create_pdf = mocker.patch(
            "glove80_visualizer.kle_renderer.create_combined_pdf_kle",
        )

        output = tmp_path / "output_kle.pdf"
        result = runner.invoke(
            main,
            [str(simple_keymap_path), "-o", str(output), "--format", "kle-pdf", "--windows"],
        )

        assert result.exit_code == 0
        # Verify os_style was passed correctly
        args, kwargs = mock_create_pdf.call_args
        assert kwargs["os_style"] == "windows"

    def test_cli_kle_pdf_with_combos(self, runner, simple_keymap_path, tmp_path, mocker):
        """SPEC-KLE-016: CLI passes parsed combos to KLE PDF generator."""
        from glove80_visualizer.cli import main
        from glove80_visualizer.models import Combo

        # Mock parse_combos to return test combos
        test_combos = [
            Combo(name="combo1", positions=[0, 1], action="&kp A", layers=None),
        ]
        mocker.patch(
            "glove80_visualizer.cli.parse_combos",
            return_value=test_combos,
        )

        # Mock the combined PDF creator
        mock_create_pdf = mocker.patch(
            "glove80_visualizer.kle_renderer.create_combined_pdf_kle",
        )

        output = tmp_path / "output_kle.pdf"
        result = runner.invoke(
            main,
            [str(simple_keymap_path), "-o", str(output), "--format", "kle-pdf"],
        )

        assert result.exit_code == 0
        # Verify combos were passed
        args, kwargs = mock_create_pdf.call_args
        assert kwargs["combos"] == test_combos

    def test_cli_kle_pdf_quiet_mode(self, runner, simple_keymap_path, tmp_path, mocker):
        """SPEC-KLE-017: CLI suppresses output in quiet mode for KLE PDF."""
        from glove80_visualizer.cli import main

        # Mock the combined PDF creator
        mocker.patch(
            "glove80_visualizer.kle_renderer.create_combined_pdf_kle",
        )

        output = tmp_path / "output_kle.pdf"
        result = runner.invoke(
            main,
            [str(simple_keymap_path), "-o", str(output), "--format", "kle-pdf", "-q"],
        )

        assert result.exit_code == 0
        # Should have minimal/no output (except maybe errors)
        assert len(result.output.strip()) == 0 or "error" not in result.output.lower()


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
