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

from uc2 import uc2const, cms
from sk1 import _
from sk1.resources import icons, get_icon

CMYK_PALETTE = [
[uc2const.COLOR_CMYK, [1.0, 1.0, 1.0, 1.0], 1.0, 'CMYK Registration'],
[uc2const.COLOR_CMYK, [0.0, 0.0, 0.0, 1.0], 1.0, 'Black'],
[uc2const.COLOR_CMYK, [0.0, 0.0, 0.0, 0.7], 1.0, '70% Black'],
[uc2const.COLOR_CMYK, [0.0, 0.0, 0.0, 0.5], 1.0, '50% Black'],
[uc2const.COLOR_CMYK, [0.0, 0.0, 0.0, 0.2], 1.0, '20% Black'],
[uc2const.COLOR_CMYK, [0.000000, 0.000000, 0.000000, 0.000000], 1.0, 'White'],
[uc2const.COLOR_CMYK, [1.0, 0.000000, 0.0, 0.000000], 1.0, 'Cyan'],
[uc2const.COLOR_CMYK, [0.0, 1.0, 0.000000, 0.000000], 1.0, 'Magenta'],
[uc2const.COLOR_CMYK, [0.000000, 0.000000, 1.0, 0.000000], 1.0, 'Yellow'],
[uc2const.COLOR_CMYK, [0.000000, 1.0, 1.0, 0.000000], 1.0, 'Red'],
[uc2const.COLOR_CMYK, [1.0, 0.0, 1.0, 0.0], 1.0, 'Green'],
[uc2const.COLOR_CMYK, [1.0, 1.0, 0.0, 0.0], 1.0, 'Blue'], ]

RGB_PALETTE = [
[uc2const.COLOR_RGB, [0.0, 0.0, 0.0], 1.0, 'Black'],
[uc2const.COLOR_RGB, [0.2, 0.2, 0.2], 1.0, '80% Black'],
[uc2const.COLOR_RGB, [0.4, 0.4, 0.4], 1.0, '60% Black'],
[uc2const.COLOR_RGB, [0.6, 0.6, 0.6], 1.0, '40% Black'],
[uc2const.COLOR_RGB, [0.8, 0.8, 0.8], 1.0, '20% Black'],
[uc2const.COLOR_RGB, [1.0, 1.0, 1.0], 1.0, 'White'],
[uc2const.COLOR_RGB, [1.0, 0.0, 0.0], 1.0, 'Red'],
[uc2const.COLOR_RGB, [0.0, 1.0, 0.0], 1.0, 'Green'],
[uc2const.COLOR_RGB, [0.0, 0.0, 1.0], 1.0, 'Blue'],
[uc2const.COLOR_RGB, [0.0, 1.0, 1.0], 1.0, 'Cyan'],
[uc2const.COLOR_RGB, [1.0, 0.0, 1.0], 1.0, 'Magenta'],
[uc2const.COLOR_RGB, [1.0, 1.0, 0.0], 1.0, 'Yellow'], ]

GRAY_PALETTE = [
[uc2const.COLOR_GRAY, [0.0, ], 1.0, 'Black'],
[uc2const.COLOR_GRAY, [0.1, ], 1.0, '90% Black'],
[uc2const.COLOR_GRAY, [0.2, ], 1.0, '80% Black'],
[uc2const.COLOR_GRAY, [0.3, ], 1.0, '70% Black'],
[uc2const.COLOR_GRAY, [0.4, ], 1.0, '60% Black'],
[uc2const.COLOR_GRAY, [0.5, ], 1.0, '50% Black'],
[uc2const.COLOR_GRAY, [0.6, ], 1.0, '40% Black'],
[uc2const.COLOR_GRAY, [0.7, ], 1.0, '30% Black'],
[uc2const.COLOR_GRAY, [0.8, ], 1.0, '20% Black'],
[uc2const.COLOR_GRAY, [0.9, ], 1.0, '10% Black'],
[uc2const.COLOR_GRAY, [0.95, ], 1.0, '5% Black'],
[uc2const.COLOR_GRAY, [1.0, ], 1.0, 'White'],
]

REG_COLOR = [1.0, 1.0, 1.0, 1.0]

