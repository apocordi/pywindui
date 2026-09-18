# PywindUI

A modern, declarative Python UI framework built on top of [Flet](https://flet.dev). Write desktop apps with minimal boilerplate using a clean, component-based syntax.

All the components you need for a fast but consistent UI.

## Requirements

```bash
Flet (Follow Installation)
Python
Node.JS
```

## Installation
```bash
# Download PywindUI
git clone https://github.com/apocordi/pywindui

# Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create app file
python pywindui.py new MyApp
```

> **Note:** Always activate the venv before running your app during development. Commands like `python pywindui.py d` require `flet` to be on your PATH, which the venv provides.

Your project folder should look like this:

```
MyApp/
├── PywindUI/
│   ├── system.py
│   ├── utilities.py
│   ├── components.py
│   └── theme.py
├── MyApp.py
└── pywindui.py
```

## Quick Start
Create app file in root (E.g MyApp.py)

> **Note:** A template can be generated with whatever app name you choose, with following command:

```bash
python pywindui.py new MyApp
```

MyApp.py
```python
from pywindui import *

MyApp = App()

MyApp("Loading",
    Window(TitleBar="Custom", Theme="Light", Title="MyApp", Size=(800, 600), minSize=(800, 600)),
)

MyApp("Design",
    View(
        TitleBar(Title="MyApp", Logo="Outline"),
        Text("Hello World!", Size=84),
    )
)
```

Run it:
```bash
python pywindui.py
```

---

## Running Your App

> **Note:** If multiple apps within root, please specify with e.g MyApp(If not given it auto-finds app).

```bash
# Run (auto-finds your app file)
python pywindui.py

# Run a specific app
python pywindui.py MyApp

# Hot-reload during development (or --dev)
python pywindui.py d

# Precompile bytecode cache (or --build)
python pywindui.py b
```

```bash
# Optimize imports before exporting/sharing (or --import)
python pywindui.py i

# Reset imports to wildcard imports (*) for developing. (or --wildcard)
python pywindui.py w
```

> **Note:** The `i` flag scans your app code, finds which components you actually use, and rewrites the wildcard `import *` in `pywindui.py` to explicit imports. Run it once before publishing. The `w` flag resets back to the wildcard `import *`.

---

## App Lifecycle

PywindUI uses a phase-based lifecycle. Register each phase with `App("Phase", ...)`:

```python
MyApp = App()

# Runs before the window opens
MyApp("Starting", Do(print, "Starting up..."))

# Configure the window
MyApp("Loading", Window(Theme="Dark", Title="My App", Size=(800, 600)))

# Build the UI
MyApp("Design", View(...))

# Runs after UI is built
MyApp("Ready", Do(print, "App is ready!"))

# Runs on close (only if registered)
MyApp("Closing", Do(print, "Goodbye!"))
```

### Decorator Style

For functions that need more logic, use decorators:

```python
@MyApp.Functions
def doSomething():
    print("Hello from a function!")

@MyApp.Ready
def onReady():
    print("App loaded!")

@MyApp.Closing
def onClose():
    print("Cleaning up...")
```

You can mix both styles freely.

---

## Window

Configure the app window in the `"Loading"` phase:

```python
MyApp("Loading",
    Window(
        Theme="Light",          # "Light", "Dark", or "System"
        Title="My App",
        TitleBar="Custom",      # "Custom" (frameless) or "Native"
        Size=(800, 600),        # (width, height)
        minSize=(400, 300),
        maxSize=(1200, 900),
        Resizable=True,
        Padding=0,
        bgColor=Colors.bg,
    ),
)
```

---

## Layout

### View

Top-level container for your UI. Wraps everything in a full-height column:

```python
View(
    TitleBar(Title="My App"),
    Box(...),
)
```

### Box

The main layout content container. Arranges children vertically, horizontally, or as a floating stack:

```python
# Vertical
Box(
    Direction="Vertical",
)

# Horizontal
Box(
    Direction="Horizontal",
)

# Floating
Box(
    Direction="Floating",
)
```

**Box Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| Direction | str | "Vertical" | "Vertical", "Horizontal", or "Floating" |
| Align | str | None | "Start", "Center", "End", "Between", "Around", "Evenly" |
| Gap | int | 0 | Space between children |
| Padding | padding | None | Inner padding (use `Pads(x, y)` or `Pad(value)`) |
| bgColor | str | None | Background color |
| Border | bool | None | Show border |
| borderColor | str | Colors.border | Border color |
| Radius | int | None | Corner radius |
| Height | int | None | Fixed height |
| Width | int | None | Fixed width |
| Fill | bool | False | Expand to fill parent |
| Opacity | float | 1.0 | Transparency (0.0 – 1.0) |
| Animate | bool | False | Animate property changes |
| onClick | func | None | Click handler |
| scroll | bool | False | Enable scrolling (vertical only) |

### xyBox
A Box within another Box, configure each Box seperatly or as one.
Centers content with same/shared alignment:

```python
xyBox(
    Text("Centered!"),
    Align="Center",
)
```

Centers content with different alignments:
```python
xyBox(
    Text("Centered!"),
    xAlign="Center",
    yAlign="Start",
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| Align | str | "" | Sets both x and y alignment |
| xAlign | str | None | "Start", "Center", "End" |
| yAlign | str | None | "Start", "Center", "End" |
| Gap | int | 0 | Space between children |
| Fill | bool | True | Expand to fill parent |

### Spacer

Injects space between children inside a Box:

```python
Box(
    Text("Top"),
    Spacer("Between", "Vertical"),  # pushes apart
    Text("Bottom"),
    Direction="Vertical",
)

Box(
    Text("Left"),
    Spacer(40, "Horizontal"),       # fixed 40px gap
    Text("Right"),
    Direction="Horizontal",
)
```
If Spacer resides in a Box with given Gap, the specific Spacer overwrites root Gap.
```python
Box(
    Box(
        Text("Left"),
        Text("Right"),

        Gap=5
        Direction="Horizontal",
    )
    Spacer(5, "Vertical"),       # fixed 5px gap, excluding the 10px root given gap
    Text("Text"),
    Button("Button"),

    Gap=10,
    Direction="Vertical",
)
```



### Padding Helpers

```python
Pads(x=16, y=8)   # horizontal and vertical padding
Pad(12)            # uniform padding on all sides
```

---

## Components

### Button

```python
# Primary (default)
Button(Text="Click Me", Icon="rocket", Click=myFunc)

# Outline
Button(Text="Cancel", Variant="Outline")

# Secondary
Button(Text="Settings", Variant="Secondary", Icon="settings")

# Ghost (transparent)
Button(Text="", Icon="close", Variant="Ghost", Width=30, Height=30)

# Icon-only
Button(Text="", Icon="folder", Variant="Outline", Width=30, Height=30)

# Tab navigation
Button(Text="Go to Settings", Goto="Settings")

# Full width
Button(Text="Submit", Fill=True)
```

**Button Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| Text | str | "Button" | Button label (empty for icon-only) |
| Icon | str | None | Material icon name (e.g. "folder", "close", "rocket") |
| Icons | str | None | Icon style: "Rounded" or "Sharp" |
| IconSize | int | 18 | Icon size |
| Click | func | None | Click handler |
| Goto | str | None | Tab name to switch to on click |
| Variant | str | "Default" | "Default", "Outline", "Secondary", "Ghost" |
| Height | int | 30 | Button height |
| Width | int | None | Button width |
| Fill | bool | False | Expand to fill parent width |
| Radius | int | Radius.md | Corner radius |

### Text

```python
Text("Hello World", Size=14)
Text("Title", Size=24, Weight=ft.FontWeight.W_600)
Text("Muted text", Size=12, Color=Colors.muted_fg, Italic=True)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| Text | str | — | The text content |
| Size | int | 14 | Font size |
| Weight | FontWeight | W_400 | Font weight |
| Color | str | Colors.fg | Text color |
| Italic | bool | False | Italic style |
| Tight | bool | True | Compact line height |

### Link

```python
Link("Learn more", Size=12, Color=Colors.accent)
```

### TextBox

```python
TextBox(Placeholder="Type here...", Height=30, TextSize=14, Width=200)
TextBox(Placeholder="Search...", Fill=True)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| Placeholder | str | "Placeholder" | Hint text |
| TextSize | int | 14 | Font size |
| Height | int | None | Input height |
| Width | int | None | Input width |
| Fill | bool | False | Expand to fill parent |
| Radius | int | Radius.md | Corner radius |

### TitleBar

Custom window title bar (use with `TitleBar="Custom"` in Window):

```python
# Simple — logo + title + window controls
TitleBar(Title="My App", Icon="folder")

# Detailed — logo + title + description + window controls
TitleBar(
    Title="My App",
    Desc="A cool app",
    Variant="LogoDesc",
    Icon="numbers",
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| Title | str | "Title" | Window title |
| Desc | str | "Description" | Subtitle (LogoDesc variant only) |
| Variant | str | "Default" | "Default" / "Logo" or "LogoDesc" / "Detailed" |
| Icon | str | "Photo" | Material icon name |
| Logo | str | "Outline" | Button variant for the logo |
| Height | int | 40 | Title bar height |
| ControlBoxes | str | "Ghost" | Variant for min/max/close buttons |

---

## Tabs

Switch between views without page navigation:

```python
MyApp("Design",
    # Register tabs
    Tab(
        xyBox(Text("Welcome!"), Gap=10),
        TabName="Home"
    ),
    Tab(
        xyBox(Text("Settings page"), Gap=10),
        TabName="Settings"
    ),

    # Build the UI with initial tab
    View(
        TitleBar(Title="My App"),
        TabView("Home")
    )
)
```

Switch tabs from buttons:

```python
Button(Text="Go to Settings", Goto="Settings")
```

---

## Theme & Colors

PywindUI includes a full design token system with Light and Dark themes.

### Using Colors

```python
Text("Hello", Color=Colors.fg)
Box(bgColor=Colors.card, Border=True, borderColor=Colors.border)
Button(Text="Danger", Variant="Default")  # uses Colors.primary automatically
```

### Available Color Tokens

| Token | Description |
|-------|-------------|
| `Colors.bg` | Page background |
| `Colors.bg_secondary` | Secondary background |
| `Colors.fg` | Primary text |
| `Colors.card` / `Colors.card_fg` | Card background / text |
| `Colors.primary` / `Colors.primary_fg` | Primary action / text |
| `Colors.secondary` / `Colors.secondary_fg` | Secondary surfaces / text |
| `Colors.muted` / `Colors.muted_fg` | Muted surfaces / text |
| `Colors.accent` / `Colors.accent_fg` | Accent highlight / text |
| `Colors.destructive` / `Colors.destructive_fg` | Destructive actions |
| `Colors.success` / `Colors.success_fg` | Success states |
| `Colors.warning` / `Colors.warning_fg` | Warning states |
| `Colors.border` | Border color |
| `Colors.input` | Input border color |
| `Colors.ring` | Focus ring color |
| `Colors.sidebar` / `Colors.sidebar_fg` | Sidebar colors |

### Alpha (Opacity)

```python
Alpha(Colors.primary, 0.5)   # 50% opacity
Alpha("#ff0000", 0.8)         # red at 80%
```

### Toggle Theme at Runtime

```python
Button(Text="Toggle Theme", Click=lambda e: Theme())
```

### Register Custom Themes

```python
Colors.register_theme("ocean", {
    "bg": "#0a1628",
    "fg": "#e0e8f0",
    "primary": "#2196f3",
    "primary_fg": "#ffffff",
    # ... all tokens
})
Colors.set_theme("ocean")
```

---

## Spacing, Size & Radius

Predefined constants for consistent spacing:

```python
class Space:
    null = 0
    one  = 1
    xxs  = 2
    xs   = 4
    sm   = 8
    md   = 16
    lg   = 24
    xl   = 32

class Radius:
    null = 0
    sm   = 4
    md   = 8
    lg   = 12
    full = 999
```

Usage:

```python
Box(Padding=Pads(Space.md, Space.sm), Radius=Radius.lg, Gap=Space.sm)
```

---

## Utilities

### Do

Wrap a function call for use in lifecycle phases:

```python
MyApp("Ready", Do(print, "App is ready!"))
```

### Url

Open a URL in the default browser:

```python
Button(Text="Open Google", Click=lambda e: Url("google.com"))
```

### Date

Returns today's date as `YYYY/MM/DD`:

```python
print(Date())  # "2026/04/11"
```

### Cacher

Debug logger with timestamp:

```python
Button(Text="Log", Click=Cacher("something happened", Name="MyCache"))
# Prints: 2026/04/11 | something happened | MyCache
```

### Terminal

Run system commands:

```python
# Run immediately, capture output
result = Terminal(Command="echo hello", Capture=True)

# Run on button click
Button(Text="Run", Click=Term("echo hello", Mode="Click"))
```

---

## License

MIT
