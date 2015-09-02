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

from uc2.formats.sk2 import sk2_model
from uc2.formats.sk2 import sk2_const

from sk1 import modes
from generic import AbstractController

class GradientChooser(AbstractController):

	mode = modes.GR_SELECT_MODE

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def start_(self):
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
		print 'Restoring'
#		self.start_()

	def stop_(self):
		print '--> stop'

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

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def start_(self):
		self.target = self.selection.objs[0]
		self.selection.clear()

	def mouse_down(self, event):pass

	def mouse_up(self, event):
		if not self.start:
			self.start = list(event.GetPositionTuple())
		else:
			self.end = list(event.GetPositionTuple())
			self.do_action()

	def stop_(self):
		print 'Create stop'
		self.start = []
		self.end = []
		self.selection.set([self.target, ])
		self.target = None

	def do_action(self):
		self.canvas.restore_mode()


class GradientEditor(AbstractController):

	mode = modes.GR_EDIT_MODE

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

