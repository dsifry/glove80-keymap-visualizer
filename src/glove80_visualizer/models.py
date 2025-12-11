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
class Combo:
    """
    Represents a keyboard combo (chord) - multiple keys pressed simultaneously.

    Attributes:
        name: Human-readable key names (e.g., "LT3+LT6", "RT1+RT4")
        positions: The ZMK key positions that trigger this combo
        action: Description of what the combo does (e.g., "Toggle Gaming")
        layers: List of layer names where combo is active, or None for all layers
    """

    name: str
    positions: list[int]
    action: str
    layers: list[str] | None = None

    def is_active_on_layer(self, layer_name: str) -> bool:
        """Check if this combo is active on the given layer."""
        if self.layers is None:
            return True
        return layer_name in self.layers

    @property
    def is_left_hand(self) -> bool:
        """Check if combo uses only left thumb keys."""
        left_thumb = {52, 53, 54, 69, 70, 71}
        return all(p in left_thumb for p in self.positions)

    @property
    def is_right_hand(self) -> bool:
        """Check if combo uses only right thumb keys."""
        right_thumb = {55, 56, 57, 72, 73, 74}
        return all(p in right_thumb for p in self.positions)

    @property
    def is_cross_hand(self) -> bool:
        """Check if combo spans both hands."""
        return not self.is_left_hand and not self.is_right_hand


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
