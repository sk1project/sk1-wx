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

from wal import const, Label
from wal.generic import Widget

from sk1.resources import icons


def render_tb_icon(surface_bmp, bmp, x=0, y=0, disabled=False):
	w, h = surface_bmp.GetSize()
	surface_bmp = surface_bmp.GetSubBitmap(wx.Rect(0, 0, w, h))
	bmp_w, bmp_h = bmp.GetSize()
	x = (w - bmp_w) / 2 + x
	y = (h - bmp_h) / 2 + y

	if disabled:
		bg_bmp = bmp.ConvertToImage()
		bg_bmp = bg_bmp.AdjustChannels(1.0, 1.0, 1.0, .25)
		bg_bmp = bg_bmp.ConvertToBitmap()
	else:
		bg_bmp = bmp

	dark_shadow = bmp.ConvertToImage()
	light_shadow = dark_shadow.Copy()
	light_shadow.Replace(0, 0, 0, 255, 255, 255)
	dark_shadow = dark_shadow.AdjustChannels(1.0, 1.0, 1.0, .25)
	light_shadow = light_shadow.AdjustChannels(1.0, 1.0, 1.0, .5)
	dark_shadow = dark_shadow.ConvertToBitmap()
	light_shadow = light_shadow.ConvertToBitmap()

	dc = wx.MemoryDC()
	dc.SelectObject(surface_bmp)
	dc.DrawBitmap(bg_bmp, x, y, True)
	dc.DrawBitmap(light_shadow, x, y + 1, True)
	dc.DrawBitmap(dark_shadow, x, y, True)
	dc.SelectObject(wx.NullBitmap)
	return surface_bmp

def composite_bmp(size, bmps):
	w, h = size
	ret = wx.EmptyBitmapRGBA(w, h, 0, 255, 0, 255)
	position = 0
	dc = wx.MemoryDC()
	dc.SelectObject(ret)
	for bmp in bmps:
		w = bmp.GetSize()[0]
		dc.DrawBitmap(bmp, position, 0, True)
		position += w
	dc.SelectObject(wx.NullBitmap)
	image = ret.ConvertToImage()
	image.SetMaskColour(0, 255, 0)
	return image.ConvertToBitmap()


class MacTB_ActionButton(wx.StaticBitmap, Widget):

	action = None
	pressed = False

	def __init__(self, parent, action):
		self.action = action
		bg_normal = wx.ArtProvider.GetBitmap(icons.MAC_TBB_NORMAL,
										wx.ART_OTHER, const.DEF_SIZE)
		bg_pressed = wx.ArtProvider.GetBitmap(icons.MAC_TBB_PRESSED,
								wx.ART_OTHER, const.DEF_SIZE)

		if const.is_gtk(): icon = self.action.get_icon(const.DEF_SIZE)
		else: icon = self.action.get_icon()
		self.bg_normal = render_tb_icon(bg_normal, icon)
		self.bg_disabled = render_tb_icon(bg_normal, icon, disabled=True)
		self.bg_pressed = render_tb_icon(bg_pressed, icon)

		wx.StaticBitmap.__init__(self, parent, wx.ID_ANY, self.bg_normal)
		self.tooltip_win = MacTB_ToolTip(self)
		self.set_tooltip(self.action.get_descr_text())
		self.action.register(self)

		self.Bind(wx.EVT_LEFT_DOWN, self._mouse_down, self)
		self.Bind(wx.EVT_LEFT_UP, self._mouse_up, self)
		self.Bind(wx.EVT_LEAVE_WINDOW, self._mouse_leave, self)
		self.Bind(wx.EVT_MOTION, self._mouse_move, self)

	def update(self):
		if not self.action.enabled == self.enabled:
			self.set_enable(self.action.enabled)
			return
		if self.enabled:
			if self.pressed:
				self.SetBitmap(self.bg_pressed)
			else:
				self.SetBitmap(self.bg_normal)
		else:
			self.SetBitmap(self.bg_disabled)

	def set_tooltip(self, txt):
		self.tooltip_win.set_text(txt)

	def set_enable(self, value):
		self.enabled = value
		self.update()

	def _mouse_down(self, event):
		self.pressed = True
		self.update()

	def _mouse_up(self, event):
		if self.pressed:
			self.pressed = False
			self.update()
			self.action.do_call()

	def _mouse_leave(self, event):
		self.tooltip_win.hide()
		if self.pressed:
			self.pressed = False
			self.update()

	def _mouse_move(self, event):
		if not self.tooltip_win.IsShown():
			self.tooltip_win.show()

