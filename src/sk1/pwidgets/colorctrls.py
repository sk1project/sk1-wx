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

import cairo, wal, os
from copy import deepcopy
from base64 import b64decode

from uc2 import uc2const, cms, libimg, libgeom
from uc2.cms import get_registration_black, verbose_color, val_255_to_dec
from uc2.formats.sk2 import sk2_const, sk2_model, sk2_config
from sk1 import _, config, events
from sk1.resources import icons, get_icon

from palette_viewer import PaletteViewer

FILL_MODES = [sk2_const.FILL_ANY, sk2_const.FILL_CLOSED_ONLY]
RULE_MODES = [sk2_const.FILL_EVENODD, sk2_const.FILL_NONZERO]

FILL_MODE_ICONS = {
sk2_const.FILL_ANY: icons.PD_FILL_ANY,
sk2_const.FILL_CLOSED_ONLY: icons.PD_FILL_CLOSED_ONLY,
}
RULE_MODE_ICONS = {
sk2_const.FILL_EVENODD: icons.PD_EVENODD,
sk2_const.FILL_NONZERO: icons.PD_NONZERO,
}

FILL_MODE_NAMES = {
sk2_const.FILL_ANY: _('Fill any contour'),
sk2_const.FILL_CLOSED_ONLY: _('Fill closed only'),
}
RULE_MODE_NAMES = {
sk2_const.FILL_EVENODD: _('Evenodd fill'),
sk2_const.FILL_NONZERO: _('Nonzero fill'),
}

class FillRuleKeeper(wal.HPanel):

	mode = 0
	fill_keeper = None
	rule_keeper = None

	def __init__(self, parent, mode=sk2_const.FILL_EVENODD):
		self.mode = mode
		wal.HPanel.__init__(self, parent)
		self.fill_keeper = wal.HToggleKeeper(self, FILL_MODES,
										FILL_MODE_ICONS, FILL_MODE_NAMES)
		self.pack(self.fill_keeper)
		self.rule_keeper = wal.HToggleKeeper(self, RULE_MODES,
										RULE_MODE_ICONS, RULE_MODE_NAMES)
		self.pack(self.rule_keeper)
		self.set_mode(self.mode)

	def set_mode(self, mode):
		self.fill_keeper.set_mode(mode & sk2_const.FILL_CLOSED_ONLY)
		self.rule_keeper.set_mode(mode & sk2_const.FILL_EVENODD)

	def get_mode(self):
		return self.rule_keeper.mode | self.fill_keeper.mode

	def set_enable(self, val):
		self.fill_keeper.set_enable(val)
		self.rule_keeper.set_enable(val)


