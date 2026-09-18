from flet.canvas import Fill

import asyncio  # top of components.py
from PywindUI.utilities import Space, Cursors, Radius, Box, xyBox, Pads, Weight
from PywindUI.theme import Colors, Alpha
from typing import overload, Literal
import inspect
import math
import flet as ft
import flet_charts as fch

def _wrap(control, fill):
    if fill:
        control.expand = True  # Button expands inside the Row
        return ft.Row(controls=[control], expand=True)  # Row expands in parent
    return control

def Click(e):
    pass

def _normalize_handler(fn):
    """Wrap a user handler so it can always be called as fn(e), sync or async."""
    if fn is None:
        return None
    takes_event = bool(inspect.signature(fn).parameters)
    if inspect.iscoroutinefunction(fn):
        if takes_event:
            return fn
        async def _async_wrapper(e):
            await fn()
        return _async_wrapper
    if takes_event:
        return fn
    return lambda e: fn()

def _combine_handlers(handlers):
    handlers = [h for h in handlers if h is not None]
    if not handlers:
        return lambda e: None
    if len(handlers) == 1:
        return handlers[0]
    async def _run(e):
        for h in handlers:
            result = h(e)
            if inspect.isawaitable(result):
                await result
            await asyncio.sleep(0)  # let flet flush the UI between handlers
    return _run

