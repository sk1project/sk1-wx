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

from sk1 import _, config
from sk1.resources import icons
from sk1.widgets import const, ALL, EXPAND, HPanel, RIGHT, LEFT

TAB_HEIGHT = 25
TAB_MARGIN = 1
TAB_PADDING = 5
SCROLL_PADDING = 2
PANEL_MARGIN = 3
PANEL_HEIGHT = 27

class DocTabsPanel(HPanel):

	def __init__(self, parent):
		HPanel.__init__(self, parent)

		self.left_scroll = TabScroller(self, icons.ARROW_LEFT,
									tooltip=_('Scroll tabs right'),
									onclick=self.scroll_left)
		self.add(self.left_scroll, 0, ALL | EXPAND)

		self.tabs_bg = TabsBgPanel(self)
		self.add(self.tabs_bg, 1, ALL | EXPAND)

		self.doc_tabs = DocTabs(self.tabs_bg, self.update_panel)
		self.tabs_bg.add(self.doc_tabs, 0, ALL | EXPAND)
		self.doc_tabs.SetPosition((0, 0))

		self.right_scroll = TabScroller(self, icons.ARROW_RIGHT,
									tooltip=_('Scroll tabs left'),
									border_side=LEFT,
									onclick=self.scroll_right)
		self.add(self.right_scroll, 0, ALL | EXPAND)
		self.Bind(wx.EVT_SIZE, self.resize, self)

	def resize(self, event):
		self.update_panel()
		event.Skip()

	def update_panel(self, *args):
		pos = self.doc_tabs.GetPosition()[0]
		width = self.doc_tabs.GetSize()[0]
		bg_width = self.tabs_bg.GetSize()[0] - 1
		if pos < 0 and bg_width > width:
			self.doc_tabs.SetPosition((0, 0))
		if pos < 0 and not self.left_scroll.get_active():
			self.left_scroll.set_active(True)
		elif pos >= 0 and self.left_scroll.get_active():
			self.left_scroll.set_active(False)
		if pos + width > bg_width and not self.right_scroll.get_active():
			self.right_scroll.set_active(True)
		elif pos + width <= bg_width and self.right_scroll.get_active():
			self.right_scroll.set_active(False)

	def scroll_left(self):
		x = self.doc_tabs.GetPosition()[0] + 10
		if x > 0: x = 0
		self.doc_tabs.SetPosition((0, 0))
		self.doc_tabs.SetPosition((x, 0))
		self.update_panel()

	def scroll_right(self):
		x = self.doc_tabs.GetPosition()[0] - 10
		win_x = self.tabs_bg.GetSize()[0]
		if win_x - x > self.doc_tabs.GetSize()[0]:
			x = win_x - (self.doc_tabs.GetSize()[0] + 3)
		self.doc_tabs.SetPosition((0, 0))
		self.doc_tabs.SetPosition((x, 0))
		self.update_panel()

class TabsBgPanel(HPanel):

	def __init__(self, parent):
		HPanel.__init__(self, parent)
		self.Bind(wx.EVT_PAINT, self._on_paint, self)

	def _on_paint(self, event):
		w, h = self.panel.GetSize()
		pdc = wx.PaintDC(self.panel)
		try:
			dc = wx.GCDC(pdc)
		except:dc = pdc
		dc.BeginDrawing()

		color1 = wx.Colour(0, 0, 0, 10)
		color2 = wx.Colour(0, 0, 0, 0)
		rect = wx.Rect(0, h / 2, w, h / 2)
		dc.GradientFillLinear(rect, color1, color2, nDirection=wx.NORTH)
		rect = wx.Rect(0, 0, w, h / 2)
		dc.GradientFillLinear(rect, color1, color2, nDirection=wx.SOUTH)

		pdc.SetPen(wx.Pen(wx.Colour(*const.UI_COLORS['hover_solid_border']), 1))
		pdc.DrawLine(0, h - 1, w, h - 1)
		pdc.DrawLine(0, 0, w, 0)

		if not pdc == dc:
			dc.EndDrawing()
			pdc.EndDrawing()
		else:
			dc.EndDrawing()
		pdc = dc = None

