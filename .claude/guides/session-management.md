# Session Management Guide

This guide explains how to use the session management system to preserve conversation context across Claude Code sessions.

## Overview

The session management system allows you to:

- Save your current conversation context with important decisions, code changes, and next steps
- Load previous sessions to continue where you left off
- Search and browse through past sessions
- Organize sessions with tags, branches, and custom names

## Quick Start

### Save Current Session

```bash
/project:save-session "Implementing layer filtering"
```

### Load Previous Session

```bash
/project:load-session filter
```

### List Recent Sessions

```bash
/project:list-sessions --recent 5
```

## Session Structure

Sessions are stored in `.claude/sessions/` with metadata and content:

```yaml
---
id: "2024-01-03-feature-layer-filtering"
name: "Layer filtering implementation"
date: "2024-01-03T10:30:00Z"
branch: "feature/layer-filtering"
tags: ["feature", "cli", "filtering"]
summary: "Implemented layer filtering CLI option"
related_prs: [12, 13]
---
# Session Content
[Conversation context, decisions, code changes, etc.]
```

## Naming Conventions

### Automatic ID Generation

Format: `YYYY-MM-DD-branch-name[-custom-name]`

Examples:

- `2024-01-03-main` - Simple session on main branch
- `2024-01-03-feature-colors` - Feature branch session
- `2024-01-03-feature-colors-svg-fixes` - With custom name

### Best Practices for Names

- Use descriptive names that explain the work
- Include key component names (parser, cli, pdf)
- Keep names concise but meaningful

## Search and Filter

### Search by Content

```bash
/project:list-sessions --search "SVG generation"
/project:list-sessions --search "parse_keymap()"
```

### Filter by Branch

```bash
/project:list-sessions --branch feature/colors
/project:list-sessions --branch main --recent 10
```

### Filter by Date

```bash
/project:list-sessions --date today
/project:list-sessions --date 2024-01-03
/project:list-sessions --date this-week
```

### Filter by Tags

```bash
/project:list-sessions --tag bugfix
/project:list-sessions --tag parser --tag urgent
```

## Session Workflow

### 1. Starting Work

```bash
# Check for previous related sessions
/project:list-sessions --branch current

# Load if continuing previous work
/project:load-session previous-session-id
```

### 2. During Work

```bash
# Save at natural breakpoints
/project:save-session "Completed SVG caching"
```

### 3. Ending Work

```bash
# Save comprehensive session
/project:save-session "Parser refactor - ready for review"

# The session captures:
# - All modified files
# - Key decisions made
# - Code snippets discussed
# - Open todos
# - Next steps
```

### 4. Resuming Work

```bash
# Next day/session
/project:load-session yesterday

# Shows:
# - What you were working on
# - Current vs session branch
# - Files modified
# - Next steps to continue
```

## Session Templates

Different templates for different work types:

- **default-template.md** - General development work
- **bug-fix-template.md** - Bug investigation and fixes
- **feature-template.md** - Feature implementation

## Integration with Git Workflow

### Pre-Commit Hook

Consider saving session before major commits:

```bash
/project:save-session "Pre-commit: <commit-message>"
```

### Branch Switching

Save session before switching branches:

```bash
/project:save-session "Switching to work on hotfix"
git checkout main
```

### PR Creation

Sessions automatically link to PRs when created:

```bash
/project:create-pr
# Session will include PR number in metadata
```

## Tips and Tricks

### 1. Consistent Tagging

Use consistent tags for easy filtering:

- `#bugfix` - Bug fixes
- `#feature` - New features
- `#refactor` - Code refactoring
- `#urgent` - High priority work
- `#research` - Investigation/exploration

### 2. Session Chains

For multi-day features, create linked sessions:

- Day 1: `color-scheme-setup`
- Day 2: `color-scheme-implementation`
- Day 3: `color-scheme-testing`

### 3. Quick Context Switch

When interrupted:

```bash
/project:save-session "WIP: Debugging PDF issue"
# Work on urgent task
/project:load-session WIP
```

## Session Management Commands Reference

- **save-session** - Save current context
- **load-session** - Load previous session
- **list-sessions** - Browse and search sessions
- **manage-sessions** - Archive, delete, merge sessions

## Best Practices Summary

1. **Save Often**: At natural stopping points
2. **Name Clearly**: Future you will thank you
3. **Tag Consistently**: Makes searching easier
4. **Link Related Work**: Connect multi-session features
5. **Archive Regularly**: Keep active list manageable
6. **Review Weekly**: Learn from past sessions

---

The session management system helps maintain continuity across your Claude Code conversations, making it easier to work on complex, long-running projects without losing context.