def Button(Text="Button", Icons=None, Icon=None, IconSize=18, Click=None, Height=30, Width=None, Fill=False, Cursor=Cursors.hand, Variant="Primary", Gap=Space.sm, Padding=Pads(Space.md, 0), Radius=Radius.md, Goto=None, FgColor=None, Dropdown=False, DropdownMenu=None, FuncOrder=("Goto", "Click")):

    # Dropdown mode — return a MenuBar wrapping a SubmenuButton styled like this Button
    if Dropdown and DropdownMenu:
        return _BuildDropdownButton(
            Text=Text, Icons=Icons, Icon=Icon, IconSize=IconSize, Height=Height,
            Width=Width, Fill=Fill, Cursor=Cursor, Variant=Variant, Gap=Gap,
            Padding=Padding, TriggerRadius=Radius, FgColor=FgColor, MenuName=DropdownMenu,
        )

    if Icon:
        Icon = Icon.strip().replace(" ", "_").replace("-", "_")    

    # Build on_click from Click and/or Goto, in FuncOrder (default: Goto first).
    # FuncOrder accepts a tuple/list like ("Click", "Goto") or a string like "Click, Goto".
    goto_handler = None
    if Goto:
        from PywindUI.system import switch_tab
        goto_handler = lambda e, _g=Goto: switch_tab(_g)
    click_handler = _normalize_handler(Click)

    if isinstance(FuncOrder, str):
        FuncOrder = [part.strip() for part in FuncOrder.split(",")]
    handlers = []
    for name in FuncOrder:
        if name.lower() == "goto":
            handlers.append(goto_handler)
        elif name.lower() == "click":
            handlers.append(click_handler)
    Click = _combine_handlers(handlers)

    if Variant == "Primary":
        bgColor = Colors.primary
        fgColor = FgColor if FgColor is not None else Colors.primary_fg

        iconName = None
        if Icon:
            if Icons == "Rounded" or Icons == "rounded":
                iconName = Icon + "_ROUNDED"
            elif Icons == "Sharp" or Icons == "sharp":
                iconName = Icon + "_SHARP"
            else:
                iconName = Icon

        if not Text and iconName:
            return ft.IconButton(
                icon=getattr(ft.Icons, iconName.upper()),
                icon_size=IconSize,
                icon_color=fgColor,
                width=Width,
                height=Height,
                on_click=Click,
                style=ft.ButtonStyle(
                    overlay_color=Alpha(Colors.primary_fg, 0),
                    shape=ft.RoundedRectangleBorder(radius=Radius),
                    padding=0,
                    mouse_cursor=Cursor,
                    bgcolor={
                        ft.ControlState.HOVERED: Alpha(Colors.primary, 0.9),
                        ft.ControlState.DEFAULT: bgColor,
                    },
                ),
            )

        btnContent = []
        if iconName:
            btnContent.append(ft.Icon(getattr(ft.Icons, iconName.upper()), size=IconSize, color=fgColor))
        if Text:
            btnContent.append(ft.Text(Text, color=fgColor))

        btn = ft.Button(
            width=Width,
            height=Height,
            color=fgColor,
            content=ft.Row(
                controls=btnContent,
                spacing=Gap if Text else 0,
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            on_click=Click,
            style=ft.ButtonStyle(
                elevation=0,
                shadow_color=ft.Colors.TRANSPARENT,
                overlay_color=Alpha(Colors.primary_fg, 0),
                shape=ft.RoundedRectangleBorder(radius=Radius),
                mouse_cursor=Cursor,
                bgcolor={
                    ft.ControlState.HOVERED: Alpha(Colors.primary, 0.9),
                    ft.ControlState.DEFAULT: bgColor,
                },
                padding=Padding,
            ),
        )
        return _wrap(btn, Fill)

    elif Variant == "Destructive":
            bgColor = Colors.destructive
            fgColor = FgColor if FgColor is not None else Colors.destructive_fg

            iconName = None
            if Icon:
                if Icons == "Rounded" or Icons == "rounded":
                    iconName = Icon + "_ROUNDED"
                elif Icons == "Sharp" or Icons == "sharp":
                    iconName = Icon + "_SHARP"
                else:
                    iconName = Icon

            if not Text and iconName:
                return ft.IconButton(
                    icon=getattr(ft.Icons, iconName.upper()),
                    icon_size=IconSize,
                    icon_color=fgColor,
                    width=Width,
                    height=Height,
                    on_click=Click,
                    style=ft.ButtonStyle(
                        overlay_color=Alpha(Colors.destructive_fg, 0),
                        shape=ft.RoundedRectangleBorder(radius=Radius),
                        padding=0,
                        mouse_cursor=Cursor,
                        bgcolor={
                            ft.ControlState.HOVERED: Alpha(Colors.destructive, 0.9),
                            ft.ControlState.DEFAULT: bgColor,
                        },
                    ),
                )

            btnContent = []
            if iconName:
                btnContent.append(ft.Icon(getattr(ft.Icons, iconName.upper()), size=IconSize, color=fgColor))
            if Text:
                btnContent.append(ft.Text(Text, color=fgColor))

            btn = ft.Button(
                width=Width,
                height=Height,
                color=fgColor,
                content=ft.Row(
                    controls=btnContent,
                    spacing=Gap if Text else 0,
                    alignment=ft.MainAxisAlignment.CENTER,
                    tight=True,
                ),
                on_click=Click,
                style=ft.ButtonStyle(
                    elevation=0,
                    shadow_color=ft.Colors.TRANSPARENT,
                    overlay_color=Alpha(Colors.destructive_fg, 0),
                    shape=ft.RoundedRectangleBorder(radius=Radius),
                    mouse_cursor=Cursor,
                    bgcolor={
                        ft.ControlState.HOVERED: Alpha(Colors.destructive, 0.9),
                        ft.ControlState.DEFAULT: bgColor,
                    },
                    padding=Padding,
                ),
            )
            return _wrap(btn, Fill)

    elif Variant == "Outline":
        # Transparent by default — Material's hover bgcolor is the only filled
        # state. This lets the button blend with whatever's behind it.
        bgColor = ft.Colors.TRANSPARENT
        # Use Colors.fg, not secondary_fg. secondary_fg is the on-secondary-bg
        # text colour, which on custom themes (where secondary != bg) reads as
        # muted on a transparent button.
        fgColor = FgColor if FgColor is not None else Colors.fg
        borderColor = Colors.border

        iconName = None
        if Icon:
            if Icons == "Rounded" or Icons == "rounded":
                iconName = Icon + "_ROUNDED"
            elif Icons == "Sharp" or Icons == "sharp":
                iconName = Icon + "_SHARP"
            else:
                iconName = Icon

        if not Text and iconName:
            return ft.IconButton(
                icon=getattr(ft.Icons, iconName.upper()),
                icon_size=IconSize,
                icon_color=fgColor,
                width=Width,
                height=Height,
                on_click=Click,
                style=ft.ButtonStyle(
                    overlay_color=Alpha(Colors.primary, 0),
                    mouse_cursor=Cursor,
                    shape=ft.RoundedRectangleBorder(radius=Radius),
                    padding=0,
                    bgcolor={
                        ft.ControlState.HOVERED: Alpha(Colors.muted, 0.8),
                        ft.ControlState.DEFAULT: bgColor,
                    },
                    side={
                        ft.ControlState.DEFAULT: ft.BorderSide(0.8, borderColor),
                    },
                ),
            )

        btnContent = []
        if iconName:
            btnContent.append(ft.Icon(getattr(ft.Icons, iconName.upper()), size=IconSize, color=fgColor))
        if Text:
            btnContent.append(ft.Text(Text, color=fgColor))

        return ft.Button(
            margin=ft.Margin(0),
            width=Width,
            height=Height,
            content=ft.Row(
                controls=btnContent,
                spacing=Gap if Text else 0,
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            on_click=Click,
            expand=Fill,
            style=ft.ButtonStyle(
                elevation=0,
                shadow_color=ft.Colors.TRANSPARENT,
                overlay_color=Alpha(Colors.primary, 0),
                shape=ft.RoundedRectangleBorder(radius=Radius),
                mouse_cursor=Cursor,
                color={
                    ft.ControlState.HOVERED: Colors.fg,
                    ft.ControlState.DEFAULT: fgColor,
                },
                bgcolor={
                    ft.ControlState.HOVERED: Alpha(Colors.muted, 0.8),
                    ft.ControlState.DEFAULT: bgColor,
                },
                side={
                    ft.ControlState.DEFAULT: ft.BorderSide(0.8, borderColor),
                },
                padding=Padding,
            ),
        )

    elif Variant == "Secondary":
        bgColor = Colors.bg_secondary
        fgColor = Colors.fg

        iconName = None
        if Icon:
            if Icons == "Rounded" or Icons == "rounded":
                iconName = Icon + "_ROUNDED"
            elif Icons == "Sharp" or Icons == "sharp":
                iconName = Icon + "_SHARP"
            else:
                iconName = Icon

        if not Text and iconName:
            return ft.IconButton(
                icon=getattr(ft.Icons, iconName.upper()),
                icon_size=IconSize,
                icon_color=fgColor,
                width=Width,
                height=Height,
                on_click=Click,
                style=ft.ButtonStyle(
                    overlay_color=Alpha(Colors.primary, 0),
                    shape=ft.RoundedRectangleBorder(radius=Radius),
                    padding=0,
                    mouse_cursor=Cursor,
                ),
            )

        btnContent = []
        if iconName:
            btnContent.append(ft.Icon(getattr(ft.Icons, iconName.upper()), size=IconSize, color=fgColor))
        if Text:
            btnContent.append(ft.Text(Text, color=fgColor))

        return ft.Button(
            margin=ft.Margin(0),
            width=Width,
            height=Height,
            content=ft.Row(
                controls=btnContent,
                spacing=Gap if Text else 0,
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            on_click=Click,
            expand=Fill,
            style=ft.ButtonStyle(
                elevation=0,
                shadow_color=ft.Colors.TRANSPARENT,
                overlay_color=Alpha(Colors.primary, 0),
                shape=ft.RoundedRectangleBorder(radius=Radius),
                mouse_cursor=Cursor,
                color={
                    ft.ControlState.HOVERED: Colors.fg,
                    ft.ControlState.DEFAULT: fgColor,
                },
                bgcolor={
                    ft.ControlState.HOVERED: Alpha(Colors.bg_secondary, 0.8),
                    ft.ControlState.DEFAULT: bgColor,
                },
                padding=Padding,
            ),
        )

    elif Variant == "Ghost":
        bgColor = ft.Colors.TRANSPARENT
        fgColor = FgColor if FgColor is not None else Colors.fg

        iconName = None
        if Icon:
            if Icons == "Rounded" or Icons == "rounded":
                iconName = Icon + "_ROUNDED"
            elif Icons == "Sharp" or Icons == "sharp":
                iconName = Icon + "_SHARP"
            else:
                iconName = Icon

        if not Text and iconName:
            return ft.IconButton(
                icon=getattr(ft.Icons, iconName.upper()),
                icon_size=IconSize,
                icon_color=fgColor,
                width=Width,
                height=Height,
                on_click=Click,
                style=ft.ButtonStyle(
                    overlay_color=Alpha(Colors.primary, 0),
                    shape=ft.RoundedRectangleBorder(radius=Radius),
                    padding=0,
                    mouse_cursor=Cursor,
                    bgcolor={
                        ft.ControlState.HOVERED: Colors.muted,
                        ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
                    },
                ),
            )

        btnContent = []
        if iconName:
            btnContent.append(ft.Icon(getattr(ft.Icons, iconName.upper()), size=IconSize, color=fgColor))
        if Text:
            btnContent.append(ft.Text(Text, color=fgColor))

        return ft.Button(
            margin=ft.Margin(0),
            width=Width,
            height=Height,
            content=ft.Row(
                controls=btnContent,
                spacing=Gap if Text else 0,
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            on_click=Click,
            expand=Fill,
            style=ft.ButtonStyle(
                elevation=0,
                shadow_color=ft.Colors.TRANSPARENT,
                overlay_color=Alpha(Colors.primary, 0),
                shape=ft.RoundedRectangleBorder(radius=Radius),
                mouse_cursor=Cursor,
                color={
                    ft.ControlState.HOVERED: Colors.fg,
                    ft.ControlState.DEFAULT: fgColor,
                },
                bgcolor={
                    ft.ControlState.HOVERED: Colors.muted,
                    ft.ControlState.DEFAULT: bgColor,
                },
                padding=Padding,
            ),
        )
    
def ControlBoxFunc(Variant="Exit"):
    from PywindUI.system import Page as _Page

    if Variant == "Exit" or Variant == "Close":
        async def _exit(e):
            from PywindUI.system import Page, _app_instance
            if Page:
                if _app_instance and _app_instance._closing:
                    for func in _app_instance._closing:
                        func()
                Page.window.visible = False
                Page.update()
                await Page.window.destroy()
        return _exit
    elif Variant == "Minimize":
        def _minimize(e):
            from PywindUI.system import Page
            if Page: Page.window.minimized = True
        return _minimize
    elif Variant == "Maximize":
        def _maximize(e):
            from PywindUI.system import Page
            if Page:
                Page.window.maximized = not Page.window.maximized
                Page.update()
        return _maximize
    else:
        return lambda e: None

# TitleBar Theme can be "Default" (same as window), "Opposite" (flip), or
# an explicit theme name like "light" / "dark".
def TitleBar(Title="Title", Variant="Detailed", Logo="Outline", Desc="built with PywindUI", Icon="Photo", Height=40, BtnHeight=26, Theme="Default", ControlBoxes="Ghost", *args, **kwargs):
    # Resolve the target theme name
    current = Colors.get_theme()
    norm = Theme.lower() if isinstance(Theme, str) else None
    if Theme is None or norm == "primary":
        target = current
    elif norm == "opposite":
        target = "light" if current == "dark" else "dark"
    elif norm in Colors._themes:
        # Explicit registered theme name (e.g. "light", "dark", a custom one)
        target = norm
    else:
        # Unknown value — keep current theme, don't crash
        target = current

    # Swap to the target theme just for the duration of building the titlebar.
    # Inner Button/Box calls snapshot Colors.* into their ButtonStyle/Container
    # at construction time, so reverting Colors afterwards is safe — the
    # built controls keep the swapped values.
    needs_swap = target != current
    if needs_swap:
        Colors.set_theme(target)
    try:
        result = _TitleBarBody(
            Title=Title, Variant=Variant, Logo=Logo, Desc=Desc, Icon=Icon,
            Height=Height, BtnHeight=BtnHeight, ControlBoxes=ControlBoxes,
        )
    finally:
        if needs_swap:
            Colors.set_theme(current)
    return result

def _TitleBarBody(Title, Variant, Logo, Desc, Icon, Height, BtnHeight, ControlBoxes):
    if Variant == "Primary" or Variant == "Detailed" or Variant == "Desc":
        titlebar_content = Box(
            Box(
                Button(Text=Title, Icon=Icon, Variant=Logo, Height=BtnHeight, Padding=Pads(Space.sm, 0)),
                ft.Text(Desc, size=12, color=Colors.fg),
                Direction="Horizontal",
                Gap=Space.sm,
            ),
            Box(
                Button(Text="", Variant=ControlBoxes, Icon="minimize", Click=ControlBoxFunc("Minimize"), Height=BtnHeight, Width=BtnHeight),
                Button(Text="", Variant=ControlBoxes, Icon="crop_square", Click=ControlBoxFunc("Maximize"), Height=BtnHeight, Width=BtnHeight),
                Button(Text="", Variant=ControlBoxes, Icon="close", Click=ControlBoxFunc("Close"), Height=BtnHeight, Width=BtnHeight),
                Gap=Space.sm,
                Name="ProjectButtons",
                Direction="Horizontal",
            ),
            Height=Height,
            Name="Titlebar",
            Align="Between",
            Direction="Horizontal",
            bgColor=Colors.bg,
            Padding=Pads((Height - BtnHeight) // 2, 0)
        )
        
        # Don't expand vertically - just horizontally fill the width
        return ft.WindowDragArea(
            content=titlebar_content,
            expand=False,        # Don't expand vertically
            expand_loose=True,   # Fill horizontal space only
            maximizable=True,
        )
    if Variant == "Logo" or Variant == "Simple" or Variant == "NoDesc":
        titlebar_content = Box(
            Button(Text=Title, Icon=Icon, Variant=Logo, Height=BtnHeight),
            Box(
                Button(Text="", Variant=ControlBoxes, Icon="minimize", Click=ControlBoxFunc("Minimize"), Height=BtnHeight, Width=BtnHeight),
                Button(Text="", Variant=ControlBoxes, Icon="crop_square", Click=ControlBoxFunc("Maximize"), Height=BtnHeight, Width=BtnHeight),
                Button(Text="", Variant=ControlBoxes, Icon="close", Click=ControlBoxFunc("Close"), Height=BtnHeight, Width=BtnHeight),
                Gap=Space.sm,
                Name="ProjectButtons",
                Direction="Horizontal",
            ),
            Height=Height,
            Name="Titlebar",
            Align="Between",
            Direction="Horizontal",
            bgColor=Colors.bg,
            Padding=Pads((Height - BtnHeight) // 2, 0)
        )
        
        # Don't expand vertically - just horizontally fill the width
        return ft.WindowDragArea(
            content=titlebar_content,
            expand=False,        # Don't expand vertically
            expand_loose=True,   # Fill horizontal space only
            maximizable=True,
        )

def ControlBar():
    return 0

@overload
def Text(Text, MaxLines=1, Size=14, Weight=ft.FontWeight.W_400, Color=None, Style=None, Italic=False, *, NoContainer: Literal[True], Name=None, **kwargs) -> ft.Text: ...

@overload
def Text(Text, MaxLines=1, Size=14, Weight=ft.FontWeight.W_400, Color=None, Style=None, Italic=False, NoContainer: Literal[False] = False, Name=None, **kwargs) -> ft.Container: ...

def Text(Text, MaxLines=1, Size=14, Weight=ft.FontWeight.W_400, Color=None, Style=None, Italic=False, NoContainer=False, Name=None, *args, **kwargs):
    if Color is None:
        Color = Colors.fg

    text_control = ft.Text(
        Text,
        size=Size,
        weight=Weight,
        color=Color,
        italic=Italic,
        max_lines=MaxLines,
        style=ft.TextStyle(height=1.0),
    )

    if Name is not None:
        Name.control = text_control

    if NoContainer:
        return text_control

    return ft.Container(
        content=text_control,
        margin=ft.Margin(0, -Size * 0.15, 0, 0),
    )

def Link(Text, Size=10, Weight=ft.FontWeight.W_100, Color=None, *args, **kwargs):
    if Color is None:
        Color = Colors.accent
    return ft.Text(Text, size=Size, weight=Weight, color=Color)


_TEXTBOX_HEIGHT = 30  # Textbox() default — RichTextbox matches this for its single-line state
_DENSITY_PAD = 4  # Material trimes top and bottom, so this add its back.

def RichTextbox(Placeholder="Placeholder", Value=None, TextSize=12, LineHeight=1.4,
                Lines=4, MaxLines=None, AutoExpand=False, Padding=None,
                Radius=Radius.md, Height=None, Width=None, Fill=False, Cursor=None,
                Variant="Default", Align=None, PlaceholderAlign=None, minChar=None,
                maxChar=None, ReadOnly=False, EnterSubmits=False, Change=None,
                Submit=None, Name=None):
    """Multi-line text input (textarea). Same look as Textbox.

    Lines        rows shown when AutoExpand is off (default 4). Ignored if
                 Height is given — the row count is derived from Height.
    LineHeight   line-height multiplier applied to text and placeholder.
    AutoExpand   start as a single 30px row (identical to Textbox) and grow
                 one line at a time as text wraps / Enter is pressed. Grows
                 until MaxLines (None = unlimited), then scrolls internally.
    Height       fixed pixel height. With AutoExpand it's the collapsed
                 single-row height instead (default 30).
    EnterSubmits Enter fires Submit, Shift+Enter inserts a newline. Off by
                 default so Enter just adds a line like a normal textarea.
    Change / Submit / minChar / maxChar / ReadOnly / Name behave as in Textbox.
    """
    text_align = _resolve_text_align(Align) or _resolve_text_align(PlaceholderAlign)

    # Height of one text row in px — the unit everything below is sized in.
    line_px = TextSize * LineHeight

    # Vertical padding per side so `rows` rows fill `total` px, plus the
    # density trim Material is going to take back off.
    def _pad_for(total, rows):
        return max(0.0, (total - rows * line_px) / 2) + _DENSITY_PAD

    # Padding that makes a single row exactly as tall as Textbox(Height=30).
    # Textbox uses Space.xs on the sides, so keep that horizontally.
    base_pad = max(0.0, (_TEXTBOX_HEIGHT - line_px) / 2)

    if AutoExpand:
        # Collapsed row height is Height if given, else the Textbox default.
        row_height = Height if Height is not None else _TEXTBOX_HEIGHT
        min_lines, max_lines, fixed_height = 1, MaxLines, None
        pad_y = _pad_for(row_height, 1)
    elif Height is not None:
        # Fill the requested Height: pick the row count that fits, then absorb
        # the remainder into the vertical padding so the border isn't short.
        min_lines = max(1, int((Height - 2 * base_pad) // line_px))
        max_lines = min_lines
        fixed_height = Height
        pad_y = _pad_for(Height, min_lines)
    else:
        min_lines = max_lines = max(1, int(Lines))
        fixed_height = None
        pad_y = base_pad + _DENSITY_PAD

    if Padding is None:
        Padding = ft.Padding(Space.xs, pad_y, Space.xs, pad_y)

    # minChar validation and the user's Change handler both run on change.
    user_change = _normalize_handler(Change)

    def _on_change(e):
        if minChar is not None:
            val = e.control.value or ""
            e.control.error_text = (
                f"Minimum {minChar} characters" if 0 < len(val) < minChar else None
            )
            e.control.update()
        if user_change is not None:
            return user_change(e)

    on_change_handler = _on_change if (minChar is not None or user_change) else None

    field = ft.TextField(
        value=Value if Value is not None else "",
        hint_text=Placeholder,
        hint_style=ft.TextStyle(color=Colors.muted_fg, size=TextSize, height=LineHeight),
        text_style=ft.TextStyle(size=TextSize, height=LineHeight),
        text_align=text_align,
        text_vertical_align=ft.VerticalAlignment.START,
        text_size=TextSize,
        multiline=True,
        min_lines=min_lines,
        max_lines=max_lines,
        shift_enter=EnterSubmits,
        dense=True,  # drop Material's 48px minimum so one row == Textbox height
        width=Width,
        height=fixed_height,
        max_length=maxChar,
        read_only=ReadOnly,
        on_change=on_change_handler,
        on_submit=_normalize_handler(Submit),
        color=Colors.muted_fg if ReadOnly else Colors.fg,
        focused_bgcolor=Alpha(Colors.input, 0.3),
        border_color=Colors.border,
        focused_border_color=Colors.ring,
        border_radius=Radius,
        border_width=0.8,
        focused_border_width=2,
        expand=Fill,
        mouse_cursor=Cursor,
        content_padding=Padding,
    )

    if Name is not None:
        Name.control = field

    return field

def _resolve_text_align(value):
    if value is None:
        return None
    if not isinstance(value, str):
        return value  # already an ft.TextAlign
    key = value.lower()
    return {
        "left":    ft.TextAlign.LEFT,
        "start":   ft.TextAlign.START,
        "center":  ft.TextAlign.CENTER,
        "right":   ft.TextAlign.RIGHT,
        "end":     ft.TextAlign.END,
        "justify": ft.TextAlign.JUSTIFY,
    }.get(key)

def Textbox(Placeholder="Placeholder", Value=None, TextSize=12, Icons=None, Icon=None,
            IconSize=18, Padding=None, Radius=Radius.md, Height=30, Width=None,
            Fill=False, Cursor=None, Variant="Default", Gap=Space.sm, Align=None,
            PlaceholderAlign=None, minChar=None, maxChar=None, Numeric=False,
            ReadOnly=False, Change=None, Submit=None, Name=None):
    """Text input.
 
    Value    initial contents.
    Numeric  restrict typing to digits plus one decimal separator (. or ,).
    ReadOnly display-only field — still selectable/copyable, not editable.
    Change   handler fired on every keystroke; called as fn() or fn(e).
    Submit   handler fired on Enter; called as fn() or fn(e).
    """
    text_align = _resolve_text_align(Align) or _resolve_text_align(PlaceholderAlign)
 
    is_centered = text_align == ft.TextAlign.CENTER
    if Padding is None:
        Padding = ft.Padding(0, Space.xs, 0, Space.xs) if is_centered else Pads(Space.xs, Space.xs)
 
    # Icon was accepted but never used before — wire it to prefix_icon.
    iconName = _resolve_icon_name(Icon, Icons)
    prefixIcon = None
    if iconName:
        prefixIcon = ft.Icon(getattr(ft.Icons, iconName.upper()),
                             size=IconSize, color=Colors.muted_fg)
 
    # minChar validation and the user's Change handler both run on change.
    user_change = _normalize_handler(Change)
 
    def _on_change(e):
        if minChar is not None:
            val = e.control.value or ""
            e.control.error_text = (
                f"Minimum {minChar} characters" if 0 < len(val) < minChar else None
            )
            e.control.update()
        if user_change is not None:
            return user_change(e)
 
    on_change_handler = _on_change if (minChar is not None or user_change) else None
 
    # Numeric filter. Guarded because ft.InputFilter has moved around between
    # Flet releases — worst case you get an unfiltered field, not a crash.
    input_filter = None
    if Numeric:
        try:
            input_filter = ft.InputFilter(
                regex_string=r"^-?[0-9]*[.,]?[0-9]*$",
                allow=True,
                replacement_string="",
            )
        except Exception:
            input_filter = None
 
    field = ft.TextField(
        value=Value if Value is not None else "",
        hint_text=Placeholder,
        hint_style=ft.TextStyle(color=Colors.muted_fg),
        text_align=text_align,
        text_size=TextSize,
        width=Width,
        height=Height,
        max_length=maxChar,
        read_only=ReadOnly,
        input_filter=input_filter,
        on_change=on_change_handler,
        on_submit=_normalize_handler(Submit),
        prefix_icon=prefixIcon,
        color=Colors.muted_fg if ReadOnly else Colors.fg,
        focused_bgcolor=Alpha(Colors.input, 0.3),
        border_color=Colors.border,
        focused_border_color=Colors.ring,
        border_radius=Radius,
        border_width=0.8,
        focused_border_width=2,
        expand=Fill,
        mouse_cursor=Cursor,
        content_padding=Padding,
    )
 
    if Name is not None:
        Name.control = field
 
    return field


def _resolve_icon_name(Icon, Icons):
    if not Icon:
        return None
    Icon = Icon.strip().replace(" ", "_").replace("-", "_")
    if Icons == "Rounded" or Icons == "rounded":
        return Icon + "_ROUNDED"
    if Icons == "Sharp" or Icons == "sharp":
        return Icon + "_SHARP"
    return Icon

# ════════════════════════════════════════
#  DROPDOWN MENU SYSTEM
# ════════════════════════════════════════
# Mirrors the Tab() / TabView() registry pattern in utilities.py:
#   DropdownMenu(item, item, ..., Name="fileMenu")   # registers
#   Button(..., Dropdown=True, DropdownMenu="fileMenu")  # references

_dropdown_menus: dict = {}

def DropdownMenu(*Items, Name="default", Pad=Space.sm, Gap=0, Width=None):
    """Register dropdown items under a name. Reference from
       Button(Dropdown=True, DropdownMenu=Name).

    Pad:   gap in pixels between the visible popover card and the (invisible)
           popover bounds Material draws. Same gap on all sides, regardless of
           which side of the window the trigger is on.
    Gap:   vertical spacing in pixels between items inside the popover
           (includes labels, separators, and item rows).
    Width: optional fixed width for the popover card. If None (default), the
           card auto-sizes to its widest item.
    """
    items_list = [i for i in Items if i is not None]
    # Bundle items inside a single styled Container. Material will render this
    # Container as the popover content (with transparent outer bg set on the
    # trigger's menu_style), so the Container's margin = visible gap from edges.
    visual_card = ft.Container(
        content=ft.Column(controls=items_list, spacing=Gap, tight=True),
        bgcolor=Colors.popover,
        border_radius=Radius.lg,
        padding=ft.Padding(Space.xs, Space.xs, Space.xs, Space.xs),
        margin=ft.Margin(Pad, 0, Pad, 0),
        width=Width,
        # Thin border — uses theme's border colour so it shows up subtly in
        # light mode and almost disappears in dark.
        border=ft.Border.all(1, Colors.border),
        # Small, soft shadow. Keep blur_radius <= Pad so the shadow doesn't
        # bleed into the transparent margin around the card (which was
        # visible as a grey smudge in light theme).
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=6,
            color=Alpha(Colors.black, 0.12),
            offset=ft.Offset(0, 2),
        ),
    )
    _dropdown_menus[Name] = [visual_card]

def DropdownMenuSeparator():
    # Material 3 menus accept plain Dividers between MenuItemButtons
    return ft.Divider(
        height=1,
        color=Colors.border,
        thickness=1,
    )

def DropdownMenuLabel(Text="Label", Height=22):
    # A disabled MenuItemButton renders as a non-interactive header row.
    # Height kwarg lets you tune row height per label; default 22px.
    return ft.MenuItemButton(
        content=ft.Text(
            Text,
            size=12,
            weight=ft.FontWeight.W_500,
            color=Colors.muted_fg,
        ),
        disabled=True,
        height=Height,
        style=ft.ButtonStyle(
            padding=ft.Padding(Space.sm, 0, Space.sm, 0),
            shape=ft.RoundedRectangleBorder(radius=Radius.md),
            visual_density=ft.VisualDensity.COMPACT,
        ),
    )

def DropdownMenuShortcut(Text=""):
    return ft.Text(Text, size=12, color=Colors.muted_fg)

def DropdownMenuItem(Text="Item", Icon=None, Icons=None, IconSize=16, Click=None,
                     Shortcut=None, Variant="Default", Disabled=False, Height=28,
                     *args, **kwargs):
    isDestructive = Variant == "Destructive" or Variant == "destructive"
    fgColor = Colors.destructive if isDestructive else Colors.fg
    hoverBg = Alpha(Colors.destructive, 0.15) if isDestructive else Colors.accent
    hoverFg = Colors.destructive if isDestructive else Colors.accent_fg

    # Handle no-param Click functions
    if Click is not None and not inspect.signature(Click).parameters:
        _click = Click
        Click = lambda e: _click()
    elif Click is None:
        Click = lambda e: None

    iconName = _resolve_icon_name(Icon, Icons)

    leading = None
    if iconName:
        leading = ft.Icon(getattr(ft.Icons, iconName.upper()), size=IconSize, color=fgColor)

    trailing = None
    if Shortcut:
        trailing = ft.Text(Shortcut, size=12, color=Colors.muted_fg)

    return ft.MenuItemButton(
        content=ft.Text(Text, size=14, color=fgColor),
        leading=leading,
        trailing=trailing,
        on_click=Click,
        disabled=Disabled,
        height=Height,
        style=ft.ButtonStyle(
            bgcolor={
                ft.ControlState.HOVERED: hoverBg,
                ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
            },
            overlay_color=Alpha(Colors.primary, 0),
            shape=ft.RoundedRectangleBorder(radius=Radius.md),
            padding=ft.Padding(Space.sm, 0, Space.sm, 0),
            mouse_cursor=Cursors.hand,
            visual_density=ft.VisualDensity.COMPACT,
        ),
    )

def DropdownMenuCheckboxItem(Text="Item", Checked=False, Change=None, Disabled=False,
                             Height=28, *args, **kwargs):
    if Change is not None and not inspect.signature(Change).parameters:
        _change = Change
        Change = lambda e: _change()

    checkbox = ft.Checkbox(
        value=Checked,
        on_change=Change,
        fill_color=Colors.primary,
        check_color=Colors.primary_fg,
    )

    return ft.MenuItemButton(
        content=ft.Text(Text, size=14, color=Colors.fg),
        leading=checkbox,
        on_click=None,  # interact via the checkbox itself
        disabled=Disabled,
        close_on_click=False,  # keep menu open while toggling
        height=Height,
        style=ft.ButtonStyle(
            bgcolor={
                ft.ControlState.HOVERED: Colors.accent,
                ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
            },
            shape=ft.RoundedRectangleBorder(radius=Radius.md),
            padding=ft.Padding(Space.sm, 0, Space.sm, 0),
            mouse_cursor=Cursors.hand,
            visual_density=ft.VisualDensity.COMPACT,
        ),
    )

def DropdownMenuRadioItem(Text="Item", Value=None, Selected=False, Change=None,
                          Disabled=False, Height=28, *args, **kwargs):
    if Change is not None and not inspect.signature(Change).parameters:
        _change = Change
        Change = lambda e: _change()

    radio = ft.Radio(
        value=Value if Value is not None else Text,
        fill_color=Colors.primary,
    )

    return ft.MenuItemButton(
        content=ft.Text(Text, size=14, color=Colors.fg),
        leading=radio,
        on_click=Change,
        disabled=Disabled,
        height=Height,
        style=ft.ButtonStyle(
            bgcolor={
                ft.ControlState.HOVERED: Colors.accent,
                ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
            },
            shape=ft.RoundedRectangleBorder(radius=Radius.md),
            padding=ft.Padding(Space.sm, 0, Space.sm, 0),
            mouse_cursor=Cursors.hand,
            visual_density=ft.VisualDensity.COMPACT,
        ),
    )

def _BuildDropdownButton(Text, Icons, Icon, IconSize, Height, Width, Fill, Cursor,
                        Variant, Gap, Padding, TriggerRadius, FgColor, MenuName):
    """Build a MenuBar+SubmenuButton styled like Button(Variant=Variant).

    Called from Button() when Dropdown=True. Looks up items registered under
    MenuName via DropdownMenu(*items, Name=MenuName).
    """
    items = _dropdown_menus.get(MenuName, [])

    # Resolve variant colors — same logic as Button
    if Variant == "Primary":
        bgColor = Colors.primary
        fgColor = FgColor if FgColor is not None else Colors.primary_fg
        hoverBg = Alpha(Colors.primary, 0.9)
        borderColor = None
    elif Variant == "Outline":
        bgColor = Colors.bg
        fgColor = FgColor if FgColor is not None else Colors.secondary_fg
        hoverBg = Alpha(Colors.muted)
        borderColor = Colors.border
    elif Variant == "Secondary":
        bgColor = Colors.bg_secondary
        fgColor = FgColor if FgColor is not None else Colors.secondary_fg
        hoverBg = Alpha(Colors.bg_secondary, 0.8)
        borderColor = None
    else:  # Default / Ghost
        bgColor = ft.Colors.TRANSPARENT
        fgColor = FgColor if FgColor is not None else Colors.fg
        hoverBg = Colors.muted
        borderColor = None

    iconName = _resolve_icon_name(Icon, Icons)

    # Icon-only: zero horizontal padding and let the trigger auto-size to the icon,
    # matching how Button(icon-only) returns an IconButton with width=None.
    iconOnly = bool(iconName) and not Text
    if iconOnly:
        Padding = 0

    btnContent = []
    if iconName:
        btnContent.append(ft.Icon(getattr(ft.Icons, iconName.upper()), size=IconSize, color=fgColor))
    if Text:
        btnContent.append(ft.Text(Text, color=fgColor))

    triggerRow = ft.Row(
        controls=btnContent,
        spacing=Gap if Text else 0,
        alignment=ft.MainAxisAlignment.CENTER,
        tight=True,
    )

    submenu = ft.SubmenuButton(
        content=triggerRow,
        controls=items,
        height=Height,
        width=Height if iconOnly else None,
        # Vertical: gap between trigger bottom and popover top.
        # Horizontal: -Space.sm cancels Material's default ~8px screen-edge
        # padding on the left side (where the offset is honoured). On the right
        # side it's ignored due to Material's clamp — but the visible card has
        # its own margin (set in DropdownMenu), so both sides end up symmetric.
        alignment_offset=(-Space.sm, Space.sm),
        style=ft.ButtonStyle(
            bgcolor={
                ft.ControlState.HOVERED: hoverBg,
                ft.ControlState.DEFAULT: bgColor,
            },
            color={
                ft.ControlState.HOVERED: Colors.fg if Variant != "Primary" else fgColor,
                ft.ControlState.DEFAULT: fgColor,
            },
            shape=ft.RoundedRectangleBorder(radius=TriggerRadius),
            padding=Padding,
            mouse_cursor=Cursor,
            elevation=0,
            shadow_color=ft.Colors.TRANSPARENT,
            overlay_color=Alpha(Colors.primary, 0),
            # Compact density removes Material's default ~8px vertical inset
            visual_density=ft.VisualDensity.COMPACT,
            side={
                ft.ControlState.DEFAULT: ft.BorderSide(0.8, borderColor),
            } if borderColor else None,
        ),
        menu_style=ft.MenuStyle(
            # Transparent outer popover — the visible card (with margin) is
            # the Container registered by DropdownMenu(). This way the gap
            # from the window edge is controlled by the Container's margin
            # and applies symmetrically on both sides.
            bgcolor=ft.Colors.TRANSPARENT,
            shadow_color=ft.Colors.TRANSPARENT,
            elevation=0,
            padding=0,
            shape=ft.RoundedRectangleBorder(radius=Radius.lg),
        ),
    )

    return ft.Container(
        content=ft.MenuBar(
            controls=[submenu],
            style=ft.MenuStyle(
                bgcolor=ft.Colors.TRANSPARENT,
                shadow_color=ft.Colors.TRANSPARENT,
                elevation=0,
                padding=0,
                shape=ft.RoundedRectangleBorder(radius=TriggerRadius),
                visual_density=ft.VisualDensity.COMPACT,
                # Clamp the MenuBar to a square footprint when icon-only,
                # otherwise Material reserves a wider tap target.
                fixed_size=ft.Size(Height, Height) if iconOnly else None,
            ),
        ),
        height=Height,
        width=Height if iconOnly else Width,
    )

def ComponentGenerator(*args, **kwargs):
 return None

"""
def CharBox(str, Fill=False):
    if len(str) == 1:
        maxLength = 1
    else:
        maxLength = 0


    return ft.TextField(
        value=str,
        text_align=ft.TextAlign.CENTER,
        border=ft.InputBorder.NONE,
        cursor_color=Colors.primary_fg,
        color=Colors.primary_fg,
        bgcolor=Colors.primary,
        max_length=maxLength,
        expand=True,
    )
"""

"""
def Btn(Text="Button", Icon=None, IconSize=18, Click=Click, Height=None, Width=None, Fill=False, Gap=Spacing.sm):
    children = []
    if Icon:
        children.append(ft.Icon(getattr(ft.Icons, Icon.upper()), size=IconSize))
    children.append(ft.Text(Text))

    return ft.Button(
        height=Height,
        width=Width,
        content=ft.Row(
            controls=children,
            spacing=Gap,
            alignment=ft.MainAxisAlignment.CENTER,
            tight=True,
        ),
        on_click=Click,
        expand=Fill,
    )
def card(title: str, *children):
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(title, size=16, weight=ft.FontWeight.W_600, color=Colors.card_fg),
                *children,
            ],
            spacing=Spacing.sm,
        ),
        bgcolor=Colors.card,
        border=ft.border.all(1, Colors.border),
        border_radius=Radius.sm,
        padding=ft.padding.all(Spacing.md),
    )
"""

# Checkbox component in shadcn style
def Checkbox(Text="", Checked=False, Change=None, Disabled=False, Height=28):
    if Change is not None and not inspect.signature(Change).parameters:
        _change = Change
        Change = lambda e: _change()

    return ft.Checkbox(
        label=Text,
        value=Checked,
        on_change=Change,
        fill_color=Colors.primary,
        check_color=Colors.primary_fg,
        disabled=Disabled,
        height=Height,
    )

# ════════════════════════════════════════
#  TABLE
#  Replaces the old ft.Table stub in components.py
# ════════════════════════════════════════
#
#   Table(
#       ("R1", "10k",  "0402", "12"),
#       ("C3", "100n", "0603", "4"),
#       Columns=("Ref", "Value", "Package", "Qty"),
#       Widths=(70, None, 90, 60),
#       Align=("Start", "Start", "Start", "End"),
#       FullWidth=400,          # total table width in px
#       Fill=False,             # don't stretch to the parent
#       Striped=True,
#       Name=BomTable,
#   )
#
#   BomTable.Data.SetRows([...])   # header stays, body swaps
#   BomTable.Data.AddRow(row)
#   BomTable.Data.Rows
#
# SIZING — three modes, in priority order:
#   FullWidth=400   -> table is exactly 400px; None-width columns split
#                      whatever is left over after the fixed ones.
#   Fill=True       -> table expands to the parent; None-width columns
#                      split the leftover space.
#   neither         -> table hugs its content. None-width columns fall
#                      back to FlexWidth (default 120) so nothing has to
#                      stretch, and the rows/dividers are pinned to the
#                      summed width instead of running to the edge.
#
# Rows may be tuples/lists, dicts keyed by column label, or a single
# ft.Control (spans the row). Any cell may be a Flet control.

_TABLE_ALIGN = {
    "Start":  (ft.Alignment.CENTER_LEFT,   ft.TextAlign.LEFT),
    "Left":   (ft.Alignment.CENTER_LEFT,   ft.TextAlign.LEFT),
    "Center": (ft.Alignment.CENTER,        ft.TextAlign.CENTER),
    "End":    (ft.Alignment.CENTER_RIGHT,  ft.TextAlign.RIGHT),
    "Right":  (ft.Alignment.CENTER_RIGHT,  ft.TextAlign.RIGHT),
}


class TableHandle:
    """Sits on Name.Data so rows can be replaced after the table is built."""

    def __init__(self, rows, rebuild):
        self.Rows = list(rows)
        self._rebuild = rebuild

    def SetRows(self, rows):
        self.Rows = list(rows)
        self._rebuild(self.Rows)

    def AddRow(self, row):
        self.Rows.append(row)
        self._rebuild(self.Rows)

    def Clear(self):
        self.Rows = []
        self._rebuild(self.Rows)

    def __repr__(self):
        return f"<TableHandle rows={len(self.Rows)}>"


_TABLE_RADIUS = Radius.md  # captured before Table shadows `Radius` with a param


def Table(*Rows, Columns=None, Widths=None, Align="Start", HeaderAlign=None,
          FullWidth=None, FlexWidth=120, Fill=False, Height=None,
          RowHeight=36, HeaderHeight=38, TextSize=12, HeaderSize=12,
          TextColor=None, HeaderColor=None, HeaderWeight=ft.FontWeight.W_500,
          HeaderBg=None, CellPad=Space.md, Radius=_TABLE_RADIUS, Border=True,
          Striped=False, StripeColor=None, Hover=True, HoverColor=None,
          Dividers=True, HeaderDivider=None, ColumnDividers=True,
          Bg=None, Scroll=False, Empty="No results.",
          Click=None, Name=None, Width=None):
    """A shadcn-style data table built from Containers (no ft.DataTable).

    Widths: per-column px width, or None for a flexible column.
    Align:  "Start"/"Center"/"End" for every column, or a per-column
            sequence. HeaderAlign defaults to Align.
    Click:  called per row as Click(index, row) — or Click(index) /
            Click() if it takes fewer args.
    Dividers / ColumnDividers: horizontal rules between rows, vertical
            rules between columns. Either can be turned off alone.
    TextColor / HeaderColor / HeaderWeight / HeaderBg: cell + column-label
            styling. Defaults are card_fg on the body and muted_fg on the
            header, matching shadcn.
    Width:  deprecated alias for FullWidth.
    """

    total_width = FullWidth if FullWidth is not None else Width
    bounded = bool(Fill) or total_width is not None

    text_color = TextColor or Colors.card_fg
    header_color = HeaderColor or Colors.muted_fg
    header_bg = HeaderBg or Alpha(Colors.accent, 0.45)
    body_bg = Bg or Colors.card
    header_rule = Dividers if HeaderDivider is None else HeaderDivider

    def _align_for(i, spec):
        if isinstance(spec, (tuple, list)):
            key = spec[i] if i < len(spec) else "Start"
        else:
            key = spec or "Start"
        return _TABLE_ALIGN.get(key, _TABLE_ALIGN["Start"])

    def _width_for(i):
        """-> (px_width, expand). Exactly one of the two is meaningful."""
        if Widths and i < len(Widths) and Widths[i] is not None:
            return Widths[i], False        # fixed column
        if bounded:
            return None, True              # share the leftover space
        return FlexWidth, False            # shrink-wrap: no stretching

    def _normalize(row):
        """Any row shape -> a flat list of cells."""
        if isinstance(row, dict):
            if Columns:
                return [row.get(c, "") for c in Columns]
            return list(row.values())
        if isinstance(row, ft.Control) or isinstance(row, str):
            return [row]
        try:
            return list(row)
        except TypeError:
            return [row]

    # ── column count & shrink-wrap width ────
    if Columns:
        col_count = len(Columns)
    else:
        col_count = max((len(_normalize(r)) for r in Rows), default=1)

    rule_count = (col_count - 1) if (ColumnDividers and col_count > 1) else 0

    content_width = None
    if not bounded:
        content_width = sum(_width_for(i)[0] for i in range(col_count)) + rule_count # type: ignore

    def _cell(value, i, align_spec, size, color, weight) -> ft.Control:
        width, expand = _width_for(i)
        alignment, text_align = _align_for(i, align_spec)

        if isinstance(value, ft.Control):
            content = value
        else:
            content = ft.Text(
                "" if value is None else str(value),
                size=size,
                color=color,
                weight=weight,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
                text_align=text_align,
            )

        return ft.Container(
            content=content,
            padding=ft.Padding(CellPad, 0, CellPad, 0),
            alignment=alignment,
            width=width,
            expand=expand,
        )

    def _cell_row(controls: "list[ft.Control]", height) -> ft.Row:
        if ColumnDividers and len(controls) > 1:
            ruled: "list[ft.Control]" = []
            for i, c in enumerate(controls):
                if i > 0:
                    ruled.append(
                        ft.Container(
                            width=1,
                            height=height,   # explicit — a childless gap otherwise stretches
                            bgcolor=Alpha(Colors.border, 0.55),
                        )
                    )
                ruled.append(c)
            controls = ruled

        return ft.Row(
            controls=controls,
            spacing=0,
            tight=not bounded,             # don't run to the edge when unbounded
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )

    def _divider(strong=False) -> ft.Control:
        return ft.Container(
            height=1,
            width=content_width,           # pinned, so it can't stretch the Column
            bgcolor=Colors.border if strong else Alpha(Colors.border, 0.55),
        )

    stripe_bg = StripeColor or Alpha(Colors.accent, 0.55)
    hover_bg = HoverColor or Alpha(Colors.accent, 0.85)

    def _make_hover(container, base_bg):
        def _on_hover(e):
            hovering = str(e.data).lower() in ("true", "1")
            container.bgcolor = hover_bg if hovering else base_bg
            container.update()
        return _on_hover

    def _make_click(index, row):
        if Click is None:
            return None
        callback = Click  # local, non-Optional binding for the closure
        try:
            argc = len(inspect.signature(callback).parameters)
        except (TypeError, ValueError):
            argc = 0

        def _on_click(e):
            if argc >= 2:
                callback(index, row)
            elif argc == 1:
                callback(index)
            else:
                callback()
        return _on_click

    def _build_row(row, index) -> ft.Control:
        cells = _normalize(row)
        if len(cells) < col_count:
            cells = list(cells) + [""] * (col_count - len(cells))

        controls: "list[ft.Control]" = [
            _cell(v, i, Align, TextSize, text_color, ft.FontWeight.W_400)
            for i, v in enumerate(cells)
        ]

        base_bg = stripe_bg if (Striped and index % 2 == 1) else ft.Colors.TRANSPARENT

        container = ft.Container(
            content=_cell_row(controls, RowHeight),
            height=RowHeight,
            width=content_width,
            bgcolor=base_bg,
        )

        if Hover:
            container.on_hover = _make_hover(container, base_bg)
        handler = _make_click(index, row)
        if handler is not None:
            container.on_click = handler

        return container

    def _build_body(rows) -> "list[ft.Control]":
        if not rows:
            empty: "list[ft.Control]" = [
                ft.Container(
                    content=ft.Text(Empty, size=TextSize, color=Colors.muted_fg),
                    height=RowHeight * 2,
                    width=content_width,
                    alignment=ft.Alignment.CENTER,
                )
            ]
            return empty

        controls: "list[ft.Control]" = []
        for index, row in enumerate(rows):
            if index > 0 and Dividers:
                controls.append(_divider())
            controls.append(_build_row(row, index))
        return controls

    # ── header ──────────────────────────
    head: "list[ft.Control]" = []
    if Columns:
        header_cells: "list[ft.Control]" = [
            _cell(c, i, HeaderAlign or Align, HeaderSize,
                  header_color, HeaderWeight)
            for i, c in enumerate(Columns)
        ]
        head.append(
            ft.Container(
                content=_cell_row(header_cells, HeaderHeight),
                height=HeaderHeight,
                width=content_width,
                bgcolor=header_bg,
            )
        )
        if header_rule:
            head.append(_divider(strong=True))

    body = ft.Column(
        controls=_build_body(list(Rows)),
        spacing=0,
        tight=not (Height or Fill),
        scroll=ft.ScrollMode.AUTO if (Scroll or Height) else None,
        expand=bool(Height or Fill),
        horizontal_alignment=ft.CrossAxisAlignment.START,
    )

    outer = ft.Container(
        content=ft.Column(
            controls=head + [body],
            spacing=0,
            tight=not (Height or Fill),
            expand=bool(Height or Fill),
            horizontal_alignment=ft.CrossAxisAlignment.START,
        ),
        bgcolor=Colors.card,
        border=ft.Border.all(1, Colors.border) if Border else None,
        border_radius=Radius,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        width=total_width if total_width is not None else content_width,
        height=Height,
        expand=bool(Fill) and total_width is None,
    )

    def _rebuild(rows):
        body.controls = _build_body(rows)
        try:
            body.update()
        except Exception:
            pass  # not mounted yet — renders with the new rows on first draw

    if Name is not None:
        Name.control = outer
        Name.Data = TableHandle(list(Rows), _rebuild)

    return outer


# ════════════════════════════════════════
#  GRAPH  (LineChart)
#  Requires, at the top of components.py:
#      import math
#      import flet_charts as fch          # pip install flet-charts
#      from PywindUI.utilities import ... , Weight
# ════════════════════════════════════════
#
#   Graph([10, 18, 12, 21, 20])                      # y-only, x = 0,1,2,...
#   Graph([(0, 10), (1, 15), (2, 18)])               # explicit (x, y)
#   Graph(profile, Color=Colors.chart_2, Height=240)
#
#   Graph(                                           # two lines
#       {"Values": measured, "Label": "Measured"},
#       {"Values": target, "Label": "Target", "Area": False, "Dash": [6, 4]},
#       YSuffix="°C", XSuffix="s", Name=ReflowGraph,
#   )
#
#   ReflowGraph.Data.SetSeries([...])   # swap data, axes rescale
#   ReflowGraph.Data.Series
#
# A series is either a bare sequence (y values, or (x, y) pairs) or a dict:
#   Values / Points   the sequence
#   Label             legend text
#   Color             defaults to Colors.chart_1..chart_5, cycling
#   Area, Stroke, Curved, Dash, Dots   per-series overrides
#
# Axis ticks are picked automatically on a 1/2/2.5/5 × 10ⁿ ladder. Pass
# YTicks / XTicks for a different count, or MinY / MaxY to pin the range.
 
 
class GraphHandle:
    """Sits on Name.Data so the data can be replaced after the graph is built."""
 
    def __init__(self, series, rebuild):
        self.Series = list(series)
        self._rebuild = rebuild
 
    def SetSeries(self, *series):
        if len(series) == 1 and isinstance(series[0], (list, tuple)) and series[0] \
                and isinstance(series[0][0], (dict, list)):
            series = tuple(series[0])
        self.Series = list(series)
        self._rebuild(self.Series)
 
    def __repr__(self):
        return f"<GraphHandle series={len(self.Series)}>"
 
 
def _graph_kw(cls, **kw):
    """Build a flet-charts object, tolerating the points/data_points and
    rounded_stroke_cap/stroke_cap_round renames across Flet versions."""
    renames = {"points": "data_points", "rounded_stroke_cap": "stroke_cap_round"}
    try:
        return cls(**kw)
    except TypeError:
        fixed = {renames.get(k, k): v for k, v in kw.items()}
        return cls(**fixed)
 
 
def _nice_ticks(lo, hi, count):
    """Ticks on a 1 / 2 / 2.5 / 5 × 10ⁿ ladder, always including the ends."""
    if count < 2:
        return [lo, hi]
    if hi <= lo:
        return [lo]
 
    raw = (hi - lo) / (count - 1)
    mag = 10 ** math.floor(math.log10(raw)) if raw > 0 else 1
    step = next((m * mag for m in (1, 2, 2.5, 5, 10) if raw <= m * mag), 10 * mag)
 
    ticks = []
    v = math.ceil(lo / step) * step
    while v <= hi + step * 1e-9:
        ticks.append(round(v, 10))
        v += step
 
    for edge in (lo, hi):
        if not any(abs(t - edge) < step * 0.35 for t in ticks):
            ticks.append(edge)
    return sorted(set(ticks))
 
 
def _fmt_tick(value, spec, suffix):
    if callable(spec):
        return str(spec(value))
    if isinstance(spec, str):
        return spec.format(value) + suffix
    text = f"{value:g}" if abs(value - round(value)) > 1e-9 else f"{round(value):g}"
    return text + suffix
 
 
_GRAPH_RADIUS = Radius.md    # captured before Graph shadows `Radius` with a param
_GRAPH_DOT = Radius.full     # same reason — Radius is a param name inside Graph
 
 
def Graph(*Series, Color=None, Stroke=2.5, Curved=True, Smoothness=0.35,
          Area=True, AreaOpacity=0.35, Dots=False, Dash=None,
          MinX=None, MaxX=None, MinY=None, MaxY=None, PadY=0.0,
          XTicks=6, YTicks=5, XFormat=None, YFormat=None,
          XSuffix="", YSuffix="", LabelSize=11, LabelColor=None,
          Grid=True, GridColor=None, VGrid=False, Axis=False,
          Height=220, FullWidth=None, Fill=False, Bg=None, Pad=Space.md,
          Radius=_GRAPH_RADIUS, Border=False, Tooltip=True, Interactive=True,
          Legend=False, Name=None, Width=None):
 
    total_width = FullWidth if FullWidth is not None else Width
 
    label_color = LabelColor or Colors.muted_fg
    grid_color = GridColor or Alpha(Colors.border, 0.35)
    palette = [Colors.chart_1, Colors.chart_2, Colors.chart_3,
               Colors.chart_4, Colors.chart_5]
 
    # ── series normalisation ────────────
    def _spec(series, index):
        if isinstance(series, dict):
            spec = dict(series)
            raw = spec.get("Values", spec.get("Points", []))
        else:
            spec = {}
            raw = series
 
        pts = []
        for i, item in enumerate(raw or []):
            if isinstance(item, (tuple, list)) and len(item) >= 2:
                pts.append((float(item[0]), float(item[1])))
            else:
                pts.append((float(i), float(item)))
 
        base = Color or palette[index % len(palette)]
        return {
            "points": pts,
            "color": spec.get("Color", base),
            "label": spec.get("Label"),
            "area": spec.get("Area", Area),
            "stroke": spec.get("Stroke", Stroke),
            "curved": spec.get("Curved", Curved),
            "dash": spec.get("Dash", Dash),
            "dots": spec.get("Dots", Dots),
        }
 
    def _specs(series_list):
        return [_spec(s, i) for i, s in enumerate(series_list)]
 
    def _bounds(specs):
        xs = [p[0] for s in specs for p in s["points"]]
        ys = [p[1] for s in specs for p in s["points"]]
        if not xs:
            return 0.0, 1.0, 0.0, 1.0
 
        lo_x = MinX if MinX is not None else min(xs)
        hi_x = MaxX if MaxX is not None else max(xs)
        lo_y = min(ys)
        hi_y = max(ys)
        if PadY:
            span = (hi_y - lo_y) or abs(hi_y) or 1.0
            lo_y -= span * PadY
            hi_y += span * PadY
        lo_y = MinY if MinY is not None else lo_y
        hi_y = MaxY if MaxY is not None else hi_y
        if hi_y == lo_y:
            hi_y = lo_y + 1
        if hi_x == lo_x:
            hi_x = lo_x + 1
        return lo_x, hi_x, lo_y, hi_y
 
    def _axis_labels(lo, hi, count, spec, suffix, bottom):
        labels = []
        for value in _nice_ticks(lo, hi, count):
            text = ft.Text(
                _fmt_tick(value, spec, suffix),
                size=LabelSize,
                color=label_color,
                weight=Weight.sm,
                no_wrap=True,
            )
            labels.append(
                _graph_kw(
                    fch.ChartAxisLabel,
                    value=value,
                    label=ft.Container(content=text, margin=ft.Margin(top=6))
                    if bottom else text,
                )
            )
        return labels
 
    def _series_controls(specs):
        out = []
        for s in specs:
            kw: "dict[str, object]" = dict(
                points=[fch.LineChartDataPoint(x, y) for x, y in s["points"]],
                color=s["color"],
                stroke_width=s["stroke"],
                curved=s["curved"],
                curve_smoothness=Smoothness,
                rounded_stroke_cap=True,
                point=True if s["dots"] else False,
            )
            if s["dash"]:
                kw["dash_pattern"] = list(s["dash"])
            if s["area"]:
                kw["below_line_gradient"] = ft.LinearGradient(
                    begin=ft.Alignment.TOP_CENTER,
                    end=ft.Alignment.BOTTOM_CENTER,
                    colors=[Alpha(s["color"], AreaOpacity), Alpha(s["color"], 0.0)],
                )
            out.append(_graph_kw(fch.LineChartData, **kw))
        return out
 
    specs = _specs(list(Series))
    lo_x, hi_x, lo_y, hi_y = _bounds(specs)
 
    chart = fch.LineChart(
        data_series=_series_controls(specs),
        min_x=lo_x, max_x=hi_x, min_y=lo_y, max_y=hi_y,
        interactive=Interactive,
        expand=True,
        bgcolor=ft.Colors.TRANSPARENT,
        border=ft.Border(bottom=ft.BorderSide(1, Alpha(Colors.border, 0.6)))
        if Axis else None,
        horizontal_grid_lines=_graph_kw(
            fch.ChartGridLines, color=grid_color, width=1,
            interval=(hi_y - lo_y) / max(YTicks - 1, 1),
        ) if Grid else None,
        vertical_grid_lines=_graph_kw(
            fch.ChartGridLines, color=grid_color, width=1,
            interval=(hi_x - lo_x) / max(XTicks - 1, 1),
        ) if VGrid else None,
        left_axis=_graph_kw(
            fch.ChartAxis, label_size=44,
            labels=_axis_labels(lo_y, hi_y, YTicks, YFormat, YSuffix, False),
        ),
        bottom_axis=_graph_kw(
            fch.ChartAxis, label_size=32,
            labels=_axis_labels(lo_x, hi_x, XTicks, XFormat, XSuffix, True),
        ),
        right_axis=_graph_kw(fch.ChartAxis, show_labels=False),
        top_axis=_graph_kw(fch.ChartAxis, show_labels=False),
        tooltip=_graph_kw(
            fch.LineChartTooltip, bgcolor=Colors.popover,
        ) if Tooltip else None,
    )
 
    # ── optional legend ─────────────────
    def _legend(specs):
        chips: "list[ft.Control]" = []
        for s in specs:
            if not s["label"]:
                continue
            chips.append(
                ft.Row(
                    controls=[
                        ft.Container(width=8, height=8, bgcolor=s["color"],
                                     border_radius=_GRAPH_DOT),
                        ft.Text(s["label"], size=LabelSize, color=label_color),
                    ],
                    spacing=Space.xs,
                    tight=True,
                )
            )
        if not chips:
            return None
        return ft.Row(controls=chips, spacing=Space.md, wrap=True)
 
    body: "list[ft.Control]" = [chart]
    legend_row = _legend(specs) if Legend else None
    if legend_row is not None:
        body.append(legend_row)
 
    outer = ft.Container(
        content=ft.Column(controls=body, spacing=Space.sm, expand=True),
        bgcolor=Bg if Bg is not None else ft.Colors.TRANSPARENT,
        border=ft.Border.all(1, Colors.border) if Border else None,
        border_radius=Radius,
        padding=ft.Padding(Pad, Pad, Pad, Pad),
        height=None if Fill else Height,
        width=total_width,
        expand=bool(Fill) and total_width is None,
    )
 
    def _rebuild(series_list):
        new_specs = _specs(list(series_list))
        a, b, c, d = _bounds(new_specs)
        chart.data_series = _series_controls(new_specs)
        chart.min_x, chart.max_x, chart.min_y, chart.max_y = a, b, c, d
        chart.left_axis = _graph_kw(
            fch.ChartAxis, label_size=44,
            labels=_axis_labels(c, d, YTicks, YFormat, YSuffix, False),
        )
        chart.bottom_axis = _graph_kw(
            fch.ChartAxis, label_size=32,
            labels=_axis_labels(a, b, XTicks, XFormat, XSuffix, True),
        )
        try:
            chart.update()
        except Exception:
            pass  # not mounted yet — renders with the new data on first draw
 
    if Name is not None:
        Name.control = outer
        Name.Data = GraphHandle(list(Series), _rebuild)
 
    return outer



_MENU_RADIUS = Radius.lg  # captured before Select shadows `Radius` with a param
def Select(*Options, Value=None, Placeholder="Select", Width=166, Height=30,
           Variant="Outline", Icon="expand_more", IconSize=18, TextSize=12,
           Radius=Radius.md, Pad=Space.sm, MenuWidth=None, Change=None, Name=None):
    """A dropdown that remembers what you picked.
 
    Options are either "Label" strings, or ("Label", value) pairs when the
    display text differs from the value you want back:
 
        Select(("0.5 oz", 0.5), ("1 oz", 1.0), ("2 oz", 2.0), Value=1.0, Name=Cu)
 
    Read the selection with `Cu.Data`. `Change` is called with the new value.
 
    Unlike Button(Dropdown=True), the trigger label updates on pick and the
    value is held on the Name, so no external state juggling is needed.
    """
    # Normalise to [(label, value)]
    pairs = []
    for opt in Options:
        if isinstance(opt, (tuple, list)) and len(opt) == 2:
            pairs.append((str(opt[0]), opt[1]))
        else:
            pairs.append((str(opt), opt))
 
    # Resolve the starting label from Value (match on value, then on label)
    start_label, start_value = Placeholder, None
    if Value is not None:
        for lbl, val in pairs:
            if val == Value or lbl == Value:
                start_label, start_value = lbl, val
                break
 
    if Variant == "Primary":
        bgColor, fgColor = Colors.primary, Colors.primary_fg
        hoverBg, borderColor = Alpha(Colors.primary, 0.9), None
    elif Variant == "Secondary":
        bgColor, fgColor = Colors.bg_secondary, Colors.secondary_fg
        hoverBg, borderColor = Alpha(Colors.bg_secondary, 0.8), None
    elif Variant == "Ghost":
        bgColor, fgColor = ft.Colors.TRANSPARENT, Colors.fg
        hoverBg, borderColor = Colors.accent, None
    else:  # Outline — matches Button(Variant="Outline")
        bgColor, fgColor = ft.Colors.TRANSPARENT, Colors.fg
        hoverBg, borderColor = Colors.accent, Colors.border
 
    label_text = ft.Text(
        start_label,
        size=TextSize,
        color=fgColor if start_value is not None else Colors.muted_fg,
        max_lines=1,
        overflow=ft.TextOverflow.ELLIPSIS,
    )
 
    if Name is not None:
        Name.control = label_text
        Name.Data = start_value
 
    def _make_pick(lbl, val):
        def _pick(e):
            label_text.value = lbl
            label_text.color = fgColor
            label_text.update()
            if Name is not None:
                Name.Data = val
            if Change is not None:
                # Call as Change(value) if it takes an arg, else Change()
                try:
                    takes_arg = bool(inspect.signature(Change).parameters)
                except (TypeError, ValueError):
                    takes_arg = False
                Change(val) if takes_arg else Change()
        return _pick
 
    items: list[ft.Control] = [
        ft.MenuItemButton(
            content=ft.Text(lbl, size=14, color=Colors.fg),
            on_click=_make_pick(lbl, val),
            height=28,
            style=ft.ButtonStyle(
                bgcolor={
                    ft.ControlState.HOVERED: Colors.accent,
                    ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
                },
                overlay_color=Alpha(Colors.primary, 0),
                shape=ft.RoundedRectangleBorder(radius=Radius),
                padding=ft.Padding(Space.sm, 0, Space.sm, 0),
                mouse_cursor=Cursors.hand,
                visual_density=ft.VisualDensity.COMPACT,
            ),
        )
        for lbl, val in pairs
    ]
 
    # Same popover card treatment as DropdownMenu() so Select and
    # Button(Dropdown=True) menus look identical.
    visual_card = ft.Container(
        content=ft.Column(controls=items, spacing=0, tight=True),
        bgcolor=Colors.popover,
        border_radius=_MENU_RADIUS,
        padding=ft.Padding(Space.xs, Space.xs, Space.xs, Space.xs),
        margin=ft.Margin(Pad, 0, Pad, 0),
        width=MenuWidth or Width,
        border=ft.Border.all(1, Colors.border),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=6,
            color=Alpha(Colors.black, 0.12),
            offset=ft.Offset(0, 2),
        ),
    )
 
    chevron = None
    chevron_name = _resolve_icon_name(Icon, None)
    if chevron_name:
        chevron = ft.Icon(
            getattr(ft.Icons, chevron_name.upper()),
            size=IconSize,
            color=Colors.muted_fg,
        )
 
    trigger_controls: list[ft.Control] = [label_text]
    if chevron is not None:
        trigger_controls.append(chevron)

    trigger = ft.Row(
        controls=trigger_controls,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=Space.sm,
        width=(Width - Space.md) if Width else None,
    )
 
    submenu = ft.SubmenuButton(
        content=trigger,
        controls=[visual_card],
        height=Height,
        width=Width,
        alignment_offset=(-Space.sm, Space.sm),
        style=ft.ButtonStyle(
            bgcolor={
                ft.ControlState.HOVERED: hoverBg,
                ft.ControlState.DEFAULT: bgColor,
            },
            color={
                ft.ControlState.HOVERED: Colors.fg if Variant != "Primary" else fgColor,
                ft.ControlState.DEFAULT: fgColor,
            },
            shape=ft.RoundedRectangleBorder(radius=Radius),
            padding=Pads(Space.sm, 0),
            mouse_cursor=Cursors.hand,
            elevation=0,
            shadow_color=ft.Colors.TRANSPARENT,
            overlay_color=Alpha(Colors.primary, 0),
            visual_density=ft.VisualDensity.COMPACT,
            side={ft.ControlState.DEFAULT: ft.BorderSide(0.8, borderColor)} if borderColor else None,
        ),
        menu_style=ft.MenuStyle(
            bgcolor=ft.Colors.TRANSPARENT,
            shadow_color=ft.Colors.TRANSPARENT,
            elevation=0,
            padding=0,
            shape=ft.RoundedRectangleBorder(radius=_MENU_RADIUS),
        ),
    )
 
    return ft.Container(
        content=ft.MenuBar(
            controls=[submenu],
            style=ft.MenuStyle(
                bgcolor=ft.Colors.TRANSPARENT,
                shadow_color=ft.Colors.TRANSPARENT,
                elevation=0,
                padding=0,
                shape=ft.RoundedRectangleBorder(radius=Radius),
                visual_density=ft.VisualDensity.COMPACT,
            ),
        ),
        height=Height,
        width=Width,
    )
