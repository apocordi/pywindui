"""TinyTail - Modern Python UI Framework"""
import flet as ft
from PywindUI.theme import Colors
import os

from typing import Any, Optional

# AI Imports =============================

import anthropic
from anthropic.types import TextBlock
# ════════════════════════════════════════
#  SPACING
# ════════════════════════════════════════

class Space:
    null = 0
    one = 1
    xxs = 2
    xs = 4
    sm = 8
    md = 16
    lg = 24
    xl = 32
    xxl = 48

# ════════════════════════════════════════
#  Size
# ════════════════════════════════════════

class Size:
    one = 1
    xxs = 2
    xs = 4
    sm = 8
    md = 16
    lg = 24
    xl = 32

class Weight:
    one = ft.FontWeight.W_200
    xxs = ft.FontWeight.W_300
    xs = ft.FontWeight.W_400
    sm = ft.FontWeight.W_500
    md = ft.FontWeight.W_600
    lg = ft.FontWeight.W_700
    xl = ft.FontWeight.W_800

# ════════════════════════════════════════
#  RADIUS
# ════════════════════════════════════════

class Radius:
    null = 0
    sm = 4
    md = 8
    lg = 12
    full = 999

# ════════════════════════════════════════
#  UTILITIES
# ════════════════════════════════════════

class Name:
    """A forward reference to a control. Assign with Name=... on a component,
    then use it anywhere — even before the control is created.
 
    Any attribute you set is forwarded to the underlying Flet control:
 
        MyField.hint_text = "V"      # instead of MyField.control.hint_text = "V"
        MyField.value     = "3.3"
        MyField.update()
 
    Attributes set *before* the control exists are queued and flushed the
    moment the component binds itself, so ordering never matters.
 
    `Data` is Name-owned storage that is NOT forwarded. Components that hold a
    value which isn't a Flet control attribute (Select) write there.
    """
 
    # Attributes that live on the Name itself and are never proxied.
    _own = ("control", "_pending", "Data")

    control: Any
    Data: Any
    _pending: dict
 
    def __init__(self, Data=None):
        object.__setattr__(self, "control", None)
        object.__setattr__(self, "_pending", {})
        object.__setattr__(self, "Data", Data)
 
    def __setattr__(self, key, val):
        if key in Name._own:
            object.__setattr__(self, key, val)
            # Binding a control flushes anything queued before it existed.
            if key == "control" and val is not None:
                pending = object.__getattribute__(self, "_pending")
                for k, v in pending.items():
                    setattr(val, k, v)
                pending.clear()
            return
 
        ctrl = object.__getattribute__(self, "control")
        if ctrl is None:
            object.__getattribute__(self, "_pending")[key] = val
        else:
            setattr(ctrl, key, val)
 
    def __getattr__(self, key):
        # Only reached when normal lookup fails, so `control`/`Data`/`update`
        # never land here.
        if key.startswith("__"):
            raise AttributeError(key)
 
        pending = object.__getattribute__(self, "_pending")
        if key in pending:
            return pending[key]
 
        ctrl = object.__getattribute__(self, "control")
        if ctrl is None:
            # `.value` stays forgiving (returns None) for backwards
            # compatibility; anything else raises so typos aren't silent.
            if key == "value":
                return None
            raise AttributeError(
                f"Name has no control bound yet — cannot read '{key}'. "
                f"Did you forget Name=... on the component?"
            )
        return getattr(ctrl, key)
 
    def update(self):
        ctrl = object.__getattribute__(self, "control")
        if ctrl is not None:
            ctrl.update()
 
    def __repr__(self):
        ctrl = object.__getattribute__(self, "control")
        data = object.__getattribute__(self, "Data")
        return f"<Name bound={ctrl is not None} Data={data!r}>"


#def AutoWidth(rootWidth):
#    return rootWidth - (OtherComp + Gap)

def onePrint(Txt: str) -> None:
    int = 0
    if int != 1:
        print(Txt)
        int = 1
        return

def xBox(*children, **kwargs):
    """Box preset to Direction="Horizontal". Same params as Box (minus Direction)."""
    kwargs["Direction"] = "Horizontal"
    return Box(*children, **kwargs)

def yBox(*children, **kwargs):
    """Box preset to Direction="Vertical". Same params as Box (minus Direction)."""
    kwargs["Direction"] = "Vertical"
    return Box(*children, **kwargs)

