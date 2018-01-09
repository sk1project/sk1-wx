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
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import wx

from basic import Panel


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

    def refresh(self):
        for item in self.buttons:
            item.set_visible(self.buttons_visible)
        w, h = self.GetSize()
        self.Refresh(rect=wx.Rect(0, 0, w, h))

    def _on_resize(self, event):
        if self.buttons:
            w0, h = self.buttons[0].GetSize()
            w = 3 * w0
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
