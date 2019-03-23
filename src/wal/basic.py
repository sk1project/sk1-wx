# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2013-2018 by Igor E. Novikov
#
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
#
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
#
# 	You should have received a copy of the GNU General Public License
# 	along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#   MacOS X env: export VERSIONER_PYTHON_PREFER_32_BIT=yes

import wx
import wx.lib.scrolledpanel as scrolled

import const
from const import FONT_SIZE, DEF_SIZE, tr
from mixins import WidgetMixin, DialogMixin
from renderer import copy_surface_to_bitmap


def new_id():
    return wx.NewId()


def cursor(path, bitmap_type, x=0, y=0):
    return wx.Cursor(tr(path), bitmap_type, x, y)


def stock_cursor(cursor_id):
    return wx.StockCursor(cursor_id)


class Application(wx.App):
    app_name = None

    mw = None
    mdi = None
    actions = {}

    def __init__(self, name='', redirect=False):
        wx.App.__init__(self, redirect=redirect)
        if name:
            self.set_app_name(name)
        const.set_ui_colors(const.UI_COLORS)
        self._set_font_size()

    def _set_font_size(self):
        dc = wx.MemoryDC()
        bmp = wx.EmptyBitmap(1, 1)
        dc.SelectObject(bmp)
        dc.SetFont(wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT))
        FONT_SIZE[0] = dc.GetTextExtent('D')[0]
        FONT_SIZE[1] = dc.GetCharHeight()
        dc.SelectObject(wx.NullBitmap)

    def set_app_name(self, name):
        self.app_name = name
        self.SetAppName(name)
        self.SetClassName(name)

    def update_actions(self):
        for item in self.actions.keys():
            self.actions[item].update()

    def call_after(self, *args):
        pass

    def run(self):
        if self.mw:
            self.SetTopWindow(self.mw)
            if self.mw.maximized:
                self.mw.Maximize()
            self.mw.build()
            if self.actions:
                self.update_actions()
            self.mw.Show(True)
            self.mdi = self.mw.mdi
            wx.CallAfter(self.call_after)
            self.MainLoop()
        else:
            raise RuntimeError('Main window is not defined!')

    def exit(self, *args):
        self.Exit()


class MainWindow(wx.Frame, DialogMixin):
    app = None
    mdi = None
    maximized = False

    def __init__(self, app=None, title='Frame', size=(100, 100),
                 vertical=True, maximized=False, on_close=None):
        self.app = app
        if app is None:
            self.app = Application()
            self.app.mw = self
            on_close = self.app.exit
        self.maximized = maximized

        wx.Frame.__init__(self, None, wx.ID_ANY, title,
                          pos=DEF_SIZE, size=size, name=title)
        self.orientation = wx.VERTICAL if vertical else wx.HORIZONTAL
        self.Centre()
        self.box = wx.BoxSizer(self.orientation)
        self.SetSizer(self.box)
        self.set_title(title)
        if on_close:
            self.Bind(wx.EVT_CLOSE, on_close, self)

    def build(self):
        pass

    def run(self):
        self.app.run()

    def set_global_shortcuts(self, actions):
        global_entries = []
        for item in actions.keys():
            if actions[item].global_accs:
                for acc in actions[item].global_accs:
                    global_entries.append(acc)
                    self.Bind(wx.EVT_KEY_DOWN, actions[item], self,
                              id=acc.GetCommand())
        if global_entries:
            self.SetAcceleratorTable(wx.AcceleratorTable(global_entries))

    def hide(self):
        self.Hide()

    def show(self):
        self.Show()

    def add(self, *args, **kw):
        """Arguments: object, expandable (0 or 1), flag, border"""
        self.box.Add(*args, **kw)

    def pack(self, obj, expand=False, fill=False,
             padding=0, start_padding=0, end_padding=0):
        expand = 1 if expand else 0
        if self.orientation == wx.VERTICAL:
            flags = wx.ALIGN_TOP | wx.ALIGN_CENTER_HORIZONTAL
            flags = flags | wx.TOP | wx.BOTTOM if padding else flags
            flags = flags | wx.TOP if start_padding else flags
            flags = flags | wx.BOTTOM if end_padding else flags
            flags = flags | wx.EXPAND if fill else flags
            self.box.Add(obj, expand, flags, padding)
        else:
            flags = wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL
            flags = flags | wx.LEFT | wx.RIGHT if padding else flags
            flags = flags | wx.LEFT if start_padding else flags
            flags = flags | wx.RIGHT if end_padding else flags
            flags = flags | wx.EXPAND if fill else flags
            self.box.Add(obj, expand, flags, padding)

    def set_icons(self, filepath):
        icons = wx.IconBundle()
        icons.AddIconFromFile(tr(filepath), wx.BITMAP_TYPE_ANY)
        self.SetIcons(icons)

    def set_menubar(self, menubar):
        self.SetMenuBar(menubar)

    def bind_timer(self, callback):
        self.Bind(wx.EVT_TIMER, callback)

    def raise_window(self):
        self.Raise()


