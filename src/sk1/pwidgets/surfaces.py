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


class Painter(object):
    def check_config(self, *args):
        pass

    def paint(self):
        pass

    def mouse_left_down(self, point):
        pass

    def mouse_left_up(self, point):
        pass

    def mouse_move(self, point):
        pass


class RulerSurface(wal.RulerCanvas):
    def __init__(self, app, parent, size=20):
        self.app = app
        wal.RulerCanvas.__init__(self, parent, size)
        self.set_bg(wal.WHITE)
        events.connect(events.CONFIG_MODIFIED, self.check_config)

    @property
    def painter(self):
        return self.app.current_doc.corner

    def check_config(self, *args):
        if args[0].startswith('ruler_'):
            self.painter.check_config(*args)
            if args[0] == 'ruler_size':
                self.fix_size(config.ruler_size)
            self.refresh()

    def paint(self):
        self.painter.paint()

    def mouse_left_down(self, point):
        self.painter.mouse_left_down(point)

    def mouse_left_up(self, point):
        self.painter.mouse_left_up(point)

    def mouse_move(self, point):
        self.painter.mouse_move(point)


class HRulerSurface(RulerSurface):
    @property
    def painter(self):
        return self.app.current_doc.hruler


class VRulerSurface(HRulerSurface):
    @property
    def painter(self):
        return self.app.current_doc.vruler
