"""
KLE Template-based generator.

Uses Sunaku's KLE JSON as a template and populates it with actual keymap bindings.
This preserves all the careful positioning, rotations, and styling.
"""

import copy
import json
from pathlib import Path
from typing import Any

from glove80_visualizer.models import Combo, KeyBinding, Layer, LayerActivator
from glove80_visualizer.svg_generator import format_key_label, get_shifted_char

# Template file location
TEMPLATE_PATH = (
    Path(__file__).parent.parent.parent / "tests" / "fixtures" / "kle" / "sunaku-base-layer.json"
)


def load_template() -> list[Any]:
    """Load Sunaku's KLE template."""
    with open(TEMPLATE_PATH) as f:
        result: list[Any] = json.load(f)
        return result


# Template positions: (row_idx, item_idx) for each slot
# These are the locations in Sunaku's KLE JSON array where key labels go
# Slot numbers are used in ZMK_TO_SLOT mapping below
TEMPLATE_POSITIONS = [
    # Main body keys (slots 0-54)
    # Row 4 (JSON index 4): Number row inner 2-5, 6-9
    # Each key has its own props dict preceding it
    (4, 1),  # slot 0: 2
    (4, 3),  # slot 1: 3
    (4, 5),  # slot 2: 4
    (4, 7),  # slot 3: 5
    (4, 9),  # slot 4: 6
    (4, 11),  # slot 5: 7
    (4, 13),  # slot 6: 8
    (4, 15),  # slot 7: 9
    # Row 5 (JSON index 5): Number row outer 1, 0
    (5, 5),  # slot 8: 1
    (5, 7),  # slot 9: 0
    # Row 6 (JSON index 6): QWERTY inner W,E,R,T | Y,U,I,O
    # Each key has its own props dict preceding it
    (6, 1),  # slot 10: W
    (6, 3),  # slot 11: E
    (6, 5),  # slot 12: R
    (6, 7),  # slot 13: T
    (6, 9),  # slot 14: Y
    (6, 11),  # slot 15: U
    (6, 13),  # slot 16: I
    (6, 15),  # slot 17: O
    # Row 7 (JSON index 7): QWERTY outer Q | P
    (7, 5),  # slot 18: Q
    (7, 7),  # slot 19: P
    (7, 9),  # slot 20: - (legacy comment, but actually used for ZMK 33 backslash)
    # Row 8 (JSON index 8): Home row inner S,D,F,G | H,J,K,L
    (8, 1),  # slot 21: S
    (8, 3),  # slot 22: D
    (8, 5),  # slot 23: F
    (8, 7),  # slot 24: G
    (8, 9),  # slot 25: H
    (8, 11),  # slot 26: J
    (8, 13),  # slot 27: K
    (8, 15),  # slot 28: L
    # Row 9 (JSON index 9): Home row outer =,A | ;,'
    (9, 3),  # slot 29: =
    (9, 5),  # slot 30: A
    (9, 7),  # slot 31: ;
    (9, 9),  # slot 32: '
    # Row 10 (JSON index 10): Bottom inner X,C,V,B | N,M,<,>
    # Each key has its own props dict preceding it
    (10, 1),  # slot 33: X
    (10, 3),  # slot 34: C
    (10, 5),  # slot 35: V
    (10, 7),  # slot 36: B
    (10, 9),  # slot 37: N
    (10, 11),  # slot 38: M
    (10, 13),  # slot 39: ,
    (10, 15),  # slot 40: .
    # Row 11 (JSON index 11): Bottom outer Lower,Z | /,Lower
    (11, 3),  # slot 41: Lower_L
    (11, 5),  # slot 42: Z
    (11, 7),  # slot 43: /
    (11, 9),  # slot 44: Lower_R
    # Row 12 (JSON index 12): Lower row [,] | \,PageUp,ScrollUp,ScrollDown
    # Each key has its own props dict preceding it
    (12, 1),  # slot 45: [
    (12, 3),  # slot 46: ]
    (12, 5),  # slot 47: \ (Emoji slot)
    (12, 7),  # slot 48: PgUp/World
    (12, 9),  # slot 49: ScrollUp
    (12, 11),  # slot 50: ScrollDown
    # Row 13 (JSON index 13): R6 Magic,` | PgDn,Magic
    (13, 3),  # slot 51: Magic_L
    (13, 5),  # slot 52: `
    (13, 7),  # slot 53: PgDn
    (13, 9),  # slot 54: Magic_R
    # Left thumb cluster (slots 55-60)
    # Physical layout: T1 (innermost) to T3 (outermost), each with upper/lower
    (16, 1),  # slot 55: T1 upper - ZMK 52 (ESC/Function)
    (17, 1),  # slot 56: T1 lower - ZMK 69 (BKSP/Cursor)
    (20, 1),  # slot 57: T2 upper - ZMK 53 (APP/Emoji)
    (21, 1),  # slot 58: T2 lower - ZMK 70 (DEL/Number)
    (24, 1),  # slot 59: T3 upper - ZMK 54 (lower)
    (25, 1),  # slot 60: T3 lower - ZMK 71 (caps)
    # Right thumb cluster (slots 61-66)
    # Physical layout: T3 (outermost) to T1 (innermost), each with upper/lower
    (28, 1),  # slot 61: T3 upper - ZMK 55 (lower)
    (29, 1),  # slot 62: T3 lower - ZMK 72 (caps)
    (32, 1),  # slot 63: T2 upper - ZMK 56 (INSERT/World)
    (33, 1),  # slot 64: T2 lower - ZMK 73 (TAB/Mouse)
    (36, 1),  # slot 65: T1 upper - ZMK 57 (ENTER/System)
    (37, 1),  # slot 66: T1 lower - ZMK 74 (SPACE/Symbol)
    # Outer column slots (slots 67-69) - added for full keyboard support
    (5, 9),  # slot 67: R2C6 right (-/_) - ZMK 21
    (7, 3),  # slot 68: R3C6 left (Tab) - ZMK 22
    (9, 3),  # slot 69: R4C6 left (Caps) - ZMK 34 (alternate to slot 29)
    # Function row R1 (slots 70-79) - ZMK 0-9
    # Template structure mirrors left/right (2 outer + 3 inner per side):
    # - Row 2: Inner function keys (C4,C3,C2 left | C2,C3,C4 right)
    # - Row 3: Outer function keys (C6,C5 left | C5,C6 right)
    # Left outer (row 3) - each key has its own props dict
    (3, 3),  # slot 70: ZMK 0 - C6 outer left
    (3, 5),  # slot 71: ZMK 1 - C5 outer left
    # Left inner (row 2) - each key has its own props dict
    (2, 1),  # slot 72: ZMK 2 - C4 inner left
    (2, 3),  # slot 73: ZMK 3 - C3 inner left
    (2, 5),  # slot 74: ZMK 4 - C2 inner left
    # Right inner (row 2) - C2,C3,C4 mirroring left's C2,C3,C4
    (2, 9),  # slot 75: ZMK 5 - C2 inner right
    (2, 11),  # slot 76: ZMK 6 - C3 inner right
    (2, 13),  # slot 77: ZMK 7 - C4 inner right
    # Right outer (row 3) - each key has its own props dict
    (3, 7),  # slot 78: ZMK 8 - C5 outer right
    (3, 9),  # slot 79: ZMK 9 - C6 outer right
    # R2 outer left (slot 80) - ZMK 10 (equals/backtick)
    (5, 3),  # slot 80: R2C6 left (=/+) - ZMK 10
]

