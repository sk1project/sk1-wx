# -*- coding: utf-8 -*-
#
#  Copyright (C) 2018 by Igor E. Novikov
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

import wx


class PrintData(wx.PrintData):
    def __init__(self, printdata=None):
        if printdata:
            wx.PrintData.__init__(self, printdata)
        else:
            wx.PrintData.__init__(self)
        if printdata is None:
            self.SetPaperId(wx.PAPER_A4)
            self.SetPrintMode(wx.PRINT_MODE_PRINTER)

    def is_landscape(self):
        return self.GetOrientation() == wx.LANDSCAPE

    def set_printer_name(self, name):
        self.SetPrinterName(name)

    def set_color(self, val):
        self.SetColour(val)

    def set_collate(self, val):
        self.SetCollate(val)

    def set_no_copies(self, val):
        self.SetNoCopies(val)


class Printout(wx.Printout):
    def __init__(self):
        wx.Printout.__init__(self)

    def HasPage(self, page):
        return self.has_page(page)

    def GetPageInfo(self):
        return self.get_page_info()

    def OnPrintPage(self, page):
        self.on_print_page(page)
        return True

    # --- methods for overloading

    def has_page(self, page):
        return False

    def get_page_info(self):
        return 1, 1, 1, 1

    def on_print_page(self, page):
        pass


class PageSetupDialogData:
    data = None

    def __init__(self, data=None, printdata=None):
        if data:
            self.data = data
        elif printdata:
            self.data = wx.PageSetupDialogData(printdata)

    def get_paper_id(self):
        return self.data.GetPaperId()

    def get_paper_size(self):
        return tuple(self.data.GetPaperSize())

    def get_margins(self):
        x0, y0 = self.data.GetMarginTopLeft()
        x1, y1 = self.data.GetMarginBottomRight()
        return y0, x1, y1, x0

    def get_print_data(self):
        return PrintData(self.data.GetPrintData())

    def set_paper_size_from_id(self):
        self.data.CalculatePaperSizeFromId()

    def set_margins(self, margins):
        self.data.SetMarginTopLeft(wx.Point(margins[-1], margins[0]))
        self.data.SetMarginBottomRight(wx.Point(margins[1], margins[2]))


def run_page_setup_dialog(win, data):
    ret = None
    dlg = wx.PageSetupDialog(win, data.data)
    if dlg.ShowModal() == wx.ID_OK:
        ret = PageSetupDialogData(dlg.GetPageSetupData())
    dlg.Destroy()
    return ret


class MSWPrinter(wx.Printer):
    def __init__(self, printdata):
        data = wx.PrintDialogData(printdata)
        data.EnablePageNumbers(False)
        wx.Printer.__init__(self, data)
