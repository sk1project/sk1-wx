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

from uc2 import utils, sk2const, libgeom
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

    def translate(self, cgm_doc, sk2_doc):
        self.sk2_doc = sk2_doc
        self.sk2_model = sk2_doc.model
        self.sk2_mtds = sk2_doc.methods
        self.page = self.sk2_mtds.get_page()
        self.page.childs = []

        for element in cgm_doc.childs:
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

    def process_element(self, element):
        signature = cgm_const.CGM_ID.get(
            element.element_id, '').replace(' ', '_').lower()
        if signature:
            mtd = getattr(self, '_' + signature, None)
            if mtd:
                mtd(element)
        for child in element.childs:
            self.process_element(child)

    # READER ------
    def read_fmt(self, fmt, chunk):
        sz = struct.calcsize(fmt)
        return struct.unpack(fmt, chunk[:sz]), chunk[sz:]

    def read_int(self, chunk):
        fmt, fn = cgm_utils.INT_F[self.cgm['intprec']]
        return fn(fmt, chunk)

    def read_title(self, chunk):
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

    def get_style(self):
        # TODO: get real stroke style
        return [[], [], [], []]

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

    # Metafile description
    def _begin_metafile(self, element):
        self.sk2_model.metainfo[3] = self.read_title(element.params)[0]
        self.cgm = self.cgm_defaults = copy.deepcopy(cgm_const.CGM_INIT)

    def _metafile_description(self, element):
        if self.sk2_model.metainfo[3]:
            self.sk2_model.metainfo[3] += '\n\n'
        self.sk2_model.metainfo[3] += self.read_title(element.params)[0]

    def _vdc_type(self, element):
        if element.params:
            self.cgm['vdc.type'] = utils.uint16_be(element.params[:2])
        if self.cgm['vdc.type'] == cgm_const.VDC_TYPE_INT:
            self.cgm['vdc.size'] = self.cgm['vdc.intsize']
            self.cgm['vdc.prec'] = self.cgm['vdc.intprec']
            self.cgm['vdc.extend'] = self.cgm['vdc.intextend']
        else:
            self.cgm['vdc.size'] = self.cgm['vdc.realsize']
            self.cgm['vdc.prec'] = self.cgm['vdc.realprec']
            self.cgm['vdc.extend'] = self.cgm['vdc.realextend']

    def _application_data(self, element):
        if self.sk2_model.metainfo[3]:
            self.sk2_model.metainfo[3] += '\n\n'
        self.sk2_model.metainfo[3] += self.read_title(element.params[2:])[0]

    def _integer_precision(self, element):
        self.cgm['intsize'] = utils.uint16_be(element.params) / 8
        if self.cgm['intsize'] not in (8, 16, 24, 32):
            raise Exception('Unsupported integer precision %s' %
                            repr(self.cgm['intsize']))
        self.cgm['intprec'] = self.cgm['intsize'] - 1

    def _real_precision(self, element):
        prec = (utils.uint16_be(element.params[2:4]),
                utils.uint16_be(element.params[4:]))
        prec_type = cgm_const.REAL_PRECISION_MAP.get(prec)
        if prec_type is None:
            raise Exception('Unsupported real precision %s' % repr(prec))
        self.cgm['realprec'] = prec_type

    def _index_precision(self, element):
        self.cgm['inxsize'] = utils.uint16_be(element.params) / 8
        if self.cgm['inxsize'] not in (8, 16, 24, 32):
            raise Exception('Unsupported index precision %s' %
                            repr(self.cgm['intsize']))
        self.cgm['inxprec'] = self.cgm['inxsize'] - 1

    def _colour_precision(self, element):
        sz = element.params_sz
        color_prec = utils.uint16_be(element.params[sz - 2:sz])
        absstruct = cgm_const.COLOR_PRECISION_MAP.get(color_prec)
        if absstruct is None:
            raise Exception('Unsupported color precision %d' % color_prec)
        self.cgm['color.absstruct'] = absstruct

    def _colour_index_precision(self, element):
        sz = element.params_sz
        index_prec = utils.uint16_be(element.params[sz - 2:sz])
        absstruct = cgm_const.COLOR_INDEX_PRECISION_MAP.get(index_prec)
        if absstruct is None:
            raise Exception('Unsupported color index precision %d' %
                            index_prec)
        self.cgm['color.inxstruct'] = absstruct

    def _maximum_colour_index(self, element):
        sz = utils.uint16_be(element.params)
        self.cgm['color.maxindex'] = sz
        self.cgm['color.table'] = cgm_const.create_color_table(sz)

    def _colour_value_extent(self, element):
        fmt = self.cgm['color.absstruct']
        sz = struct.calcsize(fmt)
        bottom = struct.unpack(fmt, element.params[:sz])
        top = struct.unpack(fmt, element.params[sz:2 * sz])
        self.cgm['color.offset'] = tuple(
            l * r for l, r in zip(bottom, (1.0, 1.0, 1.0)))
        self.cgm['color.scale'] = tuple(
            l - r for l, r in zip(top, self.cgm['color.offset']))

    def _font_list(self, element):
        self.cgm['color.absstruct'] = fonts = []
        pos = 0
        while pos < element.params_sz:
            sz = utils.byte2py_int(element.params[pos])
            pos += 1
            fonts.append(element.params[pos:pos + sz].strip())
            pos += sz

    def _vdc_extent(self, element):
        chunk = element.params
        ll, chunk = self.read_point(chunk)
        ur, chunk = self.read_point(chunk)
        self.cgm['vdc.extend'] = (ll, ur)

    # Picture references
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

        name = self.read_title(element.params)[0]
        self.layer = self.sk2_mtds.add_layer(self.page, name)

    def _begin_picture_body(self, _element):
        self.set_trafo(self.cgm['vdc.extend'])

    # Structural elements
    def _scaling_mode(self, element):
        chunk = element.params
        self.cgm['scale.mode'], chunk = self.read_enum(chunk)
        precision = None if self.cgm['realprec'] in (2, 3) else 2
        self.cgm['scale.metric'], chunk = self.read_real(chunk, precision)
        if self.cgm['scale.mode'] == 1 and self.cgm['scale.metric'] == 0:
            self.cgm['scale.mode'] = 0

    def _colour_selection_mode(self, element):
        self.cgm['color.mode'] = self.read_enum(element.params)[0]

    def _line_width_specification_mode(self, element):
        self.cgm['line.widthmode'] = self.read_enum(element.params)[0]

    def _marker_size_specification_mode(self, element):
        self.cgm['marker.sizemode'] = self.read_enum(element.params)[0]

    def _edge_width_specification_mode(self, element):
        self.cgm['edge.widthmode'] = self.read_enum(element.params)[0]

    def _background_colour(self, element):
        color = self.read_color(element.params)[0]
        # TODO: create rect as bg

    def _vdc_integer_precision(self, element):
        bit_depth = self.read_int(element.params)
        if bit_depth in (8, 16, 24, 32):
            self.cgm['vdc.intsize'] = bit_depth / 8
            self.cgm['vdc.intprec'] = self.cgm['vdc.intsize'] - 1
            if self.cgm['vdc.type'] == 0:
                self.cgm['vdc.size'] = self.cgm['vdc.intsize']
                self.cgm['vdc.prec'] = self.cgm['vdc.intprec']
        else:
            raise Exception('Unsupported vdc integer precision %d' % bit_depth)

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

    # ### Line related
    def _line(self, element):
        paths = [[[], [], sk2const.CURVE_OPENED], ]
        # paths = [[points[0], points[1:], sk2const.CURVE_OPENED], ]

        cfg = self.layer.config
        sk2_style = self.get_style()
        sk2_style[0] = []
        curve = sk2_model.Curve(cfg, self.layer, paths,
                                self.get_trafo(), sk2_style)
        # self.layer.childs.append(curve)

    def _polyline(self, element):
        pass

    def _rectangle(self, element):
        pass

    def _circle(self, element):
        pass

    def _ellipse(self, element):
        pass

    def _polygon(self, element):
        pass


class SK2_to_CGM_Translator(object):
    def translate(self, sk2_doc, cgm_doc): pass