CMYK_PALETTE = [
[uc2const.COLOR_CMYK, [1.0, 1.0, 1.0, 1.0], 1.0, 'CMYK Registration'],
[uc2const.COLOR_CMYK, [0.0, 0.0, 0.0, 1.0], 1.0, 'Black'],
[uc2const.COLOR_CMYK, [0.0, 0.0, 0.0, 0.7], 1.0, '70% Black'],
[uc2const.COLOR_CMYK, [0.0, 0.0, 0.0, 0.5], 1.0, '50% Black'],
[uc2const.COLOR_CMYK, [0.0, 0.0, 0.0, 0.2], 1.0, '20% Black'],
[uc2const.COLOR_CMYK, [0.0, 0.0, 0.0, 0.0], 1.0, 'White'],
[uc2const.COLOR_CMYK, [1.0, 0.0, 0.0, 0.0], 1.0, 'Cyan'],
[uc2const.COLOR_CMYK, [0.0, 1.0, 0.0, 0.0], 1.0, 'Magenta'],
[uc2const.COLOR_CMYK, [0.0, 0.0, 1.0, 0.0], 1.0, 'Yellow'],
[uc2const.COLOR_CMYK, [0.0, 1.0, 1.0, 0.0], 1.0, 'Red'],
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

SPOT_PALETTE = [
cms.get_registration_black(),
[uc2const.COLOR_SPOT, [[0.7608, 0.6039, 0.2196], []], 1.0, 'Rich Gold'],
[uc2const.COLOR_SPOT, [[0.6745, 0.6, 0.3804], []], 1.0, 'Metallic Gold'],
[uc2const.COLOR_SPOT, [[0.8471, 0.6118, 0.4667], []], 1.0, 'Bronze'],
[uc2const.COLOR_SPOT, [[0.7098, 0.7098, 0.7098], []], 1.0, 'Silver'],
[uc2const.COLOR_SPOT, [[1.0, 1.0, 1.0 ], [0.0, 0.0, 0.0, 0.0]], 1.0, 'Opaque White'],
[uc2const.COLOR_SPOT, [[1.0, 0.0, 0.0], []], 1.0, 'Fluorescent Red'],
[uc2const.COLOR_SPOT, [[1.0, 0.5922, 0.0118], []], 1.0, 'Fluorescent Orange'],
[uc2const.COLOR_SPOT, [[0.9216, 1.0, 0.0], []], 1.0, 'Fluorescent Yellow'],
[uc2const.COLOR_SPOT, [[0.0, 1.0, 0.0157], []], 1.0, 'Fluorescent Green'],
[uc2const.COLOR_SPOT, [[0.0549, 0.5647, 1.0], []], 1.0, 'Fluorescent Blue'],
[uc2const.COLOR_SPOT, [[1.0, 0.0039, 0.498], []], 1.0, 'Fluorescent Magenta'],
]

REG_COLOR = [1.0, 1.0, 1.0, 1.0]
REG_SPOT_COLOR = [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0, 1.0]]


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
	pattern_size = 10

	def __init__(self, border='', even_odd=False):
		self.border = border
		self.even_odd = even_odd
		wal.SensitiveCanvas.__init__(self)

	def get_cairo_color(self, color):
		r, g, b = self.cms.get_display_color(color)
		return r, g, b, color[2]

	def paint(self):
		self.draw_background()
		if not self.color is None:
			self.draw_color()
		elif self.fill:
			if self.fill[1] == sk2_const.FILL_GRADIENT:
				self.draw_gradient()
			elif self.fill[1] == sk2_const.FILL_PATTERN:
				self.draw_pattern()
		self.draw_border()

	def draw_background(self):
		if self.color and self.color[2] == 1.0: return
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
				self.draw_rect(x1, y1, self.pattern_size, self.pattern_size)
				flag_x = not flag_x
				x1 += self.pattern_size
			flag_y = not flag_y
			y1 += self.pattern_size
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
		if self.color[1] in [REG_COLOR, REG_SPOT_COLOR]:
			if not self.reg_icon:
				self.reg_icon = get_icon(icons.REG_SIGN, size=wal.DEF_SIZE)
			x = (w - 19) / 2
			y = (h - 19) / 2
			self.draw_bitmap(self.reg_icon, x, y)

	def draw_cairo_background(self, ctx):
		w, h = self.get_size()
		x1 = y1 = 0
		flag_y = self.even_odd
		while y1 < h:
			flag_x = flag_y
			while x1 < w:
				clr = wal.WHITE
				if not flag_x: clr = wal.LIGHT_GRAY
				ctx.set_source_rgb(*val_255_to_dec(clr.Get()))
				ctx.rectangle(x1, y1, self.pattern_size, self.pattern_size)
				ctx.fill()
				flag_x = not flag_x
				x1 += self.pattern_size
			flag_y = not flag_y
			y1 += self.pattern_size
			x1 = 0

	def draw_gradient(self):
		w, h = self.get_size()
		gradient = self.fill[2]
		surface = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
		ctx = cairo.Context(surface)
		self.draw_cairo_background(ctx)
		if gradient[0] == sk2_const.GRADIENT_LINEAR:
			grd = cairo.LinearGradient(0.0, h / 2.0, w, h / 2.0)
		else:
			grd = cairo.RadialGradient(w / 2.0, h / 2.0, 0,
									w / 2.0, h / 2.0, w / 2.0)
		for stop in gradient[2]:
			grd.add_color_stop_rgba(stop[0], *self.get_cairo_color(stop[1]))
		ctx.set_source(grd)
		ctx.rectangle(0, 0, w, h)
		ctx.fill()
		self.gc_draw_bitmap(wal.copy_surface_to_bitmap(surface), 0, 0)

	def draw_pattern(self):
		w, h = self.get_size()
		pattern = self.fill[2]
		surface = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
		ctx = cairo.Context(surface)
		self.draw_cairo_background(ctx)
		bmpstr = b64decode(pattern[1])
		config = sk2_config.SK2_Config()
		config_file = os.path.join(self.cms.app.appdata.app_config_dir,
								'sk2_config.xml')
		config.load(config_file)
		image_obj = sk2_model.Pixmap(config)
		libimg.set_image_data(self.cms, image_obj, bmpstr)
		if pattern[0] == sk2_const.PATTERN_IMG and len(pattern) > 2:
			image_obj.style[3] = deepcopy(pattern[2])
		libimg.update_image(self.cms, image_obj)
		sp = cairo.SurfacePattern(image_obj.cache_cdata)
		sp.set_extend(cairo.EXTEND_REPEAT)
		if pattern[0] == sk2_const.PATTERN_IMG and len(pattern) > 3:
			sp.set_matrix(cairo.Matrix(*pattern[3]))
		ctx.set_source(sp)
		ctx.rectangle(0, 0, w, h)
		ctx.fill()
		image_obj.cache_cdata = None
		self.gc_draw_bitmap(wal.copy_surface_to_bitmap(surface), 0, 0)

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


