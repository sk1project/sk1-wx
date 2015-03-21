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

import copy
import wx

from uc2.cms import verbose_color

from wal import HPanel, VPanel, Label
from sk1 import config, events

class HPalette(HPanel):

	cms = None
	palette = None
	colors = []
	position = 0
	max_pos = 0
	screen_num = 10
	cell_width = 40.0
	cell_height = 18.0

	onleftclick = None
	onrightclick = None
	onmin = None
	onmax = None

	tooltipwin = None
	mouse_pos = ()
	mouse_screen_pos = ()
	last_mouse_pos = ()
	tip = ''
	timer = None

	def __init__(self, parent, app, cms,
				onleftclick=None, onrightclick=None, onmin=None, onmax=None):
		self.app = app
		self.cms = cms
		self.onleftclick = onleftclick
		self.onrightclick = onrightclick
		self.onmin = onmin
		self.onmax = onmax
		HPanel.__init__(self, parent)
		self.set_palette(app.palettes.palette_in_use.model.colors)
		self.cell_width = config.palette_hcell_horizontal
		self.cell_height = config.palette_hcell_vertical
		self.pack((self.cell_width, self.cell_height))
		self.tooltipwin = PaletteToolTip(self)
		self.Bind(wx.EVT_PAINT, self._on_paint, self)
		self.Bind(wx.EVT_SIZE, self._on_resize, self)
		self.Bind(wx.EVT_MOUSEWHEEL, self._on_scroll, self)
		self.Bind(wx.EVT_MOTION, self._on_move, self)
		if onrightclick:
			self.Bind(wx.EVT_RIGHT_UP, self._on_right_click, self)
		if onleftclick:
			self.Bind(wx.EVT_LEFT_UP, self._on_left_click, self)
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self._on_timer)
		self.SetDoubleBuffered(True)
		events.connect(events.CONFIG_MODIFIED, self.config_update)

	def config_update(self, attr, value):
		if not attr[:7] == 'palette':return
		self.cell_width = config.palette_hcell_horizontal
		self.cell_height = config.palette_hcell_vertical
		self.refresh()

	def refresh(self, x=0, y=0, w=0, h=0):
		if not w: w, h = self.GetSize()
		self.Refresh(rect=wx.Rect(x, y, w, h))

	def set_adjustment(self):
		w = self.GetSize()[0]
		if w:
			self.screen_num = int(w / self.cell_width)
			self.max_pos = len(self.colors) * self.cell_width / w - 1.0
			self.max_pos *= w / self.cell_width
			self.max_pos += 1.0 / self.cell_width

	def set_cms(self, cms):
		self.cms = cms
		self.update_colors()

	def set_palette(self, palette):
		self.palette = palette
		self.update_colors()

	def set_position(self, position):
		self.position = position
		self.change_position(0)

	def scroll_left(self):self.change_position(-1)
	def scroll_right(self):self.change_position(1)
	def dscroll_left(self):self.change_position(-self.screen_num)
	def dscroll_right(self):self.change_position(self.screen_num)

	def change_position(self, incr):
		val = self.position + incr
		if val < 0:val = 0
		if val > self.max_pos:val = self.max_pos
		if not self.position == val:
				self.position = val
				self.refresh()
		if not self.position and self.onmin: self.onmin(False)
		if self.position and self.onmin: self.onmin(True)
		if self.position == self.max_pos and self.onmax: self.onmax(False)
		if not self.position == self.max_pos and self.onmax: self.onmax(True)

	def update_colors(self):
		self.colors = []
		for color in self.palette:
			r, g, b = self.cms.get_display_color(color)
			clr = (int(r * 255), int(g * 255), int(b * 255))
			self.colors.append(clr)

	def get_color_on_x(self, x):
		index = int((self.position * self.cell_width + x) / self.cell_width)
		return copy.deepcopy(self.palette[index])

	def set_tip(self, tip=()):
		if tip:
			self.tooltipwin.set_text(tip)
			self.tooltipwin.Show(True)
			self.tooltipwin.set_position(self.mouse_screen_pos)
		elif self.tooltipwin:
			self.tooltipwin.Hide()

	def _on_timer(self, event):
		mouse_pos = wx.GetMousePosition()
		x, y = self.GetScreenPosition()
		w, h = self.GetSize()
		rect = wx.Rect(x, y, w, h)
		if not rect.Inside(mouse_pos):
			self.timer.Stop()
			self.set_tip()
		else:
			if self.mouse_screen_pos == self.last_mouse_pos:
				if not self.tip:
					color = self.get_color_on_x(self.mouse_pos[0])
					color_name = ''
					color_txt = verbose_color(color)
					if not color[0] == 'SPOT' and color[3]:
						color_name = '' + color[3]
					self.tip = (color_name, color_txt)
					self.set_tip(self.tip)
			else:
				self.last_mouse_pos = self.mouse_screen_pos
				self.tip = ''
				self.set_tip()

	def _on_left_click(self, event):
		self.onleftclick(self.get_color_on_x(event.GetPosition()[0]))

	def _on_right_click(self, event):
		self.onrightclick(self.get_color_on_x(event.GetPosition()[0]))

	def _on_move(self, event):
		self.mouse_pos = event.GetPosition()
		self.mouse_screen_pos = event.GetEventObject().ClientToScreen(self.mouse_pos)
		self.SetFocus()
		self.set_tip()
		if not self.timer.IsRunning():
			self.timer.Start(500)

	def _on_resize(self, event):
		self.set_adjustment()
		self.refresh()

	def _on_scroll(self, event):
		self.set_tip()
		if event.GetWheelRotation() > 0:
			self.dscroll_right()
		else:
			self.dscroll_left()

	def _on_paint(self, event):
		if not self.palette:return
		width = self.GetSize()[0]
		pdc = wx.PaintDC(self)
		try:
			dc = wx.GCDC(self.pdc)
		except:dc = pdc
		dc.BeginDrawing()
		pdc.BeginDrawing()

		w = self.cell_width
		h = self.cell_height
		x = -1 * self.position * w
		for color in self.colors:
			if x > -w and x < width:
				pdc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 1))
				pdc.SetBrush(wx.Brush(wx.Colour(*color)))
				pdc.DrawRectangle(x, 0, w + 1, h)
			x += w

		if not pdc == dc:
			dc.EndDrawing()
			pdc.EndDrawing()
		else:
			dc.EndDrawing()
		pdc = dc = None

