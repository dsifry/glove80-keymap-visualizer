---
description: View a file from another branch without switching context
---

# Peek Branch

View file contents from another branch without changing your working directory.

## Usage

```bash
/project:peek-branch main src/glove80_visualizer/parser.py
/project:peek-branch feature/other-pr pyproject.toml
```

## Arguments

- `branch` - The branch name to peek into (e.g., `main`, `feature/colors`)
- `file_path` - Path to the file relative to repository root

## Steps

1. **Parse arguments**: Extract branch name and file path from `$ARGUMENTS`

2. **Validate branch exists**:

   ```bash
   git rev-parse --verify "$BRANCH" 2>/dev/null || echo "Branch not found: $BRANCH"
   ```

3. **Show file contents**:

   ```bash
   git show "$BRANCH:$FILE_PATH"
   ```

4. **Optionally show diff** if user wants comparison:

   ```bash
   git diff HEAD.."$BRANCH" -- "$FILE_PATH"
   ```

## Examples

```bash
# View pyproject.toml from main branch
/project:peek-branch main pyproject.toml

# View a module file from another feature branch
/project:peek-branch feature/new-api src/glove80_visualizer/cli.py

# Compare current file with main
# (Ask user if they want this after showing the file)
```

## Notes

- This command does NOT switch branches or modify your working directory
- Useful for referencing code from other PRs or seeing what main has
- Works with any valid git ref (branch, tag, commit hash)
