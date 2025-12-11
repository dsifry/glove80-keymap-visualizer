# CLAUDE.md - Glove80 Keymap Visualizer

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**CRITICAL**: Always follow the **[Task Completion Checklist](.claude/task-completion-checklist.md)** before marking any task as complete.

**MANDATORY VALIDATION**: Run type checking, linting, and tests on ALL modified files before completing tasks. There must be zero warnings and zero errors from these checks before a task can be considered complete.

## Essential Commands

| Command | Purpose |
|---------|---------|
| `make install-dev` | Install development dependencies |
| `make test` | Run tests (TDD - tests first!) |
| `make test-cov` | Run tests with coverage report |
| `make lint` | Check code quality (ruff) |
| `make typecheck` | Type checking (mypy) |
| `make format` | Auto-format code (black + ruff) |
| `make clean` | Clean build artifacts |

**Before marking complete**: `make lint && make typecheck && make test`

**Run tool**: `.venv/bin/glove80-viz <keymap.keymap> -o output.pdf`

## Project Overview

CLI tool that generates PDF visualizations of Glove80 keyboard layers from ZMK `.keymap` files.

## Architecture (5-stage pipeline)

```text
.keymap → Parser → YAML → Extractor → Layers → SVG Generator → PDF Generator → .pdf
              ↓                              ↓                    ↓
        keymap-drawer                  keymap-drawer          CairoSVG + pikepdf
```

## Development Rules

1. **TDD Required**: Write failing test → implement → refactor. Tests live in `tests/test_*.py`
2. **Type Hints**: All public functions must have type hints. No `Any` without justification.
3. **Error Handling**: Every external call (file I/O, keymap-drawer, CairoSVG) needs explicit error handling with actionable messages.
4. **100% Test Coverage Required**: Hard requirement - all code must have 100% test coverage. No exceptions. Use mocks for slow external dependencies (browsers, network). Run `make test-cov` to verify.
5. **Dependency Injection**: Services must be mockable. No hardcoded dependencies. Use constructor injection for external services. Create common mock factories in `tests/conftest.py`.

## Critical Guidelines

- **NEVER use `# type: ignore`** without documented justification
- **NEVER remove tests** to fix type errors
- **ALWAYS track modified files** for targeted validation
- **ALWAYS run full validation** before task completion

## Key Files & Directories

| Path | Purpose |
|------|---------|
| `src/glove80_visualizer/` | Main source code |
| `tests/` | Test files |
| `tests/conftest.py` | Pytest fixtures and mock factories |
| `tests/fixtures/*.keymap` | Test keymap files |
| `docs/{branch-name}/plans/` | Implementation plans |
| `docs/{branch-name}/specs/` | TDD specifications |
| `docs/{branch-name}/reviews/` | CTO-level reviews (timestamped) |

**Note:** `{branch-name}` uses hyphens instead of slashes. For branch `feature/my-feature`, use `docs/feature-my-feature/`.

## Custom Slash Commands

Type these directly in Claude chat:

### Task Management
- `/project:start-task <description>` - **START HERE** for task assessment
- `/project:fix-failing-tests` - Systematic test fixing

### Code Review & PRs
- `/project:review-this <path>` - CTO-level review of specs/plans/code
- `/project:create-pr <branch>` - Create comprehensive PR
- `/project:handle-pr-comments <pr-number>` - Handle PR review feedback
- `/project:pr-shepherd [pr-number]` - **Monitor PR through to merge** - watches CI/CD, handles reviews, auto-fixes issues

### Session Management
- `/project:save-session [name]` - Save current conversation context
- `/project:load-session [identifier]` - Load a previous session
- `/project:list-sessions [options]` - Browse saved sessions
- `/project:manage-sessions` - Organize and maintain sessions

### Worktree Management
- `/project:worktree-status` - Show current worktree context and all active worktrees
- `/project:worktree-create <name> <branch>` - Create a new worktree for parallel development
- `/project:peek-branch <branch> <file>` - View a file from another branch without switching
- `/project:agent-handoff [target]` - Save context for handoff to another agent or session

See all commands: `.claude/commands/`

## Glove80-Viz Skills (Auto-Activate)

These skills auto-activate based on context - you don't need to invoke them manually:

