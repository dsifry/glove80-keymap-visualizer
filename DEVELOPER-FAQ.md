# Developer FAQ for Glove80 Keymap Visualizer

**Audience**: Developers new to this project and/or Claude Code
**Last Updated**: December 2025

This FAQ answers the most common questions developers have about working on the Glove80 Keymap Visualizer. It covers project setup, development workflows, Claude Code integration, and troubleshooting.

---

## Table of Contents

- [Section 0: Getting Started](#section-0-getting-started)
  - [Q0: Environment setup](#q0-how-do-i-set-up-the-development-environment)
  - [Q1: System requirements](#q1-what-are-the-system-requirements)
  - [Q1a: Installing Python](#q1a-how-do-i-install-python-310-on-my-system)
  - [Q1b: Installing Cairo](#q1b-how-do-i-install-cairo-required-for-pdf-generation)
  - [Q1c: Installing Make](#q1c-how-do-i-install-make)
  - [Q1d: Installing Playwright](#q1d-how-do-i-install-playwright-required-for-kle-output)
  - [Q1e: Installing GitHub CLI](#q1e-how-do-i-install-github-cli-required-for-claude-code-pr-workflows)
- [Section 1: Project Architecture](#section-1-project-architecture)
- [Section 2: Development Workflow](#section-2-development-workflow)
- [Section 3: Testing](#section-3-testing)
- [Section 4: Claude Code Integration](#section-4-claude-code-integration)
- [Section 5: Troubleshooting](#section-5-troubleshooting)

---

## Section 0: Getting Started

### Q0: How do I set up the development environment?

**Step 1: Clone the repository**

```bash
git clone https://github.com/dsifry/glove80-keymap-visualizer.git
cd glove80-keymap-visualizer
```

**Step 2: Install development dependencies**

```bash
make install-dev
```

This creates a virtual environment in `.venv/` and installs all dependencies including dev tools (pytest, black, ruff, mypy).

**Step 3: Verify the installation**

```bash
make test
```

All tests should pass. If not, see [Troubleshooting](#section-5-troubleshooting).

---

### Q1: What are the system requirements?

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.10+ | Runtime environment |
| Make | Any recent version | Build automation |
| Cairo | System library | PDF generation via CairoSVG |
| GitHub CLI (`gh`) | 2.x+ | PR workflows with Claude Code |

---

### Q1a: How do I install Python 3.10+ on my system?

#### macOS

**Option A: Homebrew (Recommended)**
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11

# Verify installation
python3 --version
```

**Option B: pyenv (For managing multiple Python versions)**
```bash
# Install pyenv via Homebrew
brew install pyenv

# Add to your shell profile (~/.zshrc or ~/.bashrc)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc

# Restart shell or source the profile
source ~/.zshrc

# Install Python 3.11
pyenv install 3.11
pyenv global 3.11

# Verify
python --version
```

**Option C: mise (formerly rtx) - Modern version manager**
```bash
# Install mise
curl https://mise.run | sh

# Add to shell profile
echo 'eval "$(~/.local/bin/mise activate zsh)"' >> ~/.zshrc
source ~/.zshrc

# Install Python
mise use --global python@3.11

# Verify
python --version
```

#### Ubuntu/Debian Linux

**Option A: System package (Ubuntu 22.04+ has Python 3.10+)**
```bash
# Update package list
sudo apt update

# Install Python and venv
sudo apt install python3 python3-pip python3-venv

# Verify
python3 --version
```

**Option B: deadsnakes PPA (For newer Python on older Ubuntu)**
```bash
# Add the deadsnakes PPA
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev

# Verify
python3.11 --version
```

**Option C: pyenv**
```bash
# Install dependencies
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
  libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
  libffi-dev liblzma-dev

# Install pyenv
curl https://pyenv.run | bash

# Add to ~/.bashrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# Restart shell
exec "$SHELL"

# Install Python
pyenv install 3.11
pyenv global 3.11
```

#### Fedora/RHEL Linux

```bash
# Fedora (usually has recent Python)
sudo dnf install python3 python3-pip python3-devel

# Verify
python3 --version
```

#### Windows

**Option A: Official Python Installer (Recommended)**
1. Download Python 3.11+ from [python.org/downloads](https://www.python.org/downloads/)
2. Run the installer
3. **Important**: Check "Add Python to PATH" during installation
4. Open Command Prompt or PowerShell and verify:
   ```powershell
   python --version
   ```

**Option B: Microsoft Store**
1. Open Microsoft Store
2. Search for "Python 3.11"
3. Click "Get" to install
4. Verify in PowerShell:
   ```powershell
   python3 --version
   ```

**Option C: winget (Windows Package Manager)**
```powershell
# Install Python
winget install Python.Python.3.11

# Verify
python --version
```

**Option D: WSL2 (Recommended for best compatibility)**

Windows Subsystem for Linux provides a full Linux environment:

```powershell
# Enable WSL (run as Administrator)
wsl --install

# Restart computer, then open Ubuntu from Start menu
# Follow the Ubuntu/Debian instructions above
```

---

### Q1b: How do I install Cairo (required for PDF generation)?

#### macOS
```bash
brew install cairo
```

#### Ubuntu/Debian
```bash
sudo apt-get install libcairo2-dev
```

#### Fedora/RHEL
```bash
sudo dnf install cairo-devel
```

#### Arch Linux
```bash
sudo pacman -S cairo
```

#### Windows

**Option A: Using GTK for Windows**
1. Download the GTK+ runtime from [gtk.org](https://www.gtk.org/docs/installations/windows/)
2. Add the `bin` folder to your PATH

**Option B: Using MSYS2 (Recommended)**
```powershell
# Install MSYS2 from https://www.msys2.org/

# In MSYS2 terminal:
pacman -S mingw-w64-x86_64-cairo
```

**Option C: Using Conda**
```powershell
conda install -c conda-forge cairo
```

**Option D: WSL2 (Best compatibility)**
```bash
# In WSL2 Ubuntu terminal
sudo apt-get install libcairo2-dev
```

---

### Q1c: How do I install Make?

#### macOS
```bash
# Make is included with Xcode Command Line Tools
xcode-select --install
```

#### Ubuntu/Debian
```bash
sudo apt-get install build-essential
```

#### Fedora/RHEL
```bash
sudo dnf install make
```

#### Windows

**Option A: Using Chocolatey**
```powershell
# Install Chocolatey first (see chocolatey.org)
choco install make
```

**Option B: Using MSYS2**
```powershell
# In MSYS2 terminal
pacman -S make
```

**Option C: Using WSL2 (Recommended)**
```bash
# Make is included in build-essential
sudo apt-get install build-essential
```

**Option D: Without Make**

If you can't install Make on Windows, you can run the commands directly:

```powershell
# Instead of: make install-dev
python -m venv .venv
.\.venv\Scripts\pip install --upgrade pip
.\.venv\Scripts\pip install -r requirements-dev.txt
.\.venv\Scripts\pip install -e .

# Instead of: make test
.\.venv\Scripts\pytest

# Instead of: make lint
.\.venv\Scripts\ruff check src tests

# Instead of: make typecheck
.\.venv\Scripts\mypy src

# Instead of: make format
.\.venv\Scripts\black src tests
.\.venv\Scripts\ruff check --fix src tests
```

---

### Q1d: How do I install Playwright (required for KLE output)?

Playwright is required for generating KLE-style PNG and PDF output via headless browser.

**Step 1: Install Playwright Python package** (already included in requirements.txt)
```bash
pip install playwright
# or with make install-dev
```

**Step 2: Install Chromium browser**
```bash
playwright install chromium
```

This downloads a browser (~90MB) that runs headlessly to render keyboard layouts from keyboard-layout-editor.com.

**When is this needed?**
- Using `--format kle-png` (renders PNG via browser)
- Using `--format kle-pdf` (renders PDF via browser)
- Running the slow browser tests (`pytest -m "slow"`)

**When is this NOT needed?**
- Using `--format pdf` (default SVG-based rendering)
- Using `--format svg`
- Using `--format kle` (JSON output only)
- Running fast tests (`pytest -m "not slow"`)

---

### Q1e: How do I install GitHub CLI (required for Claude Code PR workflows)?

The GitHub CLI (`gh`) is required for Claude Code to create and manage pull requests, handle PR comments, and interact with GitHub on your behalf.

#### macOS
```bash
brew install gh
```

#### Ubuntu/Debian
```bash
# Add GitHub's official apt repository
type -p curl >/dev/null || sudo apt install curl -y
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

#### Fedora/RHEL
```bash
sudo dnf install gh
```

#### Arch Linux
```bash
sudo pacman -S github-cli
```

#### Windows
```powershell
# Using winget
winget install GitHub.cli

# Or using Chocolatey
choco install gh

# Or using Scoop
scoop install gh
```

#### Authenticate with GitHub

**Important**: After installing, you must authenticate `gh` with your GitHub account:

```bash
gh auth login
```

Follow the interactive prompts to:
1. Choose GitHub.com (or GitHub Enterprise if applicable)
2. Choose HTTPS or SSH for git operations
3. Authenticate via web browser (recommended) or paste a token

**Verify authentication:**
```bash
gh auth status
```

You should see output like:
```
github.com
  ✓ Logged in to github.com as yourusername
  ✓ Git operations for github.com configured to use https protocol.
  ✓ Token: gho_****
```

**Why is this needed?**
- Claude Code uses `gh` to create pull requests (`/project:create-pr`)
- It manages PR review comments (`/project:handle-pr-comments`)
- It monitors PR status (`/project:pr-shepherd`)
- Without authentication, these commands will fail

---

### Q2: How do I run the tool?

```bash
# Basic usage
.venv/bin/glove80-viz your-keymap.keymap -o output.pdf

# Or with the virtual environment activated
source .venv/bin/activate
glove80-viz your-keymap.keymap -o output.pdf

# Run the included example
make run-example
```

---

### Q3: What's the project structure?

```
glove80-keymap-visualizer/
├── src/glove80_visualizer/    # Main source code
│   ├── cli.py                 # Command-line interface
│   ├── parser.py              # Keymap file parsing (uses keymap-drawer)
│   ├── extractor.py           # Layer data extraction
│   ├── svg_generator.py       # SVG rendering (uses keymap-drawer)
│   ├── pdf_generator.py       # PDF output (CairoSVG + pikepdf)
│   ├── models.py              # Data models
│   ├── config.py              # Configuration
│   └── colors.py              # Color definitions
├── tests/                     # Test files
│   ├── fixtures/              # Test keymap files
│   └── test_*.py              # Test modules
├── .claude/                   # Claude Code configuration
│   ├── commands/              # Slash commands
│   ├── guides/                # Detailed guides
│   └── plugins/               # Project-specific skills
├── CLAUDE.md                  # Claude Code instructions
├── SUPERPOWERS.md             # Superpowers plugin guide
├── Makefile                   # Development commands
└── pyproject.toml             # Project configuration
```

---

## Section 1: Project Architecture

### Q4: What's the data pipeline?

The tool follows a 5-stage pipeline:

```
.keymap → Parser → YAML → Extractor → Layers → SVG Generator → PDF Generator → .pdf
              ↓                                       ↓                ↓
        keymap-drawer                           keymap-drawer    CairoSVG + pikepdf
        (ZmkKeymapParser)                       (KeymapDrawer)
```

1. **Parser** (`parser.py`): Uses `keymap-drawer`'s `ZmkKeymapParser` to convert ZMK `.keymap` to YAML
2. **Extractor** (`extractor.py`): Parses YAML and extracts layer data (pure Python, no external deps)
3. **SVG Generator** (`svg_generator.py`): Uses `keymap-drawer`'s `KeymapDrawer` to render SVG for each layer
4. **PDF Generator** (`pdf_generator.py`): Converts SVGs to PDF pages using CairoSVG, merges with pikepdf

---

### Q5: What are the key dependencies?

| Dependency | Purpose | Version |
|------------|---------|---------|
| `keymap-drawer` | Parse keymaps, generate SVGs | 0.18.x |
| `cairosvg` | Convert SVG to PDF | 2.7.x |
| `pikepdf` | Merge PDF pages | 8.x-9.x |
| `pyyaml` | Parse YAML intermediate format | 6.x |
| `click` | CLI framework | 8.x |

---

### Q6: How does keymap-drawer integration work?

We use `keymap-drawer` as a **Python library** (not subprocess):

**Parsing (keymap → YAML):**
```python
from keymap_drawer.parse.zmk import ZmkKeymapParser
from keymap_drawer.config import ParseConfig

parser = ZmkKeymapParser(ParseConfig(), columns=10, keyboard="glove80")
result = parser.parse(keymap_content)
```

**Rendering (Layer → SVG):**
```python
from keymap_drawer.draw.draw import KeymapDrawer
from keymap_drawer.config import Config as KDConfig

drawer = KeymapDrawer(config=KDConfig(), keymap=keymap_data)
svg_output = drawer.draw()
```

The integration is in `parser.py` and `svg_generator.py`. Error handling wraps library calls with clear error messages.

---

### Q7: Why PDF instead of just SVG?

- **Multi-page**: Each layer becomes a PDF page - easy to print or share
- **Portable**: PDFs work everywhere without special viewers
- **Compact**: Multiple layers in one file instead of many SVGs

---

## Section 2: Development Workflow

### Q8: What are the essential Make commands?

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `make install-dev` | Install all dependencies | Initial setup, after pulling |
| `make test` | Run tests | Before commits, TDD workflow |
| `make test-cov` | Tests with coverage report | Checking test coverage |
| `make lint` | Check code quality | Before commits |
| `make typecheck` | Type checking with mypy | Before commits |
| `make format` | Auto-format code | After making changes |
| `make clean` | Clean build artifacts | Fresh start, troubleshooting |
| `make build` | Build distribution packages | Creating releases |

**Before marking any task complete:**
```bash
make lint && make typecheck && make test
```

---

### Q9: What's the TDD workflow?

This project requires Test-Driven Development:

1. **RED**: Write a failing test first
   ```bash
   make test  # Watch it fail
   ```

2. **GREEN**: Write minimal code to pass
   ```bash
   make test  # Watch it pass
   ```

3. **REFACTOR**: Improve code while tests stay green
   ```bash
   make test  # Still passing
   ```

4. **REPEAT**: Next feature cycle

**Never write production code without a failing test first.**

---

### Q10: How do I add a new feature?

1. **Create a spec** in `docs/{branch-name}/specs/` describing the feature
   - Use hyphens instead of slashes: branch `feature/my-feature` → `docs/feature-my-feature/specs/`
2. **Write tests** in `tests/test_*.py` that fail
3. **Implement** minimal code in `src/glove80_visualizer/`
4. **Refactor** while tests stay green
5. **Run validation**: `make lint && make typecheck && make test`
6. **Create PR**

---

### Q11: What's the git workflow?

**Branch naming:**
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation only

**Commit messages:**
- Summarize the "why" not the "what"
- Include `Co-Authored-By: Claude (AI Assistant)` if Claude helped

**Before pushing:**
```bash
make lint && make typecheck && make test
```

---

### Q12: How do I handle type hints?

**Requirements:**
- All public functions must have type hints
- No `Any` without documented justification
- Never use `# type: ignore` without explanation

**Example:**
```python
def parse_keymap(keymap_path: Path) -> ParsedKeymap:
    """Parse a ZMK keymap file into structured data."""
    ...
```

---

## Section 3: Testing

### Q13: Where do tests live?

```
tests/
├── conftest.py           # Shared fixtures
├── fixtures/             # Test keymap files
│   ├── simple.keymap
│   ├── multi_layer.keymap
│   ├── hold_tap.keymap
│   └── invalid.keymap
├── test_parser.py        # Parser tests
├── test_extractor.py     # Extractor tests
├── test_svg_generator.py
├── test_pdf_generator.py
├── test_models.py        # Data model tests
├── test_colors.py        # Color scheme tests
├── test_integration.py   # End-to-end tests
└── test_cli.py           # CLI integration tests
```

---

### Q14: How do I write a good test?

**Good test characteristics:**
- Tests one thing
- Clear name describing behavior
- Uses real code (mocks only when unavoidable)
- Covers edge cases

**Example:**
```python
def test_parser_handles_empty_layer():
    """Parser should return empty key list for layer with no bindings."""
    keymap = create_keymap_with_empty_layer()
    result = parse_keymap(keymap)
    assert result.layers[0].keys == []
```

**Bad test:**
```python
def test_parser():  # Too vague
    result = parse_keymap(some_file)
    assert result  # Doesn't verify behavior
```

---

### Q15: How do I use test fixtures?

Fixtures are defined in `tests/conftest.py`:

```python
@pytest.fixture
def minimal_keymap(tmp_path):
    """Create a minimal valid keymap for testing."""
    keymap_file = tmp_path / "test.keymap"
    keymap_file.write_text(MINIMAL_KEYMAP_CONTENT)
    return keymap_file
```

Use in tests:
```python
def test_parser_parses_minimal_keymap(minimal_keymap):
    result = parse_keymap(minimal_keymap)
    assert len(result.layers) == 1
```

---

### Q15b: Where are test mocks and factories located?

All shared mocks and factories live in `tests/conftest.py`:

| Factory Class | Purpose | Created Fixtures |
|---------------|---------|-----------------|
| `PlaywrightMockFactory` | Mock headless browser operations | `playwright_mocks` |
| `PILMockFactory` | Mock PIL/Pillow image operations | `pil_image_mock`, `pil_module_mock` |
| `PdfMergerMockFactory` | Mock PyPDF2 PDF merging | `pdf_merger_mock` |

**Composite Fixture:**
- `kle_renderer_mocks` - Complete set of mocks for KLE rendering tests

**Usage Example:**
```python
def test_browser_render(playwright_mocks, mocker):
    mock_playwright, mock_browser, mock_page = playwright_mocks
    mocker.patch(
        "glove80_visualizer.kle_renderer.sync_playwright",
        return_value=mock_playwright
    )
    # Test browser-based rendering
```

**Important Guidelines:**
- **Always check conftest.py first** before creating new mocks
- **Add new factories to conftest.py** for reuse across tests
- **Use mocks for slow dependencies** (browsers, network, external APIs)
- **Avoid mocks for core business logic** - test real code when possible

---

### Q16: How do I run specific tests?

```bash
# Run single test file
.venv/bin/pytest tests/test_parser.py

# Run single test function
.venv/bin/pytest tests/test_parser.py::test_parser_handles_empty_layer

# Run tests matching pattern
.venv/bin/pytest -k "parser"

# Run with verbose output
.venv/bin/pytest -v

# Skip slow tests
.venv/bin/pytest -m "not slow"
```

---

## Section 4: Claude Code Integration

### Q17: How do I start Claude Code in this project?

```bash
cd ~/Developer/glove80-keymap-visualizer
claude
```

Claude automatically loads:
- `CLAUDE.md` - Project instructions
- Superpowers skills - Development workflows
- Custom slash commands - Project-specific tools

---

### Q18: What slash commands are available?

**Task Management:**
- `/project:start-task <description>` - Assess and start a task
- `/project:fix-failing-tests` - Systematic test fixing

**Code Review & PRs:**
- `/project:create-pr <branch>` - Create comprehensive PR
- `/project:review-this <path>` - CTO-level review of specs/plans/code
- `/project:handle-pr-comments <pr>` - Address review feedback
- `/project:pr-shepherd [pr]` - Monitor PR through merge

**Session Management:**
- `/project:save-session [name]` - Save conversation context
- `/project:load-session [id]` - Resume previous session
- `/project:list-sessions` - Browse saved sessions
- `/project:manage-sessions` - Organize and maintain sessions

**Worktree Management:**
- `/project:worktree-status` - Show current worktree context
- `/project:worktree-create <name> <branch>` - Create new worktree
- `/project:peek-branch <branch> <file>` - View file from other branch
- `/project:agent-handoff [target]` - Save context for handoff to another agent

---

### Q19: What are Superpowers skills?

Superpowers are structured workflows that guide Claude. Key skills for this project:

| Skill | When It Activates |
|-------|-------------------|
| `brainstorming` | Before coding features |
| `test-driven-development` | When implementing code |
| `systematic-debugging` | When investigating bugs |
| `verification-before-completion` | Before marking tasks done |

See [SUPERPOWERS.md](./SUPERPOWERS.md) for the full guide.

---

### Q20: How do I use extended thinking?

For complex tasks, prompt Claude with thinking keywords:

| Keyword | Thinking Level |
|---------|----------------|
| `think` | Light analysis |
| `think hard` | Deeper analysis |
| `think harder` | Extensive analysis |
| `ultrathink` | Maximum depth |

Example:
```
ultrathink about how to add support for custom color schemes
```

---

### Q21: How do sessions work?

Sessions let you save and resume Claude conversations:

**Save current context:**
```
/project:save-session adding-color-support
```

**Resume later:**
```
/project:load-session adding-color-support
```

**List available sessions:**
```
/project:list-sessions
```

Useful for:
- Long-running tasks spanning multiple days
- Handing off work to another developer
- Returning to incomplete work

---

## Section 5: Troubleshooting

### Q22: Tests are failing after a clean install

**Try these steps in order:**

1. **Clean and reinstall:**
   ```bash
   make clean
   make install-dev
   make test
   ```

2. **Check Python version:**
   ```bash
   python3 --version  # Should be 3.10+
   ```

3. **Check Cairo is installed:**
   ```bash
   # macOS
   brew list cairo

   # Linux
   ldconfig -p | grep cairo
   ```

4. **Check keymap-drawer:**
   ```bash
   .venv/bin/keymap --version
   ```

---

### Q23: Type errors I can't resolve

**DO NOT use these shortcuts:**
- `# type: ignore` without documented justification
- `Any` type without explanation
- Removing tests to fix type errors

**DO try these:**

1. **Check the actual types:**
   ```bash
   make typecheck  # See full error messages
   ```

2. **Use proper type narrowing:**
   ```python
   if isinstance(value, str):
       # Now mypy knows it's a string
   ```

3. **Ask Claude for help:**
   ```
   Help me fix this mypy error: [paste error]
   ```

---

### Q24: Lint errors from ruff

**Auto-fix most issues:**
```bash
make format
```

**Manual fixes needed for:**
- Unused imports - Remove them
- Undefined names - Fix the typo or add import
- Line too long - Break into multiple lines

---

### Q25: keymap-drawer subprocess errors

**Common causes:**

1. **keymap-drawer not installed:**
   ```bash
   make install-dev  # Reinstall dependencies
   ```

2. **Invalid keymap syntax:**
   - Check your `.keymap` file for ZMK syntax errors
   - Try parsing with keymap-drawer directly:
     ```bash
     .venv/bin/keymap parse -z your-file.keymap
     ```

3. **Missing config file:**
   - Check that config files exist in expected locations

---

### Q26: CairoSVG rendering issues

**Common causes:**

1. **Missing Cairo system library:**
   - macOS: `brew install cairo`
   - Linux: `apt-get install libcairo2-dev`

2. **Invalid SVG from keymap-drawer:**
   - Save the intermediate SVG and inspect it
   - Check for XML parsing errors

3. **Special characters in labels:**
   - Ampersands (`&`) need escaping - this was fixed in v0.4.1
   - Check for other special XML characters

---

### Q27: PDF generation fails

**Common causes:**

1. **Empty SVG pages:**
   - Check that layers have content
   - Verify keymap-drawer output

2. **pikepdf errors:**
   - Check pikepdf version compatibility (8.x-9.x)
   - Try with a simpler PDF first

3. **File permission issues:**
   - Check write permissions on output directory

---

### Q28: Claude seems confused about the project

**Reset context:**
1. Start a new Claude session
2. Let Claude read `CLAUDE.md` automatically
3. Explicitly ask Claude to check current state:
   ```
   Check the current project state and tell me what you see
   ```

**Load a saved session:**
```
/project:load-session [session-name]
```

---

## Quick Reference

### Essential Commands

| Task | Command |
|------|---------|
| Setup | `make install-dev` |
| Test | `make test` |
| Lint | `make lint` |
| Type check | `make typecheck` |
| Format | `make format` |
| Full validation | `make lint && make typecheck && make test` |
| Run tool | `.venv/bin/glove80-viz input.keymap -o output.pdf` |

### File Locations

| What | Where |
|------|-------|
| Source code | `src/glove80_visualizer/` |
| Tests | `tests/` |
| Test fixtures | `tests/fixtures/` |
| **Mock factories** | `tests/conftest.py` |
| Claude config | `.claude/` |
| Slash commands | `.claude/commands/` |
| Documentation guides | `.claude/guides/` |

### Claude Slash Commands

| Command | Purpose |
|---------|---------|
| `/project:start-task` | Begin a new task |
| `/project:create-pr` | Create pull request |
| `/project:save-session` | Save conversation |
| `/project:load-session` | Resume conversation |
| `/project:worktree-status` | Show worktree context |

---

## Further Reading

- [CLAUDE.md](./CLAUDE.md) - Claude Code project instructions
- [SUPERPOWERS.md](./SUPERPOWERS.md) - Superpowers plugin guide
- [README.md](./README.md) - Project overview and usage
- [.claude/guides/](./.claude/guides/) - Detailed workflow guides
