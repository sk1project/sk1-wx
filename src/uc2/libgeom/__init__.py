# -*- coding: utf-8 -*-
#
#  Copyright (C) 2015 by Igor E. Novikov
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

from bbox import *
from bezier_ops import *
from contour import stroke_to_curve
from cwrap import *
from flattering import get_flattened_paths, flat_paths, flat_path
from objs import *
from points import *
from shaping import intersect_paths, fuse_paths, trim_paths, excluse_paths
from text_on_path import set_text_on_path
from trafo import *

"""
Package provides basic routines for Bezier curves.

BBOX DEFINITION:
[x0,y0,x1,y1]

RECTANGLE DEFINITION
[x,y,w,h]

PATHS DEFINITION:
[path0, path1, ...]

PATH DEFINITION:
[start_point, points, end_marker]
start_pont - [x,y]
end_marker - is closed CURVE_CLOSED = 1, if not CURVE_OPENED = 0

POINTS DEFINITION:
[point0, point1,...]
line point - [x,y]
curve point - [[x1,y1],[x2,y2],[x3,y3], marker]
marker - NODE_CUSP = 0; NODE_SMOOTH = 1; NODE_SYMMETRICAL = 2 
"""
