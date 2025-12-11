---
description: Create a new worktree for parallel development
---

# Create Worktree

Create a new git worktree for parallel development work.

## Usage

```
/project:worktree-create agent-2 feature/new-feature
```

## Arguments

- `name` - Identifier for the worktree (e.g., `agent-2`, `hotfix`, `experiment`)
- `branch` - Branch name to check out in the worktree

## Steps

1. **Validate not already in a worktree**:

   ```bash
   if [ -n "$WORKTREE_ID" ]; then
     echo "You're already in worktree: $WORKTREE_ID"
     echo "Create new worktrees from the main repository."
     exit 1
   fi
   ```

2. **Create worktree**:

   ```bash
   # Derive path relative to repo location
   REPO_DIR="$(git rev-parse --show-toplevel)"
   REPO_NAME="$(basename "$REPO_DIR")"
   WORKTREE_DIR="${WORKTREES_DIR:-$(dirname "$REPO_DIR")/${REPO_NAME}-worktrees}/$NAME"
   git worktree add "$WORKTREE_DIR" -b "$BRANCH" 2>/dev/null || \
   git worktree add "$WORKTREE_DIR" "$BRANCH"
   ```

3. **Report next steps**:
   - Worktree location
   - How to start Claude in new worktree:

     ```bash
     cd $WORKTREE_DIR  # Path shown in setup output
     claude
     ```

4. **Offer to create handoff** for the new agent

## Example Output

```
Worktree created successfully!

Location: ../<repo-name>-worktrees/agent-2
Branch: feature/new-feature

To start working in this worktree:
  cd ../<repo-name>-worktrees/agent-2
  claude

Would you like me to create a handoff document for the new agent?
```

## Notes

- **New branches always start from `main`** - This ensures PRs have clean diffs without unrelated changes
- Worktrees share the same Git repository but have separate working directories
- Always create worktrees from the main repository, not from another worktree
- To base a branch on something other than main, set `BASE_BRANCH=other-branch` before running
