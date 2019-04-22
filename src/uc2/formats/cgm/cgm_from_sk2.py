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

import logging

from uc2 import utils, uc2const, libgeom, sk2const
from uc2.formats.cgm import cgm_model, cgm_const

LOG = logging.getLogger(__name__)

SCALE = 39.37 * uc2const.pt_to_mm


def cgm_unit(val, double=False):
    func = utils.py_int2signed_dword if double else utils.py_int2signed_word
    return func(int(round(SCALE * val)), True)


def builder(element_id, **kwargs):
    elf = cgm_model.element_factory
    header = params = ''
    if element_id == cgm_const.BEGIN_METAFILE:
        txt = kwargs.get('txt', 'Computer Graphics Metafile')
        params = utils.py_int2byte(len(txt)) + txt
        header = utils.py_int2word(0x0020 + len(params), True)
    elif element_id == cgm_const.END_METAFILE:
        header = '\x00\x40'
    elif element_id == cgm_const.METAFILE_VERSION:
        version = kwargs.get('version', 1)
        params = utils.py_int2word(version, True)
        header = '\x10\x22'
    elif element_id == cgm_const.METAFILE_DESCRIPTION:
        txt = kwargs.get('description', 'Created by UniConvertor')
        params = utils.py_int2byte(len(txt)) + txt
        header = '\x10\x5f' + utils.py_int2word(len(params), True)
    elif element_id == cgm_const.METAFILE_ELEMENT_LIST:
        header = '\x11\x66'
        params = '\x00\x01\xff\xff\x00\x01'
    elif element_id == cgm_const.VDC_TYPE:
        header = '\x10\x62'
        params = '\x00\x00'
    elif element_id == cgm_const.INTEGER_PRECISION:
        header = '\x10\x82'
        params = '\x00\x10'
    elif element_id == cgm_const.REAL_PRECISION:
        header = '\x10\xa6'
        params = '\x00\x00\x00\x09\x00\x17'
    elif element_id == cgm_const.INDEX_PRECISION:
        header = '\x10\xc2'
        params = '\x00\x08'
    elif element_id == cgm_const.COLOUR_PRECISION:
        header = '\x10\xe2'
        params = '\x00\x08'
    elif element_id == cgm_const.COLOUR_INDEX_PRECISION:
        header = '\x11\x02'
        params = '\x00\x08'
    # Page elements
    elif element_id == cgm_const.BEGIN_PICTURE:
        page_number = kwargs.get('page_number', 1)
        txt = 'Page %d' % page_number
        params = utils.py_int2byte(len(txt)) + txt
        header = '\x00' + utils.py_int2byte(len(params) + 0x60)
    elif element_id == cgm_const.BEGIN_PICTURE_BODY:
        header = '\x00\x80'
    elif element_id == cgm_const.END_PICTURE:
        header = '\x00\xa0'
    elif element_id == cgm_const.SCALING_MODE:
        header = '\x20\x26'
        params = '\x00\x01' + '\x3c\xd0\x13\xa9'
    elif element_id == cgm_const.COLOUR_SELECTION_MODE:
        header = '\x20\x42'
        params = '\x00\x01'
    elif element_id == cgm_const.LINE_WIDTH_SPECIFICATION_MODE:
        header = '\x20\x62'
        params = '\x00\x01'
    elif element_id == cgm_const.EDGE_WIDTH_SPECIFICATION_MODE:
        header = '\x20\xa2'
        params = '\x00\x01'
    elif element_id == cgm_const.VDC_EXTENT:
        bbox = kwargs.get('bbox', (0.0, 0.0, 1.0, 1.0))
        header = '\x20\xc8'
        params = ''.join([cgm_unit(val) for val in bbox])
    # Polyline
    elif element_id == cgm_const.LINE_WIDTH:
        header = '\x50\x64'
        val = kwargs.get('width', 2.5)
        params = utils.py_float2float(val, True)
    elif element_id == cgm_const.LINE_TYPE:
        header = '\x50\x42'
        dashes = tuple(kwargs.get('dashes', []))
        index = 0
        if dashes:
            index = cgm_const.LINE_DASHTABLE.index(dashes) + 1 \
                if dashes in cgm_const.LINE_DASHTABLE else 2
        params = utils.py_int2word(index, True)
    elif element_id == cgm_const.LINE_COLOUR:
        header = '\x50\x83'
        color = kwargs.get('color', (0, 0, 0))
        params = ''.join([utils.py_int2byte(item) for item in color])
    elif element_id == cgm_const.POLYLINE:
        points = kwargs.get('points', [(0, 0), (1, 1)])
        params = ''.join([cgm_unit(x) + cgm_unit(y) for x, y in points])
        header = '\x40\x3f' + utils.py_int2word(len(params), True)
    # Polygon
    elif element_id == cgm_const.INTERIOR_STYLE:
        empty = kwargs.get('empty', False)
        header = '\x52\xc2'
        params = '\x00\x00' if empty else '\x00\x01'
    elif element_id == cgm_const.FILL_COLOUR:
        header = '\x52\xe3'
        color = kwargs.get('color', (0, 0, 0))
        params = ''.join([utils.py_int2byte(item) for item in color])
    elif element_id == cgm_const.EDGE_VISIBILITY:
        header = '\x53\xc2'
        visible = kwargs.get('visible', True)
        params = '\x00\x01' if visible else '\x00\x00'
    elif element_id == cgm_const.EDGE_COLOUR:
        header = '\x52\xa3'
        color = kwargs.get('color', (0, 0, 0))
        params = ''.join([utils.py_int2byte(item) for item in color])
    elif element_id == cgm_const.EDGE_WIDTH:
        header = '\x53\x84'
        val = kwargs.get('width', 2.5)
        params = utils.py_float2float(val, True)
    elif element_id == cgm_const.EDGE_TYPE:
        header = '\x53\x61'
        dashes = tuple(kwargs.get('dashes', []))
        index = 0
        if dashes:
            index = cgm_const.LINE_DASHTABLE.index(dashes) + 1 \
                if dashes in cgm_const.LINE_DASHTABLE else 2
        params = utils.py_int2word(index, True)
    elif element_id == cgm_const.POLYGON:
        points = kwargs.get('points')
        if points:
            params = ''.join([cgm_unit(x) + cgm_unit(y) for x, y in points])
            header = '\x40\xff' + utils.py_int2word(len(params), True)
    elif element_id == cgm_const.POLYGON_SET:
        polygons = kwargs.get('polygons')
        params = ''
        for points in polygons:
            if points:
                end = '\x00\x03'
                if not points[0] == points[-1]:
                    points += [points[0]]
                    end = '\x00\x02'
                params += '\x00\x01'.join(
                    [cgm_unit(x) + cgm_unit(y) for x, y in points]) + end
        header = '\x41\x1f' + utils.py_int2word(len(params), True)

    if header:
        return elf(header, params)


