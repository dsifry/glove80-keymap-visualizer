---
description: Show current worktree context and all active worktrees
---

# Worktree Status

Report the current worktree environment and list all active worktrees.

## Steps

1. **Detect current context**:

   ```bash
   echo "=== Current Environment ==="
   if [ -n "$WORKTREE_ID" ]; then
     echo "Worktree: $WORKTREE_ID"
   else
     echo "Location: Main repository"
   fi
   echo "Branch: $(git branch --show-current)"
   echo "Directory: $(pwd)"
   ```

2. **List all worktrees**:

   ```bash
   echo ""
   echo "=== All Worktrees ==="
   git worktree list
   ```

3. **Report summary** to user with:
   - Current worktree context (or main repo)
   - Branch name
   - All active worktrees
