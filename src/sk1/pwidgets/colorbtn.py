# -*- coding: utf-8 -*-
#
#	Copyright (C) 2015 by Igor E. Novikov
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.

from copy import deepcopy

import wal

from uc2.formats.sk2 import sk2_const

from sk1.resources import icons
from sk1.dialogs.colordlg import change_color_dlg

from colorctrls import AlphaColorSwatch

class PDColorButton(wal.HPanel):

	dlg = None
	cms = None
	color = []
	callback = None

	def __init__(self, parent, dlg, cms, color=deepcopy(sk2_const.CMYK_BLACK),
				tooltip='', onchange=None):
		self.dlg = dlg
		self.cms = cms
		self.color = color
		self.callback = onchange
		wal.HPanel.__init__(self, parent)

		self.swatch = AlphaColorSwatch(self, self.cms, self.color, (40, 20),
									'news', onclick=self.edit_color)
		self.pack(self.swatch)

		self.pack(wal.ImageButton(self, icons.PD_EDIT, wal.SIZE_16,
				tooltip=tooltip, flat=False, onclick=self.edit_color),
				padding=5)

	def set_color(self, color):
		self.color = color
		self.swatch.set_color(color)

	def get_color(self): return deepcopy(self.color)

	def edit_color(self):
		ret = change_color_dlg(self.dlg, self.cms, self.color)
		if ret:
			self.color = ret
			self.swatch.set_color(ret)
			if self.callback:self.callback(self.get_color())