class Panel(wx.Panel, WidgetMixin):
    def __init__(self, parent, border=False, allow_input=False,
                 style=wx.TAB_TRAVERSAL):
        style = style | wx.WANTS_CHARS if allow_input else style
        style = style | wx.BORDER_MASK if border and not const.IS_WX3 else style
        wx.Panel.__init__(self, parent, wx.ID_ANY, style=style)

    def set_size(self, size):
        self.SetSize(size)

    def layout(self):
        self.Layout()

    def fit(self):
        self.Fit()


class SizedPanel(Panel):
    panel = None

    def __init__(self, parent, orientation=wx.HORIZONTAL, border=False):
        self.parent = parent
        self.orientation = orientation
        Panel.__init__(self, parent, border)
        self.box = wx.BoxSizer(orientation)
        self.SetSizer(self.box)
        self.panel = self

    def add(self, *args, **kw):
        """Arguments: object, expandable (0 or 1), flag, border"""
        obj = args[0]
        if not isinstance(obj, tuple):
            if not obj.GetParent() == self.panel:
                obj.Reparent(self.panel)
        self.box.Add(*args, **kw)
        if not isinstance(obj, tuple) and not isinstance(obj, int):
            obj.Show()

    def box_add(self, *args, **kw):
        """Arguments: object, expandable (0 or 1), flag, border"""
        self.box.Add(*args, **kw)

    def remove(self, obj):
        self.box.Detach(obj)
        if not isinstance(obj, tuple) and not isinstance(obj, int):
            obj.Hide()

    def remove_all(self):
        self.box.Clear()


class HPanel(SizedPanel):
    def __init__(self, parent, border=False):
        SizedPanel.__init__(self, parent, wx.HORIZONTAL, border)

    def pack(self, obj, expand=False, fill=False,
             padding=0, start_padding=0, end_padding=0, padding_all=0):
        expand = 1 if expand else 0
        flags = wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL
        flags = flags | wx.LEFT | wx.RIGHT if padding else flags
        flags = flags | wx.ALL if padding_all else flags
        padding = padding_all or padding
        flags = flags | wx.LEFT if start_padding else flags
        padding = start_padding or padding
        flags = flags | wx.RIGHT if end_padding else flags
        padding = end_padding or padding
        flags = flags | wx.EXPAND if fill else flags

        self.add(obj, expand, flags, padding)


class VPanel(SizedPanel):
    def __init__(self, parent, border=False):
        SizedPanel.__init__(self, parent, wx.VERTICAL, border)

    def pack(
            self, obj, expand=False, fill=False, align_center=True,
            padding=0, start_padding=0, end_padding=0, padding_all=0):
        expand = 1 if expand else 0
        flags = wx.ALIGN_TOP
        flags = flags | wx.ALIGN_CENTER_HORIZONTAL if align_center else flags
        flags = flags | wx.TOP | wx.BOTTOM if padding else flags
        flags = flags | wx.ALL if padding_all else flags
        padding = padding_all or padding
        flags = flags | wx.TOP if start_padding else flags
        padding = start_padding or padding
        flags = flags | wx.BOTTOM if end_padding else flags
        padding = end_padding or padding
        flags = flags | wx.EXPAND if fill else flags

        self.add(obj, expand, flags, padding)


