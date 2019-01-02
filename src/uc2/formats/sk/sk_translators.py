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

import math
from copy import deepcopy

from uc2 import uc2const, libgeom, sk2const
from uc2.formats.sk import sk_const, sk_model
from uc2.formats.sk2 import sk2_model

# --- SK to SK2 translation

SK2_ARC_TYPES = {
    sk_const.ArcArc: sk2const.ARC_ARC,
    sk_const.ArcChord: sk2const.ARC_CHORD,
    sk_const.ArcPieSlice: sk2const.ARC_PIE_SLICE,
}

SK2_LINE_JOIN = {
    sk_const.JoinMiter: sk2const.JOIN_MITER,
    sk_const.JoinRound: sk2const.JOIN_ROUND,
    sk_const.JoinBevel: sk2const.JOIN_BEVEL,
}

SK2_LINE_CAP = {
    sk_const.CapButt: sk2const.CAP_BUTT,
    sk_const.CapRound: sk2const.CAP_ROUND,
    sk_const.CapProjecting: sk2const.CAP_SQUARE,
}

SK2_TEXT_ALIGN = {
    sk_const.ALIGN_LEFT: sk2const.TEXT_ALIGN_LEFT,
    sk_const.ALIGN_RIGHT: sk2const.TEXT_ALIGN_RIGHT,
    sk_const.ALIGN_CENTER: sk2const.TEXT_ALIGN_CENTER,
}


def get_sk2_color(clr):
    if not clr: return deepcopy(sk_const.fallback_color)
    result = [uc2const.COLOR_RGB, [clr[0], clr[1], clr[2]], 1.0, '', '']
    return result


def get_sk2_page(fmt, size, ornt):
    if fmt in uc2const.PAGE_FORMAT_NAMES:
        size = () + uc2const.PAGE_FORMATS[fmt]
    else:
        fmt = 'Custom'
        size = () + size
    size = (min(*size), max(*size))
    if ornt == uc2const.LANDSCAPE:
        size = (max(*size), min(*size))
    return [fmt, size, ornt]


def get_sk2_layer_props(sk1_layer):
    return [sk1_layer.visible, abs(sk1_layer.locked - 1),
            sk1_layer.printable, 1]


def get_sk2_stops(sk_stops):
    stops = []
    for item in sk_stops:
        pos, clr = item
        stops = [[1.0 - pos, get_sk2_color(clr)], ] + stops
    return stops


def set_sk2_style(sk1_style, dest_obj=None):
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

    if fill_pattern.is_Solid:
        sk2_fill = []
        if fill_pattern.is_Solid:
            sk2_fill = [sk2const.FILL_EVENODD, sk2const.FILL_SOLID,
                        get_sk2_color(fill_pattern.color)]
        sk2_style[0] = sk2_fill

    elif fill_pattern.is_AxialGradient:
        stops = get_sk2_stops(fill_pattern.gradient.colors)
        point = [fill_pattern.direction.x, fill_pattern.direction.y]
        angle = libgeom.get_point_angle(point, [0.0, 0.0])
        points = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]

        m21 = math.sin(-angle)
        m11 = m22 = math.cos(-angle)
        m12 = -m21
        dx = 0.5 - m11 * 0.5 + m21 * 0.5;
        dy = 0.5 - m21 * 0.5 - m11 * 0.5;
        trafo = [m11, m21, m12, m22, dx, dy]
        points = libgeom.apply_trafo_to_points(points, trafo)
        bbox = libgeom.bbox_for_points(points)
        w, h = libgeom.bbox_size(bbox)
        vector = [[bbox[0], 0.5], [bbox[2], 0.5]]
        invtrafo = libgeom.invert_trafo(trafo)
        vector = libgeom.apply_trafo_to_points(vector, invtrafo)

        dest_obj.update()
        bbox = dest_obj.cache_bbox
        w, h = libgeom.bbox_size(bbox)
        trafo = [w, 0.0, 0.0, h, bbox[0], bbox[1]]
        vector = libgeom.apply_trafo_to_points(vector, trafo)

        sk2_fill = [sk2const.FILL_EVENODD, sk2const.FILL_GRADIENT,
                    [sk2const.GRADIENT_LINEAR, vector, stops]]
        sk2_style[0] = sk2_fill
        dest_obj.fill_trafo = [] + sk2const.NORMAL_TRAFO

    elif fill_pattern.is_RadialGradient or fill_pattern.is_ConicalGradient:
        stops = get_sk2_stops(fill_pattern.gradient.colors)
        dest_obj.update()
        bbox = dest_obj.cache_bbox
        cg = [fill_pattern.center.x, fill_pattern.center.y]
        w, h = libgeom.bbox_size(bbox)
        start_point = [bbox[0] + w * cg[0], bbox[1] + h * cg[1]]
        points = libgeom.bbox_points(bbox)
        r = 0
        for point in points:
            dist = libgeom.distance(point, start_point)
            r = max(r, dist)
        end_point = [start_point[0] + r, start_point[1]]
        sk2_fill = [sk2const.FILL_EVENODD, sk2const.FILL_GRADIENT,
                    [sk2const.GRADIENT_RADIAL, [start_point, end_point],
                     stops]]
        sk2_style[0] = sk2_fill
        dest_obj.fill_trafo = [] + sk2const.NORMAL_TRAFO

    dest_obj.style = sk2_style


