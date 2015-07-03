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

import wx

ICON_SIZES = [16, 22, 24, 32, 48, 64, 128]

PD_NEW = 'gtk-new'
PD_OPEN = 'gtk-open'
PD_FILE_SAVE = 'gtk-save'
PD_FILE_SAVE_AS = 'gtk-save-as'
PD_CLOSE = 'gtk-close'
PD_PRINT_PREVIEW = 'gtk-print-preview'
PD_PRINT = 'gtk-print'
PD_QUIT = 'gtk-quit'
PD_UNDO = 'gtk-undo'
PD_REDO = 'gtk-redo'
PD_CUT = 'gtk-cut'
PD_COPY = 'gtk-copy'
PD_PASTE = 'gtk-paste'
PD_DELETE = 'gtk-delete'
PD_EDIT = 'gtk-edit'
PD_SELECTALL = 'gtk-select-all'
PD_PROPERTIES = 'gtk-properties'
PD_PREFERENCES = 'gtk-preferences'
PD_ZOOM_100 = 'gtk-zoom-100'
PD_ZOOM_IN = 'gtk-zoom-in'
PD_ZOOM_OUT = 'gtk-zoom-out'
PD_ZOOM_PAGE = 'gtk-zoom-page'
PD_ZOOM_FIT = 'gtk-zoom-fit'
PD_REFRESH = 'gtk-refresh'
PD_INSERT_PAGE = 'action-insert-page'
PD_DELETE_PAGE = 'action-delete-page'
PD_GOTO_PAGE = 'action-goto-page'
PD_NEXT_PAGE = 'action-next-page'
PD_PREV_PAGE = 'action-previous-page'
PD_GUIDES_AT_CENTER = 'action-guides-at-center'
PD_PAGE_FRAME = 'action-page-frame'
PD_PAGE_GUIDE_FRAME = 'action-page-guide-frame'
PD_REMOVE_ALL_GUIDES = 'action-remove-all-guides'
PD_TO_CURVES = 'action-to-curves'
PD_COMBINE = 'action-combine'
PD_BREAK = 'action-break'
PD_RAISE_TO_TOP = 'action-raise-to-top'
PD_RAISE = 'action-raise'
PD_LOWER = 'action-lower'
PD_LOWER_TO_BOTTOM = 'action-lower-to-bottom'
PD_GROUP = 'action-group'
PD_UNGROUP = 'action-ungroup'
PD_UNGROUP_ALL = 'action-ungroup-all'

PD_CONV_TO_CMYK = 'action-to-cmyk'
PD_CONV_TO_RGB = 'action-to-rgb'
PD_CONV_TO_LAB = 'action-to-lab'
PD_CONV_TO_GRAY = 'action-to-gray'
PD_CONV_TO_BW = 'action-to-bw'
PD_CONV_TO_SPOT = 'action-to-spot'
PD_EMPTY = 'action-empty'
PD_EVENODD = 'action-evenodd'
PD_NONZERO = 'action-nonzero'
PD_INVERT_BITMAP = 'action-invert-bitmap'

PD_TOOL_PAGES = 'pdesign-tool-pages'
PD_TOOL_LAYERS = 'pdesign-tool-layers'
PD_TOOL_OBJBROWSER = 'pdesign-tool-objbrowser'

PD_WARNING = 'gtk-dialog-warning'
PD_HOME = 'gtk-home'
PD_FBPAGE = 'sk1-fb'
PD_ABOUT = 'gtk-about'
PD_STUB_NEW = 'stub-new'
PD_STUB_OPEN = 'stub-open'
PD_STUB_RECENT = 'stub-recent'

ORIGIN_CENTER = 'origin-center'
ORIGIN_LL = 'origin-ll'
ORIGIN_LU = 'origin-lu'

