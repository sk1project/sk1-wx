# -*- coding: utf-8 -*-
#
#  Copyright (C) 2018 by Maxim S. Barabash
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


from uc2.formats.fig import fig_model
from uc2 import uc2const
from . import fig_const


def create_new_doc(config):
    doc = fig_model.FIGDocument(config)
    return doc


class FIGMethods(object):
    presenter = None
    model = None
    config = None

    def __init__(self, presenter):
        self.presenter = presenter

    def update(self):
        self.model = self.presenter.model
        self.config = self.presenter.config

    # ---DOCUMENT

    def get_doc_units(self):
        return self.model.units

    def set_doc_units(self, units):
        self.model.units = units

    def get_doc_metainfo(self):
        return self.model.comment or ''

    def set_doc_metainfo(self, metainfo):
        if isinstance(metainfo, (list, tuple)):
            metainfo = '\n'.join(metainfo)
        self.model.comment = metainfo

    def fig_to_in(self):
        if self.model.units == fig_const.INCHES:
            coef = fig_const.PIX_PER_INCH / fig_const.DEFAULT_RESOLUTION
        else:
            coef = fig_const.PIX_PER_CM / (fig_const.PIX_PER_INCH / 2.54)
        user_scale = self.model.config.userscale or 1.0
        resolution = self.model.resolution or fig_const.DEFAULT_RESOLUTION
        return 1.0 / (resolution * coef) * user_scale * uc2const.in_to_pt

    def in_to_fig(self):
        if self.model.units == fig_const.INCHES:
            coef = fig_const.PIX_PER_INCH / fig_const.DEFAULT_RESOLUTION
        else:
            coef = fig_const.PIX_PER_CM / (fig_const.PIX_PER_INCH / 2.54)
        resolution = self.model.resolution or fig_const.DEFAULT_RESOLUTION
        return resolution * uc2const.pt_to_in * coef

    def get_doc_trafo(self):
        fig_to_in = self.fig_to_in()
        return [fig_to_in, 0.0, 0.0, -fig_to_in, 0.0, 0.0]

    # --- PAGES

    def get_page_size(self):
        paper_size = uc2const.PAGE_FORMATS.get(self.model.paper_size)
        if not paper_size:
            paper_size = uc2const.PAGE_FORMATS['Letter']
        if self.model.orientation == fig_const.LANDSCAPE:
            size = max(paper_size), min(paper_size)
        else:
            size = min(paper_size), max(paper_size)
        return size

    def get_pages_format(self):
        size = self.get_page_size()
        return [self.model.paper_size, size, self.model.orientation]

    # --- TEXT

    def get_font(self, font, font_flags):
        if font_flags & fig_const.PSFONT_TEXT:
            # A PostScript font
            name = fig_const.PS_FONT.get(font)
        else:
            # A TeX font. map to psfont
            name = fig_const.LATEX_FONT_MAP.get(font)
        return name

    # --- PIC

    def get_pic_angle(self, obj):
        p = obj.points
        direction = (p[0][0] < p[1][0], p[1][1] < p[2][1])
        direction_map = {
            (True, True): 0.0,
            (True, False): 90.0,
            (False, True): 270.0,
            (False, False): 180.0
        }
        return direction_map.get(direction, 0.0)
