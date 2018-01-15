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

import const
from basic import SizedPanel, SensitiveCanvas, Canvas, Panel


class RulerCanvas(SizedPanel, SensitiveCanvas):

    def __init__(self, parent, size=20, check_move=False):
        SizedPanel.__init__(self, parent)
        SensitiveCanvas.__init__(self, check_move=check_move)
        self.fix_size(size)
        self.set_double_buffered()

    def destroy(self):
        items = self.__dict__.keys()
        for item in items:
            self.__dict__[item] = None

    def fix_size(self, size=0):
        self.remove_all()
        size = size if size > 0 else 20
        self.add((size, size))
        self.parent.layout()


REDNDERING_DELAY = 25


class CanvasTimer(wx.Timer):
    delay = 0

    def __init__(self, parent, delay=0):
        self.delay = delay or REDNDERING_DELAY
        wx.Timer.__init__(self, parent)

    def is_running(self):
        return self.IsRunning()

    def stop(self):
        if self.IsRunning():
            self.Stop()

    def start(self, interval=0):
        if not self.IsRunning():
            self.Start(interval or self.delay)


class MainCanvas(Panel, Canvas):
    timer = None

    def __init__(self, parent, rendering_delay=0):
        rendering_delay = rendering_delay or REDNDERING_DELAY
        Panel.__init__(self, parent, allow_input=True,
                       style=wx.FULL_REPAINT_ON_RESIZE)
        Canvas.__init__(self, set_timer=False)
        self.set_bg(const.WHITE)
        self.timer = CanvasTimer(self, rendering_delay)
        self.Bind(wx.EVT_TIMER, self._on_timer)

    def _on_timer(self, event):
        self.on_timer()

    def on_timer(self):
        pass
