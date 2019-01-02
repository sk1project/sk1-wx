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
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import wx

import const
from basic import HPanel, SensitiveCanvas
from renderer import get_text_size

TAB_MARGIN = 1
TAB_PADDING = 5
TAB_SIZE = 150
INDICATOR_SIZE = 8
HTAB = 0
VTAB = 1
HTAB_HEIGHT = 25
VTAB_WIDTH = 25
ICON_SIZE = 16


class TabPanel(HPanel, SensitiveCanvas):
    painter = None
    tabs = []
    draw_top = True
    custom_bg = None
    pos_min = 0
    pos_max = 0

    def __init__(self, parent, draw_top=True, custom_bg=None, painter_index=0):
        self.draw_top = draw_top
        self.custom_bg = custom_bg
        self.tabs = []
        HPanel.__init__(self, parent)
        SensitiveCanvas.__init__(self, check_move=True)
        self.set_double_buffered()
        self.set_panel_size()
        self.set_painter(painter_index)

    def set_panel_size(self):
        pass

    def set_painter(self, painter_index):
        pass

    def arrange_tabs(self):
        pass

    def reorder_tabs(self, tab, dpos):
        index = self.tabs.index(tab)
        if dpos > 0 and index == len(self.tabs) - 1:
            pass
        elif dpos < 0 and not index:
            pass
        elif dpos > 0:
            pos1 = tab.pos + tab.get_tab_size()
            after = self.tabs[index + 1]
            pos2 = after.pos + after.get_tab_size() // 2
            if pos1 > pos2:
                self.change_tab_index(index + 1, tab)
        elif dpos < 0:
            pos1 = tab.pos
            before = self.tabs[index - 1]
            pos2 = before.pos + before.get_tab_size() // 2
            if pos1 < pos2:
                self.change_tab_index(index - 1, tab)

    def add_new_tab(self, new_tab):
        for tab in self.tabs:
            if tab.active:
                tab.set_active(False)
        self.tabs.append(new_tab)
        self.refresh()
        return new_tab

    def remove_tab(self, tab):
        self.tabs.remove(tab)
        self.refresh()

    def set_active(self, selected_tab):
        for tab in self.tabs:
            if tab.active:
                tab.set_active(False)
        selected_tab.set_active(True)
        self.refresh()

    def change_tab_index(self, index, tab):
        self.tabs.remove(tab)
        self.tabs.insert(index, tab)

    def mouse_left_dclick(self, point):
        for tab in self.tabs:
            if tab.is_point_in_tab(point):
                return
        self.double_click()

    def double_click(self):
        pass

    def mouse_left_down(self, point):
        for tab in self.tabs:
            if tab.is_point_in_tab(point):
                tab.mouse_left_down(point)
                break

    def mouse_left_up(self, point):
        for tab in self.tabs:
            if tab.moves:
                tab.mouse_left_up()
                return
        for tab in self.tabs:
            if tab.is_point_in_tab(point):
                tab.mouse_left_up()
                break

    def mouse_right_down(self, point):
        for tab in self.tabs:
            if tab.is_point_in_tab(point):
                tab.mouse_right_down()
                break

    def mouse_move(self, point):
        for tab in self.tabs:
            if tab.moves:
                tab.mouse_move(point)
                return
        for tab in self.tabs:
            if tab.is_point_in_tab(point):
                tab.mouse_move(point)
            else:
                tab.mouse_leaved_tab()

    def mouse_leave(self, point):
        for tab in self.tabs:
            tab.mouse_leaved_tab()

    def refresh(self, **kwargs):
        self.arrange_tabs()
        HPanel.refresh(self)

    def paint(self):
        if self.painter:
            self.painter.paint_panel()


