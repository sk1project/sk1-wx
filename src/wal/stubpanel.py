# -*- coding: utf-8 -*-
#
#  Copyright (C) 2018 by Igor E. Novikov
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import wx

from basic import Panel
import const


class StubPanel(Panel):
    bmp = None
    bmp_size = ()
    buttons = None
    buttons_visible = True

    def __init__(self, parent):
        Panel.__init__(self, parent)
        if self.bmp:
            self.bmp_size = self.bmp.GetSize()
        self.buttons = []

        self.Bind(wx.EVT_PAINT, self._on_paint, self)
        self.Bind(wx.EVT_SIZE, self._on_resize, self)

    def refresh(self, **kwargs):
        for item in self.buttons:
            item.set_visible(self.buttons_visible)
        w, h = self.GetSize()
        self.Refresh(rect=wx.Rect(0, 0, w, h))

    def _on_resize(self, event):
        if self.buttons:
            w0, h = self.buttons[0].GetSize()
            w = len(self.buttons) * w0
            win_w, win_h = self.GetSize()
            x = (win_w - w) / 2
            y = (win_h - h) / 3
            for item in self.buttons:
                item.SetPosition((x, y))
                x += w0
            self.refresh()

    def _on_paint(self, event):
        h = self.GetSize()[1]
        pdc = wx.PaintDC(self)
        dc = wx.GCDC(pdc)
        x = 10
        y = h - self.bmp_size[1] - 10
        dc.DrawBitmap(self.bmp, x, y, True)


NORMAL = 0
ACTIVE = 1
PRESSED = 2
DISABLED = -1


class StubBtn(wx.Panel):
    callback = None
    icon = None
    state = NORMAL
    mouse_over = False
    mouse_pressed = False
    bitmaps = None

    def __init__(self, parent, bg, icon, callback, tooltip=''):
        self.callback = callback
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(bg)
        self.icon = icon
        self._set_bmp()
        self.SetSize(self.icon.GetSize())

        if tooltip:
            self.SetToolTipString(const.tr(tooltip))

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_PAINT, self._on_paint, self)
        self.Bind(wx.EVT_ENTER_WINDOW, self._mouse_over, self)
        self.Bind(wx.EVT_LEFT_DOWN, self._mouse_down, self)
        self.Bind(wx.EVT_LEFT_UP, self._mouse_up, self)
        self.Bind(wx.EVT_TIMER, self._on_timer)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_win_leave, self)

    def _set_bmp(self):
        self.bitmaps = {}
        image = self.icon.ConvertToImage()
        image = image.AdjustChannels(1.0, 1.0, 1.0, .1)
        self.bitmaps[DISABLED] = image.ConvertToBitmap()
        image.Replace(0, 0, 0, 255, 255, 255)
        image = image.AdjustChannels(1.0, 1.0, 1.0, 3.0)
        self.bitmaps[NORMAL] = image.ConvertToBitmap()
        image = self.icon.ConvertToImage()
        image.Replace(0, 0, 0, 255, 255, 255)
        image = image.AdjustChannels(1.0, 1.0, 1.0, .8)
        self.bitmaps[ACTIVE] = image.ConvertToBitmap()
        image = image.Blur(5)
        self.bitmaps[PRESSED] = image.ConvertToBitmap()

    def set_visible(self, val):
        if val:
            self.Show()
        else:
            self.Hide()

    def set_active(self, val):
        if val:
            self.state = NORMAL
        else:
            self.state = DISABLED
        self.refresh()

    def refresh(self):
        w, h = self.GetSize()
        self.Refresh(rect=wx.Rect(0, 0, w, h))

    def _on_paint(self, event):
        pdc = wx.PaintDC(self)
        dc = wx.GCDC(pdc)
        dc.DrawBitmap(self.bitmaps[self.state], 0, 0, True)

    def _mouse_over(self, event):
        if not self.state == DISABLED:
            self.mouse_over = True
            self.state = ACTIVE
            self.refresh()
            self.timer.Start(100)

    def _mouse_down(self, event):
        if not self.state == DISABLED:
            self.mouse_pressed = True
            self.state = PRESSED
            self.refresh()

    def _mouse_up(self, event):
        self.mouse_pressed = False
        if self.mouse_over:
            if self.callback and not self.state == DISABLED:
                self.state = NORMAL
                self.refresh()
                self.callback()

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
                self.state = NORMAL
                self.refresh()

    def _on_win_leave(self, event):
        self.timer.Stop()
        if self.mouse_over:
            self.mouse_over = False
            self.mouse_pressed = False
            self.state = NORMAL
            self.refresh()
