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
from uc2.libgeom import multiply_trafo, trafo_rotate_grad
from uc2.libgeom.points import distance, is_equal_points
from uc2.libgeom.trafo import apply_trafo_to_points
from uc2 import _, uc2const, sk2const, cms
from colorsys import hsv_to_rgb
import copy


SK2_UNITS = {
    xar_const.REF_UNIT_PIXELS: uc2const.UNIT_PX,
    xar_const.REF_UNIT_MILLIMETRES: uc2const.UNIT_MM,
    xar_const.REF_UNIT_CENTIMETRES: uc2const.UNIT_CM,
    xar_const.REF_UNIT_METRES: uc2const.UNIT_M,
    xar_const.REF_UNIT_INCHES: uc2const.UNIT_IN,
    xar_const.REF_UNIT_FEET: uc2const.UNIT_FT,
}


MODE_TINT = {
    uc2const.COLOR_RGB: xar_const.RGB_WHITE,
    uc2const.COLOR_CMYK: xar_const.CMYK_WHITE,
    uc2const.COLOR_GRAY: xar_const.GREYSCALE_WHITE,
}


def color_tint(color1, coef=0.5, colour_name=''):
    mode = color1[0]
    color2 = MODE_TINT.get(mode)
    if color2 is not None:
        colour = cms.mix_lists(color2[1], color1[1], coef)
        a = cms.mix_vals(color2[2], color1[2], coef)
        return [mode, colour, a, colour_name]
    raise NotImplemented()


def pick_page_format_name(width, height):
    if width > height:
        size = (height, width)
    else:
        size = (width, height)
    for name, fzise in uc2const.PAGE_FORMATS.items():
        if is_equal_points(fzise, size, 2):
            return name
    return _('Custom')


class XAR_to_SK2_Translator(object):
    xar_mtds = None
    sk2_doc = None
    sk2_model = None
    sk2_mtds = None

    fontmap = None
    colors = None
    atomic_tags = None

    stack_style = None
    stack = None
    pages = None
    layers = None

    style = None
    trafo = None