class VPalette(VPanel):

	cms = None
	palette = None
	colors = []
	position = 0
	max_pos = 0
	screen_num = 10
	cell_width = 18.0
	cell_height = 18.0

	onleftclick = None
	onrightclick = None
	onmin = None
	onmax = None

	tooltipwin = None
	mouse_pos = ()
	mouse_screen_pos = ()
	last_mouse_pos = ()
	tip = ''
	timer = None

	def __init__(self, parent, app, cms,
				onleftclick=None, onrightclick=None, onmin=None, onmax=None):
		self.app = app
		self.cms = cms
		self.onleftclick = onleftclick
		self.onrightclick = onrightclick
		self.onmin = onmin
		self.onmax = onmax
		VPanel.__init__(self, parent)
		self.set_palette(app.palettes.palette_in_use.model.colors)
		self.cell_width = config.palette_vcell_horizontal
		self.cell_height = config.palette_vcell_vertical
		self.pack((self.cell_width, self.cell_height))
		self.tooltipwin = PaletteToolTip(self)
		self.Bind(wx.EVT_PAINT, self._on_paint, self)
		self.Bind(wx.EVT_SIZE, self._on_resize, self)
		self.Bind(wx.EVT_MOUSEWHEEL, self._on_scroll, self)
		self.Bind(wx.EVT_MOTION, self._on_move, self)
		if onrightclick:
			self.Bind(wx.EVT_RIGHT_UP, self._on_right_click, self)
		if onleftclick:
			self.Bind(wx.EVT_LEFT_UP, self._on_left_click, self)
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self._on_timer)
		self.SetDoubleBuffered(True)
		events.connect(events.CONFIG_MODIFIED, self.config_update)

	def config_update(self, attr, value):
		if not attr[:7] == 'palette':return
		self.cell_width = config.palette_vcell_horizontal
		self.cell_height = config.palette_vcell_vertical
		self.refresh()

	def refresh(self, x=0, y=0, w=0, h=0):
		if not w: w, h = self.GetSize()
		self.Refresh(rect=wx.Rect(x, y, w, h))

	def set_adjustment(self):
		h = self.GetSize()[1]
		if h:
			self.screen_num = int(h / self.cell_height)
			self.max_pos = len(self.colors) * self.cell_height / h - 1.0
			self.max_pos *= h / self.cell_height
			self.max_pos += 1.0 / self.cell_height

	def set_cms(self, cms):
		self.cms = cms
		self.update_colors()

	def set_palette(self, palette):
		self.palette = palette
		self.update_colors()

	def set_position(self, position):
		self.position = position
		self.change_position(0)

	def scroll_top(self):self.change_position(-1)
	def scroll_bottom(self):self.change_position(1)
	def dscroll_top(self):self.change_position(-self.screen_num)
	def dscroll_bottom(self):self.change_position(self.screen_num)

	def change_position(self, incr):
		val = self.position + incr
		if val < 0:val = 0
		if val > self.max_pos:val = self.max_pos
		if not self.position == val:
				self.position = val
				self.refresh()
		if not self.position and self.onmin: self.onmin(False)
		if self.position and self.onmin: self.onmin(True)
		if self.position == self.max_pos and self.onmax: self.onmax(False)
		if not self.position == self.max_pos and self.onmax: self.onmax(True)

	def update_colors(self):
		self.colors = []
		for color in self.palette:
			r, g, b = self.cms.get_display_color(color)
			clr = (int(r * 255), int(g * 255), int(b * 255))
			self.colors.append(clr)

	def get_color_on_y(self, y):
		index = int((self.position * self.cell_height + y) / self.cell_height)
		return copy.deepcopy(self.palette[index])

	def set_tip(self, tip=()):
		if tip:
			self.tooltipwin.set_text(tip)
			self.tooltipwin.Show(True)
			self.tooltipwin.set_position(self.mouse_screen_pos)
		elif self.tooltipwin:
			self.tooltipwin.Hide()

	def _on_timer(self, event):
		mouse_pos = wx.GetMousePosition()
		x, y = self.GetScreenPosition()
		w, h = self.GetSize()
		rect = wx.Rect(x, y, w, h)
		if not rect.Inside(mouse_pos):
			self.timer.Stop()
			self.set_tip()
		else:
			if self.mouse_screen_pos == self.last_mouse_pos:
				if not self.tip:
					color = self.get_color_on_y(self.mouse_pos[1])
					color_name = ''
					color_txt = verbose_color(color)
					if not color[0] == 'SPOT' and color[3]:
						color_name = '' + color[3]
					self.tip = (color_name, color_txt)
					self.set_tip(self.tip)
			else:
				self.last_mouse_pos = self.mouse_screen_pos
				self.tip = ''
				self.set_tip()

	def _on_left_click(self, event):
		self.onleftclick(self.get_color_on_y(event.GetPosition()[1]))

	def _on_right_click(self, event):
		self.onrightclick(self.get_color_on_y(event.GetPosition()[1]))

	def _on_move(self, event):
		self.mouse_pos = event.GetPosition()
		self.mouse_screen_pos = event.GetEventObject().ClientToScreen(self.mouse_pos)
		self.SetFocus()
		self.set_tip()
		if not self.timer.IsRunning():
			self.timer.Start(500)

	def _on_resize(self, event):
		self.set_adjustment()
		self.refresh()

	def _on_scroll(self, event):
		self.set_tip()
		if event.GetWheelRotation() > 0:
			self.dscroll_top()
		else:
			self.dscroll_bottom()

	def _on_paint(self, event):
		if not self.palette:return
		height = self.GetSize()[1]
		pdc = wx.PaintDC(self)
		try:
			dc = wx.GCDC(self.pdc)
		except:dc = pdc
		dc.BeginDrawing()
		pdc.BeginDrawing()

		w = self.cell_width
		h = self.cell_height
		y = -1 * self.position * h
		for color in self.colors:
			if y > -h and y < height:
				pdc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 1))
				pdc.SetBrush(wx.Brush(wx.Colour(*color)))
				pdc.DrawRectangle(0, y, w, h + 1)
			y += h

		if not pdc == dc:
			dc.EndDrawing()
			pdc.EndDrawing()
		else:
			dc.EndDrawing()
		pdc = dc = None

