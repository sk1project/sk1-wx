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

from sk1.resources import pdids
from sk1.pwidgets import AppAction

from sk1.modes import SELECT_MODE, SHAPER_MODE, ZOOM_MODE, FLEUR_MODE, \
LINE_MODE, CURVE_MODE, RECT_MODE, ELLIPSE_MODE, TEXT_MODE, POLYGON_MODE, \
ZOOM_OUT_MODE, GR_SELECT_MODE, GRAD_MODES, EDIT_MODES
from sk1.events import CLIPBOARD, DOC_CHANGED, PAGE_CHANGED, \
DOC_MODIFIED, DOC_SAVED, NO_DOCS, SELECTION_CHANGED, MODE_CHANGED, \
HISTORY_CHANGED, SNAP_CHANGED

def create_actions(app):
	# action_id, callback, channels, validator, checker,
	# callable_args, validator_args, checker_args

	doc_chnls = [NO_DOCS, DOC_CHANGED]
	tool_chnls = [NO_DOCS, DOC_CHANGED, MODE_CHANGED]
	doc_save_chnls = [NO_DOCS, DOC_CHANGED, DOC_MODIFIED, DOC_SAVED]
	sel_chnls = [NO_DOCS, DOC_CHANGED, SELECTION_CHANGED]
	page_chnls = [NO_DOCS, DOC_CHANGED, DOC_MODIFIED, PAGE_CHANGED]
	snap_chnls = [NO_DOCS, DOC_CHANGED, SNAP_CHANGED]
	insp = app.insp
	proxy = app.proxy
	actions = {}
	entries = [
#----- Canvas modes -----
(pdids.SELECT_MODE, proxy.set_mode, tool_chnls, insp.is_doc, insp.is_mode, [SELECT_MODE], [], [SELECT_MODE]),
(pdids.SHAPER_MODE, proxy.set_mode, tool_chnls, insp.is_doc, insp.is_mode, [SHAPER_MODE], [], EDIT_MODES),
(pdids.ZOOM_MODE, proxy.set_mode, tool_chnls, insp.is_doc, insp.is_mode, [ZOOM_MODE], [], [ZOOM_MODE]),
(pdids.FLEUR_MODE, proxy.set_mode, tool_chnls, insp.is_doc, insp.is_mode, [FLEUR_MODE], [], [FLEUR_MODE]),
(pdids.LINE_MODE, proxy.set_mode, tool_chnls, insp.is_doc, insp.is_mode, [LINE_MODE], [], [LINE_MODE]),
(pdids.CURVE_MODE, proxy.set_mode, tool_chnls, insp.is_doc, insp.is_mode, [CURVE_MODE], [], [CURVE_MODE]),
(pdids.RECT_MODE, proxy.set_mode, tool_chnls, insp.is_doc, insp.is_mode, [RECT_MODE], [], [RECT_MODE]),
(pdids.ELLIPSE_MODE, proxy.set_mode, tool_chnls, insp.is_doc, insp.is_mode, [ELLIPSE_MODE], [], [ELLIPSE_MODE]),
(pdids.TEXT_MODE, proxy.set_mode, tool_chnls, insp.is_doc, insp.is_mode, [TEXT_MODE], [], [TEXT_MODE]),
(pdids.POLYGON_MODE, proxy.set_mode, tool_chnls, insp.is_doc, insp.is_mode, [POLYGON_MODE], [], [POLYGON_MODE]),
(pdids.ZOOM_OUT_MODE, proxy.set_mode, tool_chnls, insp.is_doc, insp.is_mode, [ZOOM_OUT_MODE], [], [ZOOM_OUT_MODE]),
(pdids.GRADIENT_MODE, proxy.set_mode, tool_chnls, insp.is_doc, insp.is_mode, [GR_SELECT_MODE], [], GRAD_MODES),

(pdids.FILL_MODE, proxy.fill_dialog, doc_chnls, insp.is_doc),
(pdids.STROKE_MODE, proxy.stroke_dialog, doc_chnls, insp.is_doc),

(pdids.MOVE_UP, proxy.move_up, sel_chnls, insp.is_selection),
(pdids.MOVE_DOWN, proxy.move_down, sel_chnls, insp.is_selection),
(pdids.MOVE_LEFT, proxy.move_left, sel_chnls, insp.is_selection),
(pdids.MOVE_RIGHT, proxy.move_right, sel_chnls, insp.is_selection),

#------ File menu -------
(wx.ID_NEW, app.new),
(pdids.ID_NEW_FROM_TEMPLATE, app.new_from_template),
(wx.ID_OPEN, app.open),
(pdids.ID_CLEAR_LOG, proxy.clear_log),
(wx.ID_SAVE, proxy.save, doc_save_chnls, insp.is_doc_not_saved),
(wx.ID_SAVEAS, proxy.save_as, doc_chnls, insp.is_doc),
(pdids.ID_SAVE_SEL, proxy.save_selected, sel_chnls, insp.is_selection),
(pdids.ID_SAVEALL, proxy.save_all, doc_save_chnls, insp.is_any_doc_not_saved),
(wx.ID_CLOSE, proxy.close, doc_chnls, insp.is_doc),
(wx.ID_CLOSE_ALL, proxy.close_all, doc_chnls, insp.is_doc),
(pdids.ID_IMPORT, proxy.import_file, doc_chnls, insp.is_doc),
(pdids.ID_EXPORT, proxy.export_as, doc_chnls, insp.is_doc),
(pdids.ID_VIEW_LOG, proxy.view_log, [HISTORY_CHANGED, ] + doc_chnls, insp.is_file_history),
(wx.ID_PRINT_SETUP, proxy.stub, doc_chnls, insp.is_doc),
(wx.ID_PRINT, proxy.stub, doc_chnls, insp.is_doc),
(wx.ID_EXIT, proxy.exit),
#------ Edit menu -------
(wx.ID_UNDO, proxy.undo, doc_save_chnls, insp.is_undo),
(wx.ID_REDO, proxy.redo, doc_save_chnls, insp.is_redo),
(pdids.ID_CLEAR_UNDO, proxy.clear_history, doc_chnls, insp.is_history),
(wx.ID_CUT, proxy.cut, sel_chnls, insp.is_selection),
(wx.ID_COPY, proxy.copy, sel_chnls, insp.is_selection),
(wx.ID_PASTE, proxy.paste, [NO_DOCS, DOC_CHANGED, CLIPBOARD], insp.is_clipboard),
(wx.ID_DELETE, proxy.delete, sel_chnls, insp.can_be_deleted),
(pdids.ID_DUPLICATE, proxy.duplicate, sel_chnls, insp.is_selection),
(wx.ID_SELECTALL, proxy.select_all, doc_chnls, insp.is_doc),
(pdids.ID_DESELECT, proxy.deselect, sel_chnls, insp.is_selection),
(pdids.ID_INV_SELECT, proxy.invert_selection, doc_chnls, insp.is_doc),
(pdids.COPY_FILL, proxy.copy_fill, sel_chnls, insp.is_selection),
(pdids.COPY_STROKE, proxy.copy_stroke, sel_chnls, insp.is_selection),
(wx.ID_PROPERTIES, proxy.stub, doc_chnls, insp.is_doc),
(wx.ID_PREFERENCES, proxy.preferences),
#------ View menu -------
(pdids.ID_STROKE_VIEW, proxy.stroke_view, doc_chnls, insp.is_doc, insp.is_stroke_view),
(pdids.ID_DRAFT_VIEW, proxy.draft_view, doc_chnls, insp.is_doc, insp.is_draft_view),
(wx.ID_ZOOM_100, proxy.zoom_100, doc_chnls, insp.is_doc),
(wx.ID_ZOOM_IN, proxy.zoom_in, doc_chnls, insp.is_doc),
(wx.ID_ZOOM_OUT, proxy.zoom_out, doc_chnls, insp.is_doc),
(pdids.ID_PREV_ZOOM, proxy.previous_zoom, doc_chnls, insp.is_doc),
(pdids.ID_ZOOM_PAGE, proxy.fit_zoom_to_page, doc_chnls, insp.is_doc),
(wx.ID_ZOOM_FIT, proxy.zoom_selected, sel_chnls, insp.is_selection),
	(pdids.ID_SHOW_GRID, proxy.show_grid, doc_chnls, insp.is_doc, insp.is_grid_visible),
	(pdids.ID_SHOW_GUIDES, proxy.show_guides, doc_chnls, insp.is_doc, insp.is_guides_visible),
	(pdids.ID_SHOW_SNAP, proxy.show_snapping, doc_chnls, insp.is_doc, insp.is_show_snapping),
	(pdids.ID_SHOW_PAGE_BORDER, proxy.draw_page_border, doc_chnls, insp.is_doc, insp.is_draw_page_border),
	(pdids.ID_SNAP_TO_GRID, proxy.snap_to_grid, snap_chnls, insp.is_doc, insp.is_snap_to_grid),
	(pdids.ID_SNAP_TO_GUIDE, proxy.snap_to_guides, snap_chnls, insp.is_doc, insp.is_snap_to_guides),
	(pdids.ID_SNAP_TO_OBJ, proxy.snap_to_objects, snap_chnls, insp.is_doc, insp.is_snap_to_objects),
	(pdids.ID_SNAP_TO_PAGE, proxy.snap_to_page, snap_chnls, insp.is_doc, insp.is_snap_to_page),
(wx.ID_REFRESH, proxy.force_redraw, doc_chnls, insp.is_doc),
#------ Layout menu -------
(pdids.ID_INSERT_PAGE, proxy.insert_page, page_chnls, insp.is_doc),
(pdids.ID_DELETE_PAGE, proxy.delete_page, page_chnls, insp.can_delete_page),
(pdids.ID_GOTO_PAGE, proxy.goto_page, page_chnls, insp.can_goto_page),
(pdids.ID_NEXT_PAGE, proxy.next_page, page_chnls, insp.can_be_next_page),
(pdids.ID_PREV_PAGE, proxy.previous_page, page_chnls, insp.can_be_previous_page),
(pdids.ID_PAGE_FRAME, proxy.create_page_border, doc_chnls, insp.is_doc),
(pdids.ID_PAGE_GUIDE_FRAME, proxy.create_guide_border, doc_chnls, insp.is_doc),
(pdids.ID_GUIDES_AT_CENTER, proxy.create_guides_at_center, doc_chnls, insp.is_doc),
(pdids.ID_REMOVE_ALL_GUIDES, proxy.remove_all_guides, doc_chnls, insp.is_doc),
#------ Arrange menu -------
(pdids.ID_CLEAR_TRANSFORM, proxy.clear_trafo, sel_chnls, insp.can_clear_trafo),
(pdids.ID_ROTATE_LEFT, proxy.rotate_left, sel_chnls, insp.is_selection),
(pdids.ID_ROTATE_RIGHT, proxy.rotate_right, sel_chnls, insp.is_selection),
(pdids.ID_MIRROR_H, proxy.mirror_h, sel_chnls, insp.is_selection),
(pdids.ID_MIRROR_V, proxy.mirror_v, sel_chnls, insp.is_selection),
(pdids.ID_COMBINE, proxy.combine_selected, sel_chnls, insp.can_be_combined),
(pdids.ID_BREAK_APART, proxy.break_apart_selected, sel_chnls, insp.can_be_breaked),
(pdids.ID_RAISE_TO_TOP, proxy.raise_to_top, sel_chnls, insp.can_be_raised),
(pdids.ID_RAISE, proxy.raise_obj, sel_chnls, insp.can_be_raised),
(pdids.ID_LOWER, proxy.lower_obj, sel_chnls, insp.can_be_lower),
(pdids.ID_LOWER_TO_BOTTOM, proxy.lower_to_bottom, sel_chnls, insp.can_be_lower),
(pdids.ID_GROUP, proxy.group, sel_chnls, insp.can_be_grouped),
(pdids.ID_UNGROUP, proxy.ungroup, sel_chnls, insp.can_be_ungrouped),
(pdids.ID_UNGROUPALL, proxy.ungroup_all, sel_chnls, insp.can_be_ungrouped_all),
(pdids.ID_TO_CURVES, proxy.convert_to_curve, sel_chnls, insp.can_be_curve),
#------ Effects menu -------
(pdids.ID_TO_CONTAINER, proxy.set_container, sel_chnls, insp.is_selection),
(pdids.ID_FROM_CONTAINER, proxy.unpack_container, sel_chnls, insp.is_container_selected),
#------ Nodes menu -------
(pdids.ID_BEZIER_ADD_NODE, proxy.add_node, sel_chnls, insp.can_be_added_node),
(pdids.ID_BEZIER_DELETE_NODE, proxy.delete_node, sel_chnls, insp.can_be_deleted_node),
#------ Bitmaps menu -------
(pdids.ID_CONV_TO_CMYK, proxy.conv_to_cmyk, sel_chnls, insp.can_be_cmyk),
(pdids.ID_CONV_TO_RGB, proxy.conv_to_rgb, sel_chnls, insp.can_be_rgb),
(pdids.ID_CONV_TO_LAB, proxy.conv_to_lab, sel_chnls, insp.can_be_lab),
(pdids.ID_CONV_TO_GRAY, proxy.conv_to_gray, sel_chnls, insp.can_be_gray),
(pdids.ID_CONV_TO_BW, proxy.conv_to_bw, sel_chnls, insp.can_be_bw),
(pdids.ID_INVERT_BITMAP, proxy.invert_bitmap, sel_chnls, insp.is_pixmap_selected),
(pdids.ID_REMOVE_ALPHA, proxy.remove_alpha, sel_chnls, insp.is_pixmap_alpha),
(pdids.ID_INVERT_ALPHA, proxy.invert_alpha, sel_chnls, insp.is_pixmap_alpha),
(pdids.ID_EXTRACT_BITMAP, app.extract_bitmap, sel_chnls, insp.is_pixmap_selected),
#------ Text menu -------
(pdids.ID_EDIT_TEXT, proxy.stub),
#------ Tools menu -------
(pdids.ID_TOOL_PAGES, proxy.show_plugin, doc_chnls, insp.is_doc, None, ('TestPlugin',)),
(pdids.ID_TOOL_LAYERS, proxy.show_plugin, doc_chnls, insp.is_doc, None, ('AnotherTestPlugin',)),
(pdids.ID_TOOL_OBJBROWSER, proxy.stub),
#------ Help menu -------
(pdids.ID_REPORT_BUG, proxy.open_url, [], None, None, ('http://sk1project.org/contact.php',)),
(pdids.ID_APP_WEBSITE, proxy.open_url, [], None, None, ('http://sk1project.org',)),
(pdids.ID_APP_FORUM, proxy.open_url, [], None, None, ('http://sk1project.org/forum/index.php',)),
(pdids.ID_APP_FBPAGE, proxy.open_url, [], None, None, ('http://www.facebook.com/pages/sK1-Project/308311182521658',)),
(wx.ID_ABOUT, proxy.about),
	]
# action_id, callback, channels, validator, checker,
# callable_args, validator_args, checker_args
	for entry in entries:
		actions[entry[0]] = AppAction(*entry)

	return actions
