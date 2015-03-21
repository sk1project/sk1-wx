# -*- coding: utf-8 -*-
#
#	Copyright (C) 2013-2015 by Igor E. Novikov
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

import const
from const import BOTTOM, EXPAND, ALL, VERTICAL, HORIZONTAL
from basic import HPanel, VPanel
from widgets import HLine

class OkCancelDialog(wx.Dialog):

	sizer = None
	box = None
	button_box = None
	ok_btn = None
	cancel_btn = None

	def __init__(self, parent, title, size=(-1, -1), style=VERTICAL):

		wx.Dialog.__init__(self, parent, -1, title, wx.DefaultPosition, size)

		sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(sizer)

		margin = 5
		if not const.is_gtk(): margin = 10

		self.box = VPanel(self)
		sizer.Add(self.box, 0, ALL | EXPAND, margin)

		if style == HORIZONTAL:
			self.panel = HPanel(self.box)
		else:
			self.panel = VPanel(self.box)
		self.box.pack(self.panel, expand=True, fill=True)

		self.build()

		self.box.pack(HLine(self.box), fill=True, padding=5)

		self.button_box = HPanel(self.box)
		self.box.pack(self.button_box, fill=True)

		self.ok_btn = wx.Button(self.button_box, wx.ID_OK, '',
							wx.DefaultPosition, wx.DefaultSize, 0)
		self.Bind(wx.EVT_BUTTON, self.on_ok, self.ok_btn)

		self.cancel_btn = wx.Button(self.button_box, wx.ID_CANCEL, '',
								wx.DefaultPosition, wx.DefaultSize, 0)
		self.Bind(wx.EVT_BUTTON, self.on_cancel, self.cancel_btn)

		self.button_box.pack(HPanel(self.button_box), expand=True, fill=True)

		if const.is_gtk():
			self.button_box.pack(self.cancel_btn, padding=2)
			self.button_box.pack(self.ok_btn)
		elif const.is_msw():
			self.button_box.pack(self.ok_btn, padding=2)
			self.button_box.pack(self.cancel_btn)
		else:
			self.button_box.pack(self.ok_btn, padding=5)
			self.button_box.pack(self.cancel_btn, padding=5)

		self.cancel_btn.SetDefault()
		self.Fit()
		self.CenterOnParent()

	def pack(self, *args, **kw):
		obj = args[0]
		if not obj.GetParent() == self.panel:
			obj.Reparent(self.panel)
		self.panel.pack(*args, **kw)

	def build(self):pass

	def get_result(self): return None

	def on_ok(self, event):
		self.EndModal(wx.ID_OK)

	def on_cancel(self, event):
		self.EndModal(wx.ID_CANCEL)

	def show(self):
		ret = None
		if self.ShowModal() == wx.ID_OK:
			ret = self.get_result()
		self.destroy()
		return ret

	def destroy(self):
		self.Destroy()
