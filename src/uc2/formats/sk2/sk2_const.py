# -*- coding: utf-8 -*-
#
#	Copyright (C) 2015 by Igor E. Novikov
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.

#PDXF file structure elements
DOC_MIME = 'application/vnd.sk1project.pdxf-graphics'

DOC_FONT_DIR = 'Fonts'
DOC_IMAGE_DIR = 'Images'
DOC_METAINF_DIR = 'META-INF'
DOC_PALETTE_DIR = 'Palettes'
DOC_PREVIEW_DIR = 'Previews'
DOC_PROFILE_DIR = 'Profiles'
DOC_THUMBNAIL_DIR = 'Thumbnails'

DOC_STRUCTURE = [
DOC_FONT_DIR,
DOC_IMAGE_DIR,
DOC_METAINF_DIR,
DOC_PALETTE_DIR,
DOC_PREVIEW_DIR,
DOC_PROFILE_DIR,
DOC_THUMBNAIL_DIR,
]

DOC_HEADER = '##sK1 2 0'

DOC_ORIGIN_CENTER = 0
DOC_ORIGIN_LL = 1
DOC_ORIGIN_LU = 2
ORIGINS = [DOC_ORIGIN_CENTER, DOC_ORIGIN_LL, DOC_ORIGIN_LU]

#Bezier curve constants
NORMAL_TRAFO = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
CORNERS = [0.0, 0.0, 0.0, 0.0]
EMPTY_STYLE = [[], [], [], []]

CURVE_CLOSED = 1
CURVE_OPENED = 0

NODE_CUSP = 0
NODE_SMOOTH = 1
NODE_SYMMETRICAL = 2

ARC_ARC = 0
ARC_CHORD = 1
ARC_PIE_SLICE = 2

CIRCLE_CTRL = 0.55
CIRCLE_CTRL_SHIFT = 0.45

TEXTBLOCK_WIDTH = -1


STUB_RECT = [0.0, 0.0, 1.0, 1.0]
STUB_PATHS = [[[0.0, 0.0], [[10.0, 10.0], ], CURVE_OPENED], ]
STUB_CIRCLE = [[[1.0, 0.5], [
			[[1.0, 0.775], [0.775, 1.0], [0.5, 1.0], NODE_SYMMETRICAL],
			[[0.225, 1.0], [0.0, 0.775], [0.0, 0.5], NODE_SYMMETRICAL],
			[[0.0, 0.225], [0.225, 0.0], [0.5, 0.0], NODE_SYMMETRICAL],
			[[0.775, 0.0], [1.0, 0.225], [1.0, 0.5], NODE_SYMMETRICAL],
			], CURVE_CLOSED]]

#Fill and stroke constants

FILL_EVENODD = 1
FILL_NONZERO = 0

FILL_SOLID = 0
FILL_GRADIENT = 1
FILL_TILED = 2

STROKE_MIDDLE = 0
STROKE_OTSIDE = 1
STROKE_INSIDE = 2

JOIN_MITER = 0
JOIN_ROUND = 1
JOIN_BEVEL = 2


CAP_BUTT = 1
CAP_ROUND = 2
CAP_SQUARE = 3
