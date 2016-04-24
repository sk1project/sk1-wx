# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2013 by Igor E. Novikov
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
# 	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math

import wal

from uc2 import uc2const
from uc2.uc2const import point_dict, unit_dict, unit_accuracy

from wal import Label, FloatSpin, const

from sk1 import _, config, events
from sk1.resources import icons, get_icon

class StaticUnitLabel(Label):

	app = None
	insp = None
	units = uc2const.UNIT_MM

	def __init__(self, app, parent):
		self.app = app
		self.insp = app.insp
		if self.insp.is_doc(): self.units = app.current_doc.model.doc_units
		text = uc2const.unit_short_names[self.units]
		Label.__init__(self, parent, text)

class UnitLabel(StaticUnitLabel):

	def __init__(self, app, parent):
		StaticUnitLabel.__init__(self, app, parent)
		events.connect(events.DOC_CHANGED, self.update)
		events.connect(events.DOC_MODIFIED, self.update)

	def __del__(self):
		events.disconnect(events.DOC_MODIFIED, self.update)
		events.disconnect(events.DOC_CHANGED, self.update)

	def update(self, *args):
		if not self.insp.is_doc(): return
		if self.units == self.app.current_doc.model.doc_units: return
		self.units = self.app.current_doc.model.doc_units
		text = uc2const.unit_short_names[self.units]
		self.set_text(text)

class UnitSpin(FloatSpin):

	app = None
	insp = None
	ucallback = None
	point_value = 0.0
	units = uc2const.UNIT_MM

	def __init__(self, app, parent, val=0.0, step=1.0,
				 onchange=None, onenter=None, can_be_negative=False):
		self.app = app
		self.insp = app.insp
		self.point_value = val
		self.ucallback = onchange
		val_range = (0.0, 100000.0)
		if can_be_negative:val_range = (-100000.0, 100000.0)
		if self.insp.is_doc(): self.units = app.current_doc.model.doc_units
		val = self.point_value * point_dict[self.units]
		FloatSpin.__init__(self, parent, val, val_range,
						step=step, width=5,
						onchange=self.update_point_value, onenter=onenter,
						spin_overlay=config.spin_overlay)
		events.connect(events.DOC_MODIFIED, self.update_units)
		events.connect(events.DOC_CHANGED, self.update_units)
		self._set_digits(unit_accuracy[self.units])
		self.set_value(self.point_value * point_dict[self.units])

	def __del__(self):
		events.disconnect(events.DOC_MODIFIED, self.update_units)
		events.disconnect(events.DOC_CHANGED, self.update_units)

	def update_point_value(self, *args):
		self.point_value = self.get_value() * unit_dict[self.units]
		if self.ucallback: self.ucallback()

	def get_point_value(self):
		return self.point_value

	def set_point_value(self, val):
		if not self.point_value == val:
			self.point_value = val
			self.set_value(self.point_value * point_dict[self.units])

	def update_units(self, *args):
		if not self.insp.is_doc(): return
		if self.units == self.app.current_doc.model.doc_units: return
		self.units = self.app.current_doc.model.doc_units
		self._set_digits(unit_accuracy[self.units])
		self.set_value(self.point_value * point_dict[self.units])

class BitmapToggle(wal.Bitmap):

	state = True
	icons_dict = {}
	callback = None

	def __init__(self, parent, state=True, icons_dict={}, onchange=None):
		self.state = state
		self.callback = onchange
		if icons_dict:
			self.icons_dict = icons_dict
		else:
			self.icons_dict = { True:[icons.CTX_RATIO, _("Keep ratio")],
					False:[icons.CTX_NO_RATIO, _("Don't keep ratio")]}
		self.update_icons()
		wal.Bitmap.__init__(self, parent, self.icons_dict[self.state][0],
						on_left_click=self.on_change)
		if self.icons_dict[self.state][1]:
			self.set_tooltip(self.icons_dict[self.state][1])

	def on_change(self, event):
		self.set_active(not self.state)
		if self.callback: self.callback()

	def get_active(self):
		return self.state
	
	def _get_bitmap(self):
		if not self.enabled and wal.is_msw():
			return wal.disabled_bmp(self.icons_dict[self.state][0])
		return self.icons_dict[self.state][0]
	
	def _get_tooltip(self):
		return self.icons_dict[self.state][1]

	def set_active(self, state):
		self.state = state
		self.set_bitmap(self._get_bitmap())
		tooltip=self._get_tooltip()
		if tooltip: self.set_tooltip(tooltip)

	def update_icons(self):
		self.icons_dict[True] = [get_icon(self.icons_dict[True][0],
										size=const.DEF_SIZE),
							self.icons_dict[True][1]]
		self.icons_dict[False] = [get_icon(self.icons_dict[False][0],
										size=const.DEF_SIZE),
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
		BitmapToggle.__init__(self, parent, state, {}, onchange)

class ActionImageSwitch(BitmapToggle):

	action = None

	def __init__(self, parent, action, icons_dict={}, state=False):
		self.action = action
		BitmapToggle.__init__(self, parent, state, icons_dict,
							onchange=action.do_call)
		action.register(self)

	def update(self):
		self.set_active(self.action.active)

class AngleSpin(FloatSpin):

	ucallback = None
	angle_value = 0.0

	def __init__(self, parent, val=0.0, val_range=(-360.0, 360.0),
				 onchange=None, onenter=None, check_focus=False):
		self.angle_value = val
		self.ucallback = onchange
		FloatSpin.__init__(self, parent, val, val_range, step=1.0, width=5,
						onchange=self.update_angle_value, onenter=onenter,
						check_focus=check_focus, spin_overlay=config.spin_overlay)

	def update_angle_value(self, *args):
		self.angle_value = self.get_value() * math.pi / 180.0
		if self.ucallback: self.ucallback()

	def get_angle_value(self):
		return self.angle_value

	def set_angle_value(self, val):
		if not self.angle_value == val:
			self.angle_value = val
			self.set_value(round(self.angle_value * 180 / math.pi, 2))
