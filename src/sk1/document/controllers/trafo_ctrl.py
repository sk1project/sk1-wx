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

import math

from uc2 import libgeom

from sk1 import modes, config

from generic import AbstractController

class MoveController(AbstractController):

	start = None
	end = None
	trafo = []
	mode = modes.MOVE_MODE
	old_selection = []

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)
		self.move = False
		self.moved = False
		self.copy = False
		self.trafo = []

	def mouse_down(self, event):
		self.snap = self.presenter.snap
		self.start = event.get_point()
		self.move = True
		dpoint = self.canvas.win_to_doc(self.start)
		sel = self.selection.pick_at_point(dpoint)
		if sel and sel[0] not in self.selection.objs:
			self.old_selection = [] + self.selection.objs
			self.selection.clear()
			self.canvas.renderer.paint_selection()
			self.canvas.selection_repaint = False
			self.selection.set(sel)
		self.canvas.selection_repaint = False
		self.canvas.renderer.cdc_paint_doc()
		self.timer.start()

	def repaint(self):
		if self.end:
			self.canvas.renderer.cdc_draw_move_frame(self.trafo)
			self.end = []

	def _calc_trafo(self, point1, point2):
		start_point = self.canvas.win_to_doc(point1)
		end_point = self.canvas.win_to_doc(point2)
		dx = end_point[0] - start_point[0]
		dy = end_point[1] - start_point[1]
		return [1.0, 0.0, 0.0, 1.0, dx, dy]

	def mouse_move(self, event):
		if self.move:
			self.moved = True
			new = event.get_point()
			if event.is_ctrl():
				change = [new[0] - self.start[0], new[1] - self.start[1]]
				if abs(change[0]) > abs(change[1]):
					new[1] = self.start[1]
				else:
					new[0] = self.start[0]
			self.end = new
			self.trafo = self._calc_trafo(self.start, self.end)
			bbox = self.presenter.selection.bbox
			self.trafo = self._snap(bbox, self.trafo)
		else:
			point = event.get_point()
			dpoint = self.canvas.win_to_doc(point)
			if self.selection.is_point_over(dpoint):
				if self.selection.is_point_over_marker(dpoint):
					mark = self.selection.is_point_over_marker(dpoint)[0]
					self.canvas.resize_marker = mark
					self.canvas.restore_mode()
					self.canvas.set_temp_mode(modes.RESIZE_MODE)
			elif not self.selection.pick_at_point(dpoint):
				self.canvas.restore_mode()

	def mouse_up(self, event):
		if self.move:
			self.timer.stop()
			new = event.get_point()
			if event.is_ctrl():
				change = [new[0] - self.start[0], new[1] - self.start[1]]
				if abs(change[0]) > abs(change[1]):
					new[1] = self.start[1]
				else:
					new[0] = self.start[0]
			self.end = new
			self.canvas.selection_repaint = True
			self.move = False
			if self.moved:
				self.trafo = self._calc_trafo(self.start, self.end)
				bbox = self.presenter.selection.bbox
				self.trafo = self._snap(bbox, self.trafo)
				self.api.transform_selected(self.trafo, self.copy)
			elif event.is_shift():
				self.presenter.selection.set(self.old_selection)
				self.canvas.select_at_point(event.get_point(), True)
				if not self.selection.is_point_over(event.get_point()):
					self.canvas.restore_mode()
			else:
				sel = self.presenter.selection.objs
				self.presenter.selection.set(sel)
			if self.copy:
				self.canvas.restore_cursor()
			self.moved = False
			self.copy = False
			self.old_selection = []
			self.start = []
			self.end = []

	def mouse_right_up(self, event):
		if self.moved:
			self.copy = True
			cursor = self.app.cursors[modes.COPY_MODE]
			self.canvas.set_temp_cursor(cursor)
		else:
			AbstractController.mouse_right_up(self, event)

	def _snap(self, bbox, trafo):
		result = [] + trafo
		points = libgeom.bbox_middle_points(bbox)
		tr_points = libgeom.apply_trafo_to_points(points, trafo)
		active_snap = [None, None]

		shift_x = []
		snap_x = []
		for point in [tr_points[0], tr_points[2], tr_points[1]]:
			flag, wp, dp = self.snap.snap_point(point, False, snap_y=False)
			if flag:
				shift_x.append(dp[0] - point[0])
				snap_x.append(dp[0])
		if shift_x:
			if len(shift_x) > 1:
				if abs(shift_x[0]) < abs(shift_x[1]):
					dx = shift_x[0]
					active_snap[0] = snap_x[0]
				else:
					dx = shift_x[1]
					active_snap[0] = snap_x[1]
			else:
				dx = shift_x[0]
				active_snap[0] = snap_x[0]
			result[4] += dx

		shift_y = []
		snap_y = []
		for point in [tr_points[1], tr_points[3], tr_points[2]]:
			flag, wp, dp = self.snap.snap_point(point, False, snap_x=False)
			if flag:
				shift_y.append(dp[1] - point[1])
				snap_y.append(dp[1])
		if shift_y:
			if len(shift_y) > 1:
				if abs(shift_y[0]) < abs(shift_y[1]):
					dy = shift_y[0]
					active_snap[1] = snap_y[0]
				else:
					dy = shift_y[1]
					active_snap[1] = snap_y[1]
			else:
				dy = shift_y[0]
				active_snap[1] = snap_y[0]
			result[5] += dy

		self.snap.active_snap = [] + active_snap
		return result

