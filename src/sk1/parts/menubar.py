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

import wal

from sk1 import _, config, events
from sk1.resources import pdids

class AppMenuBar(wx.MenuBar):

	def __init__(self, app, mw):
		self.app = app
		self.mw = mw
		wx.MenuBar.__init__(self)
		self.entries = []

		#---File menu
		sub = (wal.ID_NEW, pdids.ID_NEW_FROM_TEMPLATE, None, wal.ID_OPEN,
				(_("Open &Recent"), (HistoryMenu(self.app, self.mw),)),
				None,
				wal.ID_SAVE, wal.ID_SAVEAS, pdids.ID_SAVE_SEL,
				pdids.ID_SAVEALL, None, wal.ID_CLOSE, wal.ID_CLOSE_ALL, None,
				pdids.ID_IMPORT, pdids.ID_EXPORT, None,
				pdids.ID_VIEW_LOG, None, wal.ID_PRINT_SETUP, wal.ID_PRINT,
				None, wal.ID_EXIT,)
		entry = (_("&File"), sub)
		self.entries.append(entry)

		#---Edit menu
		sub = (wal.ID_UNDO, wal.ID_REDO, pdids.ID_CLEAR_UNDO, None, wal.ID_CUT,
				wal.ID_COPY, wal.ID_PASTE, wal.ID_DELETE, pdids.ID_DUPLICATE,
				None, wal.ID_SELECTALL, pdids.ID_DESELECT, pdids.ID_INV_SELECT,
				None, pdids.FILL_MODE, pdids.COPY_FILL, pdids.STROKE_MODE, pdids.COPY_STROKE,
				None, wal.ID_PROPERTIES, wal.ID_PREFERENCES,)
		entry = (_("&Edit"), sub)
		self.entries.append(entry)

		#---View menu
		sub = (pdids.ID_STROKE_VIEW, pdids.ID_DRAFT_VIEW, None,
				wal.ID_ZOOM_100, wal.ID_ZOOM_IN, wal.ID_ZOOM_OUT,
				pdids.ID_PREV_ZOOM, None,
				pdids.ID_ZOOM_PAGE, wal.ID_ZOOM_FIT,
				None,
				(_("&Show"), (pdids.ID_SHOW_GRID, pdids.ID_SHOW_GUIDES,
				pdids.ID_SHOW_SNAP, pdids.ID_SHOW_PAGE_BORDER)),
				None,
				(_("S&nap to"), (pdids.ID_SNAP_TO_GRID, pdids.ID_SNAP_TO_GUIDE,
				pdids.ID_SNAP_TO_OBJ, pdids.ID_SNAP_TO_PAGE)),
				None,
				wal.ID_REFRESH,)
		entry = (_("&View"), sub)
		self.entries.append(entry)

		#---Layout menu
		sub = (pdids.ID_INSERT_PAGE, pdids.ID_DELETE_PAGE, pdids.ID_GOTO_PAGE,
			None, pdids.ID_NEXT_PAGE, pdids.ID_PREV_PAGE,
			None, pdids.ID_TOOL_LAYERS,
			None, pdids.ID_PAGE_FRAME, pdids.ID_PAGE_GUIDE_FRAME,
			pdids.ID_GUIDES_AT_CENTER, pdids.ID_REMOVE_ALL_GUIDES,)
		entry = (_("&Layout"), sub)
		self.entries.append(entry)

		#---Arrange menu
		sub = (
			(_("Trans&form"), (pdids.ID_POSITION_PLGN, pdids.ID_RESIZE_PLGN,
				pdids.ID_SCALE_PLGN, pdids.ID_ROTATE_PLGN, pdids.ID_SHEAR_PLGN,
				None, pdids.ID_ROTATE_LEFT, pdids.ID_ROTATE_RIGHT,
				None, pdids.ID_MIRROR_H, pdids.ID_MIRROR_V)),
			pdids.ID_CLEAR_TRANSFORM,
			None, pdids.ID_ALIGN_PLGN,
			(_("&Order"), (pdids.ID_RAISE_TO_TOP, pdids.ID_RAISE,
				pdids.ID_LOWER, pdids.ID_LOWER_TO_BOTTOM)),
			None, pdids.ID_COMBINE, pdids.ID_BREAK_APART,
			None, pdids.ID_GROUP, pdids.ID_UNGROUP, pdids.ID_UNGROUPALL, None,
			(_("&Shaping"), (pdids.ID_PATHS_TRIM, pdids.ID_PATHS_INTERSECTION,
				pdids.ID_PATHS_EXCLUSION, pdids.ID_PATHS_FUSION)),
			None, pdids.ID_TO_CONTAINER, pdids.ID_FROM_CONTAINER,
			None, pdids.ID_TO_CURVES, pdids.ID_STROKE_TO_CURVES)
		entry = (_("&Arrange"), sub)
		self.entries.append(entry)

		#---Effects menu
