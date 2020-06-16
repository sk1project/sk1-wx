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

import math

import wal

from uc2.sk2const import ARC_ARC, ARC_CHORD, ARC_PIE_SLICE

from sk1 import _, events
from sk1.resources import icons
from sk1.pwidgets import BitmapToggle
from sk1.pwidgets import AngleSpin
from .base import CtxPlugin

CIRCLE_TYPES = [ARC_ARC, ARC_CHORD, ARC_PIE_SLICE]


class CirclePlugin(CtxPlugin):
    name = 'CirclePlugin'
    update_flag = False
    circle_type = ARC_CHORD
    start = 0
    end = 0
    toggles = {}

    target = None
    orig_type = ARC_CHORD
    orig_start = 0
    orig_end = 0

    slider = None
    angle_spin = None
    switch = None

    def __init__(self, app, parent):
        CtxPlugin.__init__(self, app, parent)
        events.connect(events.DOC_CHANGED, self.update)
        events.connect(events.SELECTION_CHANGED, self.update)

    def build(self):

        self.toggles[ARC_ARC] = wal.ImageToggleButton(self, False,
                                                      icons.CTX_CIRCLE_ARC,
                                                      onchange=self.toggled,
                                                      tooltip=_('Arc'))
        self.pack(self.toggles[ARC_ARC])

        self.toggles[ARC_CHORD] = wal.ImageToggleButton(self, False,
                                                        icons.CTX_CIRCLE_CHORD,
                                                        onchange=self.toggled,
                                                        tooltip=_('Chord'))
        self.pack(self.toggles[ARC_CHORD])

        idx = ARC_PIE_SLICE
        self.toggles[idx] = wal.ImageToggleButton(self, False,
                                                  icons.CTX_CIRCLE_PIE_SLICE,
                                                  onchange=self.toggled,
                                                  tooltip=_('Pie slice'))
        self.pack(self.toggles[ARC_PIE_SLICE])

        self.slider = wal.Slider(self, 0, (0, 360),
                                 onchange=self.slider_changes,
                                 on_final_change=self.slider_final_changes)
        self.pack(self.slider, padding=2)

        self.angle_spin = AngleSpin(self, onchange=self.angle_changes)
        self.pack(self.angle_spin, padding=2)

        txt1 = _('Start angle')
        txt2 = _('End angle')
        icons_dict = {True: [icons.CTX_CIRCLE_START_ANGLE, txt1, ],
                      False: [icons.CTX_CIRCLE_END_ANGLE, txt2, ], }
        self.switch = BitmapToggle(self, True, icons_dict, self.switched)
        self.pack(self.switch, padding=2)

    def update(self, *args):
        if self.insp.is_selection():
            sel = self.app.current_doc.selection
            if len(sel.objs) == 1 and self.insp.is_obj_circle(sel.objs[0]):
                obj = sel.objs[0]
                self.circle_type = obj.circle_type
                self.start = obj.angle1
                self.end = obj.angle2
                self.update_flag = True
                for item in CIRCLE_TYPES:
                    self.toggles[item].set_active(item == self.circle_type)
                self.update_flag = False
                self.switched()
                if not obj == self.target:
                    self.target = obj
                    self.store_props()

    def store_props(self):
        self.orig_type = self.target.circle_type
        self.orig_start = self.target.angle1
        self.orig_end = self.target.angle2

    def toggled(self, *args):
        if self.update_flag:
            return
        self.update_flag = True
        val = -1
        for item in CIRCLE_TYPES:
            if self.toggles[item].get_active() and item != self.circle_type:
                val = item
            elif self.toggles[item].get_active() and item == self.circle_type:
                self.toggles[item].set_active(False)
        if val < 0:
            self.toggles[self.circle_type].set_active(True)
        else:
            self.circle_type = val
        self.update_flag = False
        self.apply_changes(True)

    def switched(self, *args):
        self.update_flag = True
        if self.switch.get_active():
            self.slider.set_value(int(self.start * 180.0 / math.pi))
            self.angle_spin.set_angle_value(self.start)
        else:
            self.slider.set_value(int(self.end * 180.0 / math.pi))
            self.angle_spin.set_angle_value(self.end)
        self.update_flag = False

    def angle_changes(self, *args):
        if self.update_flag:
            return
        if self.switch.get_active():
            self.start = self.angle_spin.get_angle_value()
        else:
            self.end = self.angle_spin.get_angle_value()
        self.apply_changes(True)

    def slider_changes(self, *args):
        if self.update_flag:
            return
        val = self.slider.get_value() * math.pi / 180.0
        if self.switch.get_active():
            self.start = val
        else:
            self.end = val
        self.apply_changes()

    def slider_final_changes(self, *args):
        if self.update_flag:
            return
        val = self.slider.get_value() * math.pi / 180.0
        if self.switch.get_active():
            self.start = val
        else:
            self.end = val
        self.apply_changes(True)

    def apply_changes(self, final=False):
        if self.insp.is_selection():
            sel = self.app.current_doc.selection
            if len(sel.objs) == 1 and self.insp.is_obj_circle(sel.objs[0]):
                obj = sel.objs[0]
                api = self.app.current_doc.api
                if final:
                    api.set_circle_properties_final(self.circle_type,
                                                    self.start, self.end,
                                                    self.orig_type,
                                                    self.orig_start,
                                                    self.orig_end)
                    self.store_props()
                elif not self.start == obj.angle1 or \
                        not self.end == obj.angle2:
                    api.set_circle_properties(self.circle_type,
                                              self.start, self.end)