class TabScroller(HPanel):

	callback = None
	active = False
	pressed = False

	def __init__(self, parent, icon, tooltip='', border_side=RIGHT, onclick=None):
		self.icon = wx.ArtProvider.GetBitmap(icon)
		self.callback = onclick
		self.tooltip = tooltip
		self.border_side = border_side
		HPanel.__init__(self, parent)
		width = self.icon.GetSize()[0] + SCROLL_PADDING * 2
		self.add((width, PANEL_HEIGHT))
		self.Bind(wx.EVT_PAINT, self._on_paint, self)
		self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down, self)
		self.Bind(wx.EVT_LEFT_UP, self._on_left_up, self)
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.do_action)

	def get_active(self): return self.active

	def set_active(self, val):
		self.active = val
		self.refresh()
		if self.active:
			self.SetToolTipString(self.tooltip)
		else:
			self.SetToolTip(None)
			self.timer.Stop()

	def _on_left_down(self, event):
		if self.active:
			self.pressed = True
			self.timer.Start(50)
		self.refresh()

	def _on_left_up(self, event):
		self.pressed = False
		self.do_action()
		self.timer.Stop()
		self.refresh()

	def do_action(self, *args):
		if not self.callback is None: self.callback()

	def refresh(self, x=0, y=0, w=0, h=0):
		if not w: w, h = self.GetSize()
		self.Refresh(rect=wx.Rect(x, y, w, h))

	def _on_paint(self, event):
		w, h = self.panel.GetSize()
		pdc = wx.PaintDC(self.panel)
		try:
			dc = wx.GCDC(pdc)
		except:dc = pdc
		dc.BeginDrawing()

		if self.active:
			start = wx.Colour(0, 0, 0, 10)
			end = wx.Colour(0, 0, 0, 0)

			if not self.pressed:
				#----- draw gradient
				rect = wx.Rect(0, h / 2, w, h / 2)
				dc.GradientFillLinear(rect, start, end, nDirection=wx.NORTH)
				dc.GradientFillLinear(rect, start, end, nDirection=wx.NORTH)

			#----- draw icon
			x = SCROLL_PADDING
			y = (PANEL_HEIGHT - self.icon.GetSize()[1]) / 2 + 1
			if self.border_side == RIGHT: x -= 1
			else:x += 1
			if self.pressed: x += 1
			dc.DrawBitmap(self.icon, x, y, True)

			color = const.UI_COLORS['hover_solid_border']
			pdc.SetPen(wx.Pen(wx.Colour(*color), 1))
			if self.border_side == RIGHT:
				pdc.DrawLine(w - 1, 0, w - 1, h)
			else:
				pdc.DrawLine(0, 0, 0, h)

		else:
			rect = wx.Rect(0, h / 2, w, h / 2)
			color1 = wx.Colour(0, 0, 0, 10)
			color2 = wx.Colour(0, 0, 0, 0)
			dc.GradientFillLinear(rect, color1, color2, nDirection=wx.NORTH)
			rect = wx.Rect(0, 0, w, h / 2)
			dc.GradientFillLinear(rect, color1, color2, nDirection=wx.SOUTH)

		pdc.SetPen(wx.Pen(wx.Colour(*const.UI_COLORS['hover_solid_border']), 1))
		pdc.DrawLine(0, h - 1, w, h - 1)
		pdc.DrawLine(0, 0, w, 0)

		if not pdc == dc:
			dc.EndDrawing()
			pdc.EndDrawing()
		else:
			dc.EndDrawing()
		pdc = dc = None


