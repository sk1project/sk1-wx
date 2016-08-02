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

import os

import wal

from sk1 import _, config, dialogs
from sk1.resources import get_icon, icons
from sk1.printing import prn_events, printout

class RangePanel(wal.LabeledPanel):

	def __init__(self, parent, win, printout):
		self.win = win
		self.printout = printout
		wal.LabeledPanel.__init__(self, parent, _('Print range'))

		int_panel = wal.HPanel(self)

		vpanel = wal.VPanel(int_panel)

		grid = wal.GridPanel(vpanel, 3, 2, 5, 5)
		grid.add_growable_col(1)
		self.all_opt = wal.Radiobutton(grid, _('All'), group=True,
									onclick=self.update)
		self.sel_opt = wal.Radiobutton(grid, _('Selection'),
									onclick=self.update)
		self.cpage_opt = wal.Radiobutton(grid, _('Current page'),
									onclick=self.update)
		self.pages_opt = wal.Radiobutton(grid, _('Pages:'),
									onclick=self.update)
		self.pages_entry = wal.Entry(grid, '1', onchange=self.pages_changed)
		self.pages_entry.set_enable(False)
		self.all_opt.set_value(True)
		if not self.printout.is_selection():
			self.sel_opt.set_enable(False)
		if not self.printout.get_num_pages() > 1:
			self.cpage_opt.set_enable(False)
			self.pages_opt.set_enable(False)
		grid.pack(self.all_opt)
		grid.pack((1, 1))
		grid.pack(self.sel_opt)
		grid.pack(self.cpage_opt)
		grid.pack(self.pages_opt)
		grid.pack(self.pages_entry, fill=True)
		vpanel.pack(grid, fill=True)

		vpanel.pack((5, 5))

		title = _('Enter page numbers or page ranges.')
		title += '\n' + _('For example: 1,2,5-6')
		vpanel.pack(wal.Label(self, title, fontsize=-1), align_center=False)

		int_panel.pack((10, 10))
		int_panel.pack(vpanel, fill=True, expand=True)
		int_panel.pack((10, 10))

		self.pack(int_panel, fill=True, expand=True, padding_all=3)

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

class CopiesPanel(wal.LabeledPanel):

	printer = None
	printout = None

	def __init__(self, parent, win, printout):
		self.printout = printout
		wal.LabeledPanel.__init__(self, parent, _('Copies'))

		self.icons = {
		'00':get_icon(icons.PD_PRINT_COPIES_00, size=wal.DEF_SIZE),
		'10':get_icon(icons.PD_PRINT_COPIES_10, size=wal.DEF_SIZE),
		'01':get_icon(icons.PD_PRINT_COPIES_01, size=wal.DEF_SIZE),
		'11':get_icon(icons.PD_PRINT_COPIES_11, size=wal.DEF_SIZE),
		}

		self.pack((5, 5))

		hpanel = wal.HPanel(self)
		title = _('Number of copies:')
		hpanel.pack(wal.Label(hpanel, title), padding=5)
		self.num_copies = wal.IntSpin(hpanel, 1, (1, 99999),
								spin_overlay=config.spin_overlay,
								onchange=self.copies_changed)
		hpanel.pack(self.num_copies)
		self.pack(hpanel, padding=5)

		hpanel = wal.HPanel(self)

		grid = wal.GridPanel(hpanel, 2, 1, 5, 5)
		self.collate = wal.Checkbox(grid, _('Collate'),
								onclick=self.flag_changed)
		grid.pack(self.collate)
		self.reverse = wal.Checkbox(grid, _('Reverse'),
								onclick=self.flag_changed)
		grid.pack(self.reverse)

		hpanel.pack(grid, expand=True)

		self.indicator = wal.Bitmap(hpanel, self.icons['00'])
		hpanel.pack(self.indicator)

		self.pack(hpanel, fill=True, expand=True, padding_all=10)
		self.copies_changed()
		prn_events.connect(prn_events.PRINTER_CHANGED, self.on_printer_change)
		prn_events.connect(prn_events.PRINTOUT_MODIFIED, self.copies_changed)

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
		self.update()

	def update(self):
		if self.printer:
			self.printer.set_copies(self.num_copies.get_value())
			self.printer.set_collate(self.collate.get_value())
		self.printout.set_reverse(self.reverse.get_value())


