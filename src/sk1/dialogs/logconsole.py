# -*- coding: utf-8 -*-
#
#  Copyright (C) 2017 by Igor E. Novikov
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

import os
import wal

from uc2.utils.fsutils import get_fileptr

FUCSIA = (144, 84, 141)
YELLOW = (217, 175, 106)
BLUE = (81, 124, 194)
DARK = (122, 122, 122)
LIGHT = (170, 181, 189)

COLOR_MAP = {
    ' ERROR   ': FUCSIA,
    ' WARNING ': YELLOW,
    ' DEBUG   ': DARK,
}

FG_COLOR = LIGHT
BG_COLOR = (43, 43, 43)


class ConsoleDialog(wal.SimpleDialog):
    presenter = None
    entry = None
    lpanel = None

    def __init__(self, parent, title, log_path):
        self.app = parent.app
        self.log_path = log_path
        wal.SimpleDialog.__init__(self, parent, title, (800, 500),
                                  style=wal.HORIZONTAL, resizable=True,
                                  add_line=False, margin=0)

    def build(self):
        self.lpanel = wal.VPanel(self)
        self.lpanel.set_bg((49, 51, 53))
        self.lpanel.pack((26, 26))
        self.pack(self.lpanel, fill=True)
        self.pack(wal.PLine(self, (85, 85, 85)), fill=True)
        self.entry = wal.Entry(self, '', multiline=True, editable=True,
                               richtext=True, no_border=True)
        self.entry.set_monospace()
        self.entry.set_bg(BG_COLOR)
        self.pack(self.entry, fill=True, expand=True)
        self.load_logs()

    def load_logs(self):
        filepath = os.path.join(self.app.appdata.app_config_dir, 'sk1.log')
        if not os.path.lexists(filepath):
            return
        fileptr = get_fileptr(filepath)
        while True:
            line = fileptr.readline()
            if not line:
                break
            color = COLOR_MAP.get(line[:9], FG_COLOR)
            self.entry.set_text_colors(color)
            self.entry.append(line)


def logconsole_dlg(parent, dlg_name='Logs', log_path=''):
    dlg = ConsoleDialog(parent, dlg_name, log_path)
    return dlg.show()
