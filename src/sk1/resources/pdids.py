# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2013 by Igor E. Novikov
#
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
#
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
#
# 	You should have received a copy of the GNU General Public License
# 	along with this program.  If not, see <http://www.gnu.org/licenses/>.

from wal import new_id

#----- Canvas modes
SELECT_MODE = new_id()
SHAPER_MODE = new_id()
ZOOM_MODE = new_id()
FLEUR_MODE = new_id()
LINE_MODE = new_id()
CURVE_MODE = new_id()
RECT_MODE = new_id()
ELLIPSE_MODE = new_id()
POLYGON_MODE = new_id()
TEXT_MODE = new_id()
GRADIENT_MODE = new_id()

FILL_MODE = new_id()
STROKE_MODE = new_id()

ZOOM_OUT_MODE = new_id()
MOVE_MODE = new_id()
COPY_MODE = new_id()

COPY_FILL = new_id()
COPY_STROKE = new_id()

MOVE_UP = new_id()
MOVE_DOWN = new_id()
MOVE_LEFT = new_id()
MOVE_RIGHT = new_id()

#----- File menu
ID_NEW_FROM_TEMPLATE = new_id()
ID_SAVE_SEL = new_id()
ID_SAVEALL = new_id()
ID_IMPORT = new_id()
ID_EXPORT = new_id()
ID_CLEAR_LOG = new_id()
ID_VIEW_LOG = new_id()
#----- Edit menu
ID_CLEAR_UNDO = new_id()
ID_DESELECT = new_id()
ID_INV_SELECT = new_id()
ID_DUPLICATE = new_id()
#----- View menu
ID_STROKE_VIEW = new_id()
ID_DRAFT_VIEW = new_id()
ID_PREV_ZOOM = new_id()
ID_ZOOM_PAGE = new_id()
ID_SHOW_GRID = new_id()
ID_SHOW_GUIDES = new_id()
ID_SHOW_SNAP = new_id()
ID_SHOW_PAGE_BORDER = new_id()
ID_SNAP_TO_GRID = new_id()
ID_SNAP_TO_GUIDE = new_id()
ID_SNAP_TO_OBJ = new_id()
ID_SNAP_TO_PAGE = new_id()
ID_ICONIZER = new_id()
#----- Layout menu
ID_INSERT_PAGE = new_id()
ID_DELETE_PAGE = new_id()
ID_GOTO_PAGE = new_id()
ID_NEXT_PAGE = new_id()
ID_PREV_PAGE = new_id()
ID_GUIDES_AT_CENTER = new_id()
ID_PAGE_FRAME = new_id()
ID_PAGE_GUIDE_FRAME = new_id()
ID_REMOVE_ALL_GUIDES = new_id()
#----- Arrange menu
ID_CLEAR_TRANSFORM = new_id()
ID_POSITION_PLGN = new_id()
ID_RESIZE_PLGN = new_id()
ID_SCALE_PLGN = new_id()
ID_ROTATE_PLGN = new_id()
ID_SHEAR_PLGN = new_id()
ID_ROTATE_LEFT = new_id()
ID_ROTATE_RIGHT = new_id()
ID_MIRROR_H = new_id()
ID_MIRROR_V = new_id()
ID_ALIGN_PLGN = new_id()
ID_COMBINE = new_id()
ID_BREAK_APART = new_id()
ID_RAISE_TO_TOP = new_id()
ID_RAISE = new_id()
ID_LOWER = new_id()
ID_LOWER_TO_BOTTOM = new_id()
ID_GROUP = new_id()
ID_UNGROUP = new_id()
ID_UNGROUPALL = new_id()
ID_PATHS_EXCLUSION = new_id()
ID_PATHS_FUSION = new_id()
ID_PATHS_INTERSECTION = new_id()
ID_PATHS_TRIM = new_id()
ID_TO_CONTAINER = new_id()
ID_FROM_CONTAINER = new_id()
ID_TO_CURVES = new_id()
ID_STROKE_TO_CURVES = new_id()

#----- Paths menu
ID_BEZIER_SEL_ALL_NODES = new_id()
ID_BEZIER_REVERSE_ALL_PATHS = new_id()
ID_BEZIER_SEL_SUBPATH_NODES = new_id()
ID_BEZIER_DEL_SUBPATH = new_id()
ID_BEZIER_REVERSE_SUBPATH = new_id()
ID_BEZIER_EXTRACT_SUBPATH = new_id()
ID_BEZIER_ADD_NODE = new_id()
ID_BEZIER_DELETE_NODE = new_id()
ID_BEZIER_ADD_SEG = new_id()
ID_BEZIER_DELETE_SEG = new_id()
ID_BEZIER_JOIN_NODE = new_id()
ID_BEZIER_SPLIT_NODE = new_id()
ID_BEZIER_SEG_TO_LINE = new_id()
ID_BEZIER_SEG_TO_CURVE = new_id()
ID_BEZIER_NODE_CUSP = new_id()
ID_BEZIER_NODE_SMOOTH = new_id()
ID_BEZIER_NODE_SYMMETRICAL = new_id()

#----- Bitmaps menu
ID_CONV_TO_CMYK = new_id()
ID_CONV_TO_RGB = new_id()
ID_CONV_TO_LAB = new_id()
ID_CONV_TO_GRAY = new_id()
ID_CONV_TO_BW = new_id()
ID_INVERT_BITMAP = new_id()
ID_REMOVE_ALPHA = new_id()
ID_INVERT_ALPHA = new_id()
ID_EXTRACT_BITMAP = new_id()
#----- Text menu
ID_EDIT_TEXT = new_id()
ID_TEXT_ON_PATH = new_id()
ID_TEXT_ON_CIRCLE = new_id()
ID_STRAIGHTEN_TEXT = new_id()
ID_CLEAR_MARKUP = new_id()
ID_UPPER_TEXT = new_id()
ID_LOWER_TEXT = new_id()
ID_CAPITALIZE_TEXT = new_id()
#----- Tools menu
ID_TOOL_PAGES = new_id()
ID_TOOL_LAYERS = new_id()
ID_TOOL_OBJBROWSER = new_id()
#----- Help menu
ID_REPORT_BUG = new_id()
ID_APP_WEBSITE = new_id()
ID_APP_FORUM = new_id()
ID_APP_FBPAGE = new_id()

