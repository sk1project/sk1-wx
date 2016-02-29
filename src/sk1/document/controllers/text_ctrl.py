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

NON_WORD_CHARS = ' \n\t!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~'
NON_WORD_CHARS += '¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿÷'


class TextEditController(AbstractController):

	mode = modes.TEXT_EDIT_MODE
	target = None
	text = ''
	trafos = {}
	markup = []

	text_cursor = 0
	line_num = 0
	line_pos = 0
	lines = []

	selected = []
	drag = False
	prev_pos = 0
	prev_sel = []

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)
		self.canvas.eventloop.connect(self.eventloop.DOC_MODIFIED,
									self.doc_modified)

	def start_(self):
		self.snap = self.presenter.snap
		self.target = self.selection.objs[0]
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

	def doc_modified(self, *args):
		if self.canvas.mode == modes.TEXT_EDIT_MODE:
			pos = self.text_cursor
			self.update_from_target()
			self.set_text_cursor(pos)

	def escape_pressed(self):
		self.canvas.set_mode()

	def update_from_target(self):
		self.start = []
		self.end = []
		self.selection.clear()
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

	def set_text_cursor(self, pos, selection=False):
		if pos < 0: pos = 0
		if pos > len(self.text):pos = len(self.text)
		if not selection:self.selected = []
		self.text_cursor = pos
		self.set_line_pos()
		self.canvas.selection_redraw()

	def set_selected(self, pos):
		if pos < 0: pos = 0
		if pos > len(self.text):pos = len(self.text)
		dx = pos - self.text_cursor
		if not self.selected:
			self.selected = [self.text_cursor, self.text_cursor]

		if self.selected[0] > pos:
			self.selected = [pos, self.selected[1]]
		elif self.selected[1] > pos and dx > 0:
			self.selected = [pos, self.selected[1]]
		elif self.selected[1] > pos and dx < 0:
			self.selected = [self.selected[0], pos]
		elif self.selected[1] == pos:
			self.selected = []
		elif self.selected[1] < pos:
			self.selected = [self.selected[0], pos]

		events.emit(events.SELECTION_CHANGED)

	def is_selected(self):
		return not self.selected == []

	def is_pos_in_selected(self, pos):
		return not pos < self.selected[0] and not pos > self.selected[1]

	def get_selected(self):
		if not self.selected: return ''
		return self.text[self.selected[0]:self.selected[1]]

	def delete_selected(self):
		if self.selected:
			self._delete_text_range(self.selected)
			self.set_text_cursor(self.selected[0])
			self.update_target()

	def replace_selected(self, text):
		if self.selected:
			self._delete_text_range(self.selected)
			self.set_text_cursor(self.selected[0])
		self.insert_text(text)

	def select_all(self):
		self.set_text_cursor(0)
		self.set_selected(len(self.text))
		self.set_text_cursor(len(self.text), True)

	def deselect(self):
		self.selected = []
		self.canvas.selection_redraw()

	def upper_selected(self):
		text = self.get_selected()
		if text: self.replace_selected(text.upper())

	def lower_selected(self):
		text = self.get_selected()
		if text: self.replace_selected(text.lower())

	def capitalize_selected(self):
		text = self.get_selected()
		if text: self.replace_selected(text.capitalize())



	#--- Keyboard calls
	def key_left(self, shift=False):
		if shift: self.set_selected(self.text_cursor - 1)
		self.set_text_cursor(self.text_cursor - 1, shift)

	def key_right(self, shift=False):
		if shift: self.set_selected(self.text_cursor + 1)
		self.set_text_cursor(self.text_cursor + 1, shift)

	def key_up(self, shift=False):
		if not self.line_num: return
		self.line_num -= 1
		line = self.lines[self.line_num]
		pos = self.line_pos + line[0]
		if not pos < line[1]: pos = line[1]
		if shift: self.set_selected(pos)
		self.set_text_cursor(pos, shift)

	def key_down(self, shift=False):
		if not self.line_num < len(self.lines) - 1: return
		self.line_num += 1
		line = self.lines[self.line_num]
		pos = self.line_pos + line[0]
		if not pos < line[1]: pos = line[1]
		if shift: self.set_selected(pos)
		self.set_text_cursor(pos, shift)

	def key_home(self, shift=False):
		if shift: self.set_selected(self.lines[self.line_num][0])
		self.set_text_cursor(self.lines[self.line_num][0], shift)

	def key_end(self, shift=False):
		if shift: self.set_selected(self.lines[self.line_num][1])
		self.set_text_cursor(self.lines[self.line_num][1], shift)

	def key_backspace(self):
		if self.selected:
			self.delete_selected()
		elif self.text_cursor > 0:
			self.set_text_cursor(self.text_cursor - 1)
			self.delete_char()

	def key_del(self):
		if self.selected:
			self.delete_selected()
		elif self.text_cursor < len(self.text):
			self.delete_char()

	def key_ctrl_home(self, shift=False):
		if shift: self.set_selected(0)
		self.set_text_cursor(0, shift)

	def key_ctrl_end(self, shift=False):
		if shift: self.set_selected(len(self.text))
		self.set_text_cursor(len(self.text), shift)

	#--- Mouse calls
	def is_point_in_layout_bbox(self, point):
		bbox = self.target.cache_layout_bbox
		doc_point = self.canvas.win_to_doc(point)
		inv_trafo = libgeom.invert_trafo(self.target.trafo)
		doc_point = libgeom.apply_trafo_to_point(doc_point, inv_trafo)
		return libgeom.is_point_in_bbox(doc_point, bbox)

	def get_index_by_point(self, point):
		doc_point = self.canvas.win_to_doc(point)
		inv_trafo = libgeom.invert_trafo(self.target.trafo)
		doc_point = libgeom.apply_trafo_to_point(doc_point, inv_trafo)

		line = -1
		for item in self.target.cache_line_points:
			line += 1
			if doc_point[1] >= item[1]: break

		index = self.lines[line][0]
		for item in range(*self.lines[line]):
			layout = self.target.cache_layout_data
			pos = layout[index][0] + layout[index][2] / 2.0
			if doc_point[0] <= pos: break
			index += 1
		return index

	def mouse_down(self, event):
		self.start = event.get_point()
		self.prev_pos = self.text_cursor
		self.prev_sel = [] + self.selected
		pos = self.get_index_by_point(self.start)
		if self.selected and self.is_pos_in_selected(pos):
			self.drag = True
			self.set_text_cursor(pos, True)
		else:
			self.set_text_cursor(pos)
			self.set_selected(pos)

	def mouse_move(self, event):
		if self.start:
			pos = self.get_index_by_point(event.get_point())
			if not pos == self.text_cursor:
				if not self.drag:
					self.set_selected(pos)
				self.set_text_cursor(pos, True)

	def mouse_up(self, event):
		self.end = event.get_point()
		if self.end == self.start:
			if self.drag:
				self.drag = False
				self.set_text_cursor(self.get_index_by_point(self.end))
			elif self.is_point_in_layout_bbox(self.end):
				pos = self.get_index_by_point(self.end)
				if event.is_shift():
					if self.prev_sel and self.prev_pos == self.prev_sel[0]:
						start = self.prev_sel[1]
					elif self.prev_sel and self.prev_pos == self.prev_sel[1]:
						start = self.prev_sel[0]
					else:
						start = self.prev_pos
					print start, self.prev_pos, self.selected
					self.set_text_cursor(start)
					self.set_selected(pos)
					self.set_text_cursor(pos, True)
				else:
					self.set_text_cursor(pos)
			else:
				point = self.end
				if not self.text:
					parent = self.target.parent
					index = parent.childs.index(self.target)
					self.api.delete_object(self.target, parent, index)
				objs = self.canvas.pick_at_point(point)
				if objs and objs[0].is_text():
					self.target = objs[0]
				else:
					doc_point = self.canvas.win_to_doc(point)
					self.target = self.api.create_text(doc_point)
				self.update_from_target()
				self.canvas.selection_redraw()
		else:
			if self.drag:
				self.drag = False
				pos = self.get_index_by_point(self.end)
				if self.is_pos_in_selected(pos):
					self.set_text_cursor(pos)
				else:
					sel = self.get_selected()
					if pos > self.selected[1]: pos -= len(sel)
					self._delete_text_range(self.selected)
					self.set_text_cursor(pos)
					self.insert_text(sel)

		#---
		self.start = []
		self.end = []

	def mouse_double_click(self, event):
		self.end = event.get_point()
		if self.text:
			if self.is_point_in_layout_bbox(self.end):
				start = self.text_cursor
				while True:
					if not start: break
					if not self.text[start - 1] in NON_WORD_CHARS:
						start -= 1
					else: break
				end = self.text_cursor
				while True:
					if end == len(self.text): break
					if not self.text[end] in NON_WORD_CHARS:
						end += 1
					else: break
				if not start == end:
					self.selected = [start, end]
					self.set_text_cursor(end, True)
					events.emit(events.SELECTION_CHANGED)

	#--- Text modifiers
	def _delete_char(self, index):
		if index == len(self.text) - 1:
			self.text = self.text[:-1]
		else:
			self.text = self.text[:index] + self.text[index + 1:]
		if index in self.trafos:
			self.trafos.pop(index, None)

	def _delete_text_range(self, text_range):
		if text_range[1] == len(self.text):
			self.text = self.text[:text_range[0]]
		elif not text_range[0]:
			self.text = self.text[text_range[1]:]
		else:
			self.text = self.text[:text_range[0]] + self.text[text_range[1]:]
		deleted = range(*text_range)
		for item in self.trafos:
			if item in deleted:
				self.trafos.pop(item, None)

	def _insert_text(self, text, index):
		if index == len(self.text):
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
		self.paint_selection()
		self.paint_cursor()

	def paint_selection(self):
		if not self.selected or self.selected[0] == self.selected[1]: return
		sel_blocks = []
		for line in self.lines:
			block = []
			indexes = range(*line)
			if not indexes: continue

			if self.selected[0] in indexes:
				block.append(self.selected[0])
			elif self.selected[0] < indexes[0]:
				block.append(indexes[0])
			else:
				continue

			if self.selected[1] in indexes:
				block.append(self.selected[1])
				sel_blocks.append(block)
				break
			elif self.selected[1] > indexes[-1]:
				block.append(indexes[-1] + 1)
				sel_blocks.append(block)

		bboxs = []
		layout = self.target.cache_layout_data
		for item in sel_blocks:
			x0, y0 = layout[item[0]][:2]
			y1 = y0 - layout[item[0]][3]
			x1 = x0
			for i in range(*item):
				x1 += layout[i][2]
			bbox = libgeom.normalize_bbox([x0, y0, x1, y1])
			bboxs.append(bbox)
		if bboxs:
			self.canvas.renderer.draw_text_selection(bboxs, self.target.trafo)

	def paint_cursor(self):
		if self.text_cursor < len(self.target.cache_layout_data):
			data = self.target.cache_layout_data[self.text_cursor]
			p0 = [data[0], data[1]]
			p1 = [data[0], data[1] - data[3]]
		else:
			data = self.target.cache_layout_data[-1]
			if self.text[-1] == '\n':
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
