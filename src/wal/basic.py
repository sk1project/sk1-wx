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
#
#   MacOS X env: export VERSIONER_PYTHON_PREFER_32_BIT=yes

import wx, const

from generic import Widget
from const import FONT_SIZE, DEF_SIZE


class Application(wx.App):

	app_name = None

	mw = None
	mdi = None
	actions = []

	def __init__(self, name='', redirect=False):
		wx.App.__init__(self, redirect=redirect)
		if name:
			self.set_app_name(name)
		const.set_ui_colors(const.UI_COLORS)
		self._set_font_size()

	def _set_font_size(self):
		dc = wx.MemoryDC()
		dc.SetFont(wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT))
		FONT_SIZE[0] = dc.GetTextExtent('D')[0]
		FONT_SIZE[1] = dc.GetCharHeight()

	def set_app_name(self, name):
		self.app_name = name
		self.SetAppName(name)
		self.SetClassName(name)

	def update_actions(self):
		for item in self.actions.keys():
			self.actions[item].update()

	def call_after(self, *args):pass

	def run(self):
		if self.mw:
			self.SetTopWindow(self.mw)
			self.mw.build()
			if self.mw.maximized: self.mw.Maximize()
			self.mw.Show(True)
			self.mdi = self.mw.mdi
			if self.actions:self.update_actions()
			wx.CallAfter(self.call_after)
			self.MainLoop()
		else:
			raise RuntimeError, 'Main window is not defined!'

class MainWindow(wx.Frame):

	mdi = None
	maximized = False

	def __init__(self, title='Frame', size=(100, 100), orientation=wx.VERTICAL,
				maximized=False, on_close=None):
		self.maximized = maximized

		wx.Frame.__init__(self, None, wx.ID_ANY, title, pos=DEF_SIZE, size=size,
						name=title)
		self.orientation = orientation
		self.Centre()
		self.box = wx.BoxSizer(orientation)
		self.SetSizer(self.box)
		self.set_title(title)
		if on_close: self.Bind(wx.EVT_CLOSE, on_close, self)

	def build(self):pass

	def layout(self): self.Layout()
	def get_size(self): return self.GetSize()
	def is_maximized(self): return self.IsMaximized()
	def destroy(self): self.Destroy()
	def hide(self): self.Hide()
	def show(self): self.Show()

	def add(self, *args, **kw):
		"""Arguments: object, expandable (0 or 1), flag, border"""
		self.box.Add(*args, **kw)

	def pack(self, obj, expand=False, fill=False,
			padding=0, start_padding=0, end_padding=0):
		if self.orientation == wx.VERTICAL:
			if expand:expand = 1
			else: expand = 0
			flags = wx.ALIGN_TOP | wx.ALIGN_CENTER_HORIZONTAL
			if padding:
				flags = flags | wx.TOP | wx.BOTTOM
			elif start_padding:
				flags = flags | wx.TOP
				padding = start_padding
			elif end_padding:
				flags = flags | wx.BOTTOM
				padding = end_padding
			if fill: flags = flags | wx.EXPAND
			self.box.Add(obj, expand, flags, padding)
		else:
			if expand:expand = 1
			else: expand = 0
			flags = wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL
			if padding:
				flags = flags | wx.LEFT | wx.RIGHT
			elif start_padding:
				flags = flags | wx.LEFT
				padding = start_padding
			elif end_padding:
				flags = flags | wx.RIGHT
				padding = end_padding
			if fill: flags = flags | wx.EXPAND
			self.box.Add(obj, expand, flags, padding)

	def set_title(self, title):
		self.SetTitle(title)

	def set_minsize(self, size):
		self.SetMinSize(size)

	def set_icons(self, filepath):
		icons = wx.IconBundle()
		icons.AddIconFromFile(filepath, wx.BITMAP_TYPE_ANY)
		self.SetIcons(icons)

class Panel(wx.Panel, Widget):

	def __init__(self, parent, border=False):
		style = wx.TAB_TRAVERSAL
		if border:style |= wx.BORDER_MASK
		wx.Panel.__init__(self, parent, wx.ID_ANY, style=style)

	def set_bg(self, color):
		self.SetBackgroundColour(wx.Colour(*color))
	def get_bg(self):
		return self.GetBackgroundColour().Get()

	def set_size(self, size): self.SetSize(size)
	def layout(self):self.Layout()
	def fit(self):self.Fit()

