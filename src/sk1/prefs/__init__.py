# -*- coding: utf-8 -*-
#
#  Copyright (C) 2015-2016 by Igor E. Novikov
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

import logging

import wal
from generic import RootItem
from prefs_canvas import CanvasPrefs
from prefs_cms import CMSPrefs
from prefs_fonts import FontPrefs
from prefs_general import GeneralPrefs
from prefs_ui import UiPrefs
from prefs_palettes import PalettesPrefs
from prefs_printers import PrinterPrefs
from prefs_ruler import RulersPrefs
from sk1 import _, config
from templates import GridPrefs

PREFS_APP = [GeneralPrefs, UiPrefs, CMSPrefs, RulersPrefs,
             PalettesPrefs, FontPrefs,
             # CanvasPrefs,
             PrinterPrefs, ]

LOG = logging.getLogger(__name__)

PREFS_DATA = []


class PrefsDialog(wal.OkCancelDialog):
    current_plugin = None

    splitter = None
    tree_container = None
    tree = None
    container = None
    redo_btn = None

    def __init__(self, parent, title, pid=None):
        self.app = parent.app
        size = config.prefs_dlg_size
        wal.OkCancelDialog.__init__(self, parent, title, size, resizable=True,
                                    margin=0, add_line=False,
                                    button_box_padding=5)
        self.set_minsize(config.prefs_dlg_minsize)
        pid = pid or 'General'
        for item in PREFS_DATA[0]:
            if item.pid == pid:
                self.tree.set_selected(PREFS_DATA[0].index(item))

    def build(self):
        self.panel.pack(wal.PLine(self.panel), fill=True)
        self.splitter = wal.Splitter(self.panel, hidden=True)
        self.panel.pack(self.splitter, expand=True, fill=True)
        self.tree_container = wal.VPanel(self.splitter)
        if not PREFS_DATA:
            items = []
            for class_ in PREFS_APP:
                item = class_(self.app, self, None)
                item.hide()
                items.append(item)
            PREFS_DATA.append(items)
        self.tree = wal.PrefsList(self.tree_container, data=PREFS_DATA[0],
                                  on_select=self.on_select)
        self.tree_container.pack(self.tree, fill=True, expand=True)
        cont = wal.VPanel(self.splitter)
        self.container = wal.HPanel(cont)
        self.container.pack(wal.PLine(self.container), fill=True)
        self.container.pack(
            wal.SplitterSash(self.container, self.splitter), fill=True)
        cont.pack(self.container, fill=True, expand=True)
        sash_pos = config.prefs_sash_pos
        self.splitter.split_vertically(self.tree_container, cont, sash_pos)
        self.splitter.set_min_size(sash_pos)
        self.panel.pack(wal.PLine(self.panel), fill=True)

    def set_dialog_buttons(self):
        wal.OkCancelDialog.set_dialog_buttons(self)
        title = _('Restore defaults')
        self.redo_btn = wal.Button(self.left_button_box, title,
                                   onclick=self.restore_defaults)
        self.left_button_box.pack(self.redo_btn)

    def on_select(self, plugin):
        if not self.current_plugin == plugin and plugin.leaf:
            self.container.hide()
            if not plugin.built:
                plugin.build()
            self.container.pack(plugin, fill=True, expand=True, padding_all=5)
            if self.current_plugin:
                self.container.remove(self.current_plugin)
                self.current_plugin.hide()
            plugin.show()
            self.current_plugin = plugin
            self.container.show()
            plugin.layout()

    def get_plugin_by_pid(self, pid):
        ret = None
        for item in PREFS_DATA[0]:
            if item.pid == pid:
                ret = item
                break
        LOG.info('RET %s', ret)
        return ret

    def apply_changes(self):
        for item in PREFS_DATA[0]:
            if item.built:
                item.apply_changes()

    def restore_defaults(self):
        if self.current_plugin:
            self.current_plugin.restore_defaults()

    def show(self):
        if self.show_modal() == wal.BUTTON_OK:
            self.apply_changes()
        w, h = self.get_size()
        if wal.is_unity_16_04():
            h = max(h - 28, config.prefs_dlg_minsize[1])
        config.prefs_dlg_size = (w, h)
        config.prefs_sash_pos = self.splitter.get_sash_position()
        self.destroy()


def get_prefs_dialog(parent, pid=None):
    dlg = PrefsDialog(parent, _("sK1 Preferences"), pid)
    dlg.show()
    PREFS_DATA.remove(PREFS_DATA[0])
