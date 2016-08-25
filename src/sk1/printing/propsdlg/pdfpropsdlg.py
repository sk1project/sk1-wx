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


from generic import PrnProsDialog

class MainTab(wal.VPanel):

	name = _('Main')
	app = None
	printer = None
	panels = []

	def __init__(self, parent, printer, app):
		self.app = app
		self.printer = printer
		wal.VPanel.__init__(self, parent)

	def save(self):
		for item in self.panels: item.save()

class PDF_PrnPropsDialog(PrnProsDialog):

	def build(self):
		PrnProsDialog.build(self)
		self.panel.pack((5, 5))
		self.main_tab = MainTab(self.panel, self.printer, self.app)
		self.panel.pack(self.main_tab, fill=True, expand=True)

	def get_result(self):
		self.main_tab.save()
		return True