class SizedPanel(Panel):

	panel = None

	def __init__(self, parent, orientation=wx.HORIZONTAL,
				border=False):
		self.parent = parent
		self.orientation = orientation
		Panel.__init__(self, parent, border)
		self.box = wx.BoxSizer(orientation)
		self.SetSizer(self.box)
		self.panel = self

	def add(self, *args, **kw):
		"""Arguments: object, expandable (0 or 1), flag, border"""
		obj = args[0]
		if not isinstance(obj, tuple):
			if not obj.GetParent() == self.panel:
				obj.Reparent(self.panel)
		self.box.Add(*args, **kw)
		if not isinstance(obj, tuple) and not isinstance(obj, int):
			obj.Show()

	def box_add(self, *args, **kw):
		"""Arguments: object, expandable (0 or 1), flag, border"""
		self.box.Add(*args, **kw)

	def remove(self, obj):
		self.box.Detach(obj)
		if not isinstance(obj, tuple) and not isinstance(obj, int):
			obj.Hide()

	def remove_all(self):
		self.box.Clear()


class HPanel(SizedPanel):
	def __init__(self, parent, border=False):
		SizedPanel.__init__(self, parent, wx.HORIZONTAL, border)

	def pack(self, obj, expand=False, fill=False,
			padding=0, start_padding=0, end_padding=0, padding_all=0):

		if expand:expand = 1
		else: expand = 0

		flags = wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL

		if padding:
			flags = flags | wx.LEFT | wx.RIGHT
		elif padding_all:
			flags = flags | wx.ALL
			padding = padding_all
		elif start_padding:
			flags = flags | wx.LEFT
			padding = start_padding
		elif end_padding:
			flags = flags | wx.RIGHT
			padding = end_padding

		if fill: flags = flags | wx.EXPAND

		self.add(obj, expand, flags, padding)

class VPanel(SizedPanel):
	def __init__(self, parent, border=False):
		SizedPanel.__init__(self, parent, wx.VERTICAL, border)

	def pack(self, obj, expand=False, fill=False, align_center=True,
			padding=0, start_padding=0, end_padding=0, padding_all=0):

		if expand:expand = 1
		else: expand = 0

		flags = wx.ALIGN_TOP
		if align_center:
			flags |= wx.ALIGN_CENTER_HORIZONTAL

		if padding:
			flags = flags | wx.TOP | wx.BOTTOM
		elif padding_all:
			flags = flags | wx.ALL
			padding = padding_all
		elif start_padding:
			flags = flags | wx.TOP
			padding = start_padding
		elif end_padding:
			flags = flags | wx.BOTTOM
			padding = end_padding

		if fill: flags = flags | wx.EXPAND

		self.add(obj, expand, flags, padding)