class PaletteSwatch(wal.VPanel, SwatchCanvas):

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
				even_odd=False, onclick=None):
		self.color = color
		self.cms = cms
		wal.VPanel.__init__(self, parent)
		SwatchCanvas.__init__(self, border, even_odd)
		self.pack(size)
		if onclick: self.callback = onclick

	def mouse_left_up(self, point):
		if self.callback: self.callback()

	def set_color(self, color):
		self.color = color
		tooltip = ''
		if self.color and self.color[3]:tooltip = self.color[3]
		self.set_tooltip(tooltip)
		self.refresh()


class FillSwatch(wal.VPanel, SwatchCanvas):

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
		if not fill:
			self.color = []
			self.fill = None
		elif fill[1] == sk2_const.FILL_SOLID:
			self.color = fill[2]
			self.fill = None
		elif fill[1] in [sk2_const.FILL_GRADIENT, sk2_const.FILL_PATTERN]:
			self.color = None
			self.fill = fill
		tooltip = ''
		if self.color and self.color[3]:tooltip = self.color[3]
		self.set_tooltip(tooltip)
		self.refresh()


class SB_StrokeSwatch(AlphaColorSwatch):

	pattern_size = 8

	def __init__(self, parent, app, label, color=[], size=(35, 16),
				onclick=None):
		self.app = app
		self.label = label
		cms = self.app.default_cms
		AlphaColorSwatch.__init__(self, parent, cms, color, size,
								 'news', onclick=onclick)

	def update_from_obj(self, obj):
		text = _('Stroke:')
		self.cms = self.app.current_doc.cms
		if self.app.insp.is_obj_pixmap(obj):
			self.set_color(obj.style[3][1])
			text = _('Bg:')
		else:
			stroke = obj.style[1]
			if stroke:
				point_val = stroke[1]
				self.set_color(stroke[2])
				unit = self.app.current_doc.model.doc_units
				val = str(round(point_val * uc2const.point_dict[unit], 3))
				text += ' %s ' % val
				text += uc2const.unit_short_names[unit]
			else:
				self.set_color([])
				text += ' ' + _('None')
		self.label.set_text(text)


