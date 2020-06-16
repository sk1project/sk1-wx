# -*- coding: utf-8 -*-
#
#  Copyright (C) 2015 by Ihor E. Novikov
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

import wal
from sk1 import events
from sk1.pwidgets import BitmapToggle
from sk1.resources import icons, get_icon
from uc2 import sk2const

PLG_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(PLG_DIR, 'images')


def make_artid(name):
    return os.path.join(IMG_DIR, name + '.png')


VALS = [-1.0, 0.0, 1.0]
REV_VALS = [1.0, 0.0, -1.0]

CELL_SIZE = (15, 15)


class OIToggle(BitmapToggle):
    val = (0.0, 0.0)

    def __init__(self, parent, val, state=False, onchange=None):
        self.val = val
        icons_dict = {True: [make_artid('check-yes'), ''],
                      False: [make_artid('check-no'), '']}
        if val == (0.0, 0.0):
            icons_dict = {True: [make_artid('check-yes-center'), ''],
                          False: [make_artid('check-no'), '']}
        BitmapToggle.__init__(self, parent, state, icons_dict, onchange)

    def on_change(self, event):
        if not self.state and self.get_enabled():
            self.set_active(not self.state)
            self.callback(self.val) if self.callback else None


class OrientationIndicator(wal.GridPanel):
    val = (0.0, 0.0)
    callback = None
    toggles = {}

    def __init__(self, parent, val=(0.0, 0.0), onchange=None):
        self.val = val
        self.callback = onchange
        self.toggles = {-1.0: {}, 0.0: {}, 1.0: {}}
        wal.GridPanel.__init__(self, parent, 5, 5, 2, 2)
        for y in REV_VALS:
            for x in VALS:
                state = (x, y) == (0.0, 0.0)
                toggle = OIToggle(self, (x, y), state, self.on_change)
                self.pack(toggle)
                self.toggles[x][y] = toggle
                if x < 1.0:
                    panel = wal.HPanel(self)
                    panel.pack(wal.HLine(self), expand=True)
                    self.pack(panel, fill=True)
            if y > -1.0:
                for i in range(3):
                    panel = wal.VPanel(self)
                    panel.pack(wal.VLine(panel), expand=True)
                    self.pack(panel, fill=True)
                    self.pack(CELL_SIZE) if i < 2 else None

    def on_change(self, val):
        x, y = self.val
        self.toggles[x][y].set_active(False)
        self.val = val
        self.callback(self.val) if self.callback else None

    def reset(self):
        x, y = self.val
        self.toggles[x][y].set_active(False)
        self.val = (0.0, 0.0)
        x, y = self.val
        self.toggles[x][y].set_active(True)

    def get_value(self):
        return self.val

    def set_enable(self, state):
        for y in REV_VALS:
            for x in VALS:
                self.toggles[x][y].set_enable(state)


ORIGIN_ICONS = [icons.L_ORIGIN_CENTER, icons.L_ORIGIN_LL, icons.L_ORIGIN_LU]


class OriginIndicator(wal.Bitmap):
    app = None

    def __init__(self, parent, app):
        self.app = app
        mode = sk2const.DOC_ORIGIN_LL
        wal.Bitmap.__init__(self, parent, get_icon(ORIGIN_ICONS[mode],
                                                   size=wal.DEF_SIZE))
        events.connect(events.DOC_CHANGED, self.update)
        events.connect(events.DOC_MODIFIED, self.update)

    def update(self, *_args):
        if self.app.current_doc:
            mode = self.app.current_doc.methods.get_doc_origin()
            self.set_bitmap(get_icon(ORIGIN_ICONS[mode], size=wal.DEF_SIZE))
