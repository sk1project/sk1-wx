# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013-2016 by Igor E. Novikov
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

from PIL import Image
from cStringIO import StringIO
from copy import deepcopy

import model
from uc2 import uc2const, libgeom, libimg, sk2const
from uc2.formats.sk1 import sk1_const
from uc2.formats.sk2 import sk2_model

# --- SK1 to SK2 translation

SK2_ARC_TYPES = {
    sk1_const.ArcArc: sk2const.ARC_ARC,
    sk1_const.ArcChord: sk2const.ARC_CHORD,
    sk1_const.ArcPieSlice: sk2const.ARC_PIE_SLICE,
}

SK2_LINE_JOIN = {
    sk1_const.JoinMiter: sk2const.JOIN_MITER,
    sk1_const.JoinRound: sk2const.JOIN_ROUND,
    sk1_const.JoinBevel: sk2const.JOIN_BEVEL,
}

SK2_LINE_CAP = {
    sk1_const.CapButt: sk2const.CAP_BUTT,
    sk1_const.CapRound: sk2const.CAP_ROUND,
    sk1_const.CapProjecting: sk2const.CAP_SQUARE,
}

SK2_TEXT_ALIGN = {
    sk1_const.ALIGN_LEFT: sk2const.TEXT_ALIGN_LEFT,
    sk1_const.ALIGN_RIGHT: sk2const.TEXT_ALIGN_RIGHT,
    sk1_const.ALIGN_CENTER: sk2const.TEXT_ALIGN_CENTER,
}


def get_sk2_color(clr):
    if not clr:
        return deepcopy(sk1_const.fallback_color)
    color_spec = clr[0]
    if color_spec == sk1_const.RGB:
        result = [uc2const.COLOR_RGB, [clr[1], clr[2], clr[3]], 1.0, '', '']
        if len(clr) == 5:
            result[2] = clr[4]
        return result
    elif color_spec == sk1_const.CMYK:
        result = [uc2const.COLOR_CMYK,
                  [clr[1], clr[2], clr[3], clr[4]], 1.0, '', '']
        if len(clr) == 6:
            result[2] = clr[5]
        return result
    elif color_spec == sk1_const.SPOT:
        result = [uc2const.COLOR_SPOT, [[clr[3], clr[4], clr[5]],
                                        [clr[6], clr[7], clr[8], clr[9]]], 1.0,
                  clr[2], clr[1]]
        if len(clr) == 11:
            result[2] = clr[10]
        return result
    else:
        return deepcopy(sk1_const.fallback_color)


def get_sk2_page(fmt, size, ornt):
    if fmt in uc2const.PAGE_FORMAT_NAMES:
        return [fmt, () + uc2const.PAGE_FORMATS[fmt], ornt]
    return ['Custom', () + size, ornt]


def get_sk2_layer_props(sk1_layer):
    return [sk1_layer.visible, abs(sk1_layer.locked - 1),
            sk1_layer.printable, 1]


def get_sk2_style(sk1_style):
    sk2_style = [[], [], [], []]
    line_pattern = sk1_style.line_pattern
    fill_pattern = sk1_style.fill_pattern
    if not line_pattern.is_Empty:
        sk2_line = [sk2const.STROKE_MIDDLE,
                    sk1_style.line_width,
                    get_sk2_color(line_pattern.color),
                    list(sk1_style.line_dashes),
                    SK2_LINE_CAP[sk1_style.line_cap],
                    SK2_LINE_JOIN[sk1_style.line_join],
                    10.0, 0, 0, []
                    ]
        sk2_style[1] = sk2_line
    if not fill_pattern.is_Empty:
        sk2_fill = []
        if fill_pattern.is_Solid:
            sk2_fill = [sk2const.FILL_EVENODD, sk2const.FILL_SOLID,
                        get_sk2_color(fill_pattern.color)]
        sk2_style[0] = sk2_fill
    return sk2_style


def get_sk2_txt_style(source_text):
    sk1_style = source_text.properties
    sk2_style = get_sk2_style(sk1_style)
    sk2_style[2] = [sk1_style.font, sk1_style.font_face,
                    sk1_style.font_size,
                    SK2_TEXT_ALIGN[source_text.horiz_align], [], True]
    return sk2_style


