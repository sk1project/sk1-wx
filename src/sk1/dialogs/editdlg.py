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


class EditDialog(wal.OkCancelDialog):
    presenter = None
    entry = None

    def __init__(self, parent, title, text, width):
        self.text = text
        self.width = width
        wal.OkCancelDialog.__init__(self, parent, title, style=wal.VERTICAL)

    def build(self):
        self.entry = wal.Entry(self, self.text, width=self.width)
        self.pack(self.entry, padding_all=10, fill=True)

    def get_result(self):
        txt = self.entry.get_value()
        return txt if txt else self.text


def edit_dlg(parent, dlg_name, text, width=25):
    dlg = EditDialog(parent, dlg_name, text, width)
    return dlg.show()


class MultilineEditDialog(wal.OkCancelDialog):
    presenter = None
    entry = None

    def __init__(self, parent, title, text):
        self.text = text
        wal.OkCancelDialog.__init__(self, parent, title, (400, 250),
                                    style=wal.VERTICAL, resizable=True)

    def build(self):
        self.entry = wal.Entry(self, self.text, multiline=True)
        self.pack(self.entry, padding_all=5, fill=True, expand=True)

    def get_result(self):
        txt = self.entry.get_value()
        return txt if txt else self.text


def multiline_edit_dlg(parent, dlg_name, text):
    dlg = MultilineEditDialog(parent, dlg_name, text)
    return dlg.show()
