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

from uc2 import uc2const

from sk1 import _, config
from sk1.pwidgets.colorctrls import CMYK_Mixer, RGB_Mixer, Gray_Mixer, \
ColorColorRefPanel, MiniPalette, CMYK_PALETTE, RGB_PALETTE, GRAY_PALETTE

MIXERS = {
uc2const.COLOR_CMYK: CMYK_Mixer,
uc2const.COLOR_RGB: RGB_Mixer,
uc2const.COLOR_GRAY: Gray_Mixer,
}

PALETTES = {
uc2const.COLOR_CMYK: CMYK_PALETTE,
uc2const.COLOR_RGB: RGB_PALETTE,
uc2const.COLOR_GRAY: GRAY_PALETTE,
}

class ChangeColorDialog(wal.OkCancelDialog):

	cms = None
	orig_color = None
	new_color = None

	def __init__(self, parent, title, cms, color):
		self.cms = cms
		self.orig_color = color
		self.new_color = deepcopy(self.orig_color)
		size = config.change_color_dlg_size
		wal.OkCancelDialog.__init__(self, parent, title, style=wal.VERTICAL,
								size=size)

	def build(self):
		self.pack(wal.HPanel(self), fill=True, expand=True)

		cs = self.orig_color[0]
		self.mixer = MIXERS[cs](self, self.cms, onchange=self.mixer_changed)
		self.pack(self.mixer)

		self.pack(wal.HPanel(self), fill=True, expand=True)

		self.pack(wal.HLine(self), fill=True, padding=5)

		hpanel = wal.HPanel(self)

		self.refpanel = ColorColorRefPanel(hpanel, self.cms, self.orig_color,
							self.new_color, on_orig=self.refpanel_click)
		hpanel.pack(self.refpanel)

		hpanel.pack(wal.HPanel(hpanel), fill=True, expand=True)

		self.palette = MiniPalette(hpanel, self.cms, PALETTES[cs],
								onclick=self.palette_click)
		hpanel.pack(self.palette)

		self.pack(hpanel, fill=True)
		self.update()

	def get_result(self):
		return self.mixer.get_color()

	def mixer_changed(self):
		self.new_color = self.mixer.get_color()
		self.update()

	def refpanel_click(self):
		self.new_color = deepcopy(self.orig_color)
		self.update()

	def palette_click(self, color):
		self.new_color = color
		self.update()

	def update(self):
		self.mixer.set_color(self.new_color)
		self.refpanel.update(self.orig_color, self.new_color)

def change_color_dlg(parent, cms, color, title=_('Change color')):
	return ChangeColorDialog(parent, title, cms, color).show()
