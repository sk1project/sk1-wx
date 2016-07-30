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

import os, sys

import wal

from sk1 import _, config, appconst, dialogs
from sk1.resources import get_icon, icons

import prn_events
from cups_staff import CUPS_PS, CUPS_Printout

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
		self.pages_entry = wal.Entry(grid, '1')
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

	def update(self):
		self.pages_entry.set_enable(self.pages_opt.get_value())




class CopiesPanel(wal.LabeledPanel):

	def __init__(self, parent, win, printout):
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

	def copies_changed(self):
		state = False
		if self.num_copies.get_value() > 1: state = True
		ctrls = [self.collate, self.reverse, self.indicator]
		for item in ctrls: item.set_enable(state)
		if not state:
			self.collate.set_value(False)
			self.reverse.set_value(False)

	def flag_changed(self):
		icon_key = str(int(self.collate.get_value()))
		icon_key += str(int(self.reverse.get_value()))
		self.indicator.set_bitmap(self.icons[icon_key])


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

		grid.pack(wal.Label(grid, _('Driver:'), fontsize=-1))
		self.driver_label = wal.Label(grid, _(''), fontsize=-1)
		grid.pack(self.driver_label)

		grid.pack(wal.Label(grid, _('Connection:'), fontsize=-1))
		self.conn_label = wal.Label(grid, _(''), fontsize=-1)
		grid.pack(self.conn_label)

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


	def on_printer_change(self):
		if not self.ready_flag: return
		name = self.prn_list.get_active_value()
		self.printer = self.printsys.get_printer_by_name(name)
		self.update()
		prn_events.emit(prn_events.PRINTER_CHANGED, self.printer)

	def update(self):
		self.driver_label.set_text(self.printer.get_driver_name())
		self.conn_label.set_text(self.printer.get_connection())

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

class CUPSPrintDialog(wal.OkCancelDialog):

	printsys = None
	printer = None
	printout = None

	def __init__(self, parent, title, presenter):
		self.app = parent.app
		self.presenter = presenter
		self.printsys = CUPS_PS()
		self.printer = self.printsys.get_default_printer()
		self.printout = CUPS_Printout(presenter)
		size = config.print_dlg_size
		wal.OkCancelDialog.__init__(self, parent, title, size, resizable=True,
								action_button=wal.BUTTON_PRINT)
		self.set_minsize(config.print_dlg_minsize)

	def build(self):
		self.nb = wal.Notebook(self.panel)

		self.general_tab = GeneralTab(self.nb, self,
									self.printsys, self.printout)
		self.nb.add_page(self.general_tab, self.general_tab.name)

		self.layouts_tab = wal.VPanel(self.nb)
		self.nb.add_page(self.layouts_tab, 'Layouts')

		self.prepress_tab = wal.VPanel(self.nb)
		self.nb.add_page(self.prepress_tab, 'Prepress')

		self.preflight_tab = wal.VPanel(self.nb)
		self.nb.add_page(self.preflight_tab, 'Prefligh')

		self.panel.pack(self.nb, expand=True, fill=True)
		self.general_tab.prn_panel.update()

	def set_dialog_buttons(self):
		wal.OkCancelDialog.set_dialog_buttons(self)
		self.preview_btn = wal.Button(self.left_button_box, _('Print Preview'),
								onclick=self.print_preview)
		self.left_button_box.pack(self.preview_btn)

	def end_modal(self, ret):
		prn_events.clean_all_channels()
		wal.OkCancelDialog.end_modal(self, ret)

	def print_preview(self):pass




def cups_print_dlg(parent, presenter):
	dlg = CUPSPrintDialog(parent, _("Print"), presenter)
	dlg.show()
	dlg.destroy()
