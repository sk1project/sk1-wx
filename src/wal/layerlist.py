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
ULC_SHOW_TOOLTIPS

import const


class LayerList(UltimateListCtrl):

	pos_x = None

	def __init__(self, parent, data=[], images=[], tooltips=[], alt_color=True,
				even_color=const.EVEN_COLOR, odd_color=const.ODD_COLOR):
		self.data = data
		self.tooltips = tooltips
		self.alt_color = alt_color
		self.attr1 = UltimateListItemAttr()
		self.attr1.SetBackgroundColour(odd_color)
		self.attr2 = UltimateListItemAttr()
		self.attr2.SetBackgroundColour(even_color)
		self.indexes = []

		self.il = wx.ImageList(16, 16)
		for icon_id in images:
			bmp = wx.ArtProvider.GetBitmap(icon_id, wx.ART_OTHER, const.SIZE_16)
			self.indexes.append(self.il.Add(bmp))


		style = wx.LC_REPORT | wx.LC_VRULES | wx.LC_NO_HEADER
		style |= wx.LC_SINGLE_SEL
		style |= wx.LC_VIRTUAL
		style |= wx.LC_HRULES
		if self.tooltips: style |= ULC_SHOW_TOOLTIPS
		UltimateListCtrl.__init__(self, parent, agwStyle=style)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		for i in range(4):
			self.InsertColumn(i, '')
			self.SetColumnWidth(i, 25)

		self.InsertColumn(4, '')
		self.SetItemCount(len(self.data))
		self.SetColumnWidth(4, -1)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
		self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_down)

	def on_mouse_down(self, event):
		self.pos_x = event.GetX()
		event.Skip()

	def OnItemSelected(self, event):
		self.currentItem = event.m_itemIndex
		if not self.pos_x is None:
			print 'column', self.pos_x / 25

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