class Tab(object):
    stl = HTAB
    active = True
    saved = True
    text = 'Untitled'
    pos = 0
    close_active = False
    close_pressed = False
    moves = False
    move_start = None
    orig_pos = 0
    close_rect = (0, 0, 1, 1)
    size = TAB_SIZE

    def __init__(self, parent, active=True):
        self.parent = parent
        self.active = active

    def set_position(self, pos):
        pass

    def get_tab_size(self):
        return TAB_SIZE if self.active else min(TAB_SIZE, self.size)

    def set_title(self, title):
        self.text = title
        self.parent.refresh()

    def set_active(self, value):
        self.active = value
        self.set_position(self.pos)

    def is_point_in_tab(self, point):
        return self.pos < point[self.stl] < self.pos + self.get_tab_size()

    def is_close_active(self, point):
        x, y = point
        x0, y0, x1, y1 = self.close_rect
        x0 += self.pos
        x1 += self.pos
        return x0 < x < x1 and y0 < y < y1

    def mouse_leaved_tab(self):
        if self.close_active:
            self.close_active = False
            self.close_pressed = False
            self.parent.refresh()

    def mouse_left_down(self, point):
        self.parent.capture_mouse()
        self.close_pressed = self.close_active
        self.moves = not self.close_active
        if self.close_pressed:
            self.parent.refresh()
        if self.moves:
            self.move_start = point
            self.orig_pos = self.pos
        return not self.close_active

    def mouse_left_up(self):
        self.parent.release_mouse()
        if self.close_active:
            self.close()
        self.close_pressed = False
        if self.moves:
            self.moves = False
            self.parent.refresh()

    def mouse_right_down(self):
        pass

    def mouse_move(self, point):
        if self.moves:
            dpos = - self.pos
            pos = self.orig_pos + point[self.stl] - self.move_start[self.stl]
            pos = min(pos, self.parent.pos_max - self.get_tab_size())
            pos = max(pos, self.parent.pos_min)
            self.set_position(pos)
            dpos += self.pos
            self.parent.reorder_tabs(self, dpos)
            self.parent.refresh()
            return
        if self.is_close_active(point) != self.close_active:
            self.close_active = not self.close_active
            self.parent.refresh()

    def close(self):
        pass


