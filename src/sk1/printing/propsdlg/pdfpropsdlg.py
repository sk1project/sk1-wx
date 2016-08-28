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
from uc2.formats.pdf import pdfconst

from sk1 import _
from sk1.resources import get_icon, icons
from sk1.pwidgets import StaticUnitLabel, StaticUnitSpin

from generic import PrnProsDialog

CS = [uc2const.COLOR_GRAY, uc2const.COLOR_CMYK, uc2const.COLOR_RGB]

class GenModePanel(wal.LabeledPanel):

	printer = None

	def __init__(self, parent, printer):
		self.printer = printer
		wal.LabeledPanel.__init__(self, parent, _('Generation options'))

		self.pack((1, 1), expand=True)

		grid = wal.GridPanel(self, 2, 2, 5, 5)
		grid.add_growable_col(1)

		grid.pack(wal.Label(grid, _('PDF version:')))

		self.ver_combo = wal.Combolist(grid, items=pdfconst.PDF_VER_NAMES)
		grid.pack(self.ver_combo, fill=True)

		grid.pack(wal.Label(grid, _('Color space:')))

		self.cs_combo = wal.Combolist(grid, items=CS)
		grid.pack(self.cs_combo, fill=True)

		self.pack(grid, fill=True, padding_all=8)

		hp = wal.HPanel(self)
		self.compressed = wal.Checkbox(hp, _('Use compression'))
		hp.pack((10, 5))
		hp.pack(self.compressed)
		self.pack(hp, padding_all=3, fill=True)

		self.pack((1, 1), expand=True)

		index = pdfconst.PDF_VERSIONS.index(self.printer.pdf_version)
		self.ver_combo.set_active(index)
		self.cs_combo.set_active(CS.index(self.printer.colorspace))
		self.compressed.set_value(self.printer.compressed)

	def save(self):
		self.printer.compressed = self.compressed.get_value()
		index = self.ver_combo.get_active()
		self.printer.pdf_version = pdfconst.PDF_VERSIONS[index]
		self.printer.colorspace = CS[self.cs_combo.get_active()]


class PagePanel(wal.LabeledPanel):

	app = None
	printer = None
	items = []

	def __init__(self, parent, printer, app):
		self.app = app
		self.printer = printer
		wal.LabeledPanel.__init__(self, parent, _('Document page'))

		grid = wal.GridPanel(self, 3, 2, 5, 5)
		grid.add_growable_col(1)

		grid.pack(wal.Label(grid, _('Page size:')))

		self.size_combo = wal.Combolist(grid, onchange=self.on_change)
		grid.pack(self.size_combo, fill=True)

		grid.pack(wal.Label(grid, _('Width:')))

		hpanel = wal.HPanel(grid)

		self.wspin = StaticUnitSpin(self.app, hpanel)
		hpanel.pack(self.wspin)

		hpanel.pack((5, 5))

		hpanel.pack(wal.Label(grid, _('Height:')), padding=5)

		self.hspin = StaticUnitSpin(self.app, hpanel)
		hpanel.pack(self.hspin)
		hpanel.pack(StaticUnitLabel(self.app, hpanel), padding=5)

		grid.pack(hpanel)

		grid.pack(wal.Label(grid, _('Orientation:')))

		hpanel = wal.HPanel(grid)

		self.port_opt = wal.Radiobutton(hpanel, _('Portrait'), group=True)
		self.land_opt = wal.Radiobutton(hpanel, _('Landscape'))

		hpanel.pack(self.port_opt)
		hpanel.pack((15, 5))
		hpanel.pack(self.land_opt)

		grid.pack(hpanel)

		self.pack(grid, fill=True, expand=True, padding_all=10)

		self.set_data()

	def set_data(self):
		self.land_opt.set_value(True)
		if self.printer.page_orientation == uc2const.PORTRAIT:
			self.port_opt.set_value(True)

		self.items = self.printer.get_format_items()
		self.size_combo.set_items(self.items)
		index = 0
		if not self.printer.page_format[0] == 'Custom':
			index = self.items.index(self.printer.page_format[0])
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
		if index == len(self.items) - 1:
			if not self.hspin.get_point_value() and \
			self.printer.page_format[0] == 'Custom':
				w, h = self.printer.page_format[1]
				self.wspin.set_point_value(w)
				self.hspin.set_point_value(h)
			status = True
		else:
			w, h = uc2const.PAGE_FORMATS[uc2const.PAGE_FORMAT_NAMES[index]]
			self.wspin.set_point_value(w)
			self.hspin.set_point_value(h)
		self.wspin.set_enable(status)
		self.hspin.set_enable(status)

	def save(self):
		index = self.size_combo.get_active()
		prn = self.printer
		if prn.is_custom_supported() and index == len(self.items) - 1:
			w = self.wspin.get_point_value()
			h = self.hspin.get_point_value()
			prn.page_format = ('Custom', (w, h))
		else:
			media = uc2const.PAGE_FORMAT_NAMES[index]
			w, h = uc2const.PAGE_FORMATS[media]
			prn.page_format = (media, (w, h))
		self.printer.page_orientation = uc2const.LANDSCAPE
		if self.port_opt.get_value():
			self.printer.page_orientation = uc2const.PORTRAIT