class Canvas(object):

	dc = None
	pdc = None

	def __init__(self):
		self.Bind(wx.EVT_PAINT, self._on_paint, self)
		self.Bind(wx.EVT_SIZE, self._on_size_change, self)

	def _on_size_change(self, event):
		self.refresh()

	def refresh(self, x=0, y=0, w=0, h=0):
		if not w: w, h = self.GetSize()
		self.Refresh(rect=wx.Rect(x, y, w, h))

	def _on_paint(self, event):
		w, h = self.GetSize()
		if not w or not h: return
		self.pdc = wx.PaintDC(self)
		try:
			self.dc = wx.GCDC(self.pdc)
		except:self.dc = self.pdc
		self.dc.BeginDrawing()

		self.paint()

		if not self.pdc == self.dc:
			self.dc.EndDrawing()
			self.pdc.EndDrawing()
		else:
			self.dc.EndDrawing()
		self.pdc = self.dc = None

	#Paint method for inherited class
	def paint(self):pass

	#========PaintDC

	def set_origin(self, x=0, y=0):
		self.pdc.SetDeviceOrigin(x, y)

	def set_stroke(self, color=None, width=1):
		if color is None:
			self.pdc.SetPen(wx.TRANSPARENT_PEN)
		else:
			self.pdc.SetPen(wx.Pen(wx.Colour(*color), width))

	def set_fill(self, color=None):
		if color is None:
			self.pdc.SetBrush(wx.TRANSPARENT_BRUSH)
		else:
			self.pdc.SetBrush(wx.Brush(wx.Colour(*color)))

	def set_font(self, bold=False, size_incr=0):
		font = self.GetFont()
		if bold:
			font.SetWeight(wx.FONTWEIGHT_BOLD)
		else:
			font.SetWeight(wx.FONTWEIGHT_NORMAL)
		if size_incr:
			if font.IsUsingSizeInPixels():
				sz = font.GetPixelSize() + size_incr
				font.SetPixelSize(sz)
			else:
				sz = font.GetPointSize() + size_incr
				font.SetPointSize(sz)
		self.pdc.SetFont(font)
		return self.pdc.GetCharHeight()

	def set_text_color(self, color):
		self.pdc.SetTextForeground(wx.Colour(*color))

	def draw_line(self, x0, y0, x1, y1):
		self.pdc.DrawLine(x0, y0, x1, y1)

	def draw_rounded_rect(self, x=0, y=0, w=1, h=1, radius=1.0):
		self.pdc.DrawRoundedRectangle(x, y, w, h, radius)

	def draw_rect(self, x=0, y=0, w=1, h=1):
		self.pdc.DrawRectangle(x, y, w, h)

	def draw_text(self, text, x, y):
		self.pdc.DrawText(text, x, y)

	#=========GC device

	def set_gc_origin(self, x=0, y=0):
		self.dc.SetDeviceOrigin(x, y)

	def set_gc_stroke(self, color=None, width=1):
		if color is None:
			self.dc.SetPen(wx.TRANSPARENT_PEN)
		else:
			self.dc.SetPen(wx.Pen(wx.Colour(*color), width))

	def set_gc_fill(self, color=None):
		if color is None:
			self.dc.SetBrush(wx.TRANSPARENT_BRUSH)
		else:
			self.dc.SetBrush(wx.Brush(wx.Colour(*color)))

	def set_gc_font(self, bold=False, size_incr=0):
		font = self.GetFont()
		if bold:
			font.SetWeight(wx.FONTWEIGHT_BOLD)
		else:
			font.SetWeight(wx.FONTWEIGHT_NORMAL)
		if size_incr:
			if font.IsUsingSizeInPixels():
				sz = font.GetPixelSize() + size_incr
				font.SetPixelSize(sz)
			else:
				sz = font.GetPointSize() + size_incr
				font.SetPointSize(sz)
		self.dc.SetFont(font)
		return self.dc.GetCharHeight()

	def set_gc_text_color(self, color):
		self.dc.SetTextForeground(wx.Colour(*color))

	def gc_draw_rounded_rect(self, x=0, y=0, w=1, h=1, radius=1.0):
		self.dc.DrawRoundedRectangle(x, y, w, h, radius)

	def gc_draw_line(self, x0, y0, x1, y1):
		self.dc.DrawLine(x0, y0, x1, y1)

	def gc_draw_rect(self, x=0, y=0, w=1, h=1):
		self.dc.DrawRectangle(x, y, w, h)

	def gc_draw_text(self, text, x, y):
		self.dc.DrawText(text, x, y)

class SensitiveCanvas(Canvas):

	def __init__(self):
		Canvas.__init__(self)
		self.Bind(wx.EVT_LEFT_UP, self._mouse_left_up)
		self.Bind(wx.EVT_MOUSEWHEEL, self._mouse_wheel)
		self.Bind(wx.EVT_RIGHT_UP, self._mouse_right_up)

	def _mouse_left_up(self, event):
		self.mouse_left_up(event.GetPositionTuple())

	def _mouse_right_up(self, event):
		self.mouse_right_up(event.GetPositionTuple())

	def _mouse_wheel(self, event):
		self.mouse_wheel(event.GetWheelRotation())

	def mouse_left_up(self, point):pass
	def mouse_right_up(self, point):pass
	def mouse_wheel(self, val):pass


class RoundedPanel(VPanel, Canvas):

	def __init__(self, parent):
		VPanel.__init__(self, parent)
		Canvas.__init__(self)

	def paint(self):
		w, h = self.get_size()
		self.set_fill(None)
		color = const.UI_COLORS['light_shadow']
		self.set_stroke(color)
		self.draw_rounded_rect(1, 1, w - 1, h - 1, 7.0)
		color = const.UI_COLORS['dark_shadow']
		self.set_stroke(color)
		self.draw_rounded_rect(0, 0, w - 1, h - 1, 7.0)


class LabeledPanel(VPanel):

	panel = None
	widget_panel = None
	widget = None

	def __init__(self, parent, text='', widget=None):
		VPanel.__init__(self, parent)
		self.inner_panel = RoundedPanel(self)

		if widget or text:
			self.widget_panel = HPanel(self)
			if widget:
				self.widget = widget
			elif text:
				self.widget = wx.StaticText(self.widget_panel, wx.ID_ANY, text)
			self.widget_panel.pack(self.widget, padding=5)
			self.widget_panel.SetPosition((7, 0))
			self.widget_panel.Fit()

		padding = 0
		if self.widget_panel:
			padding = round(self.widget_panel.get_size()[1] / 2.0)
			self.inner_panel.pack((1, padding))
		VPanel.pack(self, self.inner_panel, expand=True, fill=True,
				start_padding=padding)

	def pack(self, *args, **kw):
		obj = args[0]
		self.inner_panel.pack(*args, **kw)
		if not isinstance(obj, tuple) and not isinstance(obj, int):
			obj.show()


