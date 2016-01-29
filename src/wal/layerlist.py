# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2016 by Igor E. Novikov
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
from wx.lib.agw.ultimatelistctrl import UltimateListCtrl, UltimateListItemAttr, \
ULC_VRULES, ULC_HRULES

import const


class LayerList(UltimateListCtrl):

	pos_x = None
	sel_callback = None
	change_callback = None

	def __init__(self, parent, data=[], images=[], alt_color=True,
				even_color=const.EVEN_COLOR, odd_color=const.ODD_COLOR,
				on_select=None, on_change=None):
		self.alt_color = alt_color
		self.attr1 = UltimateListItemAttr()
		self.attr1.SetBackgroundColour(odd_color)
		self.attr2 = UltimateListItemAttr()
		self.attr2.SetBackgroundColour(even_color)

		self.sel_callback = on_select
		self.change_callback = on_change

		self.il = wx.ImageList(16, 16)
		for icon_id in images:
			bmp = wx.ArtProvider.GetBitmap(icon_id, wx.ART_OTHER, const.SIZE_16)
			self.il.Add(bmp)

		style = wx.LC_REPORT | wx.LC_VRULES | wx.LC_NO_HEADER
		style |= wx.LC_SINGLE_SEL
		style |= wx.LC_VIRTUAL
		style |= ULC_VRULES | ULC_HRULES
		UltimateListCtrl.__init__(self, parent, agwStyle=style)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		for i in range(4):
			self.InsertColumn(i, '')
			self.SetColumnWidth(i, 25)
		self.InsertColumn(4, '')
		self.SetColumnWidth(4, -1)

		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
		self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_down)
		selected = None
		if data:selected = 0
		self.update(data, selected)

	def update(self, data=[], selected=None):
		self.data = data
		self.SetItemCount(len(self.data))
		if not selected is None:
			self.Select(selected, True)

	def on_mouse_down(self, event):
		self.pos_x = event.GetX()
		event.Skip()

	def OnItemSelected(self, event):
		self.current_item = event.m_itemIndex
		if self.sel_callback:
			self.sel_callback(self.current_item)
		if not self.pos_x is None and self.change_callback:
			column = self.pos_x / 25
			if column > 4: column = 4
			self.change_callback(self.current_item, column)
			self.pos_x = None

	def OnGetItemToolTip(self, item, col):
		if col == 4: return self.data[item][4]
		return None

	def OnGetItemTextColour(self, item, col): return const.BLACK

	def OnGetItemText(self, item, col):
		if col == 4: return self.data[item][4]
		return ''

	def OnGetItemImage(self, item):
		return -1

	def OnGetItemAttr(self, item):
		if self.alt_color:
			if not item % 2: return self.attr1
			else: return self.attr2
		return None

	def OnGetItemColumnImage(self, item, column=0):
		if column == 4:return []
		else: return [column * 2 + self.data[item][column]]

	def OnGetItemColumnCheck(self, item, column=0): return []
	def OnGetItemColumnKind(self, item, column=0): return 0
	def OnGetItemKind(self, item): return 0


