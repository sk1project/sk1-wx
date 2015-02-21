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

from sk1 import config
from sk1.resources import icons
from sk1.widgets import const, ALL, EXPAND, VPanel

TAB_WIDTH = 25
TAB_MARGIN = 1
TAB_PADDING = 5
SCROLL_PADDING = 2
PANEL_MARGIN = 3
PANEL_WIDTH = 27

class PlgTabsPanel(VPanel):

	app = None
	active_plg = None
	plugins = []
	container = None
	tabs = None

	def __init__(self, app, parent):
		self.app = app
		VPanel.__init__(self, parent)

		self.tabs_bg = TabsBgPanel(self)
		self.add(self.tabs_bg, 1, ALL | EXPAND)

		self.plg_tabs = PlgTabs(self.tabs_bg, self.update_panel)
		self.tabs_bg.add(self.plg_tabs, 0, ALL | EXPAND)
		self.plg_tabs.SetPosition((0, 0))

	def update_panel(self, *args):pass

class TabsBgPanel(VPanel):

	def __init__(self, parent):
		VPanel.__init__(self, parent)
		self.Bind(wx.EVT_PAINT, self._on_paint, self)

	def _on_paint(self, event):
		w, h = self.panel.GetSize()
		pdc = wx.PaintDC(self.panel)
		try:
			dc = wx.GCDC(pdc)
		except:dc = pdc
		dc.BeginDrawing()

		color1 = wx.Colour(0, 0, 0, 20)
		color2 = wx.Colour(0, 0, 0, 0)
		rect = wx.Rect(0, 0, w / 2, h)
		dc.GradientFillLinear(rect, color1, color2, nDirection=wx.EAST)

		pdc.SetPen(wx.Pen(wx.Colour(*const.UI_COLORS['hover_solid_border']), 1))
		pdc.DrawLine(0, 0, 0, h)

		if not pdc == dc:
			dc.EndDrawing()
			pdc.EndDrawing()
		else:
			dc.EndDrawing()
		pdc = dc = None

class PlgTabs(VPanel):

	plg_tabs = []
	callback = None

	def __init__(self, parent, callback=None):
		VPanel.__init__(self, parent)
		self.callback = callback
		self.plg_tabs = []
		self.add((PANEL_WIDTH, PANEL_MARGIN))
		self.Bind(wx.EVT_PAINT, self._on_paint, self)

	def refresh(self, x=0, y=0, w=0, h=0):
		if not w: w, h = self.GetSize()
		self.Refresh(rect=wx.Rect(x, y, w, h))

	def update(self):
		self.Layout()
		self.SetSize(self.GetBestSize())
		if not self.callback is None: self.callback()

	def add_new_tab(self, plg):
		plg_tab = PlgTab(self.panel, plg)
		self.plg_tabs.append(plg_tab)
		self.add(plg_tab, 0, ALL | EXPAND)
		self.add((TAB_MARGIN, TAB_MARGIN))
		plg.plg_tab = plg_tab
		self.set_active(plg)

	def remove_tab(self, plg):
		plg_tab = plg.plg_tab
		self.box.Detach(plg_tab)
		self.plg_tabs.remove(plg_tab)
		plg_tab.Hide()
		self.update()

	def set_active(self, plg):
		plg_tab = plg.plg_tab
		for tab in self.plg_tabs:
			if tab.active: tab.set_active(False)
		plg_tab.set_active(True)
		self.update()

	def _on_paint(self, event):
		w, h = self.panel.GetSize()
		pdc = wx.PaintDC(self.panel)
		try:
			dc = wx.GCDC(pdc)
		except:dc = pdc
		dc.BeginDrawing()

		color1 = wx.Colour(0, 0, 0, 20)
		color2 = wx.Colour(0, 0, 0, 0)
		rect = wx.Rect(0, 0, w / 2, h)
		dc.GradientFillLinear(rect, color1, color2, nDirection=wx.EAST)

		pdc.SetPen(wx.Pen(wx.Colour(*const.UI_COLORS['hover_solid_border']), 1))
		pdc.DrawLine(0, 0, 0, h)

		if not pdc == dc:
			dc.EndDrawing()
			pdc.EndDrawing()
		else:
			dc.EndDrawing()
		pdc = dc = None

