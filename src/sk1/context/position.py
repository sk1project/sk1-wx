# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013-2021 by Igor E. Novikov
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

from sk1 import events
from sk1.pwidgets import UnitSpin
from uc2 import sk2const
from .base import CtxPlugin


class PositionPlugin(CtxPlugin):
    name = 'PositionPlugin'
    update_flag = False
    x_spin = None
    y_spin = None

    def __init__(self, app, parent):
        CtxPlugin.__init__(self, app, parent)
        events.connect(events.DOC_CHANGED, self.update)
        events.connect(events.SELECTION_CHANGED, self.update)
        events.connect(events.DOC_MODIFIED, self.update)

    def build(self):
        self.pack(wal.Label(self, 'x:'), padding=2)
        self.x_spin = UnitSpin(self.app, self, can_be_negative=True,
                               onchange=self.user_changes)
        self.pack(self.x_spin, padding=2)

        self.pack(wal.Label(self, 'y:'), padding=2)
        self.y_spin = UnitSpin(self.app, self, can_be_negative=True,
                               onchange=self.user_changes)
        self.pack(self.y_spin, padding=2)

    def get_coords(self):
        pw, ph = self.app.current_doc.get_page_size()
        bbox = self.app.current_doc.selection.bbox
        doc_origin = self.app.current_doc.methods.get_doc_origin()
        page_factor = 0.0 if doc_origin == sk2const.DOC_ORIGIN_CENTER else 1.0
        y_factor = -1.0 if doc_origin == sk2const.DOC_ORIGIN_LU else 1.0
        return (page_factor * pw + bbox[2] + bbox[0]) / 2.0, \
               (page_factor * ph + y_factor * (bbox[3] + bbox[1])) / 2.0

    def update(self, *_args):
        if self.insp.is_selection():
            x, y = self.get_coords()
            self.update_flag = True
            self.x_spin.set_point_value(x)
            self.y_spin.set_point_value(y)
            self.update_flag = False

    def user_changes(self, *_args):
        if not self.update_flag and self.insp.is_selection():
            x, y = self.get_coords()
            dx = self.x_spin.get_point_value() - x
            dy = self.y_spin.get_point_value() - y
            if any([dx, dy]):
                doc_origin = self.app.current_doc.methods.get_doc_origin()
                dy *= -1.0 if doc_origin == sk2const.DOC_ORIGIN_LU else 1.0
                trafo = [1.0, 0.0, 0.0, 1.0, dx, dy]
                self.app.current_doc.api.transform_selected(trafo)
