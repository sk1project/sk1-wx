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
from uc2.cms import get_registration_black, color_to_spot, rgb_to_hexcolor
from sk1 import _
from sk1.resources import icons

from colorctrls import PaletteSwatch, CMYK_Mixer, RGB_Mixer, Gray_Mixer, \
SPOT_Mixer, Palette_Mixer
from colorctrls import FillColorRefPanel, MiniPalette
from colorctrls import CMYK_PALETTE, RGB_PALETTE, GRAY_PALETTE, SPOT_PALETTE

#--- Solid fill panels

class SolidFillPanel(wal.VPanel):

	orig_fill = None
	cms = None
	built = False
	new_color = None

	def __init__(self, parent, app):
		self.app = app
		wal.VPanel.__init__(self, parent)

	def build(self):
		self.pack(wal.Label(self, self.orig_fill.__str__()))

	def activate(self, cms, orig_fill, new_color):
		self.orig_fill = orig_fill
		self.new_color = new_color
		if self.new_color and not self.new_color[0] == uc2const.COLOR_SPOT:
			self.new_color[3] = ''
		self.cms = cms
		if not self.built:
			self.build()
			self.built = True
		self.show()

	def get_color(self):
		return self.new_color

	def set_orig_fill(self):
		self.activate(self.cms, self.orig_fill, [])


class CMYK_Panel(SolidFillPanel):

	color_sliders = []
	color_spins = []

	def build(self):

		self.mixer = CMYK_Mixer(self, self.cms, onchange=self.update)
		self.pack(self.mixer)

		self.pack(wal.HPanel(self), fill=True, expand=True)
		self.pack(wal.HLine(self), fill=True, padding=5)

		bot_panel = wal.HPanel(self)
		self.refpanel = FillColorRefPanel(bot_panel, self.cms, [], [],
										on_orig=self.set_orig_fill)
		bot_panel.pack(self.refpanel)
		bot_panel.pack(wal.HPanel(bot_panel), fill=True, expand=True)

		minipal = MiniPalette(bot_panel, self.cms, CMYK_PALETTE,
							self.on_palette_click)
		bot_panel.pack(minipal, padding_all=5)

		self.pack(bot_panel, fill=True)

	def on_palette_click(self, color):
		self.new_color = color
		self.update()

	def update(self):
		self.mixer.set_color(self.new_color)
		self.refpanel.update(self.orig_fill, self.new_color)

	def activate(self, cms, orig_fill, new_color):
		fill = None
		if orig_fill and orig_fill[1] == sk2_const.FILL_SOLID:
			fill = orig_fill
		if not new_color and fill:
			new_color = cms.get_cmyk_color(fill[2])
		elif not new_color and not fill:
			new_color = [uc2const.COLOR_CMYK, [0.0, 0.0, 0.0, 1.0], 1.0, '']
		else:
			new_color = cms.get_cmyk_color(new_color)
		SolidFillPanel.activate(self, cms, orig_fill, new_color)
		self.update()

class RGB_Panel(SolidFillPanel):

	def build(self):

		self.mixer = RGB_Mixer(self, self.cms, onchange=self.update)
		self.pack(self.mixer)

		self.pack(wal.HLine(self), fill=True, padding=5)

		bot_panel = wal.HPanel(self)
		self.refpanel = FillColorRefPanel(bot_panel, self.cms, [], [],
										on_orig=self.set_orig_fill)
		bot_panel.pack(self.refpanel)
		bot_panel.pack(wal.HPanel(bot_panel), fill=True, expand=True)

		minipal = MiniPalette(bot_panel, self.cms, RGB_PALETTE,
							self.on_palette_click)
		bot_panel.pack(minipal, padding_all=5)

		self.pack(bot_panel, fill=True)

	def on_palette_click(self, color):
		self.new_color = color
		self.update()

	def update(self):
		self.mixer.set_color(self.new_color)
		self.refpanel.update(self.orig_fill, self.new_color)

	def activate(self, cms, orig_fill, new_color):
		fill = None
		if orig_fill and orig_fill[1] == sk2_const.FILL_SOLID:
			fill = orig_fill
		if not new_color and fill:
			new_color = cms.get_rgb_color(fill[2])
		elif not new_color and not fill:
			new_color = [uc2const.COLOR_RGB, [0.0, 0.0, 0.0], 1.0, '']
		else:
			new_color = cms.get_rgb_color(new_color)
		SolidFillPanel.activate(self, cms, orig_fill, new_color)
		self.update()


