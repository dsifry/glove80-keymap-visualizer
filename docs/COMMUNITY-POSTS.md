# Community Share Posts

Ready-to-post content for sharing glove80-keymap-visualizer.

---

## MoErgo Discord

**Channel:** #glove80-keymaps or #glove80-general

```
Hey everyone! I made a tool to generate PDF visualizations of your Glove80 keymap layers.

**What it does:**
- Takes your .keymap file (exported from my.glove80.com) and generates a PDF with a visual diagram for each layer
- Inspired by sunaku's layer diagrams: https://sunaku.github.io/moergo-glove80-keyboard-layers.pdf

**Features:**
- Semantic color coding (modifiers, navigation, numbers, symbols, etc.)
- OS-specific modifier symbols (Mac ⌘⌥⌃⇧, Windows, Linux)
- Shows held keys that activate each layer
- Table of contents for easy navigation

**Quick start:**
```
brew install cairo  # macOS (or apt-get install libcairo2-dev on Linux)
pip install glove80-keymap-visualizer
glove80-viz your-keymap.keymap -o my-layers.pdf --color
```

GitHub: https://github.com/dsifry/glove80-keymap-visualizer

Would love feedback! What features would be useful to add?
```

---

## Reddit r/ErgoMechKeyboards

**Title:** `I made a tool to generate PDF layer diagrams for Glove80 keymaps`

**Body:**
```
Hey r/ErgoMechKeyboards!

I built a CLI tool that takes ZMK .keymap files (exported from the MoErgo Glove80 Layout Editor) and generates PDF visualizations of each layer.

**Why I made this:**
I wanted something like sunaku's beautiful layer diagrams (https://sunaku.github.io/moergo-glove80-keyboard-layers.pdf) but automatically generated from my keymap file.

**Features:**
- Semantic color coding by key category (modifiers=teal, navigation=green, numbers=yellow, etc.)
- OS-specific modifier symbols — Mac (⌘⌥⌃⇧), Windows (Win+Ctrl+Alt), Linux
- Shows which key you hold to activate each layer
- Expands MEH/HYPER combos (MEH(K) → ⌃⌥⇧K)
- Table of contents in the PDF
- Can resolve transparent keys to show inherited bindings

**Install:**
```
# Install Cairo first (required for PDF generation)
brew install cairo  # macOS
# or: sudo apt-get install libcairo2-dev  # Ubuntu/Debian

pip install glove80-keymap-visualizer
```

**Usage:**
```
# Export your keymap from my.glove80.com
glove80-viz your-keymap.keymap -o my-layers.pdf --color
```

GitHub: https://github.com/dsifry/glove80-keymap-visualizer

Built with Python, uses keymap-drawer for parsing. MIT licensed.

Feedback welcome! What would make this more useful for your workflow?
```

---

## Reddit r/MechanicalKeyboards

**Title:** `[Tool] Glove80 Keymap Visualizer - Generate PDF diagrams of your keyboard layers`

**Body:**
```
For fellow Glove80 owners: I made a CLI tool that generates PDF visualizations of your keyboard layers from ZMK keymap files.

Export your .keymap from my.glove80.com, run:
```
pip install glove80-keymap-visualizer
glove80-viz keymap.keymap -o layers.pdf --color
```

Get a PDF with a diagram for each layer, color-coded by key type.

GitHub: https://github.com/dsifry/glove80-keymap-visualizer

[Example output in comments]
```

---

## Twitter/X

```
Released glove80-keymap-visualizer - generates PDF diagrams of your Glove80 keyboard layers from ZMK keymap files.

pip install glove80-keymap-visualizer
glove80-viz keymap.keymap -o layers.pdf --color

Color-coded by key type, Mac/Windows/Linux symbols, TOC included.

https://github.com/dsifry/glove80-keymap-visualizer
```

---

## Notes for Posting

1. **Before posting to Discord/Reddit:** Make sure PyPI publish is complete so `pip install` works
2. **Include an image:** Attach/link to the example-color.png from docs/images/
3. **Best times to post on Reddit:** Weekday mornings EST tend to get more visibility
4. **Discord:** The MoErgo Discord is very active and welcoming - good place for initial feedback
5. **Follow up:** Respond to comments/questions promptly to build engagement
