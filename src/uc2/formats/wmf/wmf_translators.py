# -*- coding: utf-8 -*-
#
#  Copyright (C) 2016-2017 by Igor E. Novikov
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
from copy import deepcopy
from cStringIO import StringIO

from uc2 import uc2const, libgeom, libpango, libimg, sk2const, utils
from uc2.formats.sk2 import sk2_model
from uc2.formats.wmf import wmf_const, wmf_hatches, wmf_utils, wmf_model
from uc2.formats.wmf.wmf_utils import get_data, rndpoint
from uc2.libgeom import multiply_trafo, apply_trafo_to_point

LOG = logging.getLogger(__name__)

SK2_CAPS = {
    wmf_const.PS_ENDCAP_FLAT: sk2const.CAP_BUTT,
    wmf_const.PS_ENDCAP_ROUND: sk2const.CAP_ROUND,
    wmf_const.PS_ENDCAP_SQUARE: sk2const.CAP_SQUARE,
}

SK2_JOIN = {
    wmf_const.PS_JOIN_MITER: sk2const.JOIN_MITER,
    wmf_const.PS_JOIN_ROUND: sk2const.JOIN_ROUND,
    wmf_const.PS_JOIN_BEVEL: sk2const.JOIN_BEVEL,
}

SK2_FILL_RULE = {
    wmf_const.ALTERNATE: sk2const.FILL_EVENODD,
    wmf_const.WINDING: sk2const.FILL_NONZERO,
}


class DC_Data(object):
    style = [[], [], [], []]
    curpoint = [0.0, 0.0]
    trafo = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
    opacity = True
    bgcolor = [1.0, 1.0, 1.0]
    fill_rule = sk2const.FILL_EVENODD
    text_color = [0.0, 0.0, 0.0]
    text_align = sk2const.TEXT_ALIGN_LEFT
    text_valign = sk2const.TEXT_VALIGN_BASELINE
    text_update_cp = True
    text_rtl = False
    # (fontface, size, bold,italic,underline,strikeout, rotate, charset)
    font = ('Sans', 12, False, False, False, False, 0.0, 'cp1252')


