---
model: claude-haiku-4-5-20251001
---

# Load Session

Load a previously saved conversation session to continue where you left off.

## Usage

```bash
/project:load-session [identifier]
```

- `identifier`: Can be:
  - Session ID (e.g., `2024-01-03-feature-parser`)
  - Partial name match (e.g., `parser`)
  - Date (e.g., `2024-01-03`)
  - Branch name (e.g., `feature/parser`)
  - Tag (e.g., `#bugfix`)

If multiple sessions match, you'll be prompted to select one.

## What It Does

1. **Searches** for matching sessions based on your identifier
2. **Displays** matching sessions with summaries
3. **Loads** the selected session context
4. **Shows**:
   - Session overview and summary
   - Current branch vs. session branch
   - Open todos and next steps
   - Recent context and decisions
   - File modifications from that session

## Search Methods

### By ID (Exact Match)

```bash
/project:load-session 2024-01-03-feature-parser
```

### By Name (Partial Match)

```bash
/project:load-session "PDF generation"
```

### By Date (All from Date)

```bash
/project:load-session 2024-01-03
```

Shows all sessions from January 3, 2024.

### By Branch

```bash
/project:load-session feature/parser
```

Shows all sessions from the specified branch.

### By Tag

```bash
/project:load-session #bugfix
```

Shows all sessions tagged with "bugfix".

### Interactive Mode

```bash
/project:load-session
```

Without identifier, shows recent sessions for selection.

## Session Display Format

When loading a session, you'll see:

```text
SESSION: Layer filtering complete
Date: 2024-01-03 10:30 AM
Branch: feature/layer-filtering (current: main)
Tags: feature, cli, filtering
Summary: Implemented layer filtering CLI option

Branch Mismatch: Session was on 'feature/layer-filtering', currently on 'main'

Modified Files (5):
  - src/glove80_visualizer/cli.py
  - src/glove80_visualizer/pdf_generator.py
  - tests/test_cli.py
  - tests/test_pdf_generator.py
  - docs/usage.md

Completed Tasks:
  - Add --layers CLI option
  - Implement layer filtering logic
  - Update PDF generation

Next Steps:
  - Add tests for edge cases
  - Update documentation
  - Create PR

Related:
  - PR #12: Add layer filtering option
  - Commits: abc123, def456, ghi789
```

## Options

### Load and Switch Branch

If on a different branch, you'll be asked:

```text
Session was on branch 'feature/layer-filtering' but you're on 'main'.
Would you like to:
1. Switch to feature/layer-filtering
2. Stay on main
3. View diff between branches
```

### Recent Context

Automatically shows:

- Last 5 commits from the session
- Key code blocks discussed
- Important decisions made

## Examples

### Load Most Recent

```bash
/project:load-session
```

Shows last 5 sessions for interactive selection.

### Load by Partial Name

```bash
/project:load-session parser
```

Finds all sessions with "parser" in the name.

### Load Today's Sessions

```bash
/project:load-session today
```

Special keyword to show all sessions from today.

## Best Practices

1. **Check branch alignment**: Ensure you're on the right branch
2. **Review next steps**: Pick up where you left off
3. **Check related PRs**: See if they've been merged or need updates
4. **Verify file states**: Ensure files still exist and match expectations

## Related Commands

- `/project:save-session` - Save current context
- `/project:list-sessions` - Browse all sessions
- `/project:manage-sessions` - Delete or archive sessions
