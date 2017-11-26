# -*- coding: utf-8 -*-
#
#  Copyright (C) 2016 by Igor E. Novikov
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
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from uc2 import uc2const, libimg
from uc2.formats.sk2.crenderer import CairoRenderer


class PrintRenderer(CairoRenderer):
    colorspace = uc2const.COLOR_RGB

    def __init__(self, cms):
        CairoRenderer.__init__(self, cms)

    def set_colorspace(self, cs=uc2const.COLOR_RGB):
        if not cs == self.colorspace:
            self.colorspace = cs

    def get_color(self, color):
        if self.colorspace == uc2const.COLOR_RGB:
            r, g, b = self.cms.get_display_color(color)
        elif self.colorspace == uc2const.COLOR_CMYK:
            cmyk_color = self.cms.get_cmyk_color(color)
            r, g, b = self.cms.get_display_color(cmyk_color)
        else:
            gc = self.cms.get_grayscale_color(color)
            r, g, b = self.cms.get_display_color(gc)
        return r, g, b, color[2]

    def get_image(self, pixmap):
        if self.colorspace == uc2const.COLOR_RGB:
            if not pixmap.cache_cdata:
                proofing = self.cms.proofing
                self.cms.proofing = False
                libimg.update_image(self.cms, pixmap)
                self.cms.proofing = proofing
            return pixmap.cache_cdata
        elif self.colorspace == uc2const.COLOR_CMYK:
            if not pixmap.cache_ps_cdata:
                libimg.update_image(self.cms, pixmap, True)
                pixmap.cache_ps_cdata = pixmap.cache_cdata
                pixmap.cache_cdata = None
            return pixmap.cache_ps_cdata
        else:
            if not pixmap.cache_gray_cdata:
                libimg.update_gray_image(self.cms, pixmap)
            return pixmap.cache_gray_cdata

    def get_pattern_image(self, obj):
        if self.colorspace == uc2const.COLOR_RGB:
            if not obj.cache_pattern_img:
                image_obj = self._create_pattern_image(obj)
                obj.cache_pattern_img = image_obj.cache_cdata
            return obj.cache_pattern_img
        elif self.colorspace == uc2const.COLOR_CMYK:
            if not obj.cache_ps_pattern_img:
                image_obj = self._create_pattern_image(obj, force_proofing=True)
                obj.cache_ps_pattern_img = image_obj.cache_cdata
            return obj.cache_ps_pattern_img
        else:
            if not obj.cache_gray_pattern_img:
                image_obj = self._create_pattern_image(obj, gray=True)
                obj.cache_gray_pattern_img = image_obj.cache_gray_cdata
            return obj.cache_gray_pattern_img
