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

from copy import deepcopy

import wal
from sk1 import _
from sk1.resources import icons, get_icon

AUTO_MODE = 0
NORMAL_MODE = 1
LARGE_MODE = 2
LIST_MODE = 3

MODE_ICON = {
    AUTO_MODE: icons.PD_PALETTE_AUTO,
    NORMAL_MODE: icons.PD_PALETTE_NORMAL,
    LARGE_MODE: icons.PD_PALETTE_LARGE,
    LIST_MODE: icons.PD_PALETTE_LIST,
}

MODE_NAME = {
    AUTO_MODE: _('Auto mode'),
    NORMAL_MODE: _('Small cells'),
    LARGE_MODE: _('Large cells'),
    LIST_MODE: _('List view'),
}

PREVIEW_MODES = [AUTO_MODE, NORMAL_MODE, LARGE_MODE, LIST_MODE]


class ScrolledPalette(wal.ScrolledCanvas, wal.SensitiveDrawableWidget):
    mode = AUTO_MODE
    width = 10
    height = 10
    cell_width = 16
    cell_height = 16
    cell_in_line = 10
    colors = None
    sb_width = 1
    selected_index = None
    large_sel = None
    small_sel = None
    callback = None

    def __init__(self, parent, cms, border=False, onclick=None):
        self.cms = cms
        self.parent = parent
        self.callback = onclick
        wal.ScrolledCanvas.__init__(self, parent, border)
        wal.SensitiveDrawableWidget.__init__(self, True)
        sb = wal.ScrollBar(self)
        self.sb_width = sb.get_size()[0]
        sb.destroy()
        self.large_sel = get_icon(icons.PD_LARGE_SEL_PALETTE, size=wal.DEF_SIZE)
        self.small_sel = get_icon(icons.PD_SMALL_SEL_PALETTE, size=wal.DEF_SIZE)
        self.width = (self.cell_width - 1) * self.cell_in_line
        self.width += 3 + self.sb_width
        self.set_size((self.width, -1))
        self.set_bg(wal.UI_COLORS['list_bg'])

    def mouse_move(self, point):
        if self.colors:
            index = self.get_color_index_in_point(point)
            self.set_tooltip()
            if index is not None and self.colors[index][3]:
                self.set_tooltip(self.colors[index][3])

    def mouse_left_up(self, point):
        self.selected_index = self.get_color_index_in_point(point)
        self.refresh()
        if self.callback:
            self.callback()

    def _mouse_wheel(self, event):
        event.Skip()

    def get_color_index_in_point(self, point):
        if self.mode == NORMAL_MODE:
            return self.get_color_index_normal(point)
        elif self.mode == LARGE_MODE:
            return self.get_color_index_large(point)
        elif self.mode == LIST_MODE:
            return self.get_color_index_list(point)
        else:
            if len(self.colors) < 15:
                return self.get_color_index_list(point)
            elif len(self.colors) < 50:
                return self.get_color_index_large(point)
            else:
                return self.get_color_index_normal(point)

    def get_color_index_normal(self, point):
        x, y = self.win_to_doc(*point)
        x = 3 if x < 2 else x
        x = 155 if x > 156 else x
        y = 3 if y < 2 else y
        index = int(y / 15) * 10 + int(x / 15)
        if index < len(self.colors):
            return index
        return None

    def get_color_index_large(self, point):
        x, y = self.win_to_doc(*point)
        x = 3 if x < 2 else x
        x = 155 if x > 156 else x
        y = 3 if y < 2 else y
        index = int(y / 30) * 5 + int(x / 30)
        if index < len(self.colors):
            return index
        return None

    def get_color_index_list(self, point):
        x, y = self.win_to_doc(*point)
        index = int(y / 24)
        if index < len(self.colors):
            return index
        return None

    def paint(self):
        w, h = self.get_size()
        if not self.colors:
            self.set_stroke(wal.LIGHT_GRAY)
            self.draw_line(0, 0, w, h)
            self.draw_line(w, 0, 0, h)
            return
        if self.mode == NORMAL_MODE:
            self.normal_mode_paint()
        elif self.mode == LARGE_MODE:
            self.large_mode_paint()
        elif self.mode == LIST_MODE:
            self.list_mode_paint()
        else:
            if len(self.colors) < 15:
                self.list_mode_paint()
            elif len(self.colors) < 50:
                self.large_mode_paint()
            else:
                self.normal_mode_paint()

        if not self.get_virtual_size()[1] > h:
            self.set_stroke()
            self.set_fill(wal.UI_COLORS['bg'])
            self.draw_rect(self.width - self.sb_width, -3,
                           self.sb_width + 5, self.get_size()[1] + 6)

    def normal_mode_paint(self):
        self.cell_in_line = 10
        self.cell_width = 16
        self.cell_height = 16
        self.cell_mode_paint()

    def large_mode_paint(self):
        self.cell_in_line = 5
        self.cell_width = 31
        self.cell_height = 31
        self.cell_mode_paint()

    def cell_mode_paint(self):
        self.height = round(1.0 * len(self.colors) / self.cell_in_line) + 1
        self.height = int(self.height * (self.cell_height - 1))
        self.set_virtual_size((self.width - self.sb_width, self.height))
        self.set_scroll_rate(self.cell_width - 1, self.cell_height - 1)

        self.prepare_dc(self.pdc)

        w = self.cell_width
        h = self.cell_height
        y = x = 1
        i = 0
        for color in self.colors:
            self.set_stroke(wal.BLACK)
            self.set_fill(self.cms.get_display_color255(color))
            self.draw_rect(x, y, w, h)
            if i == self.selected_index:
                bmp = self.small_sel
                if self.cell_width == 31:
                    bmp = self.large_sel
                self.draw_bitmap(bmp, x, y)
            x += w - 1
            if x > (w - 1) * self.cell_in_line:
                x = 1
                y += h - 1
            i += 1

    def list_mode_paint(self):
        self.cell_width = 20
        self.cell_height = 20
        row = self.cell_height + 4

        self.height = len(self.colors) * row
        self.set_virtual_size((self.width - self.sb_width, self.height))
        self.set_scroll_rate(self.cell_width - 1, self.cell_height - 1)

        self.prepare_dc(self.pdc)

        w = self.cell_width
        h = self.cell_height
        i = 0
        txt_height = self.set_font()
        txt_x = 5 + self.cell_width + 5
        txt_y = 2 + round((self.cell_height - txt_height) / 2.0)
        self.set_text_color(wal.BLACK)

        for color in self.colors:
            if i == self.selected_index:
                self.set_stroke()
                self.set_fill(wal.UI_COLORS['selected_text_bg'])
                self.draw_rect(0, row * i, self.width - self.sb_width, h + 4)
            self.set_stroke(wal.BLACK)
            self.set_fill(self.cms.get_display_color255(color))
            self.draw_rect(5, 2 + row * i, w, h)
            txt = color[3]
            if txt:
                if i == self.selected_index:
                    self.set_text_color(wal.UI_COLORS['selected_text'])
                else:
                    self.set_text_color(wal.BLACK)
                self.draw_text(txt, txt_x, txt_y + row * i)
            i += 1


