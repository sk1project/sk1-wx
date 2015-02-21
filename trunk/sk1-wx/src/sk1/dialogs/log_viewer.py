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

import os
import wx

from wal import BOTTOM, EXPAND, ALL, VERTICAL, HORIZONTAL
from wal import const, HPanel, VPanel, Button, HLine

from sk1 import _, appconst
from msgdlgs import error_dialog

class LogViewerDialog(wx.Dialog):

	sizer = None
	box = None
	button_box = None
	ok_btn = None
	cancel_btn = None
	lc = None
	data = []
	ret = ''

	def __init__(self, parent, title, size=(500, 350)):

		self.app = parent.app

		wx.Dialog.__init__(self, parent, -1, title, wx.DefaultPosition, size)

		self.sizer = wx.BoxSizer(VERTICAL)
		self.SetSizer(self.sizer)

		self.box = VPanel(self)
		self.sizer.Add(self.box, 1, ALL | EXPAND)

		self.build()

		self.box.add(HLine(self.box), 0, ALL | EXPAND)

		self.bottom_box = HPanel(self)
		self.sizer.Add(self.bottom_box, 0, EXPAND, 5)

		self.clear_btn = Button(self.bottom_box, _('Clear history'),
							onclick=self.clear_history)
		self.bottom_box.add(self.clear_btn, 0, ALL , 5)

		expander = HPanel(self)
		self.bottom_box.add(expander, 1, ALL , 5)


		self.open_btn = wx.Button(self.bottom_box, wx.ID_OPEN, "",
								wx.DefaultPosition, wx.DefaultSize, 0)
		self.Bind(wx.EVT_BUTTON, self.on_open, self.open_btn)

		self.cancel_btn = wx.Button(self.bottom_box, wx.ID_CANCEL, "",
								wx.DefaultPosition, wx.DefaultSize, 0)
		self.Bind(wx.EVT_BUTTON, self.on_cancel, self.cancel_btn)

		if const.is_gtk():
			self.bottom_box.add(self.cancel_btn, 0, ALL, 5)
			self.bottom_box.add(self.open_btn, 0, ALL, 5)
		elif const.is_msw():
			self.bottom_box.add(self.open_btn, 0, ALL, 5)
			self.bottom_box.add(self.cancel_btn, 0, ALL, 5)
		else:
			self.bottom_box.add(self.open_btn, 0, ALL , 5)
			self.bottom_box.add(self.cancel_btn, 0, ALL , 5)

		self.cancel_btn.SetDefault()
		self.open_btn.Enable(False)
		self.update_list()

	def build(self):
		margin = 0
		if const.is_msw(): margin = 5
		self.lc = wx.ListCtrl(self.box, -1, style=wx.LC_REPORT)
		self.box.add(self.lc, 1, ALL | EXPAND, margin)
		self.lc.Bind(wx.EVT_LIST_ITEM_SELECTED, self.update, self.lc)
		self.lc.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.update, self.lc)
		self.lc.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_open, self.lc)

	def update(self, *args):
		item = self.lc.GetFocusedItem()
		if not item < 0:self.open_btn.Enable(True)
		else:self.open_btn.Enable(False)
		if self.data: self.clear_btn.Enable(True)
		else:self.clear_btn.Enable(False)

	def update_list(self):
		self.lc.ClearAll()
		self.lc.InsertColumn(0, _(' '))
		self.lc.InsertColumn(1, _('File name'))
		self.lc.InsertColumn(2, _('Path'))
		self.lc.InsertColumn(3, _('Time'))
		self.data = self.app.history.get_history_entries()

		ldata = []
		for item in self.data:
			op = 'O'
			if item[0] == appconst.SAVED:op = 'S'
			ldata.append([op, item[1], item[2], item[4]])

		odd_color = wx.Colour(240, 240, 240)
		i = 0
		odd = False
		for item in ldata:
			self.lc.Append(item)
			if odd:
				item = self.lc.GetItem(i)
				item.SetBackgroundColour(odd_color)
				self.lc.SetItem(item)
			odd = not odd
			i += 1

		self.lc.SetColumnWidth(0, 20)
		if self.data: self.lc.SetColumnWidth(1, wx.LIST_AUTOSIZE)
		else: self.lc.SetColumnWidth(1, 100)
		self.lc.SetColumnWidth(2, 200)
		self.lc.SetColumnWidth(3, 500)
		self.update()

	def clear_history(self, *args):
		self.app.history.clear_history()
		self.update_list()

	def on_open(self, *args):
		item = self.lc.GetFocusedItem()
		if not item < 0:
			path = self.data[item][3]
			if os.path.isfile(path):
				self.ret = path
				self.EndModal(wx.ID_OK)
			else:
				txt = "%s '%s' %s" % (_('File'), path, _('is not found.'))
				error_dialog(self, _('File not found'), txt)

	def on_cancel(self, event):
		self.EndModal(wx.ID_CANCEL)

	def get_result(self): return self.ret

def log_viewer_dlg(parent):
	ret = ''
	dlg = LogViewerDialog(parent, _("Recent documents"))
	dlg.Centre()
	if dlg.ShowModal() == wx.ID_OK: ret = dlg.get_result()
	dlg.Destroy()
	if ret:parent.app.open(ret)
