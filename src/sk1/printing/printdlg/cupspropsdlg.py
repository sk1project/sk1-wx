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

from uc2 import uc2const

from sk1 import _
from sk1.resources import get_icon, icons

from generic import PrnProsDialog

CS = [uc2const.COLOR_GRAY, uc2const.COLOR_CMYK, uc2const.COLOR_RGB]

class PrintModePanel(wal.LabeledPanel):

	printer = None

	def __init__(self, parent, printer):
		self.printer = printer
		wal.LabeledPanel.__init__(self, parent, _('Print mode'))

		self.pack((5, 5))

		grid = wal.GridPanel(self, 2, 2, 5, 5)

		self.mono_opt = wal.Radiobutton(grid, _('Monochrome'), group=True,
									onclick=self.update)
		icon = get_icon(icons.PD_PRINTMODE_MONO, size=wal.DEF_SIZE)
		self.mono_bmp = wal.Bitmap(grid, icon)
		grid.pack(self.mono_bmp)
		grid.pack(self.mono_opt)

		self.color_opt = wal.Radiobutton(grid, _('Color'), onclick=self.update)
		icon = get_icon(icons.PD_PRINTMODE_COLOR, size=wal.DEF_SIZE)
		self.color_bmp = wal.Bitmap(grid, icon)
		grid.pack(self.color_bmp)
		grid.pack(self.color_opt)
		self.color_opt.set_value(True)

		self.pack(grid, padding_all=10, align_center=False)

		hpanel = wal.HPanel(self)

		self.cs_lbl = wal.Label(hpanel, _('Color space:'))
		hpanel.pack(self.cs_lbl, padding=5)

		self.cs_combo = wal.Combolist(hpanel, items=CS)
		hpanel.pack(self.cs_combo)

		self.pack(hpanel)

		self.set_data()

	def set_data(self):
		self.cs_combo.set_active(CS.index(self.printer.colorspace))
		if not self.printer.is_color():
			self.mono_opt.set_value(True)
			self.color_opt.set_enable(False)
			self.color_bmp.set_enable(False)
			self.cs_combo.set_enable(False)

	def update(self):
		if self.mono_opt.get_value():
			self.cs_combo.set_active(0)
			self.cs_combo.set_enable(False)
		else:
			self.cs_combo.set_enable(True)
			self.cs_combo.set_active(1)

	def save(self):pass


class MainTab(wal.VPanel):

	name = _('Main')
	printer = None
	panels = []

	def __init__(self, parent, printer):
		self.printer = printer
		wal.VPanel.__init__(self, parent)

		hpanel = wal.HPanel(self)
		icon_name = icons.PD_PRINTER_LASER
		if self.printer.is_color(): icon_name = icons.PD_PRINTER_INKJET
		icon = get_icon(icon_name, size=wal.DEF_SIZE)
		hpanel.pack(wal.Bitmap(hpanel, icon), padding_all=10)

		self.prnmode_panel = PrintModePanel(hpanel, self.printer)
		hpanel.pack(self.prnmode_panel, fill=True, expand=True)

		self.pack(hpanel, fill=True)

	def save(self):
		for item in self.panel: item.save()


class CUPS_PrnPropsDialog(PrnProsDialog):

	tabs = []

	def build(self):
		PrnProsDialog.build(self)
		self.panel.pack((5, 5))
		self.main_tab = MainTab(self.panel, self.printer)
		self.panel.pack(self.main_tab, fill=True, expand=True)

	def get_result(self):
		self.main_tab.save()
		return True



class PDF_PrnPropsDialog(PrnProsDialog):pass