NB_WIDTH = 26
NB_HEIGHT = 23
NB_SPACER = 1

class MacTB_ActionNestedButtons(wx.StaticBitmap, Widget):

	actions = ()
	tip = ''
	pressed = False
	pressed_index = 0
	width = 0
	height = NB_HEIGHT
	normal_bg = None
	pressed_bg = []
	normal_skins = []
	pressed_skins = []
	disabled_skins = []
	spacer_normal = None
	spacer_active = None

	def __init__(self, parent, actions):
		self.actions = actions
		self.width = len(actions) * NB_WIDTH + NB_SPACER * (len(actions) - 1)
		self.generate_skins()
		self.normal_bg = self.generate_normal_bg()
		self.pressed_bg = self.generate_pressed_bg()
		wx.StaticBitmap.__init__(self, parent, wx.ID_ANY, self.normal_bg)
		for action in self.actions: action.register(self)
		self.tip = self.actions[0].get_descr_text()
		self.tooltip_win = MacTB_ToolTip(self)
		self.set_tooltip(self.tip)

		self.Bind(wx.EVT_LEFT_DOWN, self._mouse_down, self)
		self.Bind(wx.EVT_LEFT_UP, self._mouse_up, self)
		self.Bind(wx.EVT_LEAVE_WINDOW, self._mouse_leave, self)
		self.Bind(wx.EVT_MOTION, self._mouse_move, self)

	def generate_skins(self):
		args = (wx.ART_OTHER, const.DEF_SIZE)
		get_bmp = wx.ArtProvider.GetBitmap
		left_normal = get_bmp(icons.MAC_TBNB_LEFT_NORMAL, *args)
		left_pressed = get_bmp(icons.MAC_TBNB_LEFT_PRESSED, *args)
		middle_normal = get_bmp(icons.MAC_TBNB_MIDDLE_NORMAL, *args)
		middle_pressed = get_bmp(icons.MAC_TBNB_MIDDLE_PRESSED, *args)
		right_normal = get_bmp(icons.MAC_TBNB_RIGHT_NORMAL, *args)
		right_pressed = get_bmp(icons.MAC_TBNB_RIGHT_PRESSED, *args)
		self.spacer_normal = get_bmp(icons.MAC_TBNB_SPACER_NORMAL, *args)
		self.spacer_active = get_bmp(icons.MAC_TBNB_SPACER_ACTIVE, *args)
		self.normal_skins = []
		self.pressed_skins = []
		self.disabled_skins = []
		index = 0
		last = len(self.actions) - 1
		for action in self.actions:
			if const.is_gtk(): icon = action.get_icon(const.DEF_SIZE)
			else: icon = action.get_icon()
			if not index: bg = left_normal; pbg = left_pressed
			elif index == last: bg = right_normal; pbg = right_pressed
			else: bg = middle_normal; pbg = middle_pressed
			self.normal_skins.append(render_tb_icon(bg, icon))
			self.pressed_skins.append(render_tb_icon(pbg, icon))
			self.disabled_skins.append(render_tb_icon(bg, icon, disabled=True))
			index += 1

	def generate_normal_bg(self):
		bmps = []
		index = 0
		last = len(self.actions) - 1
		for action in self.actions:
			if action.enabled: bmps.append(self.normal_skins[index])
			else: bmps.append(self.disabled_skins[index])
			if not index == last:
				bmps.append(self.spacer_normal)
			index += 1
		return composite_bmp((self.width, self.height), bmps)

	def generate_pressed_bg(self):
		ret = []
		last = len(self.actions) - 1
		for item in self.actions:
			bmps = []
			index = 0
			for action in self.actions:
				if action.enabled:
					if action == item:
						if index:bmps[-1] = self.spacer_active
						bmps.append(self.pressed_skins[index])
					else:
						bmps.append(self.normal_skins[index])
				else: bmps.append(self.disabled_skins[index])
				if not index == last:
					if action == item and action.enabled:
						bmps.append(self.spacer_active)
					else:
						bmps.append(self.spacer_normal)
				index += 1
			ret.append(composite_bmp((self.width, self.height), bmps))
		return ret

	def set_enable(self, *args):
		self.update()

	def update(self):
		self.normal_bg = self.generate_normal_bg()
		self.pressed_bg = self.generate_pressed_bg()
		self.SetBitmap(self.normal_bg)

	def get_index(self, event):
		return int(event.GetPosition()[0] / (NB_WIDTH + NB_SPACER))

	def _mouse_down(self, event):
		self.pressed = True
		self.SetBitmap(self.pressed_bg[self.get_index(event)])

	def _mouse_up(self, event):
		if self.pressed:
			self.pressed = False
			self.SetBitmap(self.normal_bg)
			index = self.get_index(event)
			if self.actions[index].enabled:
				self.actions[index].do_call()

	def _mouse_leave(self, event):
		self.tooltip_win.hide()
		if self.pressed:
			self.pressed = False
			self.SetBitmap(self.normal_bg)

	def _mouse_move(self, event):
		index = self.get_index(event)
		if not self.tip == self.actions[index].get_descr_text():
			self.tooltip_win.hide()
			self.tip = self.actions[index].get_descr_text()
			self.set_tooltip(self.tip)
		self.tooltip_win.show()

	def set_tooltip(self, txt):
		self.tooltip_win.set_text(txt)

