import sys, os
import importlib
import subprocess

# ── 0. Unified bytecode cache ──
_here = os.path.dirname(os.path.abspath(__file__))
sys.pycache_prefix = os.path.join(_here, "Allcache")

def _precompile():
    """Pre-compile all .py files into pywindui_cache so first run is fast."""
    import compileall
    cache = sys.pycache_prefix
    pkg = os.path.join(_here, "PywindUI")
    compileall.compile_dir(pkg, quiet=1)
    # Also compile loose .py files (app files, pywindui.py itself)
    compileall.compile_dir(_here, maxlevels=0, quiet=1)
    print(f"Bytecode cached in: {cache}")

# ── 1. Fix package path ──
if _here not in sys.path:
    sys.path.insert(0, _here)

# ── 2. Re-export everything ──
from PywindUI.system import *
from PywindUI.utilities import *
from PywindUI.components import *
# ── 3. App discovery ──
def _find_app():
    skip = {"pywind.py", "pywindui.py", "__init__.py"}
    for f in sorted(os.listdir(".")):
        if f.endswith(".py") and f not in skip:
            return f[:-3]
    return None

# ── 4. Auto-import optimizer ──
def _autoimport(app_name):
    """Parse app file, find used names, rewrite pywind.py with explicit imports."""
    import ast

    app_file = app_name + ".py"
    if not os.path.exists(app_file):
        print(f"File not found: {app_file}")
        return

    # Collect every name used in the app
    with open(app_file, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    used = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used.add(node.id)
        elif isinstance(node, ast.Attribute):
            used.add(node.attr)

    # Check what each module exports
    modules = {
        "PywindUI.system":     importlib.import_module("PywindUI.system"),
        "PywindUI.utilities":  importlib.import_module("PywindUI.utilities"),
        "PywindUI.components": importlib.import_module("PywindUI.components"),
    }

    imports = {}  # module -> list of names
    for mod_name, mod in modules.items():
        public = {n for n in dir(mod) if not n.startswith("_")}
        found = sorted(used & public)
        if found:
            imports[mod_name] = found

    # Build new import lines
    lines = []
    for mod_name, names in imports.items():
        lines.append(f"from {mod_name} import {', '.join(names)}")

    # Rewrite pywind.py — find the import block between section markers
    import re
    pywind_path = os.path.abspath(__file__)
    with open(pywind_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = (
        r"(# ── 2\. Re-export everything ──\n)"
        r"(.*?)"
        r"(\n# ── 3\.)"
    )
    new_imports = "\n".join(lines)
    new_content = re.sub(pattern, r"\1" + new_imports + r"\3", content, flags=re.DOTALL)

    with open(pywind_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Updated pywindui.py imports for {app_file}:")
    for line in lines:
        print(f"  {line}")

def _resetimports():
    """Reset explicit imports back to wildcard * imports for dev mode."""
    import re

    pywind_path = os.path.abspath(__file__)
    with open(pywind_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Match the import block between the section markers
    pattern = (
        r"(# ── 2\. Re-export everything ──\n)"
        r"(.*?)"
        r"(\n# ── 3\.)"
    )
    wildcards = (
        "from PywindUI.system import *\n"
        "from PywindUI.utilities import *\n"
        "from PywindUI.components import *"
    )
    new_content = re.sub(pattern, r"\1" + wildcards + r"\3", content, flags=re.DOTALL)

    if new_content == content:
        print("Imports already using wildcards (or markers not found).")
        return

    with open(pywind_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("Reset imports to wildcard (*) dev mode.")

_THEME_CSS_TEMPLATE = """\
@import "tailwindcss";

@custom-variant dark (&:is(.dark *));

:root {
  --background: #f0f8ff;
  --foreground: #374151;
  --card: #ffffff;
  --card-foreground: #374151;
  --popover: #ffffff;
  --popover-foreground: #374151;
  --primary: #22c55e;
  --primary-foreground: #ffffff;
  --secondary: #e0f2fe;
  --secondary-foreground: #4b5563;
  --muted: #f3f4f6;
  --muted-foreground: #6b7280;
  --accent: #d1fae5;
  --accent-foreground: #374151;
  --destructive: #ef4444;
  --destructive-foreground: #ffffff;
  --border: #e5e7eb;
  --input: #e5e7eb;
  --ring: #22c55e;
  --chart-1: #22c55e;
  --chart-2: #10b981;
  --chart-3: #059669;
  --chart-4: #047857;
  --chart-5: #065f46;
  --sidebar: #e0f2fe;
  --sidebar-foreground: #374151;
  --sidebar-primary: #22c55e;
  --sidebar-primary-foreground: #ffffff;
  --sidebar-accent: #d1fae5;
  --sidebar-accent-foreground: #374151;
  --sidebar-border: #e5e7eb;
  --sidebar-ring: #22c55e;
  --font-sans: DM Sans, sans-serif;
  --font-serif: Lora, serif;
  --font-mono: IBM Plex Mono, monospace;
  --radius: 0.5rem;
  --shadow-x: 0px;
  --shadow-y: 4px;
  --shadow-blur: 8px;
  --shadow-spread: -1px;
  --shadow-opacity: 0.1;
  --shadow-color: hsl(0 0% 0%);
  --shadow-2xs: 0px 4px 8px -1px hsl(0 0% 0% / 0.05);
  --shadow-xs: 0px 4px 8px -1px hsl(0 0% 0% / 0.05);
  --shadow-sm: 0px 4px 8px -1px hsl(0 0% 0% / 0.10), 0px 1px 2px -2px hsl(0 0% 0% / 0.10);
  --shadow: 0px 4px 8px -1px hsl(0 0% 0% / 0.10), 0px 1px 2px -2px hsl(0 0% 0% / 0.10);
  --shadow-md: 0px 4px 8px -1px hsl(0 0% 0% / 0.10), 0px 2px 4px -2px hsl(0 0% 0% / 0.10);
  --shadow-lg: 0px 4px 8px -1px hsl(0 0% 0% / 0.10), 0px 4px 6px -2px hsl(0 0% 0% / 0.10);
  --shadow-xl: 0px 4px 8px -1px hsl(0 0% 0% / 0.10), 0px 8px 10px -2px hsl(0 0% 0% / 0.10);
  --shadow-2xl: 0px 4px 8px -1px hsl(0 0% 0% / 0.25);
  --tracking-normal: 0em;
  --spacing: 0.25rem;
}

.dark {
  --background: #0f172a;
  --foreground: #d1d5db;
  --card: #1e293b;
  --card-foreground: #d1d5db;
  --popover: #1e293b;
  --popover-foreground: #d1d5db;
  --primary: #34d399;
  --primary-foreground: #0f172a;
  --secondary: #2d3748;
  --secondary-foreground: #a1a1aa;
  --muted: #19212e;
  --muted-foreground: #6b7280;
  --accent: #374151;
  --accent-foreground: #a1a1aa;
  --destructive: #ef4444;
  --destructive-foreground: #0f172a;
  --border: #4b5563;
  --input: #4b5563;
  --ring: #34d399;
  --chart-1: #34d399;
  --chart-2: #2dd4bf;
  --chart-3: #22c55e;
  --chart-4: #10b981;
  --chart-5: #059669;
  --sidebar: #1e293b;
  --sidebar-foreground: #d1d5db;
  --sidebar-primary: #34d399;
  --sidebar-primary-foreground: #0f172a;
  --sidebar-accent: #374151;
  --sidebar-accent-foreground: #a1a1aa;
  --sidebar-border: #4b5563;
  --sidebar-ring: #34d399;
  --font-sans: DM Sans, sans-serif;
  --font-serif: Lora, serif;
  --font-mono: IBM Plex Mono, monospace;
  --radius: 0.5rem;
  --shadow-x: 0px;
  --shadow-y: 4px;
  --shadow-blur: 8px;
  --shadow-spread: -1px;
  --shadow-opacity: 0.1;
  --shadow-color: hsl(0 0% 0%);
  --shadow-2xs: 0px 4px 8px -1px hsl(0 0% 0% / 0.05);
  --shadow-xs: 0px 4px 8px -1px hsl(0 0% 0% / 0.05);
  --shadow-sm: 0px 4px 8px -1px hsl(0 0% 0% / 0.10), 0px 1px 2px -2px hsl(0 0% 0% / 0.10);
  --shadow: 0px 4px 8px -1px hsl(0 0% 0% / 0.10), 0px 1px 2px -2px hsl(0 0% 0% / 0.10);
  --shadow-md: 0px 4px 8px -1px hsl(0 0% 0% / 0.10), 0px 2px 4px -2px hsl(0 0% 0% / 0.10);
  --shadow-lg: 0px 4px 8px -1px hsl(0 0% 0% / 0.10), 0px 4px 6px -2px hsl(0 0% 0% / 0.10);
  --shadow-xl: 0px 4px 8px -1px hsl(0 0% 0% / 0.10), 0px 8px 10px -2px hsl(0 0% 0% / 0.10);
  --shadow-2xl: 0px 4px 8px -1px hsl(0 0% 0% / 0.25);
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-popover: var(--popover);
  --color-popover-foreground: var(--popover-foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-destructive: var(--destructive);
  --color-destructive-foreground: var(--destructive-foreground);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-ring: var(--ring);
  --color-chart-1: var(--chart-1);
  --color-chart-2: var(--chart-2);
  --color-chart-3: var(--chart-3);
  --color-chart-4: var(--chart-4);
  --color-chart-5: var(--chart-5);
  --color-sidebar: var(--sidebar);
  --color-sidebar-foreground: var(--sidebar-foreground);
  --color-sidebar-primary: var(--sidebar-primary);
  --color-sidebar-primary-foreground: var(--sidebar-primary-foreground);
  --color-sidebar-accent: var(--sidebar-accent);
  --color-sidebar-accent-foreground: var(--sidebar-accent-foreground);
  --color-sidebar-border: var(--sidebar-border);
  --color-sidebar-ring: var(--sidebar-ring);

  --font-sans: var(--font-sans);
  --font-mono: var(--font-mono);
  --font-serif: var(--font-serif);

  --radius-sm: calc(var(--radius) - 4px);
  --radius-md: calc(var(--radius) - 2px);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) + 4px);

  --shadow-2xs: var(--shadow-2xs);
  --shadow-xs: var(--shadow-xs);
  --shadow-sm: var(--shadow-sm);
  --shadow: var(--shadow);
  --shadow-md: var(--shadow-md);
  --shadow-lg: var(--shadow-lg);
  --shadow-xl: var(--shadow-xl);
  --shadow-2xl: var(--shadow-2xl);
}

@layer base {
  * {
    @apply border-border outline-ring/50;
  }
  body {
    @apply bg-background text-foreground;
  }
}
"""

# ── 5. CSS → theme.py converter ──
def _css_to_theme(css_path=None):
    """
    Convert a shadcn/Tailwind CSS theme file into PywindUI's theme.py format.

    The CSS file must define CSS custom properties under :root { } (light theme)
    and .dark { } (dark theme) using the standard shadcn variable names:
      --background, --foreground, --card, --card-foreground, --primary,
      --primary-foreground, --secondary, --secondary-foreground, --muted,
      --muted-foreground, --accent, --accent-foreground, --destructive,
      --destructive-foreground, --border, --input, --ring, --popover,
      --popover-foreground, --sidebar, --sidebar-foreground,
      --sidebar-primary, --sidebar-primary-foreground, --sidebar-accent,
      --sidebar-accent-foreground, --sidebar-border, --sidebar-ring,
      --chart-1 … --chart-5

    Values may be bare hex (#rrggbb), hex with alpha (#rrggbbaa),
    or hsl(h s% l% / a) — the last three are converted to hex automatically.

    Writes the result directly into PywindUI/theme.py next to pywindui.py.
    """
    import re, colorsys

    # ── helpers ──────────────────────────────────────────────────────────

    def _hsl_to_hex(h, s, l, a=1.0):
        """Convert hsl(h, s%, l%) → #rrggbb (alpha ignored for now)."""
        r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
        return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))

    def _parse_value(raw):
        """
        Turn a CSS colour value into a plain #rrggbb hex string.
        Handles:
          #abc / #aabbcc / #aabbccdd
          hsl(210 40% 98%) / hsl(210 40% 98% / 0.5)  (space or comma separated)
          rgb(r g b) / rgb(r, g, b)
        Falls back to raw string if unrecognised.
        """
        raw = raw.strip().rstrip(";").strip()

        # Already a hex colour
        if raw.startswith("#"):
            if len(raw) == 4:                        # #abc → #aabbcc
                raw = "#" + "".join(c * 2 for c in raw[1:])
            if len(raw) == 9:                        # strip alpha byte
                raw = raw[:7]
            return raw.lower()

        # hsl(...)
        m = re.match(
            r"hsl\(\s*([\d.]+)\s+([.\d]+)%\s+([.\d]+)%"
            r"(?:\s*/\s*([\d.]+))?\s*\)",
            raw, re.I,
        )
        if m:
            h, s, l = float(m.group(1)), float(m.group(2)), float(m.group(3))
            return _hsl_to_hex(h, s, l)

        # hsl(h, s%, l%)  comma form
        m = re.match(
            r"hsl\(\s*([\d.]+),\s*([\d.]+)%,\s*([\d.]+)%"
            r"(?:,\s*([\d.]+))?\s*\)",
            raw, re.I,
        )
        if m:
            h, s, l = float(m.group(1)), float(m.group(2)), float(m.group(3))
            return _hsl_to_hex(h, s, l)

        # rgb(r g b) or rgb(r, g, b)
        m = re.match(r"rgb\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)\s*\)", raw, re.I)
        if m:
            r, g, b = int(float(m.group(1))), int(float(m.group(2))), int(float(m.group(3)))
            return "#{:02x}{:02x}{:02x}".format(r, g, b)

        return raw  # unknown — keep as-is

    # CSS var name  →  theme.py key
    _VAR_MAP = {
        "--background":                   "bg",
        "--foreground":                   "fg",
        "--card":                         "card",
        "--card-foreground":              "card_fg",
        "--popover":                      "popover",
        "--popover-foreground":           "popover_fg",
        "--primary":                      "primary",
        "--primary-foreground":           "primary_fg",
        "--secondary":                    "secondary",
        "--secondary-foreground":         "secondary_fg",
        "--muted":                        "muted",
        "--muted-foreground":             "muted_fg",
        "--accent":                       "accent",
        "--accent-foreground":            "accent_fg",
        "--destructive":                  "destructive",
        "--destructive-foreground":       "destructive_fg",
        "--border":                       "border",
        "--input":                        "input",
        "--ring":                         "ring",
        "--chart-1":                      "chart_1",
        "--chart-2":                      "chart_2",
        "--chart-3":                      "chart_3",
        "--chart-4":                      "chart_4",
        "--chart-5":                      "chart_5",
        "--sidebar":                      "sidebar",
        "--sidebar-foreground":           "sidebar_fg",
        "--sidebar-primary":              "sidebar_primary",
        "--sidebar-primary-foreground":   "sidebar_primary_fg",
        "--sidebar-accent":               "sidebar_accent",
        "--sidebar-accent-foreground":    "sidebar_accent_fg",
        "--sidebar-border":               "sidebar_border",
        "--sidebar-ring":                 "sidebar_ring",
    }

    # Keys that have no CSS equivalent — we'll carry them from the default theme
    _EXTRA_KEYS = ["bg_secondary", "success", "success_fg", "warning", "warning_fg", "black", "white"]

    # Default fallback values (dark / light) for extra keys not in CSS
    _FALLBACK = {
        "dark": {
            "bg_secondary": "#111113",
            "success":      "#22c55e",
            "success_fg":   "#ffffff",
            "warning":      "#f59e0b",
            "warning_fg":   "#ffffff",
            "black":        "#000000",
            "white":        "#ffffff",
        },
        "light": {
            "bg_secondary": "#f5f5f5",
            "success":      "#22c55e",
            "success_fg":   "#ffffff",
            "warning":      "#f59e0b",
            "warning_fg":   "#ffffff",
            "black":        "#000000",
            "white":        "#ffffff",
        },
    }

    # ── locate CSS file ───────────────────────────────────────────────────

    if css_path is None:
        candidates = [f for f in os.listdir(".") if f.endswith(".css")]
        if not candidates:
            print("No .css file found in the current directory.")
            return
        if len(candidates) > 1:
            # Prefer files with "theme" in the name
            themed = [f for f in candidates if "theme" in f.lower()]
            candidates = themed if themed else candidates
        css_path = candidates[0]

    if not os.path.exists(css_path):
        print(f"CSS file not found: {css_path}")
        return

    print(f"Reading CSS: {css_path}")

    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    # ── extract blocks ────────────────────────────────────────────────────

    def _extract_block(css, selector):
        """Return the text inside the first matching selector { } block."""
        # Match  :root { ... }  or  .dark { ... }
        pattern = re.compile(
            r"(?:^|\s)" + re.escape(selector) + r"\s*\{([^}]*)\}",
            re.DOTALL | re.MULTILINE,
        )
        m = pattern.search(css)
        return m.group(1) if m else ""

    def _parse_vars(block):
        """Return {css_var_name: hex_value} from a CSS block."""
        result = {}
        for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;]+);", block):
            var, val = m.group(1).strip(), m.group(2).strip()
            if var in _VAR_MAP:
                result[var] = _parse_value(val)
        return result

    light_block = _extract_block(css, ":root")
    dark_block  = _extract_block(css, ".dark")

    light_vars = _parse_vars(light_block)
    dark_vars  = _parse_vars(dark_block)

    # ── build theme dicts ─────────────────────────────────────────────────

    def _build_theme(vars_dict, fallback_key):
        theme = {}
        # Keys from CSS mapping
        for css_var, py_key in _VAR_MAP.items():
            if css_var in vars_dict:
                theme[py_key] = vars_dict[css_var]
        # Extra keys not in CSS
        for k in _EXTRA_KEYS:
            if k not in theme:
                theme[k] = _FALLBACK[fallback_key][k]
        return theme

    # Use dark as dark, light as light; fall back to dark for light if .dark block missing
    dark_theme  = _build_theme(dark_vars  if dark_vars  else light_vars, "dark")
    light_theme = _build_theme(light_vars if light_vars else dark_vars,  "light")

    if not dark_vars and not light_vars:
        print("Could not find :root or .dark blocks with CSS custom properties.")
        return

    # ── determine canonical key order (mirrors theme.py) ─────────────────

    _KEY_ORDER = [
        "bg", "bg_secondary", "fg",
        "card", "card_fg",
        "popover", "popover_fg",
        "primary", "primary_fg",
        "secondary", "secondary_fg",
        "muted", "muted_fg",
        "accent", "accent_fg",
        "destructive", "destructive_fg",
        "success", "success_fg",
        "warning", "warning_fg",
        "border", "input", "ring",
        "chart_1", "chart_2", "chart_3", "chart_4", "chart_5",
        "sidebar", "sidebar_fg",
        "sidebar_primary", "sidebar_primary_fg",
        "sidebar_accent", "sidebar_accent_fg",
        "sidebar_border", "sidebar_ring",
        "black", "white",
    ]

    def _dict_lines(d, indent=12):
        pad = " " * indent
        lines = []
        for k in _KEY_ORDER:
            v = d.get(k, "#000000")
            lines.append(f'{pad}"{k}":{"":>{max(1, 22 - len(k))}}"{v}",')
        return "\n".join(lines)

    # ── find widest key for static defaults alignment ─────────────────────

    def _static_lines(d, indent=4):
        pad = " " * indent
        lines = []
        for k in _KEY_ORDER:
            v = d.get(k, "#000000")
            lines.append(f'{pad}{k}:{"":>{max(1, 22 - len(k))}}str = "{v}"')
        return "\n".join(lines)

    # ── render theme.py ───────────────────────────────────────────────────

    theme_py = '''# ════════════════════════════════════════
#  COLORS  (theme-aware)
#  Auto-generated by: python pywindui.py --theme
# ════════════════════════════════════════

class Colors(str):

    _themes: dict[str, dict[str, str]] = {{

        # ── Dark ────────────────────────────
        "dark": {{
{dark_lines}
        }},

        # ── Light ───────────────────────────
        "light": {{
{light_lines}
        }},
    }}

    _current_theme: str = "dark"

    # ── Static defaults (dark) so Pylance can see them ──
{static_lines}

    # ── instance constructor ────────────
    def __new__(cls, theme: str = "dark"):
        return super().__new__(cls, theme)

    def __init__(self, theme: str = "dark"):
        if theme not in self._themes:
            raise ValueError(
                f"Unknown theme '{{theme}}'. "
                f"Available: {{list(self._themes.keys())}}"
            )
        for key, value in self._themes[theme].items():
            setattr(self, key, value)

    # ── class-level theme switch ────────
    @classmethod
    def set_theme(cls, theme: str) -> None:
        """Switch the global (class-level) color theme."""
        if theme not in cls._themes:
            raise ValueError(
                f"Unknown theme '{{theme}}'. "
                f"Available: {{list(cls._themes.keys())}}"
            )
        for key, value in cls._themes[theme].items():
            setattr(cls, key, value)
        cls._current_theme = theme

    @classmethod
    def get_theme(cls) -> str:
        """Return the name of the active global theme."""
        return cls._current_theme

    @classmethod
    def register_theme(cls, name: str, tokens: dict[str, str]) -> None:
        """Add a custom theme at runtime."""
        cls._themes[name] = tokens

def Alpha(color, Alpha=1.0):
    """opacity from 0.0 to 1.0"""
    alpha = format(int(Alpha * 255), "02x")
    return "#" + alpha + color.lstrip("#")
'''.format(
        dark_lines=_dict_lines(dark_theme),
        light_lines=_dict_lines(light_theme),
        static_lines=_static_lines(dark_theme),
    )

    # ── write output ──────────────────────────────────────────────────────

    theme_py_path = os.path.join(_here, "PywindUI", "theme.py")
    with open(theme_py_path, "w", encoding="utf-8") as f:
        f.write(theme_py)

    print(f"theme.py updated from {css_path}")
    print(f"  dark  → {len(dark_theme)} keys")
    print(f"  light → {len(light_theme)} keys")
    if not dark_vars:
        print("  (no .dark block found — used :root values for dark theme)")
    if not light_vars:
        print("  (no :root block found — used .dark values for light theme)")


# ── 5. Entry point ──
if __name__ == "__main__":

    dev_app = os.environ.get("PYWIND_APP")
    if dev_app:
        importlib.import_module(dev_app)
        from PywindUI.system import _app_instance
        _app_instance.Run(os.environ.get("PYWIND_MODE", "App"))
    else:
        # Quick commands — can appear anywhere in argv
        _commands = {"w", "--wildcard", "b", "--build", "i", "--import", "d", "--dev", "new", "t", "--theme", "ai"}
        _argv = sys.argv[1:]
        _cmd = None
        _app_arg = None

        for a in _argv:
            if a in _commands:
                _cmd = a
            elif not a.startswith("-"):
                _app_arg = a.replace(".py", "")

        def _resolve_app():
            return _app_arg or _find_app()

        if _cmd == "new":
            # python pywindui.py new theme  -> create a starter theme.css
            if _app_arg and _app_arg.lower() == "theme":
                _css_path = os.path.join(_here, "theme.css")
                if os.path.exists(_css_path):
                    print("theme.css already exists.")
                    sys.exit(1)
                with open(_css_path, "w", encoding="utf-8") as f:
                    f.write(_THEME_CSS_TEMPLATE)
                print("Created theme.css — edit it, then run: python pywindui.py t")
                sys.exit(0)

            if not _app_arg:
                print("Usage: python pywindui.py new MyApp")
                sys.exit(1)
            _path = _app_arg + ".py"
            if os.path.exists(_path):
                print(f"{_path} already exists.")
                sys.exit(1)
            with open(_path, "w") as f:
                f.write(f'from pywindui import *\n\n'
                        f'{_app_arg} = App()\n\n'
                        f'{_app_arg}("Loading",\n'
                        f'    Window(TitleBar="Custom", Theme="Light", Title="{_app_arg}", Size=(800, 600), minSize=(800, 600)),\n'
                        f')\n\n'
                        f'{_app_arg}("Design",\n'
                        f'    View(\n'
                        f'        TitleBar(Title="{_app_arg}", Logo="Outline"),\n'
                        f'        Text("Hello World!", Size=24),\n'
                        f'    )\n'
                        f')\n')
            print(f"Created {_path}")
            sys.exit(0)

        if _cmd in ("w", "--wildcard"):
            _resetimports()
            sys.exit(0)

        if _cmd in ("b", "--build"):
            _precompile()
            sys.exit(0)

        if _cmd in ("i", "--import"):
            _app_name = _resolve_app()
            if not _app_name:
                print("No app file found.")
                sys.exit(1)
            _autoimport(_app_name)
            sys.exit(0)

        if _cmd in ("ai", "--ai"):
            _app_name = _resolve_app()
            if not _app_name:
                print("No app file found.")
                sys.exit(1)
            os.environ["PYWIND_CODE_MODE"] = "1"
            importlib.import_module(_app_name)
            sys.exit(0)

        if _cmd in ("t", "--theme"):
            # Optional: pass a specific CSS file as the extra arg
            # e.g.  python pywindui.py t myTheme.css
            css_file = (_app_arg + ".css") if _app_arg else None
            _css_to_theme(css_path=css_file)
            sys.exit(0)

        if _cmd in ("d", "--dev"):
            _app_name = _resolve_app()
            if not _app_name:
                print("No app file found.")
                sys.exit(1)
            env = os.environ.copy()
            env["PYWIND_APP"] = _app_name
            env["PYWIND_MODE"] = "App"
            sys.exit(subprocess.call(
                ["flet", "run", "-r", __file__],
                env=env,
                shell=(os.name == "nt"),
            ))

        # No quick command — just run the app
        app_name = _resolve_app()

        if app_name is None:
            print("No app file found.")
            sys.exit(1)

        importlib.import_module(app_name)
        from PywindUI.system import _app_instance
        if _app_instance is None:
            print(f"No App() instance found in {app_name}.py")
            sys.exit(1)
        _app_instance.Run("App")