# ZMK to template slot mapping
# Maps ZMK firmware positions (0-79) to TEMPLATE_POSITIONS slot indices
#
# The Glove80 ZMK layout uses positions 0-79 as follows:
# Row 0 (0-9): Function row - 5 left + 5 right (no visual slots in Sunaku template)
# Row 1 (10-21): Number row - 6 left (`/~,1,2,3,4,5) + 6 right (6,7,8,9,0,-)
# Row 2 (22-33): QWERTY row - 6 left (TAB,Q,W,E,R,T) + 6 right (Y,U,I,O,P,\)
# Row 3 (34-45): Home row - 6 left (CAPS,A,S,D,F,G) + 6 right (H,J,K,L,;,')
# Row 4 (46-63): Bottom + left thumb - 6 left + 6 thumb + 6 right
# Row 5 (64-79): Lower + right thumb - 5 left + 6 thumb + 5 right

ZMK_TO_SLOT = {
    # Function row (ZMK 0-9): R1 - mapped to slots 70-79 in row 2 (after dynamic modification)
    # ZMK 0-4: Left side (C6 to C2)
    0: 70,  # ZMK 0 -> slot 70 (R1C6 left - outermost, UP arrow)
    1: 71,  # ZMK 1 -> slot 71 (R1C5 left - DOWN arrow)
    2: 72,  # ZMK 2 -> slot 72 (R1C4 left - A)
    3: 73,  # ZMK 3 -> slot 73 (R1C3 left - ^F16)
    4: 74,  # ZMK 4 -> slot 74 (R1C2 left - ^F18)
    # ZMK 5-9: Right side (C1 to C5)
    5: 75,  # ZMK 5 -> slot 75 (R1C1 right - ^F19)
    6: 76,  # ZMK 6 -> slot 76 (R1C2 right - ^F17)
    7: 77,  # ZMK 7 -> slot 77 (R1C3 right - F)
    8: 78,  # ZMK 8 -> slot 78 (R1C4 right - LEFT arrow)
    9: 79,  # ZMK 9 -> slot 79 (R1C5 right - RIGHT arrow)
    # Number row (ZMK 10-21)
    # ZMK: 10=`/~, 11=1, 12=2, 13=3, 14=4, 15=5 | 16=6, 17=7, 18=8, 19=9, 20=0, 21=-
    # Note: ZMK 21 (minus) has no dedicated slot - Sunaku's template doesn't show it
    10: 80,  # =/+ -> R2C6 left (slot 80) - number row outer
    11: 8,  # 1 -> slot 8
    12: 0,  # 2 -> slot 0
    13: 1,  # 3 -> slot 1
    14: 2,  # 4 -> slot 2
    15: 3,  # 5 -> slot 3
    16: 4,  # 6 -> slot 4
    17: 5,  # 7 -> slot 5
    18: 6,  # 8 -> slot 6
    19: 7,  # 9 -> slot 7
    20: 9,  # 0 -> slot 9
    21: 67,  # - -> slot 67 (R2C6 right)
    # QWERTY row (ZMK 22-33)
    # ZMK: 22=Tab, 23=Q, 24=W, 25=E, 26=R, 27=T | 28=Y, 29=U, 30=I, 31=O, 32=P, 33=\
    22: 68,  # Tab -> slot 68 (R3C6 left)
    23: 18,  # Q -> slot 18
    24: 10,  # W -> slot 10
    25: 11,  # E -> slot 11
    26: 12,  # R -> slot 12
    27: 13,  # T -> slot 13
    28: 14,  # Y -> slot 14
    29: 15,  # U -> slot 15
    30: 16,  # I -> slot 16
    31: 17,  # O -> slot 17
    32: 19,  # P -> slot 19
    33: 20,  # \ -> slot 20 (QWERTY outer right - position (7, 9))
    # Home row (ZMK 34-45)
    # ZMK: 34=Caps, 35=A, 36=S, 37=D, 38=F, 39=G | 40=H, 41=J, 42=K, 43=L, 44=;, 45='
    34: 29,  # Caps -> slot 29 (R4C6 left - home row outer)
    35: 30,  # A -> slot 30
    36: 21,  # S -> slot 21
    37: 22,  # D -> slot 22
    38: 23,  # F -> slot 23
    39: 24,  # G -> slot 24
    40: 25,  # H -> slot 25
    41: 26,  # J -> slot 26
    42: 27,  # K -> slot 27
    43: 28,  # L -> slot 28
    44: 31,  # ; -> slot 31
    45: 32,  # ' -> slot 32
    # Bottom row + left thumb (ZMK 46-63)
    # ZMK 46-51: Lower,Z,X,C,V,B (left bottom)
    # ZMK 52-57: left thumb (Esc,App,Lower,Lower,Ins,Enter)
    # ZMK 58-63: N,M,,,.,/,Lower (right bottom)
    46: 41,  # Lower -> slot 41
    47: 42,  # Z -> slot 42
    48: 33,  # X -> slot 33
    49: 34,  # C -> slot 34
    50: 35,  # V -> slot 35
    51: 36,  # B -> slot 36
    # Left thumb upper (ZMK 52-54) - R5 thumb section
    52: 55,  # ESC/Function -> slot 55 (T1 upper left)
    53: 57,  # APP/Emoji -> slot 57 (T2 upper left)
    54: 59,  # lower -> slot 59 (T3 upper left)
    # Right thumb upper (ZMK 55-57) - R5 thumb section
    55: 61,  # lower -> slot 61 (T3 upper right)
    56: 63,  # INSERT/World -> slot 63 (T2 upper right)
    57: 65,  # ENTER/System -> slot 65 (T1 upper right)
    58: 37,  # N -> slot 37
    59: 38,  # M -> slot 38
    60: 39,  # , -> slot 39
    61: 40,  # . -> slot 40
    62: 43,  # / -> slot 43
    63: 44,  # Lower -> slot 44
    # Lower row + right thumb (ZMK 64-79)
    # ZMK 64-68: RGB,`,{,[,Scroll (left lower)
    # ZMK 69-74: right thumb (Bksp,Del,Home,End,Tab,Space)
    # ZMK 75-79: Typing,(,),PgDn,RGB (right lower)
    64: 51,  # RGB -> slot 51 (Magic_L)
    65: 52,  # ` -> slot 52
    66: 45,  # [ -> slot 45
    67: 46,  # ] -> slot 46
    68: 47,  # shift -> slot 47 (C2 left - was Emoji/\ slot)
    # Left thumb lower (ZMK 69-71) - R6 thumb section
    69: 56,  # BKSP/Cursor -> slot 56 (T1 lower left)
    70: 58,  # DEL/Number -> slot 58 (T2 lower left)
    71: 60,  # caps -> slot 60 (T3 lower left)
    # Right thumb lower (ZMK 72-74) - R6 thumb section
    72: 62,  # caps -> slot 62 (T3 lower right)
    73: 64,  # TAB/Mouse -> slot 64 (T2 lower right)
    74: 66,  # SPACE/Symbol -> slot 66 (T1 lower right)
    # Right R6 main row (ZMK 75-79)
    # C2=shift(75), C3=((76), C4=)(77), C5=\(78), C6=Magic(79)
    75: 48,  # shift -> slot 48 (C2 right - was PgUp/World)
    76: 49,  # ( -> slot 49 (C3 right - was ScrollUp)
    77: 50,  # ) -> slot 50 (C4 right - was ScrollDown)
    78: 53,  # \ -> slot 53 (C5 right - was PgDn)
    79: 54,  # RGB -> slot 54 (C6 right - Magic_R)
}