class MacTB_ToolTip(wx.PopupWindow):

	def __init__(self, parent):
		self.parent = parent
		wx.PopupWindow.__init__(self, parent, wx.BORDER_NONE)
		bg = const.UI_COLORS['disabled_text']
		self.SetBackgroundColour(wx.Colour(*bg))
		self.label = Label(self, ' ', fontsize=-2)
		self.label.SetPosition((1, 1))
		self.set_text(' ')
		wx.CallAfter(self.Refresh)
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self._on_timer)
		self.Bind(wx.EVT_PAINT, self._on_paint, self)

	def set_text(self, tip=''):
		name = tip
		if not name:name = '---'
		self.label.set_text(name)
		sz = self.label.GetBestSize()
		self.SetSize((sz.width + 3, sz.height + 3))
		self.set_position()

	def hide(self):
		if self.timer.IsRunning(): self.timer.Stop()
		if self.IsShown(): self.Hide()

	def show(self):
		if not self.timer.IsRunning():
			self.timer.Start(1000)
		else:
			self.timer.Stop()
			self.timer.Start(1000)

	def _on_timer(self, event):
		self.set_position()
		self.Show()
		self.timer.Stop()

	def set_position(self):
		x, y = wx.GetMousePosition()
		w, h = self.GetSize()
		scr_w, scr_h = wx.DisplaySize()
		if x + w + 7 > scr_w: x = x - w - 5
		else: x += 7
		if y + h + 17 > scr_h: y = y - h - 5
		else:y += 17
		self.SetPosition((x, y))

	def _on_paint(self, event):
		w, h = self.GetSize()
		pdc = wx.PaintDC(self)
		pdc.BeginDrawing()

		pdc.SetPen(wx.TRANSPARENT_PEN)
		pdc.SetBrush(wx.Brush(wx.Colour(*const.UI_COLORS['tooltip_bg'])))
		pdc.DrawRectangle(0, 0, w - 1, h - 1)

		pdc.EndDrawing()
		pdc = None

