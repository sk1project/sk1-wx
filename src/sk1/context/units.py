# -*- coding: utf-8 -*-
#
#	Copyright (C) 2013 by Igor E. Novikov
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

from uc2.uc2const import unit_names, unit_full_names, UNIT_MM

from wal import Combolist, LEFT, CENTER

from sk1 import _, events
from sk1.resources import icons, get_bmp
from generic import CtxPlugin

class UnitsPlugin(CtxPlugin):

	name = 'UnitsPlugin'
	update_flag = False
	units = UNIT_MM

	def __init__(self, app, parent):
		CtxPlugin.__init__(self, app, parent)
		events.connect(events.DOC_CHANGED, self.update)
		events.connect(events.DOC_MODIFIED, self.update)

	def build(self):
		bmp = get_bmp(self, icons.CTX_UNITS, _('Document units'))
		self.add(bmp, 0, LEFT | CENTER, 2)

		self.add((2, 2))

		names = []
		for item in unit_names: names.append(unit_full_names[item])
		self.combo = Combolist(self, items=names, onchange=self.changed)
		self.add(self.combo, 0, LEFT | CENTER, 2)

	def update(self, *args):
		if self.insp.is_doc():
			model = self.app.current_doc.model
			if not model.doc_units == unit_names[self.combo.get_active()]:
				self.units = model.doc_units
				self.combo.set_active(unit_names.index(self.units))

	def changed(self, *args):
		if self.insp.is_doc():
			if not self.units == unit_names[self.combo.get_active()]:
				self.units = unit_names[self.combo.get_active()]
				self.app.current_doc.api.set_doc_units(self.units)
