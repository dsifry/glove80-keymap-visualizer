"""
Data models for the Glove80 keymap visualizer.

This module defines the core data structures used throughout the application.
"""

from dataclasses import dataclass, field

# Constants for special key types
TRANS_MARKERS = ("&trans", "▽", "trans")
NONE_MARKERS = ("&none", "", "none")


@dataclass
class KeyBinding:
    """
    Represents a single key binding on the keyboard.

    Attributes:
        position: The physical key position (0-79 for Glove80)
        tap: The tap behavior/key label
        hold: Optional hold behavior (for hold-tap keys)
        shifted: Optional shifted character (shown at top of key, e.g., ! for 1)
        key_type: Optional type marker (e.g., "trans", "held")
    """

    position: int
    tap: str
    hold: str | None = None
    shifted: str | None = None
    key_type: str | None = None

    @property
    def is_transparent(self) -> bool:
        """Check if this is a transparent key (&trans).

        Returns:
            True if the key is transparent, False otherwise
        """
        if self.key_type == "trans":
            return True
        return self.tap.lower() in TRANS_MARKERS if self.tap else False

    @property
    def is_none(self) -> bool:
        """Check if this is a none/blocked key (&none).

        Returns:
            True if the key is none/blocked, False otherwise
        """
        if self.tap is None or self.tap == "":
            return True
        return self.tap.lower() in NONE_MARKERS


@dataclass
class Layer:
    """
    Represents a keyboard layer containing key bindings.

    Attributes:
        name: The layer name (e.g., "QWERTY", "Symbol")
        index: The layer index (0-31 for typical ZMK configs)
        bindings: List of key bindings for this layer
    """

    name: str
    index: int
    bindings: list[KeyBinding] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        """Check if this layer has all 80 key bindings for Glove80.

        Returns:
            True if the layer has exactly 80 bindings, False otherwise
        """
        return len(self.bindings) == 80


@dataclass
class LayerActivator:
    """
    Tracks which key activates a layer.

    Used to show held key indicators on layer diagrams.

    Attributes:
        source_layer_name: Name of the layer containing the activator key
        source_position: Key position (0-79) that activates the target layer
        target_layer_name: Name of the layer being activated
        tap_key: For layer-tap: the tap behavior (None for &mo behaviors)
    """

    source_layer_name: str
    source_position: int
    target_layer_name: str
    tap_key: str | None = None


@dataclass
class VisualizationResult:
    """
    Result of a visualization operation.

    Attributes:
        success: Whether the visualization completed successfully
        partial_success: Whether some output was generated despite errors
        error_message: Description of any error that occurred
        layers_processed: Number of layers successfully processed
        output_path: Path to the generated output file(s)
    """

    success: bool
    partial_success: bool = False
    error_message: str | None = None
    layers_processed: int = 0
    output_path: str | None = None
