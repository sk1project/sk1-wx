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

from sk1 import _
from sk1.resources import icons

from generic import PrefPanel


class CanvasPrefs(PrefPanel):
    pid = 'Canvas'
    name = _('Canvas')
    title = _('Canvas marker preferences')
    icon_id = icons.PD_PREFS_PALETTE

    def __init__(self, app, dlg, *_args):
        PrefPanel.__init__(self, app, dlg)

    def build(self):
        self.built = True
