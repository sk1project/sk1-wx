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

from copy import deepcopy

from uc2 import libgeom

from sk1 import _, modes, events

from generic import AbstractController


class TextEditController(AbstractController):

	mode = modes.TEXT_EDIT_MODE
	target = None
	text_cursor = 0
	text = ''
	trafos = {}
	markup = []

	def start_(self):
		self.snap = self.presenter.snap
		self.target = self.selection.objs[0]
		self.selection.clear()
		self.update_from_target()
		msg = _('Text in editing')
		events.emit(events.APP_STATUS, msg)

	def stop_(self):
		if not self.text:
			parent = self.target.parent
			index = parent.childs.index(self.target)
			self.api.delete_object(self.target, parent, index)
		else:
			self.selection.set([self.target, ])
		self.target = None

	def escape_pressed(self):
		self.canvas.set_mode()

	def update_from_target(self):
		self.text = self.target.get_text()
		self.trafos = deepcopy(self.target.trafos)
		self.markup = deepcopy(self.target.markup)
		self.text_cursor = len(self.text)

	def update_target(self):
		self.presenter.api.change_text(self.target, '' + self.text,
								deepcopy(self.trafos), deepcopy(self.markup))

	def set_text_cursor(self, val):
		if val < 0: val = 0
		if val > len(self.text):val = len(self.text)
		self.text_cursor = val
		self.canvas.selection_redraw()

	#--- Keyboard calls
	def key_left(self):
		self.set_text_cursor(self.text_cursor - 1)

	def key_right(self):
		self.set_text_cursor(self.text_cursor + 1)

	def key_up(self):pass
	def key_down(self):pass

	def key_backspace(self):
		if self.text_cursor > 0:
			self.text_cursor -= 1
			self.delete_char()

	def key_del(self):
		if self.text_cursor < len(self.text):
			self.delete_char()

	#--- Text modifiers
	def _delete_char(self, index):
		if index == len(self.text) - 1:
			self.text = self.text[:-1]
		else:
			self.text = self.text[:index] + self.text[index + 1:]
		if index in self.trafos:
			self.trafos.pop(index, None)

	def _insert_char(self, char, index):
		if index == len(self.text) - 1:
			self.text += char
		else:
			self.text = self.text[:index] + char + self.text[index:]
		trafos = {}
		for item in self.trafos.keys():
			if item < index:
				trafos[item] = self.trafos[item]
			else:
				trafos[item + 1] = self.trafos[item]
		self.trafos = trafos

	def delete_char(self):
		if self.text_cursor < len(self.text):
			self._delete_char(self.text_cursor)
			self.update_target()

	def insert_char(self, char):
		self._insert_char(char, self.text_cursor)
		self.text_cursor += 1
		self.update_target()

	#--- REPAINT

	def repaint(self):
		bbox = self.target.cache_layout_bbox
		self.canvas.renderer.draw_text_frame(bbox, self.target.trafo)
		self.paint_cursor()

	def paint_cursor(self):
		if self.text_cursor < len(self.target.cache_layout_data):
			data = self.target.cache_layout_data[self.text_cursor]
			p0 = [data[0], data[1]]
			p1 = [data[0], data[1] - data[3]]
		else:
			data = self.target.cache_layout_data[-1]
			if ord(self.text[-1]) == 13:
				p0 = [0.0, data[1] - data[3]]
				p1 = [0.0, data[1] - 2.0 * data[3]]
			else:
				p0 = [data[0] + data[2], data[1]]
				p1 = [data[0] + data[2], data[1] - data[3]]
		trafo = self.target.trafo
		if self.text_cursor in self.trafos:
			trafo = self.trafos[self.text_cursor]
		p0, p1 = libgeom.apply_trafo_to_points([p0, p1], trafo)
		p0 = self.canvas.point_doc_to_win(p0)
		p1 = self.canvas.point_doc_to_win(p1)
		self.canvas.renderer.draw_text_cursor(p0, p1)
