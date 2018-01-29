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


class DocTabs(wal.DocTabs):

    def __init__(self, parent):
        wal.DocTabs.__init__(self, parent)

    def add_new_tab(self, doc):
        return wal.DocTabs.add_new_tab(self, LWDocTab(self, doc))

    def remove_tab(self, doc):
        wal.DocTabs.remove_tab(self, doc.docarea.doc_tab)

    def set_active(self, doc):
        wal.DocTabs.set_active(self, doc.docarea.doc_tab)


class LWDocTab(wal.LWDocTab):
    doc = None

    def __init__(self, parent, doc, active=True):
        self.doc = doc
        self.text = self.doc.doc_name
        wal.LWDocTab.__init__(self, parent, active)

    def mouse_left_down(self, point):
        if not self.active:
            self.doc.app.set_current_doc(self.doc)