def Box(*children, Direction="Vertical", Align=None, Gap=0,
        Padding=None, bgColor=None, Border=None, borderColor=Colors.border,
        Radius=None, Height=None, Width=None, Fill=False, Opacity=1.0,
        Animate=False, onClick=None, scroll=False, Name=""):
    
    # If any child is a Spacer, handle gaps manually
    has_spacer = any(
        c is not None and hasattr(c, 'data') and isinstance(c.data, dict) and c.data.get("_spacer")
        for c in children
    )

    effective_gap = Gap
    if has_spacer and Gap > 0:
        effective_gap = 0
        spaced = []
        filtered = [c for c in children if c is not None]
        for i, child in enumerate(filtered):
            is_spacer = hasattr(child, 'data') and isinstance(child.data, dict) and child.data.get("_spacer")
            
            if i > 0 and not is_spacer:
                prev = filtered[i - 1]
                prev_is_spacer = hasattr(prev, 'data') and isinstance(prev.data, dict) and prev.data.get("_spacer")
                if not prev_is_spacer:
                    # Inject parent gap between two non-spacer children
                    if Direction in ("Vertical", "Floating"):
                        spaced.append(ft.Container(height=Gap, width=0))
                    else:
                        spaced.append(ft.Container(width=Gap, height=0))
            
            spaced.append(child)
        children = spaced
    
    # ... rest of Box unchanged, but use effective_gap instead of Gap for spacing=

    global boxNum

    align_map = {
        "Start":   ft.MainAxisAlignment.START,
        "Center":  ft.MainAxisAlignment.CENTER,
        "End":     ft.MainAxisAlignment.END,
        "Between": ft.MainAxisAlignment.SPACE_BETWEEN,
        "Around":  ft.MainAxisAlignment.SPACE_AROUND,
        "Evenly":  ft.MainAxisAlignment.SPACE_EVENLY,
    }

    main_align = align_map.get(Align, ft.MainAxisAlignment.START) if Align else ft.MainAxisAlignment.START
    if Direction == "Horizontal":
        should_expand = Fill
    else:
        should_expand = Fill or (Align is not None and Align != "Start")

    # Shrink-wrap unless the caller explicitly wants this Box to spread out
    tight = not (Fill or (Align is not None and Align != "Start"))

    if Direction == "Horizontal":
        layout = ft.Row(
            controls=list(children),
            spacing=effective_gap,
            alignment=main_align,
            expand=should_expand,
            tight=tight,
        )
    elif Direction == "Floating":
        layout = ft.Stack(
            controls=list(children),
            expand=should_expand,
        )
    elif Direction == "Vertical":
        layout = ft.Column(
            controls=list(children),
            spacing=effective_gap,
            alignment=main_align,
            expand=should_expand,
            tight=tight,
            scroll=ft.ScrollMode.AUTO if scroll else None,
        )

    has_visual = any([Padding, bgColor, Border, Radius, Height, Width, onClick, Animate]) or Opacity != 1.0

    if not has_visual:
        return layout

    return ft.Container(
        content=layout,
        padding=Padding,
        bgcolor=bgColor,
        border=ft.border.all(1, borderColor) if Border else None,
        border_radius=Radius,
        height=Height,
        width=Width,
        expand=should_expand,
        opacity=Opacity,
        animate=ft.Animation(200) if Animate else None,
        on_click=onClick,
    )

def xyBox(*children, Align="", xAlign=None, yAlign=None, Gap=0, Width=None, Height=None, Fill=True, Scroll=False, Name=""):
    x = xAlign or Align
    y = yAlign or Align

    main_map = {
        "Center": ft.MainAxisAlignment.CENTER,
        "Start":  ft.MainAxisAlignment.START,
        "End":    ft.MainAxisAlignment.END,
    }
    cross_map = {
        "Center": ft.CrossAxisAlignment.CENTER,
        "Start":  ft.CrossAxisAlignment.START,
        "End":    ft.CrossAxisAlignment.END,
    }
    container_align = {
        ("Start", "Start"):   ft.Alignment.TOP_LEFT,
        ("Center", "Start"):  ft.Alignment.TOP_CENTER,
        ("End", "Start"):     ft.Alignment.TOP_RIGHT,
        ("Start", "Center"):  ft.Alignment.CENTER_LEFT,
        ("Center", "Center"): ft.Alignment.CENTER,
        ("End", "Center"):    ft.Alignment.CENTER_RIGHT,
        ("Start", "End"):     ft.Alignment.BOTTOM_LEFT,
        ("Center", "End"):    ft.Alignment.BOTTOM_CENTER,
        ("End", "End"):       ft.Alignment.BOTTOM_RIGHT,
    }

    shouldExpand = Fill and Width is None

    return ft.Container(
        content=ft.Column(
            controls=list(children),
            spacing=Gap,
            alignment=main_map.get(y, ft.MainAxisAlignment.CENTER),
            horizontal_alignment=cross_map.get(x, ft.CrossAxisAlignment.CENTER),
            expand=shouldExpand,
            scroll=ft.ScrollMode.AUTO if Scroll else None,
        ),
        alignment=container_align.get((x, y), ft.Alignment.CENTER),
        width=Width,
        height=Height,
        expand=shouldExpand,
    )

