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
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import wx

import const
import renderer
from const import DEF_SIZE, RIGHT
from mixins import GenericGWidget


class ImageLabel(GenericGWidget):
    rightclick_cmd = None

    def __init__(
            self, parent, art_id=None, art_size=DEF_SIZE, text='',
            tooltip='', padding=0,
            fontbold=False, fontsize=0, textplace=RIGHT,
            onclick=None, onrightclick=None, repeat=False):

        self.flat = True

        GenericGWidget.__init__(self, parent, tooltip, onclick, repeat)
        self.renderer = renderer.LabelRenderer(
            self, art_id, art_size, text,
            padding, fontbold, fontsize, textplace)

        if onrightclick:
            self.rightclick_cmd = onrightclick
            self.Bind(wx.EVT_RIGHT_UP, self._on_rightclick, self)

    def _on_rightclick(self, event):
        if self.rightclick_cmd:
            self.rightclick_cmd()

    def _on_paint(self, event):
        if self.enabled:
            self.renderer.draw_normal()
        else:
            self.renderer.draw_disabled()


class ImageButton(GenericGWidget):
    def __init__(
            self, parent, art_id=None, art_size=DEF_SIZE,
            text='', tooltip='', padding=0, decoration_padding=6,
            flat=True, native=True,
            fontbold=False, fontsize=0, textplace=RIGHT,
            onclick=None, repeat=False):

        self.flat = flat
        self.decoration_padding = decoration_padding

        GenericGWidget.__init__(self, parent, tooltip, onclick, repeat)

        if native:
            rndr = renderer.NativeButtonRenderer
        else:
            rndr = renderer.ButtonRenderer

        self.renderer = rndr(
            self, art_id, art_size, text,
            padding, fontbold, fontsize, textplace)

    def _on_paint(self, event):
        if self.enabled:
            if not self.mouse_over:
                self.renderer.draw_normal(self.flat)
            else:
                if self.mouse_pressed:
                    self.renderer.draw_pressed()
                else:
                    self.renderer.draw_hover()
        else:
            self.renderer.draw_disabled(self.flat)


class ImageToggleButton(GenericGWidget):
    value = False
    onchange = None

    def __init__(
            self, parent, value=False, art_id=None, art_size=DEF_SIZE,
            text='', tooltip='', padding=0, decoration_padding=6,
            flat=True, native=not const.IS_MAC,
            fontbold=False, fontsize=0, textplace=RIGHT,
            onchange=None):

        self.flat = flat
        self.decoration_padding = decoration_padding

        self.value = value
        self.onchange = onchange
        GenericGWidget.__init__(self, parent, tooltip)

        if native:
            rndr = renderer.NativeButtonRenderer
        else:
            rndr = renderer.ButtonRenderer

        self.renderer = rndr(
            self, art_id, art_size, text,
            padding, fontbold, fontsize, textplace)

    def set_value(self, value, silent=False):
        self.value = value
        if self.onchange and not silent:
            self.onchange()
        self.refresh()

    def set_active(self, value):
        self.value = value
        self.refresh()

    def get_value(self):
        return self.value

    def get_active(self):
        return self.value

    def _on_paint(self, event):
        if self.enabled:
            if not self.mouse_over and not self.value:
                self.renderer.draw_normal(self.flat)
            elif not self.mouse_over and self.value:
                self.renderer.draw_pressed()
            elif self.mouse_over and not self.value and not self.mouse_pressed:
                self.renderer.draw_hover()
            elif self.mouse_over and self.value and not self.mouse_pressed:
                self.renderer.draw_pressed()
            elif self.mouse_over and self.mouse_pressed:
                self.renderer.draw_pressed()
        else:
            if self.value:
                self.renderer.draw_pressed_disabled()
            else:
                self.renderer.draw_disabled(self.flat)

    def _mouse_up(self, event):
        self.mouse_pressed = False
        if self.mouse_over:
            if self.enabled:
                if self.value:
                    self.value = False
                else:
                    self.value = True
                if self.onchange:
                    self.onchange()
        self.refresh()
