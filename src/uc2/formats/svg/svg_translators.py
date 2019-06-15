# -*- coding: utf-8 -*-
#
#  Copyright (C) 2016-2018 by Igor E. Novikov
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
import os
from base64 import b64decode, b64encode
from cStringIO import StringIO
from copy import deepcopy

from PIL import Image

from uc2 import uc2const, libgeom, libpango, cms, sk2const, utils
from uc2.utils import fsutils
from uc2.formats.sk2 import sk2_model
from uc2.formats.svg import svg_const, svg_utils
from uc2.formats.svg.svg_utils import get_svg_trafo, check_svg_attr, \
    parse_svg_points, parse_svg_coords, parse_svg_color, parse_svg_stops, \
    get_svg_level_trafo


LOG = logging.getLogger(__name__)

SK2_UNITS = {
    svg_const.SVG_PX: uc2const.UNIT_PX,
    svg_const.SVG_PC: uc2const.UNIT_PX,
    svg_const.SVG_PT: uc2const.UNIT_PT,
    svg_const.SVG_MM: uc2const.UNIT_MM,
    svg_const.SVG_CM: uc2const.UNIT_CM,
    svg_const.SVG_M: uc2const.UNIT_M,
    svg_const.SVG_IN: uc2const.UNIT_IN,
    svg_const.SVG_FT: uc2const.UNIT_FT,
}

FONT_COEFF = 0.938

SK2_FILL_RULE = {
    'nonzero': sk2const.FILL_NONZERO,
    'evenodd': sk2const.FILL_EVENODD,
}

SK2_LINE_JOIN = {
    'miter': sk2const.JOIN_MITER,
    'round': sk2const.JOIN_ROUND,
    'bevel': sk2const.JOIN_BEVEL,
}

SK2_LINE_CAP = {
    'butt': sk2const.CAP_BUTT,
    'round': sk2const.CAP_ROUND,
    'square': sk2const.CAP_SQUARE,
}

SK2_TEXT_ALIGN = {
    'start': sk2const.TEXT_ALIGN_LEFT,
    'middle': sk2const.TEXT_ALIGN_CENTER,
    'end': sk2const.TEXT_ALIGN_RIGHT,
}

SK2_GRAD_EXTEND = {
    'pad': sk2const.GRADIENT_EXTEND_PAD,
    'reflect': sk2const.GRADIENT_EXTEND_REFLECT,
    'repeat': sk2const.GRADIENT_EXTEND_REPEAT,
}