class PaletteToolTip(wx.PopupWindow):

	def __init__(self, parent):
		wx.PopupWindow.__init__(self, parent, wx.BORDER_NONE)
		self.SetBackgroundColour("#FFFFFF")
		self.label = Label(self, ' ', fontbold=True)
		self.label.SetPosition((5, 3))
		label_h = self.label.GetBestSize().height
		self.color_vals = Label(self, '')
		self.color_vals.SetPosition((5, 4 + label_h))
		self.set_text((' ', ' '))
		wx.CallAfter(self.Refresh)
		self.Bind(wx.EVT_PAINT, self._on_paint, self)

	def set_text(self, tip=()):
		name = tip[0]
		if not name:name = '---'
		self.label.set_text(name)
		sz = self.label.GetBestSize()

		clr_vals = tip[1]
		self.color_vals.set_text(clr_vals)
		sz2 = self.color_vals.GetBestSize()

		if not clr_vals:
			self.SetSize((sz.width + 8, sz.height + 6))
		else:
			height = sz.height + sz2.height + 1
			width = max(sz.width, sz2.width)
			self.SetSize((width + 8, height + 6))

	def set_position(self, pos):
		x, y = pos
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

		pdc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 1))
		pdc.SetBrush(wx.TRANSPARENT_BRUSH)
		pdc.DrawRectangle(0, 0, w, h)

		pdc.EndDrawing()
		pdc = None


