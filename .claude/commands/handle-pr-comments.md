---
description: Handle review comments on pull requests with appropriate responses and resolutions
---

# Handle PR Comments

Handle review comments on pull requests with appropriate responses and resolutions.

## Usage

```bash
/project:handle-pr-comments <pr-number>
```

## Overview

This command helps systematically address PR review comments from automated tools (like CodeRabbit) and human reviewers. It ensures consistent, professional responses.

## Workflow

### 1. Check for New Comments

```bash
# Set PR number
PR_NUMBER=<pr-number>
OWNER=$(gh repo view --json owner -q .owner.login)
REPO_NAME=$(gh repo view --json name -q .name)

# List all review comments
gh api "repos/$OWNER/$REPO_NAME/pulls/$PR_NUMBER/comments" --paginate \
  -q '.[] | "ID: \(.id) - [\(.path):\(.line // .original_line // "?")]", "  @\(.user.login): \(.body[0:100])...", "---"'
```

### 2. Determine Current User and PR Author

```bash
# Get the current GitHub user
CURRENT_USER=$(gh api user -q '.login')
echo "Current user: @$CURRENT_USER"

# Get PR author
PR_AUTHOR=$(gh api "repos/$OWNER/$REPO_NAME/pulls/$PR_NUMBER" -q '.user.login')
echo "PR authored by: @$PR_AUTHOR"
```

### 3. Critical Workflow Order

1. **BEFORE making fixes**: Get initial comment IDs and thread information
2. **Make your fixes**: Code changes, commit, push
3. **REFRESH comment IDs**: Re-fetch CURRENT comments (IDs may change after commit!)
4. **Post responses**: Use CURRENT comment IDs to post replies
5. **WAIT for reviewer**: Do NOT resolve threads immediately
6. **Resolve only when**: Reviewer approves OR you're declining the suggestion

### 4. Posting Inline Replies

```bash
# Get CURRENT comment IDs after your fixes
gh api "repos/$OWNER/$REPO_NAME/pulls/$PR_NUMBER/comments" --paginate \
  -q '.[] | "\(.id) - \(.path):\(.line)"'

# Post reply to CURRENT comment ID
COMMENT_ID=<fresh-comment-id>
gh api "/repos/$OWNER/$REPO_NAME/pulls/$PR_NUMBER/comments/$COMMENT_ID/replies" \
  -X POST \
  -f body="Fixed in commit $(git rev-parse --short HEAD).

*(Response by Claude on behalf of @$CURRENT_USER)*"
```

## Response Templates

### Simple Fixes (typos, formatting)

```markdown
Fixed in commit <hash>.

*(Response by Claude on behalf of @username)*
```

### Substantive Changes

```markdown
Fixed in commit <hash> - Added proper type hints and updated the docstring to clarify the return type. This ensures better IDE support and documentation.

*(Response by Claude on behalf of @username)*
```

### Rejecting Suggestions

```markdown
Not implementing this suggestion because the current approach provides better performance for large keymaps. The alternative would require O(n^2) iteration instead of the current O(n) approach.

*(Response by Claude on behalf of @username)*
```

### Need Clarification

```markdown
I'm not sure I understand this suggestion. Could you clarify what you mean by [specific part]? Are you suggesting [interpretation A] or [interpretation B]?

*(Response by Claude on behalf of @username)*
```

### Partial Implementation

```markdown
Partially implemented in commit <hash> - I've added the type safety checks as suggested, but held off on the refactoring portion as it would affect multiple files. Should we tackle that in a separate PR?

*(Response by Claude on behalf of @username)*
```

## Best Practices

1. **Be Specific**: Reference exact commits, files, and line numbers
2. **Be Professional**: Thank reviewers for catching important issues
3. **Be Transparent**: Always include the Claude attribution
4. **Be Thorough**: Address all parts of multi-part suggestions
5. **Be Humble**: Acknowledge when you need help or clarification
6. **Be Conservative**: Make minimal changes to address the issue

## Verify All Comments Addressed

```bash
# List all original comments (not replies)
gh api "repos/$OWNER/$REPO_NAME/pulls/$PR_NUMBER/comments" --paginate \
  -q '.[] | select(.in_reply_to_id == null) | "ID: \(.id) - \(.path):\(.line) - @\(.user.login)"'

# List your responses
CURRENT_USER=$(gh api user -q '.login')
gh api "repos/$OWNER/$REPO_NAME/pulls/$PR_NUMBER/comments" --paginate \
  -q ".[] | select(.user.login == \"$CURRENT_USER\") | select(.in_reply_to_id) | \"Replied to ID \(.in_reply_to_id)\""
```

## When to Use This Command

- After pushing commits to an existing PR
- Before switching away from a PR branch
- When specifically asked to check PR comments
- After completing significant work on a PR

**Note**: Only handle comments on PRs you authored unless explicitly asked otherwise.
