# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2013-2015 by Igor E. Novikov
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
from const import EXPAND, ALL, VERTICAL, HORIZONTAL, is_gtk
from basic import HPanel, VPanel
from widgets import HLine, Button

class SimpleDialog(wx.Dialog):

	_timer = None
	add_line = True

	def __init__(self, parent, title, size=(-1, -1), style=VERTICAL,
				resizable=False, on_load=None, add_line=True, margin=None):
		dlg_style = wx.DEFAULT_DIALOG_STYLE
		if resizable:dlg_style |= wx.RESIZE_BORDER
		self.add_line = add_line

		wx.Dialog.__init__(self, parent, -1, title, wx.DefaultPosition,
						size, style=dlg_style)

		sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(sizer)

		if margin is None:
			margin = 5
			if not const.is_gtk(): margin = 10

		self.box = VPanel(self)
		sizer.Add(self.box, 1, ALL | EXPAND, margin)

		if style == HORIZONTAL:
			self.panel = HPanel(self.box)
		else:
			self.panel = VPanel(self.box)
		self.box.pack(self.panel, expand=True, fill=True)

		self.build()
		self.set_dialog_buttons()
		if size == (-1, -1):self.Fit()
		self.CenterOnParent()
		self.panel.layout()
		self.Bind(wx.EVT_CLOSE, self.on_close, self)
		if on_load:
			self._timer = wx.Timer(self)
			self.Bind(wx.EVT_TIMER, on_load)
			self._timer.Start(500)

	def build(self):pass
	def set_dialog_buttons(self):pass
	def get_result(self): return None
	def on_close(self, event=None): self.end_modal(const.BUTTON_CANCEL)
	def set_title(self, title): self.SetTitle(title)
	def set_minsize(self, size): self.SetMinSize(size)
	def get_size(self):return self.GetSize()
	def set_size(self, size): self.SetSize(wx.Size(*size))
	def show_modal(self):return self.ShowModal()
	def end_modal(self, ret): self.EndModal(ret)
	def destroy(self): self.Destroy()

	def pack(self, *args, **kw):
		obj = args[0]
		if not obj.GetParent() == self.panel:
			obj.Reparent(self.panel)
		self.panel.pack(*args, **kw)

	def show(self):
		self.show_modal()
		self.destroy()

class CloseDialog(SimpleDialog):

	def __init__(self, parent, title, size=(-1, -1), style=VERTICAL,
				resizable=True, on_load=None, add_line=True):
		SimpleDialog.__init__(self, parent, title, size, style, resizable,
							on_load, add_line)

	def set_dialog_buttons(self):
		if self.add_line:
			self.box.pack(HLine(self.box), fill=True, padding=5)
		else:
			self.box.pack((3, 3))

		self.button_box = HPanel(self.box)
		self.box.pack(self.button_box, fill=True)

		self.close_btn = Button(self.button_box, '', onclick=self.on_close,
							default=True, pid=const.BUTTON_CLOSE)

		self.left_button_box = HPanel(self.button_box)
		self.button_box.pack(self.left_button_box, expand=True, fill=True)
		self.button_box.pack(self.close_btn, padding=5)

class OkCancelDialog(SimpleDialog):

	sizer = None
	box = None
	button_box = None
	ok_btn = None
	cancel_btn = None
	action_button = None

	def __init__(self, parent, title, size=(-1, -1), style=VERTICAL,
				resizable=False, action_button=const.BUTTON_OK, on_load=None,
							add_line=True):
		self.action_button = action_button
		SimpleDialog.__init__(self, parent, title, size, style,
							resizable, on_load, add_line)

	def set_dialog_buttons(self):
		if self.add_line:
			self.box.pack(HLine(self.box), fill=True, padding=5)
		else:
			self.box.pack((3, 3))

		self.button_box = HPanel(self.box)
		self.box.pack(self.button_box, fill=True)

		self.ok_btn = Button(self.button_box, '', onclick=self.on_ok,
							default=True, pid=self.action_button)
		self.cancel_btn = Button(self.button_box, '', onclick=self.on_cancel,
								pid=const.BUTTON_CANCEL)

		self.left_button_box = HPanel(self.button_box)
		self.button_box.pack(self.left_button_box, expand=True, fill=True)

		if const.is_mac():
			self.button_box.pack(self.ok_btn, padding=5)
			self.button_box.pack(self.cancel_btn, padding=5)
		elif const.is_msw():
			self.button_box.pack(self.ok_btn, padding=2)
			self.button_box.pack(self.cancel_btn)
		else:
			self.button_box.pack(self.cancel_btn, padding=2)
			self.button_box.pack(self.ok_btn)

	def on_ok(self):
		self.end_modal(const.BUTTON_OK)

	def on_cancel(self):
		self.end_modal(const.BUTTON_CANCEL)

	def show(self):
		ret = None
		if self.show_modal() == const.BUTTON_OK:
			ret = self.get_result()
		self.destroy()
		return ret