class SB_FillSwatch(FillSwatch):

	pattern_size = 8

	def __init__(self, parent, app, label, fill=[], size=(35, 16),
				onclick=None):
		self.app = app
		self.label = label
		cms = self.app.default_cms
		FillSwatch.__init__(self, parent, cms, fill, size,
						'news', onclick=onclick)

	def update_from_obj(self, obj):
		text = _('Fill:')
		self.cms = self.app.current_doc.cms
		if self.app.insp.is_obj_pixmap(obj):
			text = _('Fg:')
			self.set_swatch_fill([sk2_const.FILL_EVENODD, sk2_const.FILL_SOLID,
								obj.style[3][0]])
		else:
			fill = obj.style[0]
			self.set_swatch_fill(fill)
			if fill:
				if fill[1] == sk2_const.FILL_SOLID:
					text += ' ' + cms.verbose_color(fill[2])
			else:
				text += ' ' + _('None')

		self.label.set_text(text)


class MiniPalette(wal.VPanel):

	callback = None

	def __init__(self, parent, cms, palette=CMYK_PALETTE, onclick=None):
		wal.VPanel.__init__(self, parent)
		self.set_bg(wal.BLACK)
		grid = wal.GridPanel(parent, 2, 6, 1, 1)
		grid.set_bg(wal.BLACK)
		for item in palette:
			grid.pack(PaletteSwatch(grid, cms, item, (40, 20), self.on_click))
		self.pack(grid, padding_all=1)
		if onclick: self.callback = onclick

	def on_click(self, color):
		if self.callback: self.callback(color)


class ColorColorRefPanel(wal.VPanel):

	def __init__(self, parent, cms, orig_color, new_color, on_orig=None):
		wal.VPanel.__init__(self, parent)
		grid = wal.GridPanel(self, hgap=5)
		grid.pack(wal.Label(grid, _('Old color:')))

		self.before_swatch = AlphaColorSwatch(grid, cms, orig_color, (70, 30),
										'new', onclick=on_orig)
		grid.pack(self.before_swatch)

		grid.pack(wal.Label(grid, _('New color:')))

		self.after_swatch = AlphaColorSwatch(grid, cms, new_color, (70, 30),
											even_odd=True)
		grid.pack(self.after_swatch)

		self.pack(grid, padding_all=2)

	def update(self, orig_color, new_color):
		self.before_swatch.set_color(orig_color)
		self.after_swatch.set_color(new_color)


class FillColorRefPanel(wal.VPanel):

	def __init__(self, parent, cms, fill, new_color, on_orig=None):
		wal.VPanel.__init__(self, parent)
		grid = wal.GridPanel(self, hgap=5)
		grid.pack(wal.Label(grid, _('Old fill:')))

		self.before_swatch = FillSwatch(grid, cms, fill, (70, 30),
										onclick=on_orig)
		grid.pack(self.before_swatch)

		grid.pack(wal.Label(grid, _('New fill:')))

		self.after_swatch = AlphaColorSwatch(grid, cms, new_color, (70, 30))
		grid.pack(self.after_swatch)

		self.pack(grid, padding_all=2)

	def update(self, fill, new_color):
		self.before_swatch.set_swatch_fill(fill)
		self.after_swatch.set_color(new_color)

class FillFillRefPanel(wal.VPanel):

	def __init__(self, parent, cms, fill, new_fill, on_orig=None):
		wal.VPanel.__init__(self, parent)
		grid = wal.GridPanel(self, hgap=5)
		grid.pack(wal.Label(grid, _('Old fill:')))

		self.before_swatch = FillSwatch(grid, cms, fill, (70, 30),
										onclick=on_orig)
		grid.pack(self.before_swatch)

		grid.pack(wal.Label(grid, _('New fill:')))

		self.after_swatch = FillSwatch(grid, cms, new_fill, (70, 30),
									border='swe', even_odd=False)
		grid.pack(self.after_swatch)

		self.pack(grid, padding_all=2)

	def update(self, fill, new_fill):
		self.before_swatch.set_swatch_fill(fill)
		self.after_swatch.set_swatch_fill(new_fill)


