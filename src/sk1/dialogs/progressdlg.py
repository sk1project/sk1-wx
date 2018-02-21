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


class ProgressDialog(wal.CustomProgressDialog):
    def __init__(self, title, parent):
        wal.CustomProgressDialog.__init__(self, parent, title)

    def run(self, callback, args):
        events.connect(events.FILTER_INFO, self.listener)
        result = wal.CustomProgressDialog.run(self, callback, args)
        events.disconnect(events.FILTER_INFO, self.listener)
        return result

    def listener(self, *args):
        self.update_data(int(round(args[1] * 100.0)), args[0])
