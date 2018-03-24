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

import datetime
import os
import time

from sk1 import config, appconst, events
from uc2.utils.fs import path_unicode


class AppHistoryManager:
    app = None
    history = []
    history_file = None

    def __init__(self, app):
        self.app = app
        config_dir = self.app.appdata.app_config_dir
        self.history_file = os.path.join(config_dir, 'history.cfg')
        self.read_history()

    def read_history(self):
        if os.path.isfile(self.history_file):
            with open(self.history_file, 'rb') as fp:
                lines = [line.strip(' \n\r') for line in fp.readlines()]
                for line in lines:
                    items = line.split('\t')
                    if len(items) == 3:
                        self.history.append([int(items[0]),
                                             items[1], int(items[2])])

    def save_history(self):
        with open(self.history_file, 'wb') as fp:
            for item in self.history:
                state, path, timestamp = str(item[0]), item[1], str(item[2])
                fp.write('%s\t%s\t%s\n' % (state, path, timestamp))
        events.emit(events.HISTORY_CHANGED)

    def add_entry(self, path, operation=appconst.OPENED):
        if not len(self.history) < config.history_size:
            self.history = self.history[1:]
        self.history.append([operation, path, int(time.time())])
        self.save_history()

    def clear_history(self):
        self.history = []
        self.save_history()

    def is_empty(self):
        return not self.history

    def is_history(self):
        if self.history:
            return True
        return False

    def is_more(self):
        return len(self.history) > config.history_list_size

    def get_menu_entries(self):
        entries = []
        if not self.history:
            return entries
        i = 1
        counter = 0
        ret = []
        while counter < config.history_list_size:
            item = self.history[-i]
            if not item[1] in entries:
                path = item[1]
                entries.append(path)
                filename = os.path.basename(path)
                ret.append([path_unicode(filename + ' [' + path + ']'), path])
                counter += 1
            i += 1
            if i > len(self.history):
                break
        return ret

    def get_history_entries(self):
        ret = []
        for item in self.history:
            path = item[1]
            unicode_path = path_unicode(path).encode('utf-8')
            filename = path_unicode(os.path.basename(path)).encode('utf-8')
            timestamp = datetime.datetime.fromtimestamp(item[2])
            timestr = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            ret.append([item[0], filename, unicode_path, path, timestr])
        ret.reverse()
        return ret
