# registry-verification

Use before completing any task that modified code in `src/` or fixtures in `tests/conftest.py` - ensures registries are valid and up-to-date before marking work complete.

**IMPORTANT**: This skill integrates with `verification-before-completion`. Always run registry verification alongside other pre-completion checks.

## When to Activate

Activate this skill when ANY of these conditions are true:

- About to mark a task as complete
- About to commit changes to `src/` or `tests/conftest.py`
- User asks to verify registries
- CI failed with registry-related errors

## Announce at Start

"I'm using the registry-verification skill to ensure registries are valid before completing this task."

## Verification Steps

### Step 1: Run Validation

```bash
python scripts/generate_registries.py --check
```

**Expected output for success:**

```text
Validation issues (0 errors, N warnings):
  [WARNING] ...  # Warnings are acceptable
Registry validation passed.
```

**If errors exist, STOP and fix them before proceeding.**

### Step 2: Regenerate Registries

```bash
python scripts/generate_registries.py
```

This regenerates both:
- `service-registry.toon` - Functions/classes from `src/`
- `mock-registry.toon` - Fixtures from `tests/conftest.py`

### Step 3: Check for Changes

```bash
git diff --stat service-registry.toon mock-registry.toon
```

If registries changed:
- They must be committed with the code changes
- DO NOT commit code without updated registries

### Step 4: Include in Commit

If registries changed, include them in the commit:

```bash
git add service-registry.toon mock-registry.toon
# Include in the same commit as the code changes
```

## Error Categories

### Errors (Must Fix)

These block task completion:

| Error | Meaning | Fix |
|-------|---------|-----|
| Missing docstring | Function has no docstring | Add Google-style docstring |
| Missing description | Docstring has no first line | Add description as first line |

### Warnings (Acceptable)

These are logged but don't block:

| Warning | Meaning | Optional Fix |
|---------|---------|--------------|
| Missing Args section | Has params but no Args | Add Args section |
| Missing Returns section | Returns value but no Returns | Add Returns section |

**Note:** While warnings are acceptable, fixing them improves documentation quality.

## Common Failure Scenarios

### Scenario: New function without docstring

```text
[ERROR] src/glove80_visualizer/parser.py: Function 'new_function' has no docstring
```

**Fix:** Add a Google-style docstring to the function.

### Scenario: Incomplete docstring

```text
[WARNING] src/glove80_visualizer/cli.py: Function 'main' has parameters but no Args section
```

**Fix (optional):** Add Args section to the docstring.

### Scenario: Registry out of sync

```text
git diff shows changes to service-registry.toon
```

**Fix:** Commit the registry changes with your code changes.

## Integration with Task Completion

This verification is part of the standard completion checklist:

```bash
# Full validation sequence
make lint && make typecheck && make test && python scripts/generate_registries.py --check
```

**DO NOT mark a task complete if:**

1. Registry validation has errors
2. Registry files have uncommitted changes
3. You haven't run the generator after code changes

## Quick Reference

```bash
# Validate only (no changes)
python scripts/generate_registries.py --check

# Validate and regenerate
python scripts/generate_registries.py

# Verbose output (shows all functions)
python scripts/generate_registries.py --verbose

# Check if registries need committing
git status service-registry.toon mock-registry.toon
```

## Verification Checklist

Before marking ANY task complete:

- [ ] `python scripts/generate_registries.py --check` shows 0 errors
- [ ] `python scripts/generate_registries.py` has been run
- [ ] `git diff` shows no uncommitted registry changes
- [ ] Registry files are included in commit (if changed)
