"""
Configuration handling for the Glove80 keymap visualizer.

This module defines configuration options and defaults.
"""

from dataclasses import asdict, dataclass, fields
from pathlib import Path

import yaml


@dataclass
class VisualizerConfig:
    """
    Configuration options for the keymap visualizer.

    Attributes:
        keyboard: The keyboard type (default: "glove80")
        page_size: PDF page size ("letter" or "a4")
        orientation: Page orientation ("landscape" or "portrait")
        font_size: Base font size for key labels
        background_color: SVG background color
        key_color: Key cap color
        text_color: Primary text color
        hold_text_color: Color for hold behavior text
        include_toc: Whether to include table of contents
        layer_title_format: Format string for layer titles
        output_format: Output format ("pdf" or "svg")
        continue_on_error: Continue processing if a layer fails
    """

    # Physical layout
    keyboard: str = "glove80"

    # Page layout
    page_size: str = "letter"
    orientation: str = "landscape"

    # Styling
    key_width: int = 60
    key_height: int = 56
    font_size: int = 12
    background_color: str = "#ffffff"
    key_color: str = "#f0f0f0"
    text_color: str = "#000000"
    hold_text_color: str = "#666666"

    # PDF options
    include_toc: bool = True
    layer_title_format: str = "Layer {index}: {name}"

    # Output options
    output_format: str = "pdf"
    continue_on_error: bool = False

    # OS-specific modifier symbols
    os_style: str = "mac"  # "mac", "windows", or "linux"

    # Transparent key handling
    resolve_trans: bool = False  # Show inherited keys instead of "trans"

    # Held key indicator
    show_held_indicator: bool = True  # Show which key activates current layer

    # Color output
    show_colors: bool = False  # Apply semantic colors to keys
    show_legend: bool = True  # Show color legend when colors are enabled

    # Shifted character display
    show_shifted: bool = True  # Show shifted chars on keys (e.g., ! above 1)

    # Multi-layer page layout
    layers_per_page: int = 3  # Number of layers per PDF page (1, 2, or 3)
    dpi: int = 300  # Output resolution for PDF rendering

    @classmethod
    def from_yaml(cls, yaml_content: str) -> "VisualizerConfig":
        """
        Create a VisualizerConfig from YAML content.

        Args:
            yaml_content: YAML string with configuration values

        Returns:
            VisualizerConfig with values from YAML merged with defaults
        """
        data = yaml.safe_load(yaml_content) or {}

        # Filter to only valid field names
        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}

        return cls(**filtered_data)

    @classmethod
    def from_file(cls, path: str) -> "VisualizerConfig":
        """
        Load configuration from a YAML file.

        Args:
            path: Path to the YAML configuration file

        Returns:
            VisualizerConfig with values from file merged with defaults
        """
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(file_path) as f:
            content = f.read()

        return cls.from_yaml(content)

    def to_yaml(self) -> str:
        """
        Export configuration to YAML string.

        Returns:
            YAML representation of this configuration
        """
        return yaml.dump(asdict(self), default_flow_style=False)
