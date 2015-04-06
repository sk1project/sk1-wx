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

import wal

from sk1 import _

class ScrolledPalette(wal.ScrolledPanel, wal.Canvas):

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
		wal.ScrolledPanel.__init__(self, parent)
		wal.Canvas.__init__(self)
		sb = wal.ScrollBar(self)
		self.sb_width = sb.get_size()[0]
		sb.destroy()
		self.width = (self.cell_width - 1) * self.cell_in_line + 3 + self.sb_width
		self.set_size((self.width, -1))
		self.set_bg(wal.WHITE)


	def paint(self):
		if not self.colors:return
		cms = self.app.default_cms

		self.height = round(1.0 * len(self.colors) / self.cell_in_line) + 1
		self.height = self.height * (self.cell_height - 1)
		self.set_virtual_size((self.width - self.sb_width, self.height))
		self.set_scroll_rate(self.cell_width - 1, self.cell_height - 1)

		self.prepare_dc(self.pdc)

		w = self.cell_width
		h = self.cell_height
		y = 1
		x = 1
		for color in self.colors:
			self.set_stroke(wal.BLACK)
			self.set_fill(cms.get_display_color255(color))
			self.draw_rect(x, y, w, h)
			x += w - 1
			if x > (w - 1) * self.cell_in_line:
				x = 1
				y += h - 1

		self.set_stroke(wal.UI_COLORS['dark_shadow'])
		self.set_fill(wal.UI_COLORS['bg'])
		self.draw_rect(self.width - self.sb_width, 0,
						self.sb_width + 1, self.get_size()[1] + 2)

class PaletteViewer(wal.VPanel):

	palette = None

	def __init__(self, app, parent, palette=None):
		self.app = app
		wal.VPanel.__init__(self, parent, border=True)
		options = wal.ExpandedPanel(self, _('Palette preview:'))
		self.pack(options, fill=True)
		self.win = ScrolledPalette(self.app, self)
		self.pack(self.win, expand=True, fill=True)
		if palette: self.draw_palette(palette)

	def draw_palette(self, palette=None):
		if not palette: return
		self.palette = palette
		self.win.colors = palette.model.colors
		self.win.refresh()

