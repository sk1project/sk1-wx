# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2015-2018 by Igor E. Novikov
#
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
#
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
#
# 	You should have received a copy of the GNU General Public License
# 	along with this program.  If not, see <https://www.gnu.org/licenses/>.

from basic import HPanel, VPanel
from gctrls import ImageToggleButton


class ModeToggleButton(ImageToggleButton):
    keeper = None
    mode = 0
    callback = None
    allow_off = False

    def __init__(self, parent, keeper, mode, icons, names, on_change=None,
                 allow_off=False):
        self.keeper = keeper
        self.mode = mode
        self.callback = on_change
        self.allow_off = allow_off
        ImageToggleButton.__init__(
            self, parent, False, icons[mode],
            tooltip=names[mode], onchange=self.change)

    def change(self):
        if not self.get_active():
            if self.keeper.mode == self.mode and not self.allow_off:
                self.set_active(True)
            elif self.allow_off:
                if self.callback:
                    self.callback(None)
        else:
            if not self.keeper.mode == self.mode:
                if self.callback:
                    self.callback(self.mode)

    def set_mode(self, mode):
        if not self.mode == mode:
            if self.get_active():
                self.set_active(False)
        else:
            if not self.get_active():
                self.set_active(True)


class HToggleKeeper(HPanel):
    mode = 0
    mode_buts = None
    modes = None
    callback = None
    allow_none = False

    def __init__(self, parent, modes, icons, names, on_change=None,
                 allow_none=False):
        self.modes = modes
        self.mode_buts = []
        self.callback = on_change
        self.allow_none = allow_none
        HPanel.__init__(self, parent)
        for item in self.modes:
            but = ModeToggleButton(
                self, self, item, icons, names,
                self.changed, self.allow_none)
            self.mode_buts.append(but)
            self.pack(but)

    def set_enable(self, val):
        for item in self.mode_buts:
            item.set_enable(val)

    def changed(self, mode):
        self.mode = mode
        for item in self.mode_buts:
            item.set_mode(mode)
        if self.callback:
            self.callback(mode)

    def set_mode(self, mode):
        self.mode = mode
        for item in self.mode_buts:
            item.set_mode(mode)

    def get_mode(self):
        return self.mode


class VToggleKeeper(VPanel):
    mode = 0
    mode_buts = None
    modes = None
    callback = None
    allow_none = False

    def __init__(self, parent, modes, icons, names, on_change=None,
                 allow_none=False):
        self.modes = modes
        self.mode_buts = []
        self.callback = on_change
        self.allow_none = allow_none
        VPanel.__init__(self, parent)
        for item in self.modes:
            but = ModeToggleButton(
                self, self, item, icons, names,
                self.changed, self.allow_none)
            self.mode_buts.append(but)
            self.pack(but)

    def set_enable(self, val):
        for item in self.mode_buts:
            item.set_enable(val)

    def changed(self, mode):
        self.mode = mode
        for item in self.mode_buts:
            item.set_mode(mode)
        if self.callback:
            self.callback(mode)

    def set_mode(self, mode):
        self.mode = mode
        for item in self.mode_buts:
            item.set_mode(mode)

    def get_mode(self):
        return self.mode