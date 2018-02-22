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

import wal

from sk1 import events, config
from sk1.pwidgets import ContextMenu
from sk1.resources import pdids


class DocTabs(wal.DocTabs):
    ctx_menu = None

    def __init__(self, app, parent, draw_top=True):
        wal.DocTabs.__init__(self, parent, draw_top=draw_top,
                             painter=config.tab_style)
        ITEMS = [wal.ID_CLOSE, pdids.ID_CLOSE_OTHERS, wal.ID_CLOSE_ALL, None,
                 wal.ID_NEW, wal.ID_OPEN, None,
                 wal.ID_SAVE, wal.ID_SAVEAS, pdids.ID_SAVE_SEL,
                 pdids.ID_SAVEALL, None, pdids.ID_IMPORT, pdids.ID_EXPORT,
                 None, wal.ID_PRINT, None, wal.ID_PROPERTIES]
        self.ctx_menu = ContextMenu(app, self, ITEMS)
        events.connect(events.CONFIG_MODIFIED, self.check_config)

    def check_config(self, *args):
        if args[0] == 'tab_style':
            self.set_painter(config.tab_style)
            self.refresh()

    def add_new_tab(self, doc):
        return wal.DocTabs.add_new_tab(self, LWDocTab(self, doc))

    def remove_tab(self, doc):
        wal.DocTabs.remove_tab(self, self.find_doctab(doc))

    def set_active(self, doc):
        wal.DocTabs.set_active(self, self.find_doctab(doc))

    def show_context_menu(self):
        self.popup_menu(self.ctx_menu)

    def find_doctab(self, doc):
        for tab in self.doc_tabs:
            if doc == tab.doc:
                return tab


class LWDocTab(wal.LWDocTab):
    doc = None

    def __init__(self, parent, doc, active=True):
        self.doc = doc
        self.text = self.doc.doc_name
        wal.LWDocTab.__init__(self, parent, active)

    def set_title(self, title):
        self.saved = self.doc.saved
        wal.LWDocTab.set_title(self, self.doc.doc_name)

    def close(self):
        self.mouse_leaved_tab()
        self.parent.refresh()
        self.doc.app.close(self.doc)

    def mouse_left_down(self, point):
        if wal.LWDocTab.mouse_left_down(self, point):
            if not self.active:
                self.doc.app.set_current_doc(self.doc)

    def mouse_right_down(self):
        if not self.active:
            self.doc.app.set_current_doc(self.doc)
        self.parent.show_context_menu()
