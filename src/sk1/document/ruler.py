# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013-2018 by Igor E. Novikov
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

import cairo
import math
import os

from sk1 import config, modes, events
from sk1.pwidgets import Painter
from uc2 import uc2const, cms, sk2const
from uc2.utils import fsutils

HFONT = {}
VFONT = {}


def load_font(color=(0, 0, 0)):
    fntdir = 'ruler-font%dpx' % config.ruler_font_size
    fntdir = os.path.join(config.resource_dir, 'fonts', fntdir)

    def get_colored_surface(file_name, color):
        file_name = fsutils.get_sys_path(file_name)
        surface = cairo.ImageSurface.create_from_png(file_name)
        w, h = surface.get_width(), surface.get_height()
        res = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        cr = cairo.Context(res)
        cr.set_source_rgb(*color)
        cr.mask_surface(surface, 0, 0)
        cr.fill()
        return w, res

    for char in '.,-0123456789':
        file_name = 'hdot.png' if char in '.,' else 'h%s.png' % char
        file_name = os.path.join(fntdir, file_name)
        HFONT[char] = get_colored_surface(file_name, color)

        file_name = 'vdot.png' if char in '.,' else 'v%s.png' % char
        file_name = os.path.join(fntdir, file_name)
        VFONT[char] = get_colored_surface(file_name, color)


CAIRO_WHITE = [1.0, 1.0, 1.0]
CAIRO_BLACK = [0.0, 0.0, 0.0]

CORNER = {
    sk2const.DOC_ORIGIN_CENTER: ((8, 1, 8, 6), (8, 11, 8, 16), (8, 8, 8, 9),
                                 (1, 8, 6, 8), (11, 8, 16, 8),),
    sk2const.DOC_ORIGIN_LL: ((3, 1, 3, 16), (2, 2, 5, 2), (1, 13, 16, 13),
                             (14, 12, 14, 15), (5, 11, 6, 10), (7, 9, 8, 8),
                             (9, 7, 10, 6), (11, 5, 12, 4),  (13, 3, 14, 2)),
    sk2const.DOC_ORIGIN_LU: ((3, 1, 3, 16), (2, 14, 5, 14), (1, 3, 16, 3),
                             (14, 2, 14, 5), (5, 5, 6, 6), (7, 7, 8, 8),
                             (9, 9, 10, 10), (11, 11, 12, 12), (13, 13, 14, 14))
}


class RulerCorner(Painter):
    presenter = None
    eventloop = None
    origin = sk2const.DOC_ORIGIN_LL
    mtds = None

    def __init__(self, presenter):
        self.presenter = presenter
        self.eventloop = presenter.eventloop
        self.dc = self.presenter.app.mw.mdi.corner
        Painter.__init__(self)
        self.eventloop.connect(self.eventloop.DOC_MODIFIED, self.changes)
        self.changes()

    def changes(self):
        if not self.origin == self.presenter.model.doc_origin:
            self.origin = self.presenter.model.doc_origin
            self.dc.refresh()

    def mouse_left_up(self, *args):
        origin = self.presenter.model.doc_origin
        if origin < sk2const.ORIGINS[-1]:
            origin += 1
        else:
            origin = sk2const.ORIGINS[0]
        self.presenter.api.set_doc_origin(origin)

    def paint(self):
        w, h = self.dc.get_size()
        fg = cms.val_255(config.ruler_fg)
        bg = cms.val_255(config.ruler_bg)
        self.dc.set_stroke(None)
        self.dc.set_fill(bg)
        self.dc.draw_rect(0, 0, w, h)
        self.dc.draw_linear_gradient((0, h - 1, w * 2, 1), bg, fg)
        self.dc.draw_linear_gradient((w - 1, 0, 1, h * 2), bg, fg, True)
        self.dc.set_stroke(fg)
        shift = (w - 19) / 2 + 1
        for x0, y0, x1, y1 in CORNER[self.origin]:
            self.dc.draw_line(x0 + shift, y0 + shift, x1 + shift, y1 + shift)