class HexField(wal.Entry):

	color = None
	callback = None
	hexcolor = ''

	def __init__(self, parent, onchange=None):
		wal.Entry.__init__(self, parent, width=8, onchange=self.on_change,
						onenter=self.on_enter)
		if onchange: self.callback = onchange

	def set_color(self, color):
		self.color = color
		if color[2] == 1.0:
			self.set_value(cms.rgb_to_hexcolor(color[1]))
		else:
			self.set_value(cms.rgba_to_hexcolor(color[1] + [color[2], ]))
		self.hexcolor = self.get_value()

	def get_color(self):
		return self.hexcolor

	def _check_input(self):
		ret = ''
		val = self.get_value()
		if val:
			if val[0] == '#':
				seq = val[1:].lower()
			else:
				seq = val.lower()
			ret += '#'
			for item in seq:
				if item in '0123456789abcdef':
					ret += item
		if not ret == val:
			self.set_value(ret)

	def on_enter(self):
		val = self.get_value()
		if len(val) in (4, 7, 9):
			if len(val) == 4:
				self.hexcolor = '#' + val[1] * 2 + val[2] * 2 + val[3] * 2
				self.set_value(self.hexcolor)
			if self.callback: self.callback()

	def on_change(self):
		self._check_input()
		val = self.get_value()
		if len(val) in (7, 9):
			self.hexcolor = val
			if self.callback: self.callback()


class SwatchCanvas(wal.SensitiveCanvas):

	fill = None
	color = None
	cms = None
	border = ''
	even_odd = False
	reg_icon = None

	def __init__(self, border='', even_odd=False):
		self.border = border
		self.even_odd = even_odd
		wal.SensitiveCanvas.__init__(self)

	def paint(self):
		self.draw_background()
		self.draw_color()
		self.draw_border()

	def draw_background(self):
		if not self.color or not self.color[2] < 1.0: return
		w, h = self.get_size()
		x1 = y1 = 0
		flag_y = self.even_odd
		self.set_stroke()
		while y1 < h:
			flag_x = flag_y
			while x1 < w:
				clr = wal.WHITE
				if not flag_x: clr = wal.LIGHT_GRAY
				self.set_fill(clr)
				self.draw_rect(x1, y1, 10, 10)
				flag_x = not flag_x
				x1 += 10
			flag_y = not flag_y
			y1 += 10
			x1 = 0

	def draw_color(self):
		if self.color is None: return
		if not self.color:
			self.draw_empty_pattern()
			return
		w, h = self.get_size()
		if self.color[2] < 1.0:
			self.set_gc_stroke()
			self.set_gc_fill(self.cms.get_rgba_color255(self.color))
			self.gc_draw_rect(0, 0, w, h)
		else:
			self.set_stroke()
			self.set_fill(self.cms.get_rgb_color255(self.color))
			self.draw_rect(0, 0, w, h)
		if self.color[1] == REG_COLOR:
			if not self.reg_icon:
				self.reg_icon = get_icon(icons.REG_SIGN, size=wal.DEF_SIZE)
			x = (w - 19) / 2
			y = (h - 19) / 2
			self.draw_bitmap(self.reg_icon, x, y)

	def draw_empty_pattern(self):
		w, h = self.get_size()
		self.set_stroke()
		self.set_fill(wal.WHITE)
		self.draw_rect(0, 0, w, h)
		self.set_gc_stroke(wal.RED)
		self.set_gc_fill()
		self.gc_draw_line(0, 0, w, h)
		self.gc_draw_line(w, 0, 0, h)
		self.set_stroke(wal.BLACK)
		self.set_fill()
		self.draw_rect(0, 0, w, h)

	def draw_border(self):
		if not self.border: return
		x0 = y0 = 0
		x1, y1 = self.get_size()
		if not 'n' in self.border: y0 = -1
		if not 'w' in self.border: x0 = -1
		if not 'e' in self.border: x1 += 1
		if not 's' in self.border: y1 += 1
		self.set_stroke(wal.BLACK)
		self.set_fill()
		self.draw_rect(x0, y0, x1 - x0, y1 - y0)

