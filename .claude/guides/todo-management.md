# Todo Management Guide

This guide covers best practices for using TodoWrite and TodoRead tools to track progress on complex tasks.

## Task Management with Todo Tools

**CRITICAL**: Always maintain accurate todo status to ensure task completion and proper tracking.

## When to Use Todo Tools

Use TodoWrite and TodoRead tools to track progress on complex tasks:

### Use todos for:

- Complex multi-step tasks (3+ distinct steps)
- Non-trivial and complex tasks requiring careful planning
- When user explicitly requests todo list usage
- Multiple tasks provided by user (numbered or comma-separated)
- Tasks requiring systematic tracking
- When you need to maintain state across a long conversation

### Skip todos for:

- Single, straightforward tasks
- Trivial tasks where tracking provides no benefit
- Tasks completable in less than 3 trivial steps
- Purely conversational or informational requests

## TodoRead Usage

Check current task list frequently, especially:

- At the beginning of conversations
- Before starting new tasks
- After completing tasks
- When uncertain about next steps
- **Before any context switch or branch change**
- **After every 10-15 messages in long conversations**

## TodoWrite Usage

Update task status in real-time:

- Mark tasks as `in_progress` BEFORE starting work
- Only have ONE task `in_progress` at a time
- Mark as `completed` IMMEDIATELY after finishing
- Use for tasks with 3+ steps or requiring systematic tracking
- **NEVER leave tasks as `in_progress` when switching context**
- **If interrupted, add a note about current progress**

## Todo Management Rules

### 1. No Abandoned Tasks

If you can't complete a task, update it with:

- Current progress
- What remains to be done
- Any blockers encountered

### 2. Context Switches

Before changing branches or starting new work:

- Check all `in_progress` tasks
- Either complete them or update status with notes
- Inform user of any incomplete work

### 3. Task Handoff

When a task needs user action:

- Update todo with clear next steps
- Mark as `pending` with reason
- Notify user explicitly

## Task States

- **pending**: Task not yet started
- **in_progress**: Currently working on (limit to ONE at a time)
- **completed**: Task finished successfully

## Examples of When to Use Todo List

### Example 1: Complex Feature Implementation

```text
User: I want to add support for custom color schemes. Make sure you run the tests when you're done!
```

**Use todos because**: Multi-step feature + explicit test requirements

### Example 2: Multiple Features

```text
User: I need to implement these features: custom colors, layer filtering, and SVG export.
```

**Use todos because**: Multiple complex features listed

### Example 3: Performance Optimization

```text
User: Can you help optimize the PDF generation? It's slow for large keymaps.
```

**Use todos because**: Requires analysis, then multiple optimization tasks

### Example 4: Rename Across Codebase

```text
User: Help me rename the function parse_keymap to parse_zmk_keymap across the project
```

**Use todos because**: Multiple files need systematic updates

## Examples of When NOT to Use Todo List

### Example 1: Simple Question

```text
User: How do I run the tests?
```

**Skip todos**: Single trivial informational request

### Example 2: Information Request

```text
User: What does the --verbose flag do?
```

**Skip todos**: Pure information, no tasks

### Example 3: Single Edit

```text
User: Can you add a docstring to the parse_keymap function?
```

**Skip todos**: Single straightforward task

### Example 4: Single Command

```text
User: Run make test for me and tell me what happens.
```

**Skip todos**: One command execution

## Best Practices

1. **Be Specific**: Create clear, actionable todo items
2. **Break Down Complex Tasks**: Split large tasks into manageable steps
3. **Update Immediately**: Don't batch status updates
4. **Complete Before Moving On**: Finish current task before starting next
5. **Track Progress**: Update todos with notes if interrupted

## Todo Workflow Example

```text
1. TodoRead - Check current status
2. Identify new task from user request
3. TodoWrite - Add new tasks to list
4. TodoWrite - Mark first task as in_progress
5. Complete the work
6. TodoWrite - Mark as completed
7. TodoWrite - Start next task as in_progress
8. Repeat until all tasks completed
```

## Integration with Other Workflows

- Before creating PRs: Ensure all related todos are completed
- Before context switches: Review and update all in_progress items
- During long tasks: Periodically update progress in todo notes
- After completing features: Mark all related todos as completed

## See Also

- `.claude/task-completion-checklist.md` for completion requirements
- `.claude/guides/git-workflow.md` for git integration
