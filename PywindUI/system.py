import flet as Flet
from PywindUI.theme import Colors
from PywindUI.utilities import Space
import platform
import flet as ft
import inspect
import subprocess
import json
import os
from pathlib import Path

Page: ft.Page | None = None

global AssetsRoot
AssetsRoot = "Assets"   # replaces the module-level strAssets

def StartTab(name):
    global _current_tab
    _current_tab = name

class _TabControl:
    """Single object that replaces both StartTab and Get.
    
    Usage:
        TabControl("MyTab")   # set the starting tab  (was: StartTab)
        UI(TabControl)        # pass current tab to UI (was: UI(Tab=Get()))
    """
    def __call__(self, name: str) -> None:
        global _current_tab
        _current_tab = name
 
    def get(self) -> str:
        return _current_tab
 
    def __str__(self) -> str:
        return _current_tab or ""
 
    def __repr__(self) -> str:
        return f"TabControl({_current_tab!r})"
 
TabControl = _TabControl()

_app_instance = None  # Add this line

def switch_tab(name):
    global _current_tab, Page
    _current_tab = name
    
    if Page:
        from PywindUI.utilities import _tabs, _tab_container
        content = _tabs.get(name)
        if content and _tab_container:
            _tab_container.content = content
            Page.update()
def Get():
    return _current_tab

class App():
    def __init__(self):
        global _app_instance
        _app_instance = self  # Add this line
        self._starting = []
        self._load = []
        self._ui = []
        self._ready = []
        self._closing = []
        self._functions = []

    # -------------------
    # Hook decorators
    # -------------------
    def Functions(self, func):
        self._functions.append(func)
        return func

    def Starting(self, func):
        self._starting.append(func)
        return func

    def Loading(self, func):
        self._load.append(func)
        return func

    def Design(self, func):
        self._ui.append(func)
        return func

    def Ready(self, func):
        self._ready.append(func)
        return func

    def Closing(self, func):
        self._closing.append(func)
        return func

    def _call(self, func, page):
        if inspect.signature(func).parameters:
            func(page)
        else:
            func()
    
    def __call__(self, phase, *args):
        phase = phase.lower()

        if phase == "loading":
            # args are config dicts from Window(), apply them when page exists
            configs = args
            # Apply theme RIGHT NOW so controls built after this
            # (e.g. in the "Design" phase) use the correct colors
            for c in configs:
                if isinstance(c, dict) and "Theme" in c:
                    Colors.set_theme(c["Theme"].lower())
            def _deferred(page):
                for c in configs:
                    if isinstance(c, dict):
                        Window(page=page, **c)
            self._load.append(_deferred)

        elif phase == "design":
            # Filter out None (e.g. from Tab() which only registers content)
            controls = [c for c in args if c is not None]
            def _deferred(page):
                for c in controls:
                    page.add(c)
            self._ui.append(_deferred)

        elif phase in ("starting", "ready", "closing"):
            # args should be callables (from Do() or lambda)
            hooks = {
                "starting": self._starting,
                "ready": self._ready,
                "closing": self._closing,
            }
            for a in args:
                if callable(a):
                    hooks[phase].append(a)

        elif phase == "functions":
            for a in args:
                if callable(a):
                    self._functions.append(a)


    def Run(self, mode="App"):

        # Run Starting hooks BEFORE app launches
        for func in self._starting:
            func()

        def main(page: ft.Page):

            global Page  # THIS IS THE CRITICAL LINE
            Page = page

            # Load hooks
            for func in self._load:
                self._call(func, page)

            # UI hooks (build interface)
            for func in self._ui:
                self._call(func, page)

            # Ready hooks
            for func in self._ready:
                self._call(func, page)

            # Closing hooks — only intercept if there's something to run
            if self._closing:
                async def _on_window_event(e):
                    if e.data == "close":
                        for f in self._closing:
                            f()
                        await page.window.destroy()

                page.window.on_event = _on_window_event
                page.window.prevent_close = True

        modes: dict[str, ft.AppView] = {
            "app": ft.AppView.FLET_APP,
            "website": ft.AppView.WEB_BROWSER,
            "hidden": ft.AppView.FLET_APP_HIDDEN,
        }

        View = modes.get(mode.lower())

        if View is None:
            raise ValueError("Mode must be: App, Website, or Hidden")

        ft.run(main, view=View)

