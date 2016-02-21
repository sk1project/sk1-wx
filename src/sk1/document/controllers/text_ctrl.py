# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2017 by Igor E. Novikov
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

from uc2 import libgeom

from sk1 import _, modes, events

from generic import AbstractController

class TextEditController(AbstractController):

	mode = modes.TEXT_EDIT_MODE
	target = None
	cursor = 0

	def start_(self):
		self.snap = self.presenter.snap
		self.target = self.selection.objs[0]
		self.selection.clear()
		self.cursor = 0
		msg = _('Text in editing')
		events.emit(events.APP_STATUS, msg)

	def stop_(self):
		self.selection.set([self.target, ])
		self.target = None

	def escape_pressed(self):
		self.canvas.set_mode()

	#----- REPAINT self.canvas.selection_redraw()

	def repaint(self):
		x0, y0, x1, y1 = self.target.cache_bbox
		p0 = self.canvas.point_doc_to_win([x0, y0])
		p1 = self.canvas.point_doc_to_win([x1, y1])
		bbox = libgeom.normalize_bbox(p0 + p1)
		bbox = libgeom.enlarge_bbox(bbox, 10, 10)
		self.canvas.renderer.draw_frame(bbox[:2], bbox[2:])
		self.paint_cursor()

	def paint_cursor(self):
		if self.cursor < len(self.target.cache_layout_data):
			data = self.target.cache_layout_data[self.cursor]
			p0 = [data[0], data[1]]
			p1 = [data[0], data[1] - data[3]]
		else:
			data = self.target.cache_layout_data[-1]
			p0 = [data[0] + data[2], data[1]]
			p1 = [data[0] + data[2], data[1] - data[3]]
		trafo = self.target.trafo
		if self.cursor in self.target.trafos:
			trafo = self.target.trafos[self.cursor]
		p0, p1 = libgeom.apply_trafo_to_points([p0, p1], trafo)
		p0 = self.canvas.point_doc_to_win(p0)
		p1 = self.canvas.point_doc_to_win(p1)
		self.canvas.renderer.draw_text_cursor(p0, p1)
