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

    def __init__(self, parent):
        HPanel.__init__(self, parent)
        SensitiveCanvas.__init__(self)
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
        pos = TAB_HEIGHT
        for tab in self.doc_tabs:
            tab.pos = pos
            pos += tab.get_width()

    def mouse_left_down(self, point):
        x = point[0]
        for tab in self.doc_tabs:
            if tab.pos + tab.get_width() > x:
                tab.mouse_left_down(point)
                break

    def refresh(self):
        self.arrange_tabs()
        HPanel.refresh(self)

    def paint(self):
        color = const.UI_COLORS['hover_solid_border']
        active_tab = None
        w, h = self.get_size()
        self.set_stroke(color)
        self.draw_line(0, 0, w, 0)
        for tab in self.doc_tabs:
            if not tab.active:
                tab.paint()
            else:
                active_tab = tab
        start = (0, 0, 0, 0)
        stop = (0, 0, 0, 30)
        self.gc_draw_linear_gradient((0, h / 4, w, h * 3 / 4),
                                     start, stop, True)
        self.set_stroke(color)
        self.draw_line(0, h - 1, w, h - 1)
        active_tab.paint()


INDICATOR_SIZE = 8


class LWDocTab(object):
    active = True
    saved = True
    text = 'Untitled'
    pos = 0

    def __init__(self, parent, active=True):
        self.parent = parent
        self.active = active

    def get_width(self):
        return TAB_SIZE

    def set_title(self, title):
        self.text = title
        self.parent.refresh()

    def set_active(self, value):
        self.active = value

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
        dc = self.parent

        # tab rect
        dc.set_fill(bg_color)
        dc.set_stroke(stroke_color)
        dc.draw_rect(self.pos, 0, self.get_width() + 1, TAB_HEIGHT + 5)

        # tab indicator
        s = INDICATOR_SIZE
        dc.set_gc_fill(const.RED if not self.saved else None)
        dc.set_gc_stroke(stroke_color if self.saved else (145, 45, 45))
        dc.gc_draw_rounded_rect(self.pos + s, 10, s, s, s / 2)
        if self.saved:
            dc.set_gc_stroke((255, 255, 255, 150))
            dc.gc_draw_rounded_rect(self.pos + s, 11, s, s, s / 2)

        # tab caption
        pos = self.pos + 3 * s - 2
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
            r = (self.pos + 2, 1, self.get_width() - 2, 2)
            render = wx.RendererNative.Get()
            render.DrawItemSelectionRect(dc, dc.dc, r, wx.CONTROL_SELECTED)