def set_sk2_txt_style(source_text, dest_obj):
    sk1_style = source_text.properties
    font = sk1_style.font.decode('latin1').encode('utf8')
    sk2_style = [[], [], [], []]
    text_style = [font, 'Regular', sk1_style.font_size,
                  SK2_TEXT_ALIGN[source_text.horiz_align], [], True]
    sk2_style[2] = text_style
    dest_obj.style = sk2_style
    set_sk2_style(sk1_style, dest_obj)
    dest_obj.style[2] = text_style


class SK_to_SK2_Translator(object):
    dx = dy = 0.0

    def translate(self, sk_doc, sk2_doc):
        sk_mdl = sk_doc.model
        self.sk2mtds = sk2mtds = sk2_doc.methods
        self.sk2_doc = sk2_doc
        for item in sk_mdl.childs:
            if item.cid == sk_model.LAYOUT:
                pages_obj = sk2mtds.get_pages_obj()
                fmt = get_sk2_page(item.format, item.size, item.orientation)
                pages_obj.page_format = fmt
                self.dx = -fmt[1][0] / 2.0
                self.dy = -fmt[1][1] / 2.0
                pages_obj.childs = []
                name = 'Page 1'
                self.page = sk2_model.Page(pages_obj.config, pages_obj, name)
                self.page.page_format = deepcopy(fmt)
                pages_obj.childs.append(self.page)
            elif item.cid == sk_model.GUIDELAYER:
                gl = sk2mtds.get_guide_layer()
                sk2mtds.set_guide_color(get_sk2_color(item.layer_color))
                props = get_sk2_layer_props(item)
                if props[3]: props[3] = 0
                gl.properties = props
                parse_objs = False
                for chld in item.childs:
                    if chld.cid == sk_model.GUIDE:
                        orientation = abs(chld.orientation - 1)
                        position = chld.position + self.dy
                        if orientation: position = chld.position + self.dx
                        guide = sk2_model.Guide(gl.config, gl,
                                                position, orientation)
                        gl.childs.append(guide)
                    else:
                        parse_objs = True
                if parse_objs:
                    layer = self.translate_layer(self.page, item)
                    self.page.childs.append(layer)
            elif item.cid == sk_model.GRID:
                grid = sk2mtds.get_grid_layer()
                grid.geometry = list(item.geometry)
                color = get_sk2_color(item.grid_color)
                color[2] = .15
                sk2mtds.set_grid_color(color)
                props = get_sk2_layer_props(item)
                if props[3]: props[3] = 0
                grid.properties = props
                if item.childs:
                    layer = self.translate_layer(self.page, item)
                    self.page.childs.append(layer)
            elif item.cid == sk_model.LAYER:
                self.page.childs.append(self.translate_layer(self.page, item))

        self.page.layer_counter = len(self.page.childs)
        self.page = None
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
                if source_obj.cid == sk_model.GROUP:
                    dest_obj = self.translate_group(dest_parent, source_obj)
                elif source_obj.cid == sk_model.MASKGROUP:
                    dest_obj = self.translate_mgroup(dest_parent, source_obj)
                elif source_obj.cid == sk_model.RECTANGLE:
                    dest_obj = self.translate_rect(dest_parent, source_obj)
                elif source_obj.cid == sk_model.ELLIPSE:
                    dest_obj = self.translate_ellipse(dest_parent, source_obj)
                elif source_obj.cid == sk_model.CURVE:
                    dest_obj = self.translate_curve(dest_parent, source_obj)
                elif source_obj.cid == sk_model.TEXT:
                    dest_obj = self.translate_text(dest_parent, source_obj)
                elif source_obj.cid == sk_model.IMAGE:
                    dest_obj = self.translate_image(dest_parent, source_obj)
                if dest_obj: dest_objs.append(dest_obj)
        return dest_objs

    def translate_layer(self, dest_parent, source_layer):
        name = source_layer.name.decode('latin1').encode('utf8')
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
        set_sk2_style(source_rect.properties, dest_rect)
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
        set_sk2_style(source_ellipse.properties, dest_ellipse)
        return dest_ellipse

    def translate_curve(self, dest_parent, source_curve):
        paths = deepcopy(source_curve.paths_list)
        trafo = [1.0, 0.0, 0.0, 1.0, self.dx, self.dy]
        dest_curve = sk2_model.Curve(dest_parent.config, dest_parent,
                                     paths, trafo)
        set_sk2_style(source_curve.properties, dest_curve)
        return dest_curve

    def translate_text(self, dest_parent, source_text):
        text = source_text.text.decode('latin1').encode('utf8')
        trafo = list(source_text.trafo)
        if len(source_text.trafo) == 2:
            trafo = [1.0, 0.0, 0.0, 1.0] + trafo
        trafo[4] += self.dx
        trafo[5] += self.dy
        size = source_text.properties.font_size * 1.16
        dest_text = sk2_model.Text(dest_parent.config, dest_parent,
                                   [0.0, -size], text, trafo=trafo)
        set_sk2_txt_style(source_text, dest_text)
        return dest_text

    def translate_image(self, dest_parent, source_image):
        trafo = self.get_sk2_trafo(source_image)
        dest_image = sk2_model.Pixmap(dest_parent.config)
        image = source_image.image.copy()
        dest_image.handler.load_from_images(image)
        dest_image.trafo = trafo
        return dest_image


