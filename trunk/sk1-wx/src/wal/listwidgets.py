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

ODD_COLOR = wx.Colour(240, 240, 240)

class SimpleList(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):

	data = []
	select_cmd = None
	activate_cmd = None

	def __init__(self, parent, data=[], border=True, header=False,
				single_sel=True, alt_color=False,
				on_select=None, on_activate=None):
		self.data = data
		style = wx.LC_REPORT
		if border: style |= wx.BORDER_MASK
		if not header: style |= wx.LC_NO_HEADER
		if single_sel: style |= wx.LC_SINGLE_SEL
		wx.ListCtrl.__init__(self, parent, wx.ID_ANY, style=style)
		listmix.ListCtrlAutoWidthMixin.__init__(self)
		self.set_columns()
		self.set_data(self.data, alt_color)
		if on_select:
			self.select_cmd = on_select
			self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self)
		if on_activate:
			self.activate_cmd = on_activate
			self.Bind(wx.wx.EVT_LIST_ITEM_ACTIVATED, self.on_activate, self)


	def set_columns(self):
		self.InsertColumn(0, '')

	def set_data(self, data, alt_color=True):
		odd = False
		i = 0
		for item in data:
			self.Append([item])
			if odd and alt_color:
				list_item = self.GetItem(i)
				list_item.SetBackgroundColour(ODD_COLOR)
				self.SetItem(list_item)
			odd = not odd
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


class ReportList(SimpleList):

	def __init__(self, parent, data=[], border=True, header=True,
				single_sel=True, alt_color=True,
				on_select=None, on_activate=None):
		SimpleList.__init__(self, parent, data, border, header,
						single_sel, alt_color, on_select, on_activate)

	def set_columns(self):
		for item in self.data[0]:
			index = self.data[0].index(item)
			self.InsertColumn(index, item)

	def set_data(self, data, alt_color=True):
		odd = False
		i = 0
		for item in data[1:]:
			self.Append(item)
			if odd and alt_color:
				list_item = self.GetItem(i)
				list_item.SetBackgroundColour(ODD_COLOR)
				self.SetItem(list_item)
			odd = not odd
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
