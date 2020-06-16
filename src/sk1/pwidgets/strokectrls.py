# -*- coding: utf-8 -*-
#
#  Copyright (C) 2015 by Ihor E. Novikov
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
from copy import deepcopy

import wal
from sk1 import _
from sk1.resources import icons
from uc2 import sk2const
from uc2.formats.sk2 import arrows

DASH_LIST = [
    # solid line
    [],
    # longer and shorter dashes
    [5, 5],
    [4, 4],
    [3, 3],
    [2, 2],
    # dotted
    [1, 1],
    [0.1, 1.0],
    # dash short gap
    [5, 1],
    # dash-dot
    [5, 1, 1, 1],
    # dash-dot-dot
    [5, 1, 1, 1, 1, 1],
    # dash-dot-dot-dot
    [5, 1, 1, 1, 1, 1, 1, 1],
]

DASH_BITMAP_SIZE = (200, 17)
DASH_LINE_WIDTH = 3
DASH_BITMAPS = []


def generate_dash_bitmap(dash=None):
    if not dash:
        dash = []
    w, h = DASH_BITMAP_SIZE
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surface)
    y = round(h / 2.0)

    ctx.set_source_rgba(0.0, 0.0, 0.0, 1.0)
    ctx.set_line_width(DASH_LINE_WIDTH)
    cdash = []
    for item in dash:
        cdash.append(item * DASH_LINE_WIDTH)
    ctx.set_dash(cdash)
    ctx.move_to(0, y)
    ctx.line_to(w, y)
    ctx.stroke()

    return wal.copy_surface_to_bitmap(surface)


class DashChoice(wal.BitmapChoice):
    dash_list = []

    def __init__(self, parent, dash=None):
        if not dash:
            dash = []
        self.dash_list = []
        if not DASH_BITMAPS:
            for item in DASH_LIST:
                DASH_BITMAPS.append(generate_dash_bitmap(item))
        self.dash_list += DASH_LIST
        custom_dash = []
        if dash not in DASH_LIST:
            custom_dash.append(generate_dash_bitmap(dash))
            self.dash_list.append(dash)
        bitmaps = DASH_BITMAPS + custom_dash
        wal.BitmapChoice.__init__(self, parent, 0, bitmaps)
        self.set_active(self.dash_list.index(dash))

    def get_dash(self):
        return deepcopy(self.dash_list[self.get_active()])

    def set_dash(self, dash):
        if len(self.dash_list) > len(DASH_LIST):
            self.dash_list = self.dash_list[:-1]
        custom_dash = []
        if dash not in DASH_LIST:
            custom_dash.append(generate_dash_bitmap(dash))
            self.dash_list.append(dash)
        bitmaps = DASH_BITMAPS + custom_dash
        self.set_bitmaps(bitmaps)
        self.set_active(self.dash_list.index(dash))


ARROW_BITMAP_SIZE = (120, 25)
ARROW_LINE_WIDTH = 3
ARROW_START_BITMAPS = []
ARROW_END_BITMAPS = []


def generate_arrow_bitmap(arrow=0, end=False):
    w, h = ARROW_BITMAP_SIZE
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surface)
    y = round(h / 2.0)
    x = w / 2

    ctx.set_source_rgba(0.0, 0.0, 0.0, 1.0)
    ctx.set_line_width(ARROW_LINE_WIDTH)
    x = x - 15 if end else x - 15
    ctx.move_to(x, y)
    x2 = w if end else 0
    ctx.line_to(x2, y)
    ctx.stroke()

    if arrow:
        ctx.new_path()
        trafo = [-4, 0.0, 0.0, 4, x, y] if end else [4, 0.0, 0.0, 4, x, y]
        ctx.append_path(arrows.get_arrow_cpath(arrow-1, trafo))
        ctx.fill()

    return wal.copy_surface_to_bitmap(surface)


class ArrowChoice(wal.BitmapChoice):
    arrow_list = []

    def __init__(self, parent, arrow=None, end=False):
        bitmaps = ARROW_END_BITMAPS if end else ARROW_START_BITMAPS
        if not bitmaps:
            for indx in range(len(arrows.ARROWS) + 1):
                bitmaps.append(generate_arrow_bitmap(indx, end))
        wal.BitmapChoice.__init__(self, parent, 0, bitmaps)
        self.set_active(arrow + 1 if isinstance(arrow, int) else 0)

    def get_arrow(self):
        val = self.get_active()
        return val - 1 if val else []

    def set_arrow(self, arrow):
        arrow = 0 if arrow == [] else arrow + 1
        self.set_active(arrow)


CAP_MODES = [sk2const.CAP_BUTT, sk2const.CAP_ROUND, sk2const.CAP_SQUARE]

CAP_MODE_NAMES = {
    sk2const.CAP_BUTT: _('Line exactly at the point'),
    sk2const.CAP_ROUND: _('Round ending'),
    sk2const.CAP_SQUARE: _('Squared ending'),
}

CAP_MODE_ICONS = {
    sk2const.CAP_BUTT: icons.PD_CAP_BUTT,
    sk2const.CAP_ROUND: icons.PD_CAP_ROUND,
    sk2const.CAP_SQUARE: icons.PD_CAP_SQUARE,
}


class CapChoice(wal.VToggleKeeper):
    def __init__(self, parent, val=sk2const.CAP_BUTT):
        wal.VToggleKeeper.__init__(self, parent, CAP_MODES, CAP_MODE_ICONS,
                                   CAP_MODE_NAMES)
        self.set_cap(val)

    def set_cap(self, val):
        self.set_mode(val)

    def get_cap(self): return self.get_mode()


JOIN_MODES = [sk2const.JOIN_MITER, sk2const.JOIN_ROUND, sk2const.JOIN_BEVEL]

JOIN_MODE_NAMES = {
    sk2const.JOIN_BEVEL: _('Cut-off join'),
    sk2const.JOIN_MITER: _('Sharp (angled) corner'),
    sk2const.JOIN_ROUND: _('Rounded join'),
}

JOIN_MODE_ICONS = {
    sk2const.JOIN_BEVEL: icons.PD_JOIN_BEVEL,
    sk2const.JOIN_MITER: icons.PD_JOIN_MITER,
    sk2const.JOIN_ROUND: icons.PD_JOIN_ROUND,
}


class JoinChoice(wal.VToggleKeeper):
    def __init__(self, parent, val=sk2const.JOIN_BEVEL):
        wal.VToggleKeeper.__init__(self, parent, JOIN_MODES, JOIN_MODE_ICONS,
                                   JOIN_MODE_NAMES)
        self.set_join(val)

    def set_join(self, val):
        self.set_mode(val)

    def get_join(self): return self.get_mode()
