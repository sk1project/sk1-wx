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


import wal

from uc2 import uc2const
from uc2.formats.sk2 import sk2_const
from sk1 import _, config
from sk1.resources import icons

class FillDialog(wal.OkCancelDialog):

	presenter = None
	orig_fill = []

	def __init__(self, parent, title, presenter):
		self.presenter = presenter
		wal.OkCancelDialog.__init__(self, parent, title, style=wal.VERTICAL,
								size=(500, 350), add_line=False)

	def build(self):
		self.nb = wal.Notebook(self)
		self.nb.add_page(SolidFill(self.nb, self), _('Solid Fill'))
		self.nb.add_page(GradientFill(self.nb, self), _('Gradient Fill'))
		self.nb.add_page(PatternFill(self.nb, self), _('Pattern Fill'))

		self.pack(self.nb, fill=True, expand=True)

	def get_result(self):
		return []

	def get_original_fill(self):
		ret = []
		return ret

def fill_dlg(parent, presenter, title=_("Fill")):
	return FillDialog(parent, title, presenter).show()

#--- Solid fill stuff
CMYK_MODE = 0
RGB_MODE = 1
GRAY_MODE = 2
SPOT_MODE = 3
PAL_MODE = 4
EMPTY_MODE = 5

SOLID_MODES = [CMYK_MODE, RGB_MODE, GRAY_MODE, SPOT_MODE, PAL_MODE, EMPTY_MODE]

SOLID_MODE_ICONS = {
CMYK_MODE: icons.PD_CONV_TO_CMYK,
RGB_MODE: icons.PD_CONV_TO_RGB,
GRAY_MODE: icons.PD_CONV_TO_GRAY,
SPOT_MODE: icons.PD_CONV_TO_SPOT,
PAL_MODE: icons.PD_PREFS_PALETTE,
EMPTY_MODE: icons.PD_EMPTY,
}

SOLID_MODE_NAMES = {
CMYK_MODE: _('CMYK colorspace'),
RGB_MODE: _('RGB colorspace'),
GRAY_MODE: _('Grayscale colorspace'),
SPOT_MODE: _('SPOT colors'),
PAL_MODE: _('Color from palette'),
EMPTY_MODE: _('Empty pattern'),
}

SOLID_MODE_MAP = {
uc2const.COLOR_CMYK: CMYK_MODE,
uc2const.COLOR_RGB: RGB_MODE,
uc2const.COLOR_GRAY: GRAY_MODE,
uc2const.COLOR_SPOT: SPOT_MODE,
}

RULE_MODES = [sk2_const.FILL_EVENODD, sk2_const.FILL_NONZERO]

RULE_MODE_NAMES = {
sk2_const.FILL_EVENODD: _('Evenodd fill'),
sk2_const.FILL_NONZERO: _('Nonzero fill'),
}

RULE_MODE_ICONS = {
sk2_const.FILL_EVENODD: icons.PD_EVENODD,
sk2_const.FILL_NONZERO: icons.PD_NONZERO,
}


class SolidFill(wal.VPanel):

	active_panel = None

	def __init__(self, parent, dlg):
		self.dlg = dlg
		wal.VPanel.__init__(self, parent)
		panel = wal.HPanel(self)
		self.solid_keeper = wal.HToggleKeeper(panel, SOLID_MODES,
									SOLID_MODE_ICONS,
									SOLID_MODE_NAMES, self.on_mode_change)
		panel.pack(self.solid_keeper)
		panel.pack(wal.HPanel(panel), fill=True, expand=True)
		self.rule_keeper = wal.HToggleKeeper(panel, RULE_MODES,
										RULE_MODE_ICONS,
										RULE_MODE_NAMES)
		panel.pack(self.rule_keeper)
		self.pack(panel, fill=True, padding_all=5)
		self.pack(wal.HLine(self), fill=True)

	def on_mode_change(self, mode):pass

#--- Gradient fill stuff

class GradientFill(wal.VPanel):

	def __init__(self, parent, dlg):
		self.dlg = dlg
		wal.VPanel.__init__(self, parent)

class PatternFill(wal.VPanel):

	def __init__(self, parent, dlg):
		self.dlg = dlg
		wal.VPanel.__init__(self, parent)
