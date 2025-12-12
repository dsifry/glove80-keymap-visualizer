# Known Issues - KLE Output Feature Branch

## HRM Key Alignment ✅ RESOLVED

**Problem**: Home Row Mod (HRM) keys (A, S, D, K, L with Ctrl/Alt/Cmd holds) display the tap letter at the top-left of the key instead of centered like regular single-letter keys.

**Solution**: Set `a=7` (full centering alignment) in the KLE properties for home row HRM keys only.

**Root cause**: The template's cascading alignment value was not set to 7 for HRM key positions. When a key has multi-position labels (tap at pos 0, hold at pos 4), the `a=7` alignment flag is needed to center the tap letter horizontally.

**Fix implemented**: `kle_template.py` now detects home row HRM keys (ZMK positions 35-44 with both tap AND hold) and injects `{"a": 7}` in the preceding property dict. Tests added in `test_kle_generator.py::TestKLEHRMAlignment`.

## Sticky Shift Font Issues ✅ RESOLVED

**Problem**: "Shift sticky" keys had incorrect font sizing - the template's `fa: [2, 1]` array forced very small fonts.

**Solution**: Dynamic font size logic now sets appropriate font sizes for R5 outer keys (ZMK 46, 63, 68) and removes the `fa` array override.

**Fix implemented**: `kle_template.py` identifies outer special keys and sets font sizes based on label length (f=4 for short labels, f=3 for medium, f=2 for long).

## RGB Key Issues ✅ RESOLVED

**Problem**: RGB keys had small font sizing with `f: 3`.

**Solution**: Same dynamic font size logic applied to R6 outer keys (ZMK 64, 79).

**Fix implemented**: RGB keys now get appropriate font sizes based on label content.

## Thumb Key Issues ✅ RESOLVED

**Problem**: Thumb cluster keys had multiple issues:
- Font sizes too small (template used `f: 3` and `fa: [1, 1]`)
- Text cramped and hard to read

**Solution**: Dynamic font size logic for all thumb cluster keys (ZMK 52-57 left, 69-74 right):
- Short labels (1-3 chars): f=4
- Medium labels (4-6 chars): f=3
- Long labels (7+ chars): f=2
- Removes `fa` array to use consistent sizing

**Fix implemented**: `kle_template.py` now handles thumb cluster positions with adaptive font sizing.

## R2C6 Left Key Mapping ✅ RESOLVED

**Problem**: The leftmost key on the number row (R2C6 left, ZMK position 10 - typically '=/+') was displaying in the home row area instead of the number row.

**Root cause**: The `TEMPLATE_POSITIONS` array was missing a slot for position (5, 3) - the R2 outer left position in Sunaku's KLE template. ZMK 10 was incorrectly mapped to slot 29 at position (9, 3) which is on the home row.

**Solution**:
- Added slot 80 at position (5, 3) for R2C6 left
- Updated ZMK 10 mapping to use slot 80 instead of slot 29

**Fix implemented**: `kle_template.py` now correctly maps ZMK 10 to the number row position. Test added: `test_outer_column_r2_equals_key` (KLE-036).

---

## Summary of Changes

All fixes implemented in `src/glove80_visualizer/kle_template.py`:

1. **Home row HRM alignment**: Only positions 35-44 get `a=7` for centered tap letters
2. **Dynamic font sizing**: Thumb keys and outer R5/R6 keys get font sizes based on label length
3. **Remove restrictive `fa` arrays**: Prevents template's small font arrays from overriding our sizing
4. **R2C6 left key mapping**: Added slot 80 for position (5, 3), fixed ZMK 10 mapping

Tests added in `tests/test_kle_generator.py`:

**TestKLEHRMAlignment:**
- `test_hrm_key_has_centered_alignment` (KLE-032)
- `test_hrm_key_label_format_tap_then_hold` (KLE-033)
- `test_regular_key_does_not_get_hrm_alignment` (KLE-034)
- `test_thumb_key_with_hold_does_not_get_hrm_alignment` (KLE-035)

**TestKLEKeyMapping:**
- `test_outer_column_r2_equals_key` (KLE-036)
