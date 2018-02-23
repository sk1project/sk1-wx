# -*- coding: utf-8 -*-
#
#  Copyright (C) 2018 by Igor E. Novikov
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
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import wx

import const
from basic import VPanel, SensitiveCanvas
from renderer import get_text_size

TAB_WIDTH = 25
TAB_MARGIN = 1
TAB_PADDING = 5
TAB_SIZE = 150
INDICATOR_SIZE = 8


class VTabPainter(object):
    def __init__(self, panel):
        self.panel = panel
        self.border_color = const.UI_COLORS['hover_solid_border']
        self.bg_color = const.UI_COLORS['bg']
        self.fg_color = const.UI_COLORS['fg']


PAINTERS = {
    0: VTabPainter,
}

class VTabs(VPanel, SensitiveCanvas):
    painter = None
    doc_tabs = []
    draw_top = True
    custom_bg = None
    pos_min = 0
    pos_max = 0

    def __init__(self, parent, painter=0):
        VPanel.__init__(self, parent)
        SensitiveCanvas.__init__(self, check_move=True)
        self.set_double_buffered()
        self.pack((TAB_WIDTH, TAB_PADDING))
        self.set_painter(painter if painter in PAINTERS else 0)

    def set_painter(self, painter):
        self.painter = PAINTERS[painter](self)
        self.refresh()