# -*- coding: utf-8 -*-
#
#	Copyright (C) 2015 by Igor E. Novikov
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

import wal, wx

class ScrolledPalette(wal.ScrolledPanel):

	width = 10
	height = 10
	cell_width = 16
	cell_height = 16
	cell_in_line = 10
	colors = None
	sb_width = 1

	def __init__(self, app, parent):
		self.app = app
		self.parent = parent
		wal.ScrolledPanel.__init__(self, parent, drawable=True)
		sb = wal.ScrollBar(self)
		self.sb_width = sb.get_size()[0]
		sb.Destroy()
		self.width = (self.cell_width - 1) * self.cell_in_line + 3 + self.sb_width
		self.set_size((self.width, -1))
		self.set_bg(wal.WHITE)


	def on_paint(self, event):
		if not self.colors:return
		cms = self.app.default_cms

		self.height = round(1.0 * len(self.colors) / self.cell_in_line) + 1
		self.height = self.height * (self.cell_height - 1)
		self.set_virtual_size((self.width - self.sb_width, self.height))
		self.set_scroll_rate(self.cell_width - 1, self.cell_height - 1)

		pdc = wx.PaintDC(self)
		try:
			dc = wx.GCDC(self.pdc)
		except:dc = pdc
		self.PrepareDC(dc)
		dc.BeginDrawing()
		pdc.BeginDrawing()

		w = self.cell_width
		h = self.cell_height
		y = 1
		x = 1
		for color in self.colors:
			pdc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 1))
			clr = cms.get_display_color255(color)
			pdc.SetBrush(wx.Brush(wx.Colour(*clr)))
			pdc.DrawRectangle(x, y, w, h)
			x += w - 1
			if x > (w - 1) * self.cell_in_line:
				x = 1
				y += h - 1

			color = wal.UI_COLORS['dark_shadow']
			dc.SetPen(wx.TRANSPARENT_PEN)
			dc.SetBrush(wx.Brush(wx.Colour(*color)))
			dc.DrawRectangle(self.width - self.sb_width, 0,
							self.sb_width, self.get_size()[1])
			color = wal.UI_COLORS['bg']
			dc.SetBrush(wx.Brush(wx.Colour(*color)))
			dc.DrawRectangle(self.width - self.sb_width + 1, 0,
							self.sb_width, self.get_size()[1])

		if not pdc == dc:
			dc.EndDrawing()
			pdc.EndDrawing()
		else:
			dc.EndDrawing()
		pdc = dc = None

class PaletteViewer(wal.VPanel):

	palette = None

	def __init__(self, app, parent, palette=None):
		self.app = app
		wal.VPanel.__init__(self, parent, border=True)
		self.win = ScrolledPalette(self.app, self)
		self.pack(self.win, expand=True, fill=True)
		if palette: self.draw_palette(palette)

	def draw_palette(self, palette=None):
		if not palette: return
		self.palette = palette
		self.win.colors = palette.model.colors
		self.win.refresh()

