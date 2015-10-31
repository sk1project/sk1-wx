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

from copy import deepcopy
import wal

from uc2.formats.sk2 import sk2_const

from sk1 import _

from colorctrls import SwatchCanvas
from patterns import PATTERN_PRESETS
from colorbtn import PDColorButton

class PatternPaletteSwatch(wal.VPanel, SwatchCanvas):

	callback = None
	pattern = None

	def __init__(self, parent, cms, pattern, size=(40, 20), onclick=None):
		self.color = None
		self.cms = cms
		wal.VPanel.__init__(self, parent)
		SwatchCanvas.__init__(self)
		self.pack(size)
		if onclick: self.callback = onclick
		self.set_pattern(pattern)

	def set_pattern(self, pattern):
		self.pattern = pattern
		self.fill = [0, sk2_const.FILL_PATTERN,
				[sk2_const.PATTERN_IMG, pattern]]
		self.refresh()

	def mouse_left_up(self, point):
		if self.callback: self.callback(deepcopy(self.pattern))

class PatternMiniPalette(wal.VPanel):

	callback = None
	cells = []

	def __init__(self, parent, cms, onclick=None):
		wal.VPanel.__init__(self, parent)
		self.set_bg(wal.BLACK)
		grid = wal.GridPanel(parent, 2, 6, 1, 1)
		grid.set_bg(wal.BLACK)
		self.cells = []

		for item in range(12):
			self.cells.append(PatternPaletteSwatch(grid, cms,
							PATTERN_PRESETS[item], onclick=self.on_click))
			grid.pack(self.cells[-1])
		self.pack(grid, padding_all=1)
		if onclick: self.callback = onclick

	def on_click(self, pattern):
		if self.callback: self.callback(pattern)

class PatternSwatch(wal.VPanel, SwatchCanvas):

	callback = None
	pattern = None

	def __init__(self, parent, cms, pattern_def, size=(130, 130)):
		self.color = None
		self.cms = cms
		wal.VPanel.__init__(self, parent)
		SwatchCanvas.__init__(self, border='news')
		self.pack(size)
		self.set_pattern_def(pattern_def)

	def set_pattern_def(self, pattern_def):
		self.fill = [0, sk2_const.FILL_PATTERN, pattern_def]
		self.refresh()

class PatternColorEditor(wal.HPanel):

	image_style = []
	callback = None

	def __init__(self, parent, dlg, cms, image_style, onchange=None):
		self.image_style = deepcopy(image_style)
		self.callback = onchange
		wal.HPanel.__init__(self, parent)

		self.pack(wal.Label(self, _('Fg:')))
		txt = _('Change pattern foreground color')
		self.fg_btn = PDColorButton(self, dlg, cms, self.image_style[0], txt,
								onchange=self.fg_changed)
		self.pack(self.fg_btn, padding=5)

		self.pack((10, 1))

		self.pack(wal.Label(self, _('Bg:')))
		txt = _('Change pattern background color')
		self.bg_btn = PDColorButton(self, dlg, cms, self.image_style[1], txt,
								onchange=self.bg_changed)
		self.pack(self.bg_btn, padding=5)

	def fg_changed(self, color):
		self.image_style[0] = deepcopy(color)
		if self.callback: self.callback(self.get_image_style())

	def bg_changed(self, color):
		self.image_style[1] = deepcopy(color)
		if self.callback: self.callback(self.get_image_style())

	def set_image_style(self, image_style):
		self.image_style = deepcopy(image_style)
		self.fg_btn.set_color(self.image_style[0])
		self.bg_btn.set_color(self.image_style[1])

	def get_image_style(self):
		return deepcopy(self.image_style)


class PatternEditor(wal.HPanel):

	pattern_def = []
	cms = None
	dlg = None
	callback = None

	def __init__(self, parent, dlg, cms, pattern_def, onchange=None):
		self.dlg = dlg
		self.cms = cms
		self.pattern_def = pattern_def
		self.callback = onchange
		wal.HPanel.__init__(self, parent)
		left_panel = wal.VPanel(self)
		self.pattern_swatch = PatternSwatch(left_panel, self.cms, pattern_def)
		left_panel.pack(self.pattern_swatch)
		self.pack(left_panel, fill=True)

		right_panel = wal.VPanel(self)

		self.pattern_color_editor = PatternColorEditor(right_panel, dlg, cms,
								pattern_def[2], onchange=self.color_changed)
		right_panel.pack(self.pattern_color_editor)

		self.pack(right_panel, fill=True, expand=True)

	def color_changed(self, image_style):
		self.pattern_def[2] = image_style
		if self.callback: self.callback(self.get_pattern_def())

	def set_pattern_def(self, pattern_def):
		self.pattern_def = deepcopy(pattern_def)
		self.update()

	def get_pattern_def(self):
		return deepcopy(self.pattern_def)

	def update(self):
		self.pattern_swatch.set_pattern_def(self.pattern_def)
		self.pattern_color_editor.set_image_style(self.pattern_def[2])
