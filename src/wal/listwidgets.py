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
import wx.lib.mixins.listctrl as listmix

import const
from generic import Widget

class SimpleList(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, Widget):

	data = []
	select_cmd = None
	activate_cmd = None
	alt_color = False

	def __init__(self, parent, data=[], border=True, header=False,
				single_sel=True, virtual=False, alt_color=False,
				even_color=const.EVEN_COLOR, odd_color=const.ODD_COLOR,
				on_select=None, on_activate=None):
		self.data = data
		self.alt_color = alt_color
		self.odd_color = odd_color
		self.even_color = even_color
		style = wx.LC_REPORT | wx.LC_VRULES
		if border and not const.is_wx3(): style |= wx.BORDER_MASK
		if not header: style |= wx.LC_NO_HEADER
		if single_sel: style |= wx.LC_SINGLE_SEL
		if virtual: style |= wx.LC_VIRTUAL
		wx.ListCtrl.__init__(self, parent, wx.ID_ANY, style=style)
		listmix.ListCtrlAutoWidthMixin.__init__(self)
		if self.data: self.update(self.data)
		if on_select:
			self.select_cmd = on_select
			self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self)
		if on_activate:
			self.activate_cmd = on_activate
			self.Bind(wx.wx.EVT_LIST_ITEM_ACTIVATED, self.on_activate, self)

	def set_active(self, index):
		if len(self.data) - 1 >= index:
			self.Select(index, True)

	def clear_all(self):
		self.ClearAll()

	def set_column_width(self, index, width):
		self.SetColumnWidth(index, width)

	def update(self, data):
		self.DeleteAllItems()
		self.data = data
		if not self.GetColumnCount():
			self.set_columns()
		self.set_data(self.data, self.alt_color)

	def set_columns(self):
		self.InsertColumn(0, '')

	def set_data(self, data, alt_color=True):
		even = False
		i = 0
		for item in data:
			self.Append([item])
			if alt_color:
				list_item = self.GetItem(i)
				if even: list_item.SetBackgroundColour(self.even_color)
				else:list_item.SetBackgroundColour(self.odd_color)
				self.SetItem(list_item)
				even = not even
				i += 1

	def on_select(self, *args):
		ret = None
		index = self.GetFocusedItem()
		if index >= 0:
			ret = self.data[index]
		self.select_cmd(ret)

	def on_activate(self, *args):
		index = self.GetFocusedItem()
		if not index < 0:
			self.activate_cmd(self.data[index])

	def get_selected(self):
		index = self.GetFocusedItem()
		if not index < 0:
			return self.data[index]
		return None

	def get_active(self):
		return self.GetFocusedItem()

class ReportList(SimpleList):

	def __init__(self, parent, data=[], border=True, header=True,
				single_sel=True, virtual=False, alt_color=True,
				even_color=const.EVEN_COLOR, odd_color=const.ODD_COLOR,
				on_select=None, on_activate=None):

		SimpleList.__init__(self, parent, data, border, header,
						single_sel, virtual, alt_color, even_color, odd_color,
						on_select, on_activate)

	def set_columns(self):
		for item in self.data[0]:
			index = self.data[0].index(item)
			self.InsertColumn(index, item)

	def set_data(self, data, alt_color=True):
		even = False
		i = 0
		for item in data[1:]:
			self.Append(item)
			if alt_color:
				list_item = self.GetItem(i)
				if even: list_item.SetBackgroundColour(self.even_color)
				else:list_item.SetBackgroundColour(self.odd_color)
				self.SetItem(list_item)
				even = not even
				i += 1

	def on_select(self, *args):
		ret = None
		index = self.GetFocusedItem()
		if index >= 0:
			ret = self.data[index + 1]
		self.select_cmd(ret)

	def on_activate(self, *args):
		index = self.GetFocusedItem()
		if not index < 0:
			self.activate_cmd(self.data[index + 1])

	def get_selected(self):
		index = self.GetFocusedItem()
		if not index < 0:
			return self.data[index + 1]
		return None

def VirtualList(SimpleList):

	def __init__(self, parent, data=[], border=True, header=True,
				single_sel=True, virtual=True, alt_color=True,
				even_color=const.EVEN_COLOR, odd_color=const.ODD_COLOR,
				on_select=None, on_activate=None):

		SimpleList.__init__(self, parent, data, border, header,
						single_sel, virtual, alt_color, even_color, odd_color,
						on_select, on_activate)

	def OnGetItemText(self, item, col):
		return self.get_item_text(item, col)

	def get_item_text(self, item, col):
		"""
		Callback method. Should return item text for specified column. 
		"""
		return ''

	def OnGetItemImage(self, item):
		return self.get_item_image(item)

	def get_item_image(self, item):
		"""
		Callback method. Should return item icon index or -1.
		"""
		return -1
