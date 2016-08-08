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

class PrnProsDialog(wal.OkCancelDialog):

	printer = None
	win = None
	app = None

	def __init__(self, win, printer):
		self.win = win
		self.app = win.app
		self.printer = printer
		size = config.prnprops_dlg_size
		wal.OkCancelDialog.__init__(self, win, _("Printer properties"),
											size, resizable=True)
		self.set_minsize(config.prnprops_dlg_minsize)

	def build(self):
		vpanel = wal.VPanel(self.panel)
		vpanel.set_bg(wal.WHITE)
		txt = self.printer.get_name()
		vpanel.pack(wal.Label(vpanel, txt, fontsize=2, fontbold=True), padding=5)
		line = wal.VPanel(vpanel)
		line.pack((3, 3))
		line.set_bg(wal.UI_COLORS['selected_text_bg'])
		vpanel.pack(line, fill=True)
		self.panel.pack(vpanel, fill=True)

	def get_result(self): return True