# --- SK2 to SK translation

SK_ARC_TYPES = {
    sk2const.ARC_ARC: sk_const.ArcArc,
    sk2const.ARC_CHORD: sk_const.ArcChord,
    sk2const.ARC_PIE_SLICE: sk_const.ArcPieSlice,
}

SK_LINE_JOIN = {
    sk2const.JOIN_MITER: sk_const.JoinMiter,
    sk2const.JOIN_ROUND: sk_const.JoinRound,
    sk2const.JOIN_BEVEL: sk_const.JoinBevel,
}

SK_LINE_CAP = {
    sk2const.CAP_BUTT: sk_const.CapButt,
    sk2const.CAP_ROUND: sk_const.CapRound,
    sk2const.CAP_SQUARE: sk_const.CapProjecting,
}

SK_TEXT_ALIGN = {
    sk2const.TEXT_ALIGN_LEFT: sk_const.ALIGN_LEFT,
    sk2const.TEXT_ALIGN_RIGHT: sk_const.ALIGN_RIGHT,
    sk2const.TEXT_ALIGN_CENTER: sk_const.ALIGN_CENTER,
    sk2const.TEXT_ALIGN_JUSTIFY: sk_const.ALIGN_LEFT,
}


def get_sk_color(clr, cms):
    if not clr: return deepcopy(sk_const.fallback_color)
    clr = cms.get_rgb_color(clr)
    val = clr[1]
    return (val[0], val[1], val[2])


def get_sk_style(source_obj, cms):
    sk1_style = sk_model.Style()
    fill = source_obj.style[0]
    stroke = source_obj.style[1]
    if fill and fill[1] == sk2const.FILL_SOLID:
        sk1_style.fill_pattern = sk_model.SolidPattern(
            get_sk_color(fill[2], cms))
    if stroke:
        sk1_style.line_pattern = sk_model.SolidPattern(
            get_sk_color(stroke[2], cms))
        sk1_style.line_width = stroke[1]
        sk1_style.line_join = SK_LINE_JOIN[stroke[5]]
        sk1_style.line_cap = SK_LINE_CAP[stroke[4]]
        sk1_style.line_dashes = tuple(stroke[3])
    else:
        sk1_style.line_pattern = sk_model.EmptyPattern
    return sk1_style