class ColorSwatch(wal.VPanel, SwatchCanvas):

	callback = None

	def __init__(self, parent, cms, color, size=(20, 20), onclick=None):
		self.color = color
		self.cms = cms
		wal.VPanel.__init__(self, parent)
		SwatchCanvas.__init__(self)
		self.pack(size)
		if self.color and self.color[3]:
			self.set_tooltip(self.color[3])
		if onclick: self.callback = onclick

	def mouse_left_up(self, point):
		if self.callback: self.callback(deepcopy(self.color))

class AlphaColorSwatch(wal.VPanel, SwatchCanvas):

	callback = None

	def __init__(self, parent, cms, color, size=(20, 20), border='wes',
				even_odd=False):
		self.color = color
		self.cms = cms
		wal.VPanel.__init__(self, parent)
		SwatchCanvas.__init__(self, border, even_odd)
		self.pack(size)

	def set_color(self, color):
		self.color = color
		self.refresh()

class PatternSwatch(wal.VPanel, SwatchCanvas):

	callback = None

	def __init__(self, parent, cms, fill, size=(20, 20), border='new',
				even_odd=True, onclick=None):
		self.cms = cms
		wal.VPanel.__init__(self, parent)
		SwatchCanvas.__init__(self, border, even_odd)
		self.pack(size)
		self.set_swatch_fill(fill)
		if onclick: self.callback = onclick

	def mouse_left_up(self, point):
		if self.callback: self.callback()

	def set_swatch_fill(self, fill):
		if fill:
			self.color = fill[2]
		else:
			self.color = []
		self.refresh()

class MiniPalette(wal.VPanel):

	callback = None

	def __init__(self, parent, cms, palette=CMYK_PALETTE, onclick=None):
		wal.VPanel.__init__(self, parent)
		self.set_bg(wal.BLACK)
		grid = wal.GridPanel(parent, 2, 6, 1, 1)
		grid.set_bg(wal.BLACK)
		for item in palette:
			grid.pack(ColorSwatch(grid, cms, item, (40, 20), self.on_click))
		self.pack(grid, padding_all=1)
		if onclick: self.callback = onclick

	def on_click(self, color):
		if self.callback: self.callback(color)

class FillColorRefPanel(wal.VPanel):

	def __init__(self, parent, cms, fill, new_color, on_orig=None):
		wal.VPanel.__init__(self, parent)
		grid = wal.GridPanel(self, hgap=5)
		grid.pack(wal.Label(grid, _('Old fill:')))

		self.before_swatch = PatternSwatch(grid, cms, fill, (70, 30),
										onclick=on_orig)
		grid.pack(self.before_swatch)

		grid.pack(wal.Label(grid, _('New fill:')))

		self.after_swatch = AlphaColorSwatch(grid, cms, new_color, (70, 30))
		grid.pack(self.after_swatch)

		self.pack(grid, padding_all=2)

	def update(self, fill, new_color):
		self.before_swatch.set_swatch_fill(fill)
		self.after_swatch.set_color(new_color)


class ColoredSlider(wal.VPanel, wal.SensitiveCanvas):

	start_clr = wal.BLACK
	stop_clr = wal.WHITE
	value = 0.0
	knob = None
	check_flag = False
	callback = None

	def __init__(self, parent, size=20, onchange=None):
		wal.VPanel.__init__(self, parent)
		wal.SensitiveCanvas.__init__(self, check_move=True)
		self.pack((256 + 8, size + 10))
		self.knob = get_icon(icons.SLIDER_KNOB, size=wal.DEF_SIZE)
		if onchange:
			self.callback = onchange

	def paint(self):
		w, h = self.get_size()
		w -= 6;h -= 10
		x = 3;y = 5
		self.draw_linear_gradient((x, y, w, h), self.start_clr, self.stop_clr)
		self.set_fill()
		self.set_stroke(wal.BLACK)
		self.draw_rect(x, y, w, h)
		pos = int(self.value * 255.0) + 1
		self.draw_bitmap(self.knob, pos, y + h)

	def _set_value(self, val):
		if val < 4:val = 4
		if val > 259:val = 259
		val = (val - 4) / 255.0
		self.value = val
		self.refresh()
		if self.callback: self.callback()

	def set_value(self, val, start_clr=wal.BLACK, stop_clr=wal.WHITE):
		self.value = val
		self.start_clr = start_clr
		self.stop_clr = stop_clr
		self.refresh()

	def get_value(self):
		return self.value

	def mouse_left_down(self, val):
		self.check_flag = True
		self._set_value(val[0])

	def mouse_move(self, val):
		if self.check_flag:
			self._set_value(val[0])

	def mouse_left_up(self, val):
		self.check_flag = False
		self._set_value(val[0])

