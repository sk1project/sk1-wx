# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2013 by Igor E. Novikov
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

from sk1 import _, appconst, events
from sk1.resources import icons, get_icon, pdids
from sk1.widgets import const


class AppStubPanel(wx.Panel):

	app = None
	bmp = None
	bmp_size = ()

	def __init__(self, parent):
		self.app = parent.app
		wx.Panel.__init__(self, parent)
		color = wx.Colour(*const.UI_COLORS['workspace'])
		self.SetBackgroundColour(color)
		self.bmp = get_icon(icons.CAIRO_BANNER, size=const.DEF_SIZE)
		self.bmp_size = self.bmp.GetSize()

		action = self.app.actions[wx.ID_NEW]
		tooltip = action.get_descr_text()
		self.new_btn = StubButton(self, icons.PD_STUB_NEW, action, tooltip)

		action = self.app.actions[wx.ID_OPEN]
		tooltip = action.get_descr_text()
		self.open_btn = StubButton(self, icons.PD_STUB_OPEN, action, tooltip)

		action = self.app.actions[pdids.ID_VIEW_LOG]
		tooltip = _('Open Recent')
		self.recent_btn = StubButton(self, icons.PD_STUB_RECENT, action, tooltip)
		self.recent_btn.set_active(self.app.history.is_history())

		self.Bind(wx.EVT_PAINT, self._on_paint, self)
		self.Bind(wx.EVT_SIZE, self._on_resize, self)
		events.connect(events.HISTORY_CHANGED, self.check_history)

	def check_history(self, *args):
		self.recent_btn.set_active(self.app.history.is_history())

	def hide(self):
		self.Hide()

	def show(self):
		self.Show()

	def refresh(self, x=0, y=0, w=0, h=0):
		if not w: w, h = self.GetSize()
		self.Refresh(rect=wx.Rect(x, y, w, h))

	def _on_resize(self, event):
		h = self.new_btn.GetSize()[1]
		w0 = self.new_btn.GetSize()[0]
		w = 3 * w0
		win_w, win_h = self.GetSize()
		x = (win_w - w) / 2
		y = (win_h - h) / 3
		self.new_btn.SetPosition((x, y))
		self.open_btn.SetPosition((x + w0, y))
		self.recent_btn.SetPosition((x + 2 * w0, y))
		self.refresh()

	def _on_paint(self, event):
		h = self.GetSize()[1]
		pdc = wx.PaintDC(self)
		dc = wx.GCDC(pdc)
		x = 10
		y = h - self.bmp_size[1] - 10
		dc.DrawBitmap(self.bmp, x, y, True)

class StubButton(wx.Panel):

	action = None
	icon = None
	state = appconst.NORMAL
	mouse_over = False
	mouse_pressed = False
	normal_bmp = None
	disabled_bmp = None
	active_bmp = None
	pressed_bmp = None

	def __init__(self, parent, icon, action, tooltip=''):
		self.action = action
		wx.Panel.__init__(self, parent)
		color = wx.Colour(*const.UI_COLORS['workspace'])
		self.SetBackgroundColour(color)
		self.icon = get_icon(icon, size=const.DEF_SIZE)
		self._set_bmp()
		self.SetSize(self.icon.GetSize())

		if tooltip: self.SetToolTipString(tooltip)

		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_PAINT, self._on_paint, self)
		self.Bind(wx.EVT_ENTER_WINDOW, self._mouse_over, self)
		self.Bind(wx.EVT_LEFT_DOWN, self._mouse_down, self)
		self.Bind(wx.EVT_LEFT_UP, self._mouse_up, self)
		self.Bind(wx.EVT_TIMER, self._on_timer)
		self.Bind(wx.EVT_LEAVE_WINDOW, self._on_win_leave, self)

	def _set_bmp(self):
		image = self.icon.ConvertToImage()
		image = image.AdjustChannels(1.0, 1.0, 1.0, .1)
		self.disabled_bmp = image.ConvertToBitmap()
		image.Replace(0, 0, 0, 255, 255, 255)
		image = image.AdjustChannels(1.0, 1.0, 1.0, 3.0)
		self.normal_bmp = image.ConvertToBitmap()
		image = self.icon.ConvertToImage()
		image.Replace(0, 0, 0, 255, 255, 255)
		image = image.AdjustChannels(1.0, 1.0, 1.0, .8)
		self.active_bmp = image.ConvertToBitmap()
		image = image.Blur(5)
		self.pressed_bmp = image.ConvertToBitmap()

	def set_active(self, val):
		if val: self.state = appconst.NORMAL
		else: self.state = appconst.DISABLED
		self.refresh()

	def refresh(self, x=0, y=0, w=0, h=0):
		if not w: w, h = self.GetSize()
		self.Refresh(rect=wx.Rect(x, y, w, h))

	def _on_paint(self, event):
		pdc = wx.PaintDC(self)
		dc = wx.GCDC(pdc)
		if self.state == appconst.NORMAL:
			dc.DrawBitmap(self.normal_bmp, 0, 0, True)
		elif self.state == appconst.ACTIVE:
			dc.DrawBitmap(self.active_bmp, 0, 0, True)
		elif self.state == appconst.PRESSED:
			dc.DrawBitmap(self.pressed_bmp, 0, 0, True)
		else:
			dc.DrawBitmap(self.disabled_bmp, 0, 0, True)

	def _mouse_over(self, event):
		if not self.state == appconst.DISABLED:
			self.mouse_over = True
			self.state = appconst.ACTIVE
			self.refresh()
			self.timer.Start(100)

	def _mouse_down(self, event):
		if not self.state == appconst.DISABLED:
			self.mouse_pressed = True
			self.state = appconst.PRESSED
			self.refresh()

	def _mouse_up(self, event):
		self.mouse_pressed = False
		if self.mouse_over:
			if self.action and not self.state == appconst.DISABLED:
				self.state = appconst.NORMAL
				self.refresh()
				self.action.do_call()

	def _on_timer(self, event):
		mouse_pos = wx.GetMousePosition()
		x, y = self.GetScreenPosition()
		w, h = self.GetSize()
		rect = wx.Rect(x, y, w, h)
		if not rect.Inside(mouse_pos):
			self.timer.Stop()
			if self.mouse_over:
				self.mouse_over = False
				self.mouse_pressed = False
				self.state = appconst.NORMAL
				self.refresh()

	def _on_win_leave(self, event):
		self.timer.Stop()
		if self.mouse_over:
			self.mouse_over = False
			self.mouse_pressed = False
			self.state = appconst.NORMAL
			self.refresh()