class MouseEvent(object):
    event = None

    def __init__(self, event):
        self.event = event

    def get_point(self):
        return list(self.event.GetPositionTuple())

    def get_rotation(self):
        return self.event.GetWheelRotation()

    def is_ctrl(self):
        return self.event.ControlDown()

    def is_alt(self):
        return self.event.AltDown()

    def is_shift(self):
        return self.event.ShiftDown()

    def is_cmd(self):
        return self.event.CmdDown()


class Canvas(object):
    dc = None
    pdc = None
    dashes = None

    def __init__(self, set_timer=True, buffered=False):
        self.Bind(wx.EVT_PAINT, self._on_paint, self)
        self.Bind(wx.EVT_SIZE, self._on_size_change, self)
        if buffered:
            self.set_double_buffered()
        if set_timer and const.IS_MAC:
            self.timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self._repaint_after)
            self.timer.Start(50)

    def _repaint_after(self, event):
        self.repaint_after()
        self.timer.Stop()

    def set_double_buffered(self):
        if const.IS_MSW:
            self.SetDoubleBuffered(True)

    def get_size(self):
        return self.GetSizeTuple()

    def _on_size_change(self, event):
        self.refresh()
        event.Skip()

    def _on_paint(self, event):
        w, h = self.GetSize()
        if not w or not h:
            return
        self.pdc = wx.PaintDC(self)
        try:
            self.dc = wx.GCDC(self.pdc)
        except Exception:
            self.dc = self.pdc
        self.dc.BeginDrawing()

        self.paint()

        if not self.pdc == self.dc:
            self.dc.EndDrawing()
            self.pdc.EndDrawing()
        else:
            self.dc.EndDrawing()
        self.pdc = self.dc = None

    # Paint methods for inherited class
    def paint(self):
        pass

    def repaint_after(self):
        self.refresh()

    # ========PaintDC

    def set_origin(self, x=0, y=0):
        self.pdc.SetDeviceOrigin(x, y)

    def set_stroke(self, color=None, width=1, dashes=None):
        self.dashes = [] + dashes if dashes else []
        if color is None:
            self.pdc.SetPen(wx.TRANSPARENT_PEN)
        else:
            pen = wx.Pen(wx.Colour(*color), width)
            if dashes:
                pen = wx.Pen(wx.Colour(*color), width, wx.USER_DASH)
                pen.SetDashes(self.dashes)
            pen.SetCap(wx.CAP_BUTT)
            self.pdc.SetPen(pen)

    def set_fill(self, color=None):
        self.pdc.SetBrush(wx.TRANSPARENT_BRUSH if color is None
                          else wx.Brush(wx.Colour(*color)))

    def set_font(self, bold=False, size_incr=0):
        font = self.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL)
        if size_incr:
            if font.IsUsingSizeInPixels():
                sz = font.GetPixelSize()[1] + size_incr
                font.SetPixelSize((0, sz))
            else:
                sz = font.GetPointSize() + size_incr
                font.SetPointSize(sz)
        self.pdc.SetFont(font)
        return self.pdc.GetCharHeight()

    def set_text_color(self, color):
        self.pdc.SetTextForeground(wx.Colour(*color))

    def draw_line(self, x0, y0, x1, y1):
        self.pdc.DrawLine(x0, y0, x1, y1)

    def draw_rounded_rect(self, x=0, y=0, w=1, h=1, radius=1.0):
        self.pdc.DrawRoundedRectangle(x, y, w, h, radius)

    def draw_rect(self, x=0, y=0, w=1, h=1):
        self.pdc.DrawRectangle(x, y, w, h)

    def draw_text(self, text, x, y):
        self.pdc.DrawText(text, x, y)

    def draw_rotated_text(self, text, x, y, angle):
        self.pdc.DrawRotatedText(text, x, y, angle)

    def draw_polygon(self, points):
        self.pdc.DrawPolygon(points)

    def draw_surface(self, surface, x=0, y=0, use_mask=True):
        self.pdc.DrawBitmap(copy_surface_to_bitmap(surface), x, y, use_mask)

    def put_surface(self, surface, x=0, y=0, use_mask=True):
        dc = wx.ClientDC(self)
        dc.DrawBitmap(copy_surface_to_bitmap(surface), x, y, use_mask)

    def draw_linear_gradient(self, rect, start_clr, stop_clr, ndir=False):
        ndir = wx.SOUTH if ndir else wx.EAST
        self.pdc.GradientFillLinear(
            wx.Rect(*rect),
            wx.Colour(*start_clr),
            wx.Colour(*stop_clr),
            nDirection=ndir)

    def draw_bitmap(self, bmp, x=0, y=0, use_mask=True):
        self.pdc.DrawBitmap(bmp, x, y, use_mask)

    # =========GC device

    def set_gc_origin(self, x=0, y=0):
        self.dc.SetDeviceOrigin(x, y)

    def set_gc_stroke(self, color=None, width=1, dashes=None):
        self.dashes = [] + dashes if dashes else []
        if color is None:
            self.dc.SetPen(wx.TRANSPARENT_PEN)
        else:
            pen = wx.Pen(wx.Colour(*color), width)
            if self.dashes:
                pen = wx.Pen(wx.Colour(*color), width, wx.USER_DASH)
                pen.SetDashes(self.dashes)
            pen.SetCap(wx.CAP_BUTT)
            self.dc.SetPen(pen)

    def set_gc_fill(self, color=None):
        self.dc.SetBrush(wx.TRANSPARENT_BRUSH if color is None
                         else wx.Brush(wx.Colour(*color)))

    def set_gc_font(self, bold=False, size_incr=0):
        font = self.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL)
        if size_incr:
            if font.IsUsingSizeInPixels():
                sz = font.GetPixelSize() + size_incr
                font.SetPixelSize(sz)
            else:
                sz = font.GetPointSize() + size_incr
                font.SetPointSize(sz)
        self.dc.SetFont(font)
        return self.dc.GetCharHeight()

    def set_gc_text_color(self, color):
        self.dc.SetTextForeground(wx.Colour(*color))

    def gc_draw_rounded_rect(self, x=0, y=0, w=1, h=1, radius=1.0):
        self.dc.DrawRoundedRectangle(x, y, w, h, radius)

    def gc_draw_line(self, x0, y0, x1, y1):
        self.dc.DrawLine(x0, y0, x1, y1)

    def gc_draw_rect(self, x=0, y=0, w=1, h=1):
        self.dc.DrawRectangle(x, y, w, h)

    def gc_draw_polygon(self, points):
        self.dc.DrawPolygon(points)

    def gc_draw_text(self, text, x, y):
        self.dc.DrawText(text, x, y)

    def gc_draw_rotated_text(self, text, x, y, angle):
        self.dc.DrawRotatedText(text, x, y, angle)

    def gc_draw_surface(self, surface, x=0, y=0, use_mask=True):
        self.dc.DrawBitmap(copy_surface_to_bitmap(surface), x, y, use_mask)

    def gc_draw_linear_gradient(self, rect, start_clr, stop_clr, ndir=False):
        ndir = wx.SOUTH if ndir else wx.EAST
        self.dc.GradientFillLinear(
            wx.Rect(*rect),
            wx.Colour(*start_clr),
            wx.Colour(*stop_clr),
            nDirection=ndir)

    def gc_draw_bitmap(self, bmp, x=0, y=0, use_mask=True):
        self.dc.DrawBitmap(bmp, x, y, use_mask)


