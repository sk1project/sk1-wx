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
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import wal

from sk1 import modes
from sk1.resources import pdids


class KbdProcessor:
    canvas = None

    def __init__(self, canvas):
        self.canvas = canvas
        self.app = canvas.app
        self.actions = self.app.actions

    def on_key_down(self, event):
        key_code = event.GetKeyCode()
        raw_code = event.GetRawKeyCode()
        modifiers = event.GetModifiers()

        if key_code == wal.KEY_ESCAPE and not modifiers:
            self.canvas.controller.escape_pressed()
            return

        if key_code == wal.KEY_NUMPAD_DECIMAL and modifiers == wal.ACCEL_SHIFT:
            self.actions[wal.ID_CUT].do_call()
            return

        if key_code == wal.KEY_NUMPAD0 and modifiers == wal.ACCEL_SHIFT:
            self.actions[wal.ID_PASTE].do_call()
            return

        if self.canvas.mode == modes.TEXT_EDIT_MODE:
            self.text_edit_mode(event, key_code, raw_code, modifiers)
            return

        if key_code in (wal.KEY_UP, wal.KEY_NUMPAD_UP) and not modifiers:
            self.actions[pdids.MOVE_UP].do_call()
            return

        if key_code in (wal.KEY_DOWN, wal.KEY_NUMPAD_DOWN) and not modifiers:
            self.actions[pdids.MOVE_DOWN].do_call()
            return

        if key_code in (wal.KEY_LEFT, wal.KEY_NUMPAD_LEFT) and not modifiers:
            self.actions[pdids.MOVE_LEFT].do_call()
            return

        if key_code in (wal.KEY_RIGHT, wal.KEY_NUMPAD_RIGHT) and not modifiers:
            self.actions[pdids.MOVE_RIGHT].do_call()
            return

        if key_code == wal.KEY_F2 and not modifiers:
            self.canvas.set_mode(modes.ZOOM_MODE)
            return

        if key_code == wal.KEY_SPACE and not modifiers:
            if self.canvas.mode == modes.SELECT_MODE:
                self.canvas.set_mode(modes.SHAPER_MODE)
                return
            elif self.canvas.mode in modes.EDIT_MODES:
                self.canvas.set_mode(modes.SELECT_MODE)
                return

        event.Skip()

    def text_edit_mode(self, event, key_code, raw_code, modifiers):
        if not modifiers:
            if key_code in (wal.KEY_UP, wal.KEY_NUMPAD_UP):
                self.canvas.controller.key_up()
                return
            if key_code in (wal.KEY_DOWN, wal.KEY_NUMPAD_DOWN):
                self.canvas.controller.key_down()
                return
            if key_code in (wal.KEY_LEFT, wal.KEY_NUMPAD_LEFT):
                self.canvas.controller.key_left()
                return
            if key_code in (wal.KEY_RIGHT, wal.KEY_NUMPAD_RIGHT):
                self.canvas.controller.key_right()
                return
            if key_code in (wal.KEY_HOME, wal.KEY_NUMPAD_HOME):
                self.canvas.controller.key_home()
                return
            if key_code in (wal.KEY_END, wal.KEY_NUMPAD_END):
                self.canvas.controller.key_end()
                return
            if key_code == wal.KEY_BACK:
                self.canvas.controller.key_backspace()
                return
            if key_code in (wal.KEY_RETURN, wal.KEY_NUMPAD_ENTER):
                self.canvas.controller.insert_text('\n')
                return
            if key_code in (wal.KEY_DELETE, wal.KEY_NUMPAD_DELETE):
                self.canvas.controller.key_del()
                return
        elif modifiers == wal.ACCEL_CTRL:
            if key_code in (wal.KEY_HOME, wal.KEY_NUMPAD_HOME):
                self.canvas.controller.key_ctrl_home()
                return
            if key_code in (wal.KEY_END, wal.KEY_NUMPAD_END):
                self.canvas.controller.key_ctrl_end()
                return
        elif modifiers == wal.ACCEL_CTRL | wal.ACCEL_SHIFT:
            if key_code in (wal.KEY_HOME, wal.KEY_NUMPAD_HOME):
                self.canvas.controller.key_ctrl_home(True)
                return
            if key_code in (wal.KEY_END, wal.KEY_NUMPAD_END):
                self.canvas.controller.key_ctrl_end(True)
                return
        elif modifiers == wal.ACCEL_SHIFT:
            if key_code in (wal.KEY_LEFT, wal.KEY_NUMPAD_LEFT):
                self.canvas.controller.key_left(True)
                return
            if key_code in (wal.KEY_RIGHT, wal.KEY_NUMPAD_RIGHT):
                self.canvas.controller.key_right(True)
                return
            if key_code in (wal.KEY_HOME, wal.KEY_NUMPAD_HOME):
                self.canvas.controller.key_home(True)
                return
            if key_code in (wal.KEY_END, wal.KEY_NUMPAD_END):
                self.canvas.controller.key_end(True)
                return
            if key_code in (wal.KEY_UP, wal.KEY_NUMPAD_UP):
                self.canvas.controller.key_up(True)
                return
            if key_code in (wal.KEY_DOWN, wal.KEY_NUMPAD_DOWN):
                self.canvas.controller.key_down(True)
                return

        event.Skip()

    def on_char(self, event):
        modifiers = event.GetModifiers()
        if modifiers not in (wal.ACCEL_CTRL, wal.ACCEL_CTRL | wal.ACCEL_SHIFT):
            if self.canvas.mode == modes.TEXT_EDIT_MODE:
                self.canvas.controller.insert_text(unichr(event.GetUniChar()))
                return
            elif self.canvas.mode == modes.TEXT_EDITOR_MODE:
                char = int(unichr(event.GetUniChar()))
                if char in modes.ET_MODES:
                    self.canvas.controller.set_mode(char)
                    return
        event.Skip()
