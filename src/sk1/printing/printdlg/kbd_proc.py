# -*- coding: utf-8 -*-
#
#  Copyright (C) 2016 by Ihor E. Novikov
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


class Kbd_Processor:
    canvas = None

    def __init__(self, canvas):
        self.canvas = canvas

    def on_key_down(self, key_code, raw_code, modifiers):

        if key_code == wal.KEY_ESCAPE:
            self.canvas.dlg.on_close()
            return

        if key_code in (wal.KEY_PAGEDOWN, wal.KEY_NUMPAD_PAGEDOWN):
            self.canvas.next_page()
            return

        if key_code in (wal.KEY_PAGEUP, wal.KEY_NUMPAD_PAGEUP):
            self.canvas.previous_page()
            return

        return True
