# -*- coding: utf-8 -*-
#
#	Copyright (C) 2013 by Igor E. Novikov
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

import os
import wx

from wal import const

from sk1 import config

#Canvas mode enumeration
SELECT_MODE = 0
SHAPER_MODE = 1
ZOOM_MODE = 2
FLEUR_MODE = 3
TEMP_FLEUR_MODE = 5
PICK_MODE = 4
LINE_MODE = 10
CURVE_MODE = 11
RECT_MODE = 12
ELLIPSE_MODE = 13
TEXT_MODE = 14
POLYGON_MODE = 15
ZOOM_OUT_MODE = 16
MOVE_MODE = 17
COPY_MODE = 18
RESIZE_MODE = 19
RESIZE_MODE1 = 20
RESIZE_MODE2 = 21
RESIZE_MODE3 = 22
RESIZE_MODE4 = 23
RESIZE_MODE1_COPY = 24
RESIZE_MODE2_COPY = 25
RESIZE_MODE3_COPY = 26
RESIZE_MODE4_COPY = 27
RESIZE_MODE10 = 28
RESIZE_MODE11 = 29
RESIZE_MODE13 = 30
RESIZE_MODE10_COPY = 31
RESIZE_MODE11_COPY = 32
RESIZE_MODE13_COPY = 33
GUIDE_MODE = 34
VGUIDE_MODE = 35
HGUIDE_MODE = 36
GR_SELECT_MODE = 40
GR_CREATE_MODE = 41
GR_EDIT_MODE = 42
BEZIER_EDITOR_MODE = 43
RECT_EDITOR_MODE = 44
ELLIPSE_EDITOR_MODE = 45
POLYGON_EDITOR_MODE = 45
WAIT_MODE = 100

MODE_LIST = [SELECT_MODE, SHAPER_MODE, ZOOM_MODE, LINE_MODE,
			CURVE_MODE, RECT_MODE, ELLIPSE_MODE, TEXT_MODE,
			POLYGON_MODE, ZOOM_OUT_MODE, MOVE_MODE, RESIZE_MODE, ]

EDIT_MODES = [SHAPER_MODE, BEZIER_EDITOR_MODE, RECT_EDITOR_MODE,
			ELLIPSE_EDITOR_MODE, POLYGON_EDITOR_MODE]
GRAD_MODES = [GR_SELECT_MODE, GR_EDIT_MODE, GR_CREATE_MODE]

def get_cursors():
	cursors = {
			SELECT_MODE:('cur_std', (5, 5)),
			SHAPER_MODE:('cur_edit', (5, 5)),
			ZOOM_MODE:('cur_zoom_in', (6, 6)),
			FLEUR_MODE:('cur_fleur', (11, 4)),
			TEMP_FLEUR_MODE:('cur_fleur', (11, 4)),
			PICK_MODE:('cur_pick', (9, 2)),
			LINE_MODE:('cur_create_polyline', (6, 6)),
			CURVE_MODE:('cur_create_bezier', (6, 6)),
			RECT_MODE:('cur_create_rect', (6, 6)),
			POLYGON_MODE:('cur_create_polygon', (6, 6)),
			ELLIPSE_MODE:('cur_create_ellipse', (6, 6)),
			TEXT_MODE:('cur_text', (4, 8)),
			ZOOM_OUT_MODE:('cur_zoom_out', (6, 6)),
			MOVE_MODE:('cur_move', (5, 5)),
			COPY_MODE:('cur_copy', (5, 5)),
			RESIZE_MODE:('cur_center', (5, 5)),
			RESIZE_MODE1:('cur_resize1', (10, 10)),
			RESIZE_MODE1_COPY:('cur_resize1_copy', (10, 10)),
			RESIZE_MODE2:('cur_resize2', (10, 10)),
			RESIZE_MODE2_COPY:('cur_resize2_copy', (10, 10)),
			RESIZE_MODE3:('cur_resize3', (10, 10)),
			RESIZE_MODE3_COPY:('cur_resize3_copy', (10, 10)),
			RESIZE_MODE4:('cur_resize4', (10, 10)),
			RESIZE_MODE4_COPY:('cur_resize4_copy', (10, 10)),
			RESIZE_MODE10:('cur_resize10', (10, 10)),
			RESIZE_MODE10_COPY:('cur_resize10_copy', (10, 10)),
			RESIZE_MODE11:('cur_resize11', (10, 10)),
			RESIZE_MODE11_COPY:('cur_resize11_copy', (10, 10)),
			RESIZE_MODE13:('cur_resize13', (10, 10)),
			RESIZE_MODE13_COPY:('cur_resize13_copy', (10, 10)),
			GUIDE_MODE:('cur_vguide', (12, 12)),
			VGUIDE_MODE:('cur_vguide', (12, 12)),
			HGUIDE_MODE:('cur_hguide', (12, 12)),
			GR_SELECT_MODE:('cur_gr_edit', (5, 5)),
			GR_CREATE_MODE:('cur_create_gr', (6, 6)),
			GR_EDIT_MODE:('cur_gr_edit', (5, 5)),
			BEZIER_EDITOR_MODE:('cur_edit', (5, 5)),
			RECT_EDITOR_MODE:('cur_edit', (5, 5)),
			ELLIPSE_EDITOR_MODE:('cur_edit', (5, 5)),
			POLYGON_EDITOR_MODE:('cur_edit', (5, 5)),
			}
	keys = cursors.keys()
	ext = '.png'
	if const.is_msw(): ext = '.cur'
	for key in keys:
		path = os.path.join(config.resource_dir, 'cursors', cursors[key][0] + ext)
		x, y = cursors[key][1]
		if const.is_msw():
			cursors[key] = wx.Cursor(path, wx.BITMAP_TYPE_CUR)
		else:
			cursors[key] = wx.Cursor(path, wx.BITMAP_TYPE_PNG, x, y)
	cursors[WAIT_MODE] = wx.StockCursor(wx.CURSOR_WAIT)
	return cursors
