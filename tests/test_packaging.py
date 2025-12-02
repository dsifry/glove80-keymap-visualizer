"""
Tests for package building and metadata.

These tests verify the package can be built and installed correctly.
"""

import subprocess
import sys
from pathlib import Path

import pytest

# Get project root (parent of tests directory)
PROJECT_ROOT = Path(__file__).parent.parent


class TestPackageBuilding:
    """Tests for package build process."""

    @pytest.mark.slow
    def test_package_builds(self, tmp_path: Path) -> None:
        """SPEC-CI-005: Package builds without errors."""
        result = subprocess.run(
            [sys.executable, "-m", "build", "--outdir", str(tmp_path)],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0, f"Build failed: {result.stderr}"
        assert any(tmp_path.glob("*.whl")), "No wheel file created"
        assert any(tmp_path.glob("*.tar.gz")), "No source distribution created"


class TestPackageMetadata:
    """Tests for package metadata."""

    def test_package_metadata(self) -> None:
        """SPEC-CI-006: Package metadata is correct."""
        from glove80_visualizer import __version__

        # Version should be a valid semver-like string
        assert __version__, "Version should not be empty"
        assert "." in __version__, "Version should contain dots"

    def test_package_name_importable(self) -> None:
        """Package can be imported by name."""
        import glove80_visualizer

        assert glove80_visualizer is not None


class TestCliEntryPoint:
    """Tests for CLI entry point."""

    def test_cli_entry_point(self) -> None:
        """SPEC-CI-007: CLI entry point works."""
        result = subprocess.run(
            [sys.executable, "-m", "glove80_visualizer.cli", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        # Version could be in stdout or stderr depending on Click version
        output = result.stdout + result.stderr
        assert "0." in output, f"Version not found in output: {output}"

    def test_cli_help(self) -> None:
        """CLI --help works correctly."""
        result = subprocess.run(
            [sys.executable, "-m", "glove80_visualizer.cli", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "keymap" in result.stdout.lower() or "glove80" in result.stdout.lower()