class SVG_to_SK2_Translator(object):
    page = None
    layer = None
    traffo = []
    dpi_coeff = 1.0
    user_space = []
    style_opts = {}
    classes = {}
    profiles = {}
    unit_mapping = None
    current_color = ''
    svg_doc = None
    sk2_doc = None
    svg_mt = None
    sk2_mt = None
    sk2_mtds = None
    svg_mtds = None
    id_map = None

    def translate(self, svg_doc, sk2_doc):
        self.svg_doc = svg_doc
        self.sk2_doc = sk2_doc
        self.svg_mt = svg_doc.model
        self.sk2_mt = sk2_doc.model
        self.sk2_mtds = sk2_doc.methods
        self.svg_mtds = svg_doc.methods
        self.classes = {}
        self.id_map = self.svg_mt.id_map
        self.profiles = {}
        self.current_color = ''
        self.define_units()
        self.translate_units()
        self.translate_page()
        for item in self.svg_mt.childs:
            style = self.get_level_style(self.svg_mt, svg_const.SVG_STYLE)
            self.translate_obj(self.layer, item, self.trafo, style)
        if len(self.page.childs) > 1 and not self.layer.childs:
            self.page.childs.remove(self.layer)
        self.sk2_mt.do_update()
        self._clear_objs()

    def _clear_objs(self):
        for item in self.__dict__.keys():
            obj = self.__dict__[item]
            if isinstance(obj, list):
                self.__dict__[item] = []
            elif isinstance(obj, dict):
                self.__dict__[item] = {}
            else:
                self.__dict__[item] = None
        self.dpi_coeff = 1.0
        self.current_color = ''

    # --- Utility methods

    def define_units(self):
        if not self.svg_doc.config.svg_dpi:
            if 'width' in self.svg_mt.attrs and \
                    self.svg_mtds.get_units(self.svg_mt.attrs['width']) not in \
                    (svg_const.SVG_PX, svg_const.SVG_PC):
                self.svg_doc.config.svg_dpi = 90.0

        dpi_coeff = self.svg_doc.config.svg_dpi / svg_const.SVG_DPI \
            if self.svg_doc.config.svg_dpi else 1.0

        self.unit_mapping = {
            svg_const.SVG_PX: svg_const.svg_px_to_pt / dpi_coeff,
            svg_const.SVG_PT: 1.0,
            svg_const.SVG_PC: 15.0 * svg_const.svg_px_to_pt / dpi_coeff,
            svg_const.SVG_MM: uc2const.mm_to_pt,
            svg_const.SVG_CM: uc2const.cm_to_pt,
            svg_const.SVG_IN: uc2const.in_to_pt,
            svg_const.SVG_M: uc2const.m_to_pt,
        }
        self.dpi_coeff = dpi_coeff

    def recalc_size(self, val):
        if not val:
            return None
        unit = self.svg_mtds.get_units(val)
        size = float(val.replace(unit, ''))
        return size * self.unit_mapping[unit] * self.dpi_coeff

    def get_font_size(self, sval):
        val = self.recalc_size(sval) / self.dpi_coeff
        pts = [[0.0, 0.0], [0.0, val]]
        pts = libgeom.apply_trafo_to_points(pts, self.trafo)
        return libgeom.distance(*pts)

    def get_viewbox(self, vbox):
        vbox = vbox.replace(',', ' ').replace('  ', ' ')
        return [self.recalc_size(item) for item in vbox.split()]

    def parse_def(self, svg_obj):
        if 'color' in svg_obj.attrs:
            if svg_obj.attrs['color'] == 'inherit':
                pass
            else:
                self.current_color = svg_obj.attrs['color']
        stops = []
        if svg_obj.tag == 'linearGradient':
            if 'xlink:href' in svg_obj.attrs:
                cid = svg_obj.attrs['xlink:href'][1:]
                if cid in self.id_map:
                    stops = self.parse_def(self.id_map[cid])[2][2]
                    if not stops:
                        return []
            elif svg_obj.childs:
                stops = parse_svg_stops(svg_obj.childs, self.current_color)
                if not stops:
                    return []
            else:
                return []

            x1 = 0.0
            y1 = 0.0
            x2 = self.user_space[2]
            y2 = 0.0
            if 'x1' in svg_obj.attrs:
                x1 = self.recalc_size(svg_obj.attrs['x1'])
            if 'y1' in svg_obj.attrs:
                y1 = self.recalc_size(svg_obj.attrs['y1'])
            if 'x2' in svg_obj.attrs:
                x2 = self.recalc_size(svg_obj.attrs['x2'])
            if 'y2' in svg_obj.attrs:
                y2 = self.recalc_size(svg_obj.attrs['y2'])

            if 'gradientTransform' in svg_obj.attrs:
                strafo = svg_obj.attrs['gradientTransform']
                self.style_opts['grad-trafo'] = get_svg_trafo(strafo)

            extend = sk2const.GRADIENT_EXTEND_PAD
            if 'spreadMethod' in svg_obj.attrs:
                val = svg_obj.attrs['spreadMethod']
                if val in SK2_GRAD_EXTEND:
                    extend = SK2_GRAD_EXTEND[val]

            vector = [[x1, y1], [x2, y2]]
            return [0, sk2const.FILL_GRADIENT,
                    [sk2const.GRADIENT_LINEAR, vector, stops, extend]]

        elif svg_obj.tag == 'radialGradient':
            if 'xlink:href' in svg_obj.attrs:
                cid = svg_obj.attrs['xlink:href'][1:]
                if cid in self.id_map:
                    stops = self.parse_def(self.id_map[cid])[2][2]
                    if not stops:
                        return []
            elif svg_obj.childs:
                stops = parse_svg_stops(svg_obj.childs, self.current_color)
                if not stops:
                    return []
            else:
                return []

            cx = self.user_space[2] / 2.0 + self.user_space[0]
            cy = self.user_space[3] / 2.0 + self.user_space[1]
            if 'cx' in svg_obj.attrs:
                cx = self.recalc_size(svg_obj.attrs['cx'])
            if 'cy' in svg_obj.attrs:
                cy = self.recalc_size(svg_obj.attrs['cy'])

            r = self.user_space[2] / 2.0 + self.user_space[0]
            if 'r' in svg_obj.attrs:
                r = self.recalc_size(svg_obj.attrs['r'])

            if 'gradientTransform' in svg_obj.attrs:
                strafo = svg_obj.attrs['gradientTransform']
                self.style_opts['grad-trafo'] = get_svg_trafo(strafo)

            extend = sk2const.GRADIENT_EXTEND_PAD
            if 'spreadMethod' in svg_obj.attrs:
                val = svg_obj.attrs['spreadMethod']
                if val in SK2_GRAD_EXTEND:
                    extend = SK2_GRAD_EXTEND[val]

            vector = [[cx, cy], [cx + r, cy]]
            return [0, sk2const.FILL_GRADIENT,
                    [sk2const.GRADIENT_RADIAL, vector, stops, extend]]

        return []

    def parse_clippath(self, svg_obj):
        if svg_obj.tag == 'clipPath' and svg_obj.childs:
            container = sk2_model.Container(self.layer.config)
            style = self.get_level_style(self.svg_mt, svg_const.SVG_STYLE)
            for child in svg_obj.childs:
                trafo = [] + libgeom.NORMAL_TRAFO
                self.translate_obj(container, child, trafo, style)
            if not container.childs:
                return None

            if len(container.childs) > 1:
                curves = []
                for item in container.childs:
                    item.update()
                    curve = item.to_curve()
                    pths = curve.get_initial_paths()
                    pths = libgeom.apply_trafo_to_paths(pths, curve.trafo)
                    curves.append(pths)
                paths = curves[0]
                for item in curves[1:]:
                    paths = libgeom.fuse_paths(paths, item)
            else:
                container.childs[0].update()
                curve = container.childs[0].to_curve()
                pths = curve.get_initial_paths()
                paths = libgeom.apply_trafo_to_paths(pths, curve.trafo)
            if not paths:
                return None
            curve = sk2_model.Curve(container.config, container, paths)
            container.childs = [curve, ]
            return container
        return None

    def get_level_style(self, svg_obj, style_in):
        if 'color' in svg_obj.attrs:
            if svg_obj.attrs['color'] == 'inherit':
                pass
            else:
                self.current_color = svg_obj.attrs['color']
        style = deepcopy(style_in)
        for item in svg_const.SVG_STYLE.keys():
            if item in svg_obj.attrs:
                val = svg_obj.attrs[item]
                if not val == 'inherit':
                    style[item] = val
        if 'class' in svg_obj.attrs:
            class_names = svg_obj.attrs['class'].split(' ')
            for class_name in class_names:
                if class_name in self.classes:
                    class_ = self.classes[class_name]
                    for item in class_.keys():
                        if item == 'opacity' and item in style_in:
                            op = float(class_[item]) * float(style_in[item])
                            style['opacity'] = str(op)
                        else:
                            style[item] = class_[item]
        if 'style' in svg_obj.attrs:
            stls = svg_obj.attrs['style'].split(';')
            for stl in stls:
                vals = stl.split(':')
                if len(vals) == 2:
                    key = vals[0].strip()
                    val = vals[1].strip()
                    if key == 'opacity' and key in style_in:
                        op = float(val) * float(style_in[key])
                        style['opacity'] = str(op)
                    else:
                        style[key] = val
        return style

    def get_sk2_style(self, svg_obj, style, text_style=False):
        sk2_style = [[], [], [], []]
        style = self.get_level_style(svg_obj, style)
        self.style_opts = {}

        if 'display' in style and style['display'] == 'none':
            return sk2_style
        if 'visibility' in style and \
                style['visibility'] in ('hidden', 'collapse'):
            return sk2_style

        # fill parsing
        if not style['fill'] == 'none':
            fillrule = SK2_FILL_RULE[style['fill-rule']]
            fill = style['fill'].replace('"', '')
            alpha = float(style['fill-opacity']) * float(style['opacity'])

            def_id = ''
            if len(fill) > 3 and fill[:3] == 'url':
                val = fill[5:].split(')')[0]
                if val in self.id_map:
                    def_id = val
            elif fill[0] == '#' and fill[1:] in self.id_map:
                def_id = fill[1:]

            if def_id:
                sk2_style[0] = self.parse_def(self.id_map[def_id])
                if sk2_style[0]:
                    sk2_style[0][0] = fillrule
                    if sk2_style[0][1] == sk2const.FILL_GRADIENT:
                        for stop in sk2_style[0][2][2]:
                            color = stop[1]
                            color[2] *= alpha
                if 'grad-trafo' in self.style_opts:
                    tr = [] + self.style_opts['grad-trafo']
                    self.style_opts['fill-grad-trafo'] = tr
            else:
                clr = parse_svg_color(fill, alpha, self.current_color)
                if clr:
                    sk2_style[0] = [fillrule, sk2const.FILL_SOLID, clr]

        # stroke parsing
        if not style['stroke'] == 'none':
            stroke = style['stroke'].replace('"', '')
            stroke_rule = sk2const.STROKE_MIDDLE
            stroke_width = self.recalc_size(style['stroke-width'])
            stroke_width = stroke_width / self.dpi_coeff
            stroke_linecap = SK2_LINE_CAP[style['stroke-linecap']]
            stroke_linejoin = SK2_LINE_JOIN[style['stroke-linejoin']]
            stroke_miterlimit = float(style['stroke-miterlimit'])
            alpha = float(style['stroke-opacity']) * float(style['opacity'])

            dash = []
            if style['stroke-dasharray'] != 'none':
                try:
                    code = compile('dash=[' + style['stroke-dasharray'] + ']',
                                   '<string>', 'exec')
                    exec code
                except Exception:
                    dash = []
            if dash:
                sk2_dash = []
                for item in dash:
                    sk2_dash.append(item / stroke_width)
                dash = sk2_dash

            def_id = ''
            if len(stroke) > 3 and stroke[:3] == 'url':
                val = stroke[5:].split(')')[0]
                if val in self.id_map:
                    def_id = val
            elif stroke[0] == '#' and stroke[1:] in self.id_map:
                def_id = stroke[1:]

            if def_id:
                stroke_fill = self.parse_def(self.id_map[def_id])
                if stroke_fill:
                    stroke_fill[0] = sk2const.FILL_NONZERO
                    if stroke_fill[1] == sk2const.FILL_GRADIENT:
                        for stop in stroke_fill[2][2]:
                            color = stop[1]
                            color[2] *= alpha
                    self.style_opts['stroke-fill'] = stroke_fill
                    self.style_opts['stroke-fill-color'] = stroke_fill[2][2][0][
                        1]
                    clr = parse_svg_color('black')
                    sk2_style[1] = [stroke_rule, stroke_width, clr, dash,
                                    stroke_linecap, stroke_linejoin,
                                    stroke_miterlimit, 0, 1, []]
                    if 'grad-trafo' in self.style_opts:
                        tr = [] + self.style_opts['grad-trafo']
                        self.style_opts['stroke-grad-trafo'] = tr
            else:
                clr = parse_svg_color(stroke, alpha, self.current_color)
                if clr:
                    sk2_style[1] = [stroke_rule, stroke_width, clr, dash,
                                    stroke_linecap, stroke_linejoin,
                                    stroke_miterlimit, 0, 1, []]

        if text_style:
            # font family
            font_family = 'Sans'
            if style['font-family'] in libpango.get_fonts()[0]:
                font_family = style['font-family']

            # font face
            font_face = 'Regular'
            faces = libpango.get_fonts()[1][font_family]
            if font_face not in faces:
                font_face = faces[0]

            bold = italic = False
            if style['font-style'] in ('italic', 'oblique'):
                italic = True
            if style['font-weight'] in ('bold', 'bolder'):
                bold = True

            if bold and italic:
                if 'Bold Italic' in faces:
                    font_face = 'Bold Italic'
                elif 'Bold Oblique' in faces:
                    font_face = 'Bold Oblique'
            elif bold and not italic:
                if 'Bold' in faces:
                    font_face = 'Bold'
            elif not bold and italic:
                if 'Italic' in faces:
                    font_face = 'Italic'
                elif 'Oblique' in faces:
                    font_face = 'Oblique'

            # text size
            font_size = 12.0
            try:
                font_size = self.get_font_size(style['font-size'])
            except Exception:
                pass

            # text alignment
            alignment = sk2const.TEXT_ALIGN_LEFT
            if style['text-anchor'] in SK2_TEXT_ALIGN:
                alignment = SK2_TEXT_ALIGN[style['text-anchor']]

            sk2_style[2] = [font_family, font_face, font_size,
                            alignment, [], True]

        return sk2_style

    def get_image(self, svg_obj):
        if 'xlink:href' not in svg_obj.attrs:
            return None
        link = svg_obj.attrs['xlink:href']
        if link[:4] == 'http':
            pass
        elif link[:4] == 'data':
            pos = 0
            for sig in svg_const.IMG_SIGS:
                if link[:len(sig)] == sig:
                    pos = len(sig)
            if pos:
                try:
                    raw_image = Image.open(StringIO(b64decode(link[pos:])))
                    raw_image.load()
                    return raw_image
                except Exception:
                    pass
        elif self.svg_doc.doc_file:
            file_dir = os.path.dirname(self.svg_doc.doc_file)
            image_path = os.path.join(file_dir, link)
            image_path = os.path.abspath(image_path)
            if fsutils.exists(image_path):
                raw_image = Image.open(image_path)
                raw_image.load()
                return raw_image
        return None

    # --- Translation metods

    def translate_units(self):
        units = SK2_UNITS[self.svg_mtds.doc_units()]
        self.sk2_mt.doc_units = units

    def translate_page(self):
        width = height = 0.0
        vbox = []
        if 'viewBox' in self.svg_mt.attrs:
            vbox = self.get_viewbox(self.svg_mt.attrs['viewBox'])

        if 'width' in self.svg_mt.attrs:
            if not self.svg_mt.attrs['width'][-1] == '%':
                width = self.recalc_size(self.svg_mt.attrs['width'])
            else:
                if vbox:
                    width = vbox[2]
            if 'height' in self.svg_mt.attrs and \
                    not self.svg_mt.attrs['height'][-1] == '%':
                height = self.recalc_size(self.svg_mt.attrs['height'])
            else:
                if vbox:
                    height = vbox[3]
        elif vbox:
            width = vbox[2]
            height = vbox[3]

        if not width:
            width = self.recalc_size('210mm')
        if not height:
            height = self.recalc_size('297mm')

        page_fmt = ['Custom', (width / self.dpi_coeff, height / self.dpi_coeff),
                    uc2const.LANDSCAPE if width > height else uc2const.PORTRAIT]

        pages_obj = self.sk2_mtds.get_pages_obj()
        pages_obj.page_format = page_fmt
        self.page = sk2_model.Page(pages_obj.config, pages_obj, 'SVG page')
        self.page.page_format = deepcopy(page_fmt)
        pages_obj.childs = [self.page, ]
        pages_obj.page_counter = 1

        self.layer = sk2_model.Layer(self.page.config, self.page)
        self.page.childs = [self.layer, ]

        # Document trafo calculation
        self.trafo = [1 / self.dpi_coeff, 0.0, 0.0,
                      1 / self.dpi_coeff, 0.0, 0.0]

        dx = -width / 2.0
        dy = height / 2.0
        tr = [1.0, 0.0, 0.0, -1.0, dx, dy]
        self.user_space = [0.0, 0.0, width, height]
        self.trafo = libgeom.multiply_trafo(tr, self.trafo)

        if vbox:
            dx = -vbox[0]
            dy = -vbox[1]
            xx = width / vbox[2]
            yy = height / vbox[3]
            if 'xml:space' in self.svg_mt.attrs and \
                    self.svg_mt.attrs['xml:space'] == 'preserve':
                xx = yy = min(xx, yy)
            tr = [xx, 0.0, 0.0, yy, 0.0, 0.0]
            tr = libgeom.multiply_trafo([1.0, 0.0, 0.0, 1.0, dx, dy], tr)
            self.trafo = libgeom.multiply_trafo(tr, self.trafo)
            self.user_space = vbox

    def translate_obj(self, parent, svg_obj, trafo, style):
        obj_mapping = {
            'g': self.translate_g,
            'rect': self.translate_rect,
            'circle': self.translate_circle,
            'ellipse': self.translate_ellipse,
            'line': self.translate_line,
            'polyline': self.translate_polyline,
            'polygon': self.translate_polygon,
            'path': self.translate_path,
            'use': self.translate_use,
            'text': self.translate_text,
            'image': self.translate_image,
        }

        if svg_obj.attrs.get('display') == 'none':
            return
        try:
            if svg_obj.tag == 'defs':
                self.translate_defs(svg_obj)
            elif svg_obj.tag == 'sodipodi:namedview':
                self.translate_namedview(svg_obj)
            elif svg_obj.tag == 'sodipodi:guide':
                self.translate_guide(svg_obj)
            elif svg_obj.tag in obj_mapping:
                obj_mapping[svg_obj.tag](parent, svg_obj, trafo, style)
            elif svg_obj.tag == 'linearGradient':
                return
            elif svg_obj.tag == 'radialGradient':
                return
            elif svg_obj.tag == 'style':
                self.translate_style(svg_obj)
            elif svg_obj.tag == 'pattern':
                return
            elif svg_obj.tag == 'clipPath':
                return
            elif svg_obj.childs:
                self.translate_unknown(parent, svg_obj, trafo, style)
        except Exception as e:
            LOG.warn('Cannot translate <%s> object, tag <%s>',
                     repr(svg_obj), svg_obj.tag)
            if 'id' in svg_obj.attrs:
                LOG.warn('Object id: %s', svg_obj.attrs['id'])
            LOG.warn('Error traceback: %s', e)

    def translate_defs(self, svg_obj):
        for item in svg_obj.childs:
            if item.tag == 'style':
                self.translate_style(item)
            elif item.tag == 'color-profile':
                self.translate_color_profile(item)

    def translate_namedview(self, svg_obj):
        for item in svg_obj.childs:
            self.translate_obj(None, item, None, None)

    def translate_guide(self, svg_obj):
        position = parse_svg_points(svg_obj.attrs['position'])[0]
        position = libgeom.apply_trafo_to_point(position, self.trafo)
        orientation = parse_svg_points(svg_obj.attrs['orientation'])[0]
        if position and orientation:
            if not orientation[0] and orientation[1]:
                orientation = uc2const.HORIZONTAL
                position = -position[1]
            elif not orientation[1] and orientation[0]:
                orientation = uc2const.VERTICAL
                position = position[0]
            else:
                return
            guide_layer = self.sk2_mtds.get_guide_layer()
            guide = sk2_model.Guide(guide_layer.config, guide_layer,
                                    position, orientation)
            guide_layer.childs.append(guide)

    def translate_style(self, svg_obj):
        items = []
        for item in svg_obj.childs:
            if item.is_content():
                val = item.text.strip()
                if val:
                    items.append(val)
        if not items:
            return
        items = ' '.join(items)
        if '.' not in items:
            return
        items = items.split('.')[1:]
        for item in items:
            if '{' not in item:
                continue
            class_, stylestr = item.split('{')
            stylestr = stylestr.replace('}', '')
            stls = stylestr.split(';')
            style = {}
            for stl in stls:
                vals = stl.split(':')
                if len(vals) == 2:
                    style[vals[0].strip()] = vals[1].strip()
            self.classes[class_.strip()] = style

    def translate_color_profile(self, svg_obj):
        self.profiles[svg_obj.attrs['name']] = svg_obj

    def translate_g(self, parent, svg_obj, trafo, style):
        tr = get_svg_level_trafo(svg_obj, trafo)
        stl = self.get_level_style(svg_obj, style)
        container = None

        if 'inkscape:groupmode' in svg_obj.attrs:
            if svg_obj.attrs['inkscape:groupmode'] == 'layer':
                name = 'Layer %d' % len(self.page.childs)
                if 'inkscape:label' in svg_obj.attrs:
                    name = svg_obj.attrs['inkscape:label']
                if not self.layer.childs:
                    self.page.childs.remove(self.layer)
                self.layer = sk2_model.Layer(self.page.config, self.page, name)
                self.page.childs.append(self.layer)
                if check_svg_attr(svg_obj, 'sodipodi:insensitive', 'true'):
                    self.layer.properties[1] = 0
                if 'display' in stl and stl['display'] == 'none':
                    self.layer.properties[0] = 0
                for item in svg_obj.childs:
                    self.translate_obj(self.layer, item, tr, stl)
                self.layer = sk2_model.Layer(self.page.config, self.page)
                self.page.childs.append(self.layer)
                return

        elif 'clip-path' in svg_obj.attrs:
            clip_id = svg_obj.attrs['clip-path'][5:-1].strip()
            if clip_id in self.id_map:
                container = self.parse_clippath(self.id_map[clip_id])

            if container:
                container.childs[0].trafo = [] + tr
                for item in svg_obj.childs:
                    self.translate_obj(container, item, tr, stl)
                if len(container.childs) > 1:
                    parent.childs.append(container)
                    return

        if not svg_obj.childs:
            return

        group = sk2_model.Group(parent.config, parent)
        for item in svg_obj.childs:
            self.translate_obj(group, item, tr, stl)
        if group.childs:
            if len(group.childs) == 1:
                parent.childs.append(group.childs[0])
            else:
                parent.childs.append(group)

    def translate_unknown(self, parent, svg_obj, trafo, style):
        group = sk2_model.Group(parent.config, parent)
        tr = get_svg_level_trafo(svg_obj, trafo)
        stl = self.get_level_style(svg_obj, style)
        for item in svg_obj.childs:
            self.translate_obj(group, item, tr, stl)
        if group.childs:
            parent.childs.append(group)

    def append_obj(self, parent, svg_obj, obj, trafo, style):
        obj.stroke_trafo = [] + trafo
        if style[0] and style[0][1] == sk2const.FILL_GRADIENT:
            obj.fill_trafo = [] + trafo
            if 'fill-grad-trafo' in self.style_opts:
                tr0 = self.style_opts['fill-grad-trafo']
                obj.fill_trafo = libgeom.multiply_trafo(tr0, trafo)

        curve = None
        if style[1] and 'stroke-fill' in self.style_opts:
            obj.update()
            stroke_obj = obj.to_curve()
            pths = libgeom.apply_trafo_to_paths(stroke_obj.get_initial_paths(),
                                                stroke_obj.trafo)
            try:
                pths = libgeom.stroke_to_curve(pths, obj.style[1])
                obj_style = [self.style_opts['stroke-fill'], [], [], []]
                curve = sk2_model.Curve(parent.config, parent, pths,
                                        style=obj_style)
                obj.style[1] = []
                curve.fill_trafo = [] + trafo
                if 'stroke-grad-trafo' in self.style_opts:
                    tr0 = self.style_opts['stroke-grad-trafo']
                    curve.fill_trafo = libgeom.multiply_trafo(tr0, trafo)
            except Exception:
                if 'stroke-fill-color' in self.style_opts:
                    obj.style[1][2] = self.style_opts['stroke-fill-color']
                else:
                    obj.style[1] = []

        container = None
        if 'clip-path' in svg_obj.attrs:
            clip_id = svg_obj.attrs['clip-path'][5:-1].strip()
            if clip_id in self.id_map:
                container = self.parse_clippath(self.id_map[clip_id])
                if container:
                    container.childs[0].trafo = [] + trafo

        if container:
            container.childs.append(obj)
            if curve:
                container.childs.append(curve)
            parent.childs.append(container)
        else:
            parent.childs.append(obj)
            if curve:
                parent.childs.append(curve)

    def translate_rect(self, parent, svg_obj, trafo, style):
        cfg = parent.config
        sk2_style = self.get_sk2_style(svg_obj, style)
        tr = get_svg_level_trafo(svg_obj, trafo)

        x = y = w = h = 0
        if 'x' in svg_obj.attrs:
            x = self.recalc_size(svg_obj.attrs['x'])
        if 'y' in svg_obj.attrs:
            y = self.recalc_size(svg_obj.attrs['y'])
        if 'width' in svg_obj.attrs:
            w = self.recalc_size(svg_obj.attrs['width'])
        if 'height' in svg_obj.attrs:
            h = self.recalc_size(svg_obj.attrs['height'])

        if not w or not h:
            return

        corners = [] + sk2const.CORNERS
        rx = ry = None
        if 'rx' in svg_obj.attrs:
            rx = self.recalc_size(svg_obj.attrs['rx'])
        if 'ry' in svg_obj.attrs:
            ry = self.recalc_size(svg_obj.attrs['ry'])
        if rx is None and ry is not None:
            rx = ry
        elif ry is None and rx is not None:
            ry = rx
        if not rx or not ry:
            rx = ry = None

        if rx is not None:
            rx = abs(rx)
            ry = abs(ry)
            if rx > w / 2.0:
                rx = w / 2.0
            if ry > h / 2.0:
                ry = h / 2.0
            coeff = rx / ry
            w = w / coeff
            trafo = [1.0, 0.0, 0.0, 1.0, -x, -y]
            trafo1 = [coeff, 0.0, 0.0, 1.0, 0.0, 0.0]
            trafo2 = [1.0, 0.0, 0.0, 1.0, x, y]
            trafo = libgeom.multiply_trafo(trafo, trafo1)
            trafo = libgeom.multiply_trafo(trafo, trafo2)
            tr = libgeom.multiply_trafo(trafo, tr)
            corners = [2.0 * ry / min(w, h), ] * 4

        rect = sk2_model.Rectangle(cfg, parent, [x, y, w, h], tr,
                                   sk2_style, corners)
        self.append_obj(parent, svg_obj, rect, tr, sk2_style)

    def translate_ellipse(self, parent, svg_obj, trafo, style):
        cfg = parent.config
        sk2_style = self.get_sk2_style(svg_obj, style)
        tr = get_svg_level_trafo(svg_obj, trafo)

        cx = cy = rx = ry = 0.0
        if 'cx' in svg_obj.attrs:
            cx = self.recalc_size(svg_obj.attrs['cx'])
        if 'cy' in svg_obj.attrs:
            cy = self.recalc_size(svg_obj.attrs['cy'])
        if 'rx' in svg_obj.attrs:
            rx = self.recalc_size(svg_obj.attrs['rx'])
        if 'ry' in svg_obj.attrs:
            ry = self.recalc_size(svg_obj.attrs['ry'])
        if not rx or not ry:
            return
        rect = [cx - rx, cy - ry, 2.0 * rx, 2.0 * ry]

        ellipse = sk2_model.Circle(cfg, parent, rect, style=sk2_style)
        ellipse.trafo = libgeom.multiply_trafo(ellipse.trafo, tr)
        self.append_obj(parent, svg_obj, ellipse, tr, sk2_style)

    def translate_circle(self, parent, svg_obj, trafo, style):
        cfg = parent.config
        sk2_style = self.get_sk2_style(svg_obj, style)
        tr = get_svg_level_trafo(svg_obj, trafo)

        cx = cy = r = 0.0
        if 'cx' in svg_obj.attrs:
            cx = self.recalc_size(svg_obj.attrs['cx'])
        if 'cy' in svg_obj.attrs:
            cy = self.recalc_size(svg_obj.attrs['cy'])
        if 'r' in svg_obj.attrs:
            r = self.recalc_size(svg_obj.attrs['r'])
        if not r:
            return
        rect = [cx - r, cy - r, 2.0 * r, 2.0 * r]

        ellipse = sk2_model.Circle(cfg, parent, rect, style=sk2_style)
        ellipse.trafo = libgeom.multiply_trafo(ellipse.trafo, tr)
        self.append_obj(parent, svg_obj, ellipse, tr, sk2_style)

    def translate_line(self, parent, svg_obj, trafo, style):
        cfg = parent.config
        sk2_style = self.get_sk2_style(svg_obj, style)
        tr = get_svg_level_trafo(svg_obj, trafo)

        x1 = y1 = x2 = y2 = 0.0
        if 'x1' in svg_obj.attrs:
            x1 = self.recalc_size(svg_obj.attrs['x1'])
        if 'y1' in svg_obj.attrs:
            y1 = self.recalc_size(svg_obj.attrs['y1'])
        if 'x2' in svg_obj.attrs:
            x2 = self.recalc_size(svg_obj.attrs['x2'])
        if 'y2' in svg_obj.attrs:
            y2 = self.recalc_size(svg_obj.attrs['y2'])

        paths = [[[x1, y1], [[x2, y2], ], sk2const.CURVE_OPENED], ]

        curve = sk2_model.Curve(cfg, parent, paths, tr, sk2_style)
        self.append_obj(parent, svg_obj, curve, tr, sk2_style)

    def _line(self, point1, point2):
        paths = [[[] + point1, [[] + point2, ], sk2const.CURVE_OPENED], ]
        tr = [] + self.trafo
        style = [[], self.layer.config.default_stroke, [], []]
        curve = sk2_model.Curve(self.layer.config, self.layer, paths, tr, style)
        self.layer.childs.append(curve)

    def _point(self, point, trafo=None):
        if not trafo:
            trafo = [] + self.trafo
        style = [[], self.layer.config.default_stroke, [], []]
        rect = sk2_model.Rectangle(self.layer.config, self.layer,
                                   point + [1.0, 1.0],
                                   trafo, style=style)
        self.layer.childs.append(rect)

    def translate_polyline(self, parent, svg_obj, trafo, style):
        cfg = parent.config
        sk2_style = self.get_sk2_style(svg_obj, style)
        tr = get_svg_level_trafo(svg_obj, trafo)

        if 'points' not in svg_obj.attrs:
            return
        points = parse_svg_points(svg_obj.attrs['points'])
        if not points or len(points) < 2:
            return
        paths = [[points[0], points[1:], sk2const.CURVE_OPENED], ]

        curve = sk2_model.Curve(cfg, parent, paths, tr, sk2_style)
        self.append_obj(parent, svg_obj, curve, tr, sk2_style)

    def translate_polygon(self, parent, svg_obj, trafo, style):
        cfg = parent.config
        sk2_style = self.get_sk2_style(svg_obj, style)
        tr = get_svg_level_trafo(svg_obj, trafo)

        if 'points' not in svg_obj.attrs:
            return
        points = parse_svg_points(svg_obj.attrs['points'])
        if not points or len(points) < 3:
            return
        points.append([] + points[0])
        paths = [[points[0], points[1:], sk2const.CURVE_CLOSED], ]

        curve = sk2_model.Curve(cfg, parent, paths, tr, sk2_style)
        self.append_obj(parent, svg_obj, curve, tr, sk2_style)

    def translate_path(self, parent, svg_obj, trafo, style):
        cfg = parent.config
        sk2_style = self.get_sk2_style(svg_obj, style)
        tr = get_svg_level_trafo(svg_obj, trafo)

        if check_svg_attr(svg_obj, 'sodipodi:type', 'arc'):
            cx = self.recalc_size(svg_obj.attrs['sodipodi:cx'])
            cy = self.recalc_size(svg_obj.attrs['sodipodi:cy'])
            rx = self.recalc_size(svg_obj.attrs['sodipodi:rx'])
            ry = self.recalc_size(svg_obj.attrs['sodipodi:ry'])
            angle1 = angle2 = 0.0
            if 'sodipodi:start' in svg_obj.attrs:
                angle1 = float(svg_obj.attrs['sodipodi:start'])
            if 'sodipodi:end' in svg_obj.attrs:
                angle2 = float(svg_obj.attrs['sodipodi:end'])
            circle_type = sk2const.ARC_PIE_SLICE
            if check_svg_attr(svg_obj, 'sodipodi:open', 'true'):
                circle_type = sk2const.ARC_ARC
            rect = [cx - rx, cy - ry, 2.0 * rx, 2.0 * ry]
            curve = sk2_model.Circle(cfg, parent, rect, angle1, angle2,
                                     circle_type, sk2_style)
            curve.trafo = libgeom.multiply_trafo(curve.trafo, tr)
            self.append_obj(parent, svg_obj, curve, tr, sk2_style)
        elif 'd' in svg_obj.attrs:
            paths = svg_utils.parse_svg_path_cmds(svg_obj.attrs['d'])
            if not paths:
                return

            curve = sk2_model.Curve(cfg, parent, paths, tr, sk2_style)
            self.append_obj(parent, svg_obj, curve, tr, sk2_style)

    def translate_use(self, parent, svg_obj, trafo, style):
        tr = get_svg_level_trafo(svg_obj, trafo)
        stl = self.get_level_style(svg_obj, style)
        if 'xlink:href' in svg_obj.attrs:
            obj_id = svg_obj.attrs['xlink:href'][1:]
            if obj_id in self.id_map:
                self.translate_obj(parent, self.id_map[obj_id], tr, stl)
            else:
                LOG.warn('<use> object id %s is not found', obj_id)

    def translate_text(self, parent, svg_obj, trafo, style):
        cfg = parent.config
        stl = self.get_level_style(svg_obj, style)
        sk2_style = self.get_sk2_style(svg_obj, stl, True)
        tr_level = get_svg_level_trafo(svg_obj, trafo)

        inv_tr = libgeom.invert_trafo(self.trafo)
        inv_tr[3] *= -1.0
        tr = libgeom.multiply_trafo(tr_level, inv_tr)
        tr = libgeom.multiply_trafo([FONT_COEFF, 0.0, 0.0,
                                     - FONT_COEFF, 0.0, 0.0], tr)

        x = y = 0.0
        if 'x' in svg_obj.attrs:
            x = parse_svg_coords(svg_obj.attrs['x'])[0]
        if 'y' in svg_obj.attrs:
            y = parse_svg_coords(svg_obj.attrs['y'])[0]

        if not svg_obj.childs:
            return
        txt = svg_utils.parse_svg_text(svg_obj.childs)
        if not txt:
            return

        x1, y1 = libgeom.apply_trafo_to_point([x, y], tr_level)
        x2, y2 = libgeom.apply_trafo_to_point([0.0, 0.0], tr)
        tr = libgeom.multiply_trafo(tr, [1.0, 0.0, 0.0, 1.0, -x2, -y2])

        text = sk2_model.Text(cfg, parent, [x1, y1], txt, -1, tr, sk2_style)
        self.append_obj(parent, svg_obj, text, tr_level, sk2_style)

    def translate_image(self, parent, svg_obj, trafo, style):
        cfg = parent.config
        tr_level = get_svg_level_trafo(svg_obj, trafo)
        inv_tr = libgeom.invert_trafo(self.trafo)
        tr = libgeom.multiply_trafo(inv_tr, tr_level)

        x = y = 0.0
        if 'x' in svg_obj.attrs:
            x = parse_svg_coords(svg_obj.attrs['x'])[0]
        if 'y' in svg_obj.attrs:
            y = parse_svg_coords(svg_obj.attrs['y'])[0]

        w = h = 0.0
        if 'width' in svg_obj.attrs:
            w = parse_svg_coords(svg_obj.attrs['width'])[0]
        if 'height' in svg_obj.attrs:
            h = parse_svg_coords(svg_obj.attrs['height'])[0]
        if not w or not h:
            return

        raw_image = self.get_image(svg_obj)
        if not raw_image:
            return
        img_w, img_h = raw_image.size
        trafo = [1.0, 0.0, 0.0, 1.0, -img_w / 2.0, -img_h / 2.0]
        trafo1 = [w / img_w, 0.0, 0.0, h / img_h, 0.0, 0.0]
        trafo2 = [1.0, 0.0, 0.0, 1.0, w / 2.0, h / 2.0]
        trafo = libgeom.multiply_trafo(trafo, trafo1)
        trafo = libgeom.multiply_trafo(trafo, trafo2)
        dx, dy = libgeom.apply_trafo_to_point([x, y], self.trafo)
        trafo3 = [1.0, 0.0, 0.0, 1.0, dx, dy - h]
        trafo = libgeom.multiply_trafo(trafo, trafo3)
        trafo = libgeom.multiply_trafo(trafo, tr)

        pixmap = sk2_model.Pixmap(cfg)
        pixmap.handler.load_from_images(self.sk2_doc.cms, raw_image)
        pixmap.trafo = trafo

        container = None
        if 'clip-path' in svg_obj.attrs:
            clip_id = svg_obj.attrs['clip-path'][5:-1].strip()
            if clip_id in self.id_map:
                container = self.parse_clippath(self.id_map[clip_id])
                if container:
                    container.childs[0].trafo = [] + tr_level

        if container:
            container.childs.append(pixmap)
            parent.childs.append(container)
        else:
            parent.childs.append(pixmap)


