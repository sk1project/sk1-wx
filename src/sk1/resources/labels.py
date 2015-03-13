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

from sk1 import _
from sk1.resources import pdids

#----- Text labels format: menu label, long description(optional)

LABELS = {
pdids.SELECT_MODE: (_('Selection mode'),),
pdids.SHAPER_MODE: (_('Edit mode'),),
pdids.ZOOM_MODE: (_('Zoom mode'),),
pdids.FLEUR_MODE: (_('Fleur mode'),),
pdids.LINE_MODE: (_('Create polyline'),),
pdids.CURVE_MODE: (_('Create curve'),),
pdids.RECT_MODE: (_('Create rectangle'),),
pdids.ELLIPSE_MODE: (_('Create ellipse'),),
pdids.TEXT_MODE: (_('Create text'),),
pdids.POLYGON_MODE: (_('Create polygon'),),
pdids.ZOOM_OUT_MODE: (_('Zoom out mode'),),
pdids.MOVE_MODE: (_('Move mode'),),
pdids.COPY_MODE: (_('Copy mode'),),

wx.ID_NEW: (_('&New'), _('New document')),
wx.ID_OPEN: (_('&Open...'), _('Open document')),
pdids.ID_CLEAR_LOG: (_('&Clear history'),),
wx.ID_SAVE:(_('&Save'), _('Save document')),
wx.ID_SAVEAS:(_('Save &As...'), _('Save document as...')),
pdids.ID_SAVE_SEL:(_('Save Selected Only...'), ('Save selected objects only...')),
pdids.ID_SAVEALL:(_('Save All'), ('Save all documents')),
pdids.ID_IMPORT:(_('&Import...'), ('Import graphics...')),
wx.ID_CLOSE:(_('&Close'), _('Close document')),
wx.ID_CLOSE_ALL:(_('Close All'), _('Close all documents')),
wx.ID_PRINT_SETUP:(_('Print Setup...'),),
wx.ID_PRINT:(_('&Print'), _('Print document')),
wx.ID_EXIT: (_('&Exit'), _('Exit application')),

wx.ID_UNDO: (_('&Undo'),),
wx.ID_REDO: (_('&Redo'),),
pdids.ID_CLEAR_UNDO:(_('Clear undo history'),),
wx.ID_CUT:(_('Cu&t'),),
wx.ID_COPY:(_('&Copy'),),
wx.ID_PASTE:(_('&Paste'),),
wx.ID_DELETE:(_('&Delete'),),
pdids.ID_DUPLICATE:(_('Duplicate'),),
wx.ID_SELECTALL:(_('&Select All'),),
pdids.ID_DESELECT:(_('D&eselect'),),
pdids.ID_INV_SELECT:(_('&Invert selection'),),
pdids.ID_VIEW_LOG: (_('&File history logs'),),
wx.ID_PROPERTIES:(_('Document properties'),),
wx.ID_PREFERENCES:(_('Preferences'),),

pdids.ID_STROKE_VIEW:(_('Stroke view'),),
pdids.ID_DRAFT_VIEW:(_('Draft view'),),
wx.ID_ZOOM_100:(_('Zoom 100%'),),
wx.ID_ZOOM_IN:(_('Zoom in'),),
wx.ID_ZOOM_OUT:(_('Zoom out'),),
pdids.ID_PREV_ZOOM:(_('Previous zoom'),),
pdids.ID_ZOOM_PAGE:(_('Fit zoom to page'),),
wx.ID_ZOOM_FIT:(_('Zoom selected'),),
pdids.ID_SHOW_GRID:(_('Show grid'),),
pdids.ID_SHOW_GUIDES:(_('Show guides'),),
pdids.ID_SHOW_SNAP:(_('Show active snapping'),),
pdids.ID_SHOW_PAGE_BORDER:(_('Show page border'),),
pdids.ID_SNAP_TO_GRID:(_('Snap to grid'),),
pdids.ID_SNAP_TO_GUIDE:(_('Snap to guide'),),
pdids.ID_SNAP_TO_OBJ:(_('Snap to objects'),),
pdids.ID_SNAP_TO_PAGE:(_('Snap to page'),),
wx.ID_REFRESH:(_('Redraw document'),),

pdids.ID_INSERT_PAGE:(_('Insert page...'),),
pdids.ID_DELETE_PAGE:(_('Delete page...'),),
pdids.ID_GOTO_PAGE:(_('Go to page...'),),
pdids.ID_NEXT_PAGE:(_('Next page'),),
pdids.ID_PREV_PAGE:(_('Previous page'),),
pdids.ID_GUIDES_AT_CENTER:(_('Guides at page center'),),
pdids.ID_PAGE_FRAME:(_('Page frame'),),
pdids.ID_PAGE_GUIDE_FRAME:(_('Guides around page'),),
pdids.ID_REMOVE_ALL_GUIDES:(_('Remove all guides'),),

pdids.ID_CLEAR_TRANSFORM:(_('Clear transformations'),),
pdids.ID_ROTATE_LEFT:(_('Rotate &left 90°'),),
pdids.ID_ROTATE_RIGHT:(_('Rotate &right 90°'),),
pdids.ID_MIRROR_H:(_('&Horizontal mirror'),),
pdids.ID_MIRROR_V:(_('&Vertical mirror'),),
pdids.ID_COMBINE:(_('&Combine'),),
pdids.ID_BREAK_APART:(_('&Break Apart'),),
pdids.ID_RAISE_TO_TOP:(_('Raise to &Top'),),
pdids.ID_RAISE:(_('&Raise'),),
pdids.ID_LOWER:(_('&Lower'),),
pdids.ID_LOWER_TO_BOTTOM:(_('Lower to &Bottom'),),
pdids.ID_GROUP:(_('&Group'),),
pdids.ID_UNGROUP:(_('&Ungroup'),),
pdids.ID_UNGROUPALL:(_('U&ngroup All'),),
pdids.ID_TO_CURVES:(_('Con&vert to curves'),),

pdids.ID_TO_CONTAINER:(_('&Place into container'),),
pdids.ID_FROM_CONTAINER:(_('&Extract from container'),),

pdids.ID_INVERT_BITMAP:(_('Invert bitmap'),),
pdids.ID_REMOVE_ALPHA:(_('Remove alpha-channel'),),
pdids.ID_INVERT_ALPHA:(_('Invert alpha-channel'),),

pdids.ID_EDIT_TEXT:(_('&Edit text'),),

pdids.ID_TOOL_PAGES:(_('Pages'),),
pdids.ID_TOOL_LAYERS:(_('Layers'),),
pdids.ID_TOOL_OBJBROWSER:(_('Object browser'),),

pdids.ID_REPORT_BUG:(_('&Report bug'),),
pdids.ID_APP_WEBSITE:(_('Project web site'),),
pdids.ID_APP_FORUM:(_('Project forum'),),
pdids.ID_APP_FBPAGE:(_('Project page on Face&book'),),
wx.ID_ABOUT:(_('&About sK1'),),
}