# Keep old name for backwards compatibility
ZMK_TO_KLE_SLOT = ZMK_TO_SLOT


def _expand_function_row(kle_data: list[Any]) -> None:
    """
    Enable function row keys in the template.

    The template has two rows for function keys (matching inner/outer pattern):
    - Row 2: Inner function keys (C4,C3,C2 left | C2,C3,C4 right)
    - Row 3: Outer function keys (C6,C5 left | C5,C6 right)

    This function:
    1. Modifies row 2 to enable inner function keys (no y offset - stays below labels)
    2. Modifies row 3 to enable outer function keys (already has y=-0.5)
    """
    if len(kle_data) < 4:
        return

    # === Modify Row 2 for INNER function keys ===
    # Row 2 structure after template update:
    # idx 0: props, idx 1: key1, idx 2: props, idx 3: key2, idx 4: props, idx 5: key3
    # idx 6: title props, idx 7: title, idx 8: props, idx 9-13: key4-key6
    row2 = kle_data[2]
    if isinstance(row2, list) and len(row2) >= 14:
        # Update all left inner props (indices 0, 2, 4)
        for idx in [0, 2, 4]:
            if isinstance(row2[idx], dict):
                row2[idx]["g"] = False
                row2[idx]["c"] = "#cccccc"
                row2[idx]["t"] = "#000000"
                row2[idx]["f"] = 3
                row2[idx]["a"] = 7

        # Update all right inner props (indices 8, 10, 12)
        for idx in [8, 10, 12]:
            if isinstance(row2[idx], dict):
                row2[idx]["g"] = False
                row2[idx]["c"] = "#cccccc"
                row2[idx]["t"] = "#000000"
                row2[idx]["f"] = 3
                row2[idx]["a"] = 7

    # === Modify Row 3 for OUTER function keys ===
    # Row 3 structure after template update:
    # idx 0: R1 label props, idx 1: 'R1'
    # idx 2: props, idx 3: left C6, idx 4: props, idx 5: left C5
    # idx 6: props (with x offset), idx 7: right C5, idx 8: props, idx 9: right C6
    # idx 10: R1 label props, idx 11: 'R1'
    row3 = kle_data[3]
    if isinstance(row3, list) and len(row3) >= 10:
        # Update all outer function key props (indices 2, 4, 6, 8)
        for idx in [2, 4, 6, 8]:
            if isinstance(row3[idx], dict):
                row3[idx]["g"] = False
                row3[idx]["c"] = "#cccccc"
                row3[idx]["t"] = "#000000"
                row3[idx]["f"] = 3
                row3[idx]["a"] = 7


