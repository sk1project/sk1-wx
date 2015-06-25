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
								(15, 30), spin_overlay=config.spin_overlay,
								onchange=self.update_ruler_size)
		grid.pack(self.ruler_size)

		#Ruler font size
		grid.pack(wal.Label(grid, _('Ruler font size (px):')))
		self.ruler_font_size = wal.IntSpin(grid, config.ruler_font_size,
								(5, 8), spin_overlay=config.spin_overlay,
								onchange=self.update_ruler_font)
		grid.pack(self.ruler_font_size)

		#Ruler bg color
		grid.pack(wal.Label(grid, _('Ruler background color:')))
		self.bg_btn = wal.ColorButton(grid, config.ruler_bg,
								onchange=self.update_ruler)
		grid.pack(self.bg_btn)

		#Ruler fg color
		grid.pack(wal.Label(grid, _('Ruler mark color:')))
		self.fg_btn = wal.ColorButton(grid, config.ruler_fg,
								onchange=self.update_ruler)
		grid.pack(self.fg_btn)

		#Small tick size
		grid.pack(wal.Label(grid, _('Small tick size (px):')))
		self.ruler_small_tick = wal.IntSpin(grid, config.ruler_small_tick,
								(2, 30), spin_overlay=config.spin_overlay,
								onchange=self.update_ruler)
		grid.pack(self.ruler_small_tick)

		#Large tick size
		grid.pack(wal.Label(grid, _('Large tick size (px):')))
		self.ruler_large_tick = wal.IntSpin(grid, config.ruler_large_tick,
								(2, 30), spin_overlay=config.spin_overlay,
								onchange=self.update_ruler)
		grid.pack(self.ruler_large_tick)

		#Vertical text shift
		grid.pack(wal.Label(grid, _('Text vertical shift (px):')))
		self.ruler_text_vshift = wal.IntSpin(grid, config.ruler_text_vshift,
								(0, 30), spin_overlay=config.spin_overlay,
								onchange=self.update_ruler)
		grid.pack(self.ruler_text_vshift)

		#Horizontal text shift
		grid.pack(wal.Label(grid, _('Text horizontal shift (px):')))
		self.ruler_text_hshift = wal.IntSpin(grid, config.ruler_text_hshift,
								(0, 30), spin_overlay=config.spin_overlay,
								onchange=self.update_ruler)
		grid.pack(self.ruler_text_hshift)

		self.pack(grid, padding_all=5)

		#Testing ruler
		self.pack(wal.Label(self, _('Testing ruler:'), fontbold=True),
				padding_all=10)
		panel = wal.HPanel(self)
		panel.add((360, 1))
		panel.set_bg(wal.UI_COLORS['dark_shadow'])
		self.pack(panel)

		self.ruler = RulerTest(self, self)
		self.pack(self.ruler)

		self.built = True

	def update_ruler_font(self):
		self.ruler.load_font(self.ruler_font_size.get_value())
		self.ruler.refresh()

	def update_ruler(self):
		self.ruler.refresh()

	def update_ruler_size(self):
		self.ruler.set_size()

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
		self.update_ruler_size()
		self.update_ruler_font()



SMALL_TICKS = [15.017, 34.373, 53.729, 73.085, 92.441, 111.797, 131.153,
150.509, 169.865, 189.221, 208.577, 227.933, 247.289, 266.645, 286.001,
305.357, 324.714, 344.070, ]

TEXT_TICKS = [(15.017, '-100'), (53.729, '-75'), (92.441, '-50'),
(131.153, '-25'), (169.865, '0'), (208.577, '25'),
(247.289, '50'), (286.001, '75'), (324.714, '100'), ]

class RulerTest(wal.HPanel, wal.Canvas):

	font = {}
	surface = None
	ctx = None

	def __init__(self, parent, prefs):
		self.prefs = prefs
		wal.HPanel.__init__(self, parent)
		wal.Canvas.__init__(self)
		self.set_size()
		self.set_bg(wal.WHITE)
		self.load_font(self.prefs.ruler_font_size.get_value())

	def set_size(self):
		self.remove_all()
		self.add((360, self.prefs.ruler_size.get_value()))
		self.parent.layout()

	def load_font(self, font_size):
		fntdir = 'ruler-font%dpx' % font_size
		fntdir = os.path.join(config.resource_dir, 'fonts', fntdir)
		for char in '.,-0123456789':
			if char in '.,': file_name = os.path.join(fntdir, 'hdot.png')
			else: file_name = os.path.join(fntdir, 'h%s.png' % char)
			surface = cairo.ImageSurface.create_from_png(file_name)
			self.font[char] = (surface.get_width(), surface)

	def paint(self):
		w, h = self.get_size()
		shift = 0
		if wal.is_msw():shift = 1
		fmt = cairo.FORMAT_RGB24
		self.surface = cairo.ImageSurface(fmt, w - shift, h - shift)
		self.ctx = cairo.Context(self.surface)
		self.ctx.set_matrix(cairo.Matrix(1.0, 0.0, 0.0, 1.0, 0.0, 0.0))
		self.ctx.set_source_rgb(*self.prefs.bg_btn.get_value())
		self.ctx.paint()
		self.ctx.set_antialias(cairo.ANTIALIAS_NONE)
		self.ctx.set_line_width(1.0)
		self.ctx.set_dash([])
		self.ctx.set_source_rgb(*self.prefs.fg_btn.get_value())

		self.ctx.move_to(0, h)
		self.ctx.line_to(w, h)

		small_l = self.prefs.ruler_small_tick.get_value()
		for item in SMALL_TICKS:
			self.ctx.move_to(item, h - small_l)
			self.ctx.line_to(item, h - 1)

		large_l = self.prefs.ruler_large_tick.get_value()
		for pos, txt in TEXT_TICKS:
			self.ctx.move_to(pos, h - large_l)
			self.ctx.line_to(pos, h - 1)

		self.ctx.stroke()

		vshift = self.prefs.ruler_text_vshift.get_value()
		hshift = self.prefs.ruler_text_hshift.get_value()
		for pos, txt in TEXT_TICKS:
			for character in txt:
				data = self.font[character]
				position = int(pos) + hshift
				self.ctx.set_source_surface(data[1], position, vshift)
				self.ctx.paint()
				pos += data[0]

		self.draw_surface(self.surface)