class TransformController(AbstractController):

	mode = modes.RESIZE_MODE
	painter = None

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)
		self.move = False
		self.moved = False
		self.copy = False
		self.frame = []

	def repaint(self):
		if not self.painter is None: self.painter()

	def mouse_move(self, event):
		if not self.move:
			point = self.canvas.win_to_doc(event.get_point())
			ret = self.selection.is_point_over_marker(point)
			if not ret:
				self.canvas.restore_mode()
			elif not ret[0] == self.canvas.resize_marker:
				self.canvas.resize_marker = ret[0]
				self.set_cursor()

		else:
			self.end = event.get_point()
			self.trafo = self._calc_trafo(event)
			self.moved = True


	def mouse_down(self, event):
		self.snap = self.presenter.snap
		self.start = event.get_point()
		self.move = True
		self.canvas.selection_repaint = False
		if not self.canvas.resize_marker == 9:
			self.painter = self._draw_frame
			self.canvas.renderer.cdc_paint_doc()
		else:
			self.offset_start = [] + self.selection.center_offset
			self.painter = self._draw_center
			self.canvas.selection_repaint = True
		self.timer.start()

	def mouse_up(self, event):
		self.timer.stop()
		self.end = event.get_point()
		self.move = False
		self.canvas.selection_repaint = True
		if not self.canvas.resize_marker == 9:
			self.canvas.renderer.hide_move_frame()
			if self.moved:
				self.trafo = self._calc_trafo(event)
				self.api.transform_selected(self.trafo, self.copy)
			self.moved = False
			self.copy = False
			self.start = []
			self.end = []
			point = self.canvas.win_to_doc(event.get_point())
			if not self.selection.is_point_over_marker(point):
				self.canvas.restore_mode()
		else:
			self._draw_center()
			self.moved = False
			self.copy = False
			self.start = []
			self.end = []

	def mouse_right_up(self, event):
		if self.moved:
			self.copy = True
			self.set_cursor()
		else:
			AbstractController.mouse_right_up(self, event)

	def set_cursor(self):
		mark = self.canvas.resize_marker
		mode = self.mode
		if mark == 0 or mark == 8:
			if self.copy: mode = modes.RESIZE_MODE1_COPY
			else: mode = modes.RESIZE_MODE1
		if mark == 1 or mark == 7:
			if self.copy: mode = modes.RESIZE_MODE2_COPY
			else: mode = modes.RESIZE_MODE2
		if mark == 2 or mark == 6:
			if self.copy: mode = modes.RESIZE_MODE3_COPY
			else: mode = modes.RESIZE_MODE3
		if mark == 3 or mark == 5:
			if self.copy: mode = modes.RESIZE_MODE4_COPY
			else: mode = modes.RESIZE_MODE4
		if mark == 9:
			mode = modes.RESIZE_MODE
		if mark in [10, 12, 15, 17]:
			if self.copy: mode = modes.RESIZE_MODE10_COPY
			else: mode = modes.RESIZE_MODE10
		if mark in [11, 16]:
			if self.copy: mode = modes.RESIZE_MODE11_COPY
			else: mode = modes.RESIZE_MODE11
		if mark in [13, 14]:
			if self.copy: mode = modes.RESIZE_MODE13_COPY
			else: mode = modes.RESIZE_MODE13
		self.mode = mode
		self.canvas.set_canvas_cursor(mode)

	def _calc_trafo(self, event):
		control = event.is_ctrl()
		shift = event.is_shift()
		mark = self.canvas.resize_marker
		start_point = self.canvas.win_to_doc(self.start)
		end_point = self.canvas.win_to_doc(self.end)
		bbox = self.presenter.selection.bbox
		middle_points = libgeom.bbox_middle_points(bbox)
		w = bbox[2] - bbox[0]
		h = bbox[3] - bbox[1]
		m11 = m22 = 1.0
		m12 = m21 = 0.0
		dx = dy = 0.0
		snap = [None, None]
		if mark == 0:
			dx = start_point[0] - end_point[0]
			dy = end_point[1] - start_point[1]
			if shift:
				if control:
					m11 = (w + 2.0 * dx) / w
					m22 = (h + 2.0 * dy) / h
					dx = -(bbox[2] * m11 - bbox[2]) + w * (m11 - 1.0) / 2.0
					dy = -(bbox[1] * m22 - bbox[1]) - h * (m22 - 1.0) / 2.0
					#---- snapping
					point = middle_points[0]
					trafo = [m11, m21, m12, m22, dx, dy]
					p = libgeom.apply_trafo_to_point(point, trafo)
					f, p, p_doc = self.snap.snap_point(p, False, snap_y=False)
					if f:
						dx = point[0] - p_doc[0]
						m11 = (w + 2.0 * dx) / w
						dx = -(bbox[2] * m11 - bbox[2]) + w * (m11 - 1.0) / 2.0
						snap[0] = self.snap.active_snap[0]
					point = middle_points[1]
					trafo = [m11, m21, m12, m22, dx, dy]
					p = libgeom.apply_trafo_to_point(point, trafo)
					f, p, p_doc = self.snap.snap_point(p, False, snap_x=False)
					if f:
						dy = p_doc[1] - point[1]
						m22 = (h + 2.0 * dy) / h
						dy = -(bbox[1] * m22 - bbox[1]) - h * (m22 - 1.0) / 2.0
						snap[1] = self.snap.active_snap[1]
					self.snap.active_snap = snap
					#---- snapping
				else:
					if abs(dx) < abs(dy):
						m11 = m22 = (w + 2.0 * dx) / w
					else:
						m11 = m22 = (h + 2.0 * dy) / h
					dx = -(bbox[2] * m11 - bbox[2]) + w * (m11 - 1.0) / 2.0
					dy = -(bbox[1] * m22 - bbox[1]) - h * (m22 - 1.0) / 2.0
					#---- snapping
					point = middle_points[0]
					trafo = [m11, m21, m12, m22, dx, dy]
					p = libgeom.apply_trafo_to_point(point, trafo)
					f, p, p_doc = self.snap.snap_point(p, False, snap_y=False)
					if f:
						dx = point[0] - p_doc[0]
						m11 = m22 = (w + 2.0 * dx) / w
						dx = -(bbox[2] * m11 - bbox[2]) + w * (m11 - 1.0) / 2.0
						dy = -(bbox[1] * m22 - bbox[1]) - h * (m22 - 1.0) / 2.0
						snap[0] = self.snap.active_snap[0]
					else:
						point = middle_points[1]
						trafo = [m11, m21, m12, m22, dx, dy]
						p = libgeom.apply_trafo_to_point(point, trafo)
						f, p, p_doc = self.snap.snap_point(p, False, snap_x=False)
						if f:
							dy = p_doc[1] - point[1]
							m11 = m22 = (h + 2.0 * dy) / h
							dx = -(bbox[2] * m11 - bbox[2]) + w * (m11 - 1.0) / 2.0
							dy = -(bbox[1] * m22 - bbox[1]) - h * (m22 - 1.0) / 2.0
							snap[1] = self.snap.active_snap[1]
					self.snap.active_snap = snap
					#---- snapping
			else:
				if control:
					m11 = (w + dx) / w
					m22 = (h + dy) / h
					dx = -(bbox[2] * m11 - bbox[2])
					dy = -(bbox[1] * m22 - bbox[1])
					#---- snapping
					point = middle_points[0]
					trafo = [m11, m21, m12, m22, dx, dy]
					p = libgeom.apply_trafo_to_point(point, trafo)
					f, p, p_doc = self.snap.snap_point(p, False, snap_y=False)
					if f:
						dx = point[0] - p_doc[0]
						m11 = (w + dx) / w
						dx = -(bbox[2] * m11 - bbox[2])
						snap[0] = self.snap.active_snap[0]
					point = middle_points[1]
					trafo = [m11, m21, m12, m22, dx, dy]
					p = libgeom.apply_trafo_to_point(point, trafo)
					f, p, p_doc = self.snap.snap_point(p, False, snap_x=False)
					if f:
						dy = p_doc[1] - point[1]
						m22 = (h + dy) / h
						dy = -(bbox[1] * m22 - bbox[1])
						snap[1] = self.snap.active_snap[1]
					self.snap.active_snap = snap
					#---- snapping
				else:
					if abs(dx) < abs(dy):
						m11 = m22 = (w + dx) / w
					else:
						m11 = m22 = (h + dy) / h
					dx = -(bbox[2] * m11 - bbox[2])
					dy = -(bbox[1] * m22 - bbox[1])
					#---- snapping
					point = middle_points[0]
					trafo = [m11, m21, m12, m22, dx, dy]
					p = libgeom.apply_trafo_to_point(point, trafo)
					f, p, p_doc = self.snap.snap_point(p, False, snap_y=False)
					if f:
						dx = point[0] - p_doc[0]
						m11 = m22 = (w + dx) / w
						dx = -(bbox[2] * m11 - bbox[2])
						dy = -(bbox[1] * m22 - bbox[1])
						snap[0] = self.snap.active_snap[0]
					else:
						point = middle_points[1]
						trafo = [m11, m21, m12, m22, dx, dy]
						p = libgeom.apply_trafo_to_point(point, trafo)
						f, p, p_doc = self.snap.snap_point(p, False, snap_x=False)
						if f:
							dy = p_doc[1] - point[1]
							m11 = m22 = (h + dy) / h
							dx = -(bbox[2] * m11 - bbox[2])
							dy = -(bbox[1] * m22 - bbox[1])
							snap[1] = self.snap.active_snap[1]
					self.snap.active_snap = snap
					#---- snapping
		if mark == 1:
			dy = end_point[1] - start_point[1]
			if shift:
				m22 = (h + 2.0 * dy) / h
				dy = -(bbox[1] * m22 - bbox[1]) - h * (m22 - 1.0) / 2.0
				#---- snapping
				point = middle_points[1]
				trafo = [m11, m21, m12, m22, dx, dy]
				p = libgeom.apply_trafo_to_point(point, trafo)
				f, p, p_doc = self.snap.snap_point(p, False)
				dy = p_doc[1] - point[1]
				m22 = (h + 2.0 * dy) / h
				dy = -(bbox[1] * m22 - bbox[1]) - h * (m22 - 1.0) / 2.0
				#---- snapping
			else:
				m22 = (h + dy) / h
				dy = -(bbox[1] * m22 - bbox[1])
				#---- snapping
				point = middle_points[1]
				trafo = [m11, m21, m12, m22, dx, dy]
				p = libgeom.apply_trafo_to_point(point, trafo)
				f, p, p_doc = self.snap.snap_point(p, False)
				dy = p_doc[1] - point[1]
				m22 = (h + dy) / h
				dy = -(bbox[1] * m22 - bbox[1])
				#---- snapping
		if mark == 2:
			dx = end_point[0] - start_point[0]
			dy = end_point[1] - start_point[1]
			if shift:
				if control:
					m11 = (w + 2.0 * dx) / w
					m22 = (h + 2.0 * dy) / h
					dx = -(bbox[0] * m11 - bbox[0]) - w * (m11 - 1.0) / 2.0
					dy = -(bbox[1] * m22 - bbox[1]) - h * (m22 - 1.0) / 2.0
					#---- snapping
					point = middle_points[2]
					trafo = [m11, m21, m12, m22, dx, dy]
					p = libgeom.apply_trafo_to_point(point, trafo)
					f, p, p_doc = self.snap.snap_point(p, False, snap_y=False)
					if f:
						dx = p_doc[0] - point[0]
						m11 = (w + 2.0 * dx) / w
						dx = -(bbox[0] * m11 - bbox[0]) - w * (m11 - 1.0) / 2.0
						snap[0] = self.snap.active_snap[0]
					point = middle_points[1]
					trafo = [m11, m21, m12, m22, dx, dy]
					p = libgeom.apply_trafo_to_point(point, trafo)
					f, p, p_doc = self.snap.snap_point(p, False, snap_x=False)
					if f:
						dy = p_doc[1] - point[1]
						m22 = (h + 2.0 * dy) / h
						dy = -(bbox[1] * m22 - bbox[1]) - h * (m22 - 1.0) / 2.0
						snap[1] = self.snap.active_snap[1]
					self.snap.active_snap = snap
					#---- snapping
				else:
					if abs(dx) < abs(dy):
						m11 = m22 = (w + 2.0 * dx) / w
					else:
						m11 = m22 = (h + 2.0 * dy) / h
					dx = -(bbox[0] * m11 - bbox[0]) - w * (m11 - 1.0) / 2.0
					dy = -(bbox[1] * m22 - bbox[1]) - h * (m22 - 1.0) / 2.0
					#---- snapping
					point = middle_points[2]
					trafo = [m11, m21, m12, m22, dx, dy]
					p = libgeom.apply_trafo_to_point(point, trafo)
					f, p, p_doc = self.snap.snap_point(p, False, snap_y=False)
					if f:
						dx = p_doc[0] - point[0]
						m11 = m22 = (w + 2.0 * dx) / w
						dx = -(bbox[0] * m11 - bbox[0]) - w * (m11 - 1.0) / 2.0
						dy = -(bbox[1] * m22 - bbox[1]) - h * (m22 - 1.0) / 2.0
						snap[0] = self.snap.active_snap[0]
					else:
						point = middle_points[1]
						trafo = [m11, m21, m12, m22, dx, dy]
						p = libgeom.apply_trafo_to_point(point, trafo)
						f, p, p_doc = self.snap.snap_point(p, False, snap_x=False)
						if f:
							dy = p_doc[1] - point[1]
							m11 = m22 = (h + 2.0 * dy) / h
							dx = -(bbox[0] * m11 - bbox[0]) - w * (m11 - 1.0) / 2.0
							dy = -(bbox[1] * m22 - bbox[1]) - h * (m22 - 1.0) / 2.0
							snap[1] = self.snap.active_snap[1]
					self.snap.active_snap = snap
					#---- snapping
			else:
				if control:
					m11 = (w + dx) / w
					m22 = (h + dy) / h
					dx = -(bbox[0] * m11 - bbox[0])
					dy = -(bbox[1] * m22 - bbox[1])
					#---- snapping
					point = middle_points[2]
					trafo = [m11, m21, m12, m22, dx, dy]
					p = libgeom.apply_trafo_to_point(point, trafo)
					f, p, p_doc = self.snap.snap_point(p, False, snap_y=False)
					if f:
						dx = p_doc[0] - point[0]
						m11 = (w + dx) / w
						dx = -(bbox[0] * m11 - bbox[0])
						snap[0] = self.snap.active_snap[0]
					point = middle_points[1]
					trafo = [m11, m21, m12, m22, dx, dy]
					p = libgeom.apply_trafo_to_point(point, trafo)
					f, p, p_doc = self.snap.snap_point(p, False, snap_x=False)
					if f:
						dy = p_doc[1] - point[1]
						m22 = (h + dy) / h
						dy = -(bbox[1] * m22 - bbox[1])
						snap[1] = self.snap.active_snap[1]
					self.snap.active_snap = snap
					#---- snapping
				else:
					if abs(dx) < abs(dy):
						m11 = m22 = (w + dx) / w
					else:
						m11 = m22 = (h + dy) / h
					dx = -(bbox[0] * m11 - bbox[0])
					dy = -(bbox[1] * m22 - bbox[1])
					#---- snapping
					point = middle_points[2]
					trafo = [m11, m21, m12, m22, dx, dy]
					p = libgeom.apply_trafo_to_point(point, trafo)
					f, p, p_doc = self.snap.snap_point(p, False, snap_y=False)
					if f:
						dx = p_doc[0] - point[0]
						m11 = m22 = (w + dx) / w
						dx = -(bbox[0] * m11 - bbox[0])
						dy = -(bbox[1] * m22 - bbox[1])
						snap[0] = self.snap.active_snap[0]
					else:
						point = middle_points[1]
						trafo = [m11, m21, m12, m22, dx, dy]
						p = libgeom.apply_trafo_to_point(point, trafo)
						f, p, p_doc = self.snap.snap_point(p, False, snap_x=False)
						if f:
							dy = p_doc[1] - point[1]
							m11 = m22 = (h + dy) / h
							dx = -(bbox[0] * m11 - bbox[0])
							dy = -(bbox[1] * m22 - bbox[1])
							snap[1] = self.snap.active_snap[1]
					self.snap.active_snap = snap
					#---- snapping
		if mark == 3:
			dx = start_point[0] - end_point[0]
			if shift:
				m11 = (w + 2.0 * dx) / w
				dx = -(bbox[2] * m11 - bbox[2]) + w * (m11 - 1.0) / 2.0
				#---- snapping
				point = middle_points[0]
				trafo = [m11, m21, m12, m22, dx, dy]
				p = libgeom.apply_trafo_to_point(point, trafo)
				f, p, p_doc = self.snap.snap_point(p, False)
				dx = point[0] - p_doc[0]
				m11 = (w + 2.0 * dx) / w
				dx = -(bbox[2] * m11 - bbox[2]) + w * (m11 - 1.0) / 2.0
				#---- snapping
			else:
				m11 = (w + dx) / w
				dx = -(bbox[2] * m11 - bbox[2])
				#---- snapping
				point = middle_points[0]
				trafo = [m11, m21, m12, m22, dx, dy]
				p = libgeom.apply_trafo_to_point(point, trafo)
				f, p, p_doc = self.snap.snap_point(p, False)
				dx = point[0] - p_doc[0]
				m11 = (w + dx) / w
				dx = -(bbox[2] * m11 - bbox[2])
				#---- snapping
		if mark == 5:
			dx = end_point[0] - start_point[0]
			if shift:
				m11 = (w + 2.0 * dx) / w
				dx = -(bbox[0] * m11 - bbox[0]) - w * (m11 - 1.0) / 2.0
				#---- snapping
				point = middle_points[2]
				trafo = [m11, m21, m12, m22, dx, dy]
				p = libgeom.apply_trafo_to_point(point, trafo)
				f, p, p_doc = self.snap.snap_point(p, False)
				dx = p_doc[0] - point[0]
				m11 = (w + 2.0 * dx) / w
				dx = -(bbox[0] * m11 - bbox[0]) - w * (m11 - 1.0) / 2.0
				#---- snapping
			else:
				m11 = (w + dx) / w
				dx = -(bbox[0] * m11 - bbox[0])
				#---- snapping
				point = middle_points[2]
				trafo = [m11, m21, m12, m22, dx, dy]
				p = libgeom.apply_trafo_to_point(point, trafo)
				f, p, p_doc = self.snap.snap_point(p, False)
				dx = p_doc[0] - point[0]
				m11 = (w + dx) / w
				dx = -(bbox[0] * m11 - bbox[0])
				#---- snapping
		if mark == 6:
			dx = start_point[0] - end_point[0]
			dy = start_point[1] - end_point[1]
			if shift:
				if control:
					m11 = (w + 2.0 * dx) / w
					m22 = (h + 2.0 * dy) / h
					dx = -(bbox[2] * m11 - bbox[2]) + w * (m11 - 1.0) / 2.0
					dy = -(bbox[3] * m22 - bbox[3]) + h * (m22 - 1.0) / 2.0
					#---- snapping
					point = middle_points[0]
					trafo = [m11, m21, m12, m22, dx, dy]
					p = libgeom.apply_trafo_to_point(point, trafo)
					f, p, p_doc = self.snap.snap_point(p, False, snap_y=False)
					if f:
						dx = point[0] - p_doc[0]
						m11 = (w + 2.0 * dx) / w
						dx = -(bbox[2] * m11 - bbox[2]) + w * (m11 - 1.0) / 2.0
						snap[0] = self.snap.active_snap[0]
					point = middle_points[3]
					trafo = [m11, m21, m12, m22, dx, dy]
					p = libgeom.apply_trafo_to_point(point, trafo)
					f, p, p_doc = self.snap.snap_point(p, False, snap_x=False)
					if f:
						dy = point[1] - p_doc[1]
						m22 = (h + 2.0 * dy) / h
						dy = -(bbox[3] * m22 - bbox[3]) + h * (m22 - 1.0) / 2.0
						snap[1] = self.snap.active_snap[1]
					self.snap.active_snap = snap
					#---- snapping
				else:
					if abs(dx) < abs(dy):
						m11 = m22 = (w + 2.0 * dx) / w
					else:
						m11 = m22 = (h + 2.0 * dy) / h
					dx = -(bbox[2] * m11 - bbox[2]) + w * (m11 - 1.0) / 2.0
					dy = -(bbox[3] * m22 - bbox[3]) + h * (m22 - 1.0) / 2.0
					#---- snapping
					point = middle_points[0]
					trafo = [m11, m21, m12, m22, dx, dy]
					p = libgeom.apply_trafo_to_point(point, trafo)
					f, p, p_doc = self.snap.snap_point(p, False, snap_y=False)
					if f:
						dx = point[0] - p_doc[0]
						m11 = m22 = (w + 2.0 * dx) / w
						dx = -(bbox[2] * m11 - bbox[2]) + w * (m11 - 1.0) / 2.0
						dy = -(bbox[3] * m22 - bbox[3]) + h * (m22 - 1.0) / 2.0
						snap[0] = self.snap.active_snap[0]
					else:
						point = middle_points[3]
						trafo = [m11, m21, m12, m22, dx, dy]
						p = libgeom.apply_trafo_to_point(point, trafo)
						f, p, p_doc = self.snap.snap_point(p, False, snap_x=False)
						if f:
							dy = point[1] - p_doc[1]
							m11 = m22 = (h + 2.0 * dy) / h
							dx = -(bbox[2] * m11 - bbox[2]) + w * (m11 - 1.0) / 2.0
							dy = -(bbox[3] * m22 - bbox[3]) + h * (m22 - 1.0) / 2.0
							snap[1] = self.snap.active_snap[1]
					self.snap.active_snap = snap
					#---- snapping
			else:
				if control:
					m11 = (w + dx) / w
					m22 = (h + dy) / h
					dx = -(bbox[2] * m11 - bbox[2])
					dy = -(bbox[3] * m22 - bbox[3])
					#---- snapping
					point = middle_points[0]
					trafo = [m11, m21, m12, m22, dx, dy]
					p = libgeom.apply_trafo_to_point(point, trafo)
					f, p, p_doc = self.snap.snap_point(p, False, snap_y=False)
					if f:
						dx = point[0] - p_doc[0]
						m11 = (w + dx) / w
						dx = -(bbox[2] * m11 - bbox[2])
						snap[0] = self.snap.active_snap[0]
					point = middle_points[3]
					trafo = [m11, m21, m12, m22, dx, dy]
					p = libgeom.apply_trafo_to_point(point, trafo)
					f, p, p_doc = self.snap.snap_point(p, False, snap_x=False)
					if f:
						dy = point[1] - p_doc[1]
						m22 = (h + dy) / h
						dy = -(bbox[3] * m22 - bbox[3])
						snap[1] = self.snap.active_snap[1]
					self.snap.active_snap = snap
					#---- snapping
				else:
					if abs(dx) < abs(dy):
						m11 = m22 = (w + dx) / w
					else:
						m11 = m22 = (h + dy) / h
					dx = -(bbox[2] * m11 - bbox[2])
					dy = -(bbox[3] * m22 - bbox[3])
					#---- snapping
					point = middle_points[0]
					trafo = [m11, m21, m12, m22, dx, dy]
					p = libgeom.apply_trafo_to_point(point, trafo)
					f, p, p_doc = self.snap.snap_point(p, False, snap_y=False)
					if f:
						dx = point[0] - p_doc[0]
						m11 = m22 = (w + dx) / w
						dx = -(bbox[2] * m11 - bbox[2])
						dy = -(bbox[3] * m22 - bbox[3])
						snap[0] = self.snap.active_snap[0]
					else:
						point = middle_points[3]
						trafo = [m11, m21, m12, m22, dx, dy]
						p = libgeom.apply_trafo_to_point(point, trafo)
						f, p, p_doc = self.snap.snap_point(p, False, snap_x=False)
						if f:
							dy = point[1] - p_doc[1]
							m11 = m22 = (h + dy) / h
							dx = -(bbox[2] * m11 - bbox[2])
							dy = -(bbox[3] * m22 - bbox[3])
							snap[1] = self.snap.active_snap[1]
					self.snap.active_snap = snap
					#---- snapping
		if mark == 7:
			dy = start_point[1] - end_point[1]
			if shift:
				m22 = (h + 2.0 * dy) / h
				dy = -(bbox[3] * m22 - bbox[3]) + h * (m22 - 1.0) / 2.0
				#---- snapping
				point = middle_points[3]
				trafo = [m11, m21, m12, m22, dx, dy]
				p = libgeom.apply_trafo_to_point(point, trafo)
				f, p, p_doc = self.snap.snap_point(p, False)
				dy = point[1] - p_doc[1]
				m22 = (h + 2.0 * dy) / h
				dy = -(bbox[3] * m22 - bbox[3]) + h * (m22 - 1.0) / 2.0
				#---- snapping
			else:
				m22 = (h + dy) / h
				dy = -(bbox[3] * m22 - bbox[3])
				#---- snapping
				point = middle_points[3]
				trafo = [m11, m21, m12, m22, dx, dy]
				p = libgeom.apply_trafo_to_point(point, trafo)
				f, p, p_doc = self.snap.snap_point(p, False)
				dy = point[1] - p_doc[1]
				m22 = (h + dy) / h
				dy = -(bbox[3] * m22 - bbox[3])
				#---- snapping
		if mark == 8:
			dx = end_point[0] - start_point[0]
			dy = start_point[1] - end_point[1]
			if shift:
				if control:
					m11 = (w + 2.0 * dx) / w
					m22 = (h + 2.0 * dy) / h
					dx = -(bbox[0] * m11 - bbox[0]) - w * (m11 - 1.0) / 2.0
					dy = -(bbox[3] * m22 - bbox[3]) + h * (m22 - 1.0) / 2.0
					#---- snapping
					point = middle_points[2]
					trafo = [m11, m21, m12, m22, dx, dy]
					p = libgeom.apply_trafo_to_point(point, trafo)
					f, p, p_doc = self.snap.snap_point(p, False, snap_y=False)
					if f:
						dx = p_doc[0] - point[0]
						m11 = (w + 2.0 * dx) / w
						dx = -(bbox[0] * m11 - bbox[0]) - w * (m11 - 1.0) / 2.0
						snap[0] = self.snap.active_snap[0]
					point = middle_points[3]
					trafo = [m11, m21, m12, m22, dx, dy]
					p = libgeom.apply_trafo_to_point(point, trafo)
					f, p, p_doc = self.snap.snap_point(p, False, snap_x=False)
					if f:
						dy = point[1] - p_doc[1]
						m22 = (h + 2.0 * dy) / h
						dy = -(bbox[3] * m22 - bbox[3]) + h * (m22 - 1.0) / 2.0
						snap[1] = self.snap.active_snap[1]
					self.snap.active_snap = snap
					#---- snapping
				else:
					if abs(dx) < abs(dy):
						m11 = m22 = (w + 2.0 * dx) / w
					else:
						m11 = m22 = (h + 2.0 * dy) / h
					dx = -(bbox[0] * m11 - bbox[0]) - w * (m11 - 1.0) / 2.0
					dy = -(bbox[3] * m22 - bbox[3]) + h * (m22 - 1.0) / 2.0
					#---- snapping
					point = middle_points[2]
					trafo = [m11, m21, m12, m22, dx, dy]
					p = libgeom.apply_trafo_to_point(point, trafo)
					f, p, p_doc = self.snap.snap_point(p, False, snap_y=False)
					if f:
						dx = p_doc[0] - point[0]
						m11 = m22 = (w + 2.0 * dx) / w
						dx = -(bbox[0] * m11 - bbox[0]) - w * (m11 - 1.0) / 2.0
						dy = -(bbox[3] * m22 - bbox[3]) + h * (m22 - 1.0) / 2.0
						snap[0] = self.snap.active_snap[0]
					else:
						point = middle_points[3]
						trafo = [m11, m21, m12, m22, dx, dy]
						p = libgeom.apply_trafo_to_point(point, trafo)
						f, p, p_doc = self.snap.snap_point(p, False, snap_x=False)
						if f:
							dy = point[1] - p_doc[1]
							m11 = m22 = (h + 2.0 * dy) / h
							dx = -(bbox[0] * m11 - bbox[0]) - w * (m11 - 1.0) / 2.0
							dy = -(bbox[3] * m22 - bbox[3]) + h * (m22 - 1.0) / 2.0
							snap[1] = self.snap.active_snap[1]
					self.snap.active_snap = snap
					#---- snapping
			else:
				if control:
					m11 = (w + dx) / w
					m22 = (h + dy) / h
					dx = -(bbox[0] * m11 - bbox[0])
					dy = -(bbox[3] * m22 - bbox[3])
					#---- snapping
					point = middle_points[2]
					trafo = [m11, m21, m12, m22, dx, dy]
					p = libgeom.apply_trafo_to_point(point, trafo)
					f, p, p_doc = self.snap.snap_point(p, False, snap_y=False)
					if f:
						dx = p_doc[0] - point[0]
						m11 = (w + dx) / w
						dx = -(bbox[0] * m11 - bbox[0])
						snap[0] = self.snap.active_snap[0]
					point = middle_points[3]
					trafo = [m11, m21, m12, m22, dx, dy]
					p = libgeom.apply_trafo_to_point(point, trafo)
					f, p, p_doc = self.snap.snap_point(p, False, snap_x=False)
					if f:
						dy = point[1] - p_doc[1]
						m22 = (h + dy) / h
						dy = -(bbox[3] * m22 - bbox[3])
						snap[1] = self.snap.active_snap[1]
					self.snap.active_snap = snap
					#---- snapping
				else:
					if abs(dx) < abs(dy):
						m11 = m22 = (w + dx) / w
					else:
						m11 = m22 = (h + dy) / h
					dx = -(bbox[0] * m11 - bbox[0])
					dy = -(bbox[3] * m22 - bbox[3])
					#---- snapping
					point = middle_points[2]
					trafo = [m11, m21, m12, m22, dx, dy]
					p = libgeom.apply_trafo_to_point(point, trafo)
					f, p, p_doc = self.snap.snap_point(p, False, snap_y=False)
					if f:
						dx = p_doc[0] - point[0]
						m11 = m22 = (w + dx) / w
						dx = -(bbox[0] * m11 - bbox[0])
						dy = -(bbox[3] * m22 - bbox[3])
						snap[0] = self.snap.active_snap[0]
					else:
						point = middle_points[3]
						trafo = [m11, m21, m12, m22, dx, dy]
						p = libgeom.apply_trafo_to_point(point, trafo)
						f, p, p_doc = self.snap.snap_point(p, False, snap_x=False)
						if f:
							dy = point[1] - p_doc[1]
							m11 = m22 = (h + dy) / h
							dx = -(bbox[0] * m11 - bbox[0])
							dy = -(bbox[3] * m22 - bbox[3])
							snap[1] = self.snap.active_snap[1]
					self.snap.active_snap = snap
					#---- snapping

		if mark == 11:
			change_x = end_point[0] - start_point[0]
			m12 = change_x / h
			dx = -bbox[1] * m12
		if mark == 16:
			change_x = start_point[0] - end_point[0]
			m12 = change_x / h
			dx = -bbox[3] * m12
		if mark == 13:
			change_y = start_point[1] - end_point[1]
			m21 = change_y / w
			dy = -bbox[2] * m21
		if mark == 14:
			change_y = end_point[1] - start_point[1]
			m21 = change_y / w
			dy = -bbox[0] * m21

		if mark in (10, 12, 15, 17):
			x0, y0 = bbox[:2]
			shift_x, shift_y = self.selection.center_offset
			center_x = x0 + w / 2.0 + shift_x
			center_y = y0 + h / 2.0 + shift_y
			a1 = math.atan2(start_point[1] - center_y, start_point[0] - center_x)
			a2 = math.atan2(end_point[1] - center_y, end_point[0] - center_x)
			angle = a2 - a1
			if control:
				step = config.rotation_step * math.pi / 180.0
				angle = round(angle / step) * step
			m21 = math.sin(angle)
			m11 = m22 = math.cos(angle)
			m12 = -m21
			dx = center_x - m11 * center_x + m21 * center_y;
			dy = center_y - m21 * center_x - m11 * center_y;

		if not m11: m11 = .0000000001
		if not m22: m22 = .0000000001
		return [m11, m21, m12, m22, dx, dy]

	def _draw_frame(self, *args):
		if self.end:
			self.canvas.renderer.cdc_draw_move_frame(self.trafo)
			self.end = []
		return True

	def _draw_center(self, *args):
		if self.end:
			start = self.canvas.win_to_doc(self.start)
			end = self.canvas.win_to_doc(self.end)
			dx = end[0] - start[0]
			dy = end[1] - start[1]
			x, y = self.offset_start
			cp = libgeom.bbox_center(self.selection.bbox)
			doc_p = self.snap.snap_point([cp[0] + x + dx, cp[1] + y + dy], False)[2]
			self.selection.center_offset = [doc_p[0] - cp[0], doc_p[1] - cp[1]]
			self.canvas.selection_redraw()
			#self.canvas.renderer.paint_selection()
		return True