def generate_kle_from_template(
    layer: Layer,
    title: str | None = None,
    combos: list[Combo] | None = None,
    os_style: str = "mac",
    activators: list[LayerActivator] | None = None,
    layer_names: set[str] | None = None,
) -> str:
    """
    Generate KLE JSON using Sunaku's template.

    Args:
        layer: Layer object with bindings
        title: Optional title (uses layer.name if not provided)
        combos: Optional list of combos to display in text blocks
        os_style: OS style for modifier symbols ("mac", "windows", or "linux")
        activators: Optional list of LayerActivator objects for marking held keys
        layer_names: Optional set of layer names (distinguishes layer activations)

    Returns:
        KLE JSON string
    """
    template = load_template()
    kle_data = copy.deepcopy(template)

    # Expand row 2 to accommodate all function row keys (ZMK 0-9)
    _expand_function_row(kle_data)

    # Build position map from layer bindings
    pos_map = {b.position: b for b in layer.bindings}

    # Find held positions for this layer (keys that activate this layer when held)
    held_positions: set[int] = set()
    if activators:
        for activator in activators:
            if activator.target_layer_name == layer.name:
                held_positions.add(activator.source_position)

    # Update center metadata
    layer_title = title or layer.name
    center_html = f"<center><h1>{layer_title}</h1><p>MoErgo Glove80 keyboard</p></center>"

    # Find and update center metadata (row 2, look for <center> tag)
    for row_idx, row in enumerate(kle_data):
        if isinstance(row, list):
            for item_idx, item in enumerate(row):
                if isinstance(item, str) and "<center>" in item:
                    kle_data[row_idx][item_idx] = center_html
                    break

    # Update combo text blocks (row 14)
    _update_combo_text_blocks(kle_data, layer.name, combos or [])

    # Update key labels
    for zmk_pos, binding in pos_map.items():
        if zmk_pos not in ZMK_TO_KLE_SLOT:
            continue

        kle_slot = ZMK_TO_KLE_SLOT[zmk_pos]
        if kle_slot >= len(TEMPLATE_POSITIONS):
            continue

        row_idx, item_idx = TEMPLATE_POSITIONS[kle_slot]

        # Update the label in the template
        if row_idx < len(kle_data):
            row = kle_data[row_idx]
            if isinstance(row, list) and item_idx < len(row):
                # Check if this is a held key (activates current layer)
                is_held_key = zmk_pos in held_positions
                if is_held_key:
                    # Use raised hand emoji in tap position, "Layer" in hold position
                    # a=0 12-position grid: hand at pos 9, Layer at pos 11 (bottom)
                    label = "\n\n\n\n\n\n\n\n\n✋\n\nLayer"  # 9 newlines, hand, 2 newlines, Layer
                    row[item_idx] = label
                    if item_idx > 0 and isinstance(row[item_idx - 1], dict):
                        row[item_idx - 1]["g"] = False  # Clear ghost flag
                        row[item_idx - 1]["f"] = 3  # Medium font
                        row[item_idx - 1]["a"] = 0  # 12-position grid
                    continue  # Skip further processing for held keys

                label = _format_binding_label(binding, os_style, layer_names)
                row[item_idx] = label

                # Determine required properties for this label
                needs_multiline = "\n" in label
                has_hold = binding.hold and binding.hold != "None"

                # Check for shifted from binding OR from auto-calculated shifted in label
                # shifted+tap: 8 newlines, shifted, 2 newlines, tap
                # hold+tap: 9 newlines, tap, 2 newlines, hold
                # split layer: 9 newlines, first, 1 newline, second, 1 newline, hold
                has_shifted = binding.shifted and binding.shifted != "None"
                has_three_items = False  # For split layer names
                if not has_shifted and needs_multiline:
                    # Check if label has shifted format (content at position 8)
                    parts = label.split("\n")
                    # Position 8 content means 8 empty parts before it
                    if len(parts) > 8 and parts[8] and not parts[0]:
                        has_shifted = True
                    # Check for split layer name (3 items at positions 9, 10, 11)
                    elif len(parts) >= 12 and parts[9] and parts[10] and parts[11] and not parts[8]:
                        has_three_items = True

                # Build props for this key
                new_props: dict[str, Any] = {"g": False}
                if needs_multiline:
                    new_props["a"] = 0  # 12-position grid
                    # Calculate max label part length for font sizing
                    label_parts = [p for p in label.split("\n") if p]
                    max_part_len = max(len(p) for p in label_parts) if label_parts else 0

                    if has_shifted and has_hold:
                        # 3 items: shifted, tap, hold - smallest base
                        if max_part_len >= 6:
                            new_props["f"] = 3
                            new_props["f2"] = 2
                        elif max_part_len >= 4:
                            new_props["f"] = 3
                            new_props["f2"] = 3
                        else:
                            new_props["f"] = 4
                            new_props["f2"] = 3
                    elif has_three_items:
                        # 3 items: split layer name + hold - smallest fonts
                        if max_part_len >= 6:
                            new_props["f"] = 3
                            new_props["f2"] = 2
                        elif max_part_len >= 4:
                            new_props["f"] = 3
                            new_props["f2"] = 3
                        else:
                            new_props["f"] = 4
                            new_props["f2"] = 3
                    elif has_shifted:
                        # 2 items: shifted, tap
                        if max_part_len >= 4:
                            new_props["f"] = 5
                            new_props["f2"] = 4
                        elif max_part_len >= 3:
                            new_props["f"] = 6
                            new_props["f2"] = 5
                        else:
                            new_props["f"] = 7
                            new_props["f2"] = 6
                    elif has_hold:
                        # 2 items: tap, hold
                        if max_part_len >= 7:
                            new_props["f"] = 3
                            new_props["f2"] = 3
                        elif max_part_len >= 6:
                            new_props["f"] = 3
                            new_props["f2"] = 3
                        elif max_part_len >= 5:
                            new_props["f"] = 4
                            new_props["f2"] = 3
                        elif max_part_len >= 4:
                            new_props["f"] = 5
                            new_props["f2"] = 4
                        else:
                            new_props["f"] = 6
                            new_props["f2"] = 5
                    else:  # pragma: no cover
                        # Unreachable: all multiline labels come from shifted, hold, or split paths
                        new_props["f"] = 5
                        new_props["f2"] = 4
                else:
                    new_props["a"] = 7  # Centered single-line
                    # Adjust font size based on label length
                    label_len = len(label)
                    if label_len >= 4:
                        new_props["f"] = 3  # Small font for 4+ chars (e.g., ⌃F16)
                    elif label_len >= 3:
                        new_props["f"] = 4  # Medium font for 3 chars
                    else:
                        new_props["f"] = 5  # Standard font for 1-2 chars

                # Update preceding props dict if it exists
                if item_idx > 0 and isinstance(row[item_idx - 1], dict):
                    props = row[item_idx - 1]
                    props.update(new_props)
                    # Remove fa (font array) if present - it overrides f/f2 settings
                    props.pop("fa", None)

    return json.dumps(kle_data, indent=2)


