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

import wx

import wal


class ConsoleDialog(wal.SimpleDialog):
    presenter = None
    entry = None

    def __init__(self, parent, title, log_path):
        self.log_path = log_path
        wal.SimpleDialog.__init__(self, parent, title, (800, 500),
                                  style=wal.VERTICAL, resizable=True,
                                  add_line=False, margin=0)

    def build(self):
        self.entry = wal.Entry(self, '', multiline=True, editable=False)
        self.entry.SetBackgroundColour((43,43,43))
        self.pack(self.entry, fill=True, expand=True)


def console_dlg(parent, dlg_name='Logs', log_path=''):
    dlg = ConsoleDialog(parent, dlg_name, log_path)
    return dlg.show()