class WMF_to_SK2_Translator(object):
    wmf_doc = None
    sk2_doc = None
    wmf_mt = None
    sk2_mt = None
    sk2_mtds = None
    gdiobjects = None
    dcstack = None
    dc = None
    inch = None
    bbox = None
    coef = None
    wx = 0
    vx = 0
    vwidth = 0
    wwidth = 0
    vheight = 0
    wheight = 0
    wy = 0
    vy = 0
    base_trafo = None
    rec_funcs = None
    page = None
    layer = None

    def translate(self, wmf_doc, sk2_doc):
        self.wmf_doc = wmf_doc
        self.sk2_doc = sk2_doc
        self.wmf_mt = wmf_doc.model
        self.sk2_mt = sk2_doc.model
        self.sk2_mtds = sk2_doc.methods

        inch = wmf_const.META_DPI
        left = top = 0
        right = wmf_const.META_W
        bottom = wmf_const.META_H
        header = self.wmf_mt
        self.gdiobjects = []
        self.dcstack = []
        self.dc = DC_Data()

        if self.wmf_mt.is_placeable():
            sig, handle, left, top, right, bottom, inch, rsvd, checksum \
                = get_data(wmf_const.STRUCT_PLACEABLE, self.wmf_mt.chunk)

            val = 0
            for word in get_data('<10h', self.wmf_mt.chunk[:20]):
                val = val ^ word
            if val != checksum:
                LOG.warn('Incorrect WMF header checksum!')

            header = self.wmf_mt.childs[0]

        self.inch = inch
        self.bbox = (left, top, right, bottom)

        self.coef = uc2const.in_to_pt / self.inch
        self.wx = self.vx = left
        self.vwidth = self.wwidth = right - left
        self.vheight = self.wheight = bottom - top
        self.wy = self.vy = top

        self.base_trafo = [
            self.coef, 0, 0, -self.coef,
            - self.coef * self.vwidth / 2.0 - self.coef * self.vx,
            self.coef * self.vheight / 2.0 + self.coef * self.vy]
        self.update_trafo()

        self.rec_funcs = {
            wmf_const.META_SETWINDOWORG: self.tr_set_window_org,
            wmf_const.META_SETWINDOWEXT: self.tr_set_window_ext,
            wmf_const.META_SETPOLYFILLMODE: self.tr_set_polyfill_mode,
            wmf_const.META_SETBKMODE: self.tr_set_bg_mode,
            wmf_const.META_SETBKCOLOR: self.tr_set_bg_color,
            wmf_const.META_SAVEDC: self.tr_save_dc,
            wmf_const.META_RESTOREDC: self.tr_restore_dc,

            wmf_const.META_CREATEPENINDIRECT: self.tr_create_pen_in,
            wmf_const.META_CREATEBRUSHINDIRECT: self.tr_create_brush_in,
            wmf_const.META_CREATEFONTINDIRECT: self.tr_create_font_in,
            wmf_const.META_DIBCREATEPATTERNBRUSH: self.tr_dibcreate_pat_brush,
            wmf_const.META_STRETCHDIB: self.tr_stretch_dib,
            # ---------
            wmf_const.META_CREATEPALETTE: self.tr_create_noop,
            wmf_const.META_CREATEPATTERNBRUSH: self.tr_create_noop,
            wmf_const.META_CREATEREGION: self.tr_create_noop,
            # ---------
            wmf_const.META_SELECTOBJECT: self.tr_select_object,
            wmf_const.META_DELETEOBJECT: self.tr_delete_object,

            wmf_const.META_ELLIPSE: self.tr_ellipse,
            wmf_const.META_RECTANGLE: self.tr_rectangle,
            wmf_const.META_ROUNDRECT: self.tr_round_rectangle,
            wmf_const.META_POLYGON: self.tr_polygon,
            wmf_const.META_POLYPOLYGON: self.tr_polypolygon,
            wmf_const.META_POLYLINE: self.tr_polyline,
            wmf_const.META_ARC: self.tr_arc,
            wmf_const.META_CHORD: self.tr_chord,
            wmf_const.META_PIE: self.tr_pie,
            wmf_const.META_MOVETO: self.tr_moveto,
            wmf_const.META_LINETO: self.tr_lineto,

            wmf_const.META_TEXTOUT: self.tr_textout,
            wmf_const.META_EXTTEXTOUT: self.tr_exttextout,
            wmf_const.META_SETTEXTCOLOR: self.tr_set_text_color,
            wmf_const.META_SETTEXTALIGN: self.tr_set_text_align,
            wmf_const.META_SETTEXTCHAREXTRA: self.noop,
            wmf_const.META_SETTEXTJUSTIFICATION: self.noop,
        }

        self.translate_header(header)
        self.sk2_mt.do_update()

    def update_trafo(self):
        wt = [1.0, 0.0, 0.0, 1.0, -self.wx, -self.wy]
        vt = [1.0, 0.0, 0.0, 1.0, self.vx, self.vy]
        scale = [float(self.vwidth) / self.wwidth, 0.0, 0.0,
                 float(self.vheight) / self.wheight, 0.0, 0.0]
        tr = multiply_trafo(multiply_trafo(wt, scale), vt)
        self.set_trafo(multiply_trafo(tr, self.base_trafo))

    def get_size_pt(self, val):
        return val * self.coef

    def noop(self, *args):
        pass

    def get_style(self):
        style = deepcopy(self.dc.style)
        if style[0]:
            style[0][0] = self.dc.fill_rule
        if style[0] and style[0][1] == sk2const.FILL_PATTERN:
            alpha = 1.0
            if not self.dc.opacity:
                alpha = 0.0
            style[0][2][2][1][2] = alpha
        return style

    def set_fill_style(self, fill):
        self.dc.style[0] = fill

    def set_stroke_style(self, stroke):
        self.dc.style[1] = stroke

    def set_font_style(self, font):
        self.dc.font = font

    def get_curpoint(self):
        return [] + self.dc.curpoint

    def set_curpoint(self, point):
        self.dc.curpoint = [] + point

    def get_trafo(self):
        return [] + self.dc.trafo

    def set_trafo(self, trafo):
        self.dc.trafo = [] + trafo

    def get_encoding(self):
        return self.dc.font[-1]

    def get_text_style(self):
        sk2_style = [[], [], [], []]
        clr = [] + self.dc.text_color
        clr = [uc2const.COLOR_RGB, clr, 1.0, '', '']
        sk2_style[0] = [sk2const.FILL_EVENODD, sk2const.FILL_SOLID, clr]

        font = deepcopy(self.dc.font)
        faces = libpango.get_fonts()[1][font[0]]
        a, b = 'Regular', 'Normal'
        font_face = a if a in faces else b if b in faces else faces[0]

        sk2_style[2] = [font[0], font_face, font[1],
                        self.dc.text_align, [], True]
        tags = []
        if font[2]:
            tags.append('b')
        if font[3]:
            tags.append('i')
        if font[4]:
            tags.append('u')
        if font[5]:
            tags.append('s')
        return sk2_style, tags

    def add_gdiobject(self, obj):
        if None in self.gdiobjects:
            idx = self.gdiobjects.index(None)
            self.gdiobjects[idx] = obj
        else:
            self.gdiobjects.append(obj)

    def delete_gdiobject(self, idx):
        self.gdiobjects[idx] = None

    def translate_header(self, header):
        self.sk2_mt.doc_units = uc2const.UNIT_PT
        center = [0.0, 0.0]
        p = [self.wwidth, self.wheight]
        x0, y0 = apply_trafo_to_point(center, self.get_trafo())
        x1, y1 = apply_trafo_to_point(p, self.get_trafo())
        width = abs(x1 - x0)
        height = abs(y1 - y0)

        ornt = uc2const.PORTRAIT
        if width > height:
            ornt = uc2const.LANDSCAPE
        page_fmt = ['Custom', (width, height), ornt]

        pages_obj = self.sk2_mtds.get_pages_obj()
        pages_obj.page_format = page_fmt
        self.page = sk2_model.Page(pages_obj.config, pages_obj, 'WMF page')
        self.page.page_format = deepcopy(page_fmt)
        pages_obj.childs = [self.page, ]
        pages_obj.page_counter = 1

        self.layer = sk2_model.Layer(self.page.config, self.page)
        self.page.childs = [self.layer, ]

        for record in header.childs:
            try:
                self.translate_record(record)
            except Exception as e:
                LOG.error('ERREC-->%s', wmf_const.WMF_RECORD_NAMES[record.func])
                LOG.error('Record index %s', str(header.childs.index(record)))
                LOG.error('Error: %s', e)

    def translate_record(self, record):
        if record.func in self.rec_funcs:
            self.rec_funcs[record.func](record.chunk[6:])

    def tr_set_window_org(self, chunk):
        self.wy, self.wx = get_data('<hh', chunk)
        self.update_trafo()

    def tr_set_window_ext(self, chunk):
        self.wheight, self.wwidth = get_data('<hh', chunk)
        self.update_trafo()

    def tr_set_polyfill_mode(self, chunk):
        mode = get_data('<h', chunk[:2])[0]
        if mode in SK2_FILL_RULE:
            self.dc.fill_rule = SK2_FILL_RULE[mode]

    def tr_save_dc(self):
        self.dcstack.append(deepcopy(self.dc))

    def tr_restore_dc(self):
        if self.dcstack:
            self.dc = self.dcstack[-1]
            self.dcstack = self.dcstack[:-1]

    def tr_set_bg_mode(self, chunk):
        mode = get_data('<h', chunk[:2])[0]
        self.dc.opacity = mode == wmf_const.OPAQUE

    def tr_set_bg_color(self, chunk):
        self.dc.bgcolor = [val / 255.0 for val in get_data('<BBBx', chunk)]

    def tr_set_text_color(self, chunk):
        self.dc.text_color = [val / 255.0 for val in get_data('<BBBx', chunk)]

    def tr_set_text_align(self, chunk):
        mode = get_data('<h', chunk[:2])[0]

        self.dc.text_update_cp = True
        if not mode & 0x0001:
            self.dc.text_update_cp = False

        lower = mode & 0x0007
        self.dc.text_align = sk2const.TEXT_ALIGN_LEFT
        if lower & 0x0006 == wmf_const.TA_CENTER:
            self.dc.text_align = sk2const.TEXT_ALIGN_CENTER
        elif lower & wmf_const.TA_RIGHT:
            self.dc.text_align = sk2const.TEXT_ALIGN_RIGHT

        if mode & wmf_const.TA_BASELINE == wmf_const.TA_BASELINE:
            self.dc.text_valign = sk2const.TEXT_VALIGN_BASELINE
        elif mode & wmf_const.TA_BOTTOM:
            self.dc.text_valign = sk2const.TEXT_VALIGN_BOTTOM
        else:
            self.dc.text_valign = sk2const.TEXT_VALIGN_TOP

        self.dc.text_rtl = False
        if mode & wmf_const.TA_RTLREADING:
            self.dc.text_rtl = True

    def tr_select_object(self, chunk):
        obj = None
        idx = get_data('<h', chunk)[0]
        if idx < len(self.gdiobjects):
            obj = self.gdiobjects[idx]
        if obj:
            if obj[0] == 'stroke':
                self.set_stroke_style(deepcopy(obj[1]))
            elif obj[0] == 'fill':
                self.set_fill_style(deepcopy(obj[1]))
            elif obj[0] == 'font':
                self.set_font_style(deepcopy(obj[1]))

    def tr_delete_object(self, chunk):
        idx = get_data('<h', chunk)[0]
        if idx < len(self.gdiobjects):
            self.gdiobjects[idx] = None

    def tr_create_pen_in(self, chunk):
        stroke = []
        style, width = get_data('<hh', chunk[:4])
        r, g, b = get_data('<BBBx', chunk[6:10])
        if not style & 0x000F == wmf_const.PS_NULL:
            stroke_rule = sk2const.STROKE_MIDDLE
            color_vals = [r / 255.0, g / 255.0, b / 255.0]
            color = [uc2const.COLOR_RGB, color_vals, 1.0, '']
            stroke_width = abs(width * self.get_trafo()[0])
            if stroke_width < 1.0:
                stroke_width = 1.0

            stroke_linecap = sk2const.CAP_ROUND
            cap = style & 0x0F00
            for item in SK2_CAPS.keys():
                if cap == item:
                    stroke_linecap = SK2_CAPS[item]

            stroke_linejoin = sk2const.JOIN_MITER
            join = style & 0xF000
            for item in SK2_JOIN.keys():
                if join == item:
                    stroke_linejoin = SK2_JOIN[item]

            dashes = []
            dash = style & 0x000F
            for item in wmf_const.META_DASHES.keys():
                if dash == item:
                    dashes = [] + wmf_const.META_DASHES[item]

            stroke_miterlimit = 9.0

            stroke = [stroke_rule, stroke_width, color, dashes,
                      stroke_linecap, stroke_linejoin,
                      stroke_miterlimit, 0, 1, []]
        self.add_gdiobject(('stroke', stroke))

    def tr_create_brush_in(self, chunk):
        fill = []
        style, r, g, b, hatch = get_data('<hBBBxh', chunk)
        color_vals = [r / 255.0, g / 255.0, b / 255.0]
        color = [uc2const.COLOR_RGB, color_vals, 1.0, '']
        if style == wmf_const.BS_SOLID:
            fill = [sk2const.FILL_EVENODD, sk2const.FILL_SOLID, color]
        elif style == wmf_const.BS_HATCHED:
            if hatch not in wmf_hatches.WMF_HATCHES:
                hatch = wmf_const.HS_HORIZONTAL
            ptrn = wmf_hatches.WMF_HATCHES[hatch]
            ptrn_type = sk2const.PATTERN_IMG

            bgcolor = [uc2const.COLOR_RGB, [] + self.dc.bgcolor, 1.0, '']
            ptrn_style = [color, bgcolor]

            ptrn_trafo = [] + sk2const.NORMAL_TRAFO
            ptrn_transf = [] + sk2const.PATTERN_TRANSFORMS
            pattern = [ptrn_type, ptrn, ptrn_style, ptrn_trafo, ptrn_transf]
            fill = [sk2const.FILL_EVENODD, sk2const.FILL_PATTERN, pattern]
        self.add_gdiobject(('fill', fill))

    def tr_create_font_in(self, chunk):
        h = get_data('<h', chunk[:2])[0]
        esc = get_data('<h', chunk[4:6])[0]
        weight = get_data('<h', chunk[8:10])[0]
        size = round(abs(self.coef * h), 1) * .7
        size = 12.0 if not size else size
        size = 5.0 if size < 5.0 else size
        fl_b = weight >= 500
        fl_i, fl_u, fl_s, charset = get_data('<BBBB', chunk[10:14])
        fl_i = fl_i == wmf_const.META_TRUE
        fl_u = fl_u == wmf_const.META_TRUE
        fl_s = fl_s == wmf_const.META_TRUE

        if charset in wmf_const.META_CHARSETS:
            charset = wmf_const.META_CHARSETS[charset]
        else:
            charset = wmf_const.META_CHARSETS[wmf_const.ANSI_CHARSET]

        fontface = wmf_utils.parse_nt_string(chunk[18:]).encode('utf-8')
        font_family = 'Sans'
        if fontface in libpango.get_fonts()[0]:
            font_family = fontface

        font = (font_family, size, fl_b, fl_i, fl_u, fl_s, esc / 10.0, charset)
        self.add_gdiobject(('font', font))

    def tr_dibcreate_pat_brush(self, chunk):
        # style, colorusage = get_data('<hh', chunk[:4])
        imagestr = utils.dib_to_bmp(chunk[4:])
        bitsperpixel = get_data('<h', chunk[18:20])[0]

        ptrn, flag = libimg.read_pattern(imagestr)

        ptrn_type = sk2const.PATTERN_TRUECOLOR
        if flag or bitsperpixel == 1:
            ptrn_type = sk2const.PATTERN_IMG
        ptrn_style = [deepcopy(sk2const.RGB_BLACK),
                      deepcopy(sk2const.RGB_WHITE)]
        ptrn_trafo = [] + sk2const.NORMAL_TRAFO
        ptrn_transf = [] + sk2const.PATTERN_TRANSFORMS

        pattern = [ptrn_type, ptrn, ptrn_style, ptrn_trafo, ptrn_transf]
        fill = [sk2const.FILL_EVENODD, sk2const.FILL_PATTERN, pattern]
        self.add_gdiobject(('fill', fill))

    def tr_create_noop(self, chunk):
        self.add_gdiobject(('ignore', None))

    def tr_moveto(self, chunk):
        y, x = get_data('<hh', chunk)
        self.set_curpoint([x, y])

    def tr_lineto(self, chunk):
        y, x = get_data('<hh', chunk)
        p = [x, y]
        paths = [[self.get_curpoint(), [p, ], sk2const.CURVE_OPENED], ]
        self.set_curpoint([] + p)

        cfg = self.layer.config
        sk2_style = self.get_style()
        sk2_style[0] = []
        curve = sk2_model.Curve(cfg, self.layer, paths,
                                self.get_trafo(), sk2_style)
        self.layer.childs.append(curve)

    def tr_ellipse(self, chunk):
        bottom, right, top, left = get_data('<hhhh', chunk)
        left, top = apply_trafo_to_point([left, top], self.get_trafo())
        right, bottom = apply_trafo_to_point([right, bottom], self.get_trafo())

        cfg = self.layer.config
        sk2_style = self.get_style()
        rect = [left, top, right - left, bottom - top]
        ellipse = sk2_model.Circle(cfg, self.layer, rect, style=sk2_style)
        self.layer.childs.append(ellipse)

    def tr_arc(self, chunk, arc_type=sk2const.ARC_ARC):
        ye, xe, ys, xs, bottom, right, top, left = get_data('<hhhhhhhh',
                                                            chunk)
        left, top = apply_trafo_to_point([left, top], self.get_trafo())
        right, bottom = apply_trafo_to_point([right, bottom], self.get_trafo())
        xs, ys = apply_trafo_to_point([xs, ys], self.get_trafo())
        xe, ye = apply_trafo_to_point([xe, ye], self.get_trafo())

        if left != right and top != bottom:
            t = [(right - left) / 2, 0, 0, (bottom - top) / 2,
                 (right + left) / 2, (top + bottom) / 2]
            t = libgeom.invert_trafo(t)
            xs, ys = apply_trafo_to_point([xs, ys], t)
            xe, ye = apply_trafo_to_point([xe, ye], t)
            end_angle = libgeom.get_point_angle([xs, ys], [0.0, 0.0])
            start_angle = libgeom.get_point_angle([xe, ye], [0.0, 0.0])
        else:
            start_angle = end_angle = 0.0

        cfg = self.layer.config
        sk2_style = self.get_style()
        if arc_type == sk2const.ARC_ARC:
            sk2_style[0] = []
        rect = [left, top, right - left, bottom - top]
        ellipse = sk2_model.Circle(cfg, self.layer, rect, start_angle,
                                   end_angle, arc_type, sk2_style)
        self.layer.childs.append(ellipse)

    def tr_chord(self, chunk):
        self.tr_arc(chunk, sk2const.ARC_CHORD)

    def tr_pie(self, chunk):
        self.tr_arc(chunk, sk2const.ARC_PIE_SLICE)

    def tr_rectangle(self, chunk):
        bottom, right, top, left = get_data('<hhhh', chunk)
        left, top = apply_trafo_to_point([left, top], self.get_trafo())
        right, bottom = apply_trafo_to_point([right, bottom], self.get_trafo())

        cfg = self.layer.config
        sk2_style = self.get_style()
        rect = [left, top, right - left, bottom - top]
        rect = sk2_model.Rectangle(cfg, self.layer, rect, style=sk2_style)
        self.layer.childs.append(rect)

    def tr_round_rectangle(self, chunk):
        eh, ew, bottom, right, top, left = get_data('<hhhhhh', chunk)
        corners = 4 * [0.0, ]
        if eh and ew:
            coef = max(ew / abs(right - left), eh / abs(bottom - top))
            corners = 4 * [coef, ]
        left, top = apply_trafo_to_point([left, top], self.get_trafo())
        right, bottom = apply_trafo_to_point([right, bottom], self.get_trafo())

        cfg = self.layer.config
        sk2_style = self.get_style()
        rect = [left, top, right - left, bottom - top]
        rect = sk2_model.Rectangle(cfg, self.layer, rect,
                                   style=sk2_style, corners=corners)
        self.layer.childs.append(rect)

    def tr_polygon(self, chunk):
        pointnum = get_data('<h', chunk[:2])[0]
        points = []
        for i in range(pointnum):
            x, y = get_data('<hh', chunk[2 + i * 4:6 + i * 4])
            points.append([float(x), float(y)])
        if not points[0] == points[-1]:
            points.append([] + points[0])
        if len(points) < 3:
            return
        paths = [[points[0], points[1:], sk2const.CURVE_CLOSED], ]

        cfg = self.layer.config
        sk2_style = self.get_style()
        curve = sk2_model.Curve(cfg, self.layer, paths,
                                self.get_trafo(), sk2_style)
        self.layer.childs.append(curve)

    def tr_polypolygon(self, chunk):
        polygonnum = get_data('<H', chunk[:2])[0]
        pointnums = []
        pos = 2
        for i in range(polygonnum):
            pointnums.append(get_data('<h', chunk[pos:pos + 2])[0])
            pos += 2
        paths = []
        for pointnum in pointnums:
            points = []
            for i in range(pointnum):
                x, y = get_data('<hh', chunk[pos:4 + pos])
                points.append([float(x), float(y)])
                pos += 4
            if not points[0] == points[-1]:
                points.append([] + points[0])
            paths.append([points[0], points[1:], sk2const.CURVE_CLOSED])
        if not paths:
            return

        cfg = self.layer.config
        sk2_style = self.get_style()
        curve = sk2_model.Curve(cfg, self.layer, paths,
                                self.get_trafo(), sk2_style)
        self.layer.childs.append(curve)

    def tr_polyline(self, chunk):
        pointnum = get_data('<h', chunk[:2])[0]
        points = []
        for i in range(pointnum):
            x, y = get_data('<hh', chunk[2 + i * 4:6 + i * 4])
            points.append([float(x), float(y)])
        if len(points) < 2:
            return
        paths = [[points[0], points[1:], sk2const.CURVE_OPENED], ]

        cfg = self.layer.config
        sk2_style = self.get_style()
        sk2_style[0] = []
        curve = sk2_model.Curve(cfg, self.layer, paths,
                                self.get_trafo(), sk2_style)
        self.layer.childs.append(curve)

    def tr_textout(self, chunk):
        length = get_data('<h', chunk[:2])[0]

        encoding = self.get_encoding()
        txt = chunk[8:8 + length].decode(encoding)
        txt_length = len(txt)
        txt = txt.encode('utf-8')
        y, x, = get_data('<hhhh', chunk[8 + length:16 + length])
        p = apply_trafo_to_point([x, y], self.get_trafo())

        cfg = self.layer.config
        sk2_style, tags = self.get_text_style()
        markup = [[tags, (0, txt_length)]]
        tr = [] + libgeom.NORMAL_TRAFO
        text = sk2_model.Text(cfg, self.layer, p, txt, -1, tr, sk2_style)
        text.markup = markup
        rect = None
        if self.dc.opacity:
            bg_style = [[], [], [], []]
            clr = [] + self.dc.bgcolor
            clr = [uc2const.COLOR_RGB, clr, 1.0, '', '']
            bg_style[0] = [sk2const.FILL_EVENODD, sk2const.FILL_SOLID, clr]
            text.update()
            bbox = [] + text.cache_bbox
            rect = bbox[:2] + [bbox[2] - bbox[0], bbox[3] - bbox[1]]
            rect = sk2_model.Rectangle(cfg, self.layer, rect, style=bg_style)
            self.layer.childs.append(rect)
        if self.dc.font[-2]:
            tr = libgeom.trafo_rotate_grad(self.dc.font[-2], p[0], p[1])
            text.trafo = libgeom.multiply_trafo(text.trafo, tr)
            if self.dc.opacity:
                rect.trafo = libgeom.multiply_trafo(rect.trafo, tr)
        self.layer.childs.append(text)

    def tr_exttextout(self, chunk):
        y, x, length = get_data('<hhh', chunk[:6])
        dl = 0
        if length % 2:
            length += 1
            dl += 1
        p = apply_trafo_to_point([x, y], self.get_trafo())

        encoding = self.get_encoding()
        pos = 16 if not len(chunk) - 8 == length else 8
        txt = chunk[pos:pos + length - dl].decode(encoding)
        txt_length = len(txt)
        txt = txt.encode('utf-8')

        cfg = self.layer.config
        sk2_style, tags = self.get_text_style()
        markup = [[tags, (0, txt_length)]]
        tr = [] + libgeom.NORMAL_TRAFO

        text = sk2_model.Text(cfg, self.layer, p, txt, -1, tr, sk2_style)
        text.markup = markup
        rect = None
        if self.dc.opacity:
            bg_style = [[], [], [], []]
            clr = [] + self.dc.bgcolor
            clr = [uc2const.COLOR_RGB, clr, 1.0, '', '']
            bg_style[0] = [sk2const.FILL_EVENODD, sk2const.FILL_SOLID, clr]
            text.update()
            bbox = [] + text.cache_bbox
            rect = bbox[:2] + [bbox[2] - bbox[0], bbox[3] - bbox[1]]
            rect = sk2_model.Rectangle(cfg, self.layer, rect, style=bg_style)
            rect.trafo = tr
            self.layer.childs.append(rect)
        if self.dc.font[-2]:
            tr = libgeom.trafo_rotate_grad(self.dc.font[-2], p[0], p[1])
            text.trafo = libgeom.multiply_trafo(text.trafo, tr)
            if self.dc.opacity:
                rect.trafo = libgeom.multiply_trafo(rect.trafo, tr)
        self.layer.childs.append(text)

    def _draw_point(self, point):
        style = [[], [], [], []]
        clr = [] + sk2const.RGB_BLACK
        clr[1] = [1.0, 0.0, 0.0]
        style[0] = [sk2const.FILL_EVENODD, sk2const.FILL_SOLID, clr]
        rect = point + [3.0, 3.0]
        rect = sk2_model.Rectangle(self.layer.config, self.layer,
                                   rect, style=style)
        self.layer.childs.append(rect)

    def tr_stretch_dib(self, chunk):
        src_h, src_w, = get_data('<hh', chunk[6:10])
        dst_h, dst_w, dst_y, dst_x = get_data('<hhhh', chunk[14:22])
        imagestr = utils.dib_to_bmp(chunk[22:])

        tr = self.get_trafo()
        p0 = apply_trafo_to_point([dst_x, dst_y], tr)
        p1 = apply_trafo_to_point([dst_w + dst_x, dst_h + dst_y], tr)
        w = abs(p1[0] - p0[0])
        h = abs(p1[1] - p0[1])
        trafo = [w / src_w, 0.0, 0.0, h / src_h, p0[0], p0[1] - h]

        pixmap = sk2_model.Pixmap(self.layer.config)
        pixmap.handler.load_from_fileptr(self.sk2_doc.cms, StringIO(imagestr))
        pixmap.trafo = trafo
        self.layer.childs.append(pixmap)


