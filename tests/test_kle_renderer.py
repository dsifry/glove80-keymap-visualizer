"""
Tests for KLE (Keyboard Layout Editor) renderer.

These tests verify the headless browser rendering capability.
Note: These require playwright and chromium to be installed.
"""


import pytest

# Skip tests if playwright is not installed
pytest.importorskip("playwright")


class TestKLEJavaScriptInjection:
    """Test that KLE JSON is properly injected and rendered."""

    @pytest.fixture
    def sample_kle_json(self, sample_layer):
        """Generate sample KLE JSON for testing."""
        from glove80_visualizer.kle_template import generate_kle_from_template
        return generate_kle_from_template(sample_layer)

    @pytest.mark.slow
    def test_injection_loads_correct_number_of_keys(self, sample_kle_json):
        """KLE-INJECT-001: JavaScript injection should load all keys from JSON."""
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1920, "height": 1200})

            try:
                page.goto("https://www.keyboard-layout-editor.com/",
                         wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(2000)

                # Get initial key count (default keyboard)
                initial_keys = page.evaluate(
                    'angular.element(document.querySelector("[ng-controller]")).scope().keys.length'
                )

                # Inject our layout
                result = page.evaluate(f'''
                    (function() {{
                        try {{
                            var layout = {sample_kle_json};
                            var result = $serial.deserialize(layout);
                            var el = document.querySelector('[ng-controller]');
                            var scope = angular.element(el).scope();
                            if (scope) {{
                                scope.keys = result.keys;
                                scope.meta = result.meta;
                                scope.$apply();
                                return {{ success: true, keyCount: result.keys.length }};
                            }}
                            return {{ success: false, error: "no scope" }};
                        }} catch(e) {{
                            return {{ success: false, error: e.message }};
                        }}
                    }})()
                ''')

                assert result["success"], f"Injection failed: {result.get('error')}"
                # Our Glove80 layout should have many more keys than the default
                assert result["keyCount"] > initial_keys, \
                    f"Expected more keys than default ({initial_keys}), got {result['keyCount']}"
                # Glove80 has 80 keys + decorative labels (R1-R6, C1-C6, T1-T6) + center block
                assert result["keyCount"] >= 80, (
                    f"Expected at least 80 keys, got {result['keyCount']}"
                )

            finally:
                browser.close()

    @pytest.mark.slow
    def test_injection_creates_proper_keyboard_size(self, sample_kle_json):
        """KLE-INJECT-002: After injection, keyboard element should have proper Glove80 size."""
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1920, "height": 1200})

            try:
                page.goto("https://www.keyboard-layout-editor.com/",
                         wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(2000)

                # Inject our layout
                page.evaluate(f'''
                    (function() {{
                        var layout = {sample_kle_json};
                        var result = $serial.deserialize(layout);
                        var el = document.querySelector('[ng-controller]');
                        var scope = angular.element(el).scope();
                        if (scope) {{
                            scope.keys = result.keys;
                            scope.meta = result.meta;
                            scope.$apply();
                        }}
                    }})()
                ''')

                page.wait_for_timeout(2000)

                # Get keyboard size after injection
                new_box = page.locator("#keyboard-bg").bounding_box()

                # Glove80 layout should be reasonably wide (split keyboard with center gap)
                # At minimum it should be > 800px wide
                assert new_box["width"] > 800, \
                    f"Keyboard too narrow ({new_box['width']}px), expected > 800px for Glove80"

                # Should have reasonable height
                assert new_box["height"] > 200, \
                    f"Keyboard too short ({new_box['height']}px), expected > 200px"

            finally:
                browser.close()

    @pytest.mark.slow
    def test_screenshot_contains_custom_layout(self, sample_kle_json, tmp_path):
        """KLE-INJECT-003: Screenshot should capture the custom layout, not default."""
        from PIL import Image
        from playwright.sync_api import sync_playwright

        output_path = tmp_path / "test_layout.png"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                viewport={"width": 1920, "height": 1200}, device_scale_factor=2.0
            )

            try:
                page.goto("https://www.keyboard-layout-editor.com/",
                         wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(2000)

                # Inject our layout
                page.evaluate(f'''
                    (function() {{
                        var layout = {sample_kle_json};
                        var result = $serial.deserialize(layout);
                        var el = document.querySelector('[ng-controller]');
                        var scope = angular.element(el).scope();
                        if (scope) {{
                            scope.keys = result.keys;
                            scope.meta = result.meta;
                            scope.$apply();
                        }}
                    }})()
                ''')

                page.wait_for_timeout(2000)

                # Take screenshot
                page.locator("#keyboard-bg").screenshot(path=str(output_path))

            finally:
                browser.close()

        # Verify screenshot
        assert output_path.exists()
        img = Image.open(output_path)

        # Glove80 layout should be wide (split keyboard)
        # With scale=2.0, expect at least 1500px wide for a proper Glove80 render
        assert img.width > 1500, f"Screenshot too narrow ({img.width}px), likely default keyboard"

        # Should have reasonable height for a keyboard
        assert img.height > 400, f"Screenshot too short ({img.height}px)"


class TestKLERenderToFile:
    """Test rendering KLE JSON to files."""

    @pytest.fixture
    def sample_kle_json(self, sample_layer):
        """Generate sample KLE JSON for testing."""
        from glove80_visualizer.kle_template import generate_kle_from_template
        return generate_kle_from_template(sample_layer)

    @pytest.mark.slow
    def test_render_kle_to_png(self, sample_kle_json, tmp_path):
        """KLE-RENDER-001: Should render KLE JSON to PNG file."""
        from glove80_visualizer.kle_renderer import render_kle_to_png

        output_path = tmp_path / "test.png"
        result = render_kle_to_png(sample_kle_json, output_path)

        assert result.exists()
        assert result.suffix == ".png"
        # Check file has content (should be > 10KB for a full keyboard image)
        assert result.stat().st_size > 10000, \
            f"PNG too small ({result.stat().st_size} bytes), likely not a full keyboard render"

    @pytest.mark.slow
    def test_render_kle_to_png_correct_dimensions(self, sample_kle_json, tmp_path):
        """KLE-RENDER-001b: PNG should have correct dimensions for Glove80."""
        from PIL import Image

        from glove80_visualizer.kle_renderer import render_kle_to_png

        output_path = tmp_path / "test.png"
        render_kle_to_png(sample_kle_json, output_path)

        img = Image.open(output_path)
        # With scale=2.0 (default), expect at least 1500px wide
        assert img.width > 1500, f"PNG too narrow ({img.width}px)"
        assert img.height > 400, f"PNG too short ({img.height}px)"

    @pytest.mark.slow
    def test_render_kle_to_pdf(self, sample_kle_json, tmp_path):
        """KLE-RENDER-002: Should render KLE JSON to PDF file."""
        from glove80_visualizer.kle_renderer import render_kle_to_pdf

        output_path = tmp_path / "test.pdf"
        result = render_kle_to_pdf(sample_kle_json, output_path)

        assert result.exists()
        assert result.suffix == ".pdf"
        # PDF should be substantial (keyboard images are large)
        assert result.stat().st_size > 50000, \
            f"PDF too small ({result.stat().st_size} bytes), likely not a full keyboard render"


class TestKLERenderHelper:
    """Test convenience rendering functions."""

    @pytest.mark.slow
    def test_render_layer_kle_png(self, sample_layer, tmp_path):
        """KLE-RENDER-003: Should render Layer object to PNG."""
        from glove80_visualizer.kle_renderer import render_layer_kle

        output_path = tmp_path / "layer.png"
        result = render_layer_kle(sample_layer, output_path, output_format="png")

        assert result.exists()
        assert result.stat().st_size > 10000

    @pytest.mark.slow
    def test_render_all_layers_kle(self, sample_layers, tmp_path):
        """KLE-RENDER-004: Should render all layers to files."""
        from glove80_visualizer.kle_renderer import render_all_layers_kle

        results = render_all_layers_kle(sample_layers[:2], tmp_path, output_format="png")

        assert len(results) == 2
        for path in results:
            assert path.exists()
            assert path.stat().st_size > 10000


class TestKLERenderErrors:
    """Test error handling in renderer."""

    @pytest.mark.slow
    def test_invalid_json_still_renders(self, tmp_path):
        """KLE-RENDER-005: Invalid JSON will still produce output (KLE handles gracefully)."""
        from glove80_visualizer.kle_renderer import render_kle_to_png

        # Note: KLE website doesn't validate JSON on upload - it just shows empty/no keys
        # So this will still produce a PNG (just an empty keyboard layout)
        result = render_kle_to_png("not valid json", tmp_path / "test.png", timeout=30000)
        assert result.exists()  # File is created even with invalid JSON
