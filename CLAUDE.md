# CLAUDE.md - Glove80 Keymap Visualizer

## Project Overview
CLI tool that generates PDF visualizations of Glove80 keyboard layers from ZMK `.keymap` files.

## Quick Reference

```bash
# Setup
make install-dev

# Development cycle
make test          # Run tests (TDD - tests first!)
make lint          # Check code quality
make typecheck     # Type checking
make format        # Auto-format code

# Run tool
.venv/bin/glove80-viz <keymap.keymap> -o output.pdf
```

## Architecture (5-stage pipeline)

```
.keymap → Parser → YAML → Extractor → Layers → SVG Generator → PDF Generator → .pdf
              ↓                              ↓                    ↓
        keymap-drawer                  keymap-drawer          CairoSVG + PyPDF2
```

## Development Rules

1. **TDD Required**: Write failing test → implement → refactor. Tests live in `tests/test_*.py`, specs in `docs/SPEC.md`
2. **Type Hints**: All public functions must have type hints. No `Any` without justification.
3. **Error Handling**: Every external call (file I/O, keymap-drawer, CairoSVG) needs explicit error handling with actionable messages.

## Key Files

| File | Purpose |
|------|---------|
| `docs/{branch}/plans/PLAN.md` | Architecture, data flow, implementation phases |
| `docs/{branch}/specs/SPEC.md` | TDD specifications (read before implementing) |
| `docs/{branch}/reviews/` | CTO-level reviews (timestamped) |
| `tests/conftest.py` | Pytest fixtures |
| `tests/fixtures/*.keymap` | Test keymap files |

**Current branch**: `feature-keymap-visualizer-setup` → docs at `docs/feature-keymap-visualizer-setup/`

## Commands

- `/review-this <path>` - CTO-level review of specs/plans/code
