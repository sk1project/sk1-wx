# -*- coding: utf-8 -*-
#
#  Copyright (C) 2019 by Igor E. Novikov
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

import colorsys
import logging
from copy import deepcopy

from uc2 import uc2const, sk2const, cms, utils
from uc2.formats.cmx import cmx_const
from uc2.formats.sk2 import sk2_model

LOG = logging.getLogger(__name__)

CMX_SK2_UNITS = {
    cmx_const.CONT_UNIT_MM: uc2const.UNIT_MM,
    cmx_const.CONT_UNIT_IN: uc2const.UNIT_IN,
}

CMX_CAP_MAP = {
    cmx_const.CMX_MITER_CAP: sk2const.CAP_BUTT,
    cmx_const.CMX_ROUND_CAP: sk2const.CAP_ROUND,
    cmx_const.CMX_SQUARE_CAP: sk2const.CAP_SQUARE,
}

CMX_JOIN_MAP = {
    cmx_const.CMX_MITER_JOIN: sk2const.JOIN_MITER,
    cmx_const.CMX_ROUND_JOIN: sk2const.JOIN_ROUND,
    cmx_const.CMX_BEVEL_JOIN: sk2const.JOIN_BEVEL,
}


class CMX_to_SK2_Translator(object):
    sk2_doc = None
    sk2_model = None
    sk2_mtds = None
    cmx_doc = None
    cmx_cfg = None
    cmx_model = None
    v1 = False
    rifx = False
    _colors = None
    _outlines = None
    _stack = None
    trafo = None
    scale = 1.0

    def translate(self, cmx_doc, sk2_doc):
        self.sk2_doc = sk2_doc
        self.sk2_model = sk2_doc.model
        self.sk2_mtds = sk2_doc.methods
        self.cmx_doc = cmx_doc
        self.cmx_cfg = cmx_doc.config
        self.cmx_model = cmx_doc.model
        self._colors = []
        self._outlines = []
        self._stack = []
        self.trafo = sk2const.NORMAL_TRAFO

        self.set_cmx_const()
        self.translate_doc()
        self.sk2_doc.update()

        self.sk2_doc = None
        self.sk2_model = None
        self.sk2_mtds = None
        self.cmx_doc = None
        self.cmx_cfg = None
        self.cmx_model = None
        self._colors = None
        self._outlines = None
        self._stack = None
        self.trafo = None

    def set_cmx_const(self):
        cont = self.cmx_model.chunk_map[cmx_const.CONT_ID]
        self.v1 = self.cmx_cfg.v1
        self.rifx = self.cmx_cfg.rifx
        # Trafo & unit definition
        unit = CMX_SK2_UNITS.get(cont.data['unit'], uc2const.UNIT_MM)
        self.sk2_model.doc_units = unit
        factor = utils.double2py_float(cont.data['factor'], self.cmx_cfg.rifx)
        self.scale = factor * uc2const.unit_dict[unit]
        self.trafo = [self.scale, 0.0, 0.0, self.scale, 0.0, 0.0]
        # Color processing
        if self.v1:
            self.set_v1_colors()

    def set_v1_colors(self):
        rclr = self.cmx_model.chunk_map[cmx_const.RCLR_ID]
        colors = rclr.data['colors']
        for model, _pal, vals in colors:
            model = cmx_const.COLOR_MODEL_MAP.get(model, cmx_const.CMX_INVALID)
            clr = sk2const.CMYK_BLACK
            if model == cmx_const.CMX_CMYK:
                vals = cms.val_100_to_dec(vals)
                clr = [uc2const.COLOR_CMYK, vals, 1.0, '']
            elif model == cmx_const.CMX_CMYK255:
                vals = cms.val_255_to_dec(vals)
                clr = [uc2const.COLOR_CMYK, vals, 1.0, '']
            elif model == cmx_const.CMX_CMY:
                vals = cms.val_255_to_dec(vals) + (0.0,)
                clr = [uc2const.COLOR_CMYK, vals, 1.0, '']
            elif model == cmx_const.CMX_RGB:
                vals = cms.val_255_to_dec(vals)
                clr = [uc2const.COLOR_RGB, vals, 1.0, '']
            elif model == cmx_const.CMX_HSB:
                first = vals[0] * 255 + vals[1] \
                    if self.rifx else vals[0] + vals[1] * 255
                vals = (first / 360.0, vals[2] / 255.0, vals[3] / 255.0)
                r, g, b = colorsys.hsv_to_rgb(*vals)
                clr = [uc2const.COLOR_RGB, [r, g, b], 1.0, '']
            elif model == cmx_const.CMX_HLS:
                first = vals[0] * 255 + vals[1] \
                    if self.rifx else vals[0] + vals[1] * 255
                vals = (first / 360.0, vals[2] / 255.0, vals[3] / 255.0)
                r, g, b = colorsys.hls_to_rgb(*vals)
                clr = [uc2const.COLOR_RGB, [r, g, b], 1.0, '']
            elif model == cmx_const.CMX_BW:
                vals = [1.0, 1.0, 1.0] if vals[0] else [0.0, 0.0, 0.0]
                clr = [uc2const.COLOR_RGB, vals, 1.0, '']
            elif model == cmx_const.CMX_GRAY:
                clr = [uc2const.COLOR_GRAY, [vals[0] / 255.0, ], 1.0, '']
            elif model == cmx_const.CMX_YIQ255:
                y = vals[0] / 255.0
                i = 2.0 * vals[1] / 255.0 - 1.0
                q = 2.0 * vals[2] / 255.0 - 1.0
                r, g, b = colorsys.yiq_to_rgb(y, i, q)
                clr = [uc2const.COLOR_RGB, [r, g, b], 1.0, '']
            elif model == cmx_const.CMX_LAB:
                vals = cms.val_255_to_dec(vals)
                clr = [uc2const.COLOR_LAB, vals, 1.0, '']

            self._colors.append(clr)

    def _decode(self, val):
        if self.v1:
            return val.decode(self.cmx_cfg.fallback_encoding,
                              'replace').encode('utf8')
        try:
            return val.decode(self.cmx_cfg.system_encoding).encode('utf8')
        except:
            return val.decode(self.cmx_cfg.fallback_encoding,
                              'replace').encode('utf8')

    def translate_doc(self):
        riff_pages = [item[0] for item in self.cmx_model.chunk_map['pages']]
        sk2_page = self.sk2_mtds.get_page()
        sk2_layer = self.sk2_mtds.get_layer(sk2_page)
        self._stack = [sk2_page, sk2_layer]
        for page in riff_pages:
            for child in page.childs:
                if self.v1:
                    self.translate_v1_el(child)

    def translate_v1_el(self, el):
        code = el.data['code']
        if code == cmx_const.BEGIN_PAGE:
            if not self._stack:
                self._stack.append(self.sk2_mtds.add_page())
        elif code == cmx_const.END_PAGE:
            self._stack = []
        elif code == cmx_const.BEGIN_LAYER:
            name = self._decode(el.data['layer_name'])
            if not self._stack[-1].is_layer:
                page = self._stack[0]
                self._stack.append(self.sk2_mtds.add_layer(page, name))
            else:
                self._stack[-1].name = name
        elif code == cmx_const.END_LAYER:
            self._stack = self._stack[:-1]
        elif code == cmx_const.BEGIN_GROUP:
            group = sk2_model.Group(self._stack[-1].config)
            self.sk2_mtds.append_object(group, self._stack[-1])
            self._stack.append(group)
        elif code == cmx_const.END_GROUP:
            group = self._stack[-1]
            self._stack = self._stack[:-1]
            if not group.childs:
                self.sk2_mtds.delete_object(group)
        elif code == cmx_const.POLYCURVE:
            curve = self.translate_v1_polycurve(el)
            if curve is not None:
                self.sk2_mtds.append_object(curve, self._stack[-1])

        for child in el.childs:
            self.translate_v1_el(child)

    def _get_color(self, color_index):
        return deepcopy(self._colors[color_index - 1]
                        if color_index - 1 < len(self._colors)
                        else sk2const.RGB_BLACK)

    def _get_prop(self, tag, prop, index=None, default=None):
        tag_obj = self.cmx_model.chunk_map.get(tag)
        if tag_obj is None:
            return default
        prop_value = tag_obj.data.get(prop)
        if prop_value is None:
            return default
        if index is None:
            return prop_value
        return prop_value[index] if index < len(prop_value) else default

    def get_v1_style(self, el):
        style = [[], [], [], []]
        # FILL
        fill_type = el.data.get('fill_type', cmx_const.INSTR_FILL_EMPTY)
        if fill_type == cmx_const.INSTR_FILL_UNIFORM:
            color = self._get_color(el.data['fill'][0])
            style[0] = [sk2const.FILL_CLOSED_ONLY, sk2const.FILL_SOLID, color]
        # OUTLINE
        outline_index = el.data.get('outline')
        if outline_index is not None:
            # outline (style, screen, color, arrowheads, pen, dash)
            outline = self._get_prop('rotl', 'outlines', outline_index - 1)
            # style bytes
            spec, capjoin = self._get_prop('rott', 'linestyles', outline[0] - 1)
            if not spec & 1:
                join = CMX_JOIN_MAP.get((capjoin & 0xf0) >> 4,
                                        sk2const.JOIN_MITER)
                cap = CMX_CAP_MAP.get(capjoin & 0x0f, sk2const.CAP_BUTT)

                # width
                # pen: (width, aspect, angle, matrix_flag, matrix(opt))
                width = self._get_prop('rpen', 'pens', outline[4] - 1)[0]
                width *= self.scale

                color = self._get_color(outline[2])

                # dashes
                dashes = [] if not spec & 0x04 else list(
                    self._get_prop('rdot', 'dashes', outline[5] - 1))

                LOG.info('DASHES %s', dashes)

                behind_fill = 1 if spec & 0x10 else 0
                scale_flag = 1 if spec & 0x20 else 0

                style[1] = [sk2const.STROKE_MIDDLE, width, color, dashes,
                            cap, join, 10.433, behind_fill, scale_flag, []]

        return style

    def translate_v1_polycurve(self, el):
        points = el.data.get('points')
        nodes = el.data.get('nodes')
        if not points or not nodes or len(points) != len(nodes):
            return

        index = 0
        path = None
        paths = []
        curve = None
        close = 0

        def _append_path(paths, path, close):
            if path and path[1]:
                paths.append(path)
                if close:
                    if path[1][-1] != path[0]:
                        path[1].append([] + path[0])
                    path[2] = sk2const.CURVE_CLOSED

        while index < len(points):
            point = list(points[index])
            node = nodes[index]
            type = (node & 0xc0) >> 6
            if type == 0:
                _append_path(paths, path, close)
                close = node & 0x08
                path = [point, [], sk2const.CURVE_OPENED]
            elif type == 1:
                path[1].append(point)
            elif type == 3:
                p = [point, list(points[index + 1]),
                     list(points[index + 2]), sk2const.NODE_CUSP]
                path[1].append(p)
                index += 2
            index += 1

        _append_path(paths, path, close)
        if paths:
            style = self.get_v1_style(el)
            curve = sk2_model.Curve(self.sk2_model.config, paths=paths,
                                    trafo=[] + self.trafo, style=style)
        return curve
