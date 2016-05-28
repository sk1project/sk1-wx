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

from copy import deepcopy

from uc2 import uc2const, libgeom
from uc2.formats.sk2 import sk2_const

from sk1 import _, modes, config, events
from generic import AbstractController

GRADIENT_CLR_MODES = [uc2const.COLOR_CMYK, uc2const.COLOR_RGB, uc2const.COLOR_GRAY]

DEFAULT_STOPS = [
[0.0, [uc2const.COLOR_CMYK, [0.0, 0.0, 0.0, 1.0], 1.0, 'Black']],
[1.0, [uc2const.COLOR_CMYK, [0.0, 0.0, 0.0, 0.0], 1.0, 'White']]
]

class GradientChooser(AbstractController):

	mode = modes.GR_SELECT_MODE

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def start_(self):
		sel_objs = self.selection.objs
		if len(sel_objs) == 1 and sel_objs[0].is_primitive() \
			and not sel_objs[0].is_pixmap():
			if sel_objs[0].style[0] \
			and sel_objs[0].style[0][1] == sk2_const.FILL_GRADIENT:
				self.canvas.set_temp_mode(modes.GR_EDIT_MODE)
			else:
				self.canvas.set_temp_mode(modes.GR_CREATE_MODE)
		else:
			self.selection.clear()

	def restore(self):
		self.timer.start()

	def stop_(self):pass

	def on_timer(self):
		self.timer.stop()
		self.start_()

	def mouse_down(self, event):pass

	def mouse_up(self, event):
		self.end = event.get_point()
		self.do_action()

	def mouse_move(self, event):pass

	def do_action(self):
		objs = self.canvas.pick_at_point(self.end)
		if objs and objs[0].is_primitive() and not objs[0].is_pixmap():
			self.selection.set([objs[0], ])
			self.start_()


class GradientCreator(AbstractController):

	mode = modes.GR_CREATE_MODE
	snap = None
	target = None
	is_frame = False
	is_first_point = True
	orig_style = None
	new_style = None
	msg = _('Gradient creating')

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def start_(self):
		self.snap = self.presenter.snap
		self.target = self.selection.objs[0]
		self.selection.clear()
		self.canvas.selection_redraw()
		self.orig_style = self.target.style
		self.new_style = deepcopy(self.orig_style)
		events.emit(events.APP_STATUS, self.msg)

	def escape_pressed(self):
		self.api.set_temp_style(self.target, self.orig_style)
		self.canvas.set_mode()

	def _update_style(self):
		fill_style = self.new_style[0]
		mode = sk2_const.GRADIENT_LINEAR
		rule = sk2_const.FILL_EVENODD
		p0 = [] + self.start
		if self.end:
			p1 = [] + self.end
		else:
			p1 = [] + p0
		vector = [p0, p1]
		stops = deepcopy(DEFAULT_STOPS)
		if fill_style:
			rule = fill_style[0]
			if fill_style[1] == sk2_const.FILL_SOLID:
				rule = fill_style[0]
				color0 = deepcopy(fill_style[2])
				color0[3] = ''
				color1 = deepcopy(color0)
				color1[2] = 0.0
				stops = [[0.0, color0], [1.0, color1]]
			elif fill_style[1] == sk2_const.FILL_GRADIENT:
				rule = fill_style[0]
				mode = fill_style[2][0]
				stops = fill_style[2][2]
		self.new_style[0] = [rule, sk2_const.FILL_GRADIENT,
							[mode, vector, stops]]

	def mouse_down(self, event):
		if not self.start:
			self.start = self.snap.snap_point(event.get_point())[2]
		else:
			self.is_first_point = False

	def mouse_move(self, event):
		if self.start:
			self.end = self.snap.snap_point(event.get_point())[2]
			self._update_style()
			style = deepcopy(self.new_style)
			self.api.set_temp_style(self.target, style)
			events.emit(events.APP_STATUS, self.msg)

	def mouse_up(self, event):
		p = self.snap.snap_point(event.get_point())[2]
		if not p == self.start:
			self.end = p
			self.do_action()

	def stop_(self):
		self.start = []
		self.end = []
		obj = self.target
		self.target = None
		self.orig_style = None
		self.new_style = None
		self.is_first_point = True
		self.selection.set([obj, ])

	def repaint(self):
		x0, y0, x1, y1 = self.target.cache_bbox
		p0 = self.canvas.point_doc_to_win([x0, y0])
		p1 = self.canvas.point_doc_to_win([x1, y1])
		self.canvas.renderer.draw_frame(p0, p1)
		if self.start and self.end:
			p0 = self.canvas.point_doc_to_win(self.start)
			p1 = self.canvas.point_doc_to_win(self.end)
			self.canvas.renderer.draw_gradient_vector(p0, p1)

	def do_action(self):
		self._update_style()
		self.target.style = self.orig_style
		self.selection.set([self.target, ])
		self.api.set_fill_style(deepcopy(self.new_style[0]))
		self.canvas.restore_mode()