class SensitiveCanvas(Canvas):
    kbdproc = None
    mouse_captured = False
    click_flag = False

    def __init__(self, check_move=False, kbdproc=None):
        Canvas.__init__(self)
        self.kbdproc = kbdproc
        self.Bind(wx.EVT_LEFT_UP, self._mouse_left_up)
        self.Bind(wx.EVT_LEFT_DOWN, self._mouse_left_down)
        self.Bind(wx.EVT_MOUSEWHEEL, self._mouse_wheel)
        self.Bind(wx.EVT_RIGHT_DOWN, self._mouse_right_down)
        self.Bind(wx.EVT_RIGHT_UP, self._mouse_right_up)
        self.Bind(wx.EVT_LEFT_DCLICK, self._mouse_left_dclick)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._mouse_leave)
        if check_move:
            self.Bind(wx.EVT_MOTION, self._mouse_move)
            self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self._capture_lost)
        if self.kbdproc is not None:
            self.Bind(wx.EVT_KEY_DOWN, self._on_key_down)

    def _on_key_down(self, event):
        key_code = event.GetKeyCode()
        raw_code = event.GetRawKeyCode()
        modifiers = event.GetModifiers()
        if self.kbdproc.on_key_down(key_code, raw_code, modifiers):
            event.Skip()

    def capture_mouse(self):
        if const.IS_MSW:
            self.mouse_captured = True
            self.CaptureMouse()

    def release_mouse(self):
        if self.mouse_captured:
            self.mouse_captured = False
            self.ReleaseMouse()

    def _mouse_leave(self, event):
        self.mouse_leave(event.GetPositionTuple())

    def _mouse_left_down(self, event):
        self.mouse_left_down(event.GetPositionTuple())

    def _mouse_left_up(self, event):
        if not self.click_flag:
            self.click_flag = True
            self.mouse_left_up(event.GetPositionTuple())
            self.click_flag = False

    def _mouse_right_down(self, event):
        self.mouse_right_down(event.GetPositionTuple())

    def _mouse_right_up(self, event):
        self.mouse_right_up(event.GetPositionTuple())

    def _mouse_wheel(self, event):
        self.mouse_wheel(event.GetWheelRotation())

    def _mouse_move(self, event):
        self.mouse_move(event.GetPositionTuple())

    def _capture_lost(self, event):
        self.capture_lost()

    def _mouse_left_dclick(self, event):
        self.mouse_left_dclick(event.GetPositionTuple())

    def mouse_leave(self, point):
        pass

    def mouse_left_down(self, point):
        pass

    def mouse_left_up(self, point):
        pass

    def mouse_right_down(self, point):
        pass

    def mouse_right_up(self, point):
        pass

    def mouse_wheel(self, val):
        pass

    def mouse_move(self, point):
        pass

    def capture_lost(self):
        pass

    def mouse_left_dclick(self, point):
        pass


