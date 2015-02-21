# -*- coding: utf-8 -*-
#
#	Copyright (C) 2013 by Igor E. Novikov
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import wx

from sk1 import _, config, events
from sk1.resources import icons, get_bmp
from sk1.widgets import LEFT, CENTER, FloatSpin, Slider, VPanel, HORIZONTAL
from sk1.pwidgets import RatioToggle, BitmapToggle
from generic import CtxPlugin

class RectanglePlugin(CtxPlugin):

	name = 'RectanglePlugin'
	corners = [0, 0, 0, 0]
	update_flag = False
	active_corner = 0

	def __init__(self, app, parent):
		CtxPlugin.__init__(self, app, parent)
		events.connect(events.DOC_CHANGED, self.update)
		events.connect(events.SELECTION_CHANGED, self.update)

	def build(self):
		bmp = get_bmp(self, icons.CTX_ROUNDED_RECT, _('Rounded rectangle'))
		self.add(bmp, 0, LEFT | CENTER, 2)

		self.slider = Slider(self, 0, (0, 100), onchange=self.slider_changes)
		self.add(self.slider, 0, LEFT | CENTER, 2)

		self.num_spin = FloatSpin(self, 0, (0.0, 100.0), 1.0, 0,
							width=3, onchange=self.changes,
							spin_overlay=config.spin_overlay)
		self.add(self.num_spin, 0, LEFT | CENTER, 2)

		self.switch = RectAngleSwitch(self, onchange=self.switch_changed)
		self.add(self.switch, 0, LEFT | CENTER, 3)
		self.switch.hide()

		self.keep_ratio = RatioToggle(self, onchange=self.lock_changed)
		self.add(self.keep_ratio, 0, LEFT | CENTER, 3)

	def lock_changed(self, *args):
		self.switch.set_visible(not self.keep_ratio.get_active())
		self.parent.Layout()
		if self.keep_ratio.get_active():
			val = self.corners[self.active_corner]
			self.active_corner = 0
			self.switch.set_index(0)
			if not self.update_flag: self.apply_changes(val)
		self.update_vals()

	def switch_changed(self):
		self.active_corner = self.switch.get_index()
		self.update_vals()

	def slider_changes(self, *args):
		if self.update_flag: return
		self.apply_changes(self.slider.get_value() / 100.0)

	def changes(self, *args):
		if self.update_flag: return
		self.apply_changes(self.num_spin.get_value() / 100.0)

	def apply_changes(self, val):
		if self.insp.is_selection():
			selection = self.app.current_doc.selection
			if self.insp.is_obj_rect(selection.objs[0]):
				if self.keep_ratio.get_active():
					self.corners = [val, val, val, val]
				else:
					self.corners[self.active_corner] = val
				self.app.current_doc.api.set_rect_corners(self.corners)

	def update_vals(self):
		self.update_flag = True
		self.slider.set_value(int(self.corners[self.active_corner] * 100))
		self.num_spin.set_value(self.corners[self.active_corner] * 100.0)
		self.update_flag = False

	def update(self, *args):
		if self.insp.is_selection():
			selection = self.app.current_doc.selection
			if self.insp.is_obj_rect(selection.objs[0]):
				corners = [] + selection.objs[0].corners
				if self.corners == corners:
					self.update_vals()
				else:
					self.corners = corners
					self.update_flag = True
					state = (corners[0] == corners[1] == corners[2] == corners[3])
					self.keep_ratio.set_active(state)
					self.lock_changed()


class RectAngleSwitch(VPanel):

	active = 0
	toggles = []
	onchange = None

	def __init__(self, parent, active=0, onchange=None):
		self.active = active
		self.toggles = [None, None, None, None]
		self.onchange = onchange
		VPanel.__init__(self, parent)
		row1 = wx.BoxSizer(HORIZONTAL)
		self.box.Add(row1)

		icons_dict = {True:[icons.CTX_ROUNDED_RECT2_ON, '', ],
				False:[icons.CTX_ROUNDED_RECT2_OFF, '', ], }
		tgl = BitmapToggle(self, False, icons_dict, self.changed)
		self.toggles[1] = tgl
		row1.Add(tgl)
		icons_dict = {True:[icons.CTX_ROUNDED_RECT3_ON, '', ],
				False:[icons.CTX_ROUNDED_RECT3_OFF, '', ], }
		tgl = BitmapToggle(self, False, icons_dict, self.changed)
		self.toggles[2] = tgl
		row1.Add(tgl)

		row2 = wx.BoxSizer(HORIZONTAL)
		self.box.Add(row2, 0)

		icons_dict = {True:[icons.CTX_ROUNDED_RECT1_ON, '', ],
				False:[icons.CTX_ROUNDED_RECT1_OFF, '', ], }
		tgl = BitmapToggle(self, False, icons_dict, self.changed)
		self.toggles[0] = tgl
		row2.Add(tgl)
		icons_dict = {True:[icons.CTX_ROUNDED_RECT4_ON, '', ],
				False:[icons.CTX_ROUNDED_RECT4_OFF, '', ], }
		tgl = BitmapToggle(self, False, icons_dict, self.changed)
		self.toggles[3] = tgl
		row2.Add(tgl)

		self.toggles[self.active].set_active(True)


	def changed(self, *args):
		old_active = self.active
		self.toggles[self.active].set_active(False)
		for item in self.toggles:
			if item.get_active():self.active = self.toggles.index(item)
		if old_active == self.active:
			self.toggles[self.active].set_active(True)
		else:
			if not self.onchange is None: self.onchange()


	def get_index(self):
		return self.active

	def set_index(self, index):
		self.toggles[self.active].set_active(False)
		self.active = index
		self.toggles[self.active].set_active(True)



