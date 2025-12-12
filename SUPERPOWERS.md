# Superpowers for Glove80 Keymap Visualizer

**Audience**: Developers using Claude Code with this repository
**Last Updated**: December 2025

This guide explains how to use the Superpowers plugin to enhance your Claude Code development experience with structured workflows, automated skills, and proven development patterns.

---

## Table of Contents

- [What Are Superpowers?](#what-are-superpowers)
- [Installation](#installation)
- [Available Skills](#available-skills)
- [How Skills Work](#how-skills-work)
- [Project-Specific Workflows](#project-specific-workflows)
- [Quick Reference](#quick-reference)

---

## What Are Superpowers?

Superpowers is a Claude Code plugin that provides **skills** - structured workflows that guide Claude through proven development patterns. Instead of relying on ad-hoc approaches, skills ensure consistent, high-quality work.

**Key benefits:**

- **Consistency** - Same proven approach every time
- **Quality gates** - Built-in verification steps
- **Time savings** - No reinventing workflows
- **Error prevention** - Skills encode lessons learned

---

## Installation

### Step 1: Install Claude Code

**macOS (Homebrew)**
```bash
brew install claude-code
```

**macOS/Linux (npm)**
```bash
npm install -g @anthropic-ai/claude-code
```

**Without global install**
```bash
npx @anthropic-ai/claude-code
```

### Step 2: Install the Superpowers Plugin

Start Claude Code and run these commands inside the Claude session:

```
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

**Note:** These are slash commands that run *inside* Claude Code, not shell commands. You must start Claude first, then type these commands.

The plugin installs globally and is available in all projects.

### Step 3: Verify Installation

Start Claude Code in this project:

```bash
cd ~/Developer/glove80-keymap-visualizer
claude
```

At the start of each session, Claude will announce available skills. You should see skills like `brainstorming`, `test-driven-development`, and `systematic-debugging`.

---

## Available Skills

### Core Development Skills

| Skill | When Claude Uses It | What It Does |
|-------|---------------------|--------------|
| **brainstorming** | Before coding any feature | Refines ideas through collaborative questioning before writing code |
| **test-driven-development** | When implementing features or fixes | Enforces RED-GREEN-REFACTOR: write failing test, minimal code, refactor |
| **systematic-debugging** | When encountering bugs | 4-phase process: root cause, patterns, hypothesis, implementation |
| **verification-before-completion** | Before marking any task done | Requires running verification commands and confirming output |

### Planning & Architecture

| Skill | When Claude Uses It | What It Does |
|-------|---------------------|--------------|
| **writing-plans** | After design is approved | Creates detailed implementation plans with exact file paths and code examples |
| **executing-plans** | When implementing approved plans | Executes tasks in batches with review checkpoints |

### Code Quality

| Skill | When Claude Uses It | What It Does |
|-------|---------------------|--------------|
| **requesting-code-review** | After completing major features | Dispatches review agent to verify implementation |
| **receiving-code-review** | When reviewing feedback | Ensures technical rigor, not blind agreement |
| **testing-anti-patterns** | When writing tests | Prevents mock-focused tests and test-only production code |

### Advanced Workflows

| Skill | When Claude Uses It | What It Does |
|-------|---------------------|--------------|
| **using-git-worktrees** | Starting isolated feature work | Creates git worktrees with safety verification |
| **dispatching-parallel-agents** | 3+ independent problems | Runs multiple Claude agents concurrently |
| **root-cause-tracing** | Deep execution errors | Traces bugs backward through call stack |
| **defense-in-depth** | Invalid data causes failures | Validates at every layer data passes through |

---

## How Skills Work

### Automatic Activation

Claude checks for relevant skills at the start of every task. When a skill matches, Claude:

1. Announces which skill it's using
2. Follows the skill's workflow exactly
3. Uses TodoWrite to track checklist items
4. Completes verification steps before marking done

**Example:**
```
You: Add a new command-line option for output format

Claude: I'm using the brainstorming skill to refine the design
before implementation.

Let me first understand the current CLI structure...
[Asks clarifying questions one at a time]
...

Now I'm using the test-driven-development skill to implement
this feature.

RED: Writing failing test for --format option...
```

### Manual Skill Invocation

You can explicitly request a skill:

```
You: Use the systematic-debugging skill to investigate this test failure
```

### Skills Have Checklists

Many skills include verification checklists. Claude tracks each item using TodoWrite and doesn't mark tasks complete until all items pass.

---

## Project-Specific Workflows

This project adds custom workflows on top of Superpowers:

### Custom Slash Commands

| Command | Purpose |
|---------|---------|
| `/project:start-task` | Assess task complexity and choose workflow |
| `/project:fix-failing-tests` | Systematic test fixing with TDD |
| `/project:create-pr` | Create comprehensive pull request |
| `/project:pr-shepherd` | Monitor PR through to merge |

### Project Skills

Located in `.claude/plugins/glove80-viz/skills/`:

| Skill | Purpose |
|-------|---------|
| `pr-shepherd` | Monitors PR: CI/CD, reviews, auto-fixes |
| `handling-pr-comments` | Systematic response to PR feedback |

### Validation Requirements

Before any task is complete, Claude runs:

```bash
make lint && make typecheck && make test
```

This is enforced by the `verification-before-completion` skill combined with project-specific requirements in `CLAUDE.md`.

---

## Quick Reference

### Session Startup

Claude automatically:
1. Loads CLAUDE.md project instructions
2. Checks for applicable Superpowers skills
3. Announces which skills are active

### Common Skill Triggers

| You Say | Skills That Activate |
|---------|---------------------|
| "Add a feature for..." | brainstorming → TDD |
| "Fix this bug..." | systematic-debugging → TDD |
| "Investigate why..." | systematic-debugging |
| "Create a PR..." | verification-before-completion |
| "Review this code..." | requesting-code-review |

### Validation Commands

```bash
# Full validation (required before task completion)
make lint && make typecheck && make test

# Quick test run
make test

# Format code
make format

# Run the tool
.venv/bin/glove80-viz input.keymap -o output.pdf
```

### Key Principles

1. **TDD is mandatory** - Write tests first, then implementation
2. **Brainstorm before coding** - Clarify design before writing code
3. **Verify before completing** - Run all checks, confirm output
4. **Use skills, don't skip them** - Skills exist because they work
5. **100% test coverage target** - All new code should be fully covered
6. **Dependency Injection for testability** - No hardcoded dependencies in services

### Architecture Best Practices

**Dependency Injection (DI) Requirements:**
- No hardcoded external dependencies (file paths, URLs, API clients)
- Components must be testable in isolation
- Configuration should be injectable (constructor or method parameters)
- Use abstract interfaces when possible for external services

**Example of mockable service:**
```python
class KeymapRenderer:
    def __init__(self, drawer_factory: Callable[..., KeymapDrawer]):
        """Inject drawer factory for testability."""
        self._drawer_factory = drawer_factory

    def render(self, keymap: Keymap) -> str:
        drawer = self._drawer_factory(keymap=keymap)
        return drawer.draw()
```

**Test Coverage Requirements:**
- **Hard requirement: 100% test coverage** - No exceptions
- Use mocks for slow dependencies (browsers, network, external APIs)
- Create common mock factories in `tests/conftest.py` for reuse
- Use `make test-cov` to verify coverage before every commit
- PRs with <100% coverage will not be merged

---

## Troubleshooting

### "Claude isn't using skills"

Skills activate based on task context. Be explicit:
- "Using the TDD skill, implement..."
- "Apply systematic-debugging to investigate..."

### "Skill seems overkill for this"

Skills exist because "simple" tasks often become complex. Follow the skill - it's faster than debugging problems the skill would have prevented.

### "Claude skipped verification"

Remind Claude:
- "Please run full validation before marking complete"
- "Use the verification-before-completion skill"

### Updating Superpowers

Inside a Claude Code session, run:

```
/plugin update superpowers@superpowers-marketplace
```

---

## Further Reading

- [Superpowers Plugin Repository](https://github.com/superpowers-marketplace/superpowers)
- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [Project CLAUDE.md](./CLAUDE.md) - Project-specific instructions
- [Task Completion Checklist](.claude/task-completion-checklist.md)
