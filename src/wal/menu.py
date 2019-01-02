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


def get_accelerator_entry(*args):
    return wx.AcceleratorEntry(*args)


class Menu(wx.Menu):
    def __init__(self):
        wx.Menu.__init__(self)

    def append_menu(self, item_id, text, menu):
        self.AppendMenu(item_id, const.tr(text), menu)

    def remove_item(self, item):
        self.RemoveItem(item)

    def append_item(self, item):
        self.AppendItem(item)

    def append_separator(self):
        return self.AppendSeparator()


class MenuItem(wx.MenuItem):
    def __init__(self, parent, action_id, text):
        wx.MenuItem.__init__(self, parent, action_id, text=const.tr(text))

    def bind_to(self, mw, callback, action_id):
        mw.Bind(wx.EVT_MENU, callback, id=action_id)

    def get_enable(self):
        return self.IsEnabled()

    def set_enable(self, enabled):
        if not enabled == self.get_enable():
            self.Enable(enabled)

    def set_checkable(self, val):
        self.SetCheckable(val)

    def is_checked(self):
        return self.IsChecked()

    def is_checkable(self):
        return self.IsCheckable()

    def set_bitmap(self, bmp):
        if bmp and not const.IS_MAC:
            self.SetBitmap(bmp)

    def toggle(self):
        self.Toggle()

    def set_active(self, val):
        if self.is_checkable() and self.is_checked() != val:
            self.toggle()


class MenuBar(wx.MenuBar):
    def __init__(self):
        wx.MenuBar.__init__(self)

    def append_menu(self, menu_id, txt, menu):
        self.Append(menu, const.tr(txt))