#    page = None

    layer = None
    layer_name = ''
    page_name = ''
    page_format = None

    def translate(self, xar_doc, sk2_doc):
        self.xar_mtds = xar_doc.methods
        self.sk2_doc = sk2_doc
        self.sk2_model = sk2_doc.model
        self.sk2_mtds = sk2_doc.methods
        self.sk2_mtds.delete_page()

        self.colors = copy.deepcopy(xar_const.XAR_COLOURS)
        self.atomic_tags = set()
        self.trafo = [-1.0, 0.0, 0.0, -1.0, 0.0, 0.0]

        self.stack = []
        self.stack_style = [copy.copy(xar_const.XAR_DEFAULT_STYLE)]
        self.pages = []
        self.layers = []

        self.walk(xar_doc.model.childs[::-1])
        self.handle_endoffile()
        sk2_doc.model.do_update()

    def walk(self, stack):
        while stack:
            rec = stack.pop()
            if not self.is_atomic(rec.cid):
                if rec.childs:
                    childs = rec.childs[::-1]
                    rec.childs = []
                    stack.append(childs[0])
                    stack.append(rec)
                    stack.extend(childs[1:])
                else:
                    self.process(rec)

    def is_atomic(self, cid):
        if cid in self.atomic_tags:
            return True
        elif cid not in xar_const.XAR_TYPE_RECORD:
            self.atomic_tags.add(cid)
            return True

    def process(self, rec):
        cfg = self.sk2_doc.config

        # Navigation records
        if rec.cid == xar_const.TAG_UP:
            self.handle_up(rec, cfg)
        elif rec.cid == xar_const.TAG_DOWN:
            self.handle_down(rec, cfg)

        # Document tags
        elif rec.cid == xar_const.TAG_SPREAD:
            self.handle_spread(rec, cfg)

        # Notes
        elif rec.cid == xar_const.TAG_LAYER:
            self.handle_layer(rec, cfg)
        elif rec.cid == xar_const.TAG_LAYERDETAILS:
            self.handle_layerdetails(rec, cfg)
        elif rec.cid == xar_const.TAG_SPREADINFORMATION:
            self.handle_spred_information(rec, cfg)

        # Colour reference tags
        elif rec.cid == xar_const.TAG_DEFINECOMPLEXCOLOUR:
            self.handle_definecomplexcolor(rec, cfg)

        # Object tags
        elif rec.cid == xar_const.TAG_PATH:
            raise NotImplementedError
        elif rec.cid == xar_const.TAG_PATH_FILLED:
            self.handle_path_filled(rec, cfg)
        elif rec.cid == xar_const.TAG_PATH_STROKED:
            self.handle_path_stroked(rec, cfg)
        elif rec.cid == xar_const.TAG_PATH_FILLED_STROKED:
            self.handle_path_filled_stroked(rec, cfg)

        elif rec.cid == xar_const.TAG_GROUP:
            self.handle_group(rec, cfg)
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
        elif rec.cid == xar_const.TAG_LINEARFILL:
            self.handle_linearfill(rec, cfg)
        # elif rec.cid == xar_const.TAG_LINEARTRANSPARENTFILL:
        #     self.handle_lineartransparentfill(rec, cfg)

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

        # Regular shapes

        # Ellipses
        elif rec.cid == xar_const.TAG_ELLIPSE_SIMPLE:
            self.handle_ellipse_simple(rec, cfg)
        elif rec.cid == xar_const.TAG_ELLIPSE_COMPLEX:
            self.handle_ellipse_complex(rec, cfg)

        # Rectangles

        # Polygons

        # General regular shapes
        elif rec.cid == xar_const.TAG_REGULAR_SHAPE_PHASE_2:
            self.handle_regular_shape_phase_2(rec, cfg)

        # Miscellaneous records
        elif rec.cid == xar_const.TAG_SPREAD_PHASE2:
            self.handle_spread_phase2(rec, cfg)

        # Multi stage fill tags
        elif rec.cid == xar_const.TAG_LINEARFILLMULTISTAGE:
            self.handle_linearfillmultistage(rec, cfg)

    def handle_up(self, rec, cfg):
        self.style = self.stack_style.pop()

    def handle_down(self, rec, cfg):
        self.style = copy.copy(self.stack_style[-1])
        self.stack_style.append(self.style)

    def handle_endoffile(self, rec=None, cfg=None):
        if self.stack:
            cfg = cfg or self.sk2_doc.config
            self.handle_layer(rec, cfg)
            self.handle_spread(rec, cfg)
        parent = self.sk2_mtds.get_pages_obj()

        self.pages = [page for page in self.pages if page.childs]
        for page in self.pages:
            page.parent = parent
        parent.page_counter += len(self.pages)
        parent.childs.extend(self.pages)
        self.pages = []

    def handle_spread(self, rec, cfg):
        page = sk2_model.Page(cfg, name=self.page_name)
        if self.page_format:
            page.page_format = self.page_format
        self.page_name = ''

        for el in self.layers:
            el.parent = page

        page.layer_counter += len(self.layers)
        page.childs.extend(self.layers)
        self.layers = []
        self.pages.append(page)

    def handle_spread_phase2(self, rec, cfg):
        self.handle_spread(rec, cfg)

    def handle_layer(self, rec, cfg):
        layer = sk2_model.Layer(cfg, name=self.layer_name)
        self.layer_name = ''
        self.flush_stack(layer)
        self.layers.append(layer)

    def handle_group(self, rec, cfg):
        if self.stack and len(self.stack) > 1:
            group = sk2_model.Group(cfg)
            self.flush_stack(group)
            self.stack = [group]

    def handle_regular_shape_phase_2(self, rec, cfg):
        w = distance(rec.minor_axes)
        h = distance(rec.major_axes)

        if rec.flags == 1:
            el = sk2_model.Circle(
                cfg, None,
                rect=[-w, -h, w*2.0, h*2.0],
                angle1=0.0,
                angle2=0.0,
                circle_type=sk2const.ARC_CHORD,
                style=self.get_style(fill=True, stroke=True)
            )
        else:
            el = sk2_model.Polygon(
                cfg, None,
                corners_num=rec.number_of_sides,
                coef2=rec.stell_radius_to_primary if rec.flags & 2 else 1.0,
                style=self.get_style(fill=True, stroke=True)
            )
            angle = -90 + 360.0 / rec.number_of_sides / 2.0
            tr = trafo_rotate_grad(angle, 0.5, 0.5)
            el.trafo = multiply_trafo(el.trafo, tr)
            tr = [w*2.0, 0.0, 0.0, h*2.0, -w, -h]
            el.trafo = multiply_trafo(el.trafo, tr)

        tr = [rec.a, rec.b, rec.c, rec.d, rec.e/1000.0, rec.f/1000.0]
        el.trafo = multiply_trafo(el.trafo, tr)
        el.trafo = multiply_trafo(el.trafo, self.get_trafo())
        self.stack.append(el)

    def handle_ellipse_simple(self, rec, cfg):
        raise 1

    def handle_ellipse_complex(self, rec, cfg):
        raise 1

    def handle_units(self):
        self.sk2_mtds.set_doc_units(uc2const.UNIT_PT)

    def handle_layerdetails(self, rec, cfg):
        # TODO: process layer_flags
        self.layer_name = rec.layer_name

    def handle_definecomplexcolor(self, rec, cfg):
        colour = None

        if rec.colour_type == xar_const.COLOUR_TYPE_NORMAL:
            if rec.colour_model == xar_const.COLOUR_MODEL_GREYSCALE:
                grey = [rec.component1]
                colour = [uc2const.COLOR_GRAY, grey, 1.0, rec.colour_name]
            elif rec.colour_model == xar_const.COLOUR_MODEL_RGB:
                rgb = [rec.component1, rec.component2, rec.component3]
                colour = [uc2const.COLOR_RGB, rgb, 1.0, rec.colour_name]
            elif rec.colour_model == xar_const.COLOUR_MODEL_HSV:
                rgb = hsv_to_rgb(rec.component1, rec.component2, rec.component3)
                colour = [uc2const.COLOR_RGB, list(rgb), 1.0, rec.colour_name]
            elif rec.colour_model == xar_const.COLOUR_MODEL_CMYK:
                cmyk = [rec.component1, rec.component2,
                        rec.component3, rec.component4]
                colour = [uc2const.COLOR_CMYK, cmyk, 1.0, rec.colour_name]
        elif rec.colour_type == xar_const.COLOUR_TYPE_SPOT:
            pass  # TODO
        elif rec.colour_type == xar_const.COLOUR_TYPE_TINT:
            parent_color = self.colors.get(rec.parent_colour)
            colour = color_tint(parent_color, rec.component1, rec.colour_name)
        elif rec.colour_type == xar_const.COLOUR_TYPE_LINKED:
            pass  # TODO
        elif rec.colour_type == xar_const.COLOUR_TYPE_SHADE:
            pass  # TODO

        if not colour:
            # TODO: process colour_model, colour_type
            # n = self.sk2_doc.doc_file
            # print '? color name:', rec.rgbcolor, rec.colour_name, n
            # print '? color:', rec.colour_type, self.colors[rec.parent_colour]
            # print '?', [rec.component1, rec.component2, rec.component3, rec.component4]
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

    def handle_linearfill(self, rec, cfg):
        trafo = self.get_trafo()
        vector = apply_trafo_to_points([rec.start_point, rec.end_point], trafo)
        start_colour = self.get_color(rec.start_colour)
        end_colour = self.get_color(rec.end_colour)
        stops = [[0.0, start_colour], [1.0, end_colour]]
        self.style['linearfill'] = [
            sk2const.GRADIENT_LINEAR,
            vector,
            stops,
            sk2const.GRADIENT_EXTEND_PAD  # TODO
        ]

    def handle_linearfillmultistage(self, rec, cfg):
        trafo = self.get_trafo()
        vector = apply_trafo_to_points([rec.start_point, rec.end_point], trafo)
        start_colour = self.get_color(rec.start_colour)
        end_colour = self.get_color(rec.end_colour)

        stops = [[0.0, start_colour]]
        for p in rec.stop_colors:
            stops.append([p[0], self.get_color(p[1])])
        stops.append([1.0, end_colour])

        self.style['linearfill'] = [
            sk2const.GRADIENT_LINEAR,
            vector,
            stops,
            sk2const.GRADIENT_EXTEND_PAD  # TODO
        ]

    # def handle_lineartransparentfill(self, rec, cfg):
    #     trafo = self.get_trafo()
    #
    #     vector = apply_trafo_to_points([rec.start_point, rec.end_point], trafo)
    #
    #     linearfill = self.style.get('linearfill')
    #     if linearfill:
    #         start_colour = copy.deepcopy(linearfill[2][0][1])
    #         end_colour = copy.deepcopy(linearfill[2][1][1])
    #     else:
    #         color = self.style.get('flat_colour_fill') or xar_const.RGB_WHITE
    #         start_colour = copy.deepcopy(color)
    #         end_colour = copy.deepcopy(color)
    #
    #     start_colour[2] = 1. - rec.start_transparency / 255.0
    #     end_colour[2] = 1. - rec.end_transparency / 255.0
    #
    #     self.style['linearfill'] = [
    #         sk2const.GRADIENT_LINEAR,
    #         vector,
    #         [[0.0, start_colour], [1.0, end_colour]],
    #         sk2const.GRADIENT_EXTEND_PAD
    #     ]

    def handle_path_strokedled(self, rec, cfg):
        curve = sk2_model.Curve(
            cfg, None,
            self.get_path(rec),
            self.get_trafo(),
            self.get_style(stroke=True)
        )
        self.stack.append(curve)

    def handle_path_filled(self, rec, cfg):
        curve = sk2_model.Curve(
            cfg, None,
            self.get_path(rec),
            self.get_trafo(),
            self.get_style(fill=True)
        )
        self.stack.append(curve)

    def handle_path_filled_stroked(self, rec, cfg):
        curve = sk2_model.Curve(
            cfg, None,
            self.get_path(rec),
            self.get_trafo(),
            self.get_style(stroke=True, fill=True)
        )
        self.stack.append(curve)

    def handle_path_relative_stroked(self, rec, cfg):
        curve = sk2_model.Curve(
            cfg, None,
            self.get_path_relative(rec),
            self.get_trafo(),
            self.get_style(stroke=True)
        )
        self.stack.append(curve)

    def handle_path_relative_filled(self, rec, cfg):
        curve = sk2_model.Curve(
            cfg, None,
            self.get_path_relative(rec),
            self.get_trafo(),
            self.get_style(fill=True)
        )
        self.stack.append(curve)

    def handle_path_relative_filled_stroked(self, rec, cfg):
        curve = sk2_model.Curve(
            cfg, None,
            self.get_path_relative(rec),
            self.get_trafo(),
            self.get_style(stroke=True, fill=True)
        )
        self.stack.append(curve)

    def handle_spred_information(self, rec, cfg):
        width = rec.width
        height = rec.height
        fmt = pick_page_format_name(width, height)
        size = (width, height)
        orient = uc2const.PORTRAIT
        if width > height:
            orient = uc2const.LANDSCAPE
        self.page_format = [fmt, size, orient]
        trafo = [1.0, 0.0, 0.0, 1.0, -1.0 * width / 2.0, -1.0 * height / 2.0]
        self.set_trafo(trafo)

    def get_color(self, colour_ref):
        return self.colors.get(colour_ref) or xar_const.RGB_WHITE

    def set_trafo(self, trafo):
        self.trafo = trafo

    def get_trafo(self):
        return copy.deepcopy(self.trafo)

    def get_style(self, stroke=False, fill=False):
        fill = fill and self.get_fill() or []
        stroke = stroke and self.get_stoke() or []
        return [fill, stroke, [], []]

    def get_fill(self):
        fill_rule = sk2const.FILL_EVENODD
        fill_data = []
        fill_type = sk2const.FILL_SOLID
        if self.style.get('linearfill'):
            fill_type = sk2const.FILL_GRADIENT
            fill_data = self.style['linearfill']
        elif self.style.get('flat_colour_fill'):
            fill_type = sk2const.FILL_SOLID
            fill_data = self.style['flat_colour_fill']

        if fill_data:
            return [fill_rule, fill_type, fill_data]
        return []

    def get_stoke(self):
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
        for closed, points in self.xar_mtds.read_path(zip(rec.verb, rec.coord)):
            marker = sk2const.CURVE_CLOSED if closed else sk2const.CURVE_OPENED
            path = []
            for point in points:
                if len(point) == 3:
                    point = [point[0], point[1], point[2], sk2const.NODE_CUSP]
                path.append(point)
            paths.append([path[0], path[1:], marker])
        return paths

    def get_path_relative(self, rec):
        paths = []
        for closed, points in self.xar_mtds.read_path_relative(rec.path):
            marker = sk2const.CURVE_CLOSED if closed else sk2const.CURVE_OPENED
            path = []
            for point in points:
                if len(point) == 3:
                    point = [point[0], point[1], point[2], sk2const.NODE_CUSP]
                path.append(point)
            paths.append([path[0], path[1:], marker])
        return paths

    def flush_stack(self, parent):
        for el in self.stack:
            el.parent = parent
        parent.childs.extend(self.stack)
        self.stack = []


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

