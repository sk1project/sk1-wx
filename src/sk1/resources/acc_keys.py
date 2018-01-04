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
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import wal

from sk1.resources import pdids

GENERIC_KEYS = {
    # ----- File menu
    wal.ID_NEW: (wal.ACCEL_CTRL, ord('N')),
    pdids.ID_NEW_FROM_TEMPLATE: (wal.ACCEL_SHIFT | wal.ACCEL_CTRL, ord('N')),
    wal.ID_OPEN: (wal.ACCEL_CTRL, ord('O')),
    wal.ID_SAVE: (wal.ACCEL_CTRL, ord('S')),
    pdids.ID_SAVE_SEL: (wal.ACCEL_SHIFT | wal.ACCEL_CTRL, ord('S')),
    pdids.ID_IMPORT: (wal.ACCEL_CTRL, ord('I')),
    wal.ID_CLOSE: (wal.ACCEL_CTRL, ord('W')),
    wal.ID_PRINT: (wal.ACCEL_CTRL, ord('P')),
    wal.ID_EXIT: (wal.ACCEL_ALT, wal.KEY_F4),
    # ----- Edit menu
    wal.ID_UNDO: (wal.ACCEL_CTRL, ord('Z')),
    wal.ID_REDO: (wal.ACCEL_SHIFT | wal.ACCEL_CTRL, ord('Z')),
    wal.ID_CUT: [(wal.ACCEL_CTRL, ord('X')),
                 (wal.ACCEL_SHIFT, wal.KEY_DELETE)],
    wal.ID_COPY: (wal.ACCEL_CTRL, ord('C')),
    wal.ID_PASTE: [(wal.ACCEL_CTRL, ord('V')),
                   (wal.ACCEL_SHIFT, wal.KEY_INSERT)],
    wal.ID_DELETE: [(wal.ACCEL_NORMAL, wal.KEY_DELETE),
                    (wal.ACCEL_NORMAL, wal.KEY_NUMPAD_DELETE)],
    pdids.ID_DUPLICATE: (wal.ACCEL_CTRL, ord('D')),
    wal.ID_SELECTALL: (wal.ACCEL_CTRL, ord('A')),
    pdids.ID_DESELECT: (wal.ACCEL_SHIFT | wal.ACCEL_CTRL, ord('A')),
    # pdids.ID_INV_SELECT:(wal.ACCEL_SHIFT, ord('A')),
    pdids.COPY_FILL: (wal.ACCEL_SHIFT, wal.KEY_F11),
    pdids.COPY_STROKE: (wal.ACCEL_SHIFT, wal.KEY_F12),
    # ----- View menu
    pdids.ID_STROKE_VIEW: (wal.ACCEL_SHIFT, wal.KEY_F9),
    pdids.ID_PREV_ZOOM: (wal.ACCEL_NORMAL, wal.KEY_F3),
    pdids.ID_ZOOM_PAGE: (wal.ACCEL_SHIFT, wal.KEY_F4),
    wal.ID_ZOOM_FIT: (wal.ACCEL_NORMAL, wal.KEY_F4),
    wal.ID_REFRESH: (wal.ACCEL_ALT, ord('R')),
    pdids.ID_SNAP_TO_GRID: (wal.ACCEL_ALT, ord('G')),
    pdids.ID_SNAP_TO_GUIDE: (wal.ACCEL_ALT, ord('I')),
    pdids.ID_SNAP_TO_OBJ: (wal.ACCEL_ALT, ord('O')),
    pdids.ID_SNAP_TO_PAGE: (wal.ACCEL_ALT, ord('P')),
    # ----- Layout menu
    pdids.ID_NEXT_PAGE: [(wal.ACCEL_NORMAL, wal.KEY_PAGEDOWN),
                         (wal.ACCEL_NORMAL, wal.KEY_NUMPAD_PAGEDOWN)],
    pdids.ID_PREV_PAGE: [(wal.ACCEL_NORMAL, wal.KEY_PAGEUP),
                         (wal.ACCEL_NORMAL, wal.KEY_NUMPAD_PAGEUP)],
    # ----- Arrange menu
    pdids.ID_POSITION_PLGN: (wal.ACCEL_ALT, wal.KEY_F5),
    pdids.ID_RESIZE_PLGN: (wal.ACCEL_ALT, wal.KEY_F6),
    pdids.ID_ROTATE_PLGN: (wal.ACCEL_CTRL, wal.KEY_F9),
    pdids.ID_ALIGN_PLGN: (wal.ACCEL_CTRL | wal.ACCEL_SHIFT, ord('D')),
    pdids.ID_COMBINE: (wal.ACCEL_CTRL, ord('L')),
    pdids.ID_BREAK_APART: (wal.ACCEL_CTRL, ord('K')),
    pdids.ID_RAISE_TO_TOP: (wal.ACCEL_CTRL | wal.ACCEL_SHIFT, wal.KEY_PAGEUP),
    pdids.ID_RAISE: (wal.ACCEL_CTRL, wal.KEY_PAGEUP),
    pdids.ID_LOWER: (wal.ACCEL_CTRL, wal.KEY_PAGEDOWN),
    pdids.ID_LOWER_TO_BOTTOM: (wal.ACCEL_CTRL |
                               wal.ACCEL_SHIFT, wal.KEY_PAGEDOWN),
    pdids.ID_GROUP: (wal.ACCEL_CTRL, ord('G')),
    pdids.ID_UNGROUP: (wal.ACCEL_CTRL, ord('U')),
    pdids.ID_UNGROUPALL: (wal.ACCEL_CTRL | wal.ACCEL_SHIFT, ord('U')),
    pdids.ID_TO_CURVES: (wal.ACCEL_CTRL, ord('Q')),
    pdids.ID_STROKE_TO_CURVES: (wal.ACCEL_CTRL | wal.ACCEL_SHIFT, ord('Q')),
    # ----- Text menu
    pdids.ID_EDIT_TEXT: (wal.ACCEL_NORMAL, wal.KEY_F8),
    # ----- Tools menu
    pdids.FILL_MODE: (wal.ACCEL_NORMAL, wal.KEY_F11),
    pdids.STROKE_MODE: (wal.ACCEL_NORMAL, wal.KEY_F12),
    pdids.ID_TOOL_PAGES: (wal.ACCEL_SHIFT, wal.KEY_F7),
    pdids.ID_TOOL_LAYERS: (wal.ACCEL_NORMAL, wal.KEY_F7),
}