class Ruler(Painter):
    presenter = None
    eventloop = None
    vertical = False

    init_flag = False
    draw_guide = False
    surface = None
    ctx = None
    default_cursor = None
    guide_cursor = None
    mouse_captured = False
    width = 0
    height = 0
    pointer = []

    def __init__(self, presenter, vertical=True):
        self.presenter = presenter
        self.eventloop = presenter.eventloop
        self.vertical = vertical
        Painter.__init__(self)
        mdi = self.presenter.app.mw.mdi
        self.dc = mdi.vruler if vertical else mdi.hruler

        if not VFONT:
            load_font(config.ruler_fg)
        self.default_cursor = self.dc.get_cursor()
        if not self.vertical:
            self.guide_cursor = self.presenter.app.cursors[modes.HGUIDE_MODE]
        else:
            self.guide_cursor = self.presenter.app.cursors[modes.VGUIDE_MODE]
        self.eventloop.connect(self.eventloop.VIEW_CHANGED, self.dc.refresh)
        events.connect(events.CONFIG_MODIFIED, self.check_config)

    def check_config(self, *args):
        if args[0] in ('ruler_font_size', 'ruler_fg'):
            load_font(config.ruler_fg)

    def calc_ruler(self):
        canvas = self.presenter.canvas
        w, h = self.presenter.get_page_size()
        x = y = 0
        udx = udy = uc2const.unit_dict[self.presenter.model.doc_units]
        origin = self.presenter.model.doc_origin
        if origin == sk2const.DOC_ORIGIN_LL:
            x0, y0 = canvas.point_doc_to_win([-w / 2.0 + x, -h / 2.0 + y])
        elif origin == sk2const.DOC_ORIGIN_LU:
            x0, y0 = canvas.point_doc_to_win([-w / 2.0 + x, h / 2.0 + y])
        else:
            x0, y0 = canvas.point_doc_to_win([x, y])
        dx = udx * canvas.zoom
        dy = udy * canvas.zoom
        sdist = config.snap_distance

        i = 0.0
        while dx < sdist + 3:
            i = i + 0.5
            dx = dx * 10.0 * i
        if dx / 2.0 > sdist + 3 and dx / 2.0 > udx * canvas.zoom:
            dx = dx / 2.0

        i = 0.0
        while dy < sdist + 3:
            i = i + 0.5
            dy = dy * 10.0 * i
        if dy / 2.0 > sdist + 3 and dy / 2.0 > udy * canvas.zoom:
            dy = dy / 2.0

        sx = (x0 / dx - math.floor(x0 / dx)) * dx
        sy = (y0 / dy - math.floor(y0 / dy)) * dy
        return x0, y0, dx, dy, sx, sy

    def get_ticks(self):
        canvas = self.presenter.canvas
        pw, ph = self.presenter.get_page_size()
        origin = self.presenter.model.doc_origin
        unit = uc2const.unit_dict[self.presenter.model.doc_units]
        w, h = self.dc.get_size()
        x0, y0, dx, dy, sx, sy = self.calc_ruler()
        small_ticks = []
        text_ticks = []

        if not self.vertical:
            i = -1
            pos = 0
            while pos < w:
                pos = sx + i * dx
                small_ticks.append(sx + i * dx)
                if dx > 10:
                    small_ticks.append(pos + dx * .5)
                i += 1

            coef = round(50.0 / dx) or 1.0
            dxt = dx * coef
            sxt = (x0 / dxt - math.floor(x0 / dxt)) * dxt

            unit_dx = dxt / (unit * canvas.zoom)
            float_flag = True if unit_dx < 1.0 else False

            i = -1
            pos = 0
            shift = 0.0 if origin == sk2const.DOC_ORIGIN_CENTER else pw / 2.0
            while pos < w:
                pos = sxt + i * dxt
                doc_pos = canvas.point_win_to_doc((pos, 0))[0] + shift
                doc_pos *= uc2const.point_dict[self.presenter.model.doc_units]
                if float_flag:
                    txt = str(round(doc_pos, 4)) if doc_pos else '0'
                else:
                    txt = str(int(round(doc_pos)))
                text_ticks.append((sxt + i * dxt, txt))
                i += 1

        else:
            i = -1
            pos = 0
            while pos < h:
                pos = sy + i * dy
                small_ticks.append(sy + i * dy)
                if dy > 10:
                    small_ticks.append(pos + dy * .5)
                i += 1

            coef = round(50.0 / dy) or 1.0
            dyt = dy * coef
            syt = (y0 / dyt - math.floor(y0 / dyt)) * dyt

            unit_dy = dyt / (unit * canvas.zoom)
            float_flag = True if unit_dy < 1.0 else False

            i = -1
            pos = 0
            shift = 0.0 if origin == sk2const.DOC_ORIGIN_CENTER else ph / 2.0
            shift = -shift if origin == sk2const.DOC_ORIGIN_LU else shift

            while pos < h:
                pos = syt + i * dyt
                doc_pos = canvas.point_win_to_doc((0, pos))[1] + shift
                if origin == sk2const.DOC_ORIGIN_LU:
                    doc_pos *= -1.0
                doc_pos *= uc2const.point_dict[self.presenter.model.doc_units]
                if float_flag:
                    txt = str(round(doc_pos, 4)) if doc_pos else '0'
                else:
                    txt = str(int(round(doc_pos)))
                text_ticks.append((syt + i * dyt, txt))
                i += 1
        return small_ticks, text_ticks

    def paint(self):
        if self.presenter is None:
            return
        w, h = self.dc.get_size()
        fmt = cairo.FORMAT_RGB24
        if self.surface is None or self.width != w or self.height != h:
            self.surface = cairo.ImageSurface(fmt, w, h)
            self.width, self.height = w, h
        self.ctx = cairo.Context(self.surface)
        self.ctx.set_matrix(cairo.Matrix(1.0, 0.0, 0.0, 1.0, 0.0, 0.0))
        self.ctx.set_source_rgb(*config.ruler_bg)
        self.ctx.paint()
        self.ctx.set_antialias(cairo.ANTIALIAS_NONE)
        self.ctx.set_line_width(1.0)
        self.ctx.set_dash([])
        self.ctx.set_source_rgb(*config.ruler_fg)
        if self.vertical:
            self.vrender(w, h)
        else:
            self.hrender(w, h)
        self.dc.draw_surface(self.surface, 0, 0)

    def hrender(self, w, h):
        self.ctx.move_to(0, h)
        self.ctx.line_to(w, h)

        small_ticks, text_ticks = self.get_ticks()
        for item in small_ticks:
            self.ctx.move_to(item, h - config.ruler_small_tick)
            self.ctx.line_to(item, h - 1)

        for pos, txt in text_ticks:
            self.ctx.move_to(pos, h - config.ruler_large_tick)
            self.ctx.line_to(pos, h - 1)

        self.ctx.stroke()

        vshift = config.ruler_text_vshift
        hshift = config.ruler_text_hshift
        for pos, txt in text_ticks:
            for character in txt:
                data = HFONT[character]
                position = int(pos) + hshift
                self.ctx.set_source_surface(data[1], position, vshift)
                self.ctx.paint()
                pos += data[0]

    def vrender(self, w, h):
        self.ctx.move_to(w, 0)
        self.ctx.line_to(w, h)

        small_ticks, text_ticks = self.get_ticks()
        for item in small_ticks:
            self.ctx.move_to(w - config.ruler_small_tick, item)
            self.ctx.line_to(w - 1, item)

        for item, txt in text_ticks:
            self.ctx.move_to(w - config.ruler_large_tick, item)
            self.ctx.line_to(w - 1, item)

        self.ctx.stroke()

        vshift = config.ruler_text_vshift
        hshift = config.ruler_text_hshift
        for pos, txt in text_ticks:
            for character in txt:
                data = VFONT[character]
                position = int(pos) - data[0] - hshift
                self.ctx.set_source_surface(data[1], vshift, position)
                self.ctx.paint()
                pos -= data[0]

    # ------ Guides creation
    def set_ruler_cursor(self, mode=False):
        self.dc.set_cursor(self.guide_cursor if mode else self.default_cursor)

    def capture_lost(self):
        self.dc.release_mouse()
        self.set_ruler_cursor()

    def mouse_left_down(self, point):
        if not self.presenter.methods.is_guide_editable():
            return
        self.width, self.height = (float(item) for item in self.dc.get_size())
        self.draw_guide = True
        self.set_ruler_cursor(True)
        self.dc.capture_mouse()
        canvas = self.presenter.canvas
        canvas.timer.start()
        canvas.set_temp_mode(modes.GUIDE_MODE)
        if not self.vertical:
            canvas.controller.mode = modes.HGUIDE_MODE
        else:
            canvas.controller.mode = modes.VGUIDE_MODE
        canvas.set_canvas_cursor(canvas.controller.mode)

    def mouse_left_up(self, point):
        if not self.presenter.methods.is_guide_editable():
            return
        self.pointer = point
        self.dc.release_mouse()
        if not self.vertical:
            y_win = self.pointer[1] - self.height
            if y_win > 0.0:
                p = [self.pointer[0], y_win]
                p, p_doc = self.presenter.snap.snap_point(p, snap_x=False)[1:]
                guides = [[p_doc[1], uc2const.HORIZONTAL], ]
                self.presenter.api.create_guides(guides)
        else:
            x_win = self.pointer[0] - self.width
            if x_win > 0.0:
                p = [x_win, self.pointer[1]]
                p, p_doc = self.presenter.snap.snap_point(p, snap_y=False)[1:]
                guides = [[p_doc[0], uc2const.VERTICAL], ]
                self.presenter.api.create_guides(guides)
        self.set_ruler_cursor()
        self.presenter.canvas.timer.stop()
        self.presenter.canvas.restore_mode()
        self.draw_guide = False
        self.pointer = []
        self.presenter.canvas.dragged_guide = ()
        self.presenter.canvas.force_redraw()

    def mouse_move(self, point):
        if self.draw_guide:
            self.pointer = point
            self.repaint_guide()

    def repaint_guide(self):
        p = 0
        if self.draw_guide and self.pointer:
            if not self.vertical:
                y_win = self.pointer[1] - self.height
                p = [self.pointer[0], y_win]
                p = self.presenter.snap.snap_point(p, snap_x=False)[1]
            else:
                x_win = self.pointer[0] - self.width
                p = [x_win, self.pointer[1]]
                p = self.presenter.snap.snap_point(p, snap_y=False)[1]
        self.presenter.canvas.controller.end = p