class StyleMonitor(wal.VPanel):

	def __init__(self, parent, app):
		self.app = app
		wal.VPanel.__init__(self, parent)
		self.pack((25, 25))
		self.stroke = AlphaColorSwatch(self, app.default_cms, [],
									border='news', onclick=self.stroke_click)
		self.stroke.set_position((5, 5))
		self.fill = FillSwatch(self, app.default_cms, [],
							border='news', onclick=self.fill_click)
		self.fill.set_position((0, 0))
		events.connect(events.DOC_CHANGED, self.doc_changed)
		events.connect(events.DOC_MODIFIED, self.doc_changed)
		events.connect(events.NO_DOCS, self.no_docs)

	def doc_changed(self, doc):
		cms = doc.cms
		fill_style = doc.model.styles['Default Style'][0]
		stroke_style = doc.model.styles['Default Style'][1]
		self.stroke.cms = cms
		self.fill.cms = cms
		self.fill.set_swatch_fill(deepcopy(fill_style))
		if stroke_style:
			self.stroke.set_color(deepcopy(stroke_style[2]))
		else:
			self.stroke.set_color([])

	def no_docs(self):
		self.stroke.cms = self.app.default_cms
		self.fill.cms = self.app.default_cms
		self.stroke.set_color([])
		self.fill.set_swatch_fill([])

	def fill_click(self):
		self.app.proxy.fill_dialog(True)

	def stroke_click(self):
		self.app.proxy.stroke_dialog(True)


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


class CMYK_Mixer(wal.GridPanel):

	color = None
	callback = None

	def __init__(self, parent, cms, color=None, onchange=None):
		wal.GridPanel.__init__(self, parent, 4, 4, 3, 5)
		self.cms = cms
		if color:
			self.color = color
		else:
			self.color = [uc2const.COLOR_CMYK, [0.0, 0.0, 0.0, 1.0], 1.0, '']
		if onchange: self.callback = onchange

		self.color_sliders = []
		self.color_spins = []

		labels = ['C:', 'M:', 'Y:', 'K:']
		for item in labels:
			self.pack(wal.Label(self, item))
			self.color_sliders.append(ColoredSlider(self,
										onchange=self.on_slider_change))
			self.pack(self.color_sliders[-1])
			self.color_spins.append(wal.FloatSpin(self,
									range_val=(0.0, 100.0), width=5,
									onchange=self.on_change,
									onenter=self.on_change))
			self.pack(self.color_spins[-1])
			self.pack(wal.Label(self, '%'))

		self.pack(wal.Label(self, 'A:'))
		self.alpha_slider = ColoredAlphaSlider(self,
										onchange=self.on_slider_change)
		self.pack(self.alpha_slider)
		self.alpha_spin = wal.FloatSpin(self,
									range_val=(0.0, 100.0), width=5,
									onchange=self.on_change,
									onenter=self.on_change)
		self.pack(self.alpha_spin)
		self.pack(wal.Label(self, '%'))

	def on_change(self):
		color_vals = []
		for item in self.color_spins:
			color_vals.append(item.get_value() / 100.0)
		self.color[1] = color_vals
		self.color[2] = self.alpha_spin.get_value() / 100.0
		if self.callback: self.callback()
		else: self.update()

	def on_slider_change(self):
		color_vals = []
		for item in self.color_sliders:
			color_vals.append(item.get_value())
		self.color[1] = color_vals
		self.color[2] = self.alpha_slider.get_value()
		if self.callback: self.callback()
		else: self.update()

	def get_color(self):
		return self.color

	def set_color(self, color):
		if color:
			self.color = color
			self.update()

	def update(self):
		for item in self.color_spins:
			index = self.color_spins.index(item)
			item.set_value(self.color[1][index] * 100.0)
		for item in self.color_sliders:
			index = self.color_sliders.index(item)
			start_clr = deepcopy(self.color)
			stop_clr = deepcopy(self.color)
			start_clr[1][index] = 0.0
			stop_clr[1][index] = 1.0
			start_clr = self.cms.get_rgb_color255(start_clr)
			stop_clr = self.cms.get_rgb_color255(stop_clr)
			item.set_value(self.color[1][index], start_clr, stop_clr)

		start_clr = deepcopy(self.color)
		start_clr[2] = 0.0
		stop_clr = deepcopy(self.color)
		stop_clr[2] = 1.0
		start_clr = self.cms.get_rgba_color255(start_clr)
		stop_clr = self.cms.get_rgba_color255(stop_clr)
		self.alpha_slider.set_value(self.color[2], start_clr, stop_clr)
		self.alpha_spin.set_value(self.color[2] * 100.0)


