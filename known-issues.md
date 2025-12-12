# Known Issues - KLE Output Feature Branch

## HRM Key Alignment (In Progress)

**Problem**: Home Row Mod (HRM) keys (A, S, D, K, L with Ctrl/Alt/Cmd holds) display the tap letter at the top-left of the key instead of centered like regular single-letter keys.

**Current state**:
- Regular keys (Q, W, E, R, T, etc.) display centered correctly
- HRM keys show the letter at top and modifier at front/bottom
- Multiple alignment values have been tested (a=0, 3, 4, 5, 6, 7) without achieving true centering

**Root cause analysis**:
- KLE alignment bit flags: 0x01=X-center, 0x02=Y-center, 0x04=front-center
- Single-label keys with `a=7` center correctly
- Multi-position labels (letter at pos 0, modifier at pos 4 or 5) don't center the letter vertically regardless of alignment value
- This appears to be a limitation of how KLE handles multi-position legends

**Attempted solutions**:
1. Various alignment values (0, 3, 4, 5, 6, 7)
2. Different label positions (4 vs 5 for modifier)
3. Matching "Back space" key format (which also has text at top, not centered)
4. Using `fa` (font array) property

**Possible next steps**:
1. Accept that HRM keys will have letter at top (consistent with "Back space" behavior)
2. Try using only the letter (no modifier text) and rely on color coding
3. Investigate if the SPACE key profile affects text rendering
4. Test directly in KLE website to understand position/alignment behavior better

## Sticky Shift Font Issues

**Problem**: "Shift sticky" keys have incorrect font sizing - text appears too large.

**Affected keys**: Left and right Shift sticky keys (R5)

## RGB Key Issues

**Problem**: RGB keys have font/display issues.

**Affected keys**: RGB keys on R6 (both left and right sides)

## Thumb Key Issues

**Problem**: Thumb cluster keys have multiple issues:
- Text placement is incorrect
- Font sizes are off

**Affected keys**: All thumb cluster keys (T1-T6 positions)

---

## Other Notes

- The original kle_template.py (commit 09214f1) did not have special HRM handling
- Hold layer labels (like "Cursor" on "Back space") display correctly at position 5 with `fa` array
