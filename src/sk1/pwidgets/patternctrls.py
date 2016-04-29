# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2015 by Igor E. Novikov
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

import math
from copy import deepcopy

import wal

from uc2 import libgeom, libimg
from uc2.formats.sk2 import sk2_const

from sk1 import _
from sk1.resources import icons, get_bmp

from colorctrls import SwatchCanvas
from patterns import PATTERN_PRESETS
from colorbtn import PDColorButton
from unitctrls import UnitSpin, StaticUnitLabel

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


class TransformEditor(wal.VPanel):

	app = None
	callback = None
	transforms = []


	def __init__(self, parent, app, trafo=[] + sk2_const.NORMAL_TRAFO,
				transforms=[] + sk2_const.PATTERN_TRANSFORMS, onchange=None):
		self.app = app
		self.callback = onchange
		wal.VPanel.__init__(self, parent)

		grid = wal.GridPanel(self, 3, 7, 3, 2)

		#---Origin X
		txt = _('Horizontal origin shift')
		grid.pack(get_bmp(grid, icons.PD_PATTERN_ORIGIN_X, txt))
		self.origin_x = UnitSpin(app, grid, can_be_negative=True,
								onchange=self.changes, onenter=self.changes)
		grid.pack(self.origin_x)
		grid.pack(StaticUnitLabel(app, grid))

		grid.pack((10, 5))

		#---Origin Y
		txt = _('Vertical origin shift')
		grid.pack(get_bmp(grid, icons.PD_PATTERN_ORIGIN_Y, txt))
		self.origin_y = UnitSpin(app, grid, can_be_negative=True,
								onchange=self.changes, onenter=self.changes)
		grid.pack(self.origin_y)
		grid.pack(StaticUnitLabel(app, grid))

		#---Scale X
		txt = _('Scale horizontally')
		grid.pack(get_bmp(grid, icons.PD_PATTERN_SCALE_X, txt))
		self.scale_x = wal.FloatSpin(grid, range_val=(-1000000.0, 1000000.0),
								step=1.0, width=5,
								onchange=self.changes, onenter=self.changes)
		grid.pack(self.scale_x)
		grid.pack(wal.Label(grid, '%'))

		grid.pack((10, 5))

		#---Scale Y
		txt = _('Scale vertically')
		grid.pack(get_bmp(grid, icons.PD_PATTERN_SCALE_Y, txt))
		self.scale_y = wal.FloatSpin(grid, range_val=(-1000000.0, 1000000.0),
								step=1.0, width=5,
								onchange=self.changes, onenter=self.changes)
		grid.pack(self.scale_y)
		grid.pack(wal.Label(grid, '%'))

		#---Shear X
		txt = _('Shear horizontally')
		grid.pack(get_bmp(grid, icons.PD_PATTERN_SHEAR_X, txt))
		self.shear_x = wal.FloatSpin(grid, range_val=(0.0, 85.0),
						step=1.0, width=5,
						onchange=self.changes, onenter=self.changes)
		grid.pack(self.shear_x)
		grid.pack(wal.Label(grid, _('deg')))

		grid.pack((10, 5))

		#---Shear X
		txt = _('Shear vertically')
		grid.pack(get_bmp(grid, icons.PD_PATTERN_SHEAR_Y, txt))
		self.shear_y = wal.FloatSpin(grid, range_val=(0.0, 85.0),
						step=1.0, width=5,
						onchange=self.changes, onenter=self.changes)
		grid.pack(self.shear_y)
		grid.pack(wal.Label(grid, _('deg')))

		self.pack(grid)

		#---Rotate
		rot_panel = wal.HPanel(self)
		txt = _('Rotate pattern')
		rot_panel.pack(get_bmp(rot_panel, icons.PD_PATTERN_ROTATE, txt))
		self.rotate = wal.FloatSpin(rot_panel, range_val=(-360.0, 360.0),
						step=1.0, width=5,
						onchange=self.changes, onenter=self.changes)
		rot_panel.pack(self.rotate, padding=3)
		rot_panel.pack(wal.Label(rot_panel, '°'))

		self.pack(rot_panel, padding=5)

		self.set_trafo(trafo, transforms)

	def set_trafo(self, trafo, transforms):
		x0, y0 = trafo[-2:]
		sx, sy, shx, shy, rotate = transforms
		self.origin_x.set_point_value(x0)
		self.origin_y.set_point_value(y0)
		self.scale_x.set_value(sx * 100.0)
		self.scale_y.set_value(sy * 100.0)
		self.shear_x.set_value(shx * 180.0 / math.pi)
		self.shear_y.set_value(shy * 180.0 / math.pi)
		self.rotate.set_value(rotate * 180.0 / math.pi)
		self.transforms = transforms

	def get_trafo(self):
		x0 = self.origin_x.get_point_value()
		y0 = self.origin_y.get_point_value()
		sx = self.scale_x.get_value() / 100.0
		sy = self.scale_y.get_value() / 100.0
		shx = self.shear_x.get_value()
		shy = self.shear_y.get_value()

		if shx + shy > 85:
			if shx == self.transforms[3]: shy = 85 - shx
			else: shx = 85 - shy

		shx = math.pi * shx / 180.0
		shy = math.pi * shy / 180.0

		angle = math.pi * self.rotate.get_value() / 180.0

		trafo = [sx, 0.0, 0.0, sy, x0, y0]
		if angle:
			trafo2 = [math.cos(angle), math.sin(angle),
					- math.sin(angle), math.cos(angle), 0.0, 0.0]
			trafo = libgeom.multiply_trafo(trafo, trafo2)
		if shx or shy:
			trafo2 = [1.0, math.tan(shy), math.tan(shx), 1.0, 0.0, 0.0]
			trafo = libgeom.multiply_trafo(trafo, trafo2)

		self.transforms = [sx, sy, shx, shy, angle]
		return trafo, [sx, sy, shx, shy, angle]

	def changes(self, *args):
		if self.callback: self.callback(*self.get_trafo())

