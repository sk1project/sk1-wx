# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013 by Igor E. Novikov
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
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import wx
import wal

from sk1 import _, appconst, events, config
from sk1.resources import icons, get_icon, pdids


class AppStubPanel(wal.StubPanel):
    app = None

    def __init__(self, mw):
        self.app = mw.app
        self.bmp = get_icon(icons.CAIRO_BANNER, size=wal.DEF_SIZE)
        wal.StubPanel.__init__(self, mw)
        self.set_bg(wal.DARK_GRAY)

        action = self.app.actions[wal.ID_NEW]
        tooltip = action.get_descr_text()
        self.buttons.append(StubButton(self, icons.PD_STUB_NEW, action, tooltip))

        action = self.app.actions[wal.ID_OPEN]
        tooltip = action.get_descr_text()
        self.buttons.append(StubButton(self, icons.PD_STUB_OPEN, action, tooltip))

        action = self.app.actions[pdids.ID_VIEW_LOG]
        tooltip = _('Open Recent')
        self.buttons.append(StubButton(self, icons.PD_STUB_RECENT, action, tooltip))
        self.buttons[-1].set_active(self.app.history.is_history())

        events.connect(events.HISTORY_CHANGED, self.check_history)
        events.connect(events.CONFIG_MODIFIED, self.update)

    def update(self, *args):
        if args[0] == 'show_stub_buttons':
            self.buttons_visible = config.show_stub_buttons
            self.refresh()

    def check_history(self, *args):
        self.buttons[-1].set_active(self.app.history.is_history())


class StubButton(wx.Panel):
    action = None
    icon = None
    state = appconst.NORMAL
    mouse_over = False
    mouse_pressed = False
    normal_bmp = None
    disabled_bmp = None
    active_bmp = None
    pressed_bmp = None

    def __init__(self, parent, icon, action, tooltip=''):
        self.action = action
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wal.DARK_GRAY)
        self.icon = get_icon(icon, size=wal.DEF_SIZE)
        self._set_bmp()
        self.SetSize(self.icon.GetSize())

        if tooltip:
            self.SetToolTipString(tooltip)

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_PAINT, self._on_paint, self)
        self.Bind(wx.EVT_ENTER_WINDOW, self._mouse_over, self)
        self.Bind(wx.EVT_LEFT_DOWN, self._mouse_down, self)
        self.Bind(wx.EVT_LEFT_UP, self._mouse_up, self)
        self.Bind(wx.EVT_TIMER, self._on_timer)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_win_leave, self)

    def _set_bmp(self):
        image = self.icon.ConvertToImage()
        image = image.AdjustChannels(1.0, 1.0, 1.0, .1)
        self.disabled_bmp = image.ConvertToBitmap()
        image.Replace(0, 0, 0, 255, 255, 255)
        image = image.AdjustChannels(1.0, 1.0, 1.0, 3.0)
        self.normal_bmp = image.ConvertToBitmap()
        image = self.icon.ConvertToImage()
        image.Replace(0, 0, 0, 255, 255, 255)
        image = image.AdjustChannels(1.0, 1.0, 1.0, .8)
        self.active_bmp = image.ConvertToBitmap()
        image = image.Blur(5)
        self.pressed_bmp = image.ConvertToBitmap()

    def set_visible(self, val):
        if val:
            self.Show()
        else:
            self.Hide()

    def set_active(self, val):
        if val:
            self.state = appconst.NORMAL
        else:
            self.state = appconst.DISABLED
        self.refresh()

    def refresh(self, x=0, y=0, w=0, h=0):
        if not w:
            w, h = self.GetSize()
        self.Refresh(rect=wx.Rect(x, y, w, h))

    def _on_paint(self, event):
        pdc = wx.PaintDC(self)
        dc = wx.GCDC(pdc)
        if self.state == appconst.NORMAL:
            dc.DrawBitmap(self.normal_bmp, 0, 0, True)
        elif self.state == appconst.ACTIVE:
            dc.DrawBitmap(self.active_bmp, 0, 0, True)
        elif self.state == appconst.PRESSED:
            dc.DrawBitmap(self.pressed_bmp, 0, 0, True)
        else:
            dc.DrawBitmap(self.disabled_bmp, 0, 0, True)

    def _mouse_over(self, event):
        if not self.state == appconst.DISABLED:
            self.mouse_over = True
            self.state = appconst.ACTIVE
            self.refresh()
            self.timer.Start(100)

    def _mouse_down(self, event):
        if not self.state == appconst.DISABLED:
            self.mouse_pressed = True
            self.state = appconst.PRESSED
            self.refresh()

    def _mouse_up(self, event):
        self.mouse_pressed = False
        if self.mouse_over:
            if self.action and not self.state == appconst.DISABLED:
                self.state = appconst.NORMAL
                self.refresh()
                self.action.do_call()

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
                self.state = appconst.NORMAL
                self.refresh()

    def _on_win_leave(self, event):
        self.timer.Stop()
        if self.mouse_over:
            self.mouse_over = False
            self.mouse_pressed = False
            self.state = appconst.NORMAL
            self.refresh()
