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

import wx

from sk1.printing.printout import Printout

class MSWPrintout(Printout, wx.Printout):

	def __init__(self, doc):
		Printout.__init__(self, doc)
		wx.Printout.__init__(self)

	def HasPage(self, page):
		if page <= self.get_num_print_pages(): return True
		else: return False

	def GetPageInfo(self):
		val = self.get_num_print_pages()
		return (1, val, 1, val)

	def OnPrintPage(self, page):
		return True
