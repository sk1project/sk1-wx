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

from sk1.pwidgets import ActionButton


class CtxPlugin(wal.HPanel):
    app = None
    insp = None
    proxy = None
    actions = None

    name = 'Plugin'

    def __init__(self, app, parent):
        self.app = app
        self.parent = parent
        self.insp = self.app.insp
        self.actions = self.app.actions
        wal.HPanel.__init__(self, parent)
        self.build()
        self.pack(wal.VLine(self), fill=True, padding=3)
        self.hide()

    def update(self, *args): pass

    def build(self): pass


class ActionCtxPlugin(CtxPlugin):
    ids = []

    def __init__(self, app, parent):
        CtxPlugin.__init__(self, app, parent)

    def build(self):
        for item in self.ids:
            if item is None:
                self.pack(wal.VLine(self), fill=True, padding=3)
            else:
                btn = ActionButton(self, self.actions[item])
                self.pack(btn, padding=1)
