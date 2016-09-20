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
from sk1.printing import prn_events, printout
from sk1.printing.generic import MONOCHROME_MODE

SPACER = (10, 10)

class FLabeledPanel(wal.VPanel):

	def __init__(self, parent, label='CAPTION'):
		self.title = label.upper()
		wal.VPanel.__init__(self, parent)
		hpanel = wal.HPanel(self)
		hpanel.pack(SPACER)
		self.cont = wal.VPanel(hpanel)
		self.cont.pack(wal.Label(self.cont, self.title, fontsize=3),
					padding=5, align_center=False)

		self.build()

		hpanel.pack(self.cont, fill=True, expand=True)
		hpanel.pack(SPACER)
		self.pack(hpanel, fill=True)

		self.pack(SPACER)
		self.pack(wal.HLine(self), fill=True)

	def build(self):pass

class CopiesPanel(FLabeledPanel):

	def __init__(self, parent, printer, printout):
		self.printer = printer
		self.printout = printout
		self.icons = {
		'00':get_icon(icons.PD_PRINT_COPIES_00, size=wal.DEF_SIZE),
		'10':get_icon(icons.PD_PRINT_COPIES_10, size=wal.DEF_SIZE),
		'01':get_icon(icons.PD_PRINT_COPIES_01, size=wal.DEF_SIZE),
		'11':get_icon(icons.PD_PRINT_COPIES_11, size=wal.DEF_SIZE),
		}
		FLabeledPanel.__init__(self, parent, _('Copies'))
		self.copies_changed()
		prn_events.connect(prn_events.PRINTER_CHANGED, self.on_printer_change)
		prn_events.connect(prn_events.PRINTOUT_MODIFIED, self.copies_changed)

	def build(self):
		hpanel = wal.HPanel(self)
		title = _('Number of copies:')
		hpanel.pack(wal.Label(hpanel, title), padding=5)
		self.num_copies = wal.IntSpin(hpanel, 1, (1, 9999),
								spin_overlay=config.spin_overlay,
								onchange=self.copies_changed)
		hpanel.pack(self.num_copies)
		self.cont.pack(hpanel)

		self.indicator = wal.Bitmap(hpanel, self.icons['00'])
		self.cont.pack(self.indicator, padding=5)

		hpanel = wal.HPanel(self)
		self.collate = wal.Checkbox(hpanel, _('Collate'),
								onclick=self.flag_changed)
		hpanel.pack(self.collate)
		hpanel.pack(SPACER)
		self.reverse = wal.Checkbox(hpanel, _('Reverse'),
								onclick=self.flag_changed)
		hpanel.pack(self.reverse)
		self.cont.pack(hpanel)

	def copies_changed(self):
		copies = self.num_copies.get_value()
		pages = self.printout.get_num_print_pages()
		state = False
		if pages > 1: state = True
		ctrls = [self.collate, self.reverse, self.indicator]
		for item in ctrls: item.set_enable(state)
		if not state:
			self.collate.set_value(False)
			self.reverse.set_value(False)
		if copies == 1:
			self.collate.set_value(False)
			self.collate.set_enable(False)
		self.update()

	def flag_changed(self):
		icon_key = str(int(self.collate.get_value()))
		icon_key += str(int(self.reverse.get_value()))
		self.indicator.set_bitmap(self.icons[icon_key])
		self.update()

	def on_printer_change(self, printer):
		self.printer = printer
		if self.printer and self.printer.is_virtual():
			self.num_copies.set_enable(False)
			self.num_copies.set_value(1)
			self.collate.set_enable(False)
			self.collate.set_value(False)
		self.update()

	def update(self):
		if self.printer and not self.printer.is_virtual():
			self.num_copies.set_enable(True)
			self.printer.set_copies(self.num_copies.get_value())
			self.printer.set_collate(self.collate.get_value())
		self.printout.set_reverse(self.reverse.get_value())