class RGB_Mixer(wal.VPanel):

	color = None
	callback = None

	def __init__(self, parent, cms, color=None, onchange=None):
		wal.VPanel.__init__(self, parent)
		self.cms = cms
		if color:
			self.color = color
		else:
			self.color = [uc2const.COLOR_RGB, [0.0, 0.0, 0.0], 1.0, '']
		if onchange: self.callback = onchange

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

	def on_hex_change(self):
		hexcolor = self.html.get_color()
		if len(hexcolor) == 7:
			self.color[1] = cms.hexcolor_to_rgb(hexcolor)
			self.color[2] = 1.0
		elif len(hexcolor) == 9:
			r, g, b, a = cms.hexcolor_to_rgba(hexcolor)
			self.color[1] = [r, g, b]
			self.color[2] = a
		if self.callback: self.callback()
		else: self.update()

	def on_slider_change(self):
		color_vals = []
		for item in self.color_sliders:
			color_vals.append(item.get_value())
		self.color[1] = color_vals
		self.color[2] = self.alpha_slider.get_value()
		if self.callback: self.callback()
		else: self.update()

	def on_change(self):
		color_vals = []
		for item in self.color_spins:
			color_vals.append(item.get_value() / 255.0)
		self.color[1] = color_vals
		self.color[2] = self.alpha_spin.get_value() / 255.0
		if self.callback: self.callback()
		else: self.update()

	def get_color(self):
		return self.color

	def set_color(self, color):
		if color:
			self.color = color
			self.update()

	def update(self):
		for item in self.color_spins:
			index = self.color_spins.index(item)
			item.set_value(self.color[1][index] * 255.0)
		for item in self.color_sliders:
			index = self.color_sliders.index(item)
			start_clr = deepcopy(self.color)
			stop_clr = deepcopy(self.color)
			start_clr[1][index] = 0.0
			stop_clr[1][index] = 1.0
			start_clr = self.cms.get_rgb_color255(start_clr)
			stop_clr = self.cms.get_rgb_color255(stop_clr)
			item.set_value(self.color[1][index], start_clr, stop_clr)

		start_clr = deepcopy(self.color)
		start_clr[2] = 0.0
		stop_clr = deepcopy(self.color)
		stop_clr[2] = 1.0
		start_clr = self.cms.get_rgba_color255(start_clr)
		stop_clr = self.cms.get_rgba_color255(stop_clr)
		self.alpha_slider.set_value(self.color[2], start_clr, stop_clr)
		self.alpha_spin.set_value(self.color[2] * 255.0)
		self.html.set_color(self.color)


class Gray_Mixer(wal.VPanel):

	color = None
	callback = None

	def __init__(self, parent, cms, color=None, onchange=None):
		wal.VPanel.__init__(self, parent)
		self.cms = cms
		if color:
			self.color = color
		else:
			self.color = [uc2const.COLOR_GRAY, [0.0, ], 1.0, '']
		if onchange: self.callback = onchange

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

	def on_slider_change(self):
		self.color[1] = [self.color_slider.get_value(), ]
		self.color[2] = self.alpha_slider.get_value()
		if self.callback: self.callback()
		else: self.update()

	def on_change(self):
		self.color[1] = [self.color_spin.get_value() / 255.0, ]
		self.color[2] = self.alpha_spin.get_value() / 255.0
		if self.callback: self.callback()
		else: self.update()

	def get_color(self):
		return self.color

	def set_color(self, color):
		if color:
			self.color = color
			self.update()

	def update(self):
		self.color_spin.set_value(self.color[1][0] * 255.0)
		# L slider
		start_clr = deepcopy(self.color)
		stop_clr = deepcopy(self.color)
		start_clr[1][0] = 0.0
		stop_clr[1][0] = 1.0
		start_clr = self.cms.get_rgb_color255(start_clr)
		stop_clr = self.cms.get_rgb_color255(stop_clr)
		self.color_slider.set_value(self.color[1][0], start_clr, stop_clr)
		# Alpha slider
		start_clr = deepcopy(self.color)
		start_clr[2] = 0.0
		stop_clr = deepcopy(self.color)
		stop_clr[2] = 1.0
		start_clr = self.cms.get_rgba_color255(start_clr)
		stop_clr = self.cms.get_rgba_color255(stop_clr)
		self.alpha_slider.set_value(self.color[2], start_clr, stop_clr)
		self.alpha_spin.set_value(self.color[2] * 255.0)