class GradientEditor(AbstractController):

	mode = modes.GR_EDIT_MODE
	moved_point = None
	vector = []
	msg = _('Gradient in editing')

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def start_(self):
		self.snap = self.presenter.snap
		self.target = self.selection.objs[0]
		self.selection.clear()
		self.canvas.selection_redraw()
		self.orig_style = self.target.style
		self.new_style = deepcopy(self.orig_style)
		self.vector = self._get_doc_vector(self.orig_style)
		events.emit(events.APP_STATUS, self.msg)

	def escape_pressed(self):
		if self.moved_point:
			self.new_style = None
			self.api.set_temp_style(self.target, self.orig_style)
			self.selection.set([self.target, ])
		self.canvas.set_mode()

	def _get_win_vector(self, style):
		vector = style[0][2][1]
		vector = libgeom.apply_trafo_to_points(vector, self.target.fill_trafo)
		p0 = self.canvas.point_doc_to_win(vector[0])
		p1 = self.canvas.point_doc_to_win(vector[1])
		return p0, p1

	def _get_doc_vector(self, style):
		ret = []
		vector = style[0][2][1]
		vector = libgeom.apply_trafo_to_points(vector, self.target.fill_trafo)
		for item in vector:
			ret.append(VectorPoint(self.canvas, item))
		return ret

	def _set_target_vector(self, temp=True):
		itrafo = libgeom.invert_trafo(self.target.fill_trafo)
		vector = [self.vector[0].point, self.vector[1].point]
		self.new_style[0][2][1] = libgeom.apply_trafo_to_points(vector, itrafo)
		if temp:
			self.api.set_temp_style(self.target, self.new_style)
		else:
			self.api.set_fill_style(deepcopy(self.new_style[0]))
		events.emit(events.APP_STATUS, self.msg)

	def repaint(self):
		x0, y0, x1, y1 = self.target.cache_bbox
		p0 = self.canvas.point_doc_to_win([x0, y0])
		p1 = self.canvas.point_doc_to_win([x1, y1])
		self.canvas.renderer.draw_frame(p0, p1)
		p0, p1 = self._get_win_vector(self.target.style)
		self.canvas.renderer.draw_gradient_vector(p0, p1)

	def stop_(self):
		if self.target and self.new_style:
			self.selection.set([self.target, ])
			self._set_target_vector(False)
		self.target = None
		self.orig_style = None
		self.new_style = None
		self.moved_point = None

	def mouse_down(self, event):
		point = event.get_point()
		if self.vector[0].is_pressed(point):
			self.moved_point = self.vector[0]
		elif self.vector[1].is_pressed(point):
			self.moved_point = self.vector[1]

	def mouse_move(self, event):
		if self.moved_point:
			self.moved_point.point = self.snap.snap_point(event.get_point())[2]
			self._set_target_vector()

	def mouse_up(self, event):
		point = event.get_point()
		if self.moved_point:
			self.moved_point.point = self.snap.snap_point(point)[2]
			self._set_target_vector()
			self.moved_point = None
		else:
			objs = self.canvas.pick_at_point(point)
			if objs and objs[0].is_primitive() and not objs[0].is_pixmap():
				self._set_target_vector(False)
				self.target = None
				self.selection.set([objs[0], ])
				self.canvas.restore_mode()


class VectorPoint:

	point = []
	canvas = None

	def __init__(self, canvas, doc_point):
		self.point = doc_point
		self.canvas = canvas

	def is_pressed(self, win_point):
		wpoint = self.canvas.point_doc_to_win(self.point)
		bbox = libgeom.bbox_for_point(wpoint, config.point_sensitivity_size)
		return libgeom.is_point_in_bbox(win_point, bbox)