class PlgTab(VPanel):

	plg = None
	parent = None

	active = True
	text = ''
	rect = None
	but_rect = None
	but_active = False
	but_pressed = False

	def __init__(self, parent, plg, active=True):
		self.plg = plg
		self.parent = parent
		self.active = active
		self.text = self.plg.name
		self.icon = self.plg.icon
		if not self.icon:
			self.icon = wx.ArtProvider.GetBitmap(icons.PLUGIN_ICON)
		self.close_but = wx.ArtProvider.GetBitmap(icons.PD_CLOSE_BUTTON_ACTIVE)
		self.inactive_close_but = wx.ArtProvider.GetBitmap(icons.PD_CLOSE_BUTTON)
		VPanel.__init__(self, parent)
		self.add((TAB_WIDTH, self.get_best_height()))
		self.Bind(wx.EVT_PAINT, self._on_paint, self)
		self.Bind(wx.EVT_MOTION, self._on_move, self)
		self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down, self)
		self.Bind(wx.EVT_LEFT_UP, self._on_left_up, self)
		self.Bind(wx.EVT_LEAVE_WINDOW, self._on_win_leave, self)

	def set_title(self, title):
		self.text = title
		self.remove(0)
		self.add((TAB_WIDTH, self.get_best_height()))
		self.refresh()
		self.parent.update()

	def refresh(self, x=0, y=0, w=0, h=0):
		if not w: w, h = self.GetSize()
		self.Refresh(rect=wx.Rect(x, y, w, h))

	def set_active(self, value):
		if not self.active == value:
			self.active = value
			self.remove(0)
			self.add((TAB_WIDTH, self.get_best_height()))
			self.refresh()

	def close(self):pass

	def get_best_height(self):
		height = TAB_PADDING * 2 + 2
		height += self.icon.GetSize()[0]
		height += self._get_text_size(self.text, self.active)[0]
		height += self.inactive_close_but.GetSize()[0]
		return height

	def _get_text_size(self, text, bold=False):
		font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
		if bold and config.tabs_use_bold:
			font.SetWeight(wx.FONTWEIGHT_BOLD)
		if config.tabs_fontsize:
			if font.IsUsingSizeInPixels():
				font.SetPixelSize(config.tabs_fontsize)
			else:
				font.SetPointSize(config.tabs_fontsize)
		result = (0, 0)
		if text:
			pdc = wx.MemoryDC()
			pdc.SetFont(font)
			height = pdc.GetCharHeight()
			text += '  '
			width = pdc.GetTextExtent(text)[0]
			result = (width, height)
		return result

	######################################

	def _on_move(self, event):
		mouse_pos = event.GetPosition()
		if self.but_rect.Inside(mouse_pos) and not self.but_active:
			self.but_active = True
			self.refresh()
		if not self.but_rect.Inside(mouse_pos) and self.but_active:
			self.but_active = False
			self.but_pressed = False
			self.refresh()

	def _on_win_leave(self, event):
		if self.but_active:
			self.but_active = False
			self.but_pressed = False
			self.refresh()

	def _on_left_down(self, event):
		mouse_pos = event.GetPosition()
		if self.but_rect.Inside(mouse_pos):
			self.but_pressed = True
			self.refresh()

	def _on_left_up(self, event):
		mouse_pos = event.GetPosition()
		if self.but_rect.Inside(mouse_pos):
			self.but_pressed = False
			self.refresh()
			self.plg.app.plg_area.close_plugin(self.plg.pid)
		elif self.rect.Inside(mouse_pos) and not self.active:
			self.plg.app.plg_area.show_plugin(self.plg.pid)

	######################################

	def _on_paint(self, event):
		w, h = self.panel.GetSize()
		self.rect = wx.Rect(0, 0, w, h)
		pdc = wx.PaintDC(self.panel)
		try:dc = wx.GCDC(pdc)
		except:dc = pdc
		pdc.BeginDrawing()
		dc.BeginDrawing()

		#----- colors definition
		border_color = const.UI_COLORS['hover_solid_border']
		bg_color = const.UI_COLORS['bg']
		light_bg_color = const.mix_colors((255, 255, 255), bg_color, 100)
		dark_bg_color = const.mix_colors((0, 0, 0), bg_color, 5)
		grad_start = wx.Colour(0, 0, 0, 10)
		grad_end = wx.Colour(0, 0, 0, 0)

		if self.active:
			#----- draw border
			pdc.SetBrush(wx.TRANSPARENT_BRUSH)
			pdc.SetPen(wx.Pen(wx.Colour(*border_color), 1))
			pdc.DrawRoundedRectangle(-3, 0, w, h, 3.0)
			#----- draw icon
			y = TAB_PADDING
			x = (TAB_WIDTH - self.icon.GetSize()[1]) / 2
			dc.DrawBitmap(self.icon, x, y, True)
			#----- draw text
			y += 3 + self.icon.GetSize()[0]
			txt_h = self._get_text_size(self.text, self.active)[1]
			x = (TAB_WIDTH - txt_h) / 2 + txt_h - 2
			font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
			if config.tabs_use_bold:
				font.SetWeight(wx.FONTWEIGHT_BOLD)
			if config.tabs_fontsize:
				if font.IsUsingSizeInPixels():
					font.SetPixelSize(config.tabs_fontsize)
				else:
					font.SetPointSize(config.tabs_fontsize)
			pdc.SetFont(font)
			pdc.DrawRotatedText(self.text, x, y, 270)
			#----- draw button
			y += self._get_text_size(self.text, self.active)[0]
			x = (TAB_WIDTH - self.inactive_close_but.GetSize()[0]) / 2
			if not self.active:x -= 1
			if self.but_active:
				dc.DrawBitmap(self.close_but, x, y, True)
				if self.but_pressed: dc.DrawBitmap(self.close_but, x, y, True)
			else: dc.DrawBitmap(self.inactive_close_but, x, y, True)
			but_w, but_h = self.inactive_close_but.GetSize()
			self.but_rect = wx.Rect(x, y, but_w, but_h)
		else:
			#----- draw border
			pdc.SetBrush(wx.TRANSPARENT_BRUSH)
			pdc.SetPen(wx.Pen(wx.Colour(*border_color), 1))
			pdc.DrawRoundedRectangle(-5, 0, w, h, 3.0)
			pdc.SetPen(wx.Pen(wx.Colour(*const.UI_COLORS['hover_solid_border']), 1))
			pdc.DrawLine(0, 0, 0, h)
			#----- draw icon
			y = TAB_PADDING
			x = (TAB_WIDTH - self.icon.GetSize()[1]) / 2 - 1
			dc.DrawBitmap(self.icon, x, y, True)
			#----- draw text
			y += 3 + self.icon.GetSize()[0]
			txt_h = self._get_text_size(self.text, self.active)[1]
			x = (TAB_WIDTH - txt_h) / 2 + txt_h - 3
			font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
			if config.tabs_fontsize:
				if font.IsUsingSizeInPixels():
					font.SetPixelSize(config.tabs_fontsize)
				else:
					font.SetPointSize(config.tabs_fontsize)
			pdc.SetFont(font)
			pdc.DrawRotatedText(self.text, x, y, 270)
			#----- draw button
			y += self._get_text_size(self.text, self.active)[0]
			x = (TAB_WIDTH - self.inactive_close_but.GetSize()[0]) / 2
			if not self.active:x -= 1
			if self.but_active:
				dc.DrawBitmap(self.close_but, x, y, True)
				if self.but_pressed: dc.DrawBitmap(self.close_but, x, y, True)
			else: dc.DrawBitmap(self.inactive_close_but, x, y, True)
			but_w, but_h = self.inactive_close_but.GetSize()
			self.but_rect = wx.Rect(x, y, but_w, but_h)
			#----- shadow
			color1 = wx.Colour(0, 0, 0, 20)
			color2 = wx.Colour(0, 0, 0, 0)
			rect = wx.Rect(0, 0, w / 2, h)
			dc.GradientFillLinear(rect, color1, color2, nDirection=wx.EAST)


		if not pdc == dc:
			dc.EndDrawing()
			pdc.EndDrawing()
		else:
			dc.EndDrawing()
		pdc = dc = None
