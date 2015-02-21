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

from sk1 import _, events
from sk1.resources import icons, get_bmp
from sk1.widgets import LEFT, CENTER
from sk1.pwidgets import UnitSpin, RatioToggle
from generic import CtxPlugin

class ResizePlugin(CtxPlugin):

	name = 'ResizePlugin'
	update_flag = False

	def __init__(self, app, parent):
		CtxPlugin.__init__(self, app, parent)
		events.connect(events.DOC_CHANGED, self.update)
		events.connect(events.SELECTION_CHANGED, self.update)

	def build(self):
		bmp = get_bmp(self, icons.CTX_OBJECT_RESIZE, _('Selection size'))
		self.add(bmp, 0, LEFT | CENTER, 2)

		self.add((2, 2))

		self.width_spin = UnitSpin(self.app, self,
							onchange=self.w_changes)
		self.add(self.width_spin, 0, LEFT | CENTER, 2)

		self.add(get_bmp(self, icons.CTX_W_ON_H), 0, LEFT | CENTER, 1)

		self.height_spin = UnitSpin(self.app, self,
							onchange=self.h_changes)
		self.add(self.height_spin, 0, LEFT | CENTER, 2)

		self.add((2, 2))

		self.keep_ratio = RatioToggle(self)
		self.add(self.keep_ratio, 0, LEFT | CENTER, 2)

	def update(self, *args):
		if self.insp.is_selection():
			bbox = self.app.current_doc.selection.bbox
			w = bbox[2] - bbox[0]
			h = bbox[3] - bbox[1]
			self.update_flag = True
			self.width_spin.set_point_value(w)
			self.height_spin.set_point_value(h)
			self.update_flag = False

	def w_changes(self, *args):
		if self.update_flag: return
		self.user_changes(True)

	def h_changes(self, *args):
		if self.update_flag: return
		self.user_changes(False)

	def user_changes(self, hr=True):
		if self.update_flag: return
		if self.insp.is_selection():
			doc = self.app.current_doc
			bbox = doc.selection.bbox
			w = bbox[2] - bbox[0]
			h = bbox[3] - bbox[1]
			center_x = bbox[0] + w / 2.0
			center_y = bbox[1] + h / 2.0

			new_w = self.width_spin.get_point_value()
			new_h = self.height_spin.get_point_value()

			if not w == new_w or not h == new_h:
				if not new_w: self.width_spin.set_point_value(w);return
				if not new_h: self.height_spin.set_point_value(h);return

				m11 = new_w / w
				m22 = new_h / h

				if m11 == m22 == 1.0:return

				trafo = []

				if self.keep_ratio.get_active():
					if hr:
						dx = center_x * (1 - m11)
						dy = center_y * (1 - m11)
						trafo = [m11, 0.0, 0.0, m11, dx, dy]
					else:
						dx = center_x * (1 - m22)
						dy = center_y * (1 - m22)
						trafo = [m22, 0.0, 0.0, m22, dx, dy]
				else:
					dx = center_x * (1 - m11)
					dy = center_y * (1 - m22)
					trafo = [m11, 0.0, 0.0, m22, dx, dy]

				if trafo: doc.api.transform_selected(trafo)
