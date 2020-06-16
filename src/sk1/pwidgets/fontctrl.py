# -*- coding: utf-8 -*-
#
#  Copyright (C) 2016 by Ihor E. Novikov
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import cairo

import wal
from sk1 import _, config, events
from sk1.resources import icons, get_icon
from uc2 import libpango, cms

FONTNAME_CACHE = []
FONTSAMPLE_CACHE = []
MAXSIZE = []

LOG = logging.getLogger(__name__)


def generate_fontname_cache(fonts):
    maxwidth = 0
    height = 0
    for item in fonts:
        try:
            bmp, size = wal.text_to_bitmap(item, wal.UI_COLORS['text'])
        except Exception as e:
            LOG.error('Cannot process font <%s> %s', item, e)
            continue
        FONTNAME_CACHE.append(bmp)
        maxwidth = max(size[0], maxwidth)
        height = size[1]
    MAXSIZE.append(maxwidth)
    MAXSIZE.append(height)


def generate_fontsample_cache(fonts):
    w = config.font_preview_width
    fontsize = config.font_preview_size
    color = cms.val_255(config.font_preview_color)
    text = config.font_preview_text.decode('utf-8')
    for item in fonts:
        h = libpango.get_sample_size(text, item, fontsize)[1]
        if not h:
            h = 10
            LOG.warn('Incorrect font <%s>: zero font height', item)
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
        FONTSAMPLE_CACHE.append(wal.invert_text_bitmap(bmp, color))


def font_cache_update():
    fonts = libpango.get_fonts()[0]
    generate_fontname_cache(fonts)
    generate_fontsample_cache(fonts)


class FontChoice(wal.FontBitmapChoice):
    fonts = []

    def __init__(self, parent, selected_font='Sans', onchange=None):
        self.fonts = libpango.get_fonts()[0]
        if not FONTNAME_CACHE:
            generate_fontname_cache(self.fonts)
            generate_fontsample_cache(self.fonts)
        if selected_font not in self.fonts:
            selected_font = 'Sans'
        value = self.fonts.index(selected_font)
        icon = get_icon(icons.PD_FONT, size=wal.DEF_SIZE)
        wal.FontBitmapChoice.__init__(self, parent, value, MAXSIZE,
                                      self.fonts, FONTNAME_CACHE,
                                      FONTSAMPLE_CACHE, icon, onchange)
        events.connect(events.CONFIG_MODIFIED, self.check_config)

    def check_config(self, *args):
        if args[0].startswith('font_preview'):
            FONTSAMPLE_CACHE[:] = []
            generate_fontsample_cache(self.fonts)
            index = self._get_active()
            self._set_bitmaps(self.bitmaps, FONTSAMPLE_CACHE)
            self._set_active(index)

    def get_font_family(self):
        index = self._get_active()
        return self.fonts[index]

    def set_font_family(self, family):
        if family not in self.fonts:
            family = 'Sans'
        index = self.fonts.index(family)
        self._set_active(index)