class DocTabs(HPanel):

	doc_tabs = []
	callback = None

	def __init__(self, parent, callback=None):
		HPanel.__init__(self, parent)
		self.callback = callback
		self.doc_tabs = []
		self.add((PANEL_MARGIN, PANEL_HEIGHT))
		self.Bind(wx.EVT_PAINT, self._on_paint, self)

	def refresh(self, x=0, y=0, w=0, h=0):
		if not w: w, h = self.GetSize()
		self.Refresh(rect=wx.Rect(x, y, w, h))

	def update(self):
		self.Layout()
		self.SetSize(self.GetBestSize())
		if not self.callback is None: self.callback()

	def add_new_tab(self, doc):
		doc_tab = DocTab(self.panel, doc)
		self.doc_tabs.append(doc_tab)
		self.add(doc_tab, 0, ALL | EXPAND)
		self.update()
		return doc_tab

	def remove_tab(self, doc):
		doc_tab = doc.docarea.doc_tab
		self.box.Detach(doc_tab)
		self.doc_tabs.remove(doc_tab)
		doc_tab.Hide()
		self.update()

	def set_active(self, doc):
		doc_tab = doc.docarea.doc_tab
		for tab in self.doc_tabs:
			if tab.active: tab.set_active(False)
		doc_tab.set_active(True)
		self.update()

	def _on_paint(self, event):
		w, h = self.panel.GetSize()
		pdc = wx.PaintDC(self.panel)
		try:
			dc = wx.GCDC(pdc)
		except:dc = pdc
		dc.BeginDrawing()

		rect = wx.Rect(0, h / 2, w, h / 2)
		color1 = wx.Colour(0, 0, 0, 10)
		color2 = wx.Colour(0, 0, 0, 0)
		dc.GradientFillLinear(rect, color1, color2, nDirection=wx.NORTH)
		rect = wx.Rect(0, 0, w, h / 2)
		dc.GradientFillLinear(rect, color1, color2, nDirection=wx.SOUTH)
		pdc.SetPen(wx.Pen(wx.Colour(*const.UI_COLORS['hover_solid_border']), 1))
		pdc.DrawLine(0, h - 1, w, h - 1)
		pdc.DrawLine(0, 0, w, 0)

		if not pdc == dc:
			dc.EndDrawing()
			pdc.EndDrawing()
		else:
			dc.EndDrawing()
		pdc = dc = None


