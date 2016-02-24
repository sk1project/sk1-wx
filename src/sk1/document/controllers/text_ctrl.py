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
	line_num = 0
	line_pos = 0
	lines = []
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
		self.update_lines()
		self.set_text_cursor(len(self.text))

	def update_target(self):
		self.presenter.api.change_text(self.target, '' + self.text,
								deepcopy(self.trafos), deepcopy(self.markup))
		self.update_lines()

	def update_lines(self):
		self.lines = []
		index = 0
		for item in self.text.split('\n'):
			self.lines.append((index, index + len(item)))
			index += len(item) + 1

	def set_line_pos(self):
		index = 0
		for line in self.lines:
			if not self.text_cursor > line[1]:
				self.line_num = index
				break
			index += 1
		self.line_pos = self.text_cursor - line[0]

	def set_text_cursor(self, val):
		if val < 0: val = 0
		if val > len(self.text):val = len(self.text)
		self.text_cursor = val
		self.set_line_pos()
		self.canvas.selection_redraw()

	#--- Keyboard calls
	def key_left(self):
		self.set_text_cursor(self.text_cursor - 1)

	def key_right(self):
		self.set_text_cursor(self.text_cursor + 1)

	def key_up(self):
		if not self.line_num: return
		self.line_num -= 1
		line = self.lines[self.line_num]
		pos = self.line_pos + line[0]
		if not pos < line[1]: pos = line[1]
		self.set_text_cursor(pos)

	def key_down(self):
		if not self.line_num < len(self.lines) - 1: return
		self.line_num += 1
		line = self.lines[self.line_num]
		pos = self.line_pos + line[0]
		if not pos < line[1]: pos = line[1]
		self.set_text_cursor(pos)

	def key_home(self):
		self.set_text_cursor(self.lines[self.line_num][0])

	def key_end(self):
		self.set_text_cursor(self.lines[self.line_num][1])

	def key_backspace(self):
		if self.text_cursor > 0:
			self.set_text_cursor(self.text_cursor - 1)
			self.delete_char()

	def key_del(self):
		if self.text_cursor < len(self.text):
			self.delete_char()

	def key_ctrl_home(self):
		self.set_text_cursor(0)

	def key_ctrl_end(self):
		self.set_text_cursor(len(self.text))

	#--- Text modifiers
	def _delete_char(self, index):
		if index == len(self.text) - 1:
			self.text = self.text[:-1]
		else:
			self.text = self.text[:index] + self.text[index + 1:]
		if index in self.trafos:
			self.trafos.pop(index, None)

	def _insert_text(self, text, index):
		if index == len(self.text) - 1:
			self.text += text
		else:
			self.text = self.text[:index] + text + self.text[index:]
		trafos = {}
		for item in self.trafos.keys():
			if item < index:
				trafos[item] = self.trafos[item]
			else:
				trafos[item + len(text)] = self.trafos[item]
		self.trafos = trafos

	def delete_char(self):
		if self.text_cursor < len(self.text):
			self._delete_char(self.text_cursor)
			self.update_target()

	def insert_text(self, text):
		self._insert_text(text, self.text_cursor)
		self.update_target()
		self.set_text_cursor(self.text_cursor + len(text))

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
