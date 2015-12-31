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

from uc2 import uc2const
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
	user_changes = False

	def __init__(self, parent, app, onreset=None):
		self.app = app
		self.callback = onreset
		wal.VPanel.__init__(self, parent)
		self.pack(wal.Label(self, self.name, fontbold=True), padding_all=5)
		self.build()

	def on_reset(self):
		self.orientation = (0.0, 0.0)
		self.user_changes = True
		if self.callback: self.callback()

	def build(self):pass

	def update(self):pass

	def set_enable(self, state):pass

	def set_orientation(self, orientation=(0.0, 0.0)):
		self.orientation = orientation
		self.user_changes = False
		self.update()

	def get_trafo(self):
		return [] + sk2_const.NORMAL_TRAFO

	def get_selection_bbox(self):
		doc = self.app.current_doc
		return [] + doc.selection.bbox

	def is_ll_coords(self):
		doc = self.app.current_doc
		return doc.methods.get_doc_origin() == sk2_const.DOC_ORIGIN_LL

	def is_lu_coords(self):
		doc = self.app.current_doc
		return doc.methods.get_doc_origin() == sk2_const.DOC_ORIGIN_LU

	def is_center_coords(self):
		doc = self.app.current_doc
		return doc.methods.get_doc_origin() == sk2_const.DOC_ORIGIN_CENTER

	def get_page_size(self):
		page_format = self.app.current_doc.active_page.page_format
		w, h = page_format[1]
		if page_format[2] == uc2const.LANDSCAPE:
			return (max(w, h), min(w, h))
		else:
			return (min(w, h), max(w, h))

class PositionTransform(AbstractTransform):

	name = _('Position')
	dx = 0.0
	dy = 0.0

	def build(self):
		grid = wal.GridPanel(self, 2, 3, 2, 2)

		grid.pack(get_bmp(grid, make_artid('h-sign')))
		self.h_spin = UnitSpin(self.app, grid, can_be_negative=True,
							onchange=self.on_reset)
		grid.pack(self.h_spin)
		grid.pack(UnitLabel(self.app, grid))

		grid.pack(get_bmp(grid, make_artid('v-sign')))
		self.v_spin = UnitSpin(self.app, grid, can_be_negative=True,
							onchange=self.on_reset)
		grid.pack(self.v_spin)
		grid.pack(UnitLabel(self.app, grid))

		self.pack(grid, align_center=False, padding=5)
		self.abs_pos = wal.Checkbox(self, _('Absolute position'),
								onclick=self.update)
		self.pack(self.abs_pos, align_center=False, padding=5)

	def set_enable(self, state):
		self.h_spin.set_enable(state)
		self.v_spin.set_enable(state)
		self.abs_pos.set_enable(state)
		if state: self.update()

	def update(self):
		if not self.app.insp.is_selection():return
		if self.user_changes: return
		bbox = self.get_selection_bbox()
		w = bbox[2] - bbox[0]
		h = bbox[3] - bbox[1]
		dx = self.orientation[0] * w
		dy = self.orientation[1] * h
		if self.is_lu_coords() and dy: dy *= -1.0
		if self.abs_pos.get_value():
			pw, ph = self.get_page_size()
#			self.h_spin.set_point_value(dx)
#			self.v_spin.set_point_value(dy)
		else:
			self.h_spin.set_point_value(dx)
			self.v_spin.set_point_value(dy)

	def get_trafo(self):
		trafo = [] + sk2_const.NORMAL_TRAFO
		trafo[4] = self.h_spin.get_point_value()
		trafo[5] = self.v_spin.get_point_value()
		if self.is_lu_coords() and trafo[5]: trafo[5] *= -1.0
		return trafo

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

	def set_enable(self, state):
		self.h_spin.set_enable(state)
		self.v_spin.set_enable(state)
		self.proportion.set_enable(state)

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

	def set_enable(self, state):
		self.h_spin.set_enable(state)
		self.h_mirror.set_enable(state)
		self.v_spin.set_enable(state)
		self.v_mirror.set_enable(state)
		self.proportion.set_enable(state)

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

	def set_enable(self, state):
		self.angle.set_enable(state)
		self.h_spin.set_enable(state)
		self.v_spin.set_enable(state)
		self.center.set_enable(state)


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

	def set_enable(self, state):
		self.h_shear.set_enable(state)
		self.v_shear.set_enable(state)
