# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2016 by Igor E. Novikov
#
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
#
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
#
# 	You should have received a copy of the GNU General Public License
# 	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import wal
import cairo

from uc2 import libpango, cms

from sk1 import config, events
from sk1.resources import icons, get_icon

def generate_fontnames(fonts):
	bitmaps = []
	maxwidth = 0
	height = 0
	for item in fonts:
		bmp, size = wal.text_to_bitmap(item)
		bitmaps.append(bmp)
		maxwidth = max(size[0], maxwidth)
		height = size[1]
	return bitmaps, (maxwidth, height)

def generate_fontsamples(fonts):
	bitmaps = []
	w = config.font_preview_width
	fontsize = config.font_preview_size
	color = cms.val_255(config.font_preview_color)
	text = config.font_preview_text
	for item in fonts:
		h = libpango.get_sample_size(text, item, fontsize)[1]
		surface = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
		ctx = cairo.Context(surface)
		ctx.set_source_rgb(0.0, 0.0, 0.0)
		ctx.paint()
		matrix = cairo.Matrix(1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
		ctx.set_matrix(matrix)
		ctx.set_source_rgb(1.0, 1.0, 1.0)
		ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)
		libpango.render_sample(ctx, text, item, fontsize)
		ctx.fill()
		bmp = wal.copy_surface_to_bitmap(surface)
		bitmaps.append(wal.invert_text_bitmap(bmp, color))
	return bitmaps

class FontChoice(wal.FontBitmapChoice):

	fonts = []

	def __init__(self, parent, selected_font='Sans', onchange=None):
		self.fonts = libpango.FAMILIES_LIST
		if not self.fonts: libpango.update_fonts()
		bitmaps, maxsize = generate_fontnames(self.fonts)
		samples = generate_fontsamples(self.fonts)
		if not selected_font in self.fonts:
			selected_font = 'Sans'
		value = self.fonts.index(selected_font)
		icon = get_icon(icons.PD_FONT, size=wal.DEF_SIZE)
		wal.FontBitmapChoice.__init__(self, parent, value, maxsize,
							self.fonts, bitmaps, samples, icon, onchange)
		events.connect(events.CONFIG_MODIFIED, self.check_config)

	def check_config(self, attr, value):
		if len(attr) > 12 and attr[:12] == 'font_preview':
			sample_bitmaps = generate_fontsamples(self.fonts)
			index = self._get_active()
			self._set_bitmaps(self.bitmaps, sample_bitmaps)
			self._set_active(index)

	def get_font_family(self):
		index = self._get_active()
		return '' + self.fonts[index]

	def set_font_family(self, family):
		if not family in self.fonts:
			family = 'Sans'
		index = self.fonts.index(family)
		self._set_active(index)
