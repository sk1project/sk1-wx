# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013 by Igor E. Novikov
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
from sk1 import events
from sk1 import resources


class AppAction(object):
    action_id = None
    callback = None
    channels = []
    validator = None
    checker = None
    callable_args = []
    validator_args = []
    checker_args = []

    widgets = []
    toolbar = None
    menuitem = []
    enabled = True
    active = False
    is_acc = False
    acc_entry = None
    global_accs = []

    def __init__(self, action_id, callback, channels=None,
                 validator=None, checker=None,
                 callable_args=None, validator_args=None, checker_args=None):

        self.action_id = action_id
        self.is_acc = action_id in resources.ACC_KEYS
        if self.is_acc:
            self.acc_entry, self.global_accs = resources.get_accentry_by_id(
                self.action_id)
        if not self.acc_entry:
            self.is_acc = False
        self.is_icon = action_id in resources.ART_IDS
        self.callback = callback
        self.channels = channels or []
        self.validator = validator
        self.checker = checker
        self.callable_args = callable_args or []
        self.validator_args = validator_args or []
        self.checker_args = checker_args or []

        self.widgets = []
        self.menuitem = []

        if channels:
            for channel in channels:
                events.connect(channel, self.receiver)

    def update(self):
        for widget in self.widgets:
            if not wal.IS_WX2:
                if widget not in self.menuitem:
                    widget.update()
            else:
                widget.update()
        if self.toolbar is not None and not wal.IS_MAC:
            self.toolbar.EnableTool(self.action_id, self.enabled)
            self.toolbar.SetToolShortHelp(self.action_id,
                                          wal.tr(self.get_descr_text()))

    def register(self, widget):
        self.widgets.append(widget)
        self.update()

    def register_as_tool(self, toolbar):
        self.toolbar = toolbar

    def register_as_menuitem(self, item):
        self.menuitem.append(item)
        self.widgets.append(item)
        if wal.IS_WX2:
            self.update()

    def unregister(self, widget):
        if widget in self.widgets:
            self.widgets.remove(widget)
        if widget in self.menuitem:
            self.menuitem.remove(widget)
        self.update()

    def receiver(self, *args):
        if self.validator_args:
            self.set_enable(self.validator(*self.validator_args))
        else:
            self.set_enable(self.validator())
        if self.is_toggle() and self.enabled:
            if self.checker_args:
                self.set_active(self.checker(*self.checker_args))
            else:
                self.set_active(self.checker())

    def set_enable(self, enabled):
        if not enabled == self.enabled:
            self.enabled = enabled
            for widget in self.widgets:
                widget.set_enable(self.enabled)
            if self.toolbar is not None and not wal.IS_MAC:
                self.toolbar.EnableTool(self.action_id, self.enabled)

    def set_active(self, active):
        if not active == self.active:
            self.active = active
            for widget in self.widgets:
                widget.set_active(self.active)

    def __call__(self, *args, **kwargs):
        if self.enabled:
            if self.callable_args:
                self.callback(*self.callable_args)
            else:
                self.callback()
        if self.is_toggle():
            if self.checker_args:
                self.set_active(self.checker(*self.checker_args))
            else:
                self.set_active(self.checker())

    def get_artid(self):
        if self.is_icon:
            return resources.get_art_by_id(self.action_id)
        return None

    def get_icon(self, size=(16, 16), client=wal.ART_OTHER):
        if self.is_icon:
            return resources.get_bitmap_by_id(self.action_id, client, size)
        return None

    def get_menu_text(self):
        return resources.get_menu_text(self.action_id)

    def get_tooltip_text(self):
        txt = resources.get_tooltip_text(self.action_id)
        if self.is_acc:
            shortcut = self.get_shortcut_text()
            txt = '%s (%s)' % (txt, shortcut)
        return txt

    def get_descr_text(self):
        txt = resources.get_descr_text(self.action_id)
        if self.is_acc:
            shortcut = self.get_shortcut_text()
            txt = '%s (%s)' % (txt, shortcut)
        return txt

    def get_shortcut_text(self):
        if self.is_acc:
            return wal.untr(self.acc_entry.ToString())
        return ''

    def is_toggle(self):
        return self.checker is not None


class ActionButton(wal.ImageButton):
    action = None

    def __init__(self, parent, action):
        self.action = action
        artid = action.get_artid()
        tooltip = action.get_tooltip_text()
        text = tooltip if artid is None else ''
        native = False if wal.IS_WINXP else True
        size = wal.DEF_SIZE
        super(ActionButton, self).__init__(parent, artid, size, text, tooltip,
                                           native=native,
                                           onclick=action)
        action.register(self)

    def update(self):
        self.set_enable(self.action.enabled)


class ActionToggle(wal.ImageToggleButton):
    action = None

    def __init__(self, parent, action):
        self.action = action
        artid = action.get_artid()
        tooltip = action.get_tooltip_text()
        text = tooltip if artid is None else ''
        native = False if wal.IS_WINXP else True
        size = wal.DEF_SIZE
        value = action.checker()
        super(ActionToggle, self).__init__(
            parent, value, artid, size, text, tooltip,
            native=native,
            onchange=action)
        action.register(self)

    def update(self):
        self.set_enable(self.action.enabled)
        self.set_value(self.action.checker(), silent=True)