class TrafoEditor(wal.VPanel):

	app = None
	callback = None

	def __init__(self, parent, app, trafo=[] + sk2_const.NORMAL_TRAFO,
				onchange=None):
		self.app = app
		self.callback = onchange
		wal.VPanel.__init__(self, parent)

		self.pack(wal.Label(self, _('Transformation matrix:')), padding=5)

		grid = wal.GridPanel(self, 3, 5, 3, 1)

		#---M11
		grid.pack(wal.Label(grid, 'm11:'))
		self.m11 = wal.FloatSpin(grid, range_val=(-1000000.0, 1000000.0),
								step=0.01, width=7,
								onchange=self.changes, onenter=self.changes)
		grid.pack(self.m11)

		grid.pack((5, 5))

		#---M12
		grid.pack(wal.Label(grid, 'm12:'))
		self.m12 = wal.FloatSpin(grid, range_val=(-1000000.0, 1000000.0),
								step=0.01, width=7,
								onchange=self.changes, onenter=self.changes)
		grid.pack(self.m12)

		#---M21
		grid.pack(wal.Label(grid, 'm21:'))
		self.m21 = wal.FloatSpin(grid, range_val=(-1000000.0, 1000000.0),
								step=0.01, width=7,
								onchange=self.changes, onenter=self.changes)
		grid.pack(self.m21)

		grid.pack((5, 5))

		#---M22
		grid.pack(wal.Label(grid, 'm22:'))
		self.m22 = wal.FloatSpin(grid, range_val=(-1000000.0, 1000000.0),
								step=0.01, width=7,
								onchange=self.changes, onenter=self.changes)
		grid.pack(self.m22)

		#---dx
		grid.pack(wal.Label(grid, 'dx:'))
		self.dx = wal.FloatSpin(grid, range_val=(-1000000.0, 1000000.0),
								step=0.01, width=7,
								onchange=self.changes, onenter=self.changes)
		grid.pack(self.dx)

		grid.pack((5, 5))

		#---dy
		grid.pack(wal.Label(grid, 'dy:'))
		self.dy = wal.FloatSpin(grid, range_val=(-1000000.0, 1000000.0),
								step=0.01, width=7,
								onchange=self.changes, onenter=self.changes)
		grid.pack(self.dy)

		self.pack(grid)


	def set_trafo(self, trafo, transforms):
		self.m11.set_value(trafo[0])
		self.m12.set_value(trafo[1])
		self.m21.set_value(trafo[2])
		self.m22.set_value(trafo[3])
		self.dx.set_value(trafo[4])
		self.dy.set_value(trafo[5])

	def get_trafo(self):
		m11 = self.m11.get_value()
		m12 = self.m12.get_value()
		m21 = self.m21.get_value()
		m22 = self.m22.get_value()
		dx = self.dx.get_value()
		dy = self.dy.get_value()
		return [m11, m12, m21, m22, dx, dy], []

	def changes(self, *args):
		if self.callback: self.callback(*self.get_trafo())


