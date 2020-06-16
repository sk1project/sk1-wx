# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013 by Ihor E. Novikov
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

from sk1 import _
from sk1.resources import icons, get_bmp, pdids
from sk1.pwidgets import AngleSpin, ActionButton

from .base import CtxPlugin, ActionCtxPlugin


class RotatePlugin(CtxPlugin):
    name = 'RotatePlugin'
    angle_spin = None

    def __init__(self, app, parent):
        CtxPlugin.__init__(self, app, parent)

    def build(self):
        bmp = get_bmp(self, icons.CTX_ROTATE, _('Rotate selection'))
        self.pack(bmp, padding=2)

        self.angle_spin = AngleSpin(self, onenter=self.apply_changes)
        self.pack(self.angle_spin, padding=2)

        self.pack((2, 2))

        rot_left = ActionButton(self, self.actions[pdids.ID_ROTATE_LEFT])
        self.pack(rot_left)

        rot_right = ActionButton(self, self.actions[pdids.ID_ROTATE_RIGHT])
        self.pack(rot_right)

    def apply_changes(self, *_args):
        val = self.angle_spin.get_angle_value()
        if val != 0.0:
            self.app.current_doc.api.rotate_selected(val)


class MirrorPlugin(ActionCtxPlugin):
    name = 'MirrorPlugin'
    ids = [pdids.ID_MIRROR_H, pdids.ID_MIRROR_V]
