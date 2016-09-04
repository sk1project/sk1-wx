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

from sk1 import _, config
from sk1.resources import icons, get_bmp
from sk1.printing.cups_staff import CUPS_PS

from generic import PrefPanel

class CUPS_Prefs(PrefPanel):

	pid = 'Printers'
	name = _('Printers')
	title = _('Printer preferences')
	icon_id = icons.PD_PREFS_PRINTERS

	printsys = None
	active_printer = None
	prn_list = []

	def __init__(self, app, dlg, fmt_config=None):
		PrefPanel.__init__(self, app, dlg)

	def build(self):
		self.printsys = CUPS_PS(physial_only=True)
		self.prn_list = self.printsys.get_printer_names()
		if self.prn_list:
			self.active_printer = self.printsys.get_default_printer()
			hpanel = wal.HPanel(self)
			hpanel.pack(wal.Label(hpanel, _('Printer:')))
			hpanel.pack((5, 5))
			self.prn_combo = wal.Combolist(hpanel, items=self.prn_list)
			hpanel.pack(self.prn_combo, fill=True, expand=True)
			index = self.prn_list.index(self.active_printer.get_name())
			self.prn_combo.set_active(index)
			self.pack(hpanel, fill=True, padding_all=5)
		else:
			self.pack((5, 5), expand=True)
			self.pack(get_bmp(self, icons.PD_NO_PRINTERS), padding=10)
			self.pack(wal.Label(self, _('Cannot found installed printers!')))
			self.pack((10, 10))
			self.pack((5, 5), expand=True)
		self.built = True

	def apply_changes(self):
		if not self.prn_list: return
		config.printer_config = {}
		for name in self.prn_list:
			printer = self.printsys.get_printer_by_name(name)
			if printer: printer.save_config()

	def restore_defaults(self):
		if not self.prn_list: return
#		defaults = config.get_defaults()
#		self.filler.set_value(defaults['font_preview_text'])
#		self.fontsize.set_value(defaults['font_preview_size'])
#		self.fontcolor.set_value(defaults['font_preview_color'])
#		self.pwidth.set_value(defaults['font_preview_width'])