def Window(page=None, Theme="Dark", minWidth=None, minHeight=None, maxWidth=None, maxHeight=None, Size=None, minSize=None, maxSize=None, Width=None, Height=None, Title="Window Title", Resizable=True, Padding=0, bgColor=None, Platform=None, TitleBar="Native"):
    global platform

    if page is None:
        page = Page
    if page is None:
        # No page yet — return config dict for deferred apply
        return {k: v for k, v in locals().items() if k != "page" and v is not None}

    # ... rest of existing Window code stays the same ...

    
    # Set platform globally if provided
    if Platform is not None:
        platform = Platform

    if Theme == "Light" or Theme == "light":
        page.theme_mode = ft.ThemeMode.LIGHT
        Colors.set_theme("light")
    elif Theme == "dark" or Theme == "Dark":
        page.theme_mode = ft.ThemeMode.DARK
        Colors.set_theme("dark")
    elif Theme == "system" or Theme == "System":
        page.theme_mode = ft.ThemeMode.SYSTEM

    if bgColor is None:
        bgColor = Colors.bg

    if TitleBar == "Native":
        page.window.title_bar_hidden = False
    elif TitleBar == "Custom":
        page.window.title_bar_hidden = True

    if minWidth is not None:
        page.window.min_width = minWidth
    if minHeight is not None:
        page.window.min_height = minHeight
    if maxWidth is not None:
        page.window.max_width = maxWidth
    if maxHeight is not None:
        page.window.max_height = maxHeight
    if minSize is not None:
        page.window.min_width, page.window.min_height = minSize
    if maxSize is not None:
        page.window.max_width, page.window.max_height = maxSize
    if Size is not None:
        page.window.width, page.window.height = Size
    if Width is not None:
        page.window.width = Width
    if Height is not None:
        page.window.height = Height
    if Title != "Window Title":
        page.title = Title
    if Resizable is not None:
        page.window.resizable = Resizable
    if Padding is not None:
        page.padding = Padding
    if bgColor is not None:
        page.bgcolor = bgColor

    """
    def Run(self, mode="App"):
        import sys, threading

        # Capture the REAL terminal streams before Flet steals them
        real_stdin = sys.stdin
        real_stdout = sys.stdout

        for func in self._starting:
            func()

        def main(page: ft.Page):
            utilities._page = page
            for func in self._load:
                self._call(func, page)
            for func in self._ui:
                self._call(func, page)
            for func in self._ready:
                self._call(func, page)
            page.on_close = lambda e: [f() for f in self._closing]

        # Start debugger thread BEFORE ft.run()
        def debugger_loop():
            real_stdout.write("\n  --  --  CLI Debugger  --  --  \n\n")
            real_stdout.write("Commands: BoxNames, BoxNum, exit\n")
            real_stdout.flush()
            while True:
                try:
                    real_stdout.write("Enter a command: ")
                    real_stdout.flush()
                    command = real_stdin.readline().strip()
                except (EOFError, OSError):
                    break
                if command == "BoxNames":
                    real_stdout.write("(BoxNames not yet implemented)\n")
                elif command == "BoxNum":
                    real_stdout.write(f"BoxNum: {utilities.boxNum}\n")
                elif command in ("exit", "quit"):
                    break
                else:
                    real_stdout.write("Unknown command.\n")
                real_stdout.flush()

        threading.Thread(target=debugger_loop, daemon=True).start()

        modes = {
            "app": ft.AppView.FLET_APP,
            "website": ft.AppView.WEB_BROWSER,
            "hidden": ft.AppView.FLET_APP_HIDDEN,
        }
        View = modes.get(mode.lower())
        if View is None:
            raise ValueError("Mode must be: App, Website, or Hidden")
        ft.run(main, view=View)

    """
def Theme():
    global Page, _app_instance
    
    if Page is None or _app_instance is None:
        return
    
    if Colors.get_theme() == "dark":
        Colors.set_theme("light")
    else:
        Colors.set_theme("dark")

    Page.bgcolor = Colors.bg
    Page.clean()
    for func in _app_instance._ui:
        if inspect.signature(func).parameters:
            func(Page)
        else:
            func()
    Page.update()

def Database(Name="Accounts", Dir=""):
    return Database()

