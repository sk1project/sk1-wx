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
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import wal
from sk1 import modes
from sk1.resources import pdids
from sk1.pwidgets import ContextMenu

UNDO = [wal.ID_UNDO, wal.ID_REDO]
EDIT = [None, wal.ID_CUT, wal.ID_COPY, wal.ID_PASTE,
        wal.ID_DELETE, pdids.ID_DUPLICATE, None, wal.ID_SELECTALL]
STYLE = [None, pdids.FILL_MODE, pdids.STROKE_MODE, pdids.COPY_FILL,
         pdids.COPY_STROKE]
DEFAULT = [None, wal.ID_PROPERTIES]
COMBINE = [None, pdids.ID_COMBINE, pdids.ID_BREAK_APART, ]
TO_CURVES = [None, pdids.ID_TO_CURVES]
GROUP = [None, pdids.ID_GROUP, pdids.ID_UNGROUP, pdids.ID_UNGROUPALL, ]
BEZIER_EDIT = [None, wal.ID_SELECTALL, pdids.ID_DESELECT, pdids.ID_INV_SELECT,
               None, pdids.ID_BEZIER_ADD_NODE, pdids.ID_BEZIER_DELETE_NODE,
               None, pdids.ID_BEZIER_ADD_SEG, pdids.ID_BEZIER_DELETE_SEG,
               pdids.ID_BEZIER_JOIN_NODE, pdids.ID_BEZIER_SPLIT_NODE,
               None, pdids.ID_BEZIER_SEG_TO_LINE, pdids.ID_BEZIER_SEG_TO_CURVE,
               None, pdids.ID_BEZIER_NODE_CUSP, pdids.ID_BEZIER_NODE_SMOOTH,
               pdids.ID_BEZIER_NODE_SYMMETRICAL]
TEXT = [None, pdids.ID_UPPER_TEXT, pdids.ID_LOWER_TEXT,
        pdids.ID_CAPITALIZE_TEXT]


class CanvasCtxMenu(ContextMenu):
    def __init__(self, app, parent):
        ContextMenu.__init__(self, app, parent, UNDO)

    def get_entries(self):
        if not self.insp.is_selection():
            if self.insp.is_mode(modes.BEZIER_EDITOR_MODE):
                return BEZIER_EDIT
            elif self.app.current_doc.canvas.mode == modes.TEXT_EDIT_MODE:
                return EDIT + TEXT + DEFAULT
        else:
            doc = self.app.current_doc
            sel = doc.selection.objs
            if len(sel) > 1:
                return EDIT + COMBINE + GROUP + STYLE + TO_CURVES
            elif self.insp.is_obj_rect(sel[0]):
                return EDIT + self.get_order_entries() + STYLE + TO_CURVES
            elif self.insp.is_obj_circle(sel[0]):
                return EDIT + self.get_order_entries() + STYLE + TO_CURVES
            elif self.insp.is_obj_polygon(sel[0]):
                return EDIT + self.get_order_entries() + STYLE + TO_CURVES
            elif self.insp.is_obj_curve(sel[0]):
                return EDIT + self.get_order_entries() + STYLE + COMBINE
            elif self.insp.can_be_ungrouped():
                return EDIT + self.get_order_entries() + STYLE + GROUP
            elif self.insp.is_obj_pixmap(sel[0]):
                return EDIT + self.get_order_entries()
            elif self.insp.is_obj_text(sel[0]):
                return EDIT + self.get_order_entries() + STYLE + TO_CURVES
        return EDIT + DEFAULT

    def get_order_entries(self):
        ret = []
        if self.insp.can_be_raised():
            ret += [pdids.ID_RAISE_TO_TOP, pdids.ID_RAISE]
        if self.insp.can_be_lower():
            ret += [pdids.ID_LOWER, pdids.ID_LOWER_TO_BOTTOM]
        if ret:
            ret = [None, ] + ret
        return ret