class ColoredAlphaSlider(ColoredSlider):

	def __init__(self, parent, size=20, onchange=None):
		ColoredSlider.__init__(self, parent, size, onchange)

	def paint(self):
		w, h = self.get_size()
		w -= 6;h -= 10
		x = 3;y = 5
		x1 = y1 = 0
		flag_y = True
		self.set_stroke()
		while y + y1 < h:
			flag_x = flag_y
			while x + x1 < w:
				clr = wal.WHITE
				if not flag_x: clr = wal.LIGHT_GRAY
				self.set_fill(clr)
				self.draw_rect(x + x1, y + y1, 10, 10)
				flag_x = not flag_x
				x1 += 10
			flag_y = not flag_y
			y1 += 10
			x1 = 0

		w, h = self.get_size()
		w -= 6;h -= 10
		x = 3;y = 5
		rect = (x, y, w, h)
		self.gc_draw_linear_gradient(rect, self.start_clr, self.stop_clr)
		self.set_fill()
		self.set_stroke(wal.BLACK)
		self.draw_rect(x, y, w, h)
		pos = int(self.value * 255.0) + 1
		self.draw_bitmap(self.knob, pos, y + h)

#--- Solid fill panels

class SolidFillPanel(wal.VPanel):

	orig_fill = None
	cms = None
	built = False
	new_color = None

	def __init__(self, parent):
		wal.VPanel.__init__(self, parent)

	def build(self):
		self.pack(wal.Label(self, self.orig_fill.__str__()))

	def activate(self, cms, orig_fill, new_color):
		self.orig_fill = orig_fill
		self.new_color = new_color
		if self.new_color: self.new_color[3] = ''
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

		self.color_sliders = []
		self.color_spins = []
		grid = wal.GridPanel(self, 4, 4, 3, 5)

		labels = ['C:', 'M:', 'Y:', 'K:']
		for item in labels:
			grid.pack(wal.Label(grid, item))
			self.color_sliders.append(ColoredSlider(grid,
										onchange=self.on_slider_change))
			grid.pack(self.color_sliders[-1])
			self.color_spins.append(wal.FloatSpin(grid,
									range_val=(0.0, 100.0), width=5,
									onchange=self.on_change,
									onenter=self.on_change))
			grid.pack(self.color_spins[-1])
			grid.pack(wal.Label(grid, '%'))

		grid.pack(wal.Label(grid, 'A:'))
		self.alpha_slider = ColoredAlphaSlider(grid,
										onchange=self.on_slider_change)
		grid.pack(self.alpha_slider)
		self.alpha_spin = wal.FloatSpin(grid,
									range_val=(0.0, 100.0), width=5,
									onchange=self.on_change,
									onenter=self.on_change)
		grid.pack(self.alpha_spin)
		grid.pack(wal.Label(grid, '%'))

		self.pack(grid)

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

	def on_slider_change(self):
		color_vals = []
		for item in self.color_sliders:
			color_vals.append(item.get_value())
		self.new_color[1] = color_vals
		self.new_color[2] = self.alpha_slider.get_value()
		self.update()

	def on_change(self):
		color_vals = []
		for item in self.color_spins:
			color_vals.append(item.get_value() / 100.0)
		self.new_color[1] = color_vals
		self.new_color[2] = self.alpha_spin.get_value() / 100.0
		self.update()

	def on_palette_click(self, color):
		self.new_color = color
		self.update()

	def update(self):
		for item in self.color_spins:
			index = self.color_spins.index(item)
			item.set_value(self.new_color[1][index] * 100.0)
		for item in self.color_sliders:
			index = self.color_sliders.index(item)
			start_clr = deepcopy(self.new_color)
			stop_clr = deepcopy(self.new_color)
			start_clr[1][index] = 0.0
			stop_clr[1][index] = 1.0
			start_clr = self.cms.get_rgb_color255(start_clr)
			stop_clr = self.cms.get_rgb_color255(stop_clr)
			item.set_value(self.new_color[1][index], start_clr, stop_clr)

		start_clr = deepcopy(self.new_color)
		start_clr[2] = 0.0
		stop_clr = deepcopy(self.new_color)
		stop_clr[2] = 1.0
		start_clr = self.cms.get_rgba_color255(start_clr)
		stop_clr = self.cms.get_rgba_color255(stop_clr)
		self.alpha_slider.set_value(self.new_color[2], start_clr, stop_clr)
		self.alpha_spin.set_value(self.new_color[2] * 100.0)
		self.refpanel.update(self.orig_fill, self.new_color)

	def activate(self, cms, orig_fill, new_color):
		if not new_color and orig_fill:
			new_color = cms.get_cmyk_color(orig_fill[2])
		elif not new_color and not orig_fill:
			new_color = [uc2const.COLOR_CMYK, [0.0, 0.0, 0.0, 1.0], 1.0, '']
		else:
			new_color = cms.get_cmyk_color(new_color)
		SolidFillPanel.activate(self, cms, orig_fill, new_color)
		self.update()

