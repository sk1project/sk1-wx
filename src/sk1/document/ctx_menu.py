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

import wx

from sk1 import config, modes
from sk1.resources import pdids

UNDO = [wx.ID_UNDO, wx.ID_REDO]
EDIT = [None, wx.ID_CUT, wx.ID_COPY, wx.ID_PASTE,
	wx.ID_DELETE, pdids.ID_DUPLICATE, None, wx.ID_SELECTALL]
STYLE = [None, pdids.FILL_MODE, pdids.STROKE_MODE, pdids.COPY_FILL,
		pdids.COPY_STROKE]
DEFAULT = [None, wx.ID_PROPERTIES]
COMBINE = [None, pdids.ID_COMBINE, pdids.ID_BREAK_APART, ]
TO_CURVES = [None, pdids.ID_TO_CURVES]
GROUP = [None, pdids.ID_GROUP, pdids.ID_UNGROUP, pdids.ID_UNGROUPALL, ]
BEZIER_EDIT = [None, wx.ID_SELECTALL, pdids.ID_DESELECT, pdids.ID_INV_SELECT,
None, pdids.ID_BEZIER_ADD_NODE, pdids.ID_BEZIER_DELETE_NODE,
None, pdids.ID_BEZIER_ADD_SEG, pdids.ID_BEZIER_DELETE_SEG,
pdids.ID_BEZIER_JOIN_NODE, pdids.ID_BEZIER_SPLIT_NODE,
None, pdids.ID_BEZIER_SEG_TO_LINE, pdids.ID_BEZIER_SEG_TO_CURVE,
None, pdids.ID_BEZIER_NODE_CUSP, pdids.ID_BEZIER_NODE_SMOOTH,
pdids.ID_BEZIER_NODE_SYMMETRICAL]
TEXT = [None, pdids.ID_UPPER_TEXT, pdids.ID_LOWER_TEXT, pdids.ID_CAPITALIZE_TEXT]

class ContextMenu(wx.Menu):

	app = None
	mw = None
	insp = None
	actions = None
	items = []
	persistent_items = []

	def __init__(self, app, parent):
		self.app = app
		self.mw = app.mw
		self.parent = parent
		self.insp = self.app.insp
		self.actions = self.app.actions
		wx.Menu.__init__(self)
		self.build_menu(UNDO)
		self.persistent_items = self.items
		self.items = []

	def destroy(self):
		items = self.__dict__.keys()
		for item in items:
			self.__dict__[item] = None

	def rebuild(self):
		for item in self.persistent_items:
			if not item.IsSeparator(): item.update()
		self.build_menu(self.get_entries())

	def build_menu(self, entries):
		for item in self.items: self.RemoveItem(item)
		self.items = []
		for item in entries:
			if item is None:
				self.items.append(self.AppendSeparator())
			else:
				action = self.app.actions[item]
				menuitem = CtxActionMenuItem(self.parent, self, action)
				self.AppendItem(menuitem)
				menuitem.update()
				self.items.append(menuitem)

	def get_entries(self):
		if not self.insp.is_selection():
			if self.insp.is_mode(modes.BEZIER_EDITOR_MODE):
				return BEZIER_EDIT
			elif self.app.current_doc.canvas.mode == modes.TEXT_EDIT_MODE:
				return EDIT + TEXT + DEFAULT
		else:
			doc = self.app.current_doc
			sel = doc.selection.objs
			if len(sel) > 1:
				return EDIT + COMBINE + GROUP + STYLE + TO_CURVES
			elif self.insp.is_obj_rect(sel[0]):
				return EDIT + self.get_order_entries() + STYLE + TO_CURVES
			elif self.insp.is_obj_circle(sel[0]):
				return EDIT + self.get_order_entries() + STYLE + TO_CURVES
			elif self.insp.is_obj_polygon(sel[0]):
				return EDIT + self.get_order_entries() + STYLE + TO_CURVES
			elif self.insp.is_obj_curve(sel[0]):
				return EDIT + self.get_order_entries() + STYLE + COMBINE
			elif self.insp.can_be_ungrouped():
				return EDIT + self.get_order_entries() + STYLE + GROUP
			elif self.insp.is_obj_pixmap(sel[0]):
				return EDIT + self.get_order_entries()
		return EDIT + DEFAULT

	def get_order_entries(self):
		ret = []
		if self.insp.can_be_raised():
			ret += [pdids.ID_RAISE_TO_TOP, pdids.ID_RAISE]
		if self.insp.can_be_lower():
			ret += [pdids.ID_LOWER, pdids.ID_LOWER_TO_BOTTOM]
		if ret: ret = [None, ] + ret
		return ret


class CtxActionMenuItem(wx.MenuItem):

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