class TabPainter(object):
    def __init__(self, panel):
        self.panel = panel
        self.border_color = const.UI_COLORS['hover_solid_border']
        self.bg_color = const.UI_COLORS['bg']
        self.fg_color = const.UI_COLORS['fg']

    def paint_panel(self):
        active_tab = None

        self.paint_panel_bg()
        self.paint_panel_top()

        for tab in self.panel.tabs:
            if not tab.active:
                self.paint_tab(tab)
            else:
                active_tab = tab

        self.paint_panel_shadow()

        if active_tab:
            self.paint_tab(active_tab)

    def paint_panel_bg(self):
        dc = self.panel
        w, h = dc.get_size()

        if dc.custom_bg:
            dc.set_stroke(None)
            dc.set_fill(dc.custom_bg)
            dc.draw_rect(0, 0, w, h)

    def paint_panel_top(self):
        dc = self.panel
        if not dc.draw_top or const.IS_MSW:
            w, h = dc.get_size()
            dc.set_stroke(self.border_color)
            dc.draw_line(0, 0, w, 0)

    def paint_panel_shadow(self):
        dc = self.panel
        w, h = dc.get_size()
        start = (0, 0, 0, 0)
        stop = (0, 0, 0, 30)
        dc.gc_draw_linear_gradient((0, h / 4, w, h * 3 / 4),
                                   start, stop, True)
        dc.set_stroke(self.border_color)
        dc.draw_line(0, h - 1, w, h - 1)

    def paint_tab(self, tab):
        self.paint_tab_rect(tab)
        self.paint_tab_indicator(tab)
        self.paint_tab_text(tab)
        self.paint_tab_marker(tab)
        self.paint_tab_close_btn(tab)

    def paint_tab_rect(self, tab, r=0, y=0):
        dc = self.panel
        dc.set_gc_fill(self.bg_color)
        dc.set_gc_stroke(self.border_color)
        dc.gc_draw_rounded_rect(tab.pos, y,
                                tab.get_tab_size() + 1, HTAB_HEIGHT + 5, r)

    def paint_tab_indicator(self, tab):
        dc = self.panel
        s = INDICATOR_SIZE
        dc.set_gc_fill(const.RED if not tab.saved else None)
        dc.set_gc_stroke(self.border_color if tab.saved else const.BROWN)
        dc.gc_draw_rounded_rect(tab.pos + s, 10, s, s, s / 2)
        if tab.saved:
            dc.set_gc_stroke((255, 255, 255, 150))
            dc.gc_draw_rounded_rect(tab.pos + s, 11, s, s, s / 2)

    def paint_tab_text(self, tab):
        dc = self.panel
        s = INDICATOR_SIZE
        pos = tab.pos + 3 * s - 3
        width = tab.get_tab_size() - 5 * s
        txt = const.tr(tab.text)
        if const.IS_MSW:
            if get_text_size(txt, size_incr=-1)[0] > width:
                while get_text_size(txt + '...', size_incr=-1)[0] > width:
                    txt = txt[:-1]
                txt += '...'
        else:
            while get_text_size(txt, size_incr=-1)[0] > width:
                txt = txt[:-1]

        y = int(HTAB_HEIGHT / 2 - dc.set_font(size_incr=-1) / 2) + 1
        dc.draw_text(txt, pos, y)

        if not const.IS_MSW:
            # text shade
            pos = tab.pos + tab.get_tab_size() - 5 * s
            start = self.bg_color[:-1] + (0,)
            stop = self.bg_color[:-1] + (255,)
            dc.gc_draw_linear_gradient((pos, 4, 3 * s, HTAB_HEIGHT),
                                       start, stop, False)

    def paint_tab_marker(self, tab):
        dc = self.panel
        if tab.active:
            r = (tab.pos + 1, 1, tab.get_tab_size() - 1, 2)
            if const.IS_AMBIANCE or const.IS_MSW:
                dc.set_stroke(None)
                dc.set_fill(const.UI_COLORS['selected_text_bg'])
                dc.draw_rect(*r)
            else:
                render = wx.RendererNative.Get()
                render.DrawItemSelectionRect(dc, dc.dc, r, wx.CONTROL_SELECTED)

    def paint_tab_close_btn(self, tab):
        dc = self.panel
        s = INDICATOR_SIZE
        pos = tab.pos + tab.close_rect[0]
        y = tab.close_rect[1]
        if tab.close_active:
            dc.set_gc_fill(const.BROWN if tab.close_pressed
                           else const.DARK_RED)
            dc.set_gc_stroke(None)
            dc.gc_draw_rounded_rect(pos + 1, y + 1, 2 * s - 2, 2 * s - 2, s)

        dc.set_gc_fill(None)
        dc.set_gc_stroke(const.WHITE if tab.close_active else self.fg_color,
                         2.0 if tab.close_active else 1.5)
        x0 = pos + 5
        y0 = y + 5
        x1 = pos + 2 * s - 5
        y1 = y + 2 * s - 5
        dc.gc_draw_line(x0, y0, x1, y1)
        dc.gc_draw_line(x0, y1, x1, y0)


class RoundedTabPainter(TabPainter):
    def paint_tab_rect(self, tab, **kwargs):
        y = 3 if not tab.active and not self.panel.draw_top else 0
        y = 2 if not tab.active and self.panel.draw_top else y
        TabPainter.paint_tab_rect(self, tab, 6, y)

    def paint_tab_marker(self, tab):
        pass


class RectTabPainter(TabPainter):
    def paint_tab_rect(self, tab, **kwargs):
        y = 2 if not tab.active and self.panel.draw_top else 0
        TabPainter.paint_tab_rect(self, tab, 0, y)


class FlatTabPainter(TabPainter):
    def paint_tab_rect(self, tab, **kwargs):
        if tab.active:
            TabPainter.paint_tab_rect(self, tab)
        else:
            index = self.panel.tabs.index(tab)
            dc = self.panel
            dc.set_stroke(self.fg_color, dashes=[1, 1])
            if not index or dc.tabs[index - 1].active:
                dc.draw_line(tab.pos, 4, tab.pos, HTAB_HEIGHT - 4)
            pos = tab.pos + tab.get_tab_size()
            dc.draw_line(pos, 4, pos, HTAB_HEIGHT - 4)