class RoundedPanel(VPanel, Canvas):
    widget_panel = None

    def __init__(self, parent):
        VPanel.__init__(self, parent)
        Canvas.__init__(self)

    def paint(self):
        w, h = self.get_size()
        dx = 8
        dy = 0
        if self.widget_panel:
            dx += self.widget_panel.get_size()[0]
            dy += self.widget_panel.get_size()[1] // 2
        self.set_fill(None)
        color = const.UI_COLORS['light_shadow']
        self.set_stroke(color)
        self.draw_line(1, dy + 1, 6, dy + 1)
        self.draw_line(1, dy + 1, 1, h - 1)
        self.draw_line(1, h - 1, w - 1, h - 1)
        self.draw_line(w - 1, h - 1, w - 1, dy + 1)
        self.draw_line(w - 1, dy + 1, dx, dy + 1)
        color = const.UI_COLORS['dark_shadow']
        self.set_stroke(color)
        self.draw_line(0, dy, 6, dy)
        self.draw_line(0, dy, 0, h - 2)
        self.draw_line(0, h - 2, w - 2, h - 2)
        self.draw_line(w - 2, h - 2, w - 2, dy)
        self.draw_line(w - 2, dy, dx - 1, dy)
        self.layout()
        if self.widget_panel:
            self.widget_panel.refresh()


class LabeledPanel(RoundedPanel):
    panel = None
    widget_panel = None
    widget = None

    def __init__(self, parent, text='', widget=None):
        RoundedPanel.__init__(self, parent)
        self.inner_panel = VPanel(self)

        if widget or text:
            self.widget_panel = HPanel(self)
            self.widget = widget
            if text:
                self.widget = wx.StaticText(self.widget_panel,
                                            wx.ID_ANY, tr(text))
            self.widget_panel.pack(self.widget, padding=5)
            self.widget_panel.Fit()
            self.add(self.widget_panel, 0, wx.ALIGN_LEFT | wx.LEFT, 7)

        self.add(self.inner_panel, 1,
                 wx.ALIGN_LEFT | wx.LEFT | wx.BOTTOM | wx.RIGHT | wx.EXPAND, 5)
        self.parent.refresh()

    def pack(self, *args, **kw):
        obj = args[0]
        self.inner_panel.pack(*args, **kw)
        if not isinstance(obj, tuple) and not isinstance(obj, int):
            obj.show()