"""
def Stack(*children, Gap=Spacing.null, Fill=True, scroll=False, Height=None, Width=None):
    return ft.Column(
        controls=list(children),
        spacing=Gap,
        expand=Fill,
        scroll=ft.ScrollMode.AUTO if scroll else None,
        height=Height,
        width=Width,
    )


def Row(*children, Gap=Spacing.null, Fix=False, Height=None, Width=None, Alignment="start"):
    return ft.Row(
        controls=list(children),
        spacing=Gap,
        expand=Fix,
        height=Height,
        width=Width,
        alignment=ft.MainAxisAlignment(Alignment),
    )
"""
# Tag spacers so Box can recognize them
def Spacer(Space, Direction):
    if Space == "Between":
        if Direction == "Vertical":
            c = ft.Container(expand=True, width=0)
        else:
            c = ft.Container(expand=True, height=0)
        c.data = {"_spacer": True, "space": Space, "direction": Direction}
        return c
    elif Space is not None:
        if Direction == "Vertical":
            c = ft.Container(height=Space, width=0)
        else:
            c = ft.Container(width=Space, height=0)
        c.data = {"_spacer": True, "space": Space, "direction": Direction}
        return c
    return None

        
def Pads(x=0, y=0):
    return ft.Padding.symmetric(horizontal=x, vertical=y)

def Pad(value):
    return ft.Padding.all(value)

# Tab system storage
_tabs: dict = {}

def clear_tabs():
    global _tabs
    _tabs.clear()
_tab_container = None

def Tab(*children, TabName="Default"):
    """Register a tab's content"""
    from PywindUI.utilities import Box
    _tabs[TabName] = Box(*children, Fill=True)

def TabView(Tab=None):
    """Return the content for a specific tab.
    Accepts a tab name string, a TabControl instance, or nothing (uses current tab).
    """
    from PywindUI.system import Get
    global _tab_container
 
    if Tab is None:
        tab_name = Get()
    elif isinstance(Tab, str):
        tab_name = Tab
    else:
        # TabControl instance (or any object with .get())
        tab_name = Tab.get()
    content = _tabs.get(tab_name)
    
    if content is None:
        return ft.Text(f"Tab '{tab_name}' not found")
    
    _tab_container = ft.Container(content=content, expand=True)
    return _tab_container

def View(*children):
    from PywindUI.system import Page
    col = ft.Column(controls=list(children), expand=True, spacing=0, tight=True)
    if Page is None:
        return col
    Page.add(col)




"""
def text(value, size=14, color=Colors.primary, weight=ft.FontWeight.NORMAL):
    return ft.Text(str(value), size=size, color=color, weight=weight)

def heading(value, level=1):
    sizes = {1: 32, 2: 24, 3: 20, 4: 16}
    return ft.Text(value, size=sizes.get(level, 32), weight=ft.FontWeight.BOLD, color=Colors.primary)

def divider(color=Colors.border):
    return ft.Divider(color=color, height=1)

"""

# ── Clipboard ──────────────────────────────────────────────

async def Paste():
    """Return the clipboard's text (empty string if nothing / no page)."""
    from PywindUI.system import Page
    if Page is None:
        return ""
    return await ft.Clipboard().get() or ""

async def Copy(Text=""):
    """Put text on the clipboard."""
    from PywindUI.system import Page
    if Page is None:
        return
    await ft.Clipboard().set(str(Text))

def CopyFrom(Control):
    """Click handler: copy a Textbox's current value to the clipboard."""
    async def _copy(e=None):
        await Copy(Control.value)
    return _copy

def PasteTo(Control):
    """Click handler: paste clipboard text into a Textbox and refresh it."""
    async def _paste(e=None):
        Control.value = await Paste()
        Control.update()
    return _paste