class PageRangePanel(FLabeledPanel):

	def __init__(self, parent, printout):
		self.printout = printout
		FLabeledPanel.__init__(self, parent, _('Page range'))

	def build(self):
		grid = wal.GridPanel(self.cont, 8, 1, 5, 15)
		grid.add_growable_col(0)
		self.all_opt = wal.Radiobutton(grid, _('All'), group=True,
									onclick=self.update)
		self.sel_opt = wal.Radiobutton(grid, _('Selection'),
									onclick=self.update)
		self.cpage_opt = wal.Radiobutton(grid, _('Current page'),
									onclick=self.update)
		self.pages_opt = wal.Radiobutton(grid, _('Pages:'),
									onclick=self.update)
		self.pages_entry = wal.Entry(grid, '1', onchange=self.pages_changed)
		grid.pack(self.all_opt)
		grid.pack(self.sel_opt)
		grid.pack(self.cpage_opt)
		grid.pack(self.pages_opt)
		grid.pack(self.pages_entry, fill=True)
		title = _('Enter page numbers or page ranges.')
		title += '\n' + _('For example: 1,2,5-6')
		grid.pack(wal.Label(self, title, fontsize=-1))
		self.cont.pack(grid, fill=True, padding_all=5)

		self.pages_entry.set_enable(False)
		self.all_opt.set_value(True)
		if not self.printout.is_selection():
			self.sel_opt.set_enable(False)
		if not self.printout.get_num_pages() > 1:
			self.cpage_opt.set_enable(False)
			self.pages_opt.set_enable(False)

	def pages_changed(self):
		txt = self.pages_entry.get_value()
		pos = self.pages_entry.get_cursor_pos()
		chars = ',0123456789-'
		res = ''
		if not txt or txt == '0':
			res = '1'
			txt = ''
		for item in txt:
			if item in chars:
				res += item
		if txt == res:
			self.pages_entry.set_value(res)
			self.pages_entry.set_cursor_pos(pos)
			self.update()
		else:
			self.pages_entry.set_value(res)

	def get_page_range(self):
		txt = self.pages_entry.get_value()
		vals = txt.split(',')
		ret = []
		pages_range = range(self.printout.get_num_pages())
		for item in vals:
			if not item:continue
			if '-' in item:
				rngs = item.split('-')
				int_rngs = []
				for rng in rngs:
					if rng: int_rngs.append(int(rng) - 1)
				if len(int_rngs) == 1:
					if int_rngs[0] in pages_range:
						ret.append(int_rngs[0])
				elif len(int_rngs) > 1:
					pages = range(int_rngs[0], int_rngs[-1] + 1)
					for page in pages:
						if page in pages_range:
							ret.append(page)
			else:
				val = int(item) - 1
				if val in pages_range:
					ret.append(val)
		return ret

	def update(self):
		self.pages_entry.set_enable(self.pages_opt.get_value())
		print_range = printout.PRINT_ALL
		page_range = []
		if self.all_opt.get_value():
			print_range = printout.PRINT_ALL
		elif self.sel_opt.get_value():
			print_range = printout.PRINT_SELECTION
		elif self.cpage_opt.get_value():
			print_range = printout.PRINT_CURRENT_PAGE
		elif self.pages_opt.get_value():
			print_range = printout.PRINT_PAGE_RANGE
			page_range = self.get_page_range()
		self.printout.set_print_range(print_range, page_range)
		prn_events.emit(prn_events.PRINTOUT_MODIFIED)


class PrintModePanel(FLabeledPanel):

	def __init__(self, parent, printer):
		self.printer = printer
		FLabeledPanel.__init__(self, parent, _('Print mode'))
		self.on_printer_changed(self.printer)
		prn_events.connect(prn_events.PRINTER_CHANGED, self.on_printer_changed)
		prn_events.connect(prn_events.PRINTER_MODIFIED, self.on_printer_modified)

	def build(self):

		grid = wal.GridPanel(self.cont, 2, 3, 5, 5)

		self.mono_opt = wal.Radiobutton(grid, _('Monochrome'), group=True,
									onclick=self.update)
		icon = get_icon(icons.PD_PRINTMODE_MONO, size=wal.DEF_SIZE)
		self.mono_bmp = wal.Bitmap(grid, icon)
		grid.pack(SPACER)
		grid.pack(self.mono_bmp)
		grid.pack(self.mono_opt)

		self.color_opt = wal.Radiobutton(grid, _('Color'), onclick=self.update)
		icon = get_icon(icons.PD_PRINTMODE_COLOR, size=wal.DEF_SIZE)
		self.color_bmp = wal.Bitmap(grid, icon)
		grid.pack(SPACER)
		grid.pack(self.color_bmp)
		grid.pack(self.color_opt)
		self.cont.pack(grid, align_center=False)

	def update(self):
		self.printer.set_color_mode(self.mono_opt.get_value() == False)
		prn_events.emit(prn_events.PRINTER_MODIFIED)

	def on_printer_changed(self, printer):
		self.printer = printer
		self.color_opt.set_enable(self.printer.is_color())
		self.on_printer_modified()

	def on_printer_modified(self):
		if self.printer.color_mode == MONOCHROME_MODE:
			self.mono_opt.set_value(True)
		else:
			self.color_opt.set_value(True)


class PrinterPanel(FLabeledPanel):

	ready_flag = False

	def __init__(self, parent, dlg, printsys):
		self.printsys = printsys
		self.dlg = dlg
		self.printer = self.printsys.get_default_printer()
		FLabeledPanel.__init__(self, parent, _('Printer'))

	def build(self):
		plist = self.printsys.get_printer_names()
		self.prn_list = wal.Combolist(self.cont, items=plist,
									onchange=self.on_printer_change)
		self.prn_list.set_active(plist.index(self.printer.get_name()))
		self.cont.pack(self.prn_list, fill=True, expand=True)

		self.cont.pack(SPACER)

		hpanel = wal.HPanel(self.cont)
		hpanel.pack((1, 1), fill=True, expand=True)
		self.print_btn = wal.Button(hpanel, _('Print'),
								onclick=self.dlg.on_print)
		hpanel.pack(self.print_btn)

		self.cont.pack(hpanel, fill=True)
		self.ready_flag = True

	def on_printer_change(self):
		if not self.ready_flag: return
		name = self.prn_list.get_active_value()
		self.printer = self.printsys.get_printer_by_name(name)
		prn_events.emit(prn_events.PRINTER_CHANGED, self.printer)
