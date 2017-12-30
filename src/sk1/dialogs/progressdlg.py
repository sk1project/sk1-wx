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
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.


import wal
from uc2 import events


class ProgressDialog:
    title = ''
    dlg = None

    def __init__(self, title, parent):
        self.title = title
        self.parent = parent

    def run(self, callback, args):
        events.connect(events.FILTER_INFO, self.listener)
        self.dlg = wal.ProgressDialog(self.parent, self.title)
        return callback(*args)

    def listener(self, *args):
        self.dlg.update(int(round(args[1] * 100.0)), args[0])

    def destroy(self):
        events.disconnect(events.FILTER_INFO, self.listener)
        self.dlg.destroy()