def _simplify_direction_labels(shifted: str, tap: str) -> tuple[str, str] | None:
    """
    Simplify redundant direction labels like "Sel←L" / "Sel→L".

    When shifted and tap share a common prefix and suffix but differ only
    by an arrow direction, return simplified labels:
    - shifted: the common prefix (e.g., "Sel", "Ext")
    - tap: the expanded suffix (e.g., "Line", "Word")

    Returns None if the pattern doesn't match.
    """
    # Direction arrows that might differ between shifted/tap
    arrows = {"←", "→", "↑", "↓"}

    # Suffix mappings
    suffix_map = {
        "L": "Line",
        "W": "Word",
        "P": "Para",  # Paragraph
    }

    # Check if both have same length and differ only by arrow
    if len(shifted) != len(tap) or len(shifted) < 3:
        return None

    # Find common prefix (before arrow)
    prefix = ""
    arrow_idx = -1
    for i, (s, t) in enumerate(zip(shifted, tap)):
        if s in arrows or t in arrows:
            arrow_idx = i
            break
        if s == t:
            prefix += s
        else:
            return None  # Mismatch before arrow

    if arrow_idx == -1 or not prefix:
        return None

    # Check that arrows are at same position and are different
    if shifted[arrow_idx] not in arrows or tap[arrow_idx] not in arrows:
        return None

    # Check common suffix after arrow
    suffix = shifted[arrow_idx + 1 :]
    if suffix != tap[arrow_idx + 1 :]:
        return None

    # Expand suffix if possible
    expanded_suffix = suffix_map.get(suffix, suffix)

    return (prefix, expanded_suffix)


