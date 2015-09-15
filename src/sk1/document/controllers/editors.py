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
from uc2.formats.sk2 import sk2_model
from uc2.formats.sk2 import sk2_const

from sk1 import modes, config
from generic import AbstractController, RENDERING_DELAY

class EditorChooser(AbstractController):

	mode = modes.SHAPER_MODE

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def start_(self):
		sel_objs = self.selection.objs
		if len(sel_objs) == 1 and sel_objs[0].cid == sk2_model.CURVE:
			self.canvas.set_temp_mode(modes.BEZIER_EDITOR_MODE)
		else:
			self.selection.clear()

	def restore(self):
		if not self.timer.IsRunning():
			self.timer.Start(RENDERING_DELAY)

	def stop_(self):pass

	def on_timer(self):
		if self.timer.IsRunning(): self.timer.Stop()
		self.start_()

	def mouse_down(self, event):pass

	def mouse_up(self, event):
		self.end = event.get_point()
		self.do_action()

	def mouse_move(self, event):pass

	def do_action(self):
		objs = self.canvas.pick_at_point(self.end)
		if objs and objs[0].cid > sk2_model.PRIMITIVE_CLASS \
		and not objs[0].cid == sk2_model.PIXMAP:
			self.selection.set([objs[0], ])
			self.start_()

class BezierEditor(AbstractController):

	mode = modes.BEZIER_EDITOR_MODE
	target = None

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def start_(self):
		self.snap = self.presenter.snap
		self.target = self.selection.objs[0]
		self.selection.clear()
		self.canvas.selection_redraw()

	def stop_(self):
		self.selection.set([self.target, ])
		self.target = None

	def escape_pressed(self):
		self.canvas.set_mode()

	def repaint(self):
		x0, y0, x1, y1 = self.target.cache_bbox
		p0 = self.canvas.point_doc_to_win([x0, y0])
		p1 = self.canvas.point_doc_to_win([x1, y1])
		self.canvas.renderer.draw_frame(p0, p1)

	def _collect_paths(self):pass

class BerzierNode:

	first = False
	last = False
	point = []
	canvas = None

	def __init__(self, canvas, point, first=False, last=False):
		self.canvas = canvas
		self.point = point
		self.first = first
		self.last = last

	def is_pressed(self, win_point):
		wpoint = self.canvas.point_doc_to_win(self.point)
		bbox = libgeom.bbox_for_point(wpoint, config.point_sensitivity_size)
		return libgeom.is_point_in_bbox(win_point, bbox)
