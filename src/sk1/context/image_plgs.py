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

from wal import LEFT, CENTER

from sk1.resources import pdids
from sk1.pwidgets import ActionButton
from generic import CtxPlugin

class ImageTypePlugin(CtxPlugin):

	name = 'ImageTypePlugin'

	def __init__(self, app, parent):
		CtxPlugin.__init__(self, app, parent)

	def build(self):
		for item in [pdids.ID_CONV_TO_CMYK,
					pdids.ID_CONV_TO_RGB,
#					pdids.ID_CONV_TO_LAB,
					pdids.ID_CONV_TO_GRAY,
					pdids.ID_CONV_TO_BW]:
			self.add(ActionButton(self, self.actions[item]), 0, LEFT | CENTER, 2)
