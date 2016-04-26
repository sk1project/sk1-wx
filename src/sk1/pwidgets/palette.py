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

import wal

from sk1 import config, events

class Palette(wal.VPanel, wal.SensitiveCanvas):

	hpal = True
	position = 0
	maxposition = 0
	cell_sizes = []
	ncolors = 0
	scroll_size = 0


	def __init__(self, parent, app, hpal=True,
				on_left_click=None, on_right_click=None,
				 onmin=None, onmax=None):
		self.hpal = hpal
		self.app = app
		self.cell_sizes = []
		self.onmin = onmin
		self.onmax = onmax
		self.on_left_click = on_left_click
		self.on_right_click = on_right_click
		wal.VPanel.__init__(self, parent)
		wal.SensitiveCanvas.__init__(self, True)
		self.set_double_buffered()
		self.set_palette_size()
		events.connect(events.CONFIG_MODIFIED, self.config_update)
		events.connect(events.CMS_CHANGED, self.palette_refresh)

	def config_update(self, attr, val):
		if not attr[:7] == 'palette':return
		self.refresh()

	def palette_refresh(self, *args):
		self.refresh()

	def set_palette_size(self):
		self.remove_all()
		if self.hpal: size = config.palette_hcell_height
		else: size = config.palette_vcell_width
		self.pack((size, size))

	def get_cell_size(self):
		ncolors = self.ncolors
		w, h = self.get_size()
		delta = 0
		if self.hpal:
			wcell = config.palette_hcell_width
			hcell = config.palette_hcell_height
			self.scroll_size = wcell
			self.maxposition = ncolors * (wcell - 1) + 1 - w
			if self.maxposition < 0:self.maxposition = 0
		else:
			wcell = config.palette_vcell_width
			hcell = config.palette_vcell_height
			self.scroll_size = hcell
			self.maxposition = ncolors * (hcell - 1) + 1 - h
			if self.maxposition < 0:self.maxposition = 0
		if config.palette_expand and self.hpal:
			if not ncolors * (wcell - 1) + 1 > w:
				wcell = (w - 1) / ncolors + 1
				delta = w - ncolors * (wcell - 1) - 1
				self.scroll_size = 0
				self.position = 0
				self.maxposition = 0
		if config.palette_expand and not self.hpal:
			if not ncolors * (hcell - 1) + 1 > h:
				hcell = (h - 1) / ncolors + 1
				delta = h - ncolors * (hcell - 1) - 1
				self.scroll_size = 0
				self.position = 0
				self.maxposition = 0
		return wcell, hcell, delta

	def paint(self):
		w, h = self.get_size()
		self.cell_sizes = []

		self.set_stroke(None)
		self.set_fill(self.get_bg())
		self.draw_rect(0, 0, w, h)

		colors = self.app.palettes.palette_in_use.model.colors
		cms = self.app.default_cms
		self.ncolors = len(colors)

		wcell, hcell, delta = self.get_cell_size()

		self.set_stroke(wal.BLACK)
		pos = 0

		if self.position > self.maxposition:
			self.position = self.maxposition
		if self.onmax: self.onmax(not self.position == self.maxposition)
		if self.onmin: self.onmin(not self.position == 0)

		if self.hpal: self.set_origin(x=-self.position)
		else: self.set_origin(y=-self.position)

		for color in colors:
			self.set_fill(cms.get_display_color255(color))

			d = 0
			if delta: d = 1;delta -= 1

			if self.hpal:
				self.draw_rect(pos, 0, wcell + d, hcell)
				pos += wcell + d - 1
			else:
				self.draw_rect(0, pos, wcell, hcell + d)
				pos += hcell + d - 1
			self.cell_sizes.append(pos)

	def scroll_start(self, val=1):
		if self.scroll_size:
			self.position -= (self.scroll_size - 1) * val
			if self.position < 0: self.position = 0
			self.refresh()

	def scroll_end(self, val=1):
		if self.scroll_size:
			self.position += (self.scroll_size - 1) * val
			if self.position < 0: self.position = 0
			self.refresh()

	def mouse_wheel(self, val):
		self.scroll_start(val / 12)

	def get_color(self, point):
		size = point[1] + self.position
		if self.hpal:size = point[0] + self.position
		i = 0
		ret = None
		for item in self.cell_sizes:
			if size < item:
				ret = self.app.palettes.palette_in_use.model.colors[i]
				break
			i += 1
		return ret

	def mouse_left_up(self, point):
		color = self.get_color(point)
		if not color is None:
			if self.on_left_click:self.on_left_click(color)

	def mouse_right_up(self, point):
		color = self.get_color(point)
		if not color is None:
			if self.on_right_click:self.on_right_click(color)

	def mouse_move(self, point):
		color = self.get_color(point)
		if not color is None and color[3]:
			self.set_tooltip(color[3])
		else:
			self.set_tooltip()