class SK2_to_SK_Translator(object):
    dx = dy = 0.0

    def translate(self, sk2_doc, sk_doc):
        sk2model = sk2_doc.model
        self.model = sk_doc.model
        self.skmtds = skmtds = sk_doc.methods
        self.sk_doc = sk_doc
        self.sk2_doc = sk2_doc
        for item in sk2model.childs:
            if item.cid == sk2_model.PAGES:
                layout = skmtds.get_layout_obj()
                fmt, size, ornt = item.childs[0].page_format
                layout.format = fmt
                layout.size = () + tuple(size)
                layout.orientation = ornt
                self.dx = size[0] / 2.0
                self.dy = size[1] / 2.0
                self.page_dx = 0.0
                childs = []
                for page in item.childs:
                    fmt, size, ornt = page.page_format
                    self.page_size = () + tuple(size)
                    childs += self.translate_page(self.model, page)
                    self.dx += self.page_size[0] + 30.0
                    self.page_dx += self.page_size[0] + 30.0
                self.model.childs = [self.model.childs[
                                         0], ] + childs + self.model.childs[-2:]
            elif item.cid == sk2_model.GRID_LAYER:
                grid = skmtds.get_grid_layer()
                grid.geometry = tuple(item.grid)
                grid.grid_color = get_sk_color(item.style[1][2],
                                               self.sk2_doc.cms)
                grid.visible = item.properties[0]
            elif item.cid == sk2_model.GUIDE_LAYER:
                gl = skmtds.get_guide_layer()
                gl.layer_color = get_sk_color(item.style[1][2],
                                              self.sk2_doc.cms)
                gl.visible = item.properties[0]
                gl.childs = []
                for chld in item.childs:
                    if chld.cid == sk2_model.GUIDE:
                        position = chld.position + self.dx
                        orientation = abs(chld.orientation - 1)
                        if orientation: position = chld.position + self.dy
                        guide = sk_model.SKGuide(position, orientation)
                        gl.childs.append(guide)

        self.model = None
        self.sk2_doc = None
        self.sk_doc = None
        self.skmtds = None

    def translate_objs(self, dest_parent, source_objs):
        dest_objs = []
        if source_objs:
            for source_obj in source_objs:
                dest_obj = None
                if source_obj.cid == sk2_model.LAYER:
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
                if dest_obj: dest_objs.append(dest_obj)
        return dest_objs

    def translate_page(self, dest_parent, source_obj):
        layers = self.translate_objs(self.model, source_obj.childs)
        if layers:
            m11, m22 = self.page_size
            trafo = sk_model.Trafo(m11, 0.0, 0.0, m22, self.page_dx, 0.0)
            style = sk_model.Style()
            rect = sk_model.SKRectangle(trafo=trafo, properties=style)
            layers[0].childs = [rect, ] + layers[0].childs
        return layers

    def translate_layer(self, dest_parent, source_obj):
        name = source_obj.name
        visible, editable, printable = source_obj.properties[:-1]
        locked = abs(editable - 1)
        color = get_sk_color(source_obj.style[1][2], self.sk2_doc.cms)
        dest_layer = sk_model.SKLayer(name, visible, printable, locked,
                                      outline_color=color)
        dest_layer.childs = self.translate_objs(dest_layer, source_obj.childs)
        return dest_layer

    def translate_group(self, dest_parent, source_obj):
        dest_group = sk_model.SKGroup()
        dest_group.childs = self.translate_objs(dest_group, source_obj.childs)
        return dest_group

    def translate_container(self, dest_parent, source_obj):
        dest_mgroup = sk_model.SKMaskGroup()
        dest_mgroup.childs = self.translate_objs(dest_mgroup, source_obj.childs)
        return dest_mgroup

    def translate_curve(self, dest_parent, source_obj):
        paths = source_obj.paths
        trafo = [] + source_obj.trafo
        trafo[4] += self.dx
        trafo[5] += self.dy
        paths = libgeom.apply_trafo_to_paths(paths, trafo)
        style = get_sk_style(source_obj, self.sk2_doc.cms)
        dest_curve = sk_model.SKPolyBezier(paths_list=paths, properties=style)
        return dest_curve

    def translate_image(self, dest_parent, source_obj):
        image = source_obj.handler.get_display_image(self.sk2_doc.cms)
        m11, m12, m21, m22, v1, v2 = source_obj.trafo
        v1 += self.dx
        v2 += self.dy
        trafo = sk_model.Trafo(m11, m12, m21, m22, v1, v2)
        dest_image = sk_model.SKImage(trafo, id(image), image)
        return dest_image
