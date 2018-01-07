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
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import wx


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