# ── Url/Link Handling ──────────────────────────────────────────────
def Url(url):
    from PywindUI.system import Page  # Late import inside function
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    
    if Page is not None:
        Page.run_task(Page.url_launcher.launch_url, url)
        return lambda e: e.page.run_task(e.page.url_launcher.launch_url, url)
    
    return lambda e: e.page.run_task(e.page.url_launcher.launch_url, url)

# ── Code Assistant ──────────────────────────────────────────────
def AI(*funcs):
    if not os.environ.get("PYWIND_CODE_MODE"):
        return
    for f in funcs:
        f()

def API(key, Name="API Provider"):
    def _apply():
        if key is not None:
            if Name == "OpenAI":
                os.environ["OPENAI_API_KEY"] = key
            elif Name == "Anthropic":
                os.environ["ANTHROPIC_API_KEY"] = key
        else:
            print(f"No {Name} is set")
    return _apply

def SaveChat():
    return 0

def Create(str, File="", LearnFramework=True, Effort="low"):
    def _run():
        client = anthropic.Anthropic()

        print("Thinking...")

        if LearnFramework:
            PywindUI = open(".../pywindui.py").read()
            pywinduiUtilities = open("utilities.py").read()
            pywinduiTheme = open("theme.py").read()
            pywinduiSystem = open("system.py").read()
            pywinduiComponents = open("components.py").read()
            preMessage = "You are a PywindUI/Flet/Python programming expert." + "\n" + "PywindUI Utilities:" + "\n" + pywinduiUtilities + "\n" + "PywindUI Theme:" + "\n" + pywinduiTheme + "\n" + "PywindUI System:" + "\n" + pywinduiSystem + "\n" + "PywindUI Components:" + "\n" + pywinduiComponents + "\n" + "PywindUI Starter File:" + "\n" + PywindUI + "\n" + "This is the current code im working on: "
        else:
            preMessage = "You are a PywindUI/Flet/Python programming expert." + "This is the current code im working on: "
        fileName = open(File)
        curFile = fileName.read()
        fullPrompt = preMessage + "\n\n" + curFile + "\n\n" + "Question: " + "\n" + str + "\n\n" + "How you should answer question: " + "\n" + "Give the answer as a multi line comment right under where ever the Question function/line is located(if indented keep indent in mind)" + "\n\n" + "Your actual Raw answer(FULL answer): This should include FULL file content just with that inserted comment since there will be done a raw full clear paste operation" + "\n\n" + "Important: Do NOT ever put comma after AI()"

        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=4096,
            output_config={"effort": "high"},
            messages=[{"role": "user", "content": fullPrompt}],
        )
        answer = next((b.text for b in response.content if isinstance(b, TextBlock)), "")

        lines = answer.strip().splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        answer = "\n".join(lines)

        if answer:
            try:
                compile(answer, File, "exec")
            except SyntaxError as e:
                print(f"Skipped write — model output isn't valid Python: {e}")
            else:
                with open(File, "w") as f:
                    f.write(answer)
                print("Answered!")
            
    return _run


