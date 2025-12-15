# Task Completion Checklist

**CRITICAL**: This checklist MUST be followed before marking ANY development task as complete.

## Pre-Completion Verification Steps

### 1. Test Verification

- [ ] Run `make test` on all modified test files
- [ ] Ensure ALL tests pass (no skipped, no failures)
- [ ] Verify NO tests were removed or commented out
- [ ] If tests were modified, ensure the test logic was preserved

### 2. Type Safety Verification

- [ ] Run `make typecheck` (mypy) on all modified Python files
- [ ] Fix ALL type errors properly (no `type: ignore` unless absolutely necessary)
- [ ] If fixing test type errors, preserve all existing tests
- [ ] Follow patterns in existing codebase for type hints

### 3. Code Quality Validation (MANDATORY)

Before marking ANY task complete, you MUST run ALL validation tools:

```bash
# 1. Type Check - catches type errors
make typecheck

# 2. Lint Check - catches code quality issues
make lint

# 3. Format Check - auto-fixes formatting
make format

# 4. Run Tests - ensures nothing is broken
make test
```

**CRITICAL**:
- If you see errors in one tool (e.g., mypy) but not another (e.g., ruff), keep checking!
- The user's editor shows ALL types of errors in the Problems tab
- Missing any of these makes Claude appear incompetent

#### Validation Checklist

- [ ] Run `make typecheck` - NO errors
- [ ] Run `make lint` - NO errors or warnings
- [ ] Run `make format` - Format all modified files
- [ ] Run `make test` - ALL tests pass
- [ ] Ensure code follows patterns in existing codebase

### 4. Registry Verification

If you modified code in `src/` or fixtures in `tests/conftest.py`:

- [ ] Run `python scripts/generate_registries.py --check` - NO errors
- [ ] Run `python scripts/generate_registries.py` to regenerate registries
- [ ] Check `git diff service-registry.toon mock-registry.toon` for changes
- [ ] Include registry files in commit if they changed

**CRITICAL**: Registry validation is part of CI. Failing to update registries will fail the PR.

### 5. CI Monitoring After Push (MANDATORY)

After every `git push`, you MUST monitor CI until all checks complete:

- [ ] Run `gh pr checks <pr-number>` or `gh run list --branch <branch>` to monitor
- [ ] Wait for ALL checks to complete (not just start)
- [ ] If any check fails, investigate immediately with `gh run view <id> --log-failed`
- [ ] Fix failures locally, push fix, and re-monitor
- [ ] Only proceed when ALL checks are green

**CRITICAL**: Do NOT move on to other tasks while CI is pending or failing. Fix issues while context is fresh.

```bash
# Monitor CI status
gh pr checks <pr-number>

# Get failed job logs
gh run view <run-id> --log-failed
```

### 6. Functionality Preservation

- [ ] Existing functionality remains intact
- [ ] No regression in related features
- [ ] API contracts maintained (if applicable)
- [ ] CLI interface unchanged (unless intentionally modified)

## Special Considerations

### When Fixing Type Errors in Tests

1. **NEVER** remove tests to fix type errors
2. Add proper type imports first
3. Use `cast()` from typing for complex type assertions
4. If a test seems wrong, use extended thinking before modifying
5. Preserve the original test intent

### When Modifying Existing Code

1. Understand why the code exists before changing it
2. Check for related tests that might break
3. Verify no side effects in other parts of the system
4. Use `git diff` to review all changes before committing

### Red Flags - Stop and Think

- About to delete a test? **STOP** - Fix the type error instead
- Adding `# type: ignore`? **STOP** - Find the proper type solution
- Commenting out code? **STOP** - Fix it or remove it properly
- Tests failing? **STOP** - Don't proceed until they pass

## Final Verification

Before responding to the user that a task is complete:

1. Have you run ALL verification steps above?
2. Can you confidently say the code is production-ready?
3. Would you be comfortable deploying this change?

If any answer is "no", continue working on the task.

## Quick Reference Commands

```bash
# Full validation (run before marking complete)
make lint && make typecheck && make test && python scripts/generate_registries.py --check

# Quick test run
make test

# Format and lint fix
make format

# Registry validation
python scripts/generate_registries.py --check

# Regenerate registries
python scripts/generate_registries.py
```

## Remember

> "It's better to take extra time to do it right than to rush and introduce bugs."

The user relies on you to deliver high-quality, working code. Never compromise on these standards.
