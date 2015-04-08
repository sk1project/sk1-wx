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
from sk1.resources import icons

AUTO_MODE = 0
NORMAL_MODE = 1
LARGE_MODE = 2
LIST_MODE = 3

MODE_ICON = {
AUTO_MODE:icons.PD_PALETTE_AUTO,
NORMAL_MODE:icons.PD_PALETTE_NORMAL,
LARGE_MODE:icons.PD_PALETTE_LARGE,
LIST_MODE:icons.PD_PALETTE_LIST,
}

MODE_NAME = {
AUTO_MODE:_('Auto mode'),
NORMAL_MODE:_('Small cells'),
LARGE_MODE:_('Large cells'),
LIST_MODE:_('List view'),
}

PREVIEW_MODES = [AUTO_MODE, NORMAL_MODE, LARGE_MODE, LIST_MODE]

class ScrolledPalette(wal.ScrolledPanel, wal.Canvas):

	mode = AUTO_MODE
	width = 10
	height = 10
	cell_width = 16
	cell_height = 16
	cell_in_line = 10
	colors = None
	sb_width = 1

	def __init__(self, app, parent, border=False):
		self.app = app
		self.parent = parent
		wal.ScrolledPanel.__init__(self, parent, border)
		wal.Canvas.__init__(self)
		sb = wal.ScrollBar(self)
		self.sb_width = sb.get_size()[0]
		sb.destroy()
		self.width = (self.cell_width - 1) * self.cell_in_line + 3 + self.sb_width
		self.set_size((self.width, -1))
		self.set_bg(wal.WHITE)


	def paint(self):
		if not self.colors:return
		if self.mode == NORMAL_MODE:
			self.normal_mode_paint()
		elif self.mode == LARGE_MODE:
			self.large_mode_paint()
		elif self.mode == LIST_MODE:
			self.list_mode_paint()
		else:
			if len(self.colors) < 15:
				self.list_mode_paint()
			elif len(self.colors) < 50:
				self.large_mode_paint()
			else:
				self.normal_mode_paint()

		self.set_stroke(wal.UI_COLORS['dark_shadow'])
		self.set_fill(wal.UI_COLORS['bg'])
		self.draw_rect(self.width - self.sb_width, -1,
						self.sb_width + 1, self.get_size()[1] + 2)

	def normal_mode_paint(self):
		self.cell_in_line = 10
		self.cell_width = 16
		self.cell_height = 16
		self.cell_mode_paint()

	def large_mode_paint(self):
		self.cell_in_line = 5
		self.cell_width = 31
		self.cell_height = 31
		self.cell_mode_paint()

	def cell_mode_paint(self):
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

	def list_mode_paint(self):
		self.cell_width = 20
		self.cell_height = 20
		row = self.cell_height + 4
		cms = self.app.default_cms

		self.height = len(self.colors) * row
		self.set_virtual_size((self.width - self.sb_width, self.height))
		self.set_scroll_rate(self.cell_width - 1, self.cell_height - 1)

		self.prepare_dc(self.pdc)

		w = self.cell_width
		h = self.cell_height
		i = 0
		txt_height = self.set_font()
		txt_x = 5 + self.cell_width + 5
		txt_y = 2 + round((self.cell_height - txt_height) / 2.0)
		self.set_text_color(wal.BLACK)

		for color in self.colors:
			self.set_stroke(wal.BLACK)
			self.set_fill(cms.get_display_color255(color))
			self.draw_rect(5, 2 + row * i, w, h)
			txt = color[3]
			if txt: self.draw_text(txt, txt_x, txt_y + row * i)
			i += 1

class ModeToggleButton(wal.ImageToggleButton):

	mode = AUTO_MODE
	callback = None

	def __init__(self, parent, mode, on_change=None):
		self.mode = mode
		self.callback = on_change
		wal.ImageToggleButton.__init__(self, parent, False, MODE_ICON[mode],
								tooltip=MODE_NAME[mode], onchange=self.change)

	def change(self):
		if not self.get_active():
			if self.parent.mode == self.mode:
				self.set_active(True)
		else:
			if not self.parent.mode == self.mode:
				if self.callback: self.callback(self.mode)

	def set_mode(self, mode):
		if not self.mode == mode:
			if self.get_active():
				self.set_active(False)
		else:
			if not self.get_active():
				self.set_active(True)


class PaletteModeChanger(wal.HPanel):

	buttons = []
	mode = None
	callback = None

	def __init__(self, parent, on_change=None):
		self.buttons = []
		self.callback = on_change
		wal.HPanel.__init__(self, parent)
		for item in PREVIEW_MODES:
			but = ModeToggleButton(self, item, on_change=self.set_mode)
			self.pack(but)
			self.buttons.append(but)
		self.set_mode(AUTO_MODE)

	def set_mode(self, mode):
		if self.mode == mode:return
		self.mode = mode
		for item in self.buttons:
			item.set_mode(self.mode)
		if self.callback: self.callback(self.mode)


class PaletteViewer(wal.VPanel):

	palette = None

	def __init__(self, app, parent, palette=None):
		self.app = app
		wal.VPanel.__init__(self, parent)
		options = wal.ExpandedPanel(self, _('Palette preview:'))
		changer = PaletteModeChanger(options, on_change=self.set_mode)
		options.pack(changer)
		self.pack(options, fill=True)
		border = wal.VPanel(self, border=True)
		self.pack(border, expand=True, fill=True)
		self.win = ScrolledPalette(self.app, border)
		border.pack(self.win, expand=True, fill=True)
		if palette: self.draw_palette(palette)

	def draw_palette(self, palette=None):
		if not palette: return
		self.palette = palette
		self.win.colors = palette.model.colors
		self.win.refresh()

	def set_mode(self, mode):
		if not self.palette: return
		self.win.mode = mode
		self.win.refresh()

