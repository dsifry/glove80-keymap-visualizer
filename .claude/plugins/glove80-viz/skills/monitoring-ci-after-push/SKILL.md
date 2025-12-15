# monitoring-ci-after-push

Use IMMEDIATELY after any `git push` to a remote branch - monitors CI/CD until all checks complete and fixes any failures before continuing.

**CRITICAL**: This skill is MANDATORY after every `git push`. Do not continue to other work until CI is confirmed passing.

## When to Activate

Activate this skill AUTOMATICALLY when ANY of these occur:

- Just ran `git push` (with or without flags)
- Just ran `git push -u origin <branch>`
- Just pushed a fix commit to a PR branch
- Just force-pushed to a branch

## Announce at Start

"I'm monitoring CI after the push. I'll wait for all checks to complete and fix any failures."

## The Problem This Solves

Without this skill:
1. Agent pushes code
2. Agent moves on to other tasks
3. CI fails silently in the background
4. User discovers failures later
5. Context is lost, fixing is harder

With this skill:
1. Agent pushes code
2. Agent monitors CI until complete
3. If CI fails, agent fixes immediately (while context is fresh)
4. Only proceeds when CI is green

## Monitoring Protocol

### Step 1: Get Branch/PR Info

```bash
# Get current branch
BRANCH=$(git branch --show-current)

# Check if there's a PR for this branch
PR_NUMBER=$(gh pr view --json number -q .number 2>/dev/null || echo "")
```

### Step 2: Wait for CI to Start

```bash
# Wait up to 30 seconds for CI to start
for i in {1..6}; do
  if gh pr checks $PR_NUMBER 2>/dev/null | grep -q "pending\|pass\|fail"; then
    break
  fi
  sleep 5
done
```

### Step 3: Monitor Until Complete

Poll every 30 seconds until all checks complete:

```bash
gh pr checks $PR_NUMBER
# or for branch without PR:
gh run list --branch $BRANCH --limit 1
```

### Step 4: Evaluate Results

| Result | Action |
|--------|--------|
| All pass | Announce success, continue with task |
| Any fail | Immediately investigate and fix |
| Stuck pending >10min | Report to user, ask how to proceed |

## Fixing CI Failures

When CI fails:

1. **Get failure details**:
   ```bash
   gh run view <run-id> --log-failed
   ```

2. **Categorize the failure**:
   - Lint/format → Auto-fix with `make format && make lint`
   - Type errors → Fix types
   - Test failures → Debug and fix tests
   - Infrastructure → Report to user

3. **Fix locally first**:
   ```bash
   make lint && make typecheck && make test
   ```

4. **Push fix and re-monitor**:
   ```bash
   git add -A && git commit -m "fix: <description>" && git push
   # Then restart this skill's monitoring protocol
   ```

## Timeout Handling

- **Individual check >15 minutes**: Note it but keep waiting
- **Total wait >30 minutes**: Report status to user, ask if should continue waiting
- **CI appears stuck**: Check GitHub Actions status page, report to user

## Integration with Other Skills

This skill runs BEFORE:
- Continuing to next task
- Reporting task completion
- Creating a PR (if pushing to prepare for PR)

This skill runs AFTER:
- Any `git push` command
- `verification-before-completion` (which should trigger a push)

## Example Flow

```text
Agent: [completes code changes]
Agent: [runs make lint && make typecheck && make test - all pass]
Agent: [commits and pushes]
Agent: "I'm monitoring CI after the push. I'll wait for all checks to complete."
Agent: [polls gh pr checks every 30s]
Agent: [after 3 minutes] "CI Status: lint ✓, typecheck ✓, test (3/8 complete)..."
Agent: [after 6 minutes] "All CI checks passed. Continuing with task."
```

## Failure Example

```text
Agent: [pushes code]
Agent: "I'm monitoring CI after the push."
Agent: [after 2 minutes] "CI failure detected in lint job."
Agent: [fetches logs, identifies formatting issue]
Agent: [runs make format, commits fix, pushes]
Agent: "Pushed fix. Restarting CI monitoring."
Agent: [monitors again until all pass]
Agent: "All CI checks now passing."
```

## Verification Checklist

Before moving on from this skill:

- [ ] All CI checks have completed (not pending)
- [ ] All CI checks are passing (green)
- [ ] If fixes were needed, they've been pushed and verified
- [ ] Status has been reported to user

## Common Mistakes

**Moving on while CI is pending**
- NEVER assume CI will pass. Wait for confirmation.

**Not checking for the run to start**
- CI can take 10-30 seconds to begin. Wait for it.

**Fixing without local verification**
- Always run `make lint && make typecheck && make test` before pushing fixes.

**Forgetting to re-monitor after fix**
- After pushing a fix, restart the monitoring protocol from Step 1.
