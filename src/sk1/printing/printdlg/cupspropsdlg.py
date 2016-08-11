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
from sk1.pwidgets import StaticUnitLabel, StaticUnitSpin

from generic import PrnProsDialog

CS = [uc2const.COLOR_GRAY, uc2const.COLOR_CMYK, uc2const.COLOR_RGB]

class PrintModePanel(wal.LabeledPanel):

	printer = None

	def __init__(self, parent, printer):
		self.printer = printer
		wal.LabeledPanel.__init__(self, parent, _('Print mode'))

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

		self.pack((5, 5))

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

class PaperPanel(wal.LabeledPanel):

	app = None
	printer = None
	items = []

	def __init__(self, parent, printer, app):
		self.app = app
		self.printer = printer
		wal.LabeledPanel.__init__(self, parent, _('Paper'))

		grid = wal.GridPanel(self, 2, 2, 5, 5)
		grid.add_growable_col(1)

		grid.pack(wal.Label(grid, _('Page size:')))

		self.size_combo = wal.Combolist(grid, onchange=self.on_change)
		grid.pack(self.size_combo, fill=True)

		grid.pack(wal.Label(grid, _('Width:')))

		hpanel = wal.HPanel(grid)

		self.wspin = StaticUnitSpin(self.app, hpanel)
		hpanel.pack(self.wspin)
		hpanel.pack(StaticUnitLabel(self.app, hpanel), padding=5)

		hpanel.pack((5, 5))

		hpanel.pack(wal.Label(grid, _('Height:')), padding=5)

		self.hspin = StaticUnitSpin(self.app, hpanel)
		hpanel.pack(self.hspin)
		hpanel.pack(StaticUnitLabel(self.app, hpanel), padding=5)

		grid.pack(hpanel)

		self.pack(grid, fill=True, expand=True, padding_all=10)

		self.set_data()

	def set_data(self):
		self.items = self.printer.get_format_items()
		self.size_combo.set_items(self.items)
		index = 0
		if not self.printer.def_media[:6] == 'Custom':
			index = self.printer.pf_list.index(self.printer.def_media)
		else:
			index = len(self.items) - 1
		self.size_combo.set_active(index)
		if self.printer.is_custom_supported():
			minw, minh = self.printer.customs[0]
			maxw, maxh = self.printer.customs[1]
			self.wspin.set_point_range((minw, maxw))
			self.hspin.set_point_range((minh, maxh))
		self.on_change()

	def on_change(self):
		index = self.size_combo.get_active()
		status = False
		if self.printer.is_custom_supported() and index == len(self.items) - 1:
			if not self.hspin.get_point_value() and \
			self.printer.def_media[:6] == 'Custom':
				w, h = self.printer.def_media[:7].split('x')
				w = float(w)
				h = float(h)
				self.wspin.set_point_value(w)
				self.hspin.set_point_value(h)
			status = True
		else:
			w, h = self.printer.pf_dict[self.printer.pf_list[index]][1]
			self.wspin.set_point_value(w)
			self.hspin.set_point_value(h)
		self.wspin.set_enable(status)
		self.hspin.set_enable(status)

	def save(self):pass


class OrientPanel(wal.LabeledPanel):

	app = None
	printer = None
	items = []

	def __init__(self, parent, printer, app):
		self.app = app
		self.printer = printer
		wal.LabeledPanel.__init__(self, parent, _('Orientation'))

		hpanel = wal.HPanel(self)

		vpanel = wal.VPanel(hpanel)
		self.port_opt = wal.Radiobutton(vpanel, _('Portrait'), group=True,
									onclick=self.update)
		vpanel.pack(self.port_opt, align_center=False)
		vpanel.pack((5, 5))
		self.land_opt = wal.Radiobutton(vpanel, _('Landscape'),
									onclick=self.update)
		vpanel.pack(self.land_opt, align_center=False)

		hpanel.pack(vpanel)

		self.pack(hpanel, fill=True, expand=True, padding_all=10)

	def update(self):pass

	def save(self):pass

class MarginsPanel(wal.LabeledPanel):

	app = None
	printer = None
	items = []

	def __init__(self, parent, printer, app):
		self.app = app
		self.printer = printer
		units = app.current_doc.model.doc_units
		text = uc2const.unit_short_names[units]

		wal.LabeledPanel.__init__(self, parent, _('Margins') + ' (%s)' % text)

		self.pack(wal.VPanel(self), expand=True, padding=2)

		mrgs = self.printer.margins
		self.top_spin = StaticUnitSpin(self.app, self, mrgs[0])
		self.pack(self.top_spin)

		self.pack((5, 5))

		hpanel = wal.HPanel(self)
		self.right_spin = StaticUnitSpin(self.app, self, mrgs[1])
		hpanel.pack(self.right_spin)
		hpanel.pack((5, 5))
		self.bottom_spin = StaticUnitSpin(self.app, self, mrgs[2])
		hpanel.pack(self.bottom_spin)

		self.pack(hpanel)

		self.pack((5, 5))

		self.left_spin = StaticUnitSpin(self.app, self, mrgs[3])
		self.pack(self.left_spin)

		self.pack(wal.VPanel(self), expand=True, padding=2)

	def save(self):pass

class MainTab(wal.VPanel):

	name = _('Main')
	app = None
	printer = None
	panels = []

	def __init__(self, parent, printer, app):
		self.app = app
		self.printer = printer
		wal.VPanel.__init__(self, parent)

		hpanel = wal.HPanel(self)
		icon_name = icons.PD_PRINTER_LASER
		if self.printer.is_color(): icon_name = icons.PD_PRINTER_INKJET
		icon = get_icon(icon_name, size=wal.DEF_SIZE)
		hpanel.pack(wal.Bitmap(hpanel, icon), padding=10)

		self.prnmode_panel = PrintModePanel(hpanel, self.printer)
		hpanel.pack(self.prnmode_panel, fill=True, expand=True)

		self.pack(hpanel, fill=True)

		self.pack((5, 5))

		self.paper_panel = PaperPanel(self, self.printer, self.app)
		self.pack(self.paper_panel, fill=True)

		self.pack((5, 5))

		hpanel = wal.HPanel(self)
		self.orient_panel = OrientPanel(hpanel, self.printer, self.app)
		hpanel.pack(self.orient_panel, fill=True, expand=True)

		hpanel.pack((5, 5))

		self.margins_panel = MarginsPanel(hpanel, self.printer, self.app)
		hpanel.pack(self.margins_panel, fill=True, expand=True)

		self.pack(hpanel, fill=True, expand=True)

		text = _("Note: To adjust specific printer options "
			"you could "
			"use system configuration tools like 'system-config-printer'")

		label = wal.Label(self, text, fontsize=-2)
		if wal.is_msw(): label.wrap(380)
		label.set_enable(False)
		self.pack(label, fill=True, padding_all=5, align_center=False)


	def save(self):
		for item in self.panels: item.save()


class CUPS_PrnPropsDialog(PrnProsDialog):

	tabs = []

	def build(self):
		PrnProsDialog.build(self)
		self.panel.pack((5, 5))
		self.main_tab = MainTab(self.panel, self.printer, self.app)
		self.panel.pack(self.main_tab, fill=True, expand=True)

	def get_result(self):
		self.main_tab.save()
		return True



class PDF_PrnPropsDialog(PrnProsDialog):pass