class DocTab(HPanel):

	doc = None
	parent = None

	active = True
	text = ''
	rect = None
	but_rect = None
	but_active = False
	but_pressed = False

	def __init__(self, parent, doc, active=True):
		self.doc = doc
		self.parent = parent
		self.active = active
		self.text = self.doc.doc_name
		self.icon = wx.ArtProvider.GetBitmap(icons.DOCUMENT_ICON)
		self.close_but = wx.ArtProvider.GetBitmap(icons.PD_CLOSE_BUTTON_ACTIVE)
		self.inactive_close_but = wx.ArtProvider.GetBitmap(icons.PD_CLOSE_BUTTON)
		HPanel.__init__(self, parent)
		self.add((self.get_best_width(), TAB_HEIGHT))
		self.Bind(wx.EVT_PAINT, self._on_paint, self)
		self.Bind(wx.EVT_MOTION, self._on_move, self)
		self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down, self)
		self.Bind(wx.EVT_LEFT_UP, self._on_left_up, self)
		self.Bind(wx.EVT_LEAVE_WINDOW, self._on_win_leave, self)

	def set_title(self, title):
		self.text = title
		self.remove(0)
		self.add((self.get_best_width(), TAB_HEIGHT))
		self.refresh()
		self.parent.update()

	def destroy(self):
		items = self.__dict__.keys()
		for item in items:
			self.__dict__[item] = None

	def refresh(self, x=0, y=0, w=0, h=0):
		if not w: w, h = self.GetSize()
		self.Refresh(rect=wx.Rect(x, y, w, h))

	def set_active(self, value):
		if not self.active == value:
			self.active = value
			self.remove(0)
			self.add((self.get_best_width(), TAB_HEIGHT))
			self.refresh()

	def close(self):pass

	def get_best_width(self):
		width = TAB_PADDING * 2 + 2
		width += self.icon.GetSize()[0]
		width += self._get_text_size(self.text, self.active)[0]
		width += self.inactive_close_but.GetSize()[0]
		return width

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
			self.doc.app.close(self.doc)
		elif self.rect.Inside(mouse_pos) and not self.active:
			self.doc.app.set_current_doc(self.doc)

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
		#----- draw gradient
		rect = wx.Rect(0, 0, w, h / 2)
		dc.GradientFillLinear(rect, grad_start, grad_end, nDirection=wx.SOUTH)

		if self.active:
			#----- draw background
			dc.SetBrush(wx.Brush(wx.Colour(*light_bg_color)))
			dc.SetPen(wx.TRANSPARENT_PEN)
			dc.DrawRoundedRectangle(0, 3, w, h + 5, 3.0)
			#----- draw border
			pdc.SetBrush(wx.TRANSPARENT_BRUSH)
			pdc.SetPen(wx.Pen(wx.Colour(*border_color), 1))
			pdc.DrawRoundedRectangle(0, 3, w, h + 5, 3.0)
			#----- draw gradient
			rect = wx.Rect(0, h / 2, w, h / 2)
			dc.GradientFillLinear(rect, grad_start, grad_end, nDirection=wx.NORTH)
			dc.GradientFillLinear(rect, grad_start, grad_end, nDirection=wx.NORTH)
		else:
			#----- draw background
			dc.SetBrush(wx.Brush(wx.Colour(*dark_bg_color)))
			dc.SetPen(wx.TRANSPARENT_PEN)
			dc.DrawRoundedRectangle(1, 5, w - 2, h + 5, 3.0)
			#----- draw border
			pdc.SetBrush(wx.TRANSPARENT_BRUSH)
			pdc.SetPen(wx.Pen(wx.Colour(*border_color), 1))
			pdc.DrawRoundedRectangle(1, 5, w - 2, h + 5, 3.0)

			#----- draw gradient
			rect = wx.Rect(0, h / 2, w, h / 2)
			dc.GradientFillLinear(rect, grad_start, grad_end, nDirection=wx.NORTH)
			dc.GradientFillLinear(rect, grad_start, grad_end, nDirection=wx.NORTH)

			#----- draw bottom line
			pdc.SetPen(wx.Pen(wx.Colour(*border_color), 1))
			pdc.DrawLine(0, h - 1, w , h - 1)

		#----- draw top line
		pdc.SetPen(wx.Pen(wx.Colour(*border_color), 1))
		pdc.DrawLine(0, 0, w , 0)
		#----- draw icon
		x = TAB_PADDING
		y = (TAB_HEIGHT - self.icon.GetSize()[1]) / 2 + 3
		if not self.active:y += 1
		dc.DrawBitmap(self.icon, x, y, True)
		#----- draw text
		x += 3 + self.icon.GetSize()[0]
		y = (TAB_HEIGHT - self._get_text_size(self.text, self.active)[1]) / 2 + 3
		if not self.active:y += 1
		font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
		if self.active and config.tabs_use_bold:
			font.SetWeight(wx.FONTWEIGHT_BOLD)
		if config.tabs_fontsize:
			if font.IsUsingSizeInPixels():
				font.SetPixelSize(config.tabs_fontsize)
			else:
				font.SetPointSize(config.tabs_fontsize)
		pdc.SetFont(font)
		pdc.DrawText(self.text, x, y)
		#----- draw button
		x += self._get_text_size(self.text, self.active)[0]
		y = (TAB_HEIGHT - self.inactive_close_but.GetSize()[1]) / 2 + 3
		if not self.active:y += 1
		if self.but_active:
			dc.DrawBitmap(self.close_but, x, y, True)
			if self.but_pressed: dc.DrawBitmap(self.close_but, x, y, True)
		else: dc.DrawBitmap(self.inactive_close_but, x, y, True)
		but_w, but_h = self.inactive_close_but.GetSize()
		self.but_rect = wx.Rect(x, y, but_w, but_h)

		if not pdc == dc:
			dc.EndDrawing()
			pdc.EndDrawing()
		else:
			dc.EndDrawing()
		pdc = dc = None
