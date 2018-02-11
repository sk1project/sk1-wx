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
from basic import HPanel, SensitiveCanvas

TAB_HEIGHT = 25
TAB_MARGIN = 1
TAB_PADDING = 5
TAB_SIZE = 150


class DocTabs(HPanel, SensitiveCanvas):
    doc_tabs = []
    draw_top = True
    custom_bg = None
    pos_min = 0
    pos_max = 0

    def __init__(self, parent, draw_top=True, custom_bg=None):
        self.draw_top = draw_top
        self.custom_bg = custom_bg
        HPanel.__init__(self, parent)
        SensitiveCanvas.__init__(self, check_move=True)
        self.pack((TAB_PADDING, TAB_HEIGHT))

    def add_new_tab(self, doc_tab):
        self.doc_tabs.append(doc_tab)
        self.refresh()
        return doc_tab

    def remove_tab(self, doc_tab):
        self.doc_tabs.remove(doc_tab)
        self.refresh()

    def set_active(self, doc_tab):
        for tab in self.doc_tabs:
            if tab.active:
                tab.set_active(False)
        doc_tab.set_active(True)
        self.refresh()

    def arrange_tabs(self):
        if self.doc_tabs:
            self.pos_min = pos = TAB_HEIGHT
            self.pos_max = self.get_size()[0] - pos
            width = self.pos_max - self.pos_min - TAB_SIZE
            total_docs = len(self.doc_tabs)
            size = TAB_SIZE if total_docs < 2 else width // (total_docs - 1)
            for tab in self.doc_tabs:
                tab.size = size
                if not tab.moves:
                    tab.set_position(pos)
                pos += tab.get_width()

    def reorder_tabs(self, tab, dx):
        index = self.doc_tabs.index(tab)
        if dx > 0 and index == len(self.doc_tabs) - 1:
            pass
        elif dx < 0 and not index:
            pass
        elif dx > 0:
            pos1 = tab.pos + tab.get_width()
            after = self.doc_tabs[index + 1]
            pos2 = after.pos + after.get_width() // 2
            if pos1 > pos2:
                self.doc_tabs.remove(tab)
                self.doc_tabs.insert(index + 1, tab)
        elif dx < 0:
            pos1 = tab.pos
            before = self.doc_tabs[index - 1]
            pos2 = before.pos + before.get_width() // 2
            if pos1 < pos2:
                self.doc_tabs.remove(tab)
                self.doc_tabs.insert(index - 1, tab)

    def mouse_left_down(self, point):
        for tab in self.doc_tabs:
            if tab.is_point_in_tab(point):
                tab.mouse_left_down(point)
                break

    def mouse_left_up(self, point):
        for tab in self.doc_tabs:
            if tab.moves:
                tab.mouse_left_up(point)
                return
        for tab in self.doc_tabs:
            if tab.is_point_in_tab(point):
                tab.mouse_left_up(point)
                break

    def mouse_right_down(self, point):
        for tab in self.doc_tabs:
            if tab.is_point_in_tab(point):
                tab.mouse_right_down()
                break

    def mouse_move(self, point):
        for tab in self.doc_tabs:
            if tab.moves:
                tab.mouse_move(point)
                return
        for tab in self.doc_tabs:
            if tab.is_point_in_tab(point):
                tab.mouse_move(point)
            else:
                tab.mouse_leaved_tab()

    def mouse_leave(self, point):
        for tab in self.doc_tabs:
            tab.mouse_leaved_tab()

    def refresh(self):
        self.arrange_tabs()
        HPanel.refresh(self)

    def paint(self):
        color = const.UI_COLORS['hover_solid_border']
        active_tab = None
        w, h = self.get_size()

        # optional panel background
        if self.custom_bg:
            self.set_stroke(None)
            self.set_fill(self.custom_bg)
            self.draw_rect(0, 0, w, h)
        elif const.IS_AMBIANCE:
            self.set_stroke(None)
            self.set_fill(const.AMBIANCE_GRAY)
            self.draw_rect(0, 0, w, h)

        if self.draw_top:
            self.set_stroke(color)
            self.draw_line(0, 0, w, 0)

        # tab rendering
        for tab in self.doc_tabs:
            if not tab.active:
                tab.paint()
            else:
                active_tab = tab

        # gradient
        start = (0, 0, 0, 0)
        stop = (0, 0, 0, 30)
        self.gc_draw_linear_gradient((0, h / 4, w, h * 3 / 4),
                                     start, stop, True)
        self.set_stroke(color)
        self.draw_line(0, h - 1, w, h - 1)

        # active tab rendering
        if active_tab:
            active_tab.paint()


INDICATOR_SIZE = 8


