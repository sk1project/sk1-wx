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

from uc2 import uc2const
from uc2.formats.sk2 import sk2_model
from uc2.formats.sk2 import sk2_const

from sk1 import modes
from generic import AbstractController, RENDERING_DELAY

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
		if self.timer.IsRunning(): self.timer.Stop()
		sel_objs = self.selection.objs
		if len(sel_objs) == 1 and sel_objs[0].cid > sk2_model.PRIMITIVE_CLASS \
			and not sel_objs[0].cid == sk2_model.PIXMAP:
			if sel_objs[0].style[0] and sel_objs[0].style[0][1] == sk2_const.FILL_GRADIENT:
				self.canvas.set_temp_mode(modes.GR_EDIT_MODE)
			else:
				self.canvas.set_temp_mode(modes.GR_CREATE_MODE)
		else:
			self.selection.clear()

	def restore(self):
		if not self.timer.IsRunning():
			self.timer_callback = self.start_
			self.timer.Start(RENDERING_DELAY)

	def stop_(self):pass

	def mouse_down(self, event):pass

	def mouse_up(self, event):
		self.end = list(event.GetPositionTuple())
		self.do_action()

	def mouse_move(self, event):pass

	def do_action(self):
		objs = self.canvas.pick_at_point(self.end)
		if objs and objs[0].cid > sk2_model.PRIMITIVE_CLASS \
		and not objs[0].cid == sk2_model.PIXMAP:
			self.selection.set([objs[0], ])
			self.start_()


class GradientCreator(AbstractController):

	mode = modes.GR_CREATE_MODE
	target = None
	is_frame = False
	is_first_point = True

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def start_(self):
		self.target = self.selection.objs[0]
		self.selection.clear()

	def mouse_down(self, event):
		if not self.start:
			self.start = list(event.GetPositionTuple())
		else:
			self.is_first_point = False

	def mouse_move(self, event):
		if not self.is_frame:
			x0, y0, x1, y1 = self.target.cache_bbox
			p0 = self.canvas.point_doc_to_win([x0, y0])
			p1 = self.canvas.point_doc_to_win([x1, y1])
			self.canvas.renderer.cdc_draw_frame(p0, p1)
			self.is_frame = True

	def mouse_up(self, event):
		p = list(event.GetPositionTuple())
		if self.is_first_point and not self.end and not p == self.start:
			self.end = list(event.GetPositionTuple())
			self.do_action()
		elif not self.is_first_point:
			self.end = list(event.GetPositionTuple())
			self.do_action()
			self.is_first_point = True

	def stop_(self):
		self.start = []
		self.end = []
		self.target = None
		if self.is_frame:
			self.canvas.renderer.cdc_hide_move_frame()
			self.is_frame = False
#		self.selection.set([self.target, ])

	def do_action(self):
		fill_style = self.target.style[0]
		mode = sk2_const.GRADIENT_LINEAR
		rule = sk2_const.FILL_EVENODD
		p0 = self.canvas.point_win_to_doc(self.start)
		p1 = self.canvas.point_win_to_doc(self.end)
		vector = [p0, p1]
		stops = deepcopy(DEFAULT_STOPS)
		if fill_style:
			rule = fill_style[0]
			if fill_style[1] == sk2_const.FILL_SOLID:
				color0 = deepcopy(fill_style[2])
				color0[3] = ''
				color1 = deepcopy(color0)
				color1[2] = 0.0
				stops = [[0.0, color0], [1.0, color1]]
		new_fill_style = [rule, sk2_const.FILL_GRADIENT,
						[mode, vector, stops]]
		if self.is_frame:
			self.canvas.renderer.cdc_hide_move_frame()
			self.is_frame = False
		self.selection.set([self.target, ])
		self.presenter.api.set_fill_style(new_fill_style)
		self.canvas.restore_mode()


class GradientEditor(AbstractController):

	mode = modes.GR_EDIT_MODE

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