def Terminal(Shell=True, Capture=True, OS=None,Command="",Visible=True):

    if not Command:
        return None
    if OS is None:
        OS = platform
    # Determine OS (use provided or auto-detect)
    if OS:
        system = OS.platform.lower()
        if system in ["win", "windows"]:
            system = "windows"
        elif system in ["mac", "macos", "darwin"]:
            system = "darwin"
        elif system in ["linux", "unix"]:
            system = "linux"
    else:
        system = platform.system().lower()

    # Platform-specific visible terminal handling
    if Visible:
        if system == "windows":
            if Capture:
                result = subprocess.run(Command, shell=Shell, capture_output=True, text=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
                return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
            else:
                result = subprocess.run(Command, shell=Shell, creationflags=subprocess.CREATE_NEW_CONSOLE)
                return result.returncode
        elif system == "darwin":
            terminal_cmd = f'tell application "Terminal" to do script "{Command}"'
            subprocess.run(["osascript", "-e", terminal_cmd])
            return 0
        else:
            terminals = ["gnome-terminal", "konsole", "xterm"]
            for term in terminals:
                try:
                    subprocess.run([term, "-e", Command])
                    return 0
                except FileNotFoundError:
                    continue

    # Hidden execution (default)
    if Capture:
        result = subprocess.run(Command, shell=Shell, capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    else:
        result = subprocess.run(Command, shell=Shell)
        return result.returncode

def Term(Command,Mode=None, Shell=True, Capture=True, OS=None,Visible=True):
    if Mode == "Immediate":
        if OS is None:
            OS = platform
        return Terminal(Command=Command, Shell=Shell, Capture=Capture, Visible=Visible, OS=OS)
    elif Mode == "Click":
        if OS is None:
            OS = platform
        return lambda e: Terminal(Command=Command, Shell=Shell, Capture=Capture, Visible=Visible, OS=OS)
    else:
        raise ValueError("Mode must be: Immediate or Background")

def Do(func, *args, **kwargs):
    return lambda: func(*args, **kwargs)


def Date(str):
    if str == "Raw":
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d")
    elif str == "Lined":
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
    elif str == "Scored":
        from datetime import datetime
        return datetime.now().strftime("%Y_%m_%d")
    elif str == "LinedWithTime":
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elif str == "ScoredWithTime":
        from datetime import datetime
        return datetime.now().strftime("%Y_%m_%d %H:%M:%S")
    elif str == "RawWithTime":
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d%H%M%S")

def Cacher(str, Name="Cache", Pretext=None):
    if Pretext is None:
        Pretext = ""
    elif Pretext is not None:
        Pretext = Pretext

    def _click(e=None):
        pre = Pretext() if callable(Pretext) else Pretext
        print(f"{pre}_{str}_{Name}")
    return _click


# ── Files: named path registry ──────────────────────────────
# Built-in names: "Assets" (base) plus "Scripts"/"Images"/"Fonts" which live
# under it and follow it automatically. Override any of them, or add your own,
# with Files(Name="X", Dir="...").
_DERIVED = {"Scripts": "Scripts", "Images": "Images", "Fonts": "Fonts"}
_paths = {}   # dev overrides + custom registered names

def _resolve(name) -> str:
    if name in _paths:              # override or custom name
        return _paths[name]
    if name == "Assets":
        return AssetsRoot
    if name in _DERIVED:            # derived: follows AssetsRoot
        return f"{AssetsRoot}/{_DERIVED[name]}"
    known = list(dict.fromkeys(["Assets", *_DERIVED, *_paths]))
    raise ValueError(f"Files(): unknown name {name!r}. Known: {known}")

def Files(Use="Assets", Name=None, Dir=None, Change=None, Asset="", Type="", *args) -> Path:
    global AssetsRoot

    # Register / override a name:
    #   Files(Name="Assets", Dir="assets/Downloadr")   # move the base (derived follow)
    #   Files(Name="Music",  Dir="C:/Users/igotl/Music")
    if Name:
        if Dir is None:
            raise ValueError(f"Files(Name={Name!r}) requires Dir=")
        if Name == "Assets":
            AssetsRoot = Dir
        else:
            _paths[Name] = Dir
        return Path(_resolve(Name))

    # Alias for Files(Name="Assets", Dir=Change)
    if Change:
        AssetsRoot = Change
        return Path(AssetsRoot)

    base = _resolve(Use)
    sub = Asset.strip("/\\")      # accepts "/sub" or "sub"

    # Scripts always resolve to .py files
    if Use == "Scripts" and sub:
        return Path(f"{base}/{sub}.py")

    # Extension — only for a real Type (not empty, not "Folder")
    dotType = ""
    if Type and Type != "Folder":
        dotType = Type if Type.startswith(".") else f".{Type}"

    return Path(f"{base}/{sub}{dotType}") if sub else Path(base)

def LoadingTab(Text="Loading...", Name="LoadingTab", RingSize=78, RingWidth=4, Color=Colors.primary, Gap=Space.lg):
    """Prebuilt tab: a centered progress ring with one line of text."""
    from PywindUI.utilities import Tab, xyBox, Spacer, Space
    from PywindUI.components import Text as _Text

    Tab(
        xyBox(
            ft.ProgressRing(width=RingSize, height=RingSize, stroke_width=RingWidth,
                            color=Color or Colors.primary),
            Spacer(Gap, Direction="Vertical"),
            _Text(Text, Size=14, Color=Colors.muted_fg),

            Align="Center",
        ),
        TabName=Name,
    )
def MessageTab(Text="Loading...", Name="MessageTab"):
    """Prebuilt tab: a centered progress ring with one line of text."""
    from PywindUI.utilities import Tab, xyBox, Spacer, Space
    from PywindUI.components import Text as _Text

    Tab(
        xyBox(

        ),
        TabName=Name,
    )

def EasyTab(Variant="Loading" ,Text="Downloading...", RingSize=78, RingWidth=4, Color=Colors.primary, Gap=Space.lg, Name="EasyTab"):
    if(Variant == "Loading"):
        LoadingTab(Text, Name, RingSize=RingSize, RingWidth=RingWidth, Color=Color, Gap=Gap)
    elif(Variant == "Message"):
        MessageTab(Text, Name)