SVG_FILL_RULE = {
    sk2const.FILL_NONZERO: 'nonzero',
    sk2const.FILL_EVENODD: 'evenodd',
}

SVG_LINE_JOIN = {
    sk2const.JOIN_MITER: 'miter',
    sk2const.JOIN_ROUND: 'round',
    sk2const.JOIN_BEVEL: 'bevel',
}

SVG_LINE_CAP = {
    sk2const.CAP_BUTT: 'butt',
    sk2const.CAP_ROUND: 'round',
    sk2const.CAP_SQUARE: 'square',
}

SVG_GRAD_EXTEND = {
    sk2const.GRADIENT_EXTEND_PAD: 'pad',
    sk2const.GRADIENT_EXTEND_REFLECT: 'reflect',
    sk2const.GRADIENT_EXTEND_REPEAT: 'repeat',
}


class SK2_to_SVG_Translator(object):
    dx = dy = page_dx = 0.0
    indent_level = -1
    defs_count = 0
    trafo = None
    defs = None
    svg_doc = None
    sk2_doc = None
    svg_mt = None
    sk2_mt = None
    sk2_mtds = None
    svg_mtds = None

    def translate(self, sk2_doc, svg_doc):
        self.svg_doc = svg_doc
        self.sk2_doc = sk2_doc
        self.svg_mt = svg_doc.model
        self.sk2_mt = sk2_doc.model
        self.sk2_mtds = sk2_doc.methods
        self.svg_mtds = svg_doc.methods
        self.defs_count = 0
        svg_attrs = self.svg_mt.attrs

        self.trafo = [1.0, 0.0, 0.0, -1.0, 0.0, 0.0]
        svg_attrs['id'] = utils.generate_guid()
        units = svg_const.SVG_PX if self.sk2_mt.doc_units == uc2const.UNIT_PX \
            else svg_const.SVG_PT
        for item in self.svg_mt.childs:
            if item.tag == 'defs':
                self.defs = item
                break
        for item in self.sk2_mt.childs:
            if item.cid == sk2_model.PAGES:
                page = item.childs[0]
                w, h = page.page_format[1]
                svg_attrs['width'] = str(w) + units
                svg_attrs['height'] = str(h) + units
                if units != svg_const.SVG_PX:
                    svg_attrs['viewBox'] = '0 0 %s %s' % (str(w), str(h))
                self.dx = w / 2.0
                self.dy = h / 2.0
                self.trafo[4] = self.dx
                self.trafo[5] = self.dy
                self.page_dx = 0.0
                for page in item.childs:
                    self.translate_page(self.svg_mt, page)
        self.indent_level = 0
        if self.defs.childs:
            self.add_spacer(self.defs)
        else:
            self.svg_mt.childs.remove(self.defs)
        self.add_spacer(self.svg_mt)
        self.svg_doc = None
        self.sk2_doc = None
        self.svg_mt = None
        self.sk2_mt = None
        self.sk2_mtds = None
        self.svg_mtds = None

    def add_spacer(self, parent):
        spacer = '\n' + '\t' * self.indent_level
        parent.childs.append(svg_utils.create_spacer(spacer))

    def append_obj(self, parent, obj):
        self.add_spacer(parent)
        parent.childs.append(obj)

    def translate_page(self, dest_parent, source_obj):
        w, h = source_obj.page_format[1]
        self.trafo[4] = w / 2.0 + self.page_dx
        if self.page_dx:
            rect = svg_utils.create_rect(self.page_dx, self.dy - h / 2.0, w, h)
            rect.attrs['style'] = 'fill:none;stroke:black;'
            self.append_obj(self.svg_mt, rect)
        self.translate_objs(self.svg_mt, source_obj.childs)
        self.page_dx += w + 30.0

    def translate_objs(self, dest_parent, source_objs):
        self.indent_level += 1
        for source_obj in source_objs:
            if source_obj.is_layer:
                self.translate_layer(dest_parent, source_obj)
            elif source_obj.is_group:
                self.translate_group(dest_parent, source_obj)
            elif source_obj.is_pixmap:
                self.translate_pixmap(dest_parent, source_obj)
            elif source_obj.is_primitive:
                if source_obj.style[0] and source_obj.style[1] \
                        and source_obj.style[1][7]:
                    stroke_obj = source_obj.copy()
                    stroke_obj.update()
                    stroke_obj.style[0] = []
                    self.translate_primitive(dest_parent, stroke_obj)

                    fill_obj = source_obj.copy()
                    fill_obj.update()
                    fill_obj.style[1] = []
                    self.translate_primitive(dest_parent, fill_obj)
                else:
                    self.translate_primitive(dest_parent, source_obj)
        self.indent_level -= 1

    def translate_layer(self, dest_parent, source_obj):
        group = svg_utils.create_xmlobj('g')
        if not source_obj.properties[0]:
            group.attrs['style'] = 'display:none;'
        self.translate_objs(group, source_obj.childs)
        self.add_spacer(group)
        self.append_obj(dest_parent, group)

    def translate_group(self, dest_parent, source_obj):
        if source_obj.is_container:
            clip = source_obj.childs[0]
            clip_id = self.make_clippath(clip)

            if clip.style[1] and clip.style[1][7]:
                stroke_obj = clip.copy()
                stroke_obj.update()
                stroke_obj.style[0] = []
                self.translate_primitive(dest_parent, stroke_obj)
            if clip.style[0]:
                fill_obj = clip.copy()
                fill_obj.update()
                fill_obj.style[1] = []
                self.translate_primitive(dest_parent, fill_obj)

            group = svg_utils.create_xmlobj('g')
            group.attrs['clip-path'] = 'url(#%s)' % clip_id
            self.translate_objs(group, source_obj.childs[1:])
            self.add_spacer(group)
            self.append_obj(dest_parent, group)

            if clip.style[1] and not clip.style[1][7]:
                stroke_obj = clip.copy()
                stroke_obj.update()
                stroke_obj.style[0] = []
                self.translate_primitive(dest_parent, stroke_obj)
        else:
            group = svg_utils.create_xmlobj('g')
            self.translate_objs(group, source_obj.childs)
            self.add_spacer(group)
            self.append_obj(dest_parent, group)

    def make_clippath(self, source_obj):
        clippath = svg_utils.create_xmlobj('clipPath')
        clippath.attrs['clipPathUnits'] = 'userSpaceOnUse'
        clippath.attrs['id'] = 'clipPath' + str(self.defs_count + 1)
        self.defs_count += 1

        lvl = self.indent_level
        self.indent_level = 1
        self.append_obj(self.defs, clippath)
        self.indent_level += 1
        self.translate_primitive(clippath, source_obj)
        self.indent_level = lvl
        return clippath.attrs['id']

    def translate_primitive(self, dest_parent, source_obj):
        curve = source_obj.to_curve()
        if curve.is_group:
            self.translate_group(dest_parent, curve)
            return
        curve.update()
        style = self.translate_style(source_obj)
        trafo = libgeom.multiply_trafo(curve.trafo, self.trafo)
        paths = libgeom.apply_trafo_to_paths(curve.paths, trafo)
        pth = svg_utils.create_xmlobj('path')
        pth.attrs['style'] = style
        pth.attrs['d'] = svg_utils.translate_paths_to_d(paths)
        self.append_obj(dest_parent, pth)
        arrows = curve.arrows_to_curve()
        if arrows:
            self.translate_primitive(dest_parent, arrows)

    def translate_pixmap(self, dest_parent, source_obj):
        surface = source_obj.handler.get_surface(self.sk2_doc.cms)
        image_stream = StringIO()
        surface.write_to_png(image_stream)
        content = b64encode(image_stream.getvalue())
        image = svg_utils.create_xmlobj('image')
        w, h = source_obj.get_size()
        trafo = [1.0, 0.0, 0.0, -1.0, 0.0, 0.0]
        trafo = libgeom.multiply_trafo(trafo, source_obj.trafo)
        trafo = libgeom.multiply_trafo(trafo, self.trafo)
        image.attrs['xlink:href'] = 'data:image/png;base64,' + content
        image.attrs['transform'] = 'matrix(%s)' % trafo.__str__()[1:-1]
        image.attrs['x'] = '0'
        image.attrs['y'] = str(-h)
        image.attrs['width'] = str(w)
        image.attrs['height'] = str(h)
        self.append_obj(dest_parent, image)

    def translate_style(self, obj):
        style = {}
        self.set_fill(style, obj)
        self.set_stroke(style, obj)
        return svg_utils.translate_style_dict(style)

    def set_stroke(self, svg_style, obj):
        if not obj.style[1]:
            return
        # Stroke width
        line_width = 0.0
        if obj.style[1][8]:
            stroke_trafo = obj.stroke_trafo
            if not stroke_trafo:
                stroke_trafo = [] + libgeom.NORMAL_TRAFO
            points = [[0.0, 0.0], [1.0, 0.0]]
            points = libgeom.apply_trafo_to_points(points, stroke_trafo)
            coef = libgeom.distance(*points)
            line_width = obj.style[1][1] * coef
            svg_style['stroke-width'] = str(round(line_width, 4))
        else:
            if not obj.style[1][1] == 1.0:
                line_width = obj.style[1][1]
                svg_style['stroke-width'] = str(round(line_width, 4))
        # Stroke color
        clr = self.sk2_doc.cms.get_rgb_color(obj.style[1][2])
        svg_style['stroke'] = cms.rgb_to_hexcolor(clr[1])
        if clr[2] < 1.0:
            svg_style['stroke-opacity'] = str(clr[2])
        # Stroke dash
        if obj.style[1][3]:
            vals = []
            for item in obj.style[1][3]:
                vals.append(str(round(item * line_width, 4)))
            svg_style['stroke-dasharray'] = ', '.join(vals)
        # Stroke caps
        caps = SVG_LINE_CAP[obj.style[1][4]]
        if not caps == 'butt':
            svg_style['stroke-linecap'] = caps
        # Stroke join
        join = SVG_LINE_JOIN[obj.style[1][5]]
        if not join == 'miter':
            svg_style['stroke-linejoin'] = join
        # Miter limit
        svg_style['stroke-miterlimit'] = str(round(obj.style[1][6], 4))

    def set_fill(self, svg_style, obj):
        svg_style['fill'] = 'none'
        if not obj.style[0]:
            return
        if obj.style[0][1] == sk2const.FILL_SOLID:
            if obj.style[0][0] == sk2const.FILL_EVENODD:
                svg_style['fill-rule'] = 'evenodd'
            clr = self.sk2_doc.cms.get_rgb_color(obj.style[0][2])
            svg_style['fill'] = cms.rgb_to_hexcolor(clr[1])
            if clr[2] < 1.0:
                svg_style['fill-opacity'] = str(clr[2])
        elif obj.style[0][1] == sk2const.FILL_GRADIENT:
            if obj.style[0][0] == sk2const.FILL_EVENODD:
                svg_style['fill-rule'] = 'evenodd'
            grad_id = self.translate_gradient(obj.style[0][2], obj)
            svg_style['fill'] = 'url(#%s)' % grad_id

    def translate_gradient(self, gradient, obj):
        grad_id = 'grad' + str(self.defs_count + 1)
        self.defs_count += 1
        trafo = libgeom.multiply_trafo(obj.fill_trafo, self.trafo)
        vector = libgeom.apply_trafo_to_points(gradient[1], trafo)
        spread = 'pad'
        if len(gradient) > 3:
            spread = SVG_GRAD_EXTEND[gradient[3]]
        attrs = {'gradientUnits': 'userSpaceOnUse'}
        if gradient[0] == sk2const.GRADIENT_RADIAL:
            tag = 'radialGradient'
            attrs['id'] = grad_id
            attrs['spreadMethod'] = spread
            cx, cy = gradient[1][0]
            r = libgeom.distance(*gradient[1])
            attrs['cx'] = str(cx)
            attrs['cy'] = str(cy)
            attrs['r'] = str(r)
            tr = trafo.__str__()[1:-1]
            attrs['gradientTransform'] = 'matrix(%s)' % tr
        else:
            tag = 'linearGradient'
            x1, y1 = vector[0]
            x2, y2 = vector[1]
            attrs['id'] = grad_id
            attrs['spreadMethod'] = spread
            attrs['x1'] = str(x1)
            attrs['y1'] = str(y1)
            attrs['x2'] = str(x2)
            attrs['y2'] = str(y2)
        grad_obj = svg_utils.create_xmlobj(tag, attrs)
        lvl = self.indent_level
        self.indent_level = 1
        self.append_obj(self.defs, grad_obj)
        self.indent_level += 1
        self.translate_stops(grad_obj, gradient[2])
        self.indent_level = lvl
        return grad_id

    def translate_stops(self, parent, stops):
        for stop in stops:
            attrs = {}
            offset, color = stop
            attrs['offset'] = str(offset)
            clr = self.sk2_doc.cms.get_rgb_color(color)
            clr = cms.rgb_to_hexcolor(clr[1])
            alpha = str(color[2])
            attrs['style'] = 'stop-color:%s;stop-opacity:%s;' % (clr, alpha)
            stop_obj = svg_utils.create_xmlobj('stop', attrs)
            self.append_obj(parent, stop_obj)
        self.indent_level -= 1
        self.add_spacer(parent)
