# -*- coding: utf-8 -*-
#
#	Copyright (C) 2016 by Igor E. Novikov
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


class Kbd_Processor:

	canvas = None

	def __init__(self, canvas):
		self.canvas = canvas
		self.canvas.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

	def on_key_down(self, event):
		key_code = event.GetKeyCode()
		raw_code = event.GetRawKeyCode()
		modifiers = event.GetModifiers()

		if key_code == wx.WXK_ESCAPE:
			self.canvas.dlg.on_close()
			return

		if key_code in (wx.WXK_PAGEDOWN, wx.WXK_NUMPAD_PAGEDOWN):
			self.canvas.next_page()
			return

		if key_code in (wx.WXK_PAGEUP, wx.WXK_NUMPAD_PAGEUP):
			self.canvas.previous_page()
			return

		event.Skip()