class RGB_Panel(SolidFillPanel):

	def build(self):

		self.color_sliders = []
		self.color_spins = []
		grid = wal.GridPanel(self, 4, 3, 3, 5)

		labels = ['R:', 'G:', 'B:']
		for item in labels:
			grid.pack(wal.Label(grid, item))
			self.color_sliders.append(ColoredSlider(grid,
										onchange=self.on_slider_change))
			grid.pack(self.color_sliders[-1])
			self.color_spins.append(wal.IntSpin(grid,
									range_val=(0, 255), width=4,
									onchange=self.on_change,
									onenter=self.on_change))
			grid.pack(self.color_spins[-1])

		grid.pack(wal.Label(grid, 'A:'))
		self.alpha_slider = ColoredAlphaSlider(grid,
										onchange=self.on_slider_change)
		grid.pack(self.alpha_slider)
		self.alpha_spin = wal.IntSpin(grid,
									range_val=(0, 255), width=4,
									onchange=self.on_change,
									onenter=self.on_change)
		grid.pack(self.alpha_spin)

		self.pack(grid)

		self.pack(wal.HPanel(self), fill=True, expand=True)

		html_panel = wal.HPanel(self)
		html_panel.pack(wal.Label(html_panel, _('HTML notation:')), padding=5)
		self.html = HexField(html_panel, onchange=self.on_hex_change)
		html_panel.pack(self.html)
		self.pack(html_panel, padding=5)

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

	def on_hex_change(self):
		hexcolor = self.html.get_color()
		if len(hexcolor) == 7:
			self.new_color[1] = cms.hexcolor_to_rgb(hexcolor)
			self.new_color[2] = 1.0
		elif len(hexcolor) == 9:
			r, g, b, a = cms.hexcolor_to_rgba(hexcolor)
			self.new_color[1] = [r, g, b]
			self.new_color[2] = a
		self.update()

	def on_slider_change(self):
		color_vals = []
		for item in self.color_sliders:
			color_vals.append(item.get_value())
		self.new_color[1] = color_vals
		self.new_color[2] = self.alpha_slider.get_value()
		self.update()

	def on_change(self):
		color_vals = []
		for item in self.color_spins:
			color_vals.append(item.get_value() / 255.0)
		self.new_color[1] = color_vals
		self.new_color[2] = self.alpha_spin.get_value() / 255.0
		self.update()

	def on_palette_click(self, color):
		self.new_color = color
		self.update()

	def update(self):
		for item in self.color_spins:
			index = self.color_spins.index(item)
			item.set_value(self.new_color[1][index] * 255.0)
		for item in self.color_sliders:
			index = self.color_sliders.index(item)
			start_clr = deepcopy(self.new_color)
			stop_clr = deepcopy(self.new_color)
			start_clr[1][index] = 0.0
			stop_clr[1][index] = 1.0
			start_clr = self.cms.get_rgb_color255(start_clr)
			stop_clr = self.cms.get_rgb_color255(stop_clr)
			item.set_value(self.new_color[1][index], start_clr, stop_clr)

		start_clr = deepcopy(self.new_color)
		start_clr[2] = 0.0
		stop_clr = deepcopy(self.new_color)
		stop_clr[2] = 1.0
		start_clr = self.cms.get_rgba_color255(start_clr)
		stop_clr = self.cms.get_rgba_color255(stop_clr)
		self.alpha_slider.set_value(self.new_color[2], start_clr, stop_clr)
		self.alpha_spin.set_value(self.new_color[2] * 255.0)
		self.refpanel.update(self.orig_fill, self.new_color)
		self.html.set_color(self.new_color)

	def activate(self, cms, orig_fill, new_color):
		if not new_color and orig_fill:
			new_color = cms.get_rgb_color(orig_fill[2])
		elif not new_color and not orig_fill:
			new_color = [uc2const.COLOR_RGB, [0.0, 0.0, 0.0], 1.0, '']
		else:
			new_color = cms.get_rgb_color(new_color)
		SolidFillPanel.activate(self, cms, orig_fill, new_color)
		self.update()

