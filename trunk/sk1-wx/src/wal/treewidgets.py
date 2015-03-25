# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2015 by Igor E. Novikov
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

import const

NO_ICON = -1

class TreeElement(object):

	name = ''
	icon = None
	childs = []

	def __init__(self, name='', icon=None):
		self.name = name
		self.icon = icon
		self.childs = []

class TreeWidget(wx.TreeCtrl):

	data = None
	items = []
	items_ref = []
	alt_color = True

	use_icons = True
	icon_size = const.SIZE_16
	folder_ico = 0
	file_ico = 0
	imagelist = None

	select_cmd = None

	def __init__(self, parent, data=[], border=True, alt_color=True,
				use_icons=True, on_select=None, highlight_row=True):
		style = wx.TR_DEFAULT_STYLE | wx.TR_HAS_BUTTONS | wx.TR_HIDE_ROOT
		if highlight_row: style |= wx.TR_FULL_ROW_HIGHLIGHT
		if not highlight_row:alt_color = False
		if border: style |= wx.BORDER_MASK
		wx.TreeCtrl.__init__(self, parent, wx.ID_ANY, style=style)
		self.alt_color = alt_color
		self.use_icons = use_icons
		self.select_cmd = on_select

		self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.recolor_items, self)
		self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.recolor_items, self)
		if self.select_cmd:
			self.Bind(wx.EVT_TREE_SEL_CHANGED, self.sel_changed, self)

		self.update(data)

	def sel_changed(self, event):
		item = event.GetItem()
		event.Skip()
		if item:
			self.select_cmd(self.items_ref[self.items.index(item)])

	def init_icons(self):
		self.imagelist = wx.ImageList(self.icon_size[0], self.icon_size[1])
		prov = wx.ArtProvider_GetBitmap
		icon = prov(wx.ART_FOLDER, wx.ART_OTHER, self.icon_size)
		self.folder_ico = self.imagelist.Add(icon)
		icon = prov(wx.ART_NORMAL_FILE, wx.ART_OTHER, self.icon_size)
		self.file_ico = self.imagelist.Add(icon)
		self.SetImageList(self.imagelist)

	def clear_all(self):
		self.DeleteAllItems()
		self.items = []
		self.items_ref = []
		self.init_icons()

	def update(self, data):
		self.clear_all()
		tid = self.AddRoot('root', NO_ICON, NO_ICON)
		self.add_childs(tid, data)
		self.recolor_items()

	def add_childs(self, parent, childs):
		for item in childs:
			icon = self.get_icons(item)
			tid = self.AppendItem(parent, item.name, icon, NO_ICON)
			self.items_ref.append(item)
			self.items.append(tid)
			self.add_childs(tid, item.childs)

	def get_icons(self, item):
		if not self.use_icons: return NO_ICON
		if not item.icon and item.childs:
			return self.folder_ico
		elif not item.icon and not item.childs:
			return self.file_ico
		return self.imagelist.Add(item.icon)

	def expand_all(self):
		self.ExpandAll()
		self.recolor_all_items()

	def collapse_all(self):
		self.CollapseAll()
		self.recolor_items()

	def recolor_all_items(self):
		if not self.alt_color:return
		even = False
		for item in self.items:
			if even:
				self.SetItemBackgroundColour(item, const.ODD_COLOR)
			else:
				self.SetItemBackgroundColour(item, const.EVEN_COLOR)
			even = not even

	def recolor_items(self, *args):
		if not self.alt_color:return
		even = False
		for item in self.items:
			if self.IsVisible(item):
				if even:
					self.SetItemBackgroundColour(item, const.ODD_COLOR)
				else:
					self.SetItemBackgroundColour(item, const.EVEN_COLOR)
				even = not even

	def set_indent(self, val): self.SetIndent(val)
	def get_indent(self): return self.GetIndent()


