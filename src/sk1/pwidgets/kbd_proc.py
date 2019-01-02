# -*- coding: utf-8 -*-
#
#  Copyright (C) 2015-2018 by Igor E. Novikov
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

import wal

from sk1 import modes
from sk1.resources import pdids


MAPPING = {
    (wal.KEY_DELETE, wal.ACCEL_NORMAL): wal.ID_DELETE,
    (wal.KEY_NUMPAD_DECIMAL, wal.ACCEL_NORMAL): wal.ID_DELETE,
    (wal.KEY_DELETE, wal.ACCEL_SHIFT): wal.ID_CUT,
    (wal.KEY_NUMPAD_DECIMAL, wal.ACCEL_SHIFT): wal.ID_CUT,
    (wal.KEY_NUMPAD0, wal.ACCEL_SHIFT): wal.ID_PASTE,
    (wal.KEY_UP, wal.ACCEL_NORMAL): pdids.MOVE_UP,
    (wal.KEY_NUMPAD_UP, wal.ACCEL_NORMAL): pdids.MOVE_UP,
    (wal.KEY_DOWN, wal.ACCEL_NORMAL): pdids.MOVE_DOWN,
    (wal.KEY_NUMPAD_DOWN, wal.ACCEL_NORMAL): pdids.MOVE_DOWN,
    (wal.KEY_LEFT, wal.ACCEL_NORMAL): pdids.MOVE_LEFT,
    (wal.KEY_NUMPAD_LEFT, wal.ACCEL_NORMAL): pdids.MOVE_LEFT,
    (wal.KEY_RIGHT, wal.ACCEL_NORMAL): pdids.MOVE_RIGHT,
    (wal.KEY_NUMPAD_RIGHT, wal.ACCEL_NORMAL): pdids.MOVE_RIGHT,
    (wal.KEY_U, wal.ACCEL_SHIFT|wal.ACCEL_CTRL): pdids.ID_UNGROUPALL,
}


class KbdProcessor:
    canvas = None

    def __init__(self, app):
        self.app = app
        self.actions = self.app.actions

    @property
    def painter(self):
        return self.app.current_doc.canvas

    def on_key_down(self, key_code, modifiers):

        if key_code == wal.KEY_ESCAPE and not modifiers:
            self.painter.controller.escape_pressed()
            return

        if self.painter.mode == modes.TEXT_EDIT_MODE:
            return self.text_edit_mode(key_code, modifiers)

        if (key_code, modifiers) in MAPPING:
            self.actions[MAPPING[(key_code, modifiers)]]()
            return

        if key_code == wal.KEY_SPACE and not modifiers:
            if self.painter.mode == modes.SELECT_MODE:
                self.painter.set_mode(modes.SHAPER_MODE)
                return
            elif self.painter.mode in modes.EDIT_MODES:
                self.painter.set_mode(modes.SELECT_MODE)
                return

        if key_code == wal.KEY_F2 and not modifiers:
            self.painter.set_mode(modes.ZOOM_MODE)
            return

        return True

    def text_edit_mode(self, key_code, modifiers):

        if key_code == wal.KEY_NUMPAD_DECIMAL and modifiers == wal.ACCEL_SHIFT:
            self.actions[wal.ID_CUT]()
            return

        if key_code == wal.KEY_NUMPAD0 and modifiers == wal.ACCEL_SHIFT:
            self.actions[wal.ID_PASTE]()
            return

        if not modifiers:
            if key_code in (wal.KEY_UP, wal.KEY_NUMPAD_UP):
                self.painter.controller.key_up()
                return
            if key_code in (wal.KEY_DOWN, wal.KEY_NUMPAD_DOWN):
                self.painter.controller.key_down()
                return
            if key_code in (wal.KEY_LEFT, wal.KEY_NUMPAD_LEFT):
                self.painter.controller.key_left()
                return
            if key_code in (wal.KEY_RIGHT, wal.KEY_NUMPAD_RIGHT):
                self.painter.controller.key_right()
                return
            if key_code in (wal.KEY_HOME, wal.KEY_NUMPAD_HOME):
                self.painter.controller.key_home()
                return
            if key_code in (wal.KEY_END, wal.KEY_NUMPAD_END):
                self.painter.controller.key_end()
                return
            if key_code == wal.KEY_BACK:
                self.painter.controller.key_backspace()
                return
            if key_code in (wal.KEY_RETURN, wal.KEY_NUMPAD_ENTER):
                self.painter.controller.insert_text('\n')
                return
            if key_code in (wal.KEY_DELETE, wal.KEY_NUMPAD_DELETE):
                self.painter.controller.key_del()
                return
        elif modifiers == wal.ACCEL_CTRL:
            if key_code in (wal.KEY_HOME, wal.KEY_NUMPAD_HOME):
                self.painter.controller.key_ctrl_home()
                return
            if key_code in (wal.KEY_END, wal.KEY_NUMPAD_END):
                self.painter.controller.key_ctrl_end()
                return
        elif modifiers == wal.ACCEL_CTRL | wal.ACCEL_SHIFT:
            if key_code in (wal.KEY_HOME, wal.KEY_NUMPAD_HOME):
                self.painter.controller.key_ctrl_home(True)
                return
            if key_code in (wal.KEY_END, wal.KEY_NUMPAD_END):
                self.painter.controller.key_ctrl_end(True)
                return
        elif modifiers == wal.ACCEL_SHIFT:
            if key_code in (wal.KEY_LEFT, wal.KEY_NUMPAD_LEFT):
                self.painter.controller.key_left(True)
                return
            if key_code in (wal.KEY_RIGHT, wal.KEY_NUMPAD_RIGHT):
                self.painter.controller.key_right(True)
                return
            if key_code in (wal.KEY_HOME, wal.KEY_NUMPAD_HOME):
                self.painter.controller.key_home(True)
                return
            if key_code in (wal.KEY_END, wal.KEY_NUMPAD_END):
                self.painter.controller.key_end(True)
                return
            if key_code in (wal.KEY_UP, wal.KEY_NUMPAD_UP):
                self.painter.controller.key_up(True)
                return
            if key_code in (wal.KEY_DOWN, wal.KEY_NUMPAD_DOWN):
                self.painter.controller.key_down(True)
                return

        return True

    def on_char(self, modifiers, unichar):
        if modifiers not in (wal.ACCEL_CTRL, wal.ACCEL_CTRL | wal.ACCEL_SHIFT):
            if self.painter.mode == modes.TEXT_EDIT_MODE:
                self.painter.controller.insert_text(unichar)
                return
            elif self.painter.mode == modes.TEXT_EDITOR_MODE:
                char = int(unichar)
                if char in modes.ET_MODES:
                    self.painter.controller.set_mode(char)
                    return
        return True