class TrapeziodalTabPainter(TabPainter):
    def paint_panel(self):
        active_tab = None

        self.paint_panel_bg()
        self.paint_panel_top()
        tabs = [] + self.panel.tabs
        tabs.reverse()

        for tab in tabs:
            if not tab.active:
                self.paint_tab(tab)
            else:
                active_tab = tab

        self.paint_panel_shadow()

        if active_tab:
            self.paint_tab(active_tab)

    def paint_tab_marker(self, tab):
        pass

    def paint_tab_rect(self, tab, **kwargs):
        dc = self.panel
        dc.set_gc_fill(self.bg_color)
        dc.set_gc_stroke(self.border_color)
        x, y = tab.pos, 2
        points = [(x - 7, HTAB_HEIGHT + 3),
                  (x + 6, y),
                  (x + tab.get_tab_size() - 6, y),
                  (x + tab.get_tab_size() + 7, HTAB_HEIGHT + 3)]
        dc.gc_draw_polygon(points)


HPAINTERS = {
    0: RectTabPainter,
    1: RoundedTabPainter,
    2: FlatTabPainter,
    3: TrapeziodalTabPainter,
}


class HTabPanel(TabPanel):
    def set_panel_size(self):
        self.pack((TAB_PADDING, HTAB_HEIGHT))

    def set_painter(self, painter_index):
        painter_index = painter_index if painter_index in HPAINTERS else 0
        self.painter = HPAINTERS[painter_index](self)
        self.refresh()

    def arrange_tabs(self):
        if self.tabs:
            self.pos_min = pos = HTAB_HEIGHT
            self.pos_max = self.get_size()[0] - pos
            width = self.pos_max - self.pos_min - TAB_SIZE
            total_docs = len(self.tabs)
            size = TAB_SIZE if total_docs < 2 else width // (total_docs - 1)
            for tab in self.tabs:
                tab.size = size
                if not tab.moves:
                    tab.set_position(pos)
                pos += tab.get_tab_size()


class HTab(Tab):
    def set_position(self, pos):
        self.pos = pos
        s = INDICATOR_SIZE
        x0 = self.get_tab_size() - 2 * s - int(s / 2) + 1
        y0 = int(HTAB_HEIGHT / 2 - s) + 2
        self.close_rect = (x0, y0, x0 + 2 * s, y0 + 2 * s)


