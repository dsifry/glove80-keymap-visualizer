# Start Task

Determine task complexity and use appropriate workflow for efficient development.

## Usage

```
/project:start-task <task-description>
```

## Steps

### 0. Pre-Task Checklist

Before starting any new task:

- [ ] Check if there are active PRs with pending comments
- [ ] Ask: "Before we start the new task, should we check if there are any PR comments to address?"
- [ ] If yes, run: `gh pr list --author @me --state open`

### 1. Task Assessment

**Use extended thinking** to analyze the task complexity before asking the user.

Consider:

- Number of files likely to be modified
- Whether new dependencies are needed
- Impact on existing functionality
- Testing requirements
- Integration points with external tools (keymap-drawer, CairoSVG)

Then ask the user to confirm your assessment:

> **Proposed complexity**: [Quick / Complex] - Does this match your expectation?
>
> Based on my analysis, this task appears to be a [quick task that can be completed in < 2 hours / complex task requiring > 2 hours] because [brief reasoning].

Use this prompt template:

**Quick Task (< 2 hours, use streamlined flow):**

- Bug fixes
- Small feature tweaks
- Minor text/output changes
- Simple configuration updates
- Adding basic validation
- Fixing linting/test issues

**Complex Task (> 2 hours, use full checklist):**

- New pipeline stages
- New CLI commands/options
- Complex parsing logic changes
- Multi-file refactoring
- Performance optimizations
- New output formats

### 2. Quick Task Flow

If user confirms it's a quick task:

#### Essential Steps

- [ ] Read relevant docs if unfamiliar with area
- [ ] Check existing patterns for similar functionality
- [ ] Make the change following existing patterns
- [ ] Write/update tests if logic changes
- [ ] Run `make lint && make typecheck && make test`
- [ ] Create simple PR with clear description
- [ ] Address review feedback

### 3. Complex Task Flow

If it's a complex task:

- Use the full `.claude/project-checklist.md`
- Consider breaking into smaller tasks
- Use extended thinking for planning
- Create detailed implementation plan
- Create spec in `docs/{branch-name}/specs/` (use hyphens: `feature/my-feature` → `docs/feature-my-feature/specs/`)

### 4. Task Escalation

If a "quick task" becomes complex during implementation:

- Stop and reassess
- Switch to full checklist workflow
- Inform user of complexity change
- Consider breaking into multiple PRs

## Questions to Ask User

**Initial Assessment:**
"Is this a quick task (< 2 hours) or a complex task that requires the full development checklist?

Quick tasks include: bug fixes, small feature changes, simple configuration updates
Complex tasks include: new features, new CLI options, parsing logic changes, multi-file refactoring"

**If Uncertain:**
"This task involves [X]. This suggests it might be more complex than initially thought. Should we switch to the full checklist workflow?"