PD_CLOSE_BUTTON = 'pdesign-close-button'
PD_CLOSE_BUTTON_ACTIVE = 'pdesign-close-button-active'
PD_MOUSE_MONITOR = 'mouse-monitor'
PD_APP_STATUS = 'app-status'
PD_PM_ARROW_END = "pager-arrow-end"
PD_PM_ARROW_LEFT = "pager-arrow-left"
PD_PM_ARROW_RIGHT = "pager-arrow-right"
PD_PM_ARROW_START = "pager-arrow-start"

PD_SNAP_TO_GRID_OFF = 'snap-to-grid-off'
PD_SNAP_TO_GRID_ON = 'snap-to-grid-on'
PD_SNAP_TO_GUIDE_OFF = 'snap-to-guide-off'
PD_SNAP_TO_GUIDE_ON = 'snap-to-guide-on'
PD_SNAP_TO_OBJ_OFF = 'snap-to-obj-off'
PD_SNAP_TO_OBJ_ON = 'snap-to-obj-on'
PD_SNAP_TO_PAGE_OFF = 'snap-to-page-off'
PD_SNAP_TO_PAGE_ON = 'snap-to-page-on'

PD_PREFS_CMS = 'prefs-cms'
PD_PREFS_CMS_BANNER = 'prefs-cms-banner'
PD_PREFS_PALETTE = 'prefs-palette'
PD_PREFS_RULER = 'prefs-ruler'
PD_PREFS_GRID = 'prefs-grid'

PD_PALETTE_AUTO = 'palette-auto'
PD_PALETTE_LARGE = 'palette-large'
PD_PALETTE_LIST = 'palette-list'
PD_PALETTE_NORMAL = 'palette-normal'
PD_PALETTE_SWATCH = 'palette-swatch'
PD_DOWNLOAD48 = 'download-48'

#----- MacOS X specific bitmaps
MAC_TBB_NORMAL = 'tbb-normal'
MAC_TBB_PRESSED = 'tbb-pressed'
MAC_TBNB_LEFT_NORMAL = 'tbnb-left-normal'
MAC_TBNB_LEFT_PRESSED = 'tbnb-left-pressed'
MAC_TBNB_MIDDLE_NORMAL = 'tbnb-middle-normal'
MAC_TBNB_MIDDLE_PRESSED = 'tbnb-middle-pressed'
MAC_TBNB_RIGHT_NORMAL = 'tbnb-right-normal'
MAC_TBNB_RIGHT_PRESSED = 'tbnb-right-pressed'
MAC_TBNB_SPACER_ACTIVE = 'tbnb-spacer-active'
MAC_TBNB_SPACER_NORMAL = 'tbnb-spacer-normal'

ICON_MATCH = {
	wx.ART_NEW:PD_NEW,
	wx.ART_FILE_OPEN:PD_OPEN,
	wx.ART_FILE_SAVE:PD_FILE_SAVE,
	wx.ART_FILE_SAVE_AS:PD_FILE_SAVE_AS,
	wx.ART_PRINT:PD_PRINT,
	wx.ART_QUIT:PD_QUIT,
	wx.ART_UNDO:PD_UNDO,
	wx.ART_REDO:PD_REDO,
	wx.ART_CUT:PD_CUT,
	wx.ART_COPY:PD_COPY,
	wx.ART_PASTE:PD_PASTE,
	wx.ART_DELETE:PD_DELETE,
	wx.ART_WARNING:PD_WARNING,
	}

SK1_ICON16 = 'sk1-icon-16x16'
SK1_ICON22 = 'sk1-icon-22x22'
SK1_ICON32 = 'sk1-icon-32x32'
SK1_ICON48 = 'sk1-icon-48x48'
SK1_ICON64 = 'sk1-icon-64x64'
SK1_ICON128 = 'sk1-icon-128x128'
CAIRO_BANNER = 'cairo-banner'
DOCUMENT_ICON = 'document-icon'
PLUGIN_ICON = 'plugin-icon'
ARROW_LEFT = 'arrow-left'
ARROW_RIGHT = 'arrow-right'
ARROW_TOP = 'arrow-top'
ARROW_BOTTOM = 'arrow-bottom'
DOUBLE_ARROW_LEFT = 'double-arrow-left'
DOUBLE_ARROW_RIGHT = 'double-arrow-right'
NO_COLOR = 'no-color'
SLIDER_KNOB = 'slider-knob'