def Question(str, File="", LearnFramework=True, Effort="low", InPDF=False, MaxTokens=2048):
    if InPDF == True:
        return 0
    elif InPDF == False:
        def _run():
            client = anthropic.Anthropic()

            print("Thinking...")

            if LearnFramework:
                from pathlib import Path

                
                PywindUI = (Path(__file__).parent.parent / "pywindui.py").read_text(encoding="utf-8")

                pywinduiUtilities = (
                    Path(__file__).parent.parent / "PywindUI" / "utilities.py"
                ).read_text(encoding="utf-8")

                pywinduiTheme = (
                    Path(__file__).parent.parent / "PywindUI" / "theme.py"
                ).read_text(encoding="utf-8")

                pywinduiSystem = (
                    Path(__file__).parent.parent / "PywindUI" / "system.py"
                ).read_text(encoding="utf-8")
                
                pywinduiComponents = (
                    Path(__file__).parent.parent / "PywindUI" / "components.py"
                ).read_text(encoding="utf-8")

                preMessage = "You are a PywindUI/Flet/Python programming expert." + "\n" + "PywindUI Utilities:" + "\n" + pywinduiUtilities + "\n" + "PywindUI Theme:" + "\n" + pywinduiTheme + "\n" + "PywindUI System:" + "\n" + pywinduiSystem + "\n" + "PywindUI Components:" + "\n" + pywinduiComponents + "\n" + "PywindUI Starter File:" + "\n" + PywindUI + "\n" + "This is the current code im working on: "
            else:
                preMessage = "You are a PywindUI/Flet/Python programming expert." + "This is the current code im working on: "
            fileName = open(File)
            curFile = fileName.read()
            fullPrompt = preMessage + "\n\n" + curFile + "\n\n" + "Question: " + "\n" + str + "\n\n" + "How you should answer question: " + "\n" + "Give the answer as a str within a Answer(actual answer) function(from utilities) right under where ever the Question function/line is located(if indented keep indent in mind) reply like this" + "\n\n" + "Your actual Raw answer(FULL answer): This should include FULL file content just with that inserted Answer function since there will be done a raw full clear paste operation" + "\n\n" + "Important: Keep answer short. Answer shall not be comment but an actual str inside a Answer() function(multiline if you can). Answer shall be inside AI function under Question. If Question() function does not have comma add one!. Do NOT ever put comma after AI()"

            response = client.messages.create(
                model="claude-sonnet-5",
                max_tokens=MaxTokens,
                output_config={"effort": Effort},
                messages=[{"role": "user", "content": fullPrompt}],
            )
            answer = next((b.text for b in response.content if isinstance(b, TextBlock)), "")

            lines = answer.strip().splitlines()
            if lines and lines[0].strip().startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            answer = "\n".join(lines)

            if answer:
                print(answer)
                with open(File, "w") as f:
                    f.write(answer)
                print("Answered!")
                
        return _run

def Fix(str, File=""):
    return 0

def Edit(str, File="", LearnFramework=True, Effort="low"):
    def _run():
        client = anthropic.Anthropic()

        print("Thinking...")

        if LearnFramework:
            PywindUI = open(".../pywindui.py").read()
            pywinduiUtilities = open("utilities.py").read()
            pywinduiTheme = open("theme.py").read()
            pywinduiSystem = open("system.py").read()
            pywinduiComponents = open("components.py").read()
            preMessage = "You are a PywindUI/Flet/Python programming expert." + "\n" + "PywindUI Utilities:" + "\n" + pywinduiUtilities + "\n" + "PywindUI Theme:" + "\n" + pywinduiTheme + "\n" + "PywindUI System:" + "\n" + pywinduiSystem + "\n" + "PywindUI Components:" + "\n" + pywinduiComponents + "\n" + "PywindUI Starter File:" + "\n" + PywindUI + "\n" + "This is the current code im working on: "
        else:
            preMessage = "You are a PywindUI/Flet/Python programming expert." + "This is the current code im working on: "
        fileName = open(File)
        curFile = fileName.read()
        fullPrompt = preMessage + "\n\n" + curFile + "\n\n" + "Question: " + "\n" + str + "\n\n" + "How you should answer question: " + "\n" + "Give the answer as a str within a Answer(actual answer) function(from utilities) right under where ever the Question function/line is located(if indented keep indent in mind) reply like this" + "\n" + "Answer(" + "\n" + "    """ + "\n" + ")" "\n\n" + "Your actual Raw answer(FULL answer): This should include FULL file content just with that inserted Answer function since there will be done a raw full clear paste operation" + "\n\n" + "Important: Keep answer short(comment should max be 4000 characters). Answer shall not be comment but an actual str inside a Answer() function. Do NOT ever put comma after AI()"

        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=4096,
            output_config={"effort": "high"},
            messages=[{"role": "user", "content": fullPrompt}],
        )
        answer = next((b.text for b in response.content if isinstance(b, TextBlock)), "")

        lines = answer.strip().splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        answer = "\n".join(lines)

        if answer:
            print(answer)
            with open(File, "w") as f:
                f.write(answer)
            print("Answered!")
            
    return _run


def Answer(str, File="", Source=""):
    print(str)



    
#  Native Control Systems
# ════════════════════════════════════════

# Cursor Mapping
class Cursors:
    hand = ft.MouseCursor.CLICK
    pointer = ft.MouseCursor.CLICK
    text = ft.MouseCursor.TEXT
    move = ft.MouseCursor.MOVE
    grab = ft.MouseCursor.GRAB
    grabbing = ft.MouseCursor.GRABBING
    forbidden = ft.MouseCursor.FORBIDDEN
    crosshair = ft.MouseCursor.PRECISE
    wait = ft.MouseCursor.WAIT
    default = ft.MouseCursor.BASIC