class GridPanel(Panel, Widget):

	def __init__(self, parent, rows=2, cols=2, vgap=0, hgap=0, border=False):
		Panel.__init__(self, parent, border)
		self.grid = wx.FlexGridSizer(rows, cols, vgap, hgap)
		self.SetSizer(self.grid)

	def set_vgap(self, val):self.grid.SetVGap(val)
	def set_hgap(self, val):self.grid.SetHGap(val)
	def sel_cols(self, val):self.grid.SetCols(val)
	def sel_rows(self, val):self.grid.SetRows(val)
	def add_growable_col(self, index): self.grid.AddGrowableCol(index)
	def add_growable_row(self, index): self.grid.AddGrowableRow(index)

	def pack(self, obj, expand=False, fill=False, align_right=False,
			align_left=True):
		if expand:expand = 1
		else: expand = 0
		if align_right:
			flags = wx.ALIGN_RIGHT
		elif align_left:
			flags = wx.ALIGN_LEFT
		else:
			flags = wx.ALIGN_CENTER_HORIZONTAL
		flags |= wx.ALIGN_CENTER_VERTICAL

		if fill: flags = flags | wx.EXPAND
		self.add(obj, expand, flags)

	def add(self, *args, **kw):
		"""Arguments: object, expandable (0 or 1), flag"""
		obj = args[0]
		if not isinstance(obj, tuple):
			if not obj.GetParent() == self:
				obj.Reparent(self)
		self.grid.Add(*args, **kw)
		if not isinstance(obj, tuple) and not isinstance(obj, int):
			obj.show()

class ScrolledPanel(wx.ScrolledWindow, Widget):

	def __init__(self, parent, border=False):
		style = wx.NO_BORDER
		if border:style = wx.BORDER_MASK
		wx.ScrolledWindow.__init__(self, parent, wx.ID_ANY, style=style)
		self.set_scroll_rate()
		self.SetDoubleBuffered(True)

	def set_virtual_size(self, size): self.SetVirtualSize(size)
	def set_scroll_rate(self, h=20, v=20): self.SetScrollRate(h, v)
	def set_bg(self, color): self.SetBackgroundColour(wx.Colour(*color))
	def refresh(self, x=0, y=0, w=0, h=0):
		if not w: w, h = self.GetVirtualSize()
		self.Refresh(rect=wx.Rect(x, y, w, h))
	def set_size(self, size): self.SetSize(size)
	def prepare_dc(self, dc): self.PrepareDC(dc)


class Expander(VPanel, Canvas):

	state = False
	callback = None

	def __init__(self, parent, on_click=None):
		VPanel.__init__(self, parent)
		Canvas.__init__(self)
		self.pack((13, 13))
		if on_click:
			self.callback = on_click
			self.Bind(wx.EVT_LEFT_UP, self._click, self)
			self.Bind(wx.EVT_RIGHT_UP, self._click, self)
		self.refresh()

	def _click(self, event):
		self.callback()

	def change(self, val=False):
		self.state = val
		self.refresh()

	def paint(self):
		w, h = self.get_size()
		self.set_stroke(const.BLACK, 1)
		self.set_fill(None)
		self.draw_rect(3, 3, w - 4, h - 4)
		half = int(w / 2.0) + 1
		self.draw_line(5, half, w - 3, half)
		if not self.state:
			self.draw_line(half, 5, half, h - 3)

class ExpandedPanel(VPanel):

	def __init__(self, parent, txt=''):
		VPanel.__init__(self, parent)
		header = HPanel(self)
		self.expander = Expander(header, on_click=self.expand)
		header.pack(self.expander, padding=2)
		if txt: header.pack(wx.StaticText(header, wx.ID_ANY, txt))
		VPanel.pack(self, header, fill=True)
		self.container = VPanel(self)
		VPanel.pack(self, self.container, fill=True)
		self.container.set_visible(False)
		self.layout()

	def expand(self):
		self.container.set_visible(not self.container.is_shown())
		self.parent.layout()
		self.expander.change(self.container.is_shown())

	def pack(self, *args, **kw):
		self.container.pack(*args, **kw)




