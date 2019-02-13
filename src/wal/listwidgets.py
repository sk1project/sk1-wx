# -*- coding: utf-8 -*-
#
#  Copyright (C) 2015-2018 by Igor E. Novikov
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
import wx.lib.mixins.listctrl as listmix

import const
from mixins import WidgetMixin


class SimpleList(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, WidgetMixin):
    data = []
    select_cmd = None
    activate_cmd = None
    alt_color = False

    def __init__(self, parent, data=None, border=True, header=False,
                 single_sel=True, virtual=False, alt_color=False,
                 even_color=None, odd_color=None,
                 on_select=None, on_activate=None):
        self.data = data or []
        self.alt_color = alt_color
        self.odd_color = odd_color or const.ODD_COLOR
        self.even_color = even_color or const.EVEN_COLOR
        style = wx.LC_REPORT | wx.LC_VRULES
        if not const.IS_WX3:
            style |= wx.BORDER_MASK if border else wx.NO_BORDER
        style = style | wx.LC_NO_HEADER if not header else style
        style = style | wx.LC_SINGLE_SEL if single_sel else style
        style = style | wx.LC_VIRTUAL if virtual else style
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, style=style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        if self.data:
            self.update(self.data)
        if on_select:
            self.select_cmd = on_select
            self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self)
        if on_activate:
            self.activate_cmd = on_activate
            self.Bind(wx.wx.EVT_LIST_ITEM_ACTIVATED, self.on_activate, self)

    def set_active(self, index):
        if len(self.data) - 1 >= index:
            self.Select(index, True)

    def clear_all(self):
        self.ClearAll()

    def set_column_width(self, index, width):
        self.SetColumnWidth(index, width)

    def update(self, data):
        self.DeleteAllItems()
        self.data = data
        if not self.GetColumnCount():
            self.set_columns()
        self.set_data(self.data, self.alt_color)
        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)

    def set_columns(self):
        self.InsertColumn(0, '')

    def set_data(self, data, alt_color=True):
        even = False
        i = 0
        for item in data:
            item = const.tr(item)
            self.Append([item])
            if alt_color:
                list_item = self.GetItem(i)
                if even:
                    list_item.SetBackgroundColour(self.even_color)
                else:
                    list_item.SetBackgroundColour(self.odd_color)
                self.SetItem(list_item)
                even = not even
                i += 1

    def on_select(self, *args):
        index = self.GetFocusedItem()
        ret = self.data[index] if index >= 0 else None
        self.select_cmd(ret)

    def on_activate(self, *args):
        index = self.GetFocusedItem()
        if not index < 0:
            self.activate_cmd(self.data[index])

    def get_selected(self):
        index = self.GetFocusedItem()
        return self.data[index] if not index < 0 else None

    def get_active(self):
        return self.GetFocusedItem()


class ReportList(SimpleList):
    def __init__(self, parent, data=None, border=True, header=True,
                 single_sel=True, virtual=False, alt_color=True,
                 even_color=None, odd_color=None,
                 on_select=None, on_activate=None):
        data = data or []
        SimpleList.__init__(self, parent, data, border, header, single_sel,
                            virtual, alt_color, even_color, odd_color,
                            on_select, on_activate)

    def set_columns(self):
        for item in self.data[0]:
            index = self.data[0].index(item)
            self.InsertColumn(index, const.tr(item))

    def set_data(self, data, alt_color=True):
        even = False
        i = 0
        cols = len(data[0])
        subheader = any(isinstance(i, str) for i in data)
        for item in data[1:]:
            if isinstance(item, list):
                list_item = [const.tr(label) for label in item]
            elif isinstance(item, str):
                list_item = [const.tr(item), ] + ['', ] * (cols - 1)
            else:
                continue
            self.Append(list_item)
            list_item = self.GetItem(i)
            if subheader:
                if isinstance(item, str):
                    list_item.SetBackgroundColour(self.even_color)
                    self.SetItem(list_item)
            elif alt_color:
                color = self.even_color if even else self.odd_color
                list_item.SetBackgroundColour(color)
                self.SetItem(list_item)
                even = not even
            i += 1

    def on_select(self, *args):
        index = self.GetFocusedItem()
        ret = self.data[index + 1] if index >= 0 else None
        self.select_cmd(ret)

    def on_activate(self, *args):
        index = self.GetFocusedItem()
        if not index < 0:
            self.activate_cmd(self.data[index + 1])

    def get_selected(self):
        index = self.GetFocusedItem()
        return self.data[index + 1] if not index < 0 else None


class VirtualList(SimpleList):
    def __init__(self, parent, data=None, border=True, header=True,
                 single_sel=True, virtual=True, alt_color=True,
                 even_color=None, odd_color=None,
                 on_select=None, on_activate=None):
        data = data or []
        SimpleList.__init__(self, parent, data, border, header, single_sel,
                            virtual, alt_color, even_color, odd_color,
                            on_select, on_activate)

    def OnGetItemText(self, item, col):
        return self.get_item_text(item, col)

    def get_item_text(self, item, col):
        """
        Callback method. Should return item text for specified column. 
        """
        return ''

    def OnGetItemImage(self, item):
        return self.get_item_image(item)

    def get_item_image(self, item):
        """
        Callback method. Should return item icon index or -1.
        """
        return -1