def _split_long_name(name: str, max_len: int = 5) -> tuple[str, str] | None:
    """
    Split a long name into two parts for display on two lines.

    Returns None if the name fits on one line.
    Returns (first_part, second_part) if split is needed.
    Truncates if the name is too long even for two lines.
    """
    if len(name) <= max_len:
        return None

    # Try to split at CamelCase boundaries
    # Find positions where lowercase is followed by uppercase
    split_points = []
    for i in range(1, len(name)):
        if name[i - 1].islower() and name[i].isupper():
            split_points.append(i)

    # Choose the best split point (closest to middle)
    if split_points:
        middle = len(name) // 2
        best_split = min(split_points, key=lambda x: abs(x - middle))
        first = name[:best_split]
        second = name[best_split:]
    else:
        # No CamelCase boundary, split at middle
        mid = len(name) // 2
        first = name[:mid]
        second = name[mid:]

    # Truncate if parts are still too long (max 7 chars each for 2 lines)
    max_part_len = 7
    if len(first) > max_part_len:
        first = first[: max_part_len - 1] + "…"
    if len(second) > max_part_len:
        second = second[: max_part_len - 1] + "…"

    return (first, second)


def _format_binding_label(
    binding: KeyBinding, os_style: str = "mac", layer_names: set[str] | None = None
) -> str:
    """Format a binding as a KLE label string.

    Args:
        binding: The key binding to format
        os_style: OS style for modifier symbols ("mac", "windows", or "linux")
        layer_names: Set of layer names to distinguish from modifiers
    """
    tap = binding.tap or ""
    hold = binding.hold if binding.hold and binding.hold != "None" else ""
    shifted = binding.shifted if binding.shifted and binding.shifted != "None" else ""

    # Format for nice display
    tap_fmt = format_key_label(tap, os_style) if tap else ""

    # For hold: if it's a layer name, display as-is; otherwise format as modifier
    if hold:
        if layer_names and hold in layer_names:
            hold_fmt = hold  # Layer name - display as-is
        else:
            hold_fmt = format_key_label(hold, os_style)  # Modifier - convert to symbol
    else:
        hold_fmt = ""

    shifted_fmt = format_key_label(shifted, os_style) if shifted else ""

    # Simplify redundant shifted/tap labels like "Sel←L" / "Sel→L"
    # When both share a common prefix and suffix, show prefix on shifted, suffix on tap
    if shifted_fmt and tap_fmt:
        simplified = _simplify_direction_labels(shifted_fmt, tap_fmt)
        if simplified:
            shifted_fmt, tap_fmt = simplified

    # Auto-calculate shifted character if not already provided
    # This adds shifted characters for numbers (1→!, 2→@) and punctuation
    if not shifted_fmt and tap_fmt:
        auto_shifted = get_shifted_char(tap_fmt)
        if auto_shifted:
            shifted_fmt = auto_shifted

    # KLE uses newlines for 12-position legend format with a=0
    # Grid layout:
    # [0]  [8]  [2]    (top row)
    # [6] [10]  [7]    (center row)
    # [1]  [9]  [3]    (bottom row)
    # [4] [11]  [5]    (front row)
    #
    # For hold-tap: tap at bottom-center (9), hold at front-center (11)
    if shifted_fmt and hold_fmt:
        # shifted at 8 (top-center), tap at 10 (center-center), hold at 11 (front-center)
        return f"\n\n\n\n\n\n\n\n{shifted_fmt}\n\n{tap_fmt}\n{hold_fmt}"
    elif shifted_fmt:
        # shifted at 8 (top-center), tap at 10 (center-center)
        return f"\n\n\n\n\n\n\n\n{shifted_fmt}\n\n{tap_fmt}"
    elif hold_fmt:
        # Check if tap is a layer name that needs splitting
        is_layer_tap = layer_names and tap_fmt in layer_names
        if is_layer_tap:
            split = _split_long_name(tap_fmt)
            if split:
                # Split layer: first@9 (bottom), second@10 (center), hold@11
                first, second = split
                return f"\n\n\n\n\n\n\n\n\n{first}\n{second}\n{hold_fmt}"
        # tap at bottom-center (9), hold at front-center (11)
        return f"\n\n\n\n\n\n\n\n\n{tap_fmt}\n\n{hold_fmt}"
    else:
        return tap_fmt