# 		sub = (pdids.ID_TO_CONTAINER, pdids.ID_FROM_CONTAINER,)
# 		entry = (_("Effe&cts"), sub)
# 		self.entries.append(entry)

		#---Paths menu
		sub = (pdids.ID_BEZIER_SEL_ALL_NODES, pdids.ID_BEZIER_REVERSE_ALL_PATHS,
			None, pdids.ID_BEZIER_SEL_SUBPATH_NODES, pdids.ID_BEZIER_DEL_SUBPATH,
			pdids.ID_BEZIER_REVERSE_SUBPATH, pdids.ID_BEZIER_EXTRACT_SUBPATH,
			None, pdids.ID_BEZIER_ADD_NODE, pdids.ID_BEZIER_DELETE_NODE,
			None, pdids.ID_BEZIER_ADD_SEG, pdids.ID_BEZIER_DELETE_SEG,
			pdids.ID_BEZIER_JOIN_NODE, pdids.ID_BEZIER_SPLIT_NODE,
			None, pdids.ID_BEZIER_SEG_TO_LINE, pdids.ID_BEZIER_SEG_TO_CURVE,
			None, pdids.ID_BEZIER_NODE_CUSP, pdids.ID_BEZIER_NODE_SMOOTH,
			pdids.ID_BEZIER_NODE_SYMMETRICAL,)
		entry = (_("&Paths"), sub)
		self.entries.append(entry)

		#---Bitmaps menu
		sub = (pdids.ID_CONV_TO_CMYK, pdids.ID_CONV_TO_RGB,# pdids.ID_CONV_TO_LAB,
			pdids.ID_CONV_TO_GRAY, pdids.ID_CONV_TO_BW, None,
			pdids.ID_INVERT_BITMAP, None, pdids.ID_REMOVE_ALPHA,
			pdids.ID_INVERT_ALPHA, None, pdids.ID_EXTRACT_BITMAP)
		entry = (_("&Bitmaps"), sub)
		self.entries.append(entry)

		#---Text menu
		sub = (pdids.ID_EDIT_TEXT, None, pdids.ID_TEXT_ON_PATH,
			pdids.ID_STRAIGHTEN_TEXT, None, pdids.ID_UPPER_TEXT,
			pdids.ID_LOWER_TEXT, pdids.ID_CAPITALIZE_TEXT)
		entry = (_("&Text"), sub)
		self.entries.append(entry)

		#---Tools menu
# 		sub = (
# 			pdids.ID_TOOL_PAGES,
# 			pdids.ID_TOOL_OBJBROWSER,)
# 		entry = (_("T&ools"), sub)
# 		self.entries.append(entry)

		#---Help menu
		sub = (pdids.ID_REPORT_BUG, None, pdids.ID_APP_WEBSITE,
			pdids.ID_APP_FORUM, pdids.ID_APP_FBPAGE, None, wal.ID_ABOUT,)
		entry = (_("&Help"), sub)
		self.entries.append(entry)

		self.create_menu(self, self.entries)
		self.mw.SetMenuBar(self)

	def create_menu(self, parent, entries):
		for entry in entries:
			menu = wx.Menu()
			subentries = entry[1]
			for item in subentries:
				if item is None:
					menu.AppendSeparator()
				elif isinstance(item, wx.Menu):
					menu = item
				elif isinstance(item, tuple):
					self.create_menu(menu, (item,))
				else:
					action = self.app.actions[item]
					menuitem = ActionMenuItem(self.mw, menu, action)
					menu.AppendItem(menuitem)
			parent.AppendMenu(wx.NewId(), entry[0], menu)

	def AppendMenu(self, menu_id, txt, menu):
		self.Append(menu, txt)

class HistoryMenu(wx.Menu):

	app = None
	mw = None
	items = []
	empty_item = None
	persistent_items = []

	def __init__(self, app, mw):
		self.app = app
		self.mw = mw
		wx.Menu.__init__(self)

		self.empty_item = wx.MenuItem(self, wx.NewId(), _('Empty'))
		if not wal.is_wx3(): self.empty_item.Enable(False)

		self.items.append(self.AppendSeparator())
		action = self.app.actions[pdids.ID_CLEAR_LOG]
		menuitem = ActionMenuItem(self.mw, self, action)
		self.AppendItem(menuitem)
		self.items.append(menuitem)

		self.persistent_items += self.items

		self.rebuild()
		events.connect(events.HISTORY_CHANGED, self.rebuild)

	def rebuild(self, *args):
		for item in self.items: self.RemoveItem(item)
		self.items = []
		if self.app.history.is_empty():
			self.items.append(self.empty_item)
			self.AppendItem(self.empty_item)
			self.empty_item.Enable(False)
		else:
			entries = self.app.history.get_menu_entries()
			for entry in entries:
				menuitem = HistoryMenuItem(self.mw, self, entry[0], entry[1])
				self.items.append(menuitem)
				self.AppendItem(menuitem)
			for menuitem in self.persistent_items:
				self.items.append(menuitem)
				self.AppendItem(menuitem)

class HistoryMenuItem(wx.MenuItem):

	app = None
	path = None
	id = None

	def __init__(self, mw, parent, text, path):
		self.app = mw.app
		self.path = path
		self.id = wx.NewId()
		wx.MenuItem.__init__(self, parent, self.id, text=text)
		mw.Bind(wx.EVT_MENU, self.action, id=self.id)

	def action(self, event):
		self.app.open(self.path)


class ActionMenuItem(wx.MenuItem):

	def __init__(self, mw, parent, action):
		self.mw = mw
		self.parent = parent
		self.action = action
		action_id = action.action_id
		text = self.action.get_menu_text()
		if self.action.is_acc:
			text += '\t' + self.action.get_shortcut_text()
		wx.MenuItem.__init__(self, parent, action_id, text=text)
		if not config.is_mac() and self.action.is_icon:
			bmp = self.action.get_icon(config.menu_size, wx.ART_MENU)
			if bmp: self.SetBitmap(bmp)
		self.action.register_as_menuitem(self)
		self.mw.Bind(wx.EVT_MENU, self.action.do_call, id=action_id)
		if self.action.is_toggle():
			self.SetCheckable(True)

	def update(self):
		self.set_enable(self.action.enabled)
		if self.action.is_toggle():
			self.set_active(self.action.active)

	def set_enable(self, enabled):
		if not enabled == self.get_enable():
			self.Enable(enabled)

	def set_active(self, val):
		if not self.IsChecked() == val and self.IsCheckable():
			self.Toggle()

	def get_enable(self):
		return self.IsEnabled()