class VRectTabPainter(TabPainter):
    def paint_panel_top(self):
        dc = self.panel
        if not dc.draw_top or const.IS_MSW:
            w, h = dc.get_size()
            dc.set_stroke(self.border_color)
            dc.draw_line(w, 0, w, h)

    def paint_panel_shadow(self):
        dc = self.panel
        w, h = dc.get_size()
        start = (0, 0, 0, 30)
        stop = (0, 0, 0, 0)
        dc.gc_draw_linear_gradient((0, 0, w * 3 / 4, h),
                                   start, stop, False)
        dc.set_stroke(self.border_color)
        dc.draw_line(0, 0, 0, h)

    def paint_tab_rect(self, tab, r=0, y=0):
        dc = self.panel
        dc.set_gc_fill(self.bg_color)
        dc.set_gc_stroke(self.border_color)
        dc.gc_draw_rounded_rect(-2, tab.pos,
                                VTAB_WIDTH + 5, tab.get_tab_size() + 1, r)

    def paint_tab_indicator(self, tab):
        if 'icon' in tab.__dict__:
            dc = self.panel
            x = (VTAB_WIDTH - ICON_SIZE) // 2
            x = x + 1 if tab.active else x
            y = tab.pos + 3
            dc.gc_draw_bitmap(tab.icon, x, y)

            # icon color marker
            x += 1
            y += 1
            w = 14
            h = 2

            if const.IS_AMBIANCE:
                return
            elif const.IS_MSW:
                dc.set_stroke(None)
                dc.set_fill(const.UI_COLORS['selected_text_bg'])
                dc.draw_rect(x, y, w, h)
            else:
                render = wx.RendererNative.Get()
                render.DrawItemSelectionRect(dc, dc.dc, (x + 1, y, w - 2, h),
                                             wx.CONTROL_SELECTED)

    def paint_tab_text(self, tab):
        dc = self.panel
        s = INDICATOR_SIZE
        pos = tab.pos + 3 * s - 3
        width = tab.get_tab_size() - 5 * s
        txt = const.tr(tab.text)
        if const.IS_MSW:
            if get_text_size(txt, size_incr=-1)[0] > width:
                while get_text_size(txt + '...', size_incr=-1)[0] > width:
                    txt = txt[:-1]
                txt += '...'
        else:
            while get_text_size(txt, size_incr=-1)[0] > width:
                txt = txt[:-1]
        shift = 2 if tab.active else 1
        shift = shift + 2 if const.IS_MSW else shift
        x = int(VTAB_WIDTH / 2 + dc.set_font(size_incr=-1) / 2) + shift
        dc.draw_rotated_text(txt, x, pos, 270)

        if not const.IS_MSW:
            # text shade
            pos = tab.pos + tab.get_tab_size() - 5 * s
            start = self.bg_color[:-1] + (0,)
            stop = self.bg_color[:-1] + (255,)
            dc.gc_draw_linear_gradient((4, pos, 3 * s, VTAB_WIDTH),
                                       start, stop, True)

    def paint_tab_marker(self, tab):
        pass

    def paint_tab_close_btn(self, tab):
        dc = self.panel
        s = INDICATOR_SIZE
        pos = tab.pos + tab.close_rect[1]
        x = tab.close_rect[0]
        shift = 1 if tab.active else 0
        if tab.close_active:
            dc.set_gc_fill(const.BROWN if tab.close_pressed
                           else const.DARK_RED)
            dc.set_gc_stroke(None)
            dc.gc_draw_rounded_rect(x + shift, pos + 1, 2 * s - 2, 2 * s - 2, s)

        dc.set_gc_fill(None)
        dc.set_gc_stroke(const.WHITE if tab.close_active else self.fg_color,
                         2.0 if tab.close_active else 1.5)
        y0 = pos + 5
        x0 = x + 4 + shift
        y1 = pos + 2 * s - 5
        x1 = x + 2 * s - 6 + shift
        dc.gc_draw_line(x0, y0, x1, y1)
        dc.gc_draw_line(x0, y1, x1, y0)


VPAINTERS = {
    0: VRectTabPainter,
}


class VTabPanel(TabPanel):
    def set_panel_size(self):
        self.pack((VTAB_WIDTH, TAB_PADDING))

    def set_painter(self, painter_index):
        painter_index = painter_index if painter_index in HPAINTERS else 0
        self.painter = VPAINTERS[painter_index](self)
        self.refresh()

    def arrange_tabs(self):
        if self.tabs:
            self.pos_min = pos = TAB_PADDING
            self.pos_max = self.get_size()[1] - pos
            width = self.pos_max - self.pos_min - TAB_SIZE
            total_docs = len(self.tabs)
            size = TAB_SIZE if total_docs < 2 else width // (total_docs - 1)
            for tab in self.tabs:
                tab.size = size
                if not tab.moves:
                    tab.set_position(pos)
                pos += tab.get_tab_size()


class VTab(Tab):
    stl = VTAB

    def set_position(self, pos):
        self.pos = pos
        s = INDICATOR_SIZE
        y0 = self.get_tab_size() - 2 * s - int(s / 2) + 1
        x0 = int(HTAB_HEIGHT / 2 - s)  # + 2
        self.close_rect = (x0, y0, x0 + 2 * s, y0 + 2 * s)

    def is_close_active(self, point):
        x, y = point
        x0, y0, x1, y1 = self.close_rect
        y0 += self.pos
        y1 += self.pos
        return x0 < x < x1 and y0 < y < y1
