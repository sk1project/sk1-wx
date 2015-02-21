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

from sk1.widgets import BOTTOM, EXPAND, ALL, VERTICAL, HORIZONTAL
from sk1.widgets import const, HPanel, VPanel

class GenericDialog(wx.Dialog):

	sizer = None
	box = None
	button_box = None
	ok_btn = None
	cancel_btn = None

	def __init__(self, parent, title, size=(-1, -1), style=HORIZONTAL):

		wx.Dialog.__init__(self, parent, -1, title, wx.DefaultPosition, size)

		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.sizer)

		margin = 5
		if not const.is_gtk(): margin = 10

		if style == HORIZONTAL:
			self.box = HPanel(self, border=BOTTOM, space=margin)
			self.sizer.Add(self.box, 0, ALL | EXPAND)
		else:
			self.box = VPanel(self, border=BOTTOM, space=margin)
			self.sizer.Add(self.box, 0, ALL | EXPAND)

		self.build()

		self.button_box = wx.BoxSizer(wx.HORIZONTAL)
		self.sizer.Add(self.button_box, 0, wx.ALL | wx.ALIGN_RIGHT, 5)

		self.ok_btn = wx.Button(self, wx.ID_OK, "", wx.DefaultPosition,
							wx.DefaultSize, 0)
		self.Bind(wx.EVT_BUTTON, self.on_ok, self.ok_btn)

		self.cancel_btn = wx.Button(self, wx.ID_CANCEL, "", wx.DefaultPosition,
								wx.DefaultSize, 0)
		self.Bind(wx.EVT_BUTTON, self.on_cancel, self.cancel_btn)
		if const.is_gtk():
			self.button_box.Add(self.cancel_btn, 0, wx.ALIGN_RIGHT)
			self.button_box.Add(self.ok_btn, 0, wx.ALIGN_RIGHT)
		elif const.is_msw():
			self.button_box.Add(self.ok_btn, 0, ALL | wx.ALIGN_RIGHT)
			self.button_box.Add(self.cancel_btn, 0, ALL | wx.ALIGN_RIGHT)
		else:
			self.button_box.Add(self.ok_btn, 0, ALL | wx.ALIGN_RIGHT, 5)
			self.button_box.Add(self.cancel_btn, 0, ALL | wx.ALIGN_RIGHT, 5)
		self.cancel_btn.SetDefault()
		self.sizer.Fit(self)

	def build(self):pass

	def on_ok(self, event):
		self.EndModal(wx.ID_OK)

	def on_cancel(self, event):
		self.EndModal(wx.ID_CANCEL)
