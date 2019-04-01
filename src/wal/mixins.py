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

import wx

import const
from const import tr, untr


class DialogMixin(object):
    def fit(self):
        self.Fit()

    def set_title(self, title):
        self.SetTitle(tr(title))

    def set_minsize(self, size):
        self.SetMinSize(size)

    def is_maximized(self):
        return self.IsMaximized()

    def maximize(self, val=True):
        self.Maximize(val)

    def center(self):
        self.Centre()

    def get_size(self):
        return self.GetSizeTuple()

    def set_size(self, size):
        self.SetSize(wx.Size(*size))

    def show_modal(self):
        return self.ShowModal()

    def end_modal(self, ret):
        self.EndModal(ret)

    def destroy(self):
        self.Destroy()

    def layout(self):
        self.Layout()

    def update(self):
        self.Update()


class WidgetMixin(object):
    shown = True
    enabled = True

    def set_position(self, point=(0, 0)):
        self.SetPosition(point)

    def show(self, update=True):
        self.Show()
        self.shown = True
        if update:
            parent = self.GetParent()
            parent.Layout()

    def hide(self, update=True):
        self.Hide()
        self.shown = False
        if update:
            parent = self.GetParent()
            parent.Layout()

    def get_size(self):
        return self.GetSizeTuple()

    def is_shown(self):
        return self.IsShown()

    def set_enable(self, value):
        self.enabled = value
        self.Enable(value)

    def set_visible(self, value):
        if value:
            self.show()
        else:
            self.hide()

    def get_enabled(self):
        return self.IsEnabled()

    def _set_width(self, size, width):
        if not width: return size
        width += 2
        return width * const.FONT_SIZE[0], size[1]

    def set_tooltip(self, tip=None):
        if tip:
            self.SetToolTipString(tr(tip))
        else:
            self.SetToolTip(None)

    def destroy(self):
        self.Destroy()

    def set_focus(self):
        self.SetFocus()

    def set_double_buffered(self):
        if const.IS_MSW:
            self.SetDoubleBuffered(True)

    def refresh(self, x=0, y=0, w=0, h=0, clear=True):
        if not w:
            w, h = self.GetSize()
        self.Refresh(rect=wx.Rect(x, y, w, h), eraseBackground=clear)

    def get_cursor(self):
        return self.GetCursor()

    def set_cursor(self, cursor):
        self.SetCursor(cursor)

    def set_bg(self, color):
        if isinstance(color, tuple):
            self.SetBackgroundColour(wx.Colour(*color))
        else:
            self.SetBackgroundColour(color)

    def get_bg(self):
        return self.GetBackgroundColour().Get()

    def popup_menu(self, menu):
        self.PopupMenu(menu)

    def set_drop_target(self, target):
        self.SetDropTarget(target)


class DataWidgetMixin(WidgetMixin):
    def set_value(self, value):
        self.SetValue(tr(value))

    def get_value(self):
        return untr(self.GetValue())


class RangeDataWidgetMixin(DataWidgetMixin):
    range_val = ()

    def set_range(self, range_val):
        self.range_val = range_val
        self.SetRange(*range_val)

    def get_range(self):
        return self.range_val


class GenericGWidget(wx.Panel, WidgetMixin):
    decoration_padding = 0

    renderer = None
    mouse_over = False
    mouse_pressed = False
    timer = None
    onclick = None
    repeat = False
    flat = True
    buffer = None
    counter = 0

    def __init__(self, parent, tooltip='', onclick=None, repeat=False):
        self.parent = parent
        self.onclick = onclick
        self.repeat = repeat
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        if const.IS_MSW:
            self.SetDoubleBuffered(True)
        self.box = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.box)
        self.box.Add((1, 1))
        if tooltip:
            self.set_tooltip(tooltip)

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_PAINT, self._on_paint, self)
        self.Bind(wx.EVT_ENTER_WINDOW, self._mouse_over, self)
        self.Bind(wx.EVT_LEFT_DOWN, self._mouse_down, self)
        self.Bind(wx.EVT_LEFT_UP, self._mouse_up, self)
        self.Bind(wx.EVT_TIMER, self._on_timer)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_win_leave, self)

    def set_enable(self, value):
        self.enabled = value
        self.refresh()

    def get_enabled(self):
        return self.enabled

    def set_size(self, w, h):
        self._set_size(w, h)
        if self.renderer:
            self.renderer._adjust_widget_size()

    def _set_size(self, w, h):
        self.box.Remove(0)
        self.box.Add((w, h))
        self.GetParent().Layout()
        self.refresh()

    def _on_paint(self, event):
        pass

    def _mouse_over(self, event):
        self.mouse_over = True
        self.refresh()
        self.timer.Start(100)

    def _mouse_down(self, event):
        self.mouse_pressed = True
        self.refresh()

    def _mouse_up(self, event):
        self.mouse_pressed = False
        if self.mouse_over:
            if self.onclick and self.enabled and not self.counter:
                self.counter = 5
                self.onclick()
        self.refresh()

    def _on_timer(self, event):
        mouse_pos = wx.GetMousePosition()
        x, y = self.GetScreenPosition()
        w, h = self.GetSize()
        rect = wx.Rect(x, y, w, h)
        if not rect.Inside(mouse_pos):
            self.timer.Stop()
            if self.mouse_over:
                self.mouse_over = False
                self.mouse_pressed = False
                self.refresh()
        else:
            if self.enabled:
                self.counter = self.counter - 1 if self.counter else 0
                if self.repeat and self.onclick and self.mouse_pressed:
                    self.onclick()

    def _on_win_leave(self, event):
        self.timer.Stop()
        if self.mouse_over:
            self.mouse_over = False
            self.mouse_pressed = False
            self.refresh()
