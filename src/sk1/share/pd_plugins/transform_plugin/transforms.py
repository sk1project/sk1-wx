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

import wal

from uc2.formats.sk2 import sk2_const
from sk1 import _

class AbstractTransform(wal.VPanel):

	name = 'Transform'
	app = None
	orientation = (0.5, 0.5)

	def __init__(self, parent, app):
		self.app = app
		wal.VPanel.__init__(self, parent, border=True)
		self.pack(wal.Label(self, self.name, fontbold=True), padding_all=5)
		self.build()

	def build(self):pass

	def update(self):pass

	def set_enable(self, state):pass

	def set_orientation(self, orientation=(0.5, 0.5)):
		self.orientation = orientation
		self.update()

	def get_trafo(self):
		return [] + sk2_const.NORMAL_TRAFO


class PositionTransform(AbstractTransform):

	name = _('Position')

class ResizeTransform(AbstractTransform):

	name = _('Resizing')

class ScaleTransform(AbstractTransform):

	name = _('Scale and mirror')

class RotateTransform(AbstractTransform):

	name = _('Rotation')

class ShearTransform(AbstractTransform):

	name = _('Shearing')
