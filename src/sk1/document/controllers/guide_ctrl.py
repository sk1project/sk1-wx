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

from uc2 import uc2const

from sk1 import modes
from sk1.appconst import RENDERING_DELAY
from generic import AbstractController

class GuideController(AbstractController):

	mode = modes.HGUIDE_MODE
	guide = None

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def mouse_down(self, event):
		self.draw = True
		self.end = event.get_point()
		self.timer.Start(RENDERING_DELAY)

	def mouse_move(self, event):
		self.end = event.get_point()
		if not self.draw:
			if not self.snap.is_over_guide(self.end)[0]:
				self.canvas.restore_mode()
			else:
				self.guide = self.snap.active_guide
				self.set_cursor()

	def mouse_up(self, event):
		self.end = event.get_point()
		self.draw = False
		if self.mode == modes.HGUIDE_MODE and self.end[1] > 0:
			p_doc = self.presenter.snap.snap_point(self.end, snap_x=False)[2]
			pos = p_doc[1]
			orient = uc2const.HORIZONTAL
			self.presenter.api.set_guide_propeties(self.guide, pos, orient)
		elif self.mode == modes.VGUIDE_MODE and self.end[0] > 0:
			p_doc = self.presenter.snap.snap_point(self.end, snap_y=False)[2]
			orient = uc2const.VERTICAL
			pos = p_doc[0]
			self.presenter.api.set_guide_propeties(self.guide, pos, orient)
		else:
			self.presenter.api.delete_guides([self.guide])
		self.canvas.dragged_guide = ()
		self.canvas.selection_redraw()

	def start_(self):
		self.snap = self.presenter.snap
		if not self.snap.active_guide is None:
			self.guide = self.snap.active_guide
			self.set_cursor()

	def stop_(self):
		self.presenter.snap.active_guide = None
		self.timer.Stop()
		self.canvas.selection_redraw()
		self.end = []
		self.guide = None

	def set_cursor(self):
		if not self.guide is None:
			if self.guide.orientation == uc2const.HORIZONTAL:
				mode = modes.HGUIDE_MODE
			else:
				mode = modes.VGUIDE_MODE
			self.mode = mode
			self.canvas.set_canvas_cursor(mode)

	def repaint(self):
		p_doc = []
		orient = uc2const.HORIZONTAL
		if self.end:
			if self.mode == modes.HGUIDE_MODE:
				p_doc = self.presenter.snap.snap_point(self.end, snap_x=False)[2]
			else:
				p_doc = self.presenter.snap.snap_point(self.end, snap_y=False)[2]
				orient = uc2const.VERTICAL
		self.canvas.renderer.cdc_drag_guide([p_doc, orient])
