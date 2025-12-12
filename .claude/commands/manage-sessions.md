---
model: claude-haiku-4-5-20251001
---

# Manage Sessions

Organize, archive, and maintain saved conversation sessions.

## Usage

```bash
/project:manage-sessions <action> [options]
```

## Actions

### Archive Old Sessions

```bash
/project:manage-sessions archive --older-than 30d
/project:manage-sessions archive --older-than 60d
```

Moves old sessions to `.claude/sessions/archive/YYYY/MM/`.

### Delete Sessions

```bash
/project:manage-sessions delete <session-id>
/project:manage-sessions delete --older-than 90d --dry-run
/project:manage-sessions delete --older-than 90d
```

Use `--dry-run` first to preview what will be deleted.

### Clean Up Empty Sessions

```bash
/project:manage-sessions cleanup --remove-empty
```

Removes sessions with no meaningful content.

### Merge Sessions

```bash
/project:manage-sessions merge <session-id-1> <session-id-2>
```

Combines two related sessions into one.

### Export Sessions

```bash
/project:manage-sessions export --format json
/project:manage-sessions export --format markdown --output sessions-backup.md
```

Exports sessions for backup or external use.

### Show Storage Stats

```bash
/project:manage-sessions stats
```

Shows:
- Total sessions
- Sessions by branch
- Sessions by tag
- Storage used
- Oldest/newest sessions

## Archive Structure

```text
.claude/sessions/
├── 2024-01-03-feature-parser.md           # Active
├── 2024-01-02-main-hotfix.md              # Active
└── archive/
    └── 2023/
        └── 12/
            ├── 2023-12-15-feature-cli.md  # Archived
            └── 2023-12-10-bugfix-pdf.md   # Archived
```

## Examples

### Monthly Cleanup

```bash
# Preview what will be archived
/project:manage-sessions archive --older-than 30d --dry-run

# Actually archive
/project:manage-sessions archive --older-than 30d
```

### Find and Remove Duplicates

```bash
/project:manage-sessions cleanup --find-duplicates
/project:manage-sessions delete <duplicate-session-id>
```

### Backup Before Major Work

```bash
/project:manage-sessions export --format json --output backup-$(date +%Y%m%d).json
```

## Best Practices

1. **Archive Monthly**: Keep active list clean
2. **Preview First**: Always use `--dry-run` before delete
3. **Backup Regularly**: Export before cleanup operations
4. **Tag Consistently**: Makes cleanup easier

## Related Commands

- `/project:save-session` - Save current context
- `/project:load-session` - Load a session
- `/project:list-sessions` - Browse sessions
