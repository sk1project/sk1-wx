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

import os, cairo

import wal

from sk1 import _, config
from sk1.resources import icons

from generic import PrefPanel

class RulersPrefs(PrefPanel):

	pid = 'Rulers'
	name = _('Ruler preferences')
	icon_id = icons.PD_PREFS_RULER

	def __init__(self, app, dlg, fmt_config=None):
		PrefPanel.__init__(self, app, dlg)

	def build(self):

		grid = wal.GridPanel(self, hgap=15, vgap=5)

		#Ruler size
		grid.pack(wal.Label(grid, _('Ruler size (px):')))
		self.ruler_size = wal.IntSpin(grid, config.ruler_size,
								(15, 30), spin_overlay=config.spin_overlay)
		grid.pack(self.ruler_size)

		#Ruler font size
		grid.pack(wal.Label(grid, _('Ruler font size (px):')))
		self.ruler_font_size = wal.IntSpin(grid, config.ruler_font_size,
								(5, 8), spin_overlay=config.spin_overlay)
		grid.pack(self.ruler_font_size)

		#Ruler bg color
		grid.pack(wal.Label(grid, _('Ruler background color:')))
		self.bg_btn = wal.ColorButton(grid, config.ruler_bg)
		grid.pack(self.bg_btn)

		#Ruler fg color
		grid.pack(wal.Label(grid, _('Ruler mark color:')))
		self.fg_btn = wal.ColorButton(grid, config.ruler_fg)
		grid.pack(self.fg_btn)

		#Small tick size
		grid.pack(wal.Label(grid, _('Small tick size (px):')))
		self.ruler_small_tick = wal.IntSpin(grid, config.ruler_small_tick,
								(2, 30), spin_overlay=config.spin_overlay)
		grid.pack(self.ruler_small_tick)

		#Large tick size
		grid.pack(wal.Label(grid, _('Large tick size (px):')))
		self.ruler_large_tick = wal.IntSpin(grid, config.ruler_large_tick,
								(2, 30), spin_overlay=config.spin_overlay)
		grid.pack(self.ruler_large_tick)

		#Vertical text shift
		grid.pack(wal.Label(grid, _('Vertical text shift (px):')))
		self.ruler_text_vshift = wal.IntSpin(grid, config.ruler_text_vshift,
								(0, 30), spin_overlay=config.spin_overlay)
		grid.pack(self.ruler_text_vshift)

		#Horizontal text shift
		grid.pack(wal.Label(grid, _('Horizontal text shift (px):')))
		self.ruler_text_hshift = wal.IntSpin(grid, config.ruler_text_hshift,
								(0, 30), spin_overlay=config.spin_overlay)
		grid.pack(self.ruler_text_hshift)

		self.pack(grid, padding_all=5)
		self.built = True

	def apply_changes(self):
		config.ruler_size = self.ruler_size.get_value()
		config.ruler_font_size = self.ruler_font_size.get_value()
		config.ruler_bg = self.bg_btn.get_value()
		config.ruler_fg = self.fg_btn.get_value()
		config.ruler_small_tick = self.ruler_small_tick.get_value()
		config.ruler_large_tick = self.ruler_large_tick.get_value()
		config.ruler_text_vshift = self.ruler_text_vshift.get_value()
		config.ruler_text_hshift = self.ruler_text_hshift.get_value()

	def restore_defaults(self):
		defaults = config.get_defaults()
		self.ruler_size.set_value(defaults['ruler_size'])
		self.ruler_font_size.set_value(defaults['ruler_font_size'])
		self.bg_btn.set_value(defaults['ruler_bg'])
		self.fg_btn.set_value(defaults['ruler_fg'])
		self.ruler_small_tick.set_value(defaults['ruler_small_tick'])
		self.ruler_large_tick.set_value(defaults['ruler_large_tick'])
		self.ruler_text_vshift.set_value(defaults['ruler_text_vshift'])
		self.ruler_text_hshift.set_value(defaults['ruler_text_hshift'])



SMALL_TICKS = [15.017, 34.373, 53.729, 73.085, 92.441, 111.797, 131.153,
150.509, 169.865, 189.221, 208.577, 227.933, 247.289, 266.645, 286.001,
305.357, 324.714, 344.070, ]

TEXT_TICKS = [(15.017, '-100'), (53.729, '-75'), (92.441, '-50'),
(131.153, '-25'), (169.865, '0'), (208.577, '25'),
(247.289, '50'), (286.001, '75'), (324.714, '100'), ]

HFONT = {}
VFONT = {}

def load_font():
	fntdir = 'ruler-font%dpx' % config.ruler_font_size
	fntdir = os.path.join(config.resource_dir, 'fonts', fntdir)
	for char in '.,-0123456789':
		if char in '.,': file_name = os.path.join(fntdir, 'hdot.png')
		else: file_name = os.path.join(fntdir, 'h%s.png' % char)
		surface = cairo.ImageSurface.create_from_png(file_name)
		HFONT[char] = (surface.get_width(), surface)

		if char in '.,': file_name = os.path.join(fntdir, 'vdot.png')
		else: file_name = os.path.join(fntdir, 'v%s.png' % char)
		surface = cairo.ImageSurface.create_from_png(file_name)
		VFONT[char] = (surface.get_height(), surface)

class RulerTest(wal.HPanel):

	def __init__(self, parent, prefs):
		self.prefs = prefs
		wal.HPanel.__init__(self, parent)
		self.add((360, self.prefs.ruler_size.get_value()))

