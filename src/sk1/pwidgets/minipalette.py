# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2016 by Igor E. Novikov
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

from uc2 import cms

COLORS = ['#282828', '#424242', '#666666', '#989898', '#D5D5D5', '#FFFFFF']

class ColorCell(wal.VPanel, wal.SensitiveCanvas):

	color = None
	callback = None
	state = True

	def __init__(self, parent, color=(), size=(30, 30), onclick=None):
		self.color = color
		self.callback = onclick
		wal.VPanel.__init__(self, parent)
		wal.SensitiveCanvas.__init__(self)
		self.pack(size)

	def set_color(self, color):
		self.color = color
		self.set_bg(color)

	def mouse_left_up(self, point):
		if self.state and self.color and self.callback:
			self.callback(cms.val_255_to_dec(self.color))

	def set_enable(self, state):
		self.state = state
		if state: color = self.color
		else: color = wal.UI_COLORS['bg']
		self.set_bg(color)


class CBMiniPalette(wal.VPanel):

	cells = []

	def __init__(self, parent, colors=COLORS, size=(25, 25), onclick=None):
		wal.VPanel.__init__(self, parent)
		self.grid = wal.GridPanel(self, 1 , len(colors), 1 , 1)
		self.cells = []
		for item in colors:
			color = cms.val_255(cms.hexcolor_to_rgb(item))
			cell = ColorCell(self, color, size, onclick)
			self.grid.pack(cell)
			self.cells.append(cell)
		self.pack(self.grid, padding_all=1)
		self.set_enable(True)

	def set_enable(self, state):
		if state: color = wal.BLACK
		else: color = wal.UI_COLORS['disabled_text']
		self.set_bg(color)
		self.grid.set_bg(color)
		for item in self.cells: item.set_enable(state)