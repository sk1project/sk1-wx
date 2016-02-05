# -*- coding: utf-8 -*-
#
#	Copyright (C) 2016 by Igor E. Novikov
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

from uc2 import libpango

from sk1 import _, events, config

from generic import CtxPlugin

FONT_SIZES = list(range(5, 14)) + list(range(14, 30, 2)) + [32, 36, 40, 48, 56, 64, 72]

class TextStylePlugin(CtxPlugin):

	name = 'TextStylePlugin'
	families = []
	faces_dict = {}

	def __init__(self, app, parent):
		CtxPlugin.__init__(self, app, parent)
		events.connect(events.DOC_CHANGED, self.update)
		events.connect(events.DOC_MODIFIED, self.update)

	def build(self):
		self.families, self.faces_dict = libpango.get_fonts()

		self.families_combo = wal.Combolist(self, items=self.families)
		self.families_combo.set_active(self.families.index('Sans'))
		self.add(self.families_combo, 0, wal.LEFT | wal.CENTER, 2)
		self.add((3, 3))

		self.faces_combo = wal.Combolist(self, items=self.faces_dict['Sans'])
		self.faces_combo.set_active(0)
		self.add(self.faces_combo, 0, wal.LEFT | wal.CENTER, 2)
		self.add((3, 3))

		self.size_combo = wal.FloatCombobox(self, 12, width=5,
										digits=2, items=FONT_SIZES)
		self.add(self.size_combo, 0, wal.LEFT | wal.CENTER, 2)

	def update(self, *args):pass