class SK1_to_SK2_Translator(object):
    dx = dy = 0.0
    sk2mtds = None
    sk2_doc = None

    def translate(self, sk1_doc, sk2_doc):
        sk1_model = sk1_doc.model
        self.sk2mtds = sk2mtds = sk2_doc.methods
        self.sk2_doc = sk2_doc
        dx = dy = 0.0
        for item in sk1_model.childs:
            if item.cid == model.LAYOUT:
                pages_obj = sk2mtds.get_pages_obj()
                fmt = get_sk2_page(item.format, item.size, item.orientation)
                pages_obj.page_format = fmt
                dx = item.size[0] / 2.0
                dy = item.size[1] / 2.0
            elif item.cid == model.GUIDELAYER:
                gl = sk2mtds.get_guide_layer()
                sk2mtds.set_guide_color(get_sk2_color(item.layer_color))
                props = get_sk2_layer_props(item)
                if props[3]:
                    props[3] = 0
                gl.properties = props
                for chld in item.childs:
                    if chld.cid == model.GUIDE:
                        orientation = abs(chld.orientation - 1)
                        position = chld.position - dy
                        if orientation:
                            position = chld.position - dx
                        guide = sk2_model.Guide(gl.config, gl,
                                                position, orientation)
                        gl.childs.append(guide)
            elif item.cid == model.GRID:
                grid = sk2mtds.get_grid_layer()
                grid.geometry = list(item.geometry)
                sk2mtds.set_grid_color(get_sk2_color(item.grid_color))
                props = get_sk2_layer_props(item)
                if props[3]:
                    props[3] = 0
                grid.properties = props
            elif item.cid == model.PAGES:
                pages_obj = sk2mtds.get_pages_obj()
                pages_obj.childs = self.translate_objs(pages_obj, item.childs)
                pages_obj.page_counter = len(pages_obj.childs)

        sk2_doc.model.do_update()

    def get_sk2_trafo(self, obj):
        trafo = list(obj.trafo.coeff())
        trafo[4] += self.dx
        trafo[5] += self.dy
        return trafo

    def translate_objs(self, dest_parent, source_objs):
        dest_objs = []
        if source_objs:
            for source_obj in source_objs:
                dest_obj = None
                if source_obj.cid == model.PAGE:
                    dest_obj = self.translate_page(dest_parent, source_obj)
                elif source_obj.cid == model.LAYER:
                    dest_obj = self.translate_layer(dest_parent, source_obj)
                elif source_obj.cid == model.GROUP:
                    dest_obj = self.translate_group(dest_parent, source_obj)
                elif source_obj.cid == model.MASKGROUP:
                    dest_obj = self.translate_mgroup(dest_parent, source_obj)
                elif source_obj.cid == model.RECTANGLE:
                    dest_obj = self.translate_rect(dest_parent, source_obj)
                elif source_obj.cid == model.ELLIPSE:
                    dest_obj = self.translate_ellipse(dest_parent, source_obj)
                elif source_obj.cid == model.CURVE:
                    dest_obj = self.translate_curve(dest_parent, source_obj)
                elif source_obj.cid == model.TEXT:
                    dest_obj = self.translate_text(dest_parent, source_obj)
                elif source_obj.cid == model.IMAGE:
                    dest_obj = self.translate_image(dest_parent, source_obj)
                if dest_obj:
                    dest_objs.append(dest_obj)
        return dest_objs

    def translate_page(self, dest_parent, source_page):
        name = source_page.name
        fmt = get_sk2_page(source_page.format, source_page.size,
                           source_page.orientation)
        self.dx = -source_page.size[0] / 2.0
        self.dy = -source_page.size[1] / 2.0
        dest_page = sk2_model.Page(dest_parent.config, dest_parent, name)
        dest_page.page_format = fmt
        dest_page.childs = self.translate_objs(dest_page, source_page.childs)
        dest_page.layer_counter = len(dest_page.childs)
        return dest_page

    def translate_layer(self, dest_parent, source_layer):
        name = source_layer.name
        props = get_sk2_layer_props(source_layer)
        dest_layer = sk2_model.Layer(dest_parent.config, dest_parent, name)
        color = get_sk2_color(source_layer.layer_color)
        self.sk2mtds.set_layer_color(dest_layer, color)
        dest_layer.properties = props
        dest_layer.childs = self.translate_objs(dest_layer, source_layer.childs)
        return dest_layer

    def translate_group(self, dest_parent, source_group):
        dest_group = sk2_model.Group(dest_parent.config, dest_parent)
        dest_group.childs = self.translate_objs(dest_group, source_group.childs)
        return dest_group

    def translate_mgroup(self, dest_parent, source_mgroup):
        dest_mgroup = sk2_model.Container(dest_parent.config, dest_parent)
        dest_mgroup.childs = self.translate_objs(dest_mgroup,
                                                 source_mgroup.childs)
        return dest_mgroup

    def translate_rect(self, dest_parent, source_rect):
        trafo = self.get_sk2_trafo(source_rect)
        corners = [0.0, 0.0, 0.0, 0.0]
        rect = [0.0, 0.0, 1.0, 1.0]
        if source_rect.radius1 and source_rect.radius2:
            radius = min(source_rect.radius1, source_rect.radius2)
            corners = [radius * 2.0] * 4
            if source_rect.radius1 > source_rect.radius2:
                coef = source_rect.radius1 / source_rect.radius2
                rect = [0.0, 0.0, 1.0, coef]
                tr = [1.0, 0.0, 0.0, 1.0 / coef, 0.0, 0.0]
            else:
                coef = source_rect.radius2 / source_rect.radius1
                rect = [0.0, 0.0, coef, 1.0]
                tr = [1.0 / coef, 0.0, 0.0, 1.0, 0.0, 0.0]
            trafo = libgeom.multiply_trafo(tr, trafo)
        dest_rect = sk2_model.Rectangle(dest_parent.config, dest_parent,
                                        rect, trafo, corners=corners)
        dest_rect.style = get_sk2_style(source_rect.properties)
        return dest_rect

    def translate_ellipse(self, dest_parent, source_ellipse):
        trafo = self.get_sk2_trafo(source_ellipse)
        angle1 = source_ellipse.start_angle
        angle2 = source_ellipse.end_angle
        arc_type = SK2_ARC_TYPES[source_ellipse.arc_type]
        rect = [-1.0, -1.0, 2.0, 2.0]
        dest_ellipse = sk2_model.Circle(dest_parent.config, dest_parent,
                                        rect, angle1, angle2, arc_type)
        dest_ellipse.trafo = libgeom.multiply_trafo(dest_ellipse.trafo, trafo)
        dest_ellipse.initial_trafo = [] + dest_ellipse.trafo
        dest_ellipse.style = get_sk2_style(source_ellipse.properties)
        return dest_ellipse

    def translate_curve(self, dest_parent, source_curve):
        paths = deepcopy(source_curve.paths_list)
        trafo = [1.0, 0.0, 0.0, 1.0, self.dx, self.dy]
        dest_curve = sk2_model.Curve(dest_parent.config, dest_parent,
                                     paths, trafo)
        dest_curve.style = get_sk2_style(source_curve.properties)
        return dest_curve

    def translate_text(self, dest_parent, source_text):
        text = source_text.text.encode('utf-8')
        trafo = list(source_text.trafo)
        if len(source_text.trafo) == 2:
            trafo = [1.0, 0.0, 0.0, 1.0] + trafo
        trafo[4] += self.dx
        trafo[5] += self.dy
        size = source_text.properties.font_size * 1.16
        dest_text = sk2_model.Text(dest_parent.config, dest_parent,
                                   [0.0, -size], text, trafo=trafo)
        dest_text.style = get_sk2_txt_style(source_text)
        return dest_text

    def translate_image(self, dest_parent, source_image):
        trafo = self.get_sk2_trafo(source_image)
        dest_image = sk2_model.Pixmap(dest_parent.config)
        image = source_image.image.copy()
        dest_image.handler.load_from_images(image)
        dest_image.trafo = trafo
        return dest_image


