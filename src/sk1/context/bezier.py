# -*- coding: utf-8 -*-
#
#  Copyright (C) 2015 by Ihor E. Novikov
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

from sk1.resources import pdids
from .base import ActionCtxPlugin

BEZIER_ACTIONS = [
    pdids.ID_BEZIER_SEL_ALL_NODES, pdids.ID_BEZIER_REVERSE_ALL_PATHS, None,
    pdids.ID_BEZIER_SEL_SUBPATH_NODES, pdids.ID_BEZIER_DEL_SUBPATH,
    pdids.ID_BEZIER_REVERSE_SUBPATH, pdids.ID_BEZIER_EXTRACT_SUBPATH, None,
    pdids.ID_BEZIER_ADD_NODE, pdids.ID_BEZIER_DELETE_NODE, None,
    pdids.ID_BEZIER_ADD_SEG, pdids.ID_BEZIER_DELETE_SEG,
    pdids.ID_BEZIER_JOIN_NODE, pdids.ID_BEZIER_SPLIT_NODE, None,
    pdids.ID_BEZIER_SEG_TO_LINE, pdids.ID_BEZIER_SEG_TO_CURVE, None,
    pdids.ID_BEZIER_NODE_CUSP, pdids.ID_BEZIER_NODE_SMOOTH,
    pdids.ID_BEZIER_NODE_SYMMETRICAL, ]


class BezierPlugin(ActionCtxPlugin):
    name = 'BezierPlugin'
    ids = BEZIER_ACTIONS
