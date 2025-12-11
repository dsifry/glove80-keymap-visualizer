# Create Pull Request

Create a comprehensive, well-documented pull request following project standards.

## Usage

```
/project:create-pr <feature-branch-name>
```

## Steps

### 1. Pre-PR Checklist

#### Track Modified Files

```bash
# Get list of all modified files
git diff --name-only origin/main...HEAD

# Get Python files only
MODIFIED_FILES=$(git diff --name-only origin/main...HEAD | grep -E '\.py$')
echo "Modified files to validate: $MODIFIED_FILES"
```

#### Run Targeted Validation

- [ ] Type check: `make typecheck`
- [ ] Lint check: `make lint`
- [ ] Format check: `make format`
- [ ] Run tests: `make test`
- [ ] Test coverage: `make test-cov`
- [ ] Review your own code thoroughly first

### 2. PR Title Standards

Use conventional commit format:

- `feat: add support for custom color schemes`
- `fix: resolve parsing error for hold-tap behaviors`
- `refactor: optimize SVG generation pipeline`
- `docs: update CLI usage documentation`
- `test: add comprehensive coverage for layer extraction`

### 3. PR Description Template

```markdown
## Summary

Brief description of what this PR accomplishes and why it's needed.

## Changes Made

- [ ] Added/modified specific components or features
- [ ] Updated dependencies (include version details)
- [ ] Added/updated tests with coverage details
- [ ] Updated documentation

## Testing Done

- [ ] Unit tests: [X passing, Y total]
- [ ] Integration tests: [specific scenarios tested]
- [ ] Manual testing: [keymap files tested]

## CLI Changes

- [ ] No CLI changes
- [ ] New options added: [describe]
- [ ] Existing options modified: [describe]

## Performance Impact

- [ ] No performance impact expected
- [ ] Performance improvements: [describe]
- [ ] Potential performance concerns: [describe and mitigation]

## Breaking Changes

- [ ] No breaking changes
- [ ] Breaking changes: [list and migration path]

## Related Issues

Closes #[issue-number]
Related to #[issue-number]

## Screenshots/Demo

[If visual changes, include before/after screenshots or output examples]
```

### 4. Code Review Preparation

- Self-review all changes line by line
- Add inline comments explaining complex logic
- Ensure commit messages are descriptive
- Remove any debug code, print statements, or TODOs
- Verify all new code follows existing patterns

### 5. Create the PR

```bash
# Push branch
git push origin <branch-name>

# Create PR using gh CLI
gh pr create --title "feat: clear description" --body "$(cat <<'EOF'
## Summary
<1-3 bullet points>

## Test plan
[Bulleted markdown checklist of TODOs for testing the pull request...]

Co-Authored-By: Claude (AI Assistant)
EOF
)"
```

- Assign appropriate reviewers
- Add relevant labels (feature, bug, documentation, etc.)
- Link to related issues
