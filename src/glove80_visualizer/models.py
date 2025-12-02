"""
Data models for the Glove80 keymap visualizer.

This module defines the core data structures used throughout the application.
"""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class KeyBinding:
    """
    Represents a single key binding on the keyboard.

    Attributes:
        position: The physical key position (0-79 for Glove80)
        tap: The tap behavior/key label
        hold: Optional hold behavior (for hold-tap keys)
    """

    position: int
    tap: str
    hold: Optional[str] = None

    @property
    def is_transparent(self) -> bool:
        """Check if this is a transparent key (&trans)."""
        # TODO: Implement transparent key detection
        raise NotImplementedError()

    @property
    def is_none(self) -> bool:
        """Check if this is a none/blocked key (&none)."""
        # TODO: Implement none key detection
        raise NotImplementedError()


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
    bindings: List[KeyBinding] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        """Check if this layer has all 80 key bindings for Glove80."""
        # TODO: Implement completeness check
        raise NotImplementedError()


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
    error_message: Optional[str] = None
    layers_processed: int = 0
    output_path: Optional[str] = None
