# -*- coding: utf-8 -*-
#
#  Copyright (C) 2018 by Ihor E. Novikov
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

import wal
from sk1 import config

STUB = [wal.ID_NEW, wal.ID_OPEN]


class ContextMenu(wal.Menu):
    app = None
    mw = None
    insp = None
    actions = None
    entries = None
    items = []

    def __init__(self, app, parent, entries=None):
        self.app = app
        self.mw = app.mw
        self.parent = parent
        self.insp = self.app.insp
        self.actions = self.app.actions
        self.entries = entries or STUB
        wal.Menu.__init__(self)
        self.build_menu(self.entries)
        self.items = []

    def destroy(self):
        items = self.__dict__.keys()
        for item in items:
            self.__dict__[item] = None

    def rebuild(self):
        self.build_menu(self.get_entries())

    def build_menu(self, entries):
        for item in self.items:
            self.remove_item(item)
        self.items = []
        for item in entries:
            if item is None:
                self.items.append(self.append_separator())
            else:
                action = self.app.actions[item]
                menuitem = ActionMenuItem(self.parent, self, action)
                self.append_item(menuitem)
                menuitem.update()
                self.items.append(menuitem)

    def get_entries(self):
        return self.entries


class ActionMenuItem(wal.MenuItem):
    def __init__(self, mw, parent, action):
        self.mw = mw
        self.parent = parent
        self.action = action
        action_id = action.action_id
        text = action.get_menu_text()
        if action.is_acc:
            text += '\t' + action.get_shortcut_text()
        wal.MenuItem.__init__(self, parent, action_id, text=text, checkable=action.is_toggle())
        if action.is_icon and not action.is_toggle():
            self.set_bitmap(action.get_icon(config.menu_size, wal.ART_MENU))
        action.register_as_menuitem(self)
        self.bind_to(self.mw, action, action_id)
        # For WX<4
        if action.is_toggle():
            self.set_checkable(True)

    def update(self):
        self.set_enable(self.action.enabled)
        if self.action.is_toggle():
            self.set_active(self.action.active)
