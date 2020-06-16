# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2016 by Ihor E. Novikov
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
# 	along with this program.  If not, see <https://www.gnu.org/licenses/>.

import wal
from generic import PrefPanel
from sk1 import _, config
from sk1.printing.generic import STD_MARGINS, STD_SHIFTS
from sk1.pwidgets import StaticUnitSpin
from sk1.resources import icons, get_bmp
from uc2 import uc2const


class PrinterPrefs(PrefPanel):
    pid = 'Printers'
    name = _('Printers')
    title = _('Printer calibration')
    icon_id = icons.PD_PREFS_PRINTERS

    printsys = None
    active_printer = None
    prn_list = []

    prn_combo = None
    insp = None
    hshift = None
    vshift = None
    top_spin = None
    left_spin = None
    right_spin = None
    bottom_spin = None
    a4_calibrate_btn = None
    letter_calibrate_btn = None

    def __init__(self, app, dlg, *_args):
        PrefPanel.__init__(self, app, dlg)

    def get_printsys(self):
        if wal.IS_MSW:
            from sk1.printing.msw_print import MSW_PS
            return MSW_PS(self.app, physical_only=True)
        else:
            from sk1.printing.cups_print import CUPS_PS
            return CUPS_PS(physical_only=True)

    def build(self):
        self.printsys = self.get_printsys()
        self.prn_list = self.printsys.get_printer_names()
        if self.prn_list:
            self.active_printer = self.printsys.get_default_printer()
            hpanel = wal.HPanel(self)
            hpanel.pack(wal.Label(hpanel, _('Printer:')))
            hpanel.pack((5, 5))
            self.prn_combo = wal.Combolist(hpanel, items=self.prn_list,
                                           onchange=self.set_data)
            hpanel.pack(self.prn_combo, fill=True, expand=True)
            index = self.prn_list.index(self.active_printer.get_name())
            self.prn_combo.set_active(index)
            self.pack(hpanel, fill=True, padding_all=5)

            self.pack((10, 10))

            # ---Panels
            self.insp = self.app.insp
            units = uc2const.UNIT_MM
            if self.insp.is_doc():
                units = self.app.current_doc.model.doc_units
            units_text = uc2const.unit_short_names[units]

            # ---Shift panel
            shifts = self.active_printer.shifts
            hpanel = wal.HPanel(self)
            txt = _('Printing shift') + ' (%s)' % units_text
            spanel = wal.LabeledPanel(hpanel, text=txt)
            spanel.pack((1, 1), expand=True)

            grid = wal.GridPanel(spanel, 2, 2, 5, 5)

            grid.pack(wal.Label(grid, _('Horizontal shift:')))
            self.hshift = StaticUnitSpin(self.app, grid, shifts[0],
                                         can_be_negative=True,
                                         onchange=self.save_data,
                                         onenter=self.save_data)
            grid.pack(self.hshift)

            grid.pack(wal.Label(grid, _('Vertical shift:')))
            self.vshift = StaticUnitSpin(self.app, grid, shifts[1],
                                         can_be_negative=True,
                                         onchange=self.save_data,
                                         onenter=self.save_data)
            grid.pack(self.vshift)

            spanel.pack(grid, padding_all=5)
            spanel.pack((1, 1), expand=True)

            hpanel.pack(spanel, fill=True, expand=True)

            hpanel.pack((5, 5))

            # ---Margin panel
            txt = _('Printing margins') + ' (%s)' % units_text
            mpanel = wal.LabeledPanel(hpanel, text=txt)
            mpanel.pack((5, 5))

            mrgs = self.active_printer.margins
            self.top_spin = StaticUnitSpin(self.app, mpanel, mrgs[0],
                                           onchange=self.save_data,
                                           onenter=self.save_data)
            mpanel.pack(self.top_spin)

            mpanel.pack((5, 5))

            hp = wal.HPanel(self)
            self.left_spin = StaticUnitSpin(self.app, hp, mrgs[3],
                                            onchange=self.save_data,
                                            onenter=self.save_data)
            hp.pack(self.left_spin)
            hp.pack((5, 5))
            self.right_spin = StaticUnitSpin(self.app, hp, mrgs[1],
                                             onchange=self.save_data,
                                             onenter=self.save_data)
            hp.pack(self.right_spin)

            mpanel.pack(hp)

            mpanel.pack((5, 5))

            self.bottom_spin = StaticUnitSpin(self.app, mpanel, mrgs[2],
                                              onchange=self.save_data,
                                              onenter=self.save_data)
            mpanel.pack(self.bottom_spin)

            mpanel.pack((10, 10))
            # ---

            hpanel.pack(mpanel, fill=True, expand=True)

            self.pack(hpanel, fill=True)

            self.pack((10, 10))

            # ---Calibration page
            text = _("To measure actual print area and vertical/horizontal "
                     "printing shift, just print the calibration page on "
                     "A4/Letter paper.")

            label = wal.Label(self, text)
            label.wrap(470)
            self.pack(label, fill=True, padding_all=5, align_center=False)

            self.a4_calibrate_btn = wal.Button(
                self, _('Print A4 calibration page'),
                onclick=self.print_calibration_a4)
            self.pack(self.a4_calibrate_btn)

            self.pack((5, 5))

            self.letter_calibrate_btn = wal.Button(
                self, _('Print Letter calibration page'),
                onclick=self.print_calibration_letter)
            self.pack(self.letter_calibrate_btn)

            self.pack((5, 5))

        else:
            self.pack((5, 5), expand=True)
            self.pack(get_bmp(self, icons.PD_NO_PRINTERS), padding=10)
            self.pack(wal.Label(self, _('No printers found')))
            self.pack((10, 10))
            self.pack((5, 5), expand=True)
        self.built = True

    def set_data(self):
        name = self.prn_combo.get_active_value()
        self.active_printer = self.printsys.get_printer_by_name(name)
        shifts = self.active_printer.shifts
        mrgs = self.active_printer.margins

        self.hshift.set_point_value(shifts[0])
        self.vshift.set_point_value(shifts[1])
        self.top_spin.set_point_value(mrgs[0])
        self.right_spin.set_point_value(mrgs[1])
        self.bottom_spin.set_point_value(mrgs[2])
        self.left_spin.set_point_value(mrgs[3])

    def save_data(self):
        self.active_printer.shifts = (self.hshift.get_point_value(),
                                      self.vshift.get_point_value())

        self.active_printer.margins = (self.top_spin.get_point_value(),
                                       self.right_spin.get_point_value(),
                                       self.bottom_spin.get_point_value(),
                                       self.left_spin.get_point_value())

    def apply_changes(self):
        if not self.prn_list:
            return
        config.printer_config = {}
        for name in self.prn_list:
            printer = self.printsys.get_printer_by_name(name)
            if printer:
                printer.save_config()

    def restore_defaults(self):
        if not self.prn_list:
            return
        self.active_printer.shifts = STD_SHIFTS
        self.active_printer.margins = STD_MARGINS
        self.set_data()

    def print_calibration_a4(self):
        self.active_printer.print_test_page_a4(self.app, self.dlg)

    def print_calibration_letter(self):
        self.active_printer.print_test_page_letter(self.app, self.dlg)
