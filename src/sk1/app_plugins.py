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
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import os

from sk1 import _, config, get_sys_path
from wal import VPanel
from uc2.utils import fsutils

LOG = logging.getLogger(__name__)


def check_package(path, name):
    full_path = os.path.join(path, name)
    if not os.path.isdir(full_path) or name[0] == '.':
        return False
    py_file = os.path.join(full_path, '__init__.py')
    pyc_file = os.path.join(full_path, '__init__.pyc')
    return fsutils.exists(py_file) or fsutils.exists(pyc_file)


def scan_plugins(app):
    ret = {}
    for path in config.plugin_dirs:
        path = get_sys_path(path)
        plgs = [item for item in os.listdir(path) if check_package(path, item)]
        if plgs:
            bn = os.path.basename(path)
            for item in plgs:
                try:
                    pkg = __import__(bn + '.' + item)
                    plg_mod = getattr(pkg, item)
                    pobj = plg_mod.get_plugin(app)
                    ret[pobj.pid] = pobj
                except Exception as e:
                    LOG.error('Error while importing <%s> plugin %s', item, e)
    return ret


class RsPlugin:
    pid = 'plugin'
    name = _('plugin')
    activated = False
    app = None
    panel = None
    icon = None
    plg_tab = None

    def __init__(self, app):
        self.app = app

    def build_ui(self): pass

    def activate(self):
        if not self.activated:
            self.panel = VPanel(self.app.plg_area.container)
            self.activated = True
            self.build_ui()

    def show(self, *args):
        self.panel.show()
        self.show_signal(*args)

    def hide(self):
        self.panel.hide()
        self.hide_signal()

    def show_signal(self, *args):
        pass

    def hide_signal(self):
        pass

    def is_shown(self):
        return self.panel.is_shown()
