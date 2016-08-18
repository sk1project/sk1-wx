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

	def __init__(self, parent, dlg, canvas, printer):
		self.dlg = dlg
		self.canvas = canvas
		self.printer = printer
		wal.HPanel.__init__(self, parent)

		Btn = wal.ImageButton

		buttons = [
		(icons.PD_ZOOM_IN, self.canvas.zoom_in, _('Zoom in')),
		(icons.PD_ZOOM_OUT, self.canvas.zoom_out, _('Zoom out')),
		(icons.PD_ZOOM_PAGE, self.canvas.zoom_fit_to_page, _('Fit to page')),
		(icons.PD_ZOOM_100, self.canvas.zoom_100, _('Zoom 100%')),
		None,
		(icons.PD_PRINT_PREVIEW, self.on_printer_props, _('Printer properties')),
		(),
		(icons.PD_QUIT, self.dlg.on_close, _('Close preview'))
		]

		for item in buttons:

			if item:
				self.pack(Btn(self, item[0], wal.SIZE_24,
							tooltip=item[2], onclick=item[1]))
			elif item is None:
				self.pack(wal.VLine(self), padding_all=5, fill=True)
			else:
				self.pack((5, 5), expand=True)

	def stub(self):pass

	def on_printer_props(self):
		if self.printer.run_propsdlg(self.dlg):
			self.canvas.refresh()
