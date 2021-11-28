# -*- coding: utf-8 -*-
#
#  Copyright (C) 2016 by Ihor E. Novikov
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os

import wal
from sk1 import _, config
from sk1.dialogs import ProgressDialog, error_dialog
from sk1.printing import prn_events
from uc2 import uc2const
from uc2.formats import get_loader

from . import winspool
from .generic import COLOR_MODE, MONOCHROME_MODE, AbstractPrinter, AbstractPS
from .pdf_printer import PDF_Printer
from .printout import Printout


def get_print_data(app):
    if app.print_data is None:
        app.print_data = wal.PrintData()
    return app.print_data


class MSW_PS(AbstractPS):
    printers = []
    default_printer = ''

    def __init__(self, app, physical_only=False):
        self.printers = []
        self.app = app
        self.collect_printers()
        if not physical_only:
            self.printers.append(PDF_Printer())

    def readline(self, fileptr):
        return fileptr.readline().replace('\n', '').replace('\r', '').strip()

    def collect_printers(self):
        self.default_printer = winspool.get_default_printer()
        for ptrname in winspool.get_printer_names():
            printer = MSWPrinter(self.app, ptrname)
            if winspool.is_color_printer(ptrname):
                printer.color_supported = True
                printer.colorspace = uc2const.COLOR_RGB
                printer.color_mode = COLOR_MODE
            self.printers.append(printer)

    def get_printer_by_name(self, name):
        if not name:
            self.get_default_printer()
        return AbstractPS.get_printer_by_name(self, name)


class MSWPrinter(AbstractPrinter):
    color_supported = False
    name = ''

    def __init__(self, app, name=_('Default printer')):
        self.app = app
        self.name = name
        AbstractPrinter.__init__(self)

    def is_virtual(self):
        return False

    def is_color(self):
        return self.color_supported

    def set_color_mode(self, val=True):
        if self.is_color():
            if val:
                self.color_mode = COLOR_MODE
                self.colorspace = uc2const.COLOR_RGB
            else:
                self.color_mode = MONOCHROME_MODE
                self.colorspace = uc2const.COLOR_GRAY

    def update_from_psd(self, page_setup_data):
        # --- Margins
        mrgns = page_setup_data.get_margins()
        self.margins = tuple(uc2const.mm_to_pt * x for x in mrgns)
        # --- Page Orientation
        print_data = get_print_data(self.app)
        self.page_orientation = uc2const.LANDSCAPE \
            if print_data.is_landscape() else uc2const.PORTRAIT
        # --- Page format
        page_id = page_setup_data.get_paper_id()
        page_size = page_setup_data.get_paper_size()
        page_size = tuple(uc2const.mm_to_pt * x for x in page_size)
        self.page_format = (page_id, page_size)

    def run_propsdlg(self, win):
        print_data = get_print_data(self.app)
        print_data.set_printer_name(self.name)
        data = wal.PageSetupDialogData(printdata=print_data)
        data.set_paper_size_from_id()
        # --- Margins
        mrgns = [uc2const.pt_to_mm * x for x in self.margins]
        data.set_margins(mrgns)

        page_setup_data = wal.run_page_setup_dialog(win, data)
        if page_setup_data:
            self.app.print_data = page_setup_data.get_print_data()
            self.update_from_psd(page_setup_data)
            prn_events.emit(prn_events.PRINTER_MODIFIED)
            return True
        return False

    def run_printdlg(self, win, printout):
        printout.shifts = self.shifts
        print_data = get_print_data(self.app)
        print_data.set_printer_name(self.name)
        print_data.set_color(self.color_mode == COLOR_MODE)
        print_data.set_collate(self.collate)
        print_data.set_no_copies(self.copies)
        return wal.MSWPrinter(print_data).Print(win, printout, True)

    def print_calibration(self, app, win, path, media=''):
        pd = ProgressDialog(_('Loading calibration page...'), win)
        try:
            loader = get_loader(path)
            doc_presenter = pd.run(loader, [app.appdata, path])
            self.run_printdlg(win, Printout(doc_presenter))
        except Exception:
            txt = _('Error while printing of calibration page!')
            txt += '\n' + _('Check your printer status and connection.')
            error_dialog(win, app.appdata.app_name, txt)
        finally:
            pd.destroy()

    def print_test_page_a4(self, app, win):
        path = os.path.join(config.resource_dir, 'templates',
                            'print_calibration_a4.sk2')
        self.print_calibration(app, win, path, 'A4')

    def print_test_page_letter(self, app, win):
        path = os.path.join(config.resource_dir, 'templates',
                            'print_calibration_letter.sk2')
        self.print_calibration(app, win, path, 'Letter')
