# -*- coding: utf-8 -*-
#
#  Copyright (C) 2019 by Maxim S. Barabash
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

from uc2.formats.xar import xar_model, xar_const
from uc2.formats.sk2 import sk2_model
from uc2 import _, uc2const, sk2const, cms
import copy


SK2_UNITS = {
    xar_const.REF_UNIT_PIXELS: uc2const.UNIT_PX,
    xar_const.REF_UNIT_MILLIMETRES: uc2const.UNIT_MM,
    xar_const.REF_UNIT_CENTIMETRES: uc2const.UNIT_CM,
    xar_const.REF_UNIT_METRES: uc2const.UNIT_M,
    xar_const.REF_UNIT_INCHES: uc2const.UNIT_IN,
    xar_const.REF_UNIT_FEET: uc2const.UNIT_FT,
}


class XAR_to_SK2_Translator(object):
    xar_mtds = None
    sk2_doc = None
    sk2_model = None
    sk2_mtds = None
    stack = None
    page = None
    layer = None
    xar = None
    xar_defaults = None
    trafo = None
    scale = None
    fontmap = None
    colors = None
    stack_style = None
    style = None

    def translate(self, xar_doc, sk2_doc):
        self.xar_mtds = xar_doc.methods
        self.sk2_doc = sk2_doc
        self.sk2_model = sk2_doc.model
        self.sk2_mtds = sk2_doc.methods
        self.page = self.sk2_mtds.get_page()
        self.trafo = [-1.0, 0.0, 0.0, -1.0, 0.0, 0.0]
        self.colors = {}

        style = copy.copy(xar_const.XAR_DEFAULT_STYLE)
        self.stack_style = [style]

        rec = xar_doc.model
        self.stack = rec.childs[::-1]
        self.handle_units()
        self.handle_record()

    def handle_record(self, stop_cid=None):
        while self.stack:
            if stop_cid is not None and self.stack[-1].cid == stop_cid:
                break
            rec = self.stack.pop()
            # print '..'*len(self.stack_style), rec.cid
            if rec.childs:
                self.stack.extend(rec.childs[::-1])
            self.process_record(rec)

    def process_record(self, rec):
        cfg = self.sk2_doc.config

        # Navigation records
        if rec.cid == xar_const.TAG_UP:
            self.handle_up(rec, cfg)
        elif rec.cid == xar_const.TAG_DOWN:
            self.handle_down(rec, cfg)

        # Notes
        #TAG_LAYER
        elif rec.cid == xar_const.TAG_SPREADINFORMATION:
            self.handle_spred_information(rec, cfg)

        # Colour reference tags
        elif rec.cid == xar_const.TAG_DEFINECOMPLEXCOLOUR:
            self.handle_definecomplexcolor(rec, cfg)

        # Object tags
        elif rec.cid == xar_const.TAG_PATH:
            raise 1
        elif rec.cid == xar_const.TAG_PATH_RELATIVE_STROKED:
            self.handle_path_relative_stroked(rec, cfg)
        elif rec.cid == xar_const.TAG_PATH_RELATIVE_FILLED:
            self.handle_path_relative_filled(rec, cfg)
        elif rec.cid == xar_const.TAG_PATH_RELATIVE_FILLED_STROKED:
            self.handle_path_relative_filled_stroked(rec, cfg)

        # Attribute tags
        elif rec.cid == xar_const.TAG_FLATFILL:
            self.handle_flatfill(rec, cfg)
        elif rec.cid == xar_const.TAG_LINECOLOUR:
            self.handle_linecolour(rec, cfg)
        elif rec.cid == xar_const.TAG_LINEWIDTH:
            self.handle_linewidth(rec, cfg)

        # special colour fills
        elif rec.cid == xar_const.TAG_FLATFILL_NONE:
            self.handle_flatfill_none(rec, cfg)
        elif rec.cid == xar_const.TAG_FLATFILL_BLACK:
            self.handle_flatfill_black(rec, cfg)
        elif rec.cid == xar_const.TAG_FLATFILL_WHITE:
            self.handle_flatfill_white(rec, cfg)
        elif rec.cid == xar_const.TAG_LINECOLOUR_NONE:
            self.handle_linecolour_none(rec, cfg)
        elif rec.cid == xar_const.TAG_LINECOLOUR_BLACK:
            self.handle_linecolour_black(rec, cfg)
        elif rec.cid == xar_const.TAG_LINECOLOUR_WHITE:
            self.handle_linecolour_white(rec, cfg)

    def handle_down(self, rec, cfg):
        self.style = copy.copy(self.stack_style[-1])
        self.stack_style.append(self.style)

    def handle_up(self, rec, cfg):
        self.style = self.stack_style.pop()

    def handle_units(self):
        self.sk2_mtds.set_doc_units(uc2const.UNIT_PT)

    def handle_definecomplexcolor(self, rec, cfg):
        # TODO: process colour_model, colour_type
        rgb = cms.hexcolor_to_rgb(b"#%s" % rec.rgbcolor)
        colour = [uc2const.COLOR_RGB, rgb, 1.0, rec.colour_name]
        self.colors[rec.idx] = colour

    def handle_flatfill(self, rec, cfg):
        colour = self.colors.get(rec.colour)
        if colour:
            self.style['flat_colour_fill'] = colour
            
    def handle_linecolour(self, rec, cfg):
        colour = self.colors.get(rec.colour)
        if colour:
            self.style['stroke_colour'] = colour

    def handle_flatfill_none(self, rec, cfg):
        self.style['flat_colour_fill'] = None

    def handle_flatfill_black(self, rec, cfg):
        self.style['flat_colour_fill'] = xar_const.RGB_BLACK

    def handle_flatfill_white(self, rec, cfg):
        self.style['flat_colour_fill'] = xar_const.RGB_WHITE

    def handle_linecolour_none(self, rec, cfg):
        self.style['stroke_colour'] = None

    def handle_linecolour_black(self, rec, cfg):
        self.style['stroke_colour'] = xar_const.RGB_BLACK

    def handle_linecolour_white(self, rec, cfg):
        self.style['stroke_colour'] = xar_const.RGB_WHITE

    def handle_linewidth(self, rec, cfg):
        self.style['line_width'] = rec.width

    def handle_path_relative_stroked(self, rec, cfg):
        self.handle_record(xar_const.TAG_UP)
        self.layer = self.page.childs[0]
        curve = sk2_model.Curve(
            cfg, self.layer,
            self.get_path(rec),
            self.get_trafo(),
            self.get_style(rec, stroke=True)
        )
        self.layer.childs.append(curve)

    def handle_path_relative_filled(self, rec, cfg):
        self.handle_record(xar_const.TAG_UP)
        self.layer = self.page.childs[0]
        curve = sk2_model.Curve(
            cfg, self.layer,
            self.get_path(rec),
            self.get_trafo(),
            self.get_style(rec, fill=True)
        )
        self.layer.childs.append(curve)

    def handle_path_relative_filled_stroked(self, rec, cfg):
        self.handle_record(xar_const.TAG_UP)
        self.layer = self.page.childs[0]
        curve = sk2_model.Curve(
            cfg, self.layer,
            self.get_path(rec),
            self.get_trafo(),
            self.get_style(rec, stroke=True, fill=True)
        )
        self.layer.childs.append(curve)

    def handle_spred_information(self, rec, cfg):
        fmt = _('Custom')
        width = rec.width
        height = rec.height
        size = (width, height)
        orient = uc2const.PORTRAIT
        if width > height:
            orient = uc2const.LANDSCAPE
        page_format = [fmt, size, orient]
        self.sk2_mtds.set_page_format(self.page, page_format)
        trafo = [1.0, 0.0, 0.0, 1.0, -1.0 * width / 2.0, -1.0 * height / 2.0]
        self.set_trafo(trafo)

    def set_trafo(self, trafo):
        self.trafo = trafo

    def get_trafo(self):
        return copy.deepcopy(self.trafo)

    def get_style(self, rec, stroke=False, fill=False):
        fill = fill and self.get_fill(rec) or []
        stroke = stroke and self.get_stoke(rec) or []
        return [fill, stroke, [], []]

    def get_fill(self, rec):
        fill_rule = sk2const.FILL_EVENODD
        fill_type = sk2const.FILL_SOLID
        fill_data = self.style['flat_colour_fill']
        if fill_data:
            return [fill_rule, fill_type, fill_data]
        return []

    def get_stoke(self, rec):
        colour = self.style['stroke_colour']
        if colour is None:
            return []
        cap_style = sk2const.CAP_BUTT  # TODO
        join_style = sk2const.JOIN_MITER  # TODO
        rule = sk2const.STROKE_MIDDLE
        width = self.style['line_width']
        colour = self.style['stroke_colour']
        dash = []  # TODO
        miter_limit = self.style['mitre_limit'] / 1000.0
        behind_flag = 0  # TODO
        scalable_flag = 0  # TODO
        markers = [[], []]  # TODO
        return [rule, width, colour, dash, cap_style, join_style, miter_limit,
                behind_flag, scalable_flag, markers]

    def get_path(self, rec):
        paths = []
        for closed, points in self.xar_mtds.read_path(rec):
            marker = sk2const.CURVE_CLOSED if closed else sk2const.CURVE_OPENED
            path = []
            for point in points:
                if len(point) == 3:
                    point = [point[0], point[1], point[2], sk2const.NODE_CUSP]
                path.append(point)
            paths.append([path[0], path[1:], marker])
        return paths


class SK2_to_XAR_Translator(object):
    xar_doc = None
    xar_model = None
    xar_mtds = None
    # page = None
    # fontmap = None

    def translate(self, sk2_doc, xar_doc):
        self.xar_doc = xar_doc
        self.xar_model = xar_doc.model
        self.xar_mtds = xar_doc.methods
        rec = self._TAG_FILEHEADER(sk2_doc)
        self.xar_model.add(rec)
        self.process_element(sk2_doc.model)
        rec = self._TAG_ENDOFFILE(sk2_doc)
        self.xar_model.add(rec)

    def process_element(self, element):
        for child in element.childs:
            self.process_element(child)

    def _TAG_FILEHEADER(self, sk2_doc):
        rec = xar_model.XARRecord(xar_const.TAG_FILEHEADER, 0)
        rec.file_size = 0
        rec.file_type = xar_const.FILE_TYPE_PAPER_PUBLISH
        rec.producer = sk2_doc.appdata.app_name
        rec.producer_version = sk2_doc.appdata.version
        rec.producer_build = sk2_doc.appdata.revision
        return rec

    def _TAG_ENDOFFILE(self, sk2_doc):
        return xar_model.XARRecord(xar_const.TAG_ENDOFFILE, 1)

