"""
KLE Template-based generator.

Uses Sunaku's KLE JSON as a template and populates it with actual keymap bindings.
This preserves all the careful positioning, rotations, and styling.
"""

import json
import copy
from pathlib import Path
from typing import Any

from glove80_visualizer.models import Layer, KeyBinding, Combo
from glove80_visualizer.svg_generator import format_key_label, get_shifted_char


# Template file location
TEMPLATE_PATH = Path(__file__).parent.parent.parent / "tests" / "fixtures" / "kle" / "sunaku-base-layer.json"


def load_template() -> list[Any]:
    """Load Sunaku's KLE template."""
    with open(TEMPLATE_PATH) as f:
        return json.load(f)


# Template positions: (row_idx, item_idx) for each slot
# These are the locations in Sunaku's KLE JSON array where key labels go
# Slot numbers are used in ZMK_TO_SLOT mapping below
TEMPLATE_POSITIONS = [
    # Main body keys (slots 0-54)
    # Row 4 (JSON index 4): Number row inner 2-5, 6-9
    (4, 1),   # slot 0: 2
    (4, 2),   # slot 1: 3
    (4, 3),   # slot 2: 4
    (4, 4),   # slot 3: 5
    (4, 6),   # slot 4: 6
    (4, 7),   # slot 5: 7
    (4, 8),   # slot 6: 8
    (4, 9),   # slot 7: 9
    # Row 5 (JSON index 5): Number row outer 1, 0
    (5, 5),   # slot 8: 1
    (5, 7),   # slot 9: 0
    # Row 6 (JSON index 6): QWERTY inner W,E,R,T | Y,U,I,O
    (6, 1),   # slot 10: W
    (6, 2),   # slot 11: E
    (6, 3),   # slot 12: R
    (6, 4),   # slot 13: T
    (6, 6),   # slot 14: Y
    (6, 7),   # slot 15: U
    (6, 8),   # slot 16: I
    (6, 9),   # slot 17: O
    # Row 7 (JSON index 7): QWERTY outer Q | P
    (7, 5),   # slot 18: Q
    (7, 7),   # slot 19: P
    (7, 9),   # slot 20: - (legacy comment, but actually used for ZMK 33 backslash)
    # Row 8 (JSON index 8): Home row inner S,D,F,G | H,J,K,L
    (8, 1),   # slot 21: S
    (8, 3),   # slot 22: D
    (8, 5),   # slot 23: F
    (8, 7),   # slot 24: G
    (8, 9),   # slot 25: H
    (8, 11),  # slot 26: J
    (8, 13),  # slot 27: K
    (8, 15),  # slot 28: L
    # Row 9 (JSON index 9): Home row outer =,A | ;,'
    (9, 3),   # slot 29: =
    (9, 5),   # slot 30: A
    (9, 7),   # slot 31: ;
    (9, 9),   # slot 32: '
    # Row 10 (JSON index 10): Bottom inner X,C,V,B | N,M,<,>
    # Note: [0]=props, [1]=key, [2]=props, [3-5]=keys, [6]=gap props, [7-10]=keys
    (10, 1),  # slot 33: X
    (10, 3),  # slot 34: C (skip [2] which is props)
    (10, 4),  # slot 35: V
    (10, 5),  # slot 36: B
    (10, 7),  # slot 37: N (skip [6] which is gap props)
    (10, 8),  # slot 38: M
    (10, 9),  # slot 39: ,
    (10, 10), # slot 40: .
    # Row 11 (JSON index 11): Bottom outer Lower,Z | /,Lower
    (11, 3),  # slot 41: Lower_L
    (11, 5),  # slot 42: Z
    (11, 7),  # slot 43: /
    (11, 9),  # slot 44: Lower_R
    # Row 12 (JSON index 12): Lower row [,] | \,PageUp,ScrollUp,ScrollDown
    (12, 1),  # slot 45: [
    (12, 2),  # slot 46: ]
    (12, 4),  # slot 47: \ (Emoji slot)
    (12, 6),  # slot 48: PgUp/World
    (12, 8),  # slot 49: ScrollUp
    (12, 9),  # slot 50: ScrollDown
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
    (5, 9),   # slot 67: R2C6 right (-/_) - ZMK 21
    (7, 3),   # slot 68: R3C6 left (Tab) - ZMK 22
    (9, 3),   # slot 69: R4C6 left (Caps) - ZMK 34 (alternate to slot 29)
    # Function row R1 (slots 70-79) - ZMK 0-9
    # Left side R1: ZMK 0-4 (C6 to C2)
    (2, 1),   # slot 70: R1C4 left - ZMK 2
    (2, 2),   # slot 71: R1C3 left - ZMK 3
    (2, 3),   # slot 72: R1C2 left - ZMK 4
    (3, 3),   # slot 73: R1C1 left - ZMK 5 (inner)
    (3, 4),   # slot 74: Extra left slot
    # Right side R1: ZMK 5-9 (C2 to C6)
    (3, 6),   # slot 75: R1C1 right - ZMK 6 (inner)
    (3, 7),   # slot 76: Extra right slot
    (2, 7),   # slot 77: R1C2 right - ZMK 7
    (2, 8),   # slot 78: R1C3 right - ZMK 8
    (2, 9),   # slot 79: R1C4 right - ZMK 9
    # R2 outer left (slot 80) - for ZMK 10 (=/+)
    (5, 3),   # slot 80: R2C6 left (=/+) - ZMK 10
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
    # Function row (ZMK 0-9): R1 - mapped to slots 70-79
    # R1 has 5 keys per side: C6 (outer), C5, C4, C3, C2 (no C1 on R1)
    # Template structure: Row 2 has inner keys (C4,C3,C2), Row 3 has outer keys (C6,C5)
    # Left side (ZMK 0-4): C6->C2 (outer to inner)
    0: 74,   # ZMK 0 (C6 outer) -> slot 74 (row 3, item 4)
    1: 73,   # ZMK 1 (C5) -> slot 73 (row 3, item 3)
    2: 70,   # ZMK 2 (C4) -> slot 70 (row 2, item 1)
    3: 71,   # ZMK 3 (C3) -> slot 71 (row 2, item 2)
    4: 72,   # ZMK 4 (C2 inner) -> slot 72 (row 2, item 3)
    # Right side (ZMK 5-9): C2->C6 (inner to outer)
    5: 77,   # ZMK 5 (C2 inner) -> slot 77 (row 2, item 7)
    6: 78,   # ZMK 6 (C3) -> slot 78 (row 2, item 8)
    7: 79,   # ZMK 7 (C4) -> slot 79 (row 2, item 9)
    8: 75,   # ZMK 8 (C5) -> slot 75 (row 3, item 6)
    9: 76,   # ZMK 9 (C6 outer) -> slot 76 (row 3, item 7)

    # Number row (ZMK 10-21)
    # ZMK: 10==/+, 11=1, 12=2, 13=3, 14=4, 15=5 | 16=6, 17=7, 18=8, 19=9, 20=0, 21=-
    # ZMK 10 is the leftmost key on number row (R2C6 left)
    10: 80,  # =/+ -> R2C6 left (slot 80)
    11: 8,   # 1 -> slot 8
    12: 0,   # 2 -> slot 0
    13: 1,   # 3 -> slot 1
    14: 2,   # 4 -> slot 2
    15: 3,   # 5 -> slot 3
    16: 4,   # 6 -> slot 4
    17: 5,   # 7 -> slot 5
    18: 6,   # 8 -> slot 6
    19: 7,   # 9 -> slot 7
    20: 9,   # 0 -> slot 9
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
    # Caps (34) has no main slot in template
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


def generate_kle_from_template(
    layer: Layer,
    title: str | None = None,
    combos: list[Combo] | None = None,
) -> str:
    """
    Generate KLE JSON using Sunaku's template.

    Args:
        layer: Layer object with bindings
        title: Optional title (uses layer.name if not provided)
        combos: Optional list of combos to display in text blocks

    Returns:
        KLE JSON string
    """
    template = load_template()
    kle_data = copy.deepcopy(template)

    # Build position map from layer bindings
    pos_map = {b.position: b for b in layer.bindings}

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
                label = _format_binding_label(binding)
                row[item_idx] = label

                # Check if this is an HRM key on the home row (R4)
                # Home row positions: ZMK 35-44 (A,S,D,F,G on left; H,J,K,L,; on right)
                HOME_ROW_POSITIONS = set(range(35, 45))
                is_home_row_hrm = (
                    zmk_pos in HOME_ROW_POSITIONS
                    and binding.tap
                    and binding.hold
                    and binding.hold != "None"
                )

                # Thumb cluster positions: ZMK 52-57 (left) and 69-74 (right)
                THUMB_POSITIONS = set(range(52, 58)) | set(range(69, 75))
                # R5/R6 outer column positions (Sticky Shift, RGB keys)
                OUTER_R5_R6_POSITIONS = {46, 63, 64, 68, 79}  # Sticky shift and RGB
                is_thumb_key = zmk_pos in THUMB_POSITIONS
                is_outer_special = zmk_pos in OUTER_R5_R6_POSITIONS

                # Calculate appropriate font size based on label content
                # Get the longest line in the label for font size calculation
                label_lines = label.split('\n')
                max_line_len = max((len(line) for line in label_lines if line), default=0)

                # Check if this key has a shifted character (two-line legend: "shifted\nunshifted")
                # These need a=5 alignment for proper KLE rendering
                has_shifted_char = (
                    '\n' in label
                    and len(label_lines) >= 2
                    and label_lines[0]  # Has shifted char on first line
                    and label_lines[1]  # Has unshifted char on second line
                    and not binding.hold  # Not a hold-tap key (those use different format)
                )

                # Font size logic:
                # - f=5: short labels (1-2 chars) on regular keys
                # - f=4: medium labels (3-5 chars) or thumb/outer special keys
                # - f=3: longer labels (6+ chars)
                # - f=2: very long labels (10+ chars)
                needs_font_adjustment = is_thumb_key or is_outer_special
                if needs_font_adjustment:
                    if max_line_len <= 3:
                        target_font = 4
                    elif max_line_len <= 6:
                        target_font = 3
                    else:
                        target_font = 2
                else:
                    target_font = None  # Use template default for regular keys

                # Handle preceding property dict
                if item_idx > 0 and isinstance(row[item_idx - 1], dict):
                    props = row[item_idx - 1]
                    # Remove ghost flag when we're putting actual content there
                    if props.get("g") is True:
                        props["g"] = False
                    # Set a=7 alignment for home row HRM keys to center the tap letter
                    if is_home_row_hrm:
                        props["a"] = 7
                    # Set a=5 alignment for keys with shifted characters (two-line legend)
                    elif has_shifted_char:
                        props["a"] = 5
                    # Set font size for thumb/outer special keys
                    if needs_font_adjustment and target_font:
                        props["f"] = target_font
                        # Remove fa array if present to use consistent font
                        if "fa" in props:
                            del props["fa"]
                elif is_home_row_hrm:
                    # No preceding property dict - insert one with a=7
                    row.insert(item_idx, {"a": 7})
                elif has_shifted_char:
                    # No preceding property dict - insert one with a=5 for shifted chars
                    row.insert(item_idx, {"a": 5})
                elif needs_font_adjustment and target_font:
                    # No preceding property dict - insert one with font size
                    row.insert(item_idx, {"f": target_font})

    return json.dumps(kle_data, indent=2)


def _format_binding_label(binding: KeyBinding) -> str:
    """Format a binding as a KLE label string."""
    tap = binding.tap or ""
    hold = binding.hold if binding.hold and binding.hold != "None" else ""
    shifted = binding.shifted if binding.shifted and binding.shifted != "None" else ""

    # Format for nice display
    tap_fmt = format_key_label(tap, "mac") if tap else ""
    hold_fmt = format_key_label(hold, "mac") if hold else ""

    # Auto-calculate shifted character if not already provided
    # This adds shifted characters for numbers (1→!, 2→@) and punctuation
    if not shifted and tap_fmt:
        auto_shifted = get_shifted_char(tap_fmt)
        if auto_shifted:
            shifted = auto_shifted

    # KLE uses newlines for 12-position legend format
    # Position 0 = top-left, 1 = bottom-left, 5 = center-left
    # For hold-tap: tap on top (or center), hold at bottom
    if shifted and hold_fmt:
        return f"{shifted}\n{tap_fmt}\n\n\n{hold_fmt}"
    elif shifted:
        return f"{shifted}\n{tap_fmt}"
    elif hold_fmt:
        return f"{tap_fmt}\n\n\n\n{hold_fmt}"
    else:
        return tap_fmt


def _update_combo_text_blocks(
    kle_data: list[Any],
    layer_name: str,
    combos: list[Combo],
) -> None:
    """
    Update the combo text blocks in the KLE JSON with combo information.

    Left text block (row 14, first text item): left-hand and cross-hand combos
    Right text block (row 14, second text item): right-hand combos

    Args:
        kle_data: The KLE JSON data structure to modify in place
        layer_name: Name of the current layer (for filtering)
        combos: List of all combos to potentially display
    """
    # Filter combos active on this layer
    active_combos = [c for c in combos if c.is_active_on_layer(layer_name)]

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
