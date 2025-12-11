---
model: claude-haiku-4-5-20251001
---

# List Sessions

Browse and search through saved conversation sessions.

## Usage

```bash
/project:list-sessions [options]
```

## Options

### Recent Sessions

```bash
/project:list-sessions --recent 5
/project:list-sessions --recent 10
```

Shows the N most recent sessions.

### Search by Content

```bash
/project:list-sessions --search "PDF generation"
/project:list-sessions --search "parse_keymap"
```

Searches session content and metadata.

### Filter by Branch

```bash
/project:list-sessions --branch feature/parser
/project:list-sessions --branch main
```

Shows sessions from specific branch.

### Filter by Date

```bash
/project:list-sessions --date today
/project:list-sessions --date yesterday
/project:list-sessions --date 2024-01-03
/project:list-sessions --date this-week
/project:list-sessions --date this-month
```

### Filter by Tags

```bash
/project:list-sessions --tag bugfix
/project:list-sessions --tag feature --tag urgent
```

Multiple tags are AND-ed together.

### Show Statistics

```bash
/project:list-sessions --stats
```

Shows session statistics (count by branch, tag, date).

## Output Format

```text
SESSIONS (5 found)

1. [2024-01-03] feature-parser-zmk-support
   Branch: feature/parser
   Tags: #parser #feature
   Summary: Implemented ZMK behavior parsing
   Modified: 8 files

2. [2024-01-02] main-hotfix-pdf-crash
   Branch: main
   Tags: #bugfix #urgent
   Summary: Fixed PDF generation crash on large keymaps
   Modified: 3 files

3. [2024-01-02] feature-colors-implementation
   Branch: feature/colors
   Tags: #feature #ui
   Summary: Added custom color scheme support
   Modified: 12 files
```

## Combined Filters

```bash
/project:list-sessions --branch main --date this-week --tag bugfix
```

Shows bugfix sessions on main from this week.

## Examples

### Daily Review

```bash
/project:list-sessions --date today
```

See what you worked on today.

### Find Old Work

```bash
/project:list-sessions --search "layer extraction"
```

Find sessions related to specific work.

### Weekly Summary

```bash
/project:list-sessions --date this-week --stats
```

Get overview of week's work.

## Related Commands

- `/project:save-session` - Save current context
- `/project:load-session` - Load a session
- `/project:manage-sessions` - Organize sessions