class PaletteViewer(wal.VPanel):
    palette = None
    callback = None
    sel_color = None

    def __init__(self, parent, cms, palette=None, onclick=None):
        self.cms = cms
        self.callback = onclick
        wal.VPanel.__init__(self, parent)
        if wal.IS_WX3:
            self.pack((172, 1))
        options = wal.ExpandedPanel(self, _('Palette preview:'))
        changer = wal.HToggleKeeper(options, PREVIEW_MODES, MODE_ICON,
                                    MODE_NAME, on_change=self.set_mode)
        options.pack(changer)
        self.pack(options, fill=True)
        border = wal.VPanel(self)
        border.set_bg(wal.UI_COLORS['border'])
        self.pack(border, expand=True, fill=True)
        self.win = ScrolledPalette(border, self.cms, onclick=self.select_color)
        border.pack(self.win, expand=True, fill=True, padding_all=1)
        changer.set_mode(AUTO_MODE)
        if palette:
            self.draw_palette(palette)

    def draw_palette(self, palette=None):
        if not palette:
            self.win.colors = []
            self.win.refresh()
            return
        self.palette = palette
        self.win.colors = palette.model.colors
        self.win.selected_index = None
        self.win.refresh()

    def set_mode(self, mode):
        if self.palette:
            self.win.mode = mode
            self.win.refresh()

    def get_color(self):
        return self.sel_color

    def set_active_color(self, index=0):
        if self.win.colors and index < len(self.win.colors):
            self.win.selected_index = index
            self.sel_color = deepcopy(self.win.colors[self.win.selected_index])
            self.win.refresh()

    def select_color(self):
        if self.callback and self.win.selected_index is not None:
            self.sel_color = deepcopy(self.win.colors[self.win.selected_index])
            self.callback()
