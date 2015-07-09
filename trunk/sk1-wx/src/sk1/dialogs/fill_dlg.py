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
from uc2.formats.sk2 import sk2_const
from sk1 import _, config
from sk1.resources import icons
from sk1.pwidgets import CMYK_Panel, RGB_Panel, Gray_Panel, Empty_Panel, \
SolidFillPanel

class FillDialog(wal.OkCancelDialog):

	presenter = None
	orig_fill = []

	def __init__(self, parent, title, presenter, fill_style):
		self.presenter = presenter
		self.cms = presenter.cms
		self.orig_fill = fill_style
		wal.OkCancelDialog.__init__(self, parent, title, style=wal.VERTICAL,
								size=(450, 370), add_line=False)

	def build(self):
		self.nb = wal.Notebook(self, on_change=self.on_change)
		tabs = [SolidFill(self.nb, self, self.cms),
				GradientFill(self.nb, self, self.cms),
				PatternFill(self.nb, self, self.cms)
				]
		for item in tabs:
			self.nb.add_page(item, item.name)
		self.pack(self.nb, fill=True, expand=True)

		if not self.orig_fill or self.orig_fill[1] == sk2_const.FILL_SOLID:
			self.nb.set_active_index(0)
		elif self.orig_fill[1] == sk2_const.FILL_GRADIENT:
			self.nb.set_active_index(1)
		elif self.orig_fill[1] == sk2_const.FILL_PATTERN:
			self.nb.set_active_index(2)

	def on_change(self, index):
		self.nb.get_active_page().activate(self.orig_fill)

	def get_result(self):
		return self.nb.get_active_page().get_result()

def fill_dlg(parent, presenter, fill_style, title=_("Fill")):
	return FillDialog(parent, title, presenter, fill_style).show()


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

SOLID_MODE_CLASSES = {
CMYK_MODE: CMYK_Panel,
RGB_MODE: RGB_Panel,
GRAY_MODE: Gray_Panel,
SPOT_MODE: SolidFillPanel,
PAL_MODE: SolidFillPanel,
EMPTY_MODE: Empty_Panel,
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

class FillTab(wal.VPanel):

	name = 'FillTab'
	built = False
	orig_fill = None

	def __init__(self, parent, dlg, cms):
		self.dlg = dlg
		self.cms = cms
		wal.VPanel.__init__(self, parent)

	def build(self):pass

	def activate(self, fill_style):
		self.orig_fill = fill_style
		if not self.built:
			self.build()
			self.built = True

	def get_result(self):
		return deepcopy(self.orig_fill)


class SolidFill(FillTab):

	name = _('Solid Fill')
	active_panel = None
	panels = {}
	new_color = None

	def activate(self, fill_style):
		FillTab.activate(self, fill_style)
		if not fill_style:
			mode = EMPTY_MODE
			self.rule_keeper.set_mode(sk2_const.FILL_EVENODD)
		else:
			self.rule_keeper.set_mode(fill_style[0])
			mode = SOLID_MODE_MAP[fill_style[2][0]]
		self.solid_keeper.set_mode(mode)
		self.on_mode_change(mode)

	def build(self):
		self.panels = {}
		panel = wal.HPanel(self)
		self.solid_keeper = wal.HToggleKeeper(panel, SOLID_MODES,
									SOLID_MODE_ICONS,
									SOLID_MODE_NAMES, self.on_mode_change)
		panel.pack(self.solid_keeper)
		panel.pack(wal.HPanel(panel), fill=True, expand=True)
		self.rule_keeper = wal.HToggleKeeper(panel, RULE_MODES,
										RULE_MODE_ICONS, RULE_MODE_NAMES)
		panel.pack(self.rule_keeper)
		self.pack(panel, fill=True, padding_all=5)
		self.pack(wal.HLine(self), fill=True)

		for item in SOLID_MODES:
			self.panels[item] = SOLID_MODE_CLASSES[item](self)
			self.panels[item].hide()

	def on_mode_change(self, mode):
		if self.active_panel:
			self.new_color = self.active_panel.get_color()
			self.remove(self.active_panel)
			self.active_panel.hide()
		self.active_panel = self.panels[mode]
		self.pack(self.active_panel, fill=True, expand=True, padding_all=5)
		self.active_panel.activate(self.cms, self.orig_fill, self.new_color)
		self.rule_keeper.set_enable(not mode == EMPTY_MODE)

	def get_result(self):
		clr = self.active_panel.get_color()
		if clr: return [self.rule_keeper.mode, sk2_const.FILL_SOLID, clr]
		else: return []

#--- Gradient fill stuff

class GradientFill(FillTab):

	name = _('Gradient Fill')

class PatternFill(FillTab):

	name = _('Pattern Fill')