GENERICS = [SK1_ICON16, SK1_ICON22, SK1_ICON32, SK1_ICON48, SK1_ICON64, SK1_ICON128,
		CAIRO_BANNER, DOCUMENT_ICON, ARROW_LEFT, ARROW_RIGHT, PLUGIN_ICON,
		ARROW_TOP, ARROW_BOTTOM, SLIDER_KNOB,
		DOUBLE_ARROW_LEFT, DOUBLE_ARROW_RIGHT, NO_COLOR, PD_TO_CURVES,
		PD_GROUP, PD_UNGROUP, PD_UNGROUP_ALL, PD_COMBINE, PD_BREAK,
		PD_TOOL_PAGES, PD_TOOL_LAYERS, PD_TOOL_OBJBROWSER, PD_FBPAGE,
		PD_CLOSE_BUTTON, PD_CLOSE_BUTTON_ACTIVE, ORIGIN_CENTER, ORIGIN_LL,
		ORIGIN_LU, PD_MOUSE_MONITOR, PD_PM_ARROW_END, PD_PM_ARROW_LEFT,
		PD_PM_ARROW_RIGHT, PD_PM_ARROW_START, PD_APP_STATUS, PD_GUIDES_AT_CENTER,
		PD_INSERT_PAGE, PD_DELETE_PAGE, PD_GOTO_PAGE, PD_NEXT_PAGE, PD_PREV_PAGE,
		PD_PAGE_FRAME, PD_PAGE_GUIDE_FRAME, PD_REMOVE_ALL_GUIDES,
		PD_RAISE_TO_TOP, PD_RAISE, PD_LOWER, PD_LOWER_TO_BOTTOM,
		PD_STUB_NEW, PD_STUB_OPEN, PD_STUB_RECENT, PD_CONV_TO_CMYK,
		PD_CONV_TO_RGB, PD_CONV_TO_LAB, PD_CONV_TO_GRAY, PD_CONV_TO_BW,
		PD_CONV_TO_SPOT, PD_EMPTY, PD_EVENODD, PD_NONZERO,
		PD_INVERT_BITMAP, PD_SNAP_TO_GRID_OFF, PD_SNAP_TO_GRID_ON,
		PD_SNAP_TO_GUIDE_OFF, PD_SNAP_TO_GUIDE_ON, PD_SNAP_TO_OBJ_OFF,
		PD_SNAP_TO_OBJ_ON, PD_SNAP_TO_PAGE_OFF, PD_SNAP_TO_PAGE_ON,

		PD_PREFS_CMS, PD_PREFS_PALETTE, PD_PREFS_RULER, PD_PREFS_GRID,
		PD_PREFS_CMS_BANNER,

		PD_PALETTE_AUTO, PD_PALETTE_LARGE, PD_PALETTE_LIST,
		PD_PALETTE_NORMAL, PD_PALETTE_SWATCH,

		PD_DOWNLOAD48, ]

TOOL_CREATE_CURVE = 'tool-create-curve'
TOOL_CREATE_ELLIPSE = 'tool-create-ellipse'
TOOL_CREATE_POLY = 'tool-create-poly'
TOOL_CREATE_POLYGON = 'tool-create-polygon'
TOOL_CREATE_RECT = 'tool-create-rect'
TOOL_CREATE_TEXT = 'tool-create-text'
TOOL_FILL = 'tool-fill'
TOOL_FLEUR = 'tool-fleur'
TOOL_GRADIENT = 'tool-gradient'
TOOL_SELECT = 'tool-select'
TOOL_SHAPER = 'tool-shaper'
TOOL_STROKE = 'tool-stroke'
TOOL_ZOOM = 'tool-zoom'

