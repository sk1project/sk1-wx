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

from uc2.app_palettes import PaletteManager
from uc2.formats.skp.skp_presenter import SKP_Presenter

from sk1 import _, config, events
from sk1.resources import cmyk_palette, rgb_palette

STD_CMYK_PALETTE = _('sK1 CMYK palette')
STD_RGB_PALETTE = _('sK1 RGB palette')

class AppPaletteManager(PaletteManager):

	palette_in_use = None

	def __init__(self, app):
		PaletteManager.__init__(self, app)
		self.init_builtin_palettes()
		self.set_palette(config.palette)
		events.connect(events.CONFIG_MODIFIED, self.update)

	def update(self, attr, val):
		if attr == 'palette':
			self.set_palette(config.palette)

	def get_default_palette_name(self):return STD_CMYK_PALETTE

	def set_palette(self, name=''):
		if name and name in self.palettes.keys():
			self.palette_in_use = self.palettes[name]
		else:
			self.palette_in_use = self.palettes[STD_CMYK_PALETTE]
			config.palette = STD_CMYK_PALETTE

	def init_builtin_palettes(self):
		pal = SKP_Presenter(self.app.appdata)
		pal.model.name = STD_CMYK_PALETTE
		pal.model.source = 'sK1 Project'
		pal.model.builtin = True
		pal.model.colors = cmyk_palette.colors
		txt = _('The palette has been converted from sK1 RGB palette.')
		pal.model.comments = txt
		self.palettes[STD_CMYK_PALETTE] = pal

		pal = SKP_Presenter(self.app.appdata)
		pal.model.name = STD_RGB_PALETTE
		pal.model.source = 'sK1 Project'
		pal.model.builtin = True
		pal.model.colors = rgb_palette.colors
		txt = _('The palette has been inherited from Sketch application.')
		pal.model.comments = txt
		self.palettes[STD_RGB_PALETTE] = pal

