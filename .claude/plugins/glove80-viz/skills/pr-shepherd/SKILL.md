# pr-shepherd

Use when a PR has been created and needs to be monitored through to merge - handles CI failures, review comments, and thread resolution automatically until all checks pass and all threads are resolved.

**IMPORTANT**: This skill is designed for the **agent working in a worktree**, NOT the orchestrator. The agent handles its own PR monitoring so the orchestrator remains free for other work.

## When to Activate

Activate this skill when ANY of these conditions are true:

- Agent just created a PR with `gh pr create`
- User asks to "shepherd", "monitor", or "see through" a PR
- User invokes `/project:pr-shepherd <pr-number>`
- User asks to "watch this PR" or "handle this PR until it's merged"
- Orchestrator spawned you with instructions to shepherd a PR

## Announce at Start

"I'm using the pr-shepherd skill to monitor this PR through to merge. I'll watch CI/CD, handle review comments, and fix issues as they arise."

## For Orchestrators: Spawning Agents with PR Shepherding

When spawning an agent to work in a worktree, include PR shepherding in the task prompt:

```text
Work in worktree on branch feature/xyz.

Task: [describe the implementation task]

After creating the PR:
1. Use the pr-shepherd skill to monitor it through to merge
2. Handle CI failures and review comments autonomously
3. Only escalate to orchestrator for complex issues requiring user input
4. Report back when PR is ready to merge or if blocked

Run in background so I can continue other work.
```

**Key principle**: The agent owns its PR lifecycle. The orchestrator spawns and forgets, checking back via `AgentOutputTool` when needed.

## State Machine

The agent operates in one of these states:

```text
MONITORING → FIXING → MONITORING → WAITING_FOR_USER → FIXING → MONITORING → DONE
```

| State              | What Happens                                | Exit When                                      |
| ------------------ | ------------------------------------------- | ---------------------------------------------- |
| `MONITORING`       | Poll CI and reviews every 60s in background | CI fails, new comments, all done, or need help |
| `FIXING`           | Fix issues using TDD, run local validation  | Local validation passes OR need user guidance  |
| `HANDLING_REVIEWS` | Invoke `handling-pr-comments` skill         | Comments handled OR need user input            |
| `WAITING_FOR_USER` | Present options, wait for user decision     | User responds                                  |
| `DONE`             | All CI green + all threads resolved         | Exit successfully                              |

## Phase 1: Initialize

```bash
# Get PR info
PR_NUMBER=$(gh pr view --json number -q .number 2>/dev/null)
OWNER=$(gh repo view --json owner -q .owner.login)
REPO=$(gh repo view --json name -q .name)

# If no PR on current branch, check if number was provided
if [ -z "$PR_NUMBER" ]; then
  echo "No PR found for current branch. Provide PR number."
  exit 1
fi

echo "Shepherding PR #$PR_NUMBER"
```

## Phase 2: Monitoring Loop (Background)

Run these checks every 60 seconds:

### Check CI Status

```bash
# Get all check runs
gh pr checks $PR_NUMBER --json name,state,conclusion --jq '.[] | "\(.name): \(.state) \(.conclusion)"'

# Check for failures
FAILED_CHECKS=$(gh pr checks $PR_NUMBER --json name,conclusion --jq '[.[] | select(.conclusion == "FAILURE")] | length')
```

### Check Review Comments

```bash
# Get comment count and latest
COMMENTS=$(gh api "repos/$OWNER/$REPO/pulls/$PR_NUMBER/comments" --paginate)
COMMENT_COUNT=$(echo "$COMMENTS" | jq 'length')

# Get unresolved thread count
UNRESOLVED=$(gh api graphql -f query='
  query($owner: String!, $repo: String!, $pr: Int!) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $pr) {
        reviewThreads(first: 100) {
          nodes {
            isResolved
          }
        }
      }
    }
  }
' -f owner="$OWNER" -f repo="$REPO" -F pr="$PR_NUMBER" \
  --jq '[.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false)] | length')
```

### Evaluate State Transitions

```text
if ALL_CHECKS_PASS and UNRESOLVED == 0:
  → DONE

if FAILED_CHECKS > 0:
  if is_simple_failure(failure):
    → FIXING
  else:
    → WAITING_FOR_USER (present options)

if NEW_COMMENTS:
  → HANDLING_REVIEWS
```

## Phase 3: Fixing Issues

### Simple Issues (Auto-fix)

These can be fixed without user approval:

- Lint failures → run `make lint`
- Format failures → run `make format`
- Type errors → fix the types
- Test failures in code YOU wrote → fix using TDD

### Complex Issues (Need Approval)

These require user input BEFORE fixing:

- Test failures in code you didn't write
- Infrastructure/config failures
- Ambiguous errors
- Anything you're uncertain about

### FIXING State Rules

1. **Use TDD** - Write failing test, implement fix, refactor
2. **Stay until green** - Don't leave FIXING until `make lint && make typecheck && make test` pass
3. **Only push when verified** - Never push code that fails local validation
4. **Return to MONITORING after push** - Let CI run, continue monitoring

```bash
# After fixing, always validate locally
make lint && make typecheck && make test

# Only push if all pass
git add -A && git commit -m "fix: <description>" && git push
```

## Phase 4: Handling Reviews

When new review comments are detected:

1. Invoke the `glove80-viz:handling-pr-comments` skill
2. That skill handles categorization, fixes, responses, and thread resolution
3. **ALL threads must be resolved** before returning to MONITORING
4. If a thread cannot be resolved (needs clarification from reviewer), query the comment author asking for follow-up
5. Return to MONITORING only when all threads are resolved

## Phase 5: Waiting for User

When user input is needed, ALWAYS:

1. **Present the situation clearly**
2. **Offer 2-4 options with pros/cons**
3. **State your recommendation**
4. **Allow user to choose OR provide their own approach**

### Template

```text
[Describe what happened]

**Options:**

1. **[Option name]** (Recommended)
   - [What it involves]
   - Pros: [benefits]
   - Cons: [drawbacks]

2. **[Option name]**
   - [What it involves]
   - Pros: [benefits]
   - Cons: [drawbacks]

3. **[Option name]**
   - [What it involves]
   - Pros: [benefits]
   - Cons: [drawbacks]

Which approach would you like? (Or describe a different approach)
```

## Exit Conditions

### Success (DONE)

Exit successfully when ALL are true:

- All CI checks passing
- All review threads resolved
- No pending questions

Report:

```text
**PR #[number] Ready to Merge**

- CI: All checks passing
- Reviews: All threads resolved
- Commits: [N] total ([M] fix commits)

The PR is ready for final approval and merge.
```

## Verification Checklist

Before exiting DONE state:

- [ ] All CI checks are green
- [ ] All review threads are resolved
- [ ] No pending user questions
- [ ] Final status reported to user

## Common Mistakes

**Pushing without local validation**

- NEVER push code that hasn't passed `make lint && make typecheck && make test`

**Auto-fixing complex issues**

- If uncertain, ASK. Always go through WAITING_FOR_USER for complex issues.

**Forgetting to invoke handling-pr-comments**

- When new comments arrive, delegate to that skill. Don't handle comments inline.

**Not presenting options to user**

- Always give 2-4 options with pros/cons. Never just ask "what should I do?"

**Leaving FIXING state early**

- Stay in FIXING until local validation passes. Don't assume a fix worked.