class GridPanel(Panel, WidgetMixin):
    def __init__(self, parent, rows=2, cols=2, vgap=0, hgap=0, border=False):
        Panel.__init__(self, parent, border)
        self.grid = wx.FlexGridSizer(rows, cols, vgap, hgap)
        self.SetSizer(self.grid)

    def set_vgap(self, val):
        self.grid.SetVGap(val)

    def set_hgap(self, val):
        self.grid.SetHGap(val)

    def sel_cols(self, val):
        self.grid.SetCols(val)

    def sel_rows(self, val):
        self.grid.SetRows(val)

    def add_growable_col(self, index):
        self.grid.AddGrowableCol(index)

    def add_growable_row(self, index):
        self.grid.AddGrowableRow(index)

    def pack(self, obj, expand=False, fill=False, align_right=False,
             align_left=True):
        expand = 1 if expand else 0
        flags = wx.ALIGN_CENTER_HORIZONTAL
        flags = wx.ALIGN_RIGHT if align_right else flags
        flags = wx.ALIGN_LEFT if align_left else flags
        flags |= wx.ALIGN_CENTER_VERTICAL
        flags = flags | wx.EXPAND if fill else flags
        self.add(obj, expand, flags)

    def add(self, *args, **kw):
        """Arguments: object, expandable (0 or 1), flag"""
        obj = args[0]
        if not isinstance(obj, tuple):
            if not obj.GetParent() == self:
                obj.Reparent(self)
        self.grid.Add(*args, **kw)
        if not isinstance(obj, tuple) and not isinstance(obj, int):
            obj.show()


class ScrolledPanel(scrolled.ScrolledPanel, WidgetMixin):
    def __init__(self, parent):
        scrolled.ScrolledPanel.__init__(self, parent, -1)
        self.box = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.box)
        self.SetAutoLayout(1)
        self.SetupScrolling()
        self.panel = self

    def set_size(self, size):
        self.SetSize(size)

    def layout(self):
        self.Layout()

    def fit(self):
        self.Fit()

    def pack(self, obj, expand=False, fill=False, align_center=True,
             padding=0, start_padding=0, end_padding=0, padding_all=0):
        expand = 1 if expand else 0

        flags = wx.ALIGN_TOP
        flags = flags | wx.ALIGN_CENTER_HORIZONTAL if align_center else flags
        flags = flags | wx.TOP | wx.BOTTOM if padding else flags
        flags = flags | wx.ALL if padding_all else flags
        padding = padding_all or padding
        flags = flags | wx.TOP if start_padding else flags
        padding = start_padding or padding
        flags = flags | wx.BOTTOM if end_padding else flags
        padding = end_padding or padding
        flags = flags | wx.EXPAND if fill else flags

        self.add(obj, expand, flags, padding)

    def add(self, *args, **kw):
        """Arguments: object, expandable (0 or 1), flag, border"""
        obj = args[0]
        if not isinstance(obj, tuple):
            if not obj.GetParent() == self.panel:
                obj.Reparent(self.panel)
        self.box.Add(*args, **kw)
        if not isinstance(obj, tuple) and not isinstance(obj, int):
            obj.Show()

    def box_add(self, *args, **kw):
        """Arguments: object, expandable (0 or 1), flag, border"""
        self.box.Add(*args, **kw)

    def remove(self, obj):
        self.box.Detach(obj)
        if not isinstance(obj, tuple) and not isinstance(obj, int):
            obj.Hide()

    def remove_all(self):
        self.box.Clear()


class ScrolledCanvas(wx.ScrolledWindow, WidgetMixin):
    def __init__(self, parent, border=False):
        style = wx.NO_BORDER
        if border and not const.IS_WX3:
            style = wx.BORDER_MASK
        wx.ScrolledWindow.__init__(self, parent, wx.ID_ANY, style=style)
        self.set_scroll_rate()
        self.set_double_buffered()

    def set_virtual_size(self, size):
        self.SetVirtualSize(size)

    def set_scroll_rate(self, h=20, v=20):
        self.SetScrollRate(h, v)

    def refresh(self, x=0, y=0, w=0, h=0, clear=True):
        if not w:
            w, h = self.GetVirtualSize()
        self.Refresh(rect=wx.Rect(x, y, w, h))

    def set_size(self, size):
        self.SetSize(size)

    def prepare_dc(self, dc):
        self.PrepareDC(dc)

    def win_to_doc(self, x, y):
        return tuple(self.CalcUnscrolledPosition(wx.Point(x, y)))

    def doc_to_win(self, x, y):
        return tuple(self.CalcScrolledPosition(wx.Point(x, y)))


