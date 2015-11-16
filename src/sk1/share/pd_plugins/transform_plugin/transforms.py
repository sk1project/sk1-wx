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

import os, wal

from uc2.formats.sk2 import sk2_const
from sk1 import _
from sk1.resources import get_bmp
from sk1.pwidgets import UnitSpin, UnitLabel, AngleSpin

PLG_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(PLG_DIR, 'images')

def make_artid(name):
	return os.path.join(IMG_DIR, name + '.png')

class AbstractTransform(wal.VPanel):

	name = 'Transform'
	app = None
	orientation = (0.0, 0.0)
	callback = None

	def __init__(self, parent, app, onreset=None):
		self.app = app
		self.callback = onreset
		wal.VPanel.__init__(self, parent)
		self.pack(wal.Label(self, self.name, fontbold=True), padding_all=5)
		self.build()

	def build(self):pass

	def update(self):pass

	def set_enable(self, state):pass

	def set_orientation(self, orientation=(0.0, 0.0)):
		self.orientation = orientation
		self.update()

	def get_trafo(self):
		return [] + sk2_const.NORMAL_TRAFO


class PositionTransform(AbstractTransform):

	name = _('Position')

	def build(self):
		grid = wal.GridPanel(self, 2, 3, 2, 2)

		grid.pack(get_bmp(grid, make_artid('h-sign')))
		self.h_spin = UnitSpin(self.app, grid)
		grid.pack(self.h_spin)
		grid.pack(UnitLabel(self.app, grid))

		grid.pack(get_bmp(grid, make_artid('v-sign')))
		self.v_spin = UnitSpin(self.app, grid)
		grid.pack(self.v_spin)
		grid.pack(UnitLabel(self.app, grid))

		self.pack(grid, align_center=False, padding=5)
		self.abs_pos = wal.Checkbox(self, _('Absolute position'))
		self.pack(self.abs_pos, align_center=False, padding=5)

class ResizeTransform(AbstractTransform):

	name = _('Resizing')

	def build(self):
		grid = wal.GridPanel(self, 2, 3, 2, 2)

		grid.pack(get_bmp(grid, make_artid('h-sign')))
		self.h_spin = UnitSpin(self.app, grid)
		grid.pack(self.h_spin)
		grid.pack(UnitLabel(self.app, grid))

		grid.pack(get_bmp(grid, make_artid('v-sign')))
		self.v_spin = UnitSpin(self.app, grid)
		grid.pack(self.v_spin)
		grid.pack(UnitLabel(self.app, grid))

		self.pack(grid, align_center=False, padding=5)
		self.proportion = wal.Checkbox(self, _('Keep ratio'), True)
		self.pack(self.proportion, align_center=False, padding=5)

class ScaleTransform(AbstractTransform):

	name = _('Scale and mirror')

	def build(self):
		grid = wal.GridPanel(self, 2, 5, 2, 2)

		grid.pack(get_bmp(grid, make_artid('h-sign')))
		self.h_spin = wal.FloatSpin(grid, 100.0, (0.0, 10000.0), 1.0)
		grid.pack(self.h_spin)
		grid.pack(wal.Label(grid, '%'))
		grid.pack((5, 5))
		self.h_mirror = wal.ImageToggleButton(grid, False,
					make_artid('h-mirror'), tooltip=_('Horizontal mirror'),
					flat=False)
		grid.pack(self.h_mirror)

		grid.pack(get_bmp(grid, make_artid('v-sign')))
		self.v_spin = wal.FloatSpin(grid, 100.0, (0.0, 10000.0), 1.0)
		grid.pack(self.v_spin)
		grid.pack(wal.Label(grid, '%'))
		grid.pack((5, 5))
		self.v_mirror = wal.ImageToggleButton(grid, False,
					make_artid('v-mirror'), tooltip=_('Vertical mirror'),
					flat=False)
		grid.pack(self.v_mirror)

		self.pack(grid, align_center=False, padding=5)
		self.proportion = wal.Checkbox(self, _('Keep ratio'), True)
		self.pack(self.proportion, align_center=False, padding=5)

class RotateTransform(AbstractTransform):

	name = _('Rotation')

	def build(self):
		grid = wal.GridPanel(self, 1, 3, 2, 2)

		grid.pack(wal.Label(grid, _('Angle:')))
		self.angle = AngleSpin(grid, val_range=(-89.0, 89.0))
		grid.pack(self.angle)
		grid.pack(wal.Label(grid, _('degrees')))

		self.pack(grid, align_center=False, padding=5)
		self.pack(wal.Label(grid, _('Center:')), align_center=False, padding=5)

		grid = wal.GridPanel(self, 2, 3, 2, 2)

		grid.pack(get_bmp(grid, make_artid('h-sign')))
		self.h_spin = UnitSpin(self.app, grid)
		grid.pack(self.h_spin)
		grid.pack(UnitLabel(self.app, grid))

		grid.pack(get_bmp(grid, make_artid('v-sign')))
		self.v_spin = UnitSpin(self.app, grid)
		grid.pack(self.v_spin)
		grid.pack(UnitLabel(self.app, grid))

		self.pack(grid, align_center=False, padding_all=5)
		self.center = wal.Checkbox(self, _('Relative center'))
		self.pack(self.center, align_center=False, padding=5)


class ShearTransform(AbstractTransform):

	name = _('Shearing')

	def build(self):
		grid = wal.GridPanel(self, 3, 3, 2, 2)

		grid.pack(get_bmp(grid, make_artid('h-sign')))
		self.h_shear = AngleSpin(grid, val_range=(-89.0, 89.0))
		grid.pack(self.h_shear)
		grid.pack(wal.Label(grid, _('degrees')))

		grid.pack(get_bmp(grid, make_artid('v-sign')))
		self.v_shear = AngleSpin(grid, val_range=(-89.0, 89.0))
		grid.pack(self.v_shear)
		grid.pack(wal.Label(grid, _('degrees')))

		self.pack(grid, align_center=False, padding=5)
