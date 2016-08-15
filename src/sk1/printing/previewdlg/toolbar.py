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
from sk1.resources import icons

class PreviewToolbar(wal.HPanel):

	canvas = None

	def __init__(self, parent, dlg, canvas):
		self.dlg = dlg
		self.canvas = canvas
		wal.HPanel.__init__(self, parent)

		Btn = wal.ImageButton

		buttons = [
				(icons.PD_ZOOM_IN, self.stub),
				(icons.PD_ZOOM_OUT, self.stub),
				(icons.PD_ZOOM_PAGE, self.stub),
				(icons.PD_ZOOM_100, self.stub),
				None,
				(icons.PD_PROPERTIES, self.stub),
				]

		for item in buttons:
			if item:
				self.pack(Btn(self, item[0], wal.SIZE_24, onclick=item[1]))
			else:
				self.pack(wal.VLine(self), padding_all=5, fill=True)

		self.pack((5, 5), expand=True)
		self.pack(wal.Button(self, _('Close'), onclick=self.close_dlg))

	def stub(self):pass

	def close_dlg(self):
		self.dlg.on_close()