INCH = 1440


class SK2_to_WMF_Translator(object):
    wmf_doc = None
    sk2_doc = None
    sk2_mt = None
    sk2_mtds = None
    wmf_records = None
    wmf_objs = None
    latest_objs = None
    inch = 0
    scale = 1.0
    trafo = None
    bbox = None

    def translate(self, sk2_doc, wmf_doc):
        self.wmf_doc = wmf_doc
        self.sk2_doc = sk2_doc
        self.sk2_mt = sk2_doc.model
        self.sk2_mtds = sk2_doc.methods
        self.wmf_records = []
        self.wmf_objs = []
        self.latest_objs = []

        page = self.sk2_mtds.get_page()
        left, bottom, right, top = self.sk2_mtds.count_bbox(page.childs)
        width = right - left
        height = top - bottom

        self.inch = INCH
        x = max(width, height)
        if x * (INCH / 72.0) > 0xFFFF / 2:
            self.inch = 0xFFFF / (2 * x)
        self.scale = coef = self.inch / 72.0
        self.trafo = [coef, 0, 0, -coef, -coef * left, coef * top]
        self.bbox = self.point4wmf([left, bottom]) + self.point4wmf(
            [right, top])

        self.add(wmf_model.set_window_org(self.bbox[0], self.bbox[3]))
        self.add(wmf_model.set_window_ext(self.bbox[2], self.bbox[1]))
        self.add(wmf_model.set_bkmode(wmf_const.TRANSPARENT))
        self.add(wmf_model.set_bkcolor([1.0, ] * 3))
        self.add(wmf_model.set_rop2(wmf_const.R2_COPYPEN))
        self.add(wmf_model.set_polyfillmode(wmf_const.ALTERNATE))

        for layer in page.childs:
            if self.sk2_mtds.is_layer_visible(layer):
                self.translate_objs(layer.childs)

        self.add(wmf_model.get_eof_rec())

        filesize, maxrecord = self.count_record_size()
        filesize += 18
        numobjs = len(self.wmf_objs)
        header = wmf_model.get_wmf_header(filesize, numobjs, maxrecord)
        header.childs = self.wmf_records
        placeable = wmf_model.get_placeble_header(self.bbox, self.inch)
        placeable.childs = [header, ]
        self.wmf_doc.model = placeable

    def point4wmf(self, point):
        return rndpoint(apply_trafo_to_point(point, self.trafo))

    def add(self, record):
        self.wmf_records.append(record)

    def add_obj(self, obj_record):
        self.add(obj_record)
        indx = len(self.wmf_objs)
        self.wmf_objs.append(obj_record)
        self.latest_objs.append(indx)
        self.add(wmf_model.select_obj(indx))

    def delete_obj(self, indx):
        self.add(wmf_model.delete_obj(indx))
        if indx in self.latest_objs:
            self.latest_objs.remove(indx)

    def delete_latest_objs(self):
        for item in [] + self.latest_objs:
            self.delete_obj(item)

    def count_record_size(self):
        total_size = 0
        maxrecord = 0
        for item in self.wmf_records:
            total_size += len(item.chunk)
            maxrecord = max(maxrecord, len(item.chunk))
        return total_size, maxrecord

    def translate_objs(self, objs):
        for obj in objs:
            if obj.is_primitive:
                self.translate_primitive(obj)
            elif obj.is_layer:
                if obj.properties[0]:
                    self.translate_group(obj)
            elif obj.is_pixmap:
                self.translate_pixmap(obj)
            else:
                self.translate_group(obj)

    def translate_group(self, obj):
        self.translate_objs(obj.childs)

    def translate_primitive(self, obj):
        curve = obj.to_curve()
        if curve.is_group:
            self.translate_group(curve)
            return
        curve.update()
        trafo = libgeom.multiply_trafo(curve.trafo, self.trafo)
        paths = libgeom.apply_trafo_to_paths(curve.paths, trafo)
        paths = libgeom.flat_paths(paths)
        self.translate_paths(obj.style, paths)

    def translate_paths(self, style, paths):
        if style[1] and style[1][7]:
            self.translate_stroke(style, paths)
        if style[0]:
            self.translate_fill(style, paths)
        if style[1] and not style[1][7]:
            self.translate_stroke(style, paths)

    def translate_stroke(self, style, paths):

        self.delete_latest_objs()

    def translate_fill(self, style, paths):

        self.delete_latest_objs()

    def translate_pixmap(self, obj):
        pass
