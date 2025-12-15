"""Test that row and column labels have consistent font sizes and positions in KLE output."""

import json
from pathlib import Path

import pytest


def get_label_props(kle_data: list) -> dict:
    """Extract font sizes and x positions for row and column labels from KLE data."""
    labels = {
        "column_labels": [],
        "row_labels_left": [],
        "row_labels_right": [],
    }

    # Track current properties (KLE cascades properties)
    current_font = None
    current_x = 0  # Cumulative x position

    for row_idx, row in enumerate(kle_data):
        if isinstance(row, list):
            # Reset x at start of each row
            current_x = 0
            for idx, item in enumerate(row):
                if isinstance(item, dict):
                    if "f" in item:
                        current_font = item["f"]
                    if "x" in item:
                        current_x += item["x"]  # x is relative offset
                elif isinstance(item, str):
                    # Column labels (C1-C6)
                    if item in ["C1", "C2", "C3", "C4", "C5", "C6"]:
                        labels["column_labels"].append(
                            {
                                "label": item,
                                "font": current_font,
                                "x": current_x,
                                "row": row_idx,
                                "idx": idx,
                            }
                        )
                    # Row labels (R1-R6)
                    elif item in ["R1", "R2", "R3", "R4", "R5", "R6"]:
                        # Determine if left or right side based on position in row
                        side = "row_labels_left" if idx < len(row) // 2 else "row_labels_right"
                        labels[side].append(
                            {
                                "label": item,
                                "font": current_font,
                                "x": current_x,
                                "row": row_idx,
                                "idx": idx,
                            }
                        )
                    # Each key takes up 1 unit of width
                    current_x += 1

    return labels


class TestKLELabelFonts:
    """Tests for consistent label fonts and positions in KLE output."""

    @pytest.fixture
    def sample_kle_output(self) -> list:
        """Load committed KLE fixture for hermetic testing."""
        kle_path = Path(__file__).parent / "fixtures" / "kle" / "sunaku-base-layer.json"
        return json.loads(kle_path.read_text(encoding="utf-8"))

    def test_column_labels_consistent_font(self, sample_kle_output):
        """All column labels (C1-C6) should have the same font size."""
        labels = get_label_props(sample_kle_output)
        column_fonts = [f["font"] for f in labels["column_labels"]]

        unique_fonts = set(column_fonts)
        assert len(unique_fonts) == 1, (
            f"Column labels have inconsistent fonts: {labels['column_labels']}"
        )

    def test_row_labels_left_consistent_font(self, sample_kle_output):
        """All left row labels (R1-R6) should have the same font size."""
        labels = get_label_props(sample_kle_output)
        row_fonts = [f["font"] for f in labels["row_labels_left"]]

        unique_fonts = set(row_fonts)
        assert len(unique_fonts) == 1, (
            f"Left row labels have inconsistent fonts: {labels['row_labels_left']}"
        )

    def test_row_labels_right_consistent_font(self, sample_kle_output):
        """All right row labels (R1-R6) should have the same font size."""
        labels = get_label_props(sample_kle_output)
        row_fonts = [f["font"] for f in labels["row_labels_right"]]

        unique_fonts = set(row_fonts)
        assert len(unique_fonts) == 1, (
            f"Right row labels have inconsistent fonts: {labels['row_labels_right']}"
        )

    def test_row_labels_match_column_labels(self, sample_kle_output):
        """Row labels should have the same font size as column labels."""
        labels = get_label_props(sample_kle_output)

        if not labels["column_labels"]:
            pytest.skip("No column labels found")

        column_font = labels["column_labels"][0]["font"]
        left_fonts = [f["font"] for f in labels["row_labels_left"]]
        right_fonts = [f["font"] for f in labels["row_labels_right"]]

        all_row_fonts = set(left_fonts + right_fonts)

        assert len(all_row_fonts) == 1, (
            f"Row labels not consistent: left={left_fonts}, right={right_fonts}"
        )

        row_font = all_row_fonts.pop()
        assert row_font == column_font, (
            f"Row labels font ({row_font}) doesn't match column labels font ({column_font})"
        )

    def test_row_labels_left_consistent_x(self, sample_kle_output):
        """All left row labels (R1-R6) should have the same x position."""
        labels = get_label_props(sample_kle_output)
        row_x_values = [f["x"] for f in labels["row_labels_left"]]

        unique_x = set(row_x_values)
        assert len(unique_x) == 1, (
            f"Left row labels have inconsistent x positions: {labels['row_labels_left']}"
        )

    def test_row_labels_right_consistent_x(self, sample_kle_output):
        """All right row labels (R1-R6) should have the same x position."""
        labels = get_label_props(sample_kle_output)
        row_x_values = [f["x"] for f in labels["row_labels_right"]]

        unique_x = set(row_x_values)
        assert len(unique_x) == 1, (
            f"Right row labels have inconsistent x positions: {labels['row_labels_right']}"
        )
