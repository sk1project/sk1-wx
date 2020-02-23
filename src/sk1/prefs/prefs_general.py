# -*- coding: utf-8 -*-
#
#  Copyright (C) 2015-2018 by Ihor E. Novikov
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

import os

import wal
from generic import PrefPanel
from sk1 import _, config
from sk1.resources import icons
from uc2.utils import fsutils

COLORS = [
    ('#FFFFFF', 'White'),
    ('#D4D0C8', 'Win2k'),
    ('#ECE9D8', 'WinXP'),
    ('#E0DFE3', 'WinXP Silver'),
    ('#F0F0F0', 'Win7'),
    ('#F2F1F0', 'Ubuntu'),
]

LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR']

LANGS = []


def get_langs():
    if not LANGS:
        LANGS.append(_('system'))
    path = os.path.join(config.resource_dir, 'locales')
    langs = ['en', ]
    if fsutils.exists(path):
        langs += [item for item in os.listdir(fsutils.get_sys_path(path))
                  if fsutils.isdir(os.path.join(path, item))]
    langs.sort()
    for item in langs:
        LANGS.append(item)


get_langs()


class GeneralPrefs(PrefPanel):
    pid = 'General'
    name = _('General')
    title = _('General application preferences')
    icon_id = icons.PD_PREFS_GENERAL

    newdoc = None
    backup = None
    expbackup = None
    hist_size = None
    hist_menu_size = None
    log_level = None
    fcache = None
    server = None

    def __init__(self, app, dlg, *_args):
        PrefPanel.__init__(self, app, dlg)

    def build(self):
        space = (120, 1)

        table = wal.GridPanel(self, rows=8, cols=3, hgap=5, vgap=7)

        txt = _('New document on start')
        table.pack(wal.Label(table, txt))
        table.pack(space)
        self.newdoc = wal.Switch(table, config.new_doc_on_start)
        table.pack(self.newdoc)

        txt = _('Backup on document save')
        table.pack(wal.Label(table, txt))
        table.pack(space)
        self.backup = wal.Switch(table, config.make_backup)
        table.pack(self.backup)

        txt = _('Backup on export')
        table.pack(wal.Label(table, txt))
        table.pack(space)
        self.expbackup = wal.Switch(table, config.make_export_backup)
        table.pack(self.expbackup)

        txt = _('Make font cache on start')
        table.pack(wal.Label(table, txt))
        table.pack(space)
        self.fcache = wal.Switch(table, config.make_font_cache_on_start)
        table.pack(self.fcache)

        txt = _('Run as server')
        table.pack(wal.Label(table, txt))
        table.pack(space)
        self.server = wal.Switch(table, config.app_server)
        table.pack(self.server)

        txt = _('History log size:')
        table.pack(wal.Label(table, txt))
        table.pack(space)
        self.hist_size = wal.IntSpin(table, config.history_size, (10, 1000))
        table.pack(self.hist_size)

        txt = _('History menu size:')
        table.pack(wal.Label(table, txt))
        table.pack(space)
        self.hist_menu_size = wal.IntSpin(
            table, config.history_list_size, (5, 20))
        table.pack(self.hist_menu_size)

        txt = _('Logging level (*):')
        table.pack(wal.Label(table, txt))
        table.pack(space)
        self.log_level = wal.Combolist(table, items=LEVELS)
        self.log_level.set_active(LEVELS.index(config.log_level))
        table.pack(self.log_level)

        self.pack(table)
        self.pack((1, 1), expand=True)

        txt = _('(*) - Application restart is required to apply these options')
        self.pack(wal.Label(self, txt, fontsize=-1))

        self.built = True

    def apply_changes(self):
        config.new_doc_on_start = self.newdoc.get_value()
        config.make_backup = self.backup.get_value()
        config.make_export_backup = self.expbackup.get_value()
        config.app_server = self.server.get_value()
        config.history_size = self.hist_size.get_value()
        config.history_list_size = self.hist_menu_size.get_value()
        config.log_level = self.log_level.get_active_value()
        config.make_font_cache_on_start = self.fcache.get_value()

    def restore_defaults(self):
        defaults = config.get_defaults()
        self.newdoc.set_value(defaults['new_doc_on_start'])
        self.backup.set_value(defaults['make_backup'])
        self.expbackup.set_value(defaults['make_export_backup'])
        self.server.set_value(defaults['app_server'])
        self.hist_size.set_value(defaults['history_size'])
        self.hist_menu_size.set_value(defaults['history_list_size'])
        self.log_level.set_active(LEVELS.index(defaults['log_level']))
        self.fcache.set_value(defaults['make_font_cache_on_start'])
