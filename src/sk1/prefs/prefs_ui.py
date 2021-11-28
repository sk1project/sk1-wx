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
from sk1 import _, config
from sk1.resources import icons
from uc2.utils import fsutils

from .generic import PrefPanel

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
        langs += [item for item in fsutils.listdir(path)
                  if fsutils.isdir(os.path.join(path, item))]
    langs.sort()
    for item in langs:
        LANGS.append(item)


get_langs()


class UiPrefs(PrefPanel):
    pid = 'UI'
    name = _('UI')
    title = _('User interface preferences')
    icon_id = icons.PD_PREFS_UI

    ui_style = None
    tab_style = None

    lang = None
    stub_buttons = None
    spin_overlay = None
    spin_sep = None
    ubuntu_gm = None
    ubuntu_overlay = None

    def __init__(self, app, dlg, *_args):
        PrefPanel.__init__(self, app, dlg)

    def build(self):
        vpanel = wal.VPanel(self)
        grid = wal.GridPanel(vpanel, rows=4, cols=2, hgap=25, vgap=7)

        txt = _('Language (*):')
        grid.pack(wal.Label(grid, txt))
        self.lang = wal.Combolist(grid, items=LANGS)
        index = 0 if config.language == 'system' \
            else LANGS.index(config.language)
        self.lang.set_active(index)
        grid.pack(self.lang, fill=True)

        txt = _('UI style (*):')
        grid.pack(wal.Label(grid, txt))
        items = [_('Classic'), _('Tabbed')]
        self.ui_style = wal.Combolist(grid, items=items)
        self.ui_style.set_active(config.ui_style)
        grid.pack(self.ui_style, fill=True)

        txt = _('Tab style:')
        grid.pack(wal.Label(grid, txt))
        items = [_('Rectangular tabs'),
                 _('Rounded tabs'),
                 _('Flat tabs'),
                 _('Trapezoidal tabs')]
        self.tab_style = wal.Combolist(grid, items=items)
        index = config.tab_style if config.tab_style < len(items) else 0
        self.tab_style.set_active(index)
        grid.pack(self.tab_style, fill=True)

        txt = _('Show quick access buttons')
        grid.pack(wal.Label(grid, txt))
        self.stub_buttons = wal.Switch(grid, config.show_stub_buttons)
        grid.pack(self.stub_buttons)

        vpanel.pack(grid, align_center=False, padding_all=10)

        # ---------------------------------

        int_vp = wal.VPanel(vpanel)
        vpanel.pack(int_vp, fill=True, padding_all=5)

        self.pack(vpanel)
        self.pack((1, 1), expand=True)

        txt = _('(*) - Application restart is required to apply these options')
        self.pack(wal.Label(self, txt, fontsize=-1))

        self.built = True

    def apply_changes(self):
        config.ui_style = self.ui_style.get_active()
        config.tab_style = self.tab_style.get_active()

        config.language = 'system' if not self.lang.get_active() \
            else self.lang.get_active_value()
        config.show_stub_buttons = self.stub_buttons.get_value()

    def restore_defaults(self):
        defaults = config.get_defaults()
        self.ui_style.set_active(defaults['ui_style'])
        self.tab_style.set_active(defaults['tab_style'])
        index = 0 if defaults['language'] == 'system' \
            else LANGS.index(defaults['language'])
        self.lang.set_active(index)
        self.stub_buttons.set_value(defaults['show_stub_buttons'])
