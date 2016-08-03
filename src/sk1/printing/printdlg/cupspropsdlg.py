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

from sk1 import _, config
from sk1.resources import get_icon, icons

from generic import PrnProsDialog

class MaintenanceTab(wal.VPanel):

	name = _('Maintenance')
	printer = None

	def __init__(self, parent, printer):
		self.printer = printer
		wal.VPanel.__init__(self, parent)

	def save(self):pass

class PaperTab(wal.VPanel):

	name = _('Paper')
	printer = None

	def __init__(self, parent, printer):
		self.printer = printer
		wal.VPanel.__init__(self, parent)

	def save(self):pass

class MainTab(wal.VPanel):

	name = _('Main')
	printer = None

	def __init__(self, parent, printer):
		self.printer = printer
		wal.VPanel.__init__(self, parent)

		hpanel = wal.HPanel(self)
		icon_name = icons.PD_PRINTER_LASER
		if self.printer.is_color(): icon_name = icons.PD_PRINTER_INKJET
		icon = get_icon(icon_name, size=wal.DEF_SIZE)
		hpanel.pack(wal.Bitmap(hpanel, icon), padding_all=10)
		self.pack(hpanel, fill=True)

	def save(self):pass


class CUPS_PrnPropsDialog(PrnProsDialog):

	tabs = []

	def build(self):
		PrnProsDialog.build(self)
		self.panel.pack((5, 5))
		self.tabs = []
		self.nb = wal.Notebook(self.panel)
		cls = (MainTab, PaperTab, MaintenanceTab)
		for item in cls:
			tab = item(self.nb, self.printer)
			self.nb.add_page(tab, tab.name)
			self.tabs.append(tab)
		self.panel.pack(self.nb, fill=True, expand=True)

	def get_result(self):
		for item in self.tabs: item.save()
		return True



class PDF_PrnPropsDialog(PrnProsDialog):pass
