# -*- coding: utf-8 -*-
#
#  Copyright (C) 2015-2021 by Ihor E. Novikov
#  Copyright (C) 2020 by Michael Schorcht
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
    (wal.KEY_U, wal.ACCEL_SHIFT | wal.ACCEL_CTRL): pdids.ID_UNGROUPALL,
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
            return self.painter.controller.escape_pressed()

        if self.painter.mode == modes.TEXT_EDIT_MODE:
            return self.text_edit_mode(key_code, modifiers)

        if self.painter.mode == modes.BEZIER_EDITOR_MODE:
            return self.bezier_editor_mode(key_code, modifiers)

        if (key_code, modifiers) in MAPPING:
            return self.actions[MAPPING[(key_code, modifiers)]]()

        if key_code == wal.KEY_SPACE and not modifiers:
            if self.painter.mode == modes.SELECT_MODE:
                return self.painter.set_mode(modes.SHAPER_MODE)
            elif self.painter.mode in modes.EDIT_MODES:
                return self.painter.set_mode(modes.SELECT_MODE)

        if key_code == wal.KEY_F2 and not modifiers:
            return self.painter.set_mode(modes.ZOOM_MODE)

        return True

    def bezier_editor_mode(self, key_code, modifiers):

        if not modifiers:
            if key_code in (wal.KEY_UP, wal.KEY_NUMPAD_UP):
                return self.painter.controller.move_selected_points_by_kbd(0.0, 1.0)
            if key_code in (wal.KEY_RIGHT, wal.KEY_NUMPAD_RIGHT):
                return self.painter.controller.move_selected_points_by_kbd(1.0, 0.0)
            if key_code in (wal.KEY_DOWN, wal.KEY_NUMPAD_DOWN):
                return self.painter.controller.move_selected_points_by_kbd(0.0, -1.0)
            if key_code in (wal.KEY_LEFT, wal.KEY_NUMPAD_LEFT):
                return self.painter.controller.move_selected_points_by_kbd(-1.0, 0.0)

            if key_code in (wal.KEY_ADD, wal.KEY_NUMPAD_ADD) or key_code == ord('='):
                return self.painter.controller.insert_new_node_by_kbd()
            if key_code in (ord('-'), wal.KEY_SUBTRACT, wal.KEY_NUMPAD_SUBTRACT):
                return self.painter.controller.delete_selected_nodes()
            if key_code == wal.KEY_TAB:
                return self.painter.controller.change_selection_by_kbd()

        if key_code == wal.KEY_TAB and modifiers == wal.ACCEL_CTRL:
            return self.painter.controller.change_selection_by_kbd(back=True)

        if key_code in (wal.KEY_UP, wal.KEY_NUMPAD_UP) and modifiers == wal.ACCEL_SHIFT:
            return self.painter.controller.change_path_by_kbd()

        if key_code in (wal.KEY_DOWN, wal.KEY_NUMPAD_DOWN) and modifiers == wal.ACCEL_SHIFT:
            return self.painter.controller.change_path_by_kbd(back=True)

        if key_code in (wal.KEY_RIGHT, wal.KEY_NUMPAD_RIGHT) and modifiers == wal.ACCEL_SHIFT:
            return self.painter.controller.add_selected_by_kbd()

        if key_code in (wal.KEY_LEFT, wal.KEY_NUMPAD_LEFT) and modifiers == wal.ACCEL_SHIFT:
            return self.painter.controller.add_selected_by_kbd(back=True)

        return True

    def text_edit_mode(self, key_code, modifiers):

        if key_code == wal.KEY_NUMPAD_DECIMAL and modifiers == wal.ACCEL_SHIFT:
            return self.actions[wal.ID_CUT]()

        if key_code == wal.KEY_NUMPAD0 and modifiers == wal.ACCEL_SHIFT:
            return self.actions[wal.ID_PASTE]()

        if not modifiers:
            if key_code in (wal.KEY_UP, wal.KEY_NUMPAD_UP):
                return self.painter.controller.key_up()
            if key_code in (wal.KEY_DOWN, wal.KEY_NUMPAD_DOWN):
                return self.painter.controller.key_down()
            if key_code in (wal.KEY_LEFT, wal.KEY_NUMPAD_LEFT):
                return self.painter.controller.key_left()
            if key_code in (wal.KEY_RIGHT, wal.KEY_NUMPAD_RIGHT):
                return self.painter.controller.key_right()
            if key_code in (wal.KEY_HOME, wal.KEY_NUMPAD_HOME):
                return self.painter.controller.key_home()
            if key_code in (wal.KEY_END, wal.KEY_NUMPAD_END):
                return self.painter.controller.key_end()
            if key_code == wal.KEY_BACK:
                return self.painter.controller.key_backspace()
            if key_code in (wal.KEY_RETURN, wal.KEY_NUMPAD_ENTER):
                return self.painter.controller.insert_text('\n')
            if key_code in (wal.KEY_DELETE, wal.KEY_NUMPAD_DELETE):
                return self.painter.controller.key_del()
        elif modifiers == wal.ACCEL_CTRL:
            if key_code in (wal.KEY_HOME, wal.KEY_NUMPAD_HOME):
                return self.painter.controller.key_ctrl_home()
            if key_code in (wal.KEY_END, wal.KEY_NUMPAD_END):
                return self.painter.controller.key_ctrl_end()
        elif modifiers == wal.ACCEL_CTRL | wal.ACCEL_SHIFT:
            if key_code in (wal.KEY_HOME, wal.KEY_NUMPAD_HOME):
                return self.painter.controller.key_ctrl_home(True)
            if key_code in (wal.KEY_END, wal.KEY_NUMPAD_END):
                return self.painter.controller.key_ctrl_end(True)
        elif modifiers == wal.ACCEL_SHIFT:
            if key_code in (wal.KEY_LEFT, wal.KEY_NUMPAD_LEFT):
                return self.painter.controller.key_left(True)
            if key_code in (wal.KEY_RIGHT, wal.KEY_NUMPAD_RIGHT):
                return self.painter.controller.key_right(True)
            if key_code in (wal.KEY_HOME, wal.KEY_NUMPAD_HOME):
                return self.painter.controller.key_home(True)
            if key_code in (wal.KEY_END, wal.KEY_NUMPAD_END):
                return self.painter.controller.key_end(True)
            if key_code in (wal.KEY_UP, wal.KEY_NUMPAD_UP):
                return self.painter.controller.key_up(True)
            if key_code in (wal.KEY_DOWN, wal.KEY_NUMPAD_DOWN):
                return self.painter.controller.key_down(True)

        return True

    def on_char(self, modifiers, unichar):
        if modifiers not in (wal.ACCEL_CTRL, wal.ACCEL_CTRL | wal.ACCEL_SHIFT):
            if self.painter.mode == modes.TEXT_EDIT_MODE:
                return self.painter.controller.insert_text(unichar)
            elif self.painter.mode == modes.TEXT_EDITOR_MODE:
                char = int(unichar)
                if char in modes.ET_MODES:
                    return self.painter.controller.set_mode(char)
        return True
