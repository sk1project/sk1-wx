# -*- coding: utf-8 -*-
#
#  Copyright (C) 2015 by Ihor E. Novikov
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

from sk1 import modes
from generic import AbstractController


class EditorChooser(AbstractController):
    mode = modes.SHAPER_MODE
    target = None

    def __init__(self, canvas, presenter):
        AbstractController.__init__(self, canvas, presenter)

    def start_(self):
        sel_objs = self.selection.objs
        if not sel_objs:
            self.selection.clear()
        else:
            set_mode = self.canvas.set_mode
            self.target = obj = self.selection.objs[0]

            if self.target.is_container:
                set_mode = self.canvas.set_temp_mode
                self.selection.set([self.target.childs[0], ])
                obj = self.selection.objs[0]
            elif self.target.is_group:
                return
            elif self.target.is_pixmap:
                return

            if obj.is_curve:
                set_mode(modes.BEZIER_EDITOR_MODE)
            elif obj.is_rect:
                set_mode(modes.RECT_EDITOR_MODE)
            elif obj.is_circle:
                set_mode(modes.ELLIPSE_EDITOR_MODE)
            elif obj.is_polygon:
                set_mode(modes.POLYGON_EDITOR_MODE)
            elif obj.is_text:
                set_mode(modes.TEXT_EDITOR_MODE)
            else:
                self.selection.clear()

    def restore(self):
        if self.target and self.target.is_container:
            self.target.childs[0].update()
            self.target.update()
            if self.target.childs[0] == self.selection.objs[0]:
                self.selection.set([self.target, ])
        self.target = None

    def stop_(self):
        if self.target:
            self.selection.set([self.target, ])
            self.target = None

    def on_timer(self):
        self.timer.stop()
        self.start_()

    def mouse_down(self, event):
        pass

    def mouse_up(self, event):
        self.end = event.get_point()
        self.do_action()

    def mouse_move(self, event):
        pass

    def do_action(self, event=None):
        objs = self.canvas.pick_at_point(self.end)
        if objs and not objs[0] == self.target:
            self.selection.set([objs[0], ])
            self.timer.start()