| Skill                            | When It Activates                  | What It Does                                                                               |
| -------------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------ |
| `glove80-viz:monitoring-ci-after-push` | **MANDATORY after every `git push`** | Monitors CI until complete, fixes failures immediately |
| `glove80-viz:pr-shepherd`        | After PR creation or on-demand     | Monitors PR through merge: CI/CD, reviews, auto-fixes, thread resolution                   |
| `glove80-viz:handling-pr-comments` | When addressing PR review feedback | Ensures systematic responses to each comment thread with proper attribution and resolution |
| `glove80-viz:maintaining-service-registry` | When modifying functions in `src/` | Ensures Google-style docstrings and registry updates |
| `glove80-viz:maintaining-mock-registry` | When modifying fixtures in `tests/conftest.py` | Ensures fixture documentation and registry updates |
| `glove80-viz:registry-verification` | Before completing any task | Validates registries are current and error-free |

**CRITICAL**: After any `git push`, you MUST use `monitoring-ci-after-push` to wait for CI and fix any failures before continuing.

Skills are defined in `.claude/plugins/glove80-viz/skills/`.

## Service & Mock Registries

This project maintains auto-generated registries of all functions and mocks:

| File | Contents |
|------|----------|
| `service-registry.toon` | All functions, classes, and services in `src/` |
| `mock-registry.toon` | All fixtures from `tests/conftest.py` |

### Registry Requirements

- All functions must have **Google-style docstrings** with Args, Returns, Raises sections
- All fixtures must have docstrings describing their purpose
- CI fails if registries are out of date or have docstring errors

### Registry Commands

```bash
# Validate docstrings (errors fail, warnings OK)
python scripts/generate_registries.py --check

# Regenerate registries
python scripts/generate_registries.py

# Verbose output
python scripts/generate_registries.py --verbose
```

### Before Completing Tasks

Add to your validation sequence:

```bash
make lint && make typecheck && make test && python scripts/generate_registries.py --check
```

## Worktree Development

### Session Start Protocol

At every session start and after compaction, detect worktree context:

```bash
# Check if in worktree
if [ -n "$WORKTREE_ID" ]; then
  echo "Worktree: $WORKTREE_ID"
else
  echo "Main repository"
fi

# Show active worktrees
git worktree list 2>/dev/null | head -5
```

### Cross-Branch Reference

View code from other branches without switching:

```bash
# View file from main
git show main:path/to/file.py

# Diff current vs main
git diff main -- path/to/file.py
```

### Multi-Agent Handoff

When passing work to another agent:

1. Save context with `/project:save-session`
2. Note the worktree and branch
3. List remaining tasks explicitly

### Worktree Guide

For comprehensive worktree patterns, load `.claude/guides/worktree-development.md` when needed. Covers:

- When to use worktrees
- Multi-agent coordination
- Troubleshooting common issues

## Detailed Guides (Load When Needed)

These guides contain detailed patterns - load them with `@` when working in their area:

| Guide | When to Load |
|-------|--------------|
| `.claude/guides/git-workflow.md` | PRs, commits, branch management |
| `.claude/guides/todo-management.md` | Complex multi-step tasks |
| `.claude/guides/session-management.md` | Saving/loading conversation context |
| `.claude/guides/worktree-development.md` | Parallel development, multi-agent work |

## Checklists

- **Task Completion**: `.claude/task-completion-checklist.md` - Completion requirements
- **Complex Tasks**: `.claude/project-checklist.md` - Full development checklist
- **Quick Tasks**: `.claude/checklists/quick-task-checklist.md` - Streamlined flow

## Documentation Structure

```text
docs/
└── {git-branch-name}/           # e.g., feature-layer-filtering
    ├── specs/
    │   └── FEATURE_SPEC.md      # TDD specifications
    ├── plans/
    │   └── IMPLEMENTATION_PLAN.md
    ├── testing/
    │   └── TESTING_STRATEGY.md
    └── reviews/
        ├── REVIEW-PLANNING-01-INITIAL-{timestamp}.md
        └── REVIEW-PLANNING-02-APPROVED-{timestamp}.md
```

## TDD Workflow (Mandatory)

For every feature:

1. **RED**: Write failing test first
2. **GREEN**: Implement minimal code to pass
3. **REFACTOR**: Improve code while tests stay green
4. **REPEAT**: Next feature cycle

## Extended Thinking

For complex tasks use: `think`, `think hard`, `think harder`, or `ultrathink`

## Important Reminders

- **TDD is mandatory**: Write tests first, then implementation
- **Ask when unclear**: Better to clarify than assume
- Track todos with TodoRead/TodoWrite for multi-step tasks
- Check branch before git operations: `git branch --show-current`
- Include `Co-Authored-By: Claude (AI Assistant)` in commits

# important-instruction-reminders

Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.

## Quick Reference

```bash
# Full validation (run before marking complete)
make lint && make typecheck && make test

# Quick test run
make test

# Format code
make format

# Run the tool
.venv/bin/glove80-viz input.keymap -o output.pdf
```