def _is_thumb_only_combo(combo: Combo) -> bool:
    """Check if a combo uses only thumb cluster keys."""
    # Thumb cluster positions: left thumb (52-57), right thumb (69-74)
    thumb_positions = set(range(52, 58)) | set(range(69, 75))
    return all(pos in thumb_positions for pos in combo.positions)


def _update_combo_text_blocks(
    kle_data: list[Any],
    layer_name: str,
    combos: list[Combo],
) -> None:
    """
    Update the combo text blocks in the KLE JSON with combo information.

    Only displays combos that use thumb cluster keys.
    Left text block (row 14, first text item): left-hand and cross-hand combos
    Right text block (row 14, second text item): right-hand combos

    Args:
        kle_data: The KLE JSON data structure to modify in place
        layer_name: Name of the current layer (for filtering)
        combos: List of all combos to potentially display
    """
    # Filter combos: active on this layer AND using only thumb keys
    active_combos = [
        c for c in combos if c.is_active_on_layer(layer_name) and _is_thumb_only_combo(c)
    ]

    # Separate into left/cross-hand and right-hand
    left_combos = [c for c in active_combos if c.is_left_hand or c.is_cross_hand]
    right_combos = [c for c in active_combos if c.is_right_hand]

    # Generate HTML for left block (name → action)
    left_html = _format_combo_list_html(left_combos, "left")

    # Generate HTML for right block (action ← name)
    right_html = _format_combo_list_html(right_combos, "right")

    # Find and update combo text blocks in row 14
    if len(kle_data) > 14 and isinstance(kle_data[14], list):
        combo_block_count = 0
        for item_idx, item in enumerate(kle_data[14]):
            if isinstance(item, str) and ("combos" in item.lower() or "<ul" in item.lower()):
                if combo_block_count == 0:
                    # First combo block = left
                    kle_data[14][item_idx] = left_html
                else:
                    # Second combo block = right
                    kle_data[14][item_idx] = right_html
                combo_block_count += 1


def _format_combo_list_html(combos: list[Combo], side: str) -> str:
    """
    Format a list of combos as HTML for the KLE text block.

    Args:
        combos: List of combos to format
        side: "left" or "right" - determines arrow direction

    Returns:
        HTML string with combo list
    """
    if not combos:
        return ""

    items = []
    for combo in combos:
        if side == "left":
            # Left block: name → action
            items.append(f"<li>{combo.name} → {combo.action}</li>")
        else:
            # Right block: action ← name
            items.append(f"<li>{combo.action} ← {combo.name}</li>")

    return f'<ul class="combos {side}">{"".join(items)}</ul>'