TOOLS_ICONS = [TOOL_CREATE_CURVE, TOOL_CREATE_ELLIPSE, TOOL_CREATE_POLY,
	TOOL_CREATE_POLYGON, TOOL_CREATE_RECT, TOOL_CREATE_TEXT, TOOL_FILL,
	TOOL_FLEUR, TOOL_GRADIENT, TOOL_SELECT, TOOL_SHAPER, TOOL_STROKE,
	TOOL_ZOOM, ]

CTX_PAGE_LANDSCAPE = 'ctx-page-landscape'
CTX_PAGE_PORTRAIT = 'ctx-page-portrait'
CTX_UNITS = 'ctx-units'
CTX_OBJECT_JUMP = 'ctx-object-jump'
CTX_OBJECT_RESIZE = 'ctx-object-resize'
CTX_RATIO = 'ctx-ratio'
CTX_NO_RATIO = 'ctx-no-ratio'
CTX_W_ON_H = 'ctx-w-on-h'
CTX_ROTATE = 'ctx-rotate'
CTX_ROTATE_LEFT = 'ctx-rotate-left'
CTX_ROTATE_RIGHT = 'ctx-rotate-right'
CTX_MIRROR_H = 'ctx-mirror-h'
CTX_MIRROR_V = 'ctx-mirror-v'
CTX_POLYGON_NUM = 'ctx-plgn-num'
CTX_POLYGON_CFG = 'ctx-plgn-cfg'
CTX_ROUNDED_RECT = 'ctx-rounded-rect'
CTX_ROUNDED_RECT1_ON = 'ctx-rounded-rect1_on'
CTX_ROUNDED_RECT1_OFF = 'ctx-rounded-rect1_off'
CTX_ROUNDED_RECT2_ON = 'ctx-rounded-rect2_on'
CTX_ROUNDED_RECT2_OFF = 'ctx-rounded-rect2_off'
CTX_ROUNDED_RECT3_ON = 'ctx-rounded-rect3_on'
CTX_ROUNDED_RECT3_OFF = 'ctx-rounded-rect3_off'
CTX_ROUNDED_RECT4_ON = 'ctx-rounded-rect4_on'
CTX_ROUNDED_RECT4_OFF = 'ctx-rounded-rect4_off'
CTX_CIRCLE_ARC = 'circle-arc'
CTX_CIRCLE_CHORD = 'circle-chord'
CTX_CIRCLE_PIE_SLICE = 'circle-pie-slice'
CTX_CIRCLE_END_ANGLE = 'ctx-circle-end-angle'
CTX_CIRCLE_START_ANGLE = 'ctx-circle-start-angle'

CTX_ICONS = [CTX_PAGE_LANDSCAPE, CTX_PAGE_PORTRAIT, CTX_UNITS, CTX_OBJECT_JUMP,
			CTX_OBJECT_RESIZE, CTX_RATIO, CTX_NO_RATIO, CTX_W_ON_H, CTX_ROTATE,
			CTX_ROTATE_LEFT, CTX_ROTATE_RIGHT, CTX_MIRROR_H, CTX_MIRROR_V,
			CTX_POLYGON_NUM, CTX_POLYGON_CFG, CTX_ROUNDED_RECT,
			CTX_ROUNDED_RECT1_ON, CTX_ROUNDED_RECT1_OFF, CTX_ROUNDED_RECT2_ON,
			CTX_ROUNDED_RECT2_OFF, CTX_ROUNDED_RECT3_ON, CTX_ROUNDED_RECT3_OFF,
			CTX_ROUNDED_RECT4_ON, CTX_ROUNDED_RECT4_OFF, CTX_CIRCLE_ARC,
			CTX_CIRCLE_CHORD, CTX_CIRCLE_PIE_SLICE, CTX_CIRCLE_END_ANGLE,
			CTX_CIRCLE_START_ANGLE, ]

GENERIC_ICONS = TOOLS_ICONS + GENERICS + CTX_ICONS