# --- SK2 to SK1 translation

SK1_ARC_TYPES = {
    sk2const.ARC_ARC: sk1_const.ArcArc,
    sk2const.ARC_CHORD: sk1_const.ArcChord,
    sk2const.ARC_PIE_SLICE: sk1_const.ArcPieSlice,
}

SK1_LINE_JOIN = {
    sk2const.JOIN_MITER: sk1_const.JoinMiter,
    sk2const.JOIN_ROUND: sk1_const.JoinRound,
    sk2const.JOIN_BEVEL: sk1_const.JoinBevel,
}

SK1_LINE_CAP = {
    sk2const.CAP_BUTT: sk1_const.CapButt,
    sk2const.CAP_ROUND: sk1_const.CapRound,
    sk2const.CAP_SQUARE: sk1_const.CapProjecting,
}

SK1_TEXT_ALIGN = {
    sk2const.TEXT_ALIGN_LEFT: sk1_const.ALIGN_LEFT,
    sk2const.TEXT_ALIGN_RIGHT: sk1_const.ALIGN_RIGHT,
    sk2const.TEXT_ALIGN_CENTER: sk1_const.ALIGN_CENTER,
    sk2const.TEXT_ALIGN_JUSTIFY: sk1_const.ALIGN_LEFT,
}


