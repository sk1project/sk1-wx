# -*- coding: utf-8 -*-
#
#  Copyright (C) 2017-2019 by Igor E. Novikov
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

import copy
import struct

from uc2 import utils, sk2const, libgeom, uc2const, libpango
from uc2.formats.cgm import cgm_const, cgm_utils
from uc2.formats.sk2 import sk2_model


def sign(num):
    return num / abs(num)


class CGM_to_SK2_Translator(object):
    sk2_doc = None
    sk2_model = None
    sk2_mtds = None
    page = None
    layer = None
    cgm = None
    cgm_defaults = None
    trafo = None
    scale = None
    fontmap = None

    def translate(self, cgm_doc, sk2_doc):
        self.sk2_doc = sk2_doc
        self.sk2_model = sk2_doc.model
        self.sk2_mtds = sk2_doc.methods
        self.page = self.sk2_mtds.get_page()
        self.page.childs = []
        self.fontmap = []

        for element in cgm_doc.model.childs:
            if element.element_id == cgm_const.END_METAFILE:
                break
            self.process_element(element)

        self.sk2_doc = None
        self.sk2_model = None
        self.sk2_mtds = None
        self.page = None
        self.layer = None
        self.cgm = None
        self.cgm_defaults = None
        self.fontmap = None

    def process_element(self, element):
        signature = cgm_const.CGM_ID.get(
            element.element_id, '').replace(' ', '_').lower()
        if signature:
            mtd = getattr(self, '_' + signature, None)
            if mtd:
                mtd(element)
        for child in element.childs:
            self.process_element(child)

    # READER ------>
    def read_fmt(self, fmt, chunk):
        sz = struct.calcsize(fmt)
        return struct.unpack(fmt, chunk[:sz]), chunk[sz:]

    def read_int(self, chunk):
        fmt, fn = cgm_utils.INT_F[self.cgm['intprec']]
        return fn(fmt, chunk)

    def read_str(self, chunk):
        if not chunk:
            return '', chunk
        sz = utils.byte2py_int(chunk[0])
        title = chunk[1:1 + sz]
        return title, chunk[sz:]

    def read_real(self, chunk, precision=None):
        precision = self.cgm['realprec'] if precision is None else precision
        fmt, fn = cgm_utils.REAL_F[precision]
        return fn(fmt, chunk)

    def read_enum(self, chunk):
        return cgm_utils._unpack('!h', chunk)

    def read_vdc(self, chunk):
        fmt, fn = cgm_utils.VDC_F[self.cgm['vdc.type']][self.cgm['vdc.prec']]
        return fn(fmt, chunk)

    def read_point(self, chunk):
        x, chunk = self.read_vdc(chunk)
        y, chunk = self.read_vdc(chunk)
        return (x, y), chunk

    def read_points(self, chunk):
        sz = 2 * self.cgm['vdc.size']
        points = []
        while len(chunk) >= sz:
            point, chunk = self.read_point(chunk)
            points.append(point)
        return points

    def read_path(self, chunk):
        points = self.read_points(chunk)
        return [points[0], points[1:], sk2const.CURVE_OPENED]

    def read_color(self, chunk):
        if self.cgm['color.mode'] == 1:
            color, chunk = self.read_fmt(self.cgm['color.absstruct'], chunk)
            color = [x - y for x, y in zip(color, self.cgm['color.offset'])]
            color = [x / y for x, y in zip(color, self.cgm['color.scale'])]
        else:
            (indx,), chunk = self.read_fmt(self.cgm['color.inxstruct'], chunk)
            color = self.cgm['color.table'][indx % self.cgm['color.maxindex']]
        return color, chunk

    # READER END =====

    def get_fill_style(self, cgm_color=None):
        if cgm_color:
            color = [uc2const.COLOR_RGB, list(cgm_color), 1.0, '']
            return [sk2const.FILL_EVENODD, sk2const.FILL_SOLID, color]
        return []

    def get_stroke_style(self):
        width = self.cgm['line.width']
        if self.cgm['line.widthmode'] == 0:
            width *= self.scale
        color = [uc2const.COLOR_RGB, list(self.cgm['line.color']), 1.0, '']
        dash = self.cgm['line.dashtable'][self.cgm['line.type'] - 1]
        cap = sk2const.CAP_BUTT
        join = sk2const.JOIN_MITER
        miter_limit = 10.433
        behind_flag = 0
        scalable_flag = 0
        markers = []
        return [sk2const.STROKE_MIDDLE, width, color, dash, cap, join,
                miter_limit, behind_flag, scalable_flag, markers]

    def get_edge_style(self):
        if not self.cgm['edge.width']:
            return []
        width = self.cgm['edge.width']
        if self.cgm['edge.widthmode'] == 0:
            width *= self.scale
        color = [uc2const.COLOR_RGB, list(self.cgm['line.color']), 1.0, '']
        dash = self.cgm['edge.dashtable'][self.cgm['edge.type'] - 1]
        cap = sk2const.CAP_BUTT
        join = sk2const.JOIN_MITER
        miter_limit = 10.433
        behind_flag = 0
        scalable_flag = 0
        markers = []
        return [sk2const.STROKE_MIDDLE, width, color, dash, cap, join,
                miter_limit, behind_flag, scalable_flag, markers]

    def get_text_style(self):
        cgm_font = self.fontmap[self.cgm['text.fontindex']]
        family, face = libpango.find_font_and_face(cgm_font)
        print family, face
        size = self.cgm['text.height'] * self.scale
        alignment = 0
        spacing = []
        cluster_flag = True
        return [family, face, size, alignment, spacing, cluster_flag]

    def get_style(self, fill=False, stroke=False, text=False):
        if stroke:
            return [[], self.get_stroke_style(), [], []]

        elif text:
            fill_style = self.get_fill_style(cgm_color=self.cgm['text.color'])
            text_style = self.get_text_style()
            return [fill_style, [], text_style, []]

        elif fill:
            fill_style = self.get_fill_style(cgm_color=self.cgm['fill.color'])
            stroke_style = self.get_edge_style()
            return [fill_style, stroke_style, [], []]

        # TODO: get real stroke style
        return [self.get_fill_style() if fill else [],
                self.get_stroke_style() if stroke else [],
                self.get_text_style() if text else [], []]

    def set_trafo(self, extend):
        if self.cgm['scale.mode'] == 0:
            left, bottom = extend[0]
            right, top = extend[1]
            width = right - left
            height = top - bottom
            sc = 841 / (1.0 * max(abs(width), abs(height)))
        else:
            left = 0
            bottom = 0
            width = 1
            height = 1
            sc = self.cgm['scale.metric'] * 72 / 25.4
        self.scale = sc
        tr = [1.0, 0.0, 0.0, 1.0, -left, -bottom]
        scale = [sign(width) * sc, 0.0, 0.0, sign(height) * sc, 0.0, 0.0]
        # TODO: check trafo order
        self.trafo = libgeom.multiply_trafo(scale, tr)

    def get_trafo(self):
        return copy.deepcopy(self.trafo)

    # METAFILE RECODRS ----->

    # 0x0020
    def _begin_metafile(self, element):
        self.sk2_model.metainfo[3] = self.read_str(element.params)[0]
        self.cgm = self.cgm_defaults = copy.deepcopy(cgm_const.CGM_INIT)

    # 0x0060
    def _begin_picture(self, element):
        self.cgm = copy.deepcopy(self.cgm_defaults)

        if self.cgm['vdc.extend'] is None:
            if self.cgm['vdc.type'] == 0:
                self.cgm['vdc.extend'] = self.cgm['vdc.intextend']
                self.cgm['vdc.size'] = self.cgm['vdc.intsize']
                self.cgm['vdc.prec'] = self.cgm['vdc.intprec']
            else:
                self.cgm['vdc.extend'] = self.cgm['vdc.realextend']
                self.cgm['vdc.size'] = self.cgm['vdc.realsize']
                self.cgm['vdc.prec'] = self.cgm['vdc.realprec']
        if self.cgm['vdc.prec'] is None:
            if self.cgm['vdc.type'] == 0:
                self.cgm['vdc.size'] = self.cgm['vdc.intsize']
                self.cgm['vdc.prec'] = self.cgm['vdc.intprec']
            else:
                self.cgm['vdc.size'] = self.cgm['vdc.realsize']
                self.cgm['vdc.prec'] = self.cgm['vdc.realprec']

        vdc = self.cgm['vdc.extend']
        height = vdc[1][1] - vdc[0][1]
        width = vdc[1][0] - vdc[0][0]
        maxsz = max(abs(height), abs(width))

        if self.cgm['clip.rect'] is None:
            self.cgm['clip.rect'] = vdc

        if self.cgm['marker.size'] is None:
            if self.cgm['marker.sizemode'] == 0:
                self.cgm['marker.size'] = maxsz / 100.0
            else:
                self.cgm['marker.size'] = 3

        if self.cgm['text.height'] is None:
            self.cgm['text.height'] = maxsz / 100.0

        if self.cgm['edge.width'] is None:
            if self.cgm['edge.widthmode'] == 0:
                self.cgm['edge.width'] = maxsz / 1000.0
            else:
                self.cgm['edge.width'] = 1

        if self.cgm['line.width'] is None:
            if self.cgm['line.widthmode'] == 0:
                self.cgm['line.width'] = maxsz / 1000.0
            else:
                self.cgm['line.width'] = 1

        name = self.read_str(element.params)[0]
        self.layer = self.sk2_mtds.add_layer(self.page, name)

    # 0x0080
    def _begin_picture_body(self, _element):
        self.set_trafo(self.cgm['vdc.extend'])

    # 0x1040
    def _metafile_description(self, element):
        if self.sk2_model.metainfo[3]:
            self.sk2_model.metainfo[3] += '\n\n'
        self.sk2_model.metainfo[3] += self.read_str(element.params)[0]

    # 0x1060
    def _vdc_type(self, element):
        self.cgm['vdc.type'] = self.read_enum(element.params)[0]
        if self.cgm['vdc.type'] == cgm_const.VDC_TYPE_INT:
            self.cgm['vdc.size'] = self.cgm['vdc.intsize']
            self.cgm['vdc.prec'] = self.cgm['vdc.intprec']
            self.cgm['vdc.extend'] = self.cgm['vdc.intextend']
        else:
            self.cgm['vdc.size'] = self.cgm['vdc.realsize']
            self.cgm['vdc.prec'] = self.cgm['vdc.realprec']
            self.cgm['vdc.extend'] = self.cgm['vdc.realextend']

    # 0x1080
    def _integer_precision(self, element):
        bits = self.read_int(element.params)[0]
        if bits not in (8, 16, 24, 32):
            raise Exception('Unsupported %d-bit integer precision' % bits)
        self.cgm['intsize'] = bits / 8
        self.cgm['intprec'] = self.cgm['intsize'] - 1

    # 0x10a0
    def _real_precision(self, element):
        real_type, chunk = self.read_enum(element.params)
        p0, chunk = self.read_int(chunk)
        p1, chunk = self.read_int(chunk)
        prec = (p0, p1)
        prec_type = cgm_const.REAL_PRECISION_MAP.get(prec)
        if prec_type is None:
            raise Exception('Unsupported real precision %s' % repr(prec))
        self.cgm['realprec'] = prec_type

    # 0x10c0
    def _index_precision(self, element):
        bits = self.read_int(element.params)[0]
        if bits not in (8, 16, 24, 32):
            raise Exception('Unsupported %d-bit index precision' % bits)
        self.cgm['inxsize'] = bits / 8
        self.cgm['inxprec'] = self.cgm['inxsize'] - 1

    # 0x10e0
    def _colour_precision(self, element):
        bits = self.read_int(element.params)[0]
        absstruct = cgm_const.COLOR_PRECISION_MAP.get(bits)
        if absstruct is None:
            raise Exception('Unsupported %d-bit color precision' % bits)
        self.cgm['color.absstruct'] = absstruct

    # 0x1100
    def _colour_index_precision(self, element):
        bits = self.read_int(element.params)[0]
        inxstruct = cgm_const.COLOR_INDEX_PRECISION_MAP.get(bits)
        if inxstruct is None:
            raise Exception('Unsupported %d-bit color index precision' % bits)
        self.cgm['color.inxstruct'] = inxstruct

    # 0x1120
    def _maximum_colour_index(self, element):
        (sz,) = self.read_fmt(self.cgm['color.inxstruct'], element.params)[0]
        self.cgm['color.maxindex'] = sz
        self.cgm['color.table'] = cgm_const.create_color_table(sz)

    # 0x1140
    def _colour_value_extent(self, element):
        chunk = element.params
        bottom, chunk = self.read_fmt(self.cgm['color.absstruct'], chunk)
        top, chunk = self.read_fmt(self.cgm['color.absstruct'], chunk)
        self.cgm['color.offset'] = tuple(
            l * r for l, r in zip(bottom, (1.0, 1.0, 1.0)))
        self.cgm['color.scale'] = tuple(
            l - r for l, r in zip(top, self.cgm['color.offset']))

    # 0x11a0
    def _font_list(self, element):
        chunk = element.params[:element.params_sz]
        while chunk:
            font, chunk = self.read_str(chunk)
            self.fontmap.append(font.strip())

    # Structural elements
    # 0x2020
    def _scaling_mode(self, element):
        chunk = element.params
        self.cgm['scale.mode'], chunk = self.read_enum(chunk)
        precision = None if self.cgm['realprec'] in (2, 3) else 2
        self.cgm['scale.metric'], chunk = self.read_real(chunk, precision)
        if self.cgm['scale.mode'] == 1 and self.cgm['scale.metric'] == 0:
            self.cgm['scale.mode'] = 0

    # 0x2040
    def _colour_selection_mode(self, element):
        self.cgm['color.mode'] = self.read_enum(element.params)[0]

    # 0x2060
    def _line_width_specification_mode(self, element):
        self.cgm['line.widthmode'] = self.read_enum(element.params)[0]

    # 0x2080
    def _marker_size_specification_mode(self, element):
        self.cgm['marker.sizemode'] = self.read_enum(element.params)[0]

    # 0x20a0
    def _edge_width_specification_mode(self, element):
        self.cgm['edge.widthmode'] = self.read_enum(element.params)[0]

    # 0x20c0
    def _vdc_extent(self, element):
        chunk = element.params
        ll, chunk = self.read_point(chunk)
        ur, chunk = self.read_point(chunk)
        self.cgm['vdc.extend'] = (ll, ur)

    # 0x20e0
    def _background_colour(self, element):
        color = self.read_color(element.params)[0]
        # TODO: create rect as bg

    # 0x3020
    def _vdc_integer_precision(self, element):
        bit_depth = self.read_int(element.params)[0]
        if bit_depth in (8, 16, 24, 32):
            self.cgm['vdc.intsize'] = bit_depth / 8
            self.cgm['vdc.intprec'] = self.cgm['vdc.intsize'] - 1
            if self.cgm['vdc.type'] == 0:
                self.cgm['vdc.size'] = self.cgm['vdc.intsize']
                self.cgm['vdc.prec'] = self.cgm['vdc.intprec']
        else:
            raise Exception('Unsupported vdc integer precision %d' % bit_depth)

    # 0x3040
    def _vdc_real_precision(self, element):
        chunk = element.params
        prec_type, chunk = self.read_enum(chunk)
        x, chunk = self.read_int(chunk)
        y, chunk = self.read_int(chunk)
        precision = (x, y)
        if prec_type == 1:
            if precision == (16, 16):
                self.cgm['vdc.realprec'] = 0  # 32 bit fixed precision
            elif precision == (32, 32):
                self.cgm['vdc.realprec'] = 1  # 64 bit fixed precision
            else:
                raise Exception(
                    'Unsupported real precision (%d, %d)' % precision)
        else:
            if precision == (9, 23):
                self.cgm['vdc.realprec'] = 2  # 32 bit floating point
            elif precision == (12, 52):
                self.cgm['vdc.realprec'] = 3  # 64 bit floating point
            else:
                raise Exception(
                    'Unsupported real precision (%d, %d)' % precision)

        if self.cgm['vdc.type'] == 1:
            self.cgm['vdc.size'] = self.cgm['vdc.realsize']
            self.cgm['vdc.prec'] = self.cgm['vdc.realprec']

    # 0x30a0
    def _clip_rectangle(self, element):
        chunk = element.params
        p0, chunk = self.read_point(chunk)
        p1, chunk = self.read_point(chunk)
        self.cgm['clip.rect'] = (p0, p1)

    # ### Line related
    # 0x4020
    def _polyline(self, element):
        curve = sk2_model.Curve(self.layer.config, self.layer,
                                [self.read_path(element.params), ],
                                self.get_trafo(), self.get_style(stroke=True))
        self.layer.childs.append(curve)

    # 0x4040
    def _disjoint_polyline(self, element):
        points = self.read_points(element.params)
        first_point = points[0]
        paths = []
        for point in points[1:]:
            paths.append([first_point, [point, ], sk2const.CURVE_OPENED])
            first_point = point
        curve = sk2_model.Curve(self.layer.config, self.layer, paths,
                                self.get_trafo(), self.get_style(stroke=True))
        self.layer.childs.append(curve)

    # 0x4080
    def _text(self, element):
        (x, y), chunk = self.read_point(element.params)
        flg, chunk = self.read_enum(chunk)
        txt, chunk = self.read_str(chunk)
        trafo = libgeom.multiply_trafo(self.get_trafo(),
                                       [1.0, 0.0, 0.0, 1.0, x, y])
        py, px = self.cgm['text.orientation']
        py = libgeom.normalize_point(py)
        px = libgeom.normalize_point(px)
        p0 = [0.0, 0.0]
        tr = libgeom.sub_points(px, p0) + libgeom.sub_points(py, p0) + p0
        text = sk2_model.Text(self.layer.config, self.layer,
                              p0, txt, -1,
                              libgeom.multiply_trafo(trafo, tr),
                              self.get_style(text=True))
        self.layer.childs.append(text)

    # 0x40e0
    def _polygon(self, element):
        path = self.read_path(element.params)[0]
        if path[0] != path[1][-1]:
            path[1].append([] + path[0])
        path[2] = sk2const.CURVE_CLOSED
        curve = sk2_model.Curve(self.layer.config, self.layer, [path,],
                                self.get_trafo(), self.get_style(fill=True))
        self.layer.childs.append(curve)

    # 0x4100
    def _polygon_set(self):
        pass

    def _rectangle(self, element):
        pass

    def _circle(self, element):
        pass

    def _ellipse(self, element):
        pass

    # 0x7040
    def _application_data(self, element):
        if self.sk2_model.metainfo[3]:
            self.sk2_model.metainfo[3] += '\n\n'
        self.sk2_model.metainfo[3] += self.read_str(element.params[2:])[0]


class SK2_to_CGM_Translator(object):
    def translate(self, sk2_doc, cgm_doc): pass