class LWDocTab(object):
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

    def get_width(self):
        return TAB_SIZE if self.active else min(TAB_SIZE, self.size)

    def set_title(self, title):
        self.text = title
        self.parent.refresh()

    def set_active(self, value):
        self.active = value
        self.set_position(self.pos)

    def set_position(self, pos):
        self.pos = pos
        s = INDICATOR_SIZE
        x0 = self.get_width() - 2 * s - int(s / 2) + 1
        y0 = int(TAB_HEIGHT / 2 - s) + 2
        self.close_rect = (x0, y0, x0 + 2 * s, y0 + 2 * s)

    def is_point_in_tab(self, point):
        return self.pos < point[0] < self.pos + self.get_width()

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
        self.close_pressed = self.close_active
        self.moves = not self.close_active
        if self.close_pressed:
            self.parent.refresh()
        if self.moves:
            self.move_start = point
            self.orig_pos = self.pos
        return not self.close_active

    def mouse_left_up(self, point):
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
            dx = - self.pos
            pos = self.orig_pos + point[0] - self.move_start[0]
            pos = min(pos, self.parent.pos_max - self.get_width())
            pos = max(pos, self.parent.pos_min)
            self.set_position(pos)
            dx += self.pos
            self.parent.reorder_tabs(self, dx)
            self.parent.refresh()
            return
        if self.is_close_active(point) != self.close_active:
            self.close_active = not self.close_active
            self.parent.refresh()

    def close(self):
        pass

    def _get_text_size(self, text, bold=False, size_incr=0):
        font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        if bold:
            font.SetWeight(wx.FONTWEIGHT_BOLD)
        if size_incr:
            if font.IsUsingSizeInPixels():
                sz = font.GetPixelSize()[1] + size_incr
                font.SetPixelSize((0, sz))
            else:
                sz = font.GetPointSize() + size_incr
                font.SetPointSize(sz)
        pdc = wx.MemoryDC()
        bmp = wx.EmptyBitmap(1, 1)
        pdc.SelectObject(bmp)
        pdc.SetFont(font)
        height = pdc.GetCharHeight()
        width = pdc.GetTextExtent(text)[0]
        result = (width, height)
        pdc.SelectObject(wx.NullBitmap)
        return result

    def paint(self):
        stroke_color = const.UI_COLORS['hover_solid_border']
        bg_color = const.UI_COLORS['bg']
        fg_color = const.UI_COLORS['fg']
        dc = self.parent

        # tab rect
        dc.set_gc_fill(bg_color)
        dc.set_gc_stroke(stroke_color)
        r = 0 if self.active or self.parent.draw_top else 6
        y = 0 if self.active or self.parent.draw_top else 2
        dc.gc_draw_rounded_rect(self.pos, y,
                                self.get_width() + 1, TAB_HEIGHT + 5, r)

        # tab indicator
        s = INDICATOR_SIZE
        dc.set_gc_fill(const.RED if not self.saved else None)
        dc.set_gc_stroke(stroke_color if self.saved else const.BROWN)
        dc.gc_draw_rounded_rect(self.pos + s, 10, s, s, s / 2)
        if self.saved:
            dc.set_gc_stroke((255, 255, 255, 150))
            dc.gc_draw_rounded_rect(self.pos + s, 11, s, s, s / 2)

        # tab caption
        pos = self.pos + 3 * s - 3
        width = self.get_width() - 5 * s
        txt = self.text
        while self._get_text_size(txt, size_incr=-1)[0] > width:
            txt = txt[:-1]

        y = int(TAB_HEIGHT / 2 - dc.set_font(size_incr=-1) / 2) + 1
        dc.draw_text(txt, pos, y)

        # tab caption shade
        pos = self.pos + self.get_width() - 5 * s
        start = bg_color[:-1] + (0,)
        stop = bg_color[:-1] + (255,)
        dc.gc_draw_linear_gradient((pos, 4, 3 * s, TAB_HEIGHT),
                                   start, stop, False)

        # tab marker
        if self.active:
            r = (self.pos + 1, 1, self.get_width() - 1, 2)
            if const.IS_AMBIANCE:
                dc.set_stroke(None)
                dc.set_fill(const.UI_COLORS['selected_text_bg'])
                dc.draw_rect(*r)
            else:
                render = wx.RendererNative.Get()
                render.DrawItemSelectionRect(dc, dc.dc, r, wx.CONTROL_SELECTED)

        # close button --------
        pos = self.pos + self.close_rect[0]
        y = self.close_rect[1]
        if self.close_active:
            dc.set_gc_fill(const.BROWN if self.close_pressed
                           else const.DARK_RED)
            dc.set_gc_stroke(None)
            dc.gc_draw_rounded_rect(pos + 1, y + 1, 2 * s - 2, 2 * s - 2, s)

        dc.set_gc_fill(None)
        dc.set_gc_stroke(const.WHITE if self.close_active else fg_color,
                         2.0 if self.close_active else 1.5)
        x0 = pos + 5
        y0 = y + 5
        x1 = pos + 2 * s - 5
        y1 = y + 2 * s - 5
        dc.gc_draw_line(x0, y0, x1, y1)
        dc.gc_draw_line(x0, y1, x1, y0)


class RoundedTabPainter(object):
    def __init__(self, panel):
        self.panel = panel
