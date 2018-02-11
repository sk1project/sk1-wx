# -*- coding: utf-8 -*-
#
#  Copyright (C) 2015 by Igor E. Novikov
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

import wal
from generic import PrefPanel
from sk1 import _, config
from sk1.pwidgets import CBMiniPalette
from sk1.resources import icons
from uc2 import cms

COLORS = [
    ('#FFFFFF', 'White'),
    ('#D4D0C8', 'Win2k'),
    ('#ECE9D8', 'WinXP'),
    ('#E0DFE3', 'WinXP Silver'),
    ('#F0F0F0', 'Win7'),
    ('#F2F1F0', 'Ubuntu'),
]


class GeneralPrefs(PrefPanel):
    pid = 'General'
    name = _('General')
    title = _('General application preferences')
    icon_id = icons.PD_PROPERTIES

    nb = None
    ui_style = None
    tab_bg = None
    palette = None
    use_tab_colors = None
    newdoc = None
    backup = None
    expbackup = None
    hist_size = None
    hist_menu_size = None
    fcache = None
    stub_buttons = None
    spin_overlay = None
    spin_sep = None
    ubuntu_gm = None
    ubuntu_overlay = None

    def __init__(self, app, dlg, *args):
        PrefPanel.__init__(self, app, dlg)

    def build(self):
        self.nb = wal.Notebook(self)

        # ----------------------

        vpanel = wal.VPanel(self.nb)
        grid = wal.GridPanel(vpanel, rows=2, cols=2, hgap=10, vgap=5)
        grid.pack(wal.Label(grid, _('UI style (*):')))

        items = [_('Classic'), _('Tabbed')]
        self.ui_style = wal.Combolist(grid, items=items)
        self.ui_style.set_active(config.ui_style)
        grid.pack(self.ui_style, fill=True)

        grid.pack(wal.Label(grid, _('Tab panel color:')))
        panel = wal.HPanel(grid)
        self.tab_panel_bg = wal.ColorButton(panel)
        self.tab_panel_bg.set_value(config.tab_panel_bg
                                    or cms.val_255_to_dec(wal.UI_COLORS['bg']))
        self.palette = CBMiniPalette(panel, COLORS,
                                     onclick=self.tab_panel_bg.set_value)
        panel.pack(self.tab_panel_bg)
        panel.pack((10, 5))
        panel.pack(self.palette)
        grid.pack(panel)

        vpanel.pack(grid, align_center=False, padding_all=10)

        txt = _('Custom colors for tab panel')
        self.use_tab_colors = wal.Checkbox(vpanel, txt, config.use_tab_colors,
                                           onclick=self.on_click_use_tab_colors)
        self.on_click_use_tab_colors()
        vpanel.pack(self.use_tab_colors, align_center=False, padding_all=5)

        self.nb.add_page(vpanel, _('UI style'))

        # ----------------------

        vpanel = wal.VPanel(self.nb)
        table = wal.GridPanel(vpanel, rows=1, cols=3, hgap=5, vgap=5)
        vpanel.pack(table, fill=True, padding_all=5)

        grid = wal.VPanel(table)

        txt = _('New document on start')
        self.newdoc = wal.Checkbox(grid, txt, config.new_doc_on_start)
        grid.pack(self.newdoc, align_center=False, padding=3)

        txt = _('Backup on document save')
        self.backup = wal.Checkbox(grid, txt, config.make_backup)
        grid.pack(self.backup, align_center=False, padding=3)

        txt = _('Make font cache on start')
        self.fcache = wal.Checkbox(grid, txt, config.make_font_cache_on_start)
        grid.pack(self.fcache, align_center=False, padding=3)

        txt = _('Backup on export')
        self.expbackup = wal.Checkbox(grid, txt, config.make_export_backup)
        grid.pack(self.expbackup, align_center=False, padding=3)

        txt = _('Show quick access buttons')
        self.stub_buttons = wal.Checkbox(grid, txt, config.show_stub_buttons)
        grid.pack(self.stub_buttons, align_center=False, padding=3)

        table.pack(grid)
        table.pack((15, 5))

        grid = wal.GridPanel(self, rows=2, cols=3, hgap=5, vgap=3)
        grid.pack(wal.Label(grid, _('History log size:')))
        self.hist_size = wal.IntSpin(grid, config.history_size, (10, 1000))
        grid.pack(self.hist_size)
        grid.pack(wal.Label(grid, _('records')))
        grid.pack(wal.Label(grid, _('History menu size:')))
        self.hist_menu_size = wal.IntSpin(grid, config.history_list_size,
                                          (5, 20))
        grid.pack(self.hist_menu_size)
        grid.pack(wal.Label(grid, _('records')))
        table.pack(grid)

        if wal.IS_MSW:
            vpanel.pack((5, 5))

        if not wal.IS_MAC and wal.IS_WX2:
            txt = _('Use overlay for spinbox widgets (*)')
            self.spin_overlay = wal.Checkbox(vpanel, txt, config.spin_overlay)
            vpanel.pack(self.spin_overlay, align_center=False)

        if wal.IS_GTK and wal.IS_WX2:
            txt = _('Separate spin in spinbox widgets (*)')
            self.spin_sep = wal.Checkbox(vpanel, txt, config.spin_sep)
            vpanel.pack(self.spin_sep, align_center=False)

        if wal.IS_UNITY:
            txt = _('Unity related features')
            vpanel.pack(wal.Label(vpanel, txt, fontsize=2, fontbold=True),
                        start_padding=10)
            vpanel.pack(wal.HLine(vpanel), fill=True, padding=2)

            txt = _('Use Unity Global Menu (*)')
            self.ubuntu_gm = wal.Checkbox(vpanel, txt,
                                          config.ubuntu_global_menu)
            vpanel.pack(self.ubuntu_gm, align_center=False)

            txt = _('Allow overlay for scrollbars (*)')
            self.ubuntu_overlay = wal.Checkbox(vpanel, txt,
                                               config.ubuntu_scrollbar_overlay)
            vpanel.pack(self.ubuntu_overlay, align_center=False)

        self.nb.add_page(vpanel, _('Generic features'))
        self.pack(self.nb, fill=True, expand=True, padding=5)

        txt = _('(*) - These options require application restart')
        self.pack(wal.Label(grid, txt, fontsize=-1), align_center=False)

        self.built = True

    def on_click_use_tab_colors(self):
        val = self.use_tab_colors.get_value()
        self.tab_panel_bg.set_enable(val)
        self.palette.set_enable(val)

    def apply_changes(self):
        config.ui_style = self.ui_style.get_active()
        config.tab_panel_bg = self.tab_panel_bg.get_value()
        config.use_tab_colors = self.use_tab_colors.get_value()
        # -----------
        config.new_doc_on_start = self.newdoc.get_value()
        config.make_backup = self.backup.get_value()
        config.make_export_backup = self.expbackup.get_value()
        config.history_size = self.hist_size.get_value()
        config.history_list_size = self.hist_menu_size.get_value()
        config.show_stub_buttons = self.stub_buttons.get_value()
        config.make_font_cache_on_start = self.fcache.get_value()
        if not wal.IS_MAC and wal.IS_WX2:
            config.spin_overlay = self.spin_overlay.get_value()
        if wal.IS_GTK and wal.IS_WX2:
            config.spin_sep = self.spin_sep.get_value()
        if wal.IS_UNITY:
            config.ubuntu_global_menu = self.ubuntu_gm.get_value()
            config.ubuntu_scrollbar_overlay = self.ubuntu_overlay.get_value()

    def restore_defaults(self):
        defaults = config.get_defaults()
        self.ui_style.set_active(defaults['ui_style'])
        self.tab_panel_bg.set_value(defaults['tab_panel_bg'])
        self.use_tab_colors.set_value(defaults['use_tab_colors'])
        # --------
        self.newdoc.set_value(defaults['new_doc_on_start'])
        self.backup.set_value(defaults['make_backup'])
        self.expbackup.set_value(defaults['make_export_backup'])
        self.hist_size.set_value(defaults['history_size'])
        self.hist_menu_size.set_value(defaults['history_list_size'])
        self.stub_buttons.set_value(defaults['show_stub_buttons'])
        self.fcache.set_value(defaults['make_font_cache_on_start'])
        if not wal.IS_MAC and wal.IS_WX2:
            self.spin_overlay.set_value(defaults['spin_overlay'])
        if wal.IS_GTK and wal.IS_WX2:
            self.spin_sep.set_value(defaults['spin_sep'])
        if wal.IS_UNITY:
            self.ubuntu_gm.set_value(defaults['ubuntu_global_menu'])
            self.ubuntu_overlay.set_value(defaults['ubuntu_scrollbar_overlay'])
