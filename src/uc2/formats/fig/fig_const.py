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
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

DEFAULT_COORD_SYSTEM = 2
DEFAULT_DEPTH = 50

BLACK_COLOR = 0
WHITE_COLOR = 7
DEFAULT_COLOR = -1

NO_FILL = -1
WHITE_FILL = 0.0
BLACK_FILL = 20.0

DEFAULT_RESOLUTION = 1200.0
PIX_PER_INCH = 1200.0
PIX_PER_CM = 450.0

"""Line thicknesses are given in 1/80 inch (0.3175mm)"""
LINE_RESOLUTION = 80.0

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
T_APPROX = (T_OPEN_APPROX, T_CLOSED_APPROX)
T_INTERPOLATED = (T_OPEN_INTERPOLATED, T_CLOSED_INTERPOLATED)
T_XSPLINE = (T_OPEN_XSPLINE, T_CLOSED_XSPLINE)

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


"""
 0 = Miter (the default in xfig 2.1 and earlier)
 1 = Round
 2 = Bevel
"""
JOIN_MITER = 0
JOIN_ROUND = 1
JOIN_BEVEL = 2

"""
 0 = Butt (the default in xfig 2.1 and earlier)
 1 = Round
 2 = Projecting/square
"""
CAP_BUTT = 0
CAP_ROUND = 1
CAP_SQUARE = 2

DEF_FONTSIZE = 12
DEF_PS_FONT = 0
DEF_LATEX_FONT = 0

PS_FONT = {
    -1: 'Default',
    0: 'Times-Roman',
    1: 'Times-Italic',
    2: 'Times-Bold',
    3: 'Times-BoldItalic',
    4: 'AvantGarde-Book',
    5: 'AvantGarde-BookOblique',
    6: 'AvantGarde-Demi',
    7: 'AvantGarde-DemiOblique',
    8: 'Bookman-Light',
    9: 'Bookman-LightItalic',
    10: 'Bookman-Demi',
    11: 'Bookman-DemiItalic',
    12: 'Courier',
    13: 'Courier-Oblique',
    14: 'Courier-Bold',
    15: 'Courier-BoldOblique',
    16: 'Helvetica',
    17: 'Helvetica-Oblique',
    18: 'Helvetica-Bold',
    19: 'Helvetica-BoldOblique',
    20: 'Helvetica-Narrow',
    21: 'Helvetica-Narrow-Oblique',
    22: 'Helvetica-Narrow-Bold',
    23: 'Helvetica-Narrow-BoldOblique',
    24: 'NewCenturySchlbk-Roman',
    25: 'NewCenturySchlbk-Italic',
    26: 'NewCenturySchlbk-Bold',
    27: 'NewCenturySchlbk-BoldItalic',
    28: 'Palatino-Roman',
    29: 'Palatino-Italic',
    30: 'Palatino-Bold',
    31: 'Palatino-BoldItalic',
    32: 'Symbol',
    33: 'ZapfChancery-MediumItalic',
    34: 'ZapfDingbats',
}

LATEX_FONT = {
    DEFAULT_FONT: 'Roman',
    ROMAN_FONT: 'Roman',
    BOLD_FONT: 'Bold',
    ITALIC_FONT: 'Italic',
    MODERN_FONT: 'Sans Serif',
    MAX_FONT: 'Typewriter'
}

LATEX_FONT_MAP = {
    DEFAULT_FONT: 'Times-Roman',
    ROMAN_FONT: 'Times-Roman',
    BOLD_FONT: 'Times-Bold',
    ITALIC_FONT: 'Times-Italic',
    MODERN_FONT: 'Helvetica',
    MAX_FONT: 'Courier'
}