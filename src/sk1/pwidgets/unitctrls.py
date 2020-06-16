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
from sk1 import _, events
from sk1.resources import icons, get_icon
from uc2 import uc2const
from uc2.uc2const import point_dict, unit_dict, unit_accuracy


class StaticUnitLabel(wal.Label):
    app = None
    insp = None
    units = uc2const.UNIT_MM

    def __init__(self, app, parent):
        self.app = app
        self.insp = app.insp
        if self.insp.is_doc():
            self.units = app.current_doc.model.doc_units
        text = uc2const.unit_short_names[self.units]
        super(StaticUnitLabel, self).__init__(parent, text)


class UnitLabel(StaticUnitLabel):
    def __init__(self, app, parent):
        super(UnitLabel, self).__init__(app, parent)
        events.connect(events.DOC_CHANGED, self.update)
        events.connect(events.DOC_MODIFIED, self.update)

    def __del__(self):
        events.disconnect(events.DOC_MODIFIED, self.update)
        events.disconnect(events.DOC_CHANGED, self.update)

    def update(self, *args):
        if not self.insp.is_doc():
            return
        if self.units == self.app.current_doc.model.doc_units:
            return
        self.units = self.app.current_doc.model.doc_units
        text = uc2const.unit_short_names[self.units]
        self.set_text(text)


POIN_RANGE = (0.0, 100000.0)
NEGATIVE_POINT_RANGE = (-100000.0, 100000.0)


class StaticUnitSpin(wal.FloatSpin):
    app = None
    insp = None
    ucallback = None
    point_value = 0.0
    point_range = POIN_RANGE
    units = uc2const.UNIT_MM

    def __init__(self, app, parent, val=0.0, step=1.0, onchange=None,
                 onenter=None, can_be_negative=False):
        self.app = app
        self.insp = app.insp
        self.point_value = val
        self.ucallback = onchange
        if can_be_negative:
            self.point_range = NEGATIVE_POINT_RANGE
        if self.insp.is_doc():
            self.units = app.current_doc.model.doc_units
        val = self.point_value * point_dict[self.units]
        super(StaticUnitSpin, self).__init__(parent, val, self.point_range,
                                             step=step,
                                             onchange=self.update_point_value,
                                             onenter=onenter)
        self._set_digits(unit_accuracy[self.units])
        self.set_value(self.point_value * point_dict[self.units])

    def update_point_value(self, *args):
        self.point_value = self.get_value() * unit_dict[self.units]
        if self.ucallback:
            self.ucallback()

    def get_point_value(self):
        return self.point_value

    def set_point_value(self, val):
        if not self.point_value == val:
            self.point_value = val
            self.set_value(self.point_value * point_dict[self.units])

    def set_point_range(self, range_val=POIN_RANGE):
        if range_val:
            self.point_range = range_val
            minv, maxv = self.point_range
            minv *= point_dict[self.units]
            maxv *= point_dict[self.units]
            self.set_range((minv, maxv))


class UnitSpin(StaticUnitSpin):
    def __init__(self, app, parent, val=0.0, step=1.0,
                 onchange=None, onenter=None, can_be_negative=False):
        super(UnitSpin, self).__init__(app, parent, val, step,
                                       onchange, onenter, can_be_negative)
        events.connect(events.DOC_MODIFIED, self.update_units)
        events.connect(events.DOC_CHANGED, self.update_units)

    def __del__(self):
        events.disconnect(events.DOC_MODIFIED, self.update_units)
        events.disconnect(events.DOC_CHANGED, self.update_units)

    def update_units(self, *args):
        if not self.insp.is_doc():
            return
        if self.units == self.app.current_doc.model.doc_units:
            return
        self.units = self.app.current_doc.model.doc_units
        self._set_digits(unit_accuracy[self.units])
        self.set_point_range()
        self.set_value(self.point_value * point_dict[self.units])


class BitmapToggle(wal.Bitmap):
    state = True
    icons_dict = {}
    callback = None

    def __init__(self, parent, state=True, icons_dict=None, onchange=None):
        icons_dict = icons_dict or {}
        self.state = state
        self.callback = onchange
        if icons_dict:
            self.icons_dict = icons_dict
        else:
            self.icons_dict = {
                True: [icons.CTX_RATIO, _("Keep ratio")],
                False: [icons.CTX_NO_RATIO, _("Don't keep ratio")]}
        self.update_icons()
        super(BitmapToggle, self).__init__(parent,
                                           self.icons_dict[self.state][0],
                                           on_left_click=self.on_change)
        if self.icons_dict[self.state][1]:
            self.set_tooltip(self.icons_dict[self.state][1])

    def on_change(self, event):
        self.set_active(not self.state)
        if self.callback:
            self.callback()

    def get_active(self):
        return self.state

    def _get_bitmap(self):
        if not self.enabled and wal.IS_MSW:
            return wal.disabled_bmp(self.icons_dict[self.state][0])
        return self.icons_dict[self.state][0]

    def _get_tooltip(self):
        return self.icons_dict[self.state][1]

    def set_active(self, state):
        self.state = state
        self.set_bitmap(self._get_bitmap())
        tooltip = self._get_tooltip()
        if tooltip:
            self.set_tooltip(tooltip)

    def update_icons(self):
        self.icons_dict[True] = [
            get_icon(self.icons_dict[True][0], size=wal.DEF_SIZE),
            self.icons_dict[True][1]]
        self.icons_dict[False] = [
            get_icon(self.icons_dict[False][0], size=wal.DEF_SIZE),
            self.icons_dict[False][1]]

    def set_icons_dict(self, icons_dict):
        self.icons_dict = icons_dict
        self.update_icons()
        self.set_active(self.state)

    def set_enable(self, value):
        wal.Bitmap.set_enable(self, value)
        self.set_bitmap(self._get_bitmap())


class RatioToggle(BitmapToggle):
    def __init__(self, parent, state=True, onchange=None):
        super(RatioToggle, self).__init__(parent, state, {}, onchange)


class ActionImageSwitch(BitmapToggle):
    action = None

    def __init__(self, parent, action, icons_dict=None, state=False):
        icons_dict = icons_dict or {}
        self.action = action
        super(ActionImageSwitch, self).__init__(parent, state, icons_dict,
                                                onchange=action)
        action.register(self)

    def update(self):
        self.set_active(self.action.active)


class AngleSpin(wal.FloatSpin):
    ucallback = None
    angle_value = 0.0

    def __init__(self, parent, val=0.0, val_range=(-360.0, 360.0),
                 onchange=None, onenter=None, check_focus=False):
        self.angle_value = val
        self.ucallback = onchange
        super(AngleSpin, self).__init__(parent, val, val_range,
                                        step=1.0,
                                        onchange=self.update_angle_value,
                                        onenter=onenter,
                                        check_focus=check_focus)

    def update_angle_value(self, *args):
        self.angle_value = self.get_value() * math.pi / 180.0
        if self.ucallback:
            self.ucallback()

    def get_angle_value(self):
        return self.angle_value

    def set_angle_value(self, val):
        if not self.angle_value == val:
            self.angle_value = val
            self.set_value(round(self.angle_value * 180 / math.pi, 2))
