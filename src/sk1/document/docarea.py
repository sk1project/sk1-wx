# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013-2018 by Igor E. Novikov
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


from sk1.document.ruler import Ruler, RulerCorner
from sk1.document.canvas import AppCanvas


class DocArea(object):
    doc_tab = None

    def __init__(self, presenter):
        self.presenter = presenter
        self.corner = RulerCorner(presenter)
        self.hruler = Ruler(presenter, vertical=False)
        self.vruler = Ruler(presenter)
        self.canvas = AppCanvas(presenter)

    def destroy(self):
        objs = [self.hruler, self.vruler, self.corner, self.canvas]
        for obj in objs:
            obj.destroy()

        items = self.__dict__.keys()
        for item in items:
            self.__dict__[item] = None