class Gray_Panel(SolidFillPanel):

	def build(self):
		self.pack(wal.HPanel(self), fill=True, expand=True)

		grid = wal.GridPanel(self, 2, 3, 3, 5)

		grid.pack(wal.Label(grid, 'L:'))
		self.color_slider = ColoredSlider(grid, size=40,
									onchange=self.on_slider_change)
		grid.pack(self.color_slider)
		self.color_spin = wal.IntSpin(grid,
								range_val=(0, 255), width=4,
								onchange=self.on_change,
								onenter=self.on_change)
		grid.pack(self.color_spin)

		grid.pack(wal.Label(grid, 'A:'))
		self.alpha_slider = ColoredAlphaSlider(grid, size=40,
										onchange=self.on_slider_change)
		grid.pack(self.alpha_slider)
		self.alpha_spin = wal.IntSpin(grid,
									range_val=(0, 255), width=4,
									onchange=self.on_change,
									onenter=self.on_change)
		grid.pack(self.alpha_spin)

		self.pack(grid)

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

	def on_slider_change(self):
		self.new_color[1] = [self.color_slider.get_value(), ]
		self.new_color[2] = self.alpha_slider.get_value()
		self.update()


	def on_change(self):
		self.new_color[1] = [self.color_spin.get_value() / 255.0, ]
		self.new_color[2] = self.alpha_spin.get_value() / 255.0
		self.update()

	def on_palette_click(self, color):
		self.new_color = color
		self.update()

	def update(self):
		self.color_spin.set_value(self.new_color[1][0] * 255.0)
		# L slider
		start_clr = deepcopy(self.new_color)
		stop_clr = deepcopy(self.new_color)
		start_clr[1][0] = 0.0
		stop_clr[1][0] = 1.0
		start_clr = self.cms.get_rgb_color255(start_clr)
		stop_clr = self.cms.get_rgb_color255(stop_clr)
		self.color_slider.set_value(self.new_color[1][0], start_clr, stop_clr)
		# Alpha slider
		start_clr = deepcopy(self.new_color)
		start_clr[2] = 0.0
		stop_clr = deepcopy(self.new_color)
		stop_clr[2] = 1.0
		start_clr = self.cms.get_rgba_color255(start_clr)
		stop_clr = self.cms.get_rgba_color255(stop_clr)
		self.alpha_slider.set_value(self.new_color[2], start_clr, stop_clr)
		self.alpha_spin.set_value(self.new_color[2] * 255.0)
		self.refpanel.update(self.orig_fill, self.new_color)

	def activate(self, cms, orig_fill, new_color):
		if not new_color and orig_fill:
			new_color = cms.get_grayscale_color(orig_fill[2])
		elif not new_color and not orig_fill:
			new_color = [uc2const.COLOR_GRAY, [0.0, ], 1.0, '']
		else:
			new_color = cms.get_grayscale_color(new_color)
		SolidFillPanel.activate(self, cms, orig_fill, new_color)
		self.update()

class Empty_Panel(SolidFillPanel):

	def build(self):
		self.pack(wal.HPanel(self), fill=True, expand=True)
		self.pack(ColorSwatch(self, self.cms, [], (250, 150)))
		txt = _('Empty pattern selected, i.e. object will not be filled.')
		self.pack(wal.Label(self, txt), padding=10)
		self.pack(wal.HPanel(self), fill=True, expand=True)

	def activate(self, cms, orig_fill, new_color):
		new_color = []
		SolidFillPanel.activate(self, cms, orig_fill, new_color)
