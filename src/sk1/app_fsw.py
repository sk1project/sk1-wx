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

import os

import wal
from sk1 import config, events


class AppFileWatcher(object):
    app = None
    mw = None

    def __init__(self, app, mw):
        self.app = app
        self.mw = mw
        self.timer = wal.CanvasTimer(mw, 1000)
        self.mw.bind_timer(self.on_timer)
        self.socket = os.path.join(self.app.appdata.app_config_dir, 'socket')
        self.lock = os.path.join(self.app.appdata.app_config_dir, 'lock')
        events.connect(events.CONFIG_MODIFIED, self.check_config)
        if config.app_server:
            self.timer.start()
            with open(self.lock, 'wb') as fp:
                fp.write('\n')

    def destroy(self):
        if os.path.exists(self.lock):
            os.remove(self.lock)
        if self.timer.is_running():
            self.timer.stop()

    def check_config(self, *args):
        if config.app_server and not self.timer.is_running():
            self.timer.start()
        elif not config.app_server and self.timer.is_running():
            self.timer.stop()

    def on_timer(self, *args):
        if os.path.exists(self.socket):
            self.mw.raise_window()
            with open(self.socket, 'rb') as fp:
                lines = fp.readlines()
            os.remove(self.socket)
            [self.app.open(item.strip('\n'))
             for item in lines
             if os.path.exists(item.strip('\n'))]
        if not os.path.exists(self.lock):
            with open(self.lock, 'wb') as fp:
                fp.write('\n')
