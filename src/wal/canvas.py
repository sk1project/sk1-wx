# -*- coding: utf-8 -*-
#
#  Copyright (C) 2018 by Igor E. Novikov
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

from basic import SizedPanel, SensitiveCanvas


class RulerCanvas(SizedPanel, SensitiveCanvas):

    def __init__(self, parent, size=20, check_move=False):
        SizedPanel.__init__(self, parent)
        SensitiveCanvas.__init__(self, check_move=check_move)
        self.fix_size(size)
        self.set_double_buffered()

    def fix_size(self, size=0):
        self.remove_all()
        size = size if size > 0 else 20
        self.add((size, size))
        self.parent.layout()