class PrinterPanel(wal.LabeledPanel):

	printsys = None
	printer = None
	ready_flag = False
	win = None

	def __init__(self, parent, win, printsys):
		self.printsys = printsys
		self.win = win
		self.printer = self.printsys.get_default_printer()
		wal.LabeledPanel.__init__(self, parent, _('Printer'))

		grid = wal.GridPanel(self, 4, 2, 5, 5)
		grid.add_growable_col(1)

		grid.pack(wal.Label(grid, _('Name:')))

		hpanel = wal.HPanel(grid)
		plist = self.printsys.get_printer_names()
		self.prn_list = wal.Combolist(hpanel, items=plist,
									onchange=self.on_printer_change)
		self.prn_list.set_active(plist.index(self.printer.get_name()))
		hpanel.pack(self.prn_list, fill=True, expand=True)
		hpanel.pack((5, 5))
		self.prop_btn = wal.Button(hpanel, _('Properties...'))
		hpanel.pack(self.prop_btn)
		grid.pack(hpanel, fill=True)

		prn_info = self.printer.get_prn_info()
		self.info_00 = wal.Label(grid, prn_info[0][0], fontsize=-1)
		grid.pack(self.info_00)
		self.info_01 = wal.Label(grid, prn_info[0][1], fontsize=-1)
		grid.pack(self.info_01)

		self.info_10 = wal.Label(grid, prn_info[1][0], fontsize=-1)
		grid.pack(self.info_10)
		self.info_11 = wal.Label(grid, prn_info[1][1], fontsize=-1)
		grid.pack(self.info_11)

		self.output_label = wal.Label(grid, _('Output file:'))
		grid.pack(self.output_label)

		hpanel = wal.HPanel(grid)
		path = self.printer.get_filepath()
		self.output_file = wal.Entry(hpanel, path, editable=False)
		hpanel.pack(self.output_file, fill=True, expand=True)
		hpanel.pack((5, 5))
		self.output_choice = wal.ImageButton(hpanel, icons.PD_OPEN, wal.SIZE_16,
									flat=False, onclick=self.on_choice,
									tooltip=_('Select output file'))
		hpanel.pack(self.output_choice)
		grid.pack(hpanel, fill=True)

		self.pack(grid, fill=True, expand=True, padding_all=10)
		self.ready_flag = True
		self.update()

	def on_choice(self):
		doc_file = 'print'
		doc_file = os.path.join(config.print_dir, doc_file)
		doc_file = dialogs.get_save_file_name(self.win, None, doc_file,
							_('Select output file'), path_only=True,
							file_types=[self.printer.get_file_type(), ])
		if doc_file:
			self.printer.set_filepath(doc_file)
			self.output_file.set_value(doc_file)
			config.print_dir = str(os.path.dirname(doc_file))
			prn_events.emit(prn_events.PRINTER_MODIFIED)

	def on_printer_change(self):
		if not self.ready_flag: return
		name = self.prn_list.get_active_value()
		self.printer = self.printsys.get_printer_by_name(name)
		self.update()
		prn_events.emit(prn_events.PRINTER_CHANGED, self.printer)

	def update(self):
		prn_info = self.printer.get_prn_info()
		self.info_00.set_text(prn_info[0][0])
		self.info_01.set_text(prn_info[0][1])
		self.info_10.set_text(prn_info[1][0])
		self.info_11.set_text(prn_info[1][1])
		self.layout()

		self.output_file.set_value(self.printer.get_filepath())
		file_ctrls = (self.output_label, self.output_file, self.output_choice)
		state = self.printer.is_virtual()
		for item in file_ctrls: item.set_enable(state)


class GeneralTab(wal.VPanel):

	name = _('General')

	def __init__(self, parent, win, printsys, printout):
		wal.VPanel.__init__(self, parent)

		int_panel = wal.VPanel(self)

		self.prn_panel = PrinterPanel(int_panel, win, printsys)
		int_panel.pack(self.prn_panel, fill=True)

		int_panel.pack((5, 5))

		hpanel = wal.HPanel(int_panel)
		self.range_panel = RangePanel(hpanel, win, printout)
		hpanel.pack(self.range_panel, fill=True, expand=True)
		hpanel.pack((5, 5))
		self.copies_panel = CopiesPanel(hpanel, win, printout)
		hpanel.pack(self.copies_panel, fill=True, expand=True)
		int_panel.pack(hpanel, fill=True, expand=True)

		self.pack(int_panel, fill=True, expand=True, padding_all=5)
