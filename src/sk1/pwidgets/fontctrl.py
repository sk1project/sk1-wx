# -*- coding: utf-8 -*-
#
#  Copyright (C) 2016-2021 by Ihor E. Novikov
#  Copyright (C) 2021 by Maxim S. Barabash
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

import cairo
import logging

import wal
from sk1 import config, events
from sk1.resources import icons, get_icon
from uc2 import libpango

LOG = logging.getLogger(__name__)
DEFAULT_FONT_FAMILY = 'Sans'


def get_max_size_by_fontname(fonts):
    """
    Calculate the approximate size of the surface needed to display font names.
    :param fonts: (list) list of font names
    :return: (int, int) width, height
    """
    family = ""
    max_len_fontname = 0
    for fontname in fonts:
        length = len(fontname)
        if max_len_fontname < length:
            max_len_fontname = length
            family = fontname
    return wal.get_text_size(family, wal.UI_COLORS['text'])


def font_cache_update():
    pass
    # TODO: reimplement it
    # fonts = libpango.get_fonts()[0]
    # generate_fontname_cache(fonts)
    # generate_fontsample_cache(fonts)


class LazyFontSamples(list):

    def __init__(self, fonts):
        """
        Storage for lazy generation of font samples.
        :param fonts: (list) list of font names
        """
        super(LazyFontSamples, self).__init__()
        self._fonts = [] + fonts
        self._cache = {}
        self._text = ''

    def invalidate(self):
        self._cache.clear()
        self._text = ''

    def _generate_fontsample(self, text, family, fontsize, color, w, h):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        ctx = cairo.Context(surface)
        ctx.set_source_rgb(*color)
        ctx.set_matrix(cairo.Matrix(1.0, 0.0, 0.0, 1.0, 0.0, 0.0))
        ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)
        libpango.render_sample(ctx, text, family, fontsize)
        ctx.fill()
        bmp = wal.copy_surface_to_bitmap(surface)
        return bmp

    def __getitem__(self, item):
        if item not in self._cache:
            text = self._text or config.font_preview_text.decode('utf-8')
            family = self._fonts[item]
            # repaint in the desired color at the place of display
            color = (0, 0, 0)
            font_size = config.font_preview_size
            w = config.font_preview_width
            h = libpango.get_sample_size(text, family, font_size)[1]
            if not h:
                h = 10
                LOG.warn('Incorrect font <%s>: zero font height', family)
            bmp = self._generate_fontsample(
                text, family, font_size, color, w, h
            )
            self._cache[item] = bmp
        return self._cache[item]

    def __len__(self):
        return len(self._fonts)


class LazyFontNames(list):

    def __init__(self, fonts):
        """
        Storage for lazy generation of font names.
        :param fonts: (list) list of font names
        """
        super(LazyFontNames, self).__init__()
        self.__items = []
        self._fonts = [] + fonts
        self._cache = {}
        self._text = ""

    def invalidate(self):
        self._cache.clear()

    def __getitem__(self, item):
        if item not in self._cache:
            family = self._fonts[item]
            color = wal.UI_COLORS['text']
            self._cache[item] = wal.text_to_bitmap(family, color)[0]
        return self._cache[item]

    def __len__(self):
        return len(self._fonts)


class FontChoice(wal.FontBitmapChoice):

    def __init__(self, parent, selected_font=None, onchange=None):
        self.fonts = libpango.get_fonts()[0]
        self.bitmaps = LazyFontNames(self.fonts)
        self.sample_bitmaps = LazyFontSamples(self.fonts)
        size = get_max_size_by_fontname(self.fonts)
        if selected_font in None or selected_font not in self.fonts:
            selected_font = DEFAULT_FONT_FAMILY
        value = self.fonts.index(selected_font)
        icon = get_icon(icons.PD_FONT, size=wal.DEF_SIZE)
        wal.FontBitmapChoice.__init__(self, parent, value, size,
                                      config.font_preview_width,
                                      self.fonts, self.bitmaps,
                                      self.sample_bitmaps, icon, onchange)
        events.connect(events.CONFIG_MODIFIED, self.check_config)

    def check_config(self, *args):
        if args[0] == 'font_preview_width':
            self.preview_width = config.font_preview_width
            self._set_bitmaps(self.bitmaps, self.sample_bitmaps)

        if args[0].startswith('font_preview'):
            self.bitmaps.invalidate()
            self.sample_bitmaps.invalidate()
            index = self._get_active()
            self._set_active(index)

    def get_font_family(self):
        index = self._get_active()
        return self.fonts[index]

    def set_font_family(self, family):
        if family not in self.fonts:
            family = DEFAULT_FONT_FAMILY
        index = self.fonts.index(family)
        self._set_active(index)