class DocInfoPanel(wal.LabeledPanel):

	printer = None

	def __init__(self, parent, printer, app):
		self.printer = printer
		self.app = app
		wal.LabeledPanel.__init__(self, parent, _('Document metainfo'))

		grid = wal.GridPanel(self, 3, 2, 2, 5)
		grid.add_growable_col(1)

		grid.pack(wal.Label(grid, _('Title:')))
		self.title = wal.Entry(grid, self.printer.meta_title)
		grid.pack(self.title, fill=True)

		grid.pack(wal.Label(grid, _('Subject:')))
		self.subject = wal.Entry(grid, self.printer.meta_subject)
		grid.pack(self.subject, fill=True)

		grid.pack(wal.Label(grid, _('Author:')))
		self.author = wal.Entry(grid, self.printer.meta_author)
		grid.pack(self.author, fill=True)

		grid.pack(wal.Label(grid, _('Keywords:')))
		self.keywords = wal.Entry(grid, self.printer.meta_keywords)
		grid.pack(self.keywords, fill=True)

		self.pack(grid, fill=True, expand=True, padding_all=10)

	def is_metadata(self):
		metainfo = self.app.current_doc.model.metainfo
		if metainfo:
			return bool(metainfo[0] or metainfo[2])
		return False

	def import_data(self):
		metainfo = self.app.current_doc.model.metainfo
		self.title.set_value('' + self.app.current_doc.doc_name)
		self.author.set_value('' + metainfo[0])
		self.keywords.set_value('' + metainfo[2])

	def save(self):
		self.printer.meta_title = self.title.get_value()
		self.printer.meta_subject = self.subject.get_value()
		self.printer.meta_author = self.author.get_value()
		self.printer.meta_keywords = self.keywords.get_value()


class MainPanel(wal.VPanel):

	app = None
	printer = None
	panels = []

	def __init__(self, parent, printer, app):
		self.app = app
		self.printer = printer
		wal.VPanel.__init__(self, parent)

		hpanel = wal.HPanel(self)
		icon = get_icon(icons.PD_PRINTER_PDF, size=wal.DEF_SIZE)
		hpanel.pack(wal.Bitmap(hpanel, icon), padding=10)

		self.prnmode_panel = GenModePanel(hpanel, self.printer)
		hpanel.pack(self.prnmode_panel, fill=True, expand=True)

		self.pack(hpanel, fill=True)

		self.page_panel = PagePanel(self, self.printer, self.app)
		self.pack(self.page_panel, fill=True)

		self.doc_info = DocInfoPanel(self, self.printer, self.app)
		self.pack(self.doc_info, fill=True, expand=True)

		self.panels = [self.prnmode_panel, self.page_panel, self.doc_info]

	def save(self):
		for item in self.panels: item.save()

class PDF_PrnPropsDialog(PrnProsDialog):

	def build(self):
		PrnProsDialog.build(self)
		self.panel.pack((5, 5))
		self.main_panel = MainPanel(self.panel, self.printer, self.app)
		self.panel.pack(self.main_panel, fill=True, expand=True)

	def set_dialog_buttons(self):
		PrnProsDialog.set_dialog_buttons(self)
		self.import_btn = wal.Button(self.left_button_box, _('Set metainfo'),
							tooltip=_('Set metainfo from current document'),
							onclick=self.main_panel.doc_info.import_data)
		self.left_button_box.pack(self.import_btn)
		self.import_btn.set_enable(self.main_panel.doc_info.is_metadata())

	def get_result(self):
		self.main_panel.save()
		return True