class PatternTrafoEditor(wal.VPanel):

	app = None
	callback = None
	transforms = []
	active_panel = None


	def __init__(self, parent, app, trafo=[] + sk2_const.NORMAL_TRAFO,
				transforms=[], onchange=None):
		wal.VPanel.__init__(self, parent)
		self.transfom_editor = TransformEditor(self, app,
											onchange=onchange)
		self.trafo_editor = TrafoEditor(self, app,
											onchange=onchange)
		self.transfom_editor.set_visible(False)
		self.pack(self.trafo_editor)
		self.active_panel = self.trafo_editor

	def set_trafo(self, trafo, transforms):
		if not transforms:
			m11, m12, m21, m22 = trafo[:4]
			if not m12 and not m21:
				transforms = [m11, m22, 0.0, 0.0, 0.0]
		if transforms:
			if not self.active_panel == self.transfom_editor:
				self.remove(self.active_panel)
				self.active_panel.set_visible(False)
				self.active_panel = self.transfom_editor
				self.pack(self.transfom_editor)
				self.active_panel.set_visible(True)
		else:
			if not self.active_panel == self.trafo_editor:
				self.remove(self.active_panel)
				self.active_panel.set_visible(False)
				self.active_panel = self.trafo_editor
				self.pack(self.active_panel)
				self.active_panel.set_visible(True)
		self.active_panel.set_trafo(trafo, transforms)

class PatternEditor(wal.HPanel):

	pattern_def = []
	cms = None
	dlg = None
	callback = None

	def __init__(self, parent, dlg, cms, pattern_def, onchange=None):
		self.dlg = dlg
		self.app = dlg.app
		self.cms = cms
		self.pattern_def = deepcopy(pattern_def)
		self.callback = onchange
		wal.HPanel.__init__(self, parent)
		left_panel = wal.VPanel(self)
		self.pattern_swatch = PatternSwatch(left_panel, self.cms, pattern_def)
		left_panel.pack(self.pattern_swatch)

		button_panel = wal.HPanel(left_panel)
		txt = _('Load pattern from file')
		button_panel.pack(wal.ImageButton(self, icons.PD_OPEN, wal.SIZE_16,
				tooltip=txt, flat=False, onclick=self.load_pattern),
				padding=1)
		txt = _('Save pattern into file')
		button_panel.pack(wal.ImageButton(self, icons.PD_FILE_SAVE, wal.SIZE_16,
				tooltip=txt, flat=False, onclick=self.save_pattern),
				padding=1)
		left_panel.pack(button_panel, padding=2)

		self.pack(left_panel, fill=True)

		right_panel = wal.VPanel(self)

		self.pattern_color_editor = PatternColorEditor(right_panel, dlg, cms,
								pattern_def[2], onchange=self.color_changed)
		right_panel.pack(self.pattern_color_editor, padding=5)

		self.trafo_editor = PatternTrafoEditor(right_panel, dlg.app,
											onchange=self.trafo_changed)
		right_panel.pack(self.trafo_editor, padding=5)

		self.pack(right_panel, fill=True, expand=True)

	def color_changed(self, image_style):
		self.pattern_def[2] = image_style
		if self.callback: self.callback(self.get_pattern_def())

	def trafo_changed(self, trafo, transforms=[]):
		self.pattern_def[3] = trafo
		self.pattern_def[4] = transforms
		if self.callback: self.callback(self.get_pattern_def())

	def set_pattern_def(self, pattern_def):
		self.pattern_def = deepcopy(pattern_def)
		self.update()

	def get_pattern_def(self):
		return deepcopy(self.pattern_def)

	def update(self):
		self.pattern_swatch.set_pattern_def(self.pattern_def)
		self.pattern_color_editor.set_image_style(self.pattern_def[2])
		self.trafo_editor.set_trafo(self.pattern_def[3], self.pattern_def[4])
		self.pattern_color_editor.set_visible(self.pattern_def[0] == sk2_const.PATTERN_IMG)

	def load_pattern(self):
		img_file = self.app.import_pattern(self.dlg)
		if img_file:
			fobj = open(img_file, 'rb')
			pattern, flag = libimg.read_pattern(fobj.read())
			pattern_type = sk2_const.PATTERN_TRUECOLOR
			if flag:
				pattern_type = sk2_const.PATTERN_IMG
				if flag == 'EPS':
					pattern_type = sk2_const.PATTERN_EPS
			self.pattern_def[0] = pattern_type
			self.pattern_def[1] = pattern
			if self.callback: self.callback(self.get_pattern_def())

	def save_pattern(self):
		self.app.extract_pattern(self.dlg, self.pattern_def[1],
								self.pattern_def[0] == sk2_const.PATTERN_EPS)

