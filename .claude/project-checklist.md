# Project Development Checklist

**For Complex Tasks Only** - Use `/project:start-task` to determine if you need this full checklist or the quick task flow.

Use this checklist for complex, multi-step tasks (> 2 hours). Claude can work through this systematically and mark items as complete.

## When to Use This Checklist

- New pipeline stages or components
- New CLI commands/options
- Complex parsing logic changes
- Multi-file refactoring
- Performance optimizations
- New output formats

## When to Use Quick Task Flow Instead

- Bug fixes
- Small feature tweaks
- Minor text/output changes
- Simple configuration updates
- Adding basic validation
- Fixing linting/test issues

## Pre-Development

- [ ] Read relevant documentation from `docs/` and `README.md`
- [ ] Understand the feature requirements and scope
- [ ] Check existing similar implementations in the codebase
- [ ] Review the 5-stage pipeline architecture
- [ ] Plan integration points with keymap-drawer/CairoSVG

## TDD Workflow (Required)

For each feature component:

- [ ] **RED**: Write failing test first
- [ ] **GREEN**: Implement minimal code to pass test
- [ ] **REFACTOR**: Improve code while keeping tests green
- [ ] Repeat for next component

## Implementation

- [ ] Create/update modules in `src/glove80_visualizer/`
- [ ] Follow existing patterns for type hints
- [ ] Implement proper error handling with actionable messages
- [ ] Add CLI options if needed in `cli.py`
- [ ] Update configuration handling if applicable

## Testing

- [ ] Write unit tests following `tests/test_*.py` patterns
- [ ] Use fixtures from `tests/conftest.py`
- [ ] Test with fixture keymaps from `tests/fixtures/`
- [ ] Test error cases and edge conditions
- [ ] Run `make test` to ensure all tests pass
- [ ] Check test coverage with `make test-cov`

## Quality Assurance

- [ ] Run `make lint` and fix any issues
- [ ] Run `make typecheck` and fix any type errors
- [ ] Run `make format` to ensure consistent formatting
- [ ] Test CLI with real keymap files
- [ ] Verify PDF output looks correct
- [ ] Test error handling and edge cases

## Documentation

- [ ] Update relevant documentation files in `docs/`
- [ ] Add docstrings to new functions (Google style)
- [ ] Update README.md if adding new features
- [ ] Document any new CLI options
- [ ] Update CLAUDE.md if adding new patterns

## Pull Request & Code Review

- [ ] Create comprehensive PR following `/project:create-pr` guidelines
- [ ] Write clear PR description with testing details
- [ ] Self-review all changes before requesting review
- [ ] Address AI code review feedback (CodeRabbit, etc.)
- [ ] Respond to human reviewer feedback
- [ ] Ensure all CI checks are passing

## Post-Implementation

- [ ] Update CHANGELOG.md with changes
- [ ] Consider version bump if needed
- [ ] Document any new patterns in CLAUDE.md

---

**Usage**: Copy relevant sections to a new file for specific tasks, then have Claude work through the checklist systematically.
