# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013-2018 by Ihor E. Novikov
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
import typing as tp

import wal
from sk1 import appconst, config
from sk1.parts.mdiarea import MDIArea
from sk1.parts.menubar import AppMenuBar
from sk1.parts.stubpanel import AppStubPanel
from sk1.parts.toolbar import build_toolbar


class AppMainWindow(wal.MainWindow):
    menubar = None
    mdi = None
    stub = None
    palette_panel = None
    statusbar = None
    toolbar = None

    def __init__(self, app):
        self.app = app
        wal.MainWindow.__init__(
            self, app, '', config.mw_size,
            maximized=config.mw_maximized,
            on_close=self.app.exit)
        self.set_minsize(config.mw_min_size)
        self.set_icons(os.path.join(config.resource_dir, 'icons', 'generic', 'sk1-icon.ico'))

    def build(self):
        # ----- Menubar
        self.menubar = AppMenuBar(self.app, self)
        self.set_menubar(self.menubar)
        # ----- Toolbar
        if config.ui_style == appconst.GUI_CLASSIC:
            self.toolbar = build_toolbar(self)

        # ----- MDI Area
        self.mdi = MDIArea(self.app, self)
        self.pack(self.mdi, expand=True, fill=True)
        if not config.new_doc_on_start:
            self.mdi.hide()

        # ----- Stub panel
        self.stub = AppStubPanel(self)
        self.pack(self.stub, expand=True, fill=True)
        if config.new_doc_on_start:
            self.stub.hide()

        self.layout()

    def set_title(self, title=''):
        appname = self.app.appdata.app_name
        title = '[%s] - %s' % (title, appname) if title else appname
        wal.MainWindow.set_title(self, title)

    def show_mdi(self, value):
        if value and not self.mdi.is_shown():
            self.stub.hide()
            self.update()
            self.mdi.show()
        elif not value and self.mdi.is_shown():
            self.mdi.hide()
            self.update()
            self.stub.show()