class Gray_Panel(SolidFillPanel):

	def build(self):
		self.pack(wal.HPanel(self), fill=True, expand=True)

		self.mixer = Gray_Mixer(self, self.cms, onchange=self.update)
		self.pack(self.mixer)

		self.pack(wal.HPanel(self), fill=True, expand=True)
		self.pack(wal.HLine(self), fill=True, padding=5)

		bot_panel = wal.HPanel(self)
		self.refpanel = FillColorRefPanel(bot_panel, self.cms, [], [],
										on_orig=self.set_orig_fill)
		bot_panel.pack(self.refpanel)
		bot_panel.pack(wal.HPanel(bot_panel), fill=True, expand=True)

		minipal = MiniPalette(bot_panel, self.cms, GRAY_PALETTE,
							self.on_palette_click)
		bot_panel.pack(minipal, padding_all=5)

		self.pack(bot_panel, fill=True)

	def on_palette_click(self, color):
		self.new_color = color
		self.update()

	def update(self):
		self.mixer.set_color(self.new_color)
		self.refpanel.update(self.orig_fill, self.new_color)

	def activate(self, cms, orig_fill, new_color):
		fill = None
		if orig_fill and orig_fill[1] == sk2_const.FILL_SOLID:
			fill = orig_fill
		if not new_color and fill:
			new_color = cms.get_grayscale_color(fill[2])
		elif not new_color and not fill:
			new_color = [uc2const.COLOR_GRAY, [0.0, ], 1.0, '']
		else:
			new_color = cms.get_grayscale_color(new_color)
		SolidFillPanel.activate(self, cms, orig_fill, new_color)
		self.update()

class SPOT_Panel(SolidFillPanel):

	def build(self):
		self.pack(wal.HPanel(self), fill=True, expand=True)
		self.mixer = SPOT_Mixer(self, self.cms, onchange=self.update)
		self.pack(self.mixer)

		self.pack(wal.HPanel(self), fill=True, expand=True)
		self.pack(wal.HLine(self), fill=True, padding=5)

		bot_panel = wal.HPanel(self)
		self.refpanel = FillColorRefPanel(bot_panel, self.cms, [], [],
										on_orig=self.set_orig_fill)
		bot_panel.pack(self.refpanel)
		bot_panel.pack(wal.HPanel(bot_panel), fill=True, expand=True)

		minipal = MiniPalette(bot_panel, self.cms, SPOT_PALETTE,
							self.on_palette_click)
		bot_panel.pack(minipal, padding_all=5)

		self.pack(bot_panel, fill=True)

	def on_palette_click(self, color):
		self.new_color = color
		self.update()

	def update(self):
		self.mixer.set_color(self.new_color)
		self.refpanel.update(self.orig_fill, self.new_color)

	def activate(self, cms, orig_fill, new_color):
		fill = None
		if orig_fill and orig_fill[1] == sk2_const.FILL_SOLID:
			fill = orig_fill
		if not new_color and fill:
			new_color = color_to_spot(fill[2])
		elif not new_color and not fill:
			new_color = get_registration_black()
		else:
			new_color = color_to_spot(new_color)
		if not new_color[3]:
			new_color[3] = rgb_to_hexcolor(cms.get_rgb_color(new_color)[1])
		SolidFillPanel.activate(self, cms, orig_fill, new_color)
		self.update()

class Empty_Panel(SolidFillPanel):

	def build(self):
		self.pack(wal.HPanel(self), fill=True, expand=True)
		self.pack(PaletteSwatch(self, self.cms, [], (250, 150)))
		txt = _('Empty pattern selected')
		self.pack(wal.Label(self, txt), padding=10)
		self.pack(wal.HPanel(self), fill=True, expand=True)

	def activate(self, cms, orig_fill, new_color):
		new_color = []
		SolidFillPanel.activate(self, cms, orig_fill, new_color)

class Palette_Panel(SolidFillPanel):

	def build(self):
		self.mixer = Palette_Mixer(self, self.app, self.cms,
								onchange=self.set_color)
		self.pack(self.mixer, fill=True, expand=True)

	def activate(self, cms, orig_fill, new_color):
		new_color = get_registration_black()
		SolidFillPanel.activate(self, cms, orig_fill, new_color)
		self.mixer.on_change()

	def set_color(self, color):
		self.new_color = color

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
SPOT_MODE: SPOT_Panel,
PAL_MODE: Palette_Panel,
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
		self.app = dlg.app
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
	callback = None
	use_rule = True

	def activate(self, fill_style, use_rule=True, onmodechange=None):
		if onmodechange: self.callback = onmodechange
		self.use_rule = use_rule
		FillTab.activate(self, fill_style)
		if not fill_style:
			mode = EMPTY_MODE
			self.rule_keeper.set_mode(sk2_const.FILL_EVENODD)
		else:
			self.rule_keeper.set_mode(fill_style[0])
			if fill_style[1] in [sk2_const.FILL_GRADIENT,
								sk2_const.FILL_PATTERN]:
				mode = CMYK_MODE
			else:
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
		if not self.use_rule: self.rule_keeper.set_visible(False)
		self.pack(panel, fill=True, padding_all=5)
		self.pack(wal.HLine(self), fill=True)

		for item in SOLID_MODES:
			self.panels[item] = SOLID_MODE_CLASSES[item](self, self.app)
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
		if self.callback: self.callback()

	def get_result(self):
		clr = self.active_panel.get_color()
		if clr: return [self.rule_keeper.mode, sk2_const.FILL_SOLID, clr]
		else: return []

#--- Gradient fill stuff

class GradientFill(FillTab):

	name = _('Gradient Fill')

class PatternFill(FillTab):

	name = _('Pattern Fill')
