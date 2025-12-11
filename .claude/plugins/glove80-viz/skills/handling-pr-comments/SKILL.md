# handling-pr-comments

Use when addressing PR review feedback, after receiving review comments from CodeRabbit or human reviewers - ensures systematic responses to each comment thread with proper attribution and thread resolution.

## When to Activate

Activate this skill when ANY of these conditions are true:

- User asks to "address PR comments" or "handle review feedback"
- User mentions CodeRabbit or reviewer comments
- User is working on fixes requested in a PR review
- User asks to "check PR comments" or "respond to reviewers"
- After making fixes to address review feedback

## CRITICAL: The Complete Workflow

**Most developers forget steps 4-6. This skill ensures they happen.**

### Phase 1: Discover Comments

```bash
# Get PR number from current branch
PR_NUMBER=$(gh pr view --json number -q .number 2>/dev/null)
OWNER=$(gh repo view --json owner -q .owner.login)
REPO_NAME=$(gh repo view --json name -q .name)

# List all review comments
gh api "repos/$OWNER/$REPO_NAME/pulls/$PR_NUMBER/comments" --paginate \
  -q '.[] | "ID: \(.id) | \(.path):\(.line // .original_line) | @\(.user.login)"'
```

### Phase 2: Triage Comments

Categorize each comment as:

1. **Bug/Issue** - Must fix (high priority)
2. **Enhancement** - Should fix (medium priority)
3. **Nitpick** - Nice to fix (low priority)
4. **Question** - Needs clarification
5. **Intentional** - Decline with explanation

### Phase 3: Make Fixes

Fix the actual code issues. Commit and push.

### Phase 4: RESPOND TO EACH THREAD (Often Forgotten!)

**After pushing fixes, respond to EACH comment thread individually:**

```bash
CURRENT_USER=$(gh api user -q '.login')
COMMENT_ID=<id-from-step-1>

gh api "/repos/$OWNER/$REPO_NAME/pulls/$PR_NUMBER/comments/$COMMENT_ID/replies" \
  -X POST \
  -f body="Fixed in commit $(git rev-parse --short HEAD).

*(Response by Claude on behalf of @$CURRENT_USER)*"
```

### Phase 5: Resolve ALL Threads

**Every thread must be resolved after responding.** Use GraphQL to resolve:

```bash
# Get thread ID for the comment
THREAD_ID="PRRT_kwDOK-xA485..."  # From GraphQL query

gh api graphql -f query='mutation {
  resolveReviewThread(input: {threadId: "'"$THREAD_ID"'"}) {
    thread { id isResolved }
  }
}'
```

### Phase 6: Handle Threads That Can't Be Resolved

If a thread requires clarification or you can't address it:

1. **Query the comment author** asking for specific follow-up
2. **Do NOT leave unresolved** - either resolve after responding, or ask for clarification
3. If waiting for author response, mark as needing user input (escalate to WAITING_FOR_USER state)

## Response Templates

### For Fixes Made

```text
Fixed in commit <hash>.

*(Response by Claude on behalf of @username)*
```

### For Acknowledged Nitpicks

```text
Acknowledged - this is a valid suggestion. Deferring to a future cleanup PR to keep this PR focused.

*(Response by Claude on behalf of @username)*
```

### For Intentional Decisions

```text
This is intentional because [reason]. The [thing] is designed to [explanation].

*(Response by Claude on behalf of @username)*
```

## Verification Checklist

Before declaring PR comments handled:

- [ ] All comments have been reviewed and categorized
- [ ] Code fixes have been made and pushed
- [ ] Each comment thread has a response posted
- [ ] **ALL threads have been resolved** (no unresolved threads remaining)
- [ ] All responses include proper attribution
- [ ] Any threads needing clarification have been escalated with a query to the author

## Reference

For the complete detailed workflow with all edge cases, rate limit handling, and cross-platform compatibility, see:
`.claude/commands/handle-pr-comments.md`
