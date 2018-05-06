# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013-2018 by Igor E. Novikov
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

from sk1 import _, events, config
from sk1.resources import icons, get_icon, pdids


class AppStubPanel(wal.StubPanel):
    app = None

    def __init__(self, mw):
        self.app = mw.app
        self.bmp = get_icon(icons.CAIRO_BANNER, size=wal.DEF_SIZE)
        wal.StubPanel.__init__(self, mw)
        bg = wal.DARK_GRAY
        self.set_bg(bg)

        items = ((wal.ID_NEW, icons.PD_STUB_NEW),
                 (wal.ID_OPEN, icons.PD_STUB_OPEN),
                 (pdids.ID_VIEW_LOG, icons.PD_STUB_RECENT))
        for pid, icon in items:
            action = self.app.actions[pid]
            tooltip = _('Open Recent') if pid == pdids.ID_VIEW_LOG \
                else action.get_descr_text()
            icon = get_icon(icon, size=wal.DEF_SIZE)
            self.buttons.append(wal.StubBtn(self, bg, icon, action, tooltip))

        self.buttons[-1].set_active(self.app.history.is_history())

        events.connect(events.HISTORY_CHANGED, self.check_history)
        events.connect(events.CONFIG_MODIFIED, self.update)

    def update(self, *args):
        if args[0] == 'show_stub_buttons':
            self.buttons_visible = config.show_stub_buttons
            self.refresh()

    def check_history(self, *args):
        self.buttons[-1].set_active(self.app.history.is_history())