class SPOT_Mixer(wal.VPanel):

	color = None
	callback = None

	def __init__(self, parent, cms, color=None, onchange=None):
		wal.VPanel.__init__(self, parent)
		self.cms = cms
		if color:
			self.color = color
		else:
			self.color = get_registration_black()
		if onchange: self.callback = onchange

		name_panel = wal.HPanel(self)
		name_panel.pack(wal.Label(name_panel, 'Name:'), padding=5)
		self.name_field = wal.Entry(name_panel, width=30,
								onchange=self.on_change)
		name_panel.pack(self.name_field)
		self.pack(name_panel, padding_all=5)

		grid = wal.GridPanel(self, 3, 4, 3, 5)

		grid.pack((1, 1))
		self.rgb_txt = wal.Label(grid, '---')
		grid.pack(self.rgb_txt)
		grid.pack((1, 1))
		grid.pack((1, 1))

		grid.pack((1, 1))
		self.cmyk_txt = wal.Label(grid, '---')
		grid.pack(self.cmyk_txt)
		grid.pack((1, 1))
		grid.pack((1, 1))

		grid.pack(wal.Label(grid, 'A:'))
		self.alpha_slider = ColoredAlphaSlider(grid,
										onchange=self.on_slider_change)
		grid.pack(self.alpha_slider)
		self.alpha_spin = wal.FloatSpin(grid,
									range_val=(0.0, 100.0), width=5,
									onchange=self.on_change,
									onenter=self.on_change)
		grid.pack(self.alpha_spin)
		grid.pack(wal.Label(self, '%'))

		self.pack(grid)


	def on_slider_change(self):
		self.color[2] = self.alpha_slider.get_value()
		if self.callback: self.callback()
		else: self.update()

	def on_change(self):
		self.color[3] = self.name_field.get_value()
		self.color[2] = self.alpha_spin.get_value() / 100.0
		if self.callback: self.callback()
		else: self.update()

	def get_color(self):
		return self.color

	def set_color(self, color):
		if color:
			self.color = color
			self.update()

	def update(self):
		self.name_field.set_value(self.color[3])
		txt = 'RGB: '
		if self.color[1][0]:
			txt += verbose_color(self.cms.get_rgb_color(self.color))
		else:
			txt += '---'
		self.rgb_txt.set_text(txt)

		txt = 'CMYK: '
		if self.color[1][1]:
			txt += verbose_color(self.cms.get_cmyk_color(self.color))
		else:
			txt += '---'
		self.cmyk_txt.set_text(txt)

		# Alpha slider
		start_clr = deepcopy(self.color)
		start_clr[2] = 0.0
		stop_clr = deepcopy(self.color)
		stop_clr[2] = 1.0
		start_clr = self.cms.get_rgba_color255(start_clr)
		stop_clr = self.cms.get_rgba_color255(stop_clr)
		self.alpha_slider.set_value(self.color[2], start_clr, stop_clr)
		self.alpha_spin.set_value(self.color[2] * 255.0)


