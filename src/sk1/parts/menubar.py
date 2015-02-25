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

from sk1 import _, config, events
from sk1.resources import pdids

class AppMenuBar(wx.MenuBar):

	def __init__(self, app, mw):
		self.app = app
		self.mw = mw
		wx.MenuBar.__init__(self)
		self.entries = []

		#---File menu
		sub = (wx.ID_NEW, None, wx.ID_OPEN,
				(_("Open &Recent"), (HistoryMenu(self.app, self.mw),)),
				None,
				wx.ID_SAVE, wx.ID_SAVEAS, pdids.ID_SAVE_SEL,
				pdids.ID_SAVEALL, None, wx.ID_CLOSE, wx.ID_CLOSE_ALL, None,
				pdids.ID_IMPORT, None,
				pdids.ID_VIEW_LOG, None, wx.ID_PRINT_SETUP, wx.ID_PRINT,
				None, wx.ID_EXIT,)
		entry = (_("&File"), sub)
		self.entries.append(entry)

		#---Edit menu
		sub = (wx.ID_UNDO, wx.ID_REDO, pdids.ID_CLEAR_UNDO, None, wx.ID_CUT,
				wx.ID_COPY, wx.ID_PASTE, wx.ID_DELETE, pdids.ID_DUPLICATE,
				None, wx.ID_SELECTALL, pdids.ID_DESELECT, pdids.ID_INV_SELECT,
				None, wx.ID_PROPERTIES, wx.ID_PREFERENCES,)
		entry = (_("&Edit"), sub)
		self.entries.append(entry)

		#---View menu
		sub = (pdids.ID_STROKE_VIEW, pdids.ID_DRAFT_VIEW, None,
				wx.ID_ZOOM_100, wx.ID_ZOOM_IN, wx.ID_ZOOM_OUT,
				pdids.ID_PREV_ZOOM, None,
				pdids.ID_ZOOM_PAGE, wx.ID_ZOOM_FIT,
				None,
				(_("&Show"), (pdids.ID_SHOW_GRID, pdids.ID_SHOW_GUIDES,
				pdids.ID_SHOW_SNAP, pdids.ID_SHOW_PAGE_BORDER)),
				None,
				(_("S&nap to"), (pdids.ID_SNAP_TO_GRID, pdids.ID_SNAP_TO_GUIDE,
				pdids.ID_SNAP_TO_OBJ, pdids.ID_SNAP_TO_PAGE)),
				None,
				wx.ID_REFRESH,)
		entry = (_("&View"), sub)
		self.entries.append(entry)

		#---Layout menu
		sub = (pdids.ID_INSERT_PAGE, pdids.ID_DELETE_PAGE, pdids.ID_GOTO_PAGE,
			None, pdids.ID_NEXT_PAGE, pdids.ID_PREV_PAGE, None,
			pdids.ID_PAGE_FRAME, pdids.ID_PAGE_GUIDE_FRAME,
			pdids.ID_GUIDES_AT_CENTER, pdids.ID_REMOVE_ALL_GUIDES,)
		entry = (_("&Layout"), sub)
		self.entries.append(entry)

		#---Arrange menu
		sub = (
			(_("Trans&form"), (pdids.ID_ROTATE_LEFT, pdids.ID_ROTATE_RIGHT,
				None, pdids.ID_MIRROR_H, pdids.ID_MIRROR_V)),
			pdids.ID_CLEAR_TRANSFORM,
			None, pdids.ID_COMBINE, pdids.ID_BREAK_APART, None,
			(_("&Order"), (pdids.ID_RAISE_TO_TOP, pdids.ID_RAISE,
				pdids.ID_LOWER, pdids.ID_LOWER_TO_BOTTOM)),
			None, pdids.ID_GROUP,
			pdids.ID_UNGROUP, pdids.ID_UNGROUPALL, None, pdids.ID_TO_CURVES,)
		entry = (_("&Arrange"), sub)
		self.entries.append(entry)

		#---Effects menu
		sub = (pdids.ID_TO_CONTAINER, pdids.ID_FROM_CONTAINER,)
		entry = (_("Effe&cts"), sub)
		self.entries.append(entry)

		#---Bitmaps menu
		sub = ()
		entry = (_("&Bitmaps"), sub)
		self.entries.append(entry)

		#---Text menu
		sub = (pdids.ID_EDIT_TEXT,)
		entry = (_("&Text"), sub)
		self.entries.append(entry)

		#---Tools menu
		sub = (pdids.ID_TOOL_PAGES, pdids.ID_TOOL_LAYERS,
			pdids.ID_TOOL_OBJBROWSER,)
		entry = (_("T&ools"), sub)
		self.entries.append(entry)

		#---Help menu
		sub = (pdids.ID_REPORT_BUG, None, pdids.ID_APP_WEBSITE,
			pdids.ID_APP_FORUM, pdids.ID_APP_FBPAGE, None, wx.ID_ABOUT,)
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
		self.empty_item.Enable(False)

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
		self.action.register(self)
		self.mw.Bind(wx.EVT_MENU, self.action.do_call, id=action_id)
		if self.action.is_toggle():
			self.SetCheckable(True)

	def update(self):
		self.set_enable(self.action.enabled)
		if self.action.is_toggle():
			self.set_active(self.action.active)

	def set_enable(self, enabled):
		self.Enable(enabled)

	def set_active(self, val):
		if not self.IsChecked() == val and self.IsCheckable():
			self.Toggle()
