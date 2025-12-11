# Git Workflow Guide

This guide covers Git best practices, branch management, commit conventions, and PR workflows.

## Current Branch Awareness

**CRITICAL**: Always maintain awareness of your current branch to prevent wrong-branch operations.

Before ANY git operation (add, commit, push, checkout), you MUST:

```bash
# 1. Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

# 2. Verify it matches your intention
# If working on a PR, ensure branch name matches the PR

# 3. Check if PR exists for this branch
gh pr list --head "$CURRENT_BRANCH" --state open
```

Common branch confusion scenarios to avoid:

- Pushing to main instead of feature branch
- Creating PR from wrong branch
- Committing fixes to unrelated branch
- Losing track after multiple git operations

## Git Commit Attribution and PR Workflow

### Pre-Commit Verification

Before ANY git operations:

1. **Verify current branch**: `git branch --show-current`
2. **Check for uncommitted changes**: `git status`
3. **Review changes**: `git diff` (unstaged) or `git diff --cached` (staged)
4. **Run validation on modified files**:

   ```bash
   # Run full validation before committing
   make lint && make typecheck && make test
   ```

### Commit Guidelines

When making commits with Claude's assistance:

- **DO**: Include emoji prefix in commit messages for clarity
- **DO**: Use `Co-Authored-By: Claude (AI Assistant)` for attribution
- **DO**: Group related changes into logical commits
- **DON'T**: Create commits without running validation first

### PR Creation Workflow

1. **Verify branch**: `git branch --show-current`
2. **Push branch**: `git push origin <branch-name>`
3. **Create PR with comprehensive description**:
   ```bash
   gh pr create --title "feat: clear description" --body "..."
   ```
4. Include in PR description:
   - Summary with before/after metrics
   - Detailed list of changes
   - Review focus areas
   - Testing confirmation
   - Any remaining work

Example commit message:

```text
feat: add layer visualization enhancements

- Implement smart caching for SVG generation
- Add support for custom color schemes
- Improve error handling for malformed keymaps

Co-Authored-By: Claude (AI Assistant)
```

## PR Comment Monitoring Workflow

Claude will remind you to check for PR comments **only when working on existing PRs** at these key moments:

1. **After completing significant work on an existing PR, before committing**
2. **After pushing updates to an existing PR**
3. **Before switching away from a PR branch**
4. **Before starting new tasks** (if you have open PRs)

### When This Workflow Applies

This workflow **only applies when**:

- A PR has already been created and pushed to GitHub
- You're making additional changes to an existing PR
- You have open PRs that might have received feedback

This workflow **does not apply when**:

- Working on initial feature development before creating a PR
- Making changes on a branch that hasn't been pushed yet
- Working on a branch without an associated PR

## Checking for Comments (Your PRs Only)

```bash
# List YOUR open PRs
gh pr list --author @me --state open

# Quick check for new comments on YOUR PR
gh pr view <pr-number> --json comments,reviews | jq -r '.comments | length'

# View all review comments on YOUR PR
gh api repos/{owner}/{repo}/pulls/<pr-number>/comments
```

## Multi-File Commit Strategy

### Strategy 1: Single Comprehensive Commit

Best for: Related changes across multiple files

```bash
git add .
git commit -m "feat: implement layer visualization enhancements

- Add SVG caching for better performance
- Update PDF generation logic
- Enhance CLI options

Co-Authored-By: Claude (AI Assistant)"
```

### Strategy 2: Logical Commit Grouping

Best for: Large features with distinct components

```bash
# Core functionality
git add src/glove80_visualizer/*.py
git commit -m "feat: add core visualization logic"

# Tests
git add tests/*.py
git commit -m "test: add visualization tests"

# Documentation
git add docs/*.md README.md
git commit -m "docs: update documentation"
```

### Strategy 3: File-by-File Commits

Best for: Unrelated changes or debugging

```bash
git add src/glove80_visualizer/parser.py
git commit -m "fix: resolve null reference in keymap parser"

git add src/glove80_visualizer/cli.py
git commit -m "style: improve CLI output formatting"
```

## Common Git Commands

### Working with Branches

```bash
# Create and switch to new branch
git checkout -b feature/branch-name

# List all branches
git branch -a

# Delete local branch
git branch -d branch-name

# Update branch from main
git checkout main
git pull origin main
git checkout feature/branch-name
git rebase main
```

### Stashing Changes

```bash
# Save current changes
git stash

# List stashes
git stash list

# Apply most recent stash
git stash pop

# Apply specific stash
git stash apply stash@{2}
```

### Undoing Changes

```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Amend last commit
git commit --amend
```

## Best Practices

1. **Commit Frequently**: Make small, logical commits
2. **Write Clear Messages**: Use conventional commit format
3. **Review Before Push**: Always review changes before pushing
4. **Keep Branches Updated**: Regularly sync with main branch
5. **Clean Up**: Delete merged branches locally and remotely

## See Also

- `.claude/commands/handle-pr-comments.md` for PR comment handling
- `.claude/commands/create-pr.md` for PR creation workflow
- `.claude/task-completion-checklist.md` for completion requirements
