# -*- coding: utf-8 -*-
#
#  Copyright (C) 2018 by Maxim S. Barabash
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

BLACK_COLOR = 0
WHITE_COLOR = 7
DEFAULT_COLOR = -1

NO_FILL = -1
WHITE_FILL = 0
BLACK_FILL = 20

DEFAULT_RESOLUTION = 1200


T_ELLIPSE_BY_RAD = 1
T_ELLIPSE_BY_DIA = 2
T_CIRCLE_BY_RAD = 3
T_CIRCLE_BY_DIA = 4

T_OPEN_ARC = 1
T_PIE_WEDGE_ARC = 2

T_POLYLINE = 1
T_BOX = 2
T_POLYGON = 3
T_ARC_BOX = 4
T_PIC_BOX = 5

T_LEFT_JUSTIFIED = 0
T_CENTER_JUSTIFIED = 1
T_RIGHT_JUSTIFIED = 2

DEFAULT_FONT = 0
ROMAN_FONT = 1
BOLD_FONT = 2
ITALIC_FONT = 3
MODERN_FONT = 4
TYPEWRITER_FONT = 5
MAX_FONT = 5

RIGID_TEXT = 1
SPECIAL_TEXT = 2
PSFONT_TEXT = 4
HIDDEN_TEXT = 8

T_OPEN_APPROX = 0
T_CLOSED_APPROX = 1
T_OPEN_INTERPOLATED = 2
T_CLOSED_INTERPOLATED = 3
T_OPEN_XSPLINE = 4
T_CLOSED_XSPLINE = 5

S_SPLINE_ANGULAR = 0.0
S_SPLINE_APPROX = 1.0
S_SPLINE_INTERP = -1.0

SOLID_LINE = 0
DASH_LINE = 1
DOTTED_LINE = 2
DASH_DOT_LINE = 3
DASH_2_DOTS_LINE = 4
DASH_3_DOTS_LINE = 5

CLOSED_PATH = 0
OPEN_PATH = 1

PORTRAIT = 0
LANDSCAPE = 1
ORIENTATION = ("Portrait", "Landscape")

CENTER_JUSTIFIED = 0
FLUSH_LEFT_JUSTIFIED = 1
JUSTIFICATION = ("Center", "Flush Left")

INCHES = 0
METRIC = 1
UNITS = ("Inches", "Metric")

SINGLE = 0
MULTIPLE = 1
MULTIPLE_PAGE = ("Single", "Multiple")