def get_sk1_color(clr, cms):
    if not clr:
        return deepcopy(sk1_const.fallback_sk1color)
    color_spec = clr[0]
    val = clr[1]
    alpha = clr[2]
    if color_spec == uc2const.COLOR_RGB:
        if clr[2] == 1.0:
            result = (sk1_const.RGB, val[0], val[1], val[2])
        else:
            result = (sk1_const.RGB, val[0], val[1], val[2], alpha)
        return result
    elif color_spec == uc2const.COLOR_CMYK:
        if clr[2] == 1.0:
            result = (sk1_const.CMYK, val[0], val[1], val[2], val[3])
        else:
            result = (sk1_const.CMYK, val[0], val[1], val[2], val[3], alpha)
        return result
    elif color_spec == uc2const.COLOR_GRAY:
        if clr[2] == 1.0:
            result = (sk1_const.CMYK, 0.0, 0.0, 0.0, 1.0 - val[0])
        else:
            result = (sk1_const.CMYK, 0.0, 0.0, 0.0, 1.0 - val[0], alpha)
        return result
    elif color_spec == uc2const.COLOR_SPOT:
        clr = cms.get_rgb_color(clr)
        val = clr[1]
        alpha = clr[2]
        if clr[2] == 1.0:
            result = (sk1_const.RGB, val[0], val[1], val[2])
        else:
            result = (sk1_const.RGB, val[0], val[1], val[2], alpha)
        return result
    else:
        return deepcopy(sk1_const.fallback_sk1color)


def get_sk1_style(source_obj, cms):
    sk1_style = model.Style()
    fill = source_obj.style[0]
    stroke = source_obj.style[1]
    if fill and fill[1] == sk2const.FILL_SOLID:
        sk1_style.fill_pattern = model.SolidPattern(get_sk1_color(fill[2], cms))
    if stroke:
        sk1_style.line_pattern = model.SolidPattern(
            get_sk1_color(stroke[2], cms))
        sk1_style.line_width = stroke[1]
        sk1_style.line_join = SK1_LINE_JOIN[stroke[5]]
        sk1_style.line_cap = SK1_LINE_CAP[stroke[4]]
        sk1_style.line_dashes = tuple(stroke[3])
    else:
        sk1_style.line_pattern = model.EmptyPattern
    return sk1_style