class SK2_to_CGM_Translator(object):
    cgm_doc = None
    cgm_model = None
    sk2_doc = None
    sk2_mtds = None

    def translate(self, sk2_doc, cgm_doc):
        self.cgm_doc = cgm_doc
        self.cgm_model = cgm_doc.model
        self.sk2_doc = sk2_doc
        self.sk2_mtds = sk2_doc.methods

        self.add(cgm_const.BEGIN_METAFILE)
        self.add(cgm_const.METAFILE_VERSION)
        d = self.sk2_doc.appdata
        txt = 'Created by %s %s%s' % (d.app_name, d.version, d.revision)
        self.add(cgm_const.METAFILE_DESCRIPTION, description=txt)
        self.add(cgm_const.METAFILE_ELEMENT_LIST)
        self.add(cgm_const.VDC_TYPE)
        self.add(cgm_const.INTEGER_PRECISION)
        self.add(cgm_const.REAL_PRECISION)
        self.add(cgm_const.INDEX_PRECISION)
        self.add(cgm_const.COLOUR_PRECISION)
        self.add(cgm_const.COLOUR_INDEX_PRECISION)

        index = 1
        for page in self.sk2_mtds.get_pages():
            self.process_page(page, index)
            index += 1

        self.add(cgm_const.END_METAFILE)

        self.cgm_doc = None
        self.cgm_model = None
        self.sk2_doc = None
        self.sk2_mtds = None

    def add(self, element_id, **kwargs):
        self.cgm_model.add(builder(element_id, **kwargs))

    def process_page(self, page, index=1):
        self.add(cgm_const.BEGIN_PICTURE, page_number=index)

        self.add(cgm_const.SCALING_MODE)
        self.add(cgm_const.COLOUR_SELECTION_MODE)
        self.add(cgm_const.LINE_WIDTH_SPECIFICATION_MODE)
        self.add(cgm_const.EDGE_WIDTH_SPECIFICATION_MODE)

        w, h = self.sk2_mtds.get_page_size(page)
        bbox = (-w / 2.0, -h / 2.0, w / 2.0, h / 2.0)
        self.add(cgm_const.VDC_EXTENT, bbox=bbox)

        self.add(cgm_const.BEGIN_PICTURE_BODY)

        layers = self.sk2_mtds.get_visible_layers(page)
        for layer in layers:
            for obj in layer.childs:
                self.process_obj(obj)

        self.add(cgm_const.END_PICTURE)

    def process_obj(self, obj):
        if obj.is_primitive:
            curve = obj.to_curve()
            if not curve:
                return
            if not curve.is_primitive:
                self.process_obj(curve)
                return
            if curve.style[0]:
                self.make_polygons(curve)
            elif curve.style[1]:
                self.make_polylines(curve)
        else:
            for item in obj.childs:
                self.process_obj(item)

    def make_polylines(self, obj, paths=None):
        stroke = obj.style[1]
        self.add(cgm_const.LINE_WIDTH, width=stroke[1])
        color = self.sk2_doc.cms.get_display_color255(stroke[2])[:3]
        self.add(cgm_const.LINE_COLOUR, color=color)
        if not paths:
            paths = libgeom.get_flattened_paths(obj)
        for path in paths:
            points = [path[0], ] + path[1]
            self.add(cgm_const.POLYLINE, points=points)

    def make_polygons(self, obj):
        fill = obj.style[0]
        stroke = obj.style[1]
        paths = libgeom.get_flattened_paths(obj)
        if not paths:
            return
        if stroke and stroke[7]:
            self.make_polylines(obj, paths)
        if fill:
            self.add(cgm_const.INTERIOR_STYLE)
            color = sk2const.RGB_BLACK
            if fill[1] == sk2const.FILL_SOLID:
                color = fill[2]
            elif fill[1] == sk2const.FILL_GRADIENT:
                color = fill[2][2][0][1]
            elif fill[1] == sk2const.FILL_PATTERN:
                color = fill[2][2][0]
            color = self.sk2_doc.cms.get_display_color255(color)[:3]
            self.add(cgm_const.FILL_COLOUR, color=color)
            polygons = [[path[0], ] + path[1] for path in paths]
            if len(polygons) == 1:
                self.add(cgm_const.POLYGON, points=polygons[0])
            else:
                self.add(cgm_const.POLYGON_SET, polygons=polygons)
        if stroke and not stroke[7]:
            self.make_polylines(obj, paths)
