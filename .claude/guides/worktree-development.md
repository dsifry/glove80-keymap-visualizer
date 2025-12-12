# Worktree Development Guide

This guide covers git worktree usage patterns for parallel development.

## Table of Contents

- [When to Use Worktrees](#when-to-use-worktrees)
- [Worktree Setup](#worktree-setup)
- [Workflow Patterns](#workflow-patterns)
- [Multi-Agent Coordination](#multi-agent-coordination)
- [Troubleshooting](#troubleshooting)

## When to Use Worktrees

### Good Use Cases

| Scenario                               | Why Worktrees Help                                            |
| -------------------------------------- | ------------------------------------------------------------- |
| **Multiple PRs in review**             | Work on new features while PRs await review                   |
| **Parallel feature development**       | Multiple agents can work on different features simultaneously |
| **Testing against different branches** | Compare behavior across branches without stashing             |
| **Long-running tasks**                 | Don't block other work while waiting for builds/tests         |
| **Code review reference**              | Keep PR code open while working on something else             |

### When NOT to Use Worktrees

- **Simple, quick tasks** - Overhead isn't worth it for 5-minute fixes
- **Tight integration work** - When changes need to see each other immediately
- **Single-branch workflow** - If you're only working on one thing

## Worktree Setup

### Creating a Worktree

From the **main repository** (not from another worktree):

```bash
# Using the command
/project:worktree-create agent-2 feature/new-feature

# Or using git directly (creates sibling directory)
REPO_DIR="$(git rev-parse --show-toplevel)"
REPO_NAME="$(basename "$REPO_DIR")"
git worktree add "$(dirname "$REPO_DIR")/${REPO_NAME}-worktrees/agent-2" -b feature/new-feature
```

### Worktree Directory Structure

Worktrees are created as siblings to the main repository:

```text
<parent-directory>/
├── <repo-name>/                    # Main repository
│   └── .claude/
│       └── handoffs/               # Handoff documents
└── <repo-name>-worktrees/          # All worktrees live here
    ├── agent-2/
    │   └── .claude/
    │       └── handoffs/
    ├── hotfix/
    └── experiment/
```

## Workflow Patterns

### Starting Work in a New Worktree

1. Create the worktree from main repo:

   ```bash
   /project:worktree-create agent-2 feature/my-feature
   ```

2. Navigate and start Claude (path shown in command output):

   ```bash
   cd ../$(basename $(pwd))-worktrees/agent-2
   claude
   ```

3. Install dependencies (first time only):

   ```bash
   make install-dev
   ```

4. Start development

### Referencing Code from Other Branches

Use `/project:peek-branch` to view files without switching context:

```bash
# View file from main
/project:peek-branch main src/glove80_visualizer/parser.py

# View file from another feature branch
/project:peek-branch feature/other-pr pyproject.toml
```

Or use git directly:

```bash
# View file content
git show main:src/glove80_visualizer/parser.py

# Diff against main
git diff main -- src/glove80_visualizer/
```

### Passing Work Between Agents

Use the handoff workflow:

1. **Source agent** creates handoff:

   ```bash
   /project:agent-handoff agent-2
   ```

2. **Target agent** receives handoff file in `.claude/handoffs/`

3. **Target agent** can load context:

   ```bash
   # Read the handoff file
   cat .claude/handoffs/202501101430-handoff.md

   # Or load a saved session
   /project:load-session
   ```

## Multi-Agent Coordination

### Spawning Agents in Worktrees (Recommended)

Instead of manually navigating to worktrees and starting Claude sessions, **orchestrate agents directly**:

```text
# From main repository, use Claude's Task tool to spawn an agent
Task(
  description: "Fix Issue #123 in worktree"
  subagent_type: "general-purpose"
  run_in_background: true
  prompt: "
    You are working in a git worktree for this repository.
    Branch: fix/issue-123

    IMPORTANT: Change to the worktree directory first (path provided by worktree-create).

    Your task: [Detailed task description]

    After creating the PR, use the pr-shepherd skill to:
    1. Monitor CI and handle failures autonomously
    2. Respond to review comments and resolve all threads
    3. Only escalate to orchestrator for complex issues requiring user input
    4. Report back when PR is ready to merge or if blocked

    Run autonomously - the orchestrator will check in via AgentOutputTool.
  "
)
```

**Key principle**: Agents own their PR lifecycle. The orchestrator spawns and moves on, checking back periodically rather than polling CI.

### Hub-and-Spoke Pattern

Recommended for complex features:

```text
Main Repository (Hub/Orchestrator)
├── Creates worktrees
├── Spawns agents using Task tool (run_in_background: true)
├── Continues other work while agents run
├── Checks in periodically with AgentOutputTool(block=false)
├── Merges completed features
└── Coordinates changes

Worktree: fix-123 (Spoke/Worker Agent)
├── Agent works in isolated directory
├── Creates PR when implementation done
├── Uses pr-shepherd skill to monitor CI
├── Handles review comments autonomously
├── Resolves all threads before reporting done
└── Reports back only when PR ready to merge OR blocked
```

### Handoff Contracts

When handing off work, always include:

1. **What was accomplished** - Completed tasks
2. **What remains** - Specific next steps (not vague goals)
3. **Key decisions** - Why certain approaches were chosen
4. **Gotchas** - Things the next agent should know
5. **Test status** - Did tests pass? What needs testing?

### Avoiding Conflicts

| Shared Resource     | How to Coordinate                                           |
| ------------------- | ----------------------------------------------------------- |
| **pyproject.toml**  | Commit lock files; coordinate version changes               |
| **Shared modules**  | Use interfaces; don't modify contracts without coordination |
| **Test fixtures**   | Use unique identifiers per worktree                         |

## Troubleshooting

### Build Cache Problems

**Symptom**: Stale builds, incorrect types after switching branches

**Solution**:

```bash
# Clean build artifacts
make clean

# Reinstall dependencies
make install-dev
```

### Stale Worktrees

**Symptom**: Old worktrees taking up space or causing confusion

**Solution**:

```bash
# List all worktrees
git worktree list

# Remove a stale worktree (use path from git worktree list)
git worktree remove <worktree-path>

# Prune worktree references
git worktree prune
```

### Worktree Won't Create

**Symptom**: `fatal: 'branch-name' is already checked out at...`

**Cause**: Branch is checked out in another worktree

**Solution**:

```bash
# Create a new branch for this worktree
REPO_DIR="$(git rev-parse --show-toplevel)"
REPO_NAME="$(basename "$REPO_DIR")"
git worktree add "$(dirname "$REPO_DIR")/${REPO_NAME}-worktrees/new-wt" -b new-branch-name

# Or check out a different branch in the existing worktree first
```

## Quick Reference Commands

| Command                                    | Purpose                                |
| ------------------------------------------ | -------------------------------------- |
| `/project:worktree-status`                 | Show current context and all worktrees |
| `/project:worktree-create <name> <branch>` | Create new worktree                    |
| `/project:peek-branch <branch> <file>`     | View file from another branch          |
| `/project:agent-handoff [target]`          | Create handoff document                |
| `git worktree list`                        | List all worktrees                     |
| `git worktree remove <path>`               | Remove a worktree                      |
| `git worktree prune`                       | Clean up stale worktree references     |

## See Also

- [Git Workflow Guide](./git-workflow.md) - Branch management and PR workflows
- [Session Management Guide](./session-management.md) - Saving and loading conversation context
- [Todo Management Guide](./todo-management.md) - Tracking work across sessions