class Expander(VPanel, Canvas):
    state = False
    callback = None

    def __init__(self, parent, on_click=None):
        VPanel.__init__(self, parent)
        Canvas.__init__(self)
        self.pack((13, 13))
        if on_click:
            self.callback = on_click
            self.Bind(wx.EVT_LEFT_UP, self._click, self)
            self.Bind(wx.EVT_RIGHT_UP, self._click, self)
        self.refresh()

    def _click(self, event):
        self.callback()

    def change(self, val=False):
        self.state = val
        self.refresh()

    def paint(self):
        w, h = self.get_size()
        self.set_stroke(const.BLACK, 1)
        self.set_fill(None)
        self.draw_rect(3, 3, w - 4, h - 4)
        half = int(w / 2.0) + 1
        self.draw_line(5, half, w - 3, half)
        if not self.state:
            self.draw_line(half, 5, half, h - 3)


class ExpandedPanel(VPanel):
    def __init__(self, parent, txt=''):
        VPanel.__init__(self, parent)
        header = HPanel(self)
        self.expander = Expander(header, on_click=self.expand)
        header.pack(self.expander, padding=2)
        if txt:
            header.pack(wx.StaticText(header, wx.ID_ANY, tr(txt)))
        VPanel.pack(self, header, fill=True)
        self.container = VPanel(self)
        VPanel.pack(self, self.container, fill=True)
        self.container.set_visible(False)
        self.layout()

    def expand(self):
        self.container.set_visible(not self.container.is_shown())
        self.parent.layout()
        self.expander.change(self.container.is_shown())

    def pack(self, *args, **kw):
        self.container.pack(*args, **kw)


class PLine(VPanel):
    def __init__(self, parent, color=()):
        VPanel.__init__(self, parent)
        self.pack((1, 1))
        self.set_bg(color or const.UI_COLORS['hover_solid_border'])


class HSizer(HPanel):
    def __init__(self, parent, grip_width=5, visible=True):
        HPanel.__init__(self, parent)
        self.client = None
        self.client_parent = None
        self.client_min = 0
        self.left_side = True
        self.move = False
        self.mouse_captured = False
        self.processing = False
        self.start = 0
        self.end = 0
        self.grip_width = grip_width
        self.visible = visible
        if self.visible:
            self.pack((self.grip_width, self.grip_width))
        self.Bind(wx.EVT_LEFT_DOWN, self.mouse_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.mouse_left_up)
        self.Bind(wx.EVT_MOTION, self.mouse_move)
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.capture_lost)
        self.SetCursor(wx.StockCursor(wx.CURSOR_SIZEWE))

    def set_client(self, client_parent, client, client_min=0, left_side=True):
        self.client = client
        self.client_parent = client_parent
        self.client_min = client_min
        self.left_side = left_side

    def resize(self):
        change = self.end - self.start
        if not change:
            return
        w = self.client.get_size()[0]
        w = w + change if self.left_side else w - change
        w = self.client_min if w < self.client_min else w
        self.client.remove_all()
        self.client.pack((w, 0))
        self.client_parent.Layout()

    def capture_mouse(self):
        if const.IS_MSW:
            self.CaptureMouse()
            self.mouse_captured = True

    def release_mouse(self):
        if self.mouse_captured:
            try:
                self.ReleaseMouse()
            except Exception:
                pass
            self.mouse_captured = False

    def capture_lost(self, event):
        self.release_mouse()

    def mouse_left_down(self, event):
        self.move = True
        self.capture_mouse()
        event = MouseEvent(event)
        self.start = self.end = event.get_point()[0]

    def mouse_left_up(self, event):
        self.release_mouse()
        self.move = False
        event = MouseEvent(event)
        self.end = event.get_point()[0]
        self.resize()

    def mouse_move(self, event):
        if self.move:
            if self.processing:
                return
            self.processing = True
            event = MouseEvent(event)
            self.end = event.get_point()[0]
            self.resize()
            self.processing = False