class SK2_to_SK1_Translator(object):
    dx = dy = 0.0
    sk1mtds = None
    sk1_doc = None
    sk2_doc = None

    def translate(self, sk2_doc, sk1_doc):
        sk2model = sk2_doc.model
        self.sk1mtds = sk1mtds = sk1_doc.methods
        self.sk1_doc = sk1_doc
        self.sk2_doc = sk2_doc
        dx = dy = 0.0
        for item in sk2model.childs:
            if item.cid == sk2_model.PAGES:
                layout = sk1mtds.get_layout_obj()
                fmt, size, ornt = item.page_format
                layout.format = fmt
                layout.size = () + tuple(size)
                layout.orientation = ornt
                dx = size[0] / 2.0
                dy = size[1] / 2.0
                pages_obj = sk1mtds.get_pages_obj()
                pages_obj.childs = self.translate_objs(pages_obj, item.childs)
            elif item.cid == sk2_model.GRID_LAYER:
                grid = sk1mtds.get_grid_layer()
                grid.geometry = tuple(item.grid)
                grid.grid_color = get_sk1_color(item.style[1][2],
                                                self.sk2_doc.cms)
                grid.visible = item.properties[0]
            elif item.cid == sk2_model.GUIDE_LAYER:
                gl = sk1mtds.get_guide_layer()
                gl.layer_color = get_sk1_color(item.style[1][2],
                                               self.sk2_doc.cms)
                gl.visible = item.properties[0]
                gl.childs = []
                for chld in item.childs:
                    if chld.cid == sk2_model.GUIDE:
                        position = chld.position + dx
                        orientation = abs(chld.orientation - 1)
                        if orientation:
                            position = chld.position + dy
                        guide = model.SK1Guide(position, orientation)
                        gl.childs.append(guide)

    def translate_objs(self, dest_parent, source_objs):
        dest_objs = []
        if source_objs:
            for source_obj in source_objs:
                dest_obj = None
                if source_obj.cid == sk2_model.PAGE:
                    dest_obj = self.translate_page(dest_parent, source_obj)
                elif source_obj.cid == sk2_model.LAYER:
                    dest_obj = self.translate_layer(dest_parent, source_obj)
                elif source_obj.cid == sk2_model.GROUP:
                    dest_obj = self.translate_group(dest_parent, source_obj)
                elif source_obj.cid == sk2_model.CONTAINER:
                    dest_obj = self.translate_container(dest_parent, source_obj)
                elif source_obj.cid == sk2_model.CURVE:
                    dest_obj = self.translate_curve(dest_parent, source_obj)
                elif source_obj.cid in (sk2_model.RECTANGLE, sk2_model.CIRCLE,
                                        sk2_model.POLYGON):
                    source_obj = source_obj.to_curve()
                    dest_obj = self.translate_curve(dest_parent, source_obj)
                elif source_obj.is_text:
                    source_obj = source_obj.to_curve()
                    objs = self.translate_objs(dest_parent, [source_obj, ])
                    if objs:
                        for item in objs:
                            dest_objs.append(item)
                    continue
                elif source_obj.cid == sk2_model.PIXMAP:
                    dest_obj = self.translate_image(dest_parent, source_obj)
                if dest_obj:
                    dest_objs.append(dest_obj)
        return dest_objs

    def translate_page(self, dest_parent, source_obj):
        name = source_obj.name
        fmt, size, ornt = deepcopy(source_obj.page_format)
        self.dx = size[0] / 2.0
        self.dy = size[1] / 2.0
        dest_page = model.SK1Page(name, fmt, size, ornt)
        dest_page.childs = self.translate_objs(dest_page, source_obj.childs)
        return dest_page

    def translate_layer(self, dest_parent, source_obj):
        name = source_obj.name
        visible, editable, printable = source_obj.properties[:-1]
        locked = abs(editable - 1)
        color = get_sk1_color(source_obj.style[1][2], self.sk2_doc.cms)
        dest_layer = model.SK1Layer(name, visible, printable, locked,
                                    outline_color=color)
        dest_layer.childs = self.translate_objs(dest_layer, source_obj.childs)
        return dest_layer

    def translate_group(self, dest_parent, source_obj):
        dest_group = model.SK1Group()
        dest_group.childs = self.translate_objs(dest_group, source_obj.childs)
        return dest_group

    def translate_container(self, dest_parent, source_obj):
        dest_mgroup = model.SK1MaskGroup()
        dest_mgroup.childs = self.translate_objs(dest_mgroup, source_obj.childs)
        return dest_mgroup

    def translate_curve(self, dest_parent, source_obj):
        paths = source_obj.paths
        trafo = [] + source_obj.trafo
        trafo[4] += self.dx
        trafo[5] += self.dy
        paths = libgeom.apply_trafo_to_paths(paths, trafo)
        style = get_sk1_style(source_obj, self.sk2_doc.cms)
        dest_curve = model.PolyBezier(paths_list=paths, properties=style)
        return dest_curve

    def translate_image(self, dest_parent, source_obj):
        image = source_obj.handler.get_display_image(self.sk2_doc.cms)
        m11, m12, m21, m22, v1, v2 = source_obj.trafo
        v1 += self.dx
        v2 += self.dy
        trafo = model.Trafo(m11, m12, m21, m22, v1, v2)
        dest_image = model.SK1Image(trafo, id(image), image)
        return dest_image
