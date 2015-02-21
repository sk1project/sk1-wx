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

from sk1.widgets import ALL, EXPAND, HORIZONTAL, VERTICAL, LEFT, TOP
from sk1.widgets import const, VPanel
from sk1.document.ruler import Ruler, RulerCorner
from sk1.document.canvas import AppCanvas
from sk1.document.viewer import DocViewer

class DocArea(VPanel):

	doc_tab = None

	def __init__(self, presenter, parent):
		self.presenter = presenter
		VPanel.__init__(self, parent)
		self.SetBackgroundColour(wx.Colour(255, 255, 255))

		#----- First row
		row_hbox = wx.BoxSizer(HORIZONTAL)
		self.corner = RulerCorner(presenter, self)
		row_hbox.Add(self.corner)
		self.hruler = Ruler(presenter, self, HORIZONTAL)
		row_hbox.Add(self.hruler, 1, EXPAND)
		self.box.Add(row_hbox, 0, EXPAND)

		#----- Second row
		row_hbox = wx.BoxSizer(HORIZONTAL)
		self.vruler = Ruler(presenter, self, VERTICAL)
		row_hbox.Add(self.vruler, 0, EXPAND)

		vbox = wx.BoxSizer(VERTICAL)
		hbox = wx.BoxSizer(HORIZONTAL)
		vbox.Add(hbox, 1, EXPAND)
		self.canvas = AppCanvas(presenter, self)
		hbox.Add(self.canvas, 1, EXPAND)
		self.vscroll = wx.ScrollBar(self, wx.ID_ANY, style=wx.SB_VERTICAL)
		hbox.Add(self.vscroll, 0, EXPAND)

		#----- Bottom row
		bottom_hbox = wx.BoxSizer(HORIZONTAL)
		bottom_vbox = wx.BoxSizer(VERTICAL)
		self.hscroll = wx.ScrollBar(self, wx.ID_ANY, style=wx.SB_HORIZONTAL)
		bottom_hbox.Add(self.hscroll, 1, EXPAND)
		self.bottom_corner = VPanel(self)

		size = self.vscroll.GetSize()[0]
		self.viewer = DocViewer(presenter, self, (size, size))
		self.bottom_corner.add(self.viewer)
		bottom_hbox.Add(self.bottom_corner)

		vbox.Add(bottom_hbox, 0, EXPAND)
		row_hbox.Add(vbox, 1, EXPAND)
		self.box.Add(row_hbox, 1, EXPAND)

		self.canvas._set_scrolls(self.hscroll, self.vscroll)

	def destroy(self):
		objs = [self.doc_tab, self.hruler,
			self.vruler, self.corner, self.canvas]
		for obj in objs: obj.destroy()

		items = self.__dict__.keys()
		for item in items:
			self.__dict__[item] = None

