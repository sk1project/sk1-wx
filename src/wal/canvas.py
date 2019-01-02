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

import const
from basic import SizedPanel, SensitiveCanvas, Canvas, Panel


class RulerCanvas(SizedPanel, SensitiveCanvas):

    def __init__(self, parent, size=20, check_move=True):
        SizedPanel.__init__(self, parent)
        SensitiveCanvas.__init__(self, check_move=check_move)
        self.set_bg(const.WHITE)
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


RENDERING_DELAY = 25


class CanvasTimer(wx.Timer):
    delay = 0

    def __init__(self, parent, delay=0):
        self.delay = delay or RENDERING_DELAY
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
    mouse_captured = False
    kbproc = None

    def __init__(self, parent, rendering_delay=0):
        rendering_delay = rendering_delay or RENDERING_DELAY
        Panel.__init__(self, parent, allow_input=True,
                       style=wx.FULL_REPAINT_ON_RESIZE)
        Canvas.__init__(self, set_timer=False)
        self.set_bg(const.WHITE)
        self.timer = CanvasTimer(self, rendering_delay)
        self.Bind(wx.EVT_TIMER, self._on_timer)
        self.Bind(wx.EVT_ENTER_WINDOW, self.mouse_enter, self)
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.capture_lost)
        # ----- Keyboard binding
        self.Bind(wx.EVT_KEY_DOWN, self._on_key_down)
        self.Bind(wx.EVT_CHAR, self._on_char)
        # ----- Mouse binding
        self.Bind(wx.EVT_LEFT_DOWN, self._mouse_left_down)
        self.Bind(wx.EVT_LEFT_UP, self._mouse_left_up)
        self.Bind(wx.EVT_LEFT_DCLICK, self.mouse_left_dclick)
        self.Bind(wx.EVT_RIGHT_DOWN, self.mouse_right_down)
        self.Bind(wx.EVT_RIGHT_UP, self.mouse_right_up)
        self.Bind(wx.EVT_MIDDLE_DOWN, self.mouse_middle_down)
        self.Bind(wx.EVT_MIDDLE_UP, self.mouse_middle_up)
        self.Bind(wx.EVT_MOUSEWHEEL, self.mouse_wheel)
        self.Bind(wx.EVT_MOTION, self.mouse_move)

    def _on_key_down(self, event):
        key_code = event.GetKeyCode()
        modifiers = event.GetModifiers()
        if self.kbproc and not self.kbproc.on_key_down(key_code, modifiers):
                return
        event.Skip()

    def _on_char(self, event):
        modifiers = event.GetModifiers()
        unichar = unichr(event.GetUniChar())
        if self.kbproc and not self.kbproc.on_char(modifiers, unichar):
            return
        event.Skip()

    def _on_timer(self, event):
        self.on_timer()

    def on_timer(self):
        pass

    def mouse_enter(self, event):
        if const.IS_MSW:
            self.set_focus()

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

    def _mouse_left_down(self, event):
        self.capture_mouse()
        self.mouse_left_down(event)
        event.Skip()

    def mouse_left_down(self, event):
        pass

    def _mouse_left_up(self, event):
        self.release_mouse()
        self.mouse_left_up(event)

    def mouse_left_up(self, event):
        pass

    def mouse_left_dclick(self, event):
        pass

    def mouse_move(self, event):
        pass

    def mouse_right_down(self, event):
        pass

    def mouse_right_up(self, event):
        pass

    def mouse_middle_down(self, event):
        pass

    def mouse_middle_up(self, event):
        pass

    def mouse_wheel(self, event):
        pass
