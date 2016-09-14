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

from sk1 import _

class FLabeledPanel(wal.VPanel):

	def __init__(self, parent, label='CAPTION'):
		self.title = label.upper()
		wal.VPanel.__init__(self, parent)
		hpanel = wal.HPanel(self)
		hpanel.pack((5, 5))
		self.cont = wal.VPanel(hpanel)
		self.cont.pack(wal.Label(self.cont, self.title, fontsize=3),
					padding=5, align_center=False)

		self.build()

		hpanel.pack(self.cont, fill=True, expand=True)
		hpanel.pack((5, 5))
		self.pack(hpanel, fill=True)
		panel = wal.VPanel(self)
		panel.set_bg(wal.UI_COLORS['workspace'])
		panel.pack((1, 1))
		self.pack(panel, fill=True)

	def build(self):pass


class PrinterPanel(FLabeledPanel):

	def __init__(self, parent, win, printsys):
		self.printsys = printsys
		self.win = win
		self.printer = self.printsys.get_default_printer()
		FLabeledPanel.__init__(self, parent, _('Destination'))

	def build(self):
		self.cont.pack((200, 100))