class ColorSticker(wal.VPanel):

	def __init__(self, parent, cms, color=None):
		self.cms = cms
		if not color:
			color = get_registration_black()
		wal.VPanel.__init__(self, parent, True)

		nf = wal.VPanel(self)
		nf.set_bg(wal.BLACK)
		self.name_field = wal.Label(nf, '???', fontbold=True, fg=wal.WHITE)
		nf.pack(self.name_field, padding_all=3)

		vf = wal.VPanel(self)
		vf.set_bg(wal.WHITE)
		self.color_type = wal.Label(vf, '???', fontbold=True, fontsize=-1)
		self.line1 = wal.Label(vf, '???', fontsize=-1)
		self.line2 = wal.Label(vf, '???', fontsize=-1)
		vf.pack(self.color_type, padding_all=3)
		vf.pack(self.line1, padding_all=1)
		vf.pack(self.line2, padding_all=1)

		self.color_swatch = AlphaColorSwatch(self, self.cms, color, (180, 100),
											border='')
		self.pack(nf, fill=True)
		self.pack(vf, fill=True)
		self.pack(self.color_swatch, fill=True, expand=True)

	def set_color(self, color):
		if not color: return
		txt = '' + color[3]
		if not txt: txt = '???'
		self.name_field.set_text(txt)
		self.color_swatch.set_color(color)
		self.color_type.set_text(color[0] + ' ' + _('color'))
		if not color[0] == uc2const.COLOR_SPOT:
			self.line1.set_text(cms.verbose_color(color))
			self.line2.set_text('')
		else:
			txt1 = ''
			txt2 = ''
			if color[1][0]:
				txt1 = cms.verbose_color(self.cms.get_rgb_color(color))
			if color[1][1]:
				txt2 = cms.verbose_color(self.cms.get_cmyk_color(color))
			self.line1.set_text(txt1)
			self.line2.set_text(txt2)
		self.parent.layout()


class Palette_Mixer(wal.HPanel):

	callback = None

	def __init__(self, parent, app, cms, onchange=None):
		self.cms = cms
		self.app = app
		self.callback = onchange
		wal.HPanel.__init__(self, parent)

		current_palette = self.get_current_palette()
		self.palviewer = PaletteViewer(self, self.cms, current_palette,
									self.on_change)
		self.pack(self.palviewer, fill=True)
		self.pack((5, 5))

		view_panel = wal.VPanel(self)
		view_panel.pack(wal.Label(view_panel, _('Palette:')), align_center=False)

		pal_list = self.get_palette_list()
		self.pal = wal.Combolist(view_panel, items=pal_list,
								onchange=self.change_palette)
		current_palette_name = current_palette.model.name
		self.pal.set_active(pal_list.index(current_palette_name))
		view_panel.pack(self.pal, fill=True)

		self.sticker = ColorSticker(view_panel, self.cms)
		view_panel.pack(self.sticker, padding=5)
		self.pack(view_panel, fill=True, expand=True)
		self.palviewer.set_active_color()

	def change_palette(self):
		palette_name = self.get_palette_name_by_index(self.pal.get_active())
		current_palette = self.get_palette_by_name(palette_name)
		self.palviewer.draw_palette(current_palette)
		self.palviewer.set_active_color()
		self.on_change()

	def on_change(self):
		self.color = self.palviewer.get_color()
		self.sticker.set_color(self.color)
		if self.callback: self.callback(self.color)

	def get_color(self):
		return self.color

	#===Stuff
	def get_current_palette(self):
		current_palette_name = config.palette
		if not current_palette_name:
			return self.app.palettes.palette_in_use
		return self.get_palette_by_name(current_palette_name)

	def get_palette_list(self):
		palettes = self.app.palettes.palettes
		pal_list = palettes.keys()
		pal_list.sort()
		return pal_list

	def get_palette_by_name(self, name):
		palettes = self.app.palettes.palettes
		pal_list = self.get_palette_list()
		if not name in pal_list:
			name = self.app.palettes.get_default_palette_name()
		return palettes[name]

	def get_palette_name_by_index(self, index):
		pal_list = self.get_palette_list()
		return pal_list[index]

	def get_index_by_palette_name(self, name=''):
		pal_list = self.get_palette_list()
		if not name in pal_list:
			name = self.app.palettes.get_default_palette_name()
		return pal_list.index(name)
