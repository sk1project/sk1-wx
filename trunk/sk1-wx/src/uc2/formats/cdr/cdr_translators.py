# -*- coding: utf-8 -*-
#
#	Copyright (C) 2012 by Igor E. Novikov
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

from copy import deepcopy

from uc2.formats.pdxf.const import FILL_EVENODD, FILL_SOLID, STROKE_MIDDLE
from uc2.formats.pdxf import model

class CDR_to_PDXF_Translator:

	default_style = None
	parent_stack = []
	page_counter = 0

	stroke_props = {}
	fill_props = {}
	font_props = {}

	def translate(self, cdr_doc, pdxf_doc):
		self.pdxf_doc = pdxf_doc
		self.methods = pdxf_doc.methods
		self.methods.delete_pages()
		self.stroke_props = {}
		self.fill_props = {}
		self.font_props = {}
		self.parent_stack = []

		self.default_style = [deepcopy(pdxf_doc.config.default_fill),
				deepcopy(pdxf_doc.config.default_stroke),
				deepcopy(pdxf_doc.config.default_text_style),
				deepcopy(pdxf_doc.config.default_structural_style)]

		cdr_doc.model.translate(self)

		pdxf_doc.model.do_update()

	def set_doc_properties(self, obj):
		self.methods.set_default_page_size(obj.page_width, obj.page_height)

	def add_fill_prop(self, obj):
		if obj.fill_color:
			self.fill_props[obj.fill_id] = [FILL_EVENODD, FILL_SOLID, obj.fill_color]
		else:
			self.fill_props[obj.fill_id] = []

	def get_fill_prop(self, id):
		res = []
		if self.fill_props.has_key(id):
			res = deepcopy(self.fill_props[id])
		return res

	def add_stroke_prop(self, obj):
		if obj.stroke_spec & 0x01:
			self.stroke_props[obj.stroke_id] = []
			return
		else:
			color = obj.stroke_color

		if not obj.stroke_color:
			self.stroke_props[obj.stroke_id] = []
			return

		if obj.stroke_spec & 0x04:
			dashes = obj.stroke_dashes
		else:
			dashes = []

		if obj.stroke_spec & 0x02:
			scalable_flag = 1
		else:
			scalable_flag = 0

		self.stroke_props[obj.stroke_id] = [
					STROKE_MIDDLE,
					obj.stroke_width,
					color,
					dashes,
					obj.stroke_caps + 1,
					obj.stroke_join,
					self.pdxf_doc.config.default_stroke_miter_limit,
					self.pdxf_doc.config.default_stroke_behind_flag,
					scalable_flag,
					self.pdxf_doc.config.default_stroke_markers
											]

	def get_stroke_prop(self, id):
		res = []
		if self.stroke_props.has_key(id):
			res = deepcopy(self.stroke_props[id])
		return res

	def add_font_prop(self, obj):
		self.font_props[obj.font_id] = obj.font_name

	def get_font_prop(self, id):
		res = ''
		if self.font_props.has_key(id):
			res = deepcopy(self.stroke_props[id])
		return res

	def start_page(self, obj):
		if not self.page_counter:
			self.page_counter += 1
			return False
		page = self.methods.insert_page()
		self.parent_stack.append(page)
		return True

	def close_page(self):
		self.parent_stack = self.parent_stack[:-1]

	def start_layer(self, obj):
		page = self.parent_stack[-1]
		layer_name = ''
		if obj.layer_name: layer_name = str(obj.layer_name)
		layer = self.methods.add_layer(page, layer_name)
		self.parent_stack.append(layer)

	def close_layer(self):
		self.parent_stack = self.parent_stack[:-1]

	def start_group(self):
		parent = self.parent_stack[-1]
		config = self.pdxf_doc.config
		group = model.Group(config, parent)
		self.methods.append_object(group, parent)
		self.parent_stack.append(group)

	def close_group(self):
		group = self.parent_stack[-1]
		self.parent_stack = self.parent_stack[:-1]
		if not group.childs:
			self.methods.delete_object(group)

	def create_curve(self, obj):
		config = self.pdxf_doc.config
		parent = self.parent_stack[-1]
		paths = deepcopy(obj.paths)
		trafo = deepcopy(obj.trafo)
		if not obj.style_id is None and obj.fill_id is None and obj.outl_id is None:
			style = [[], deepcopy(config.default_stroke), [], []]
		else:
			if obj.fill_id is None:	fill = []
			else: fill = self.get_fill_prop(obj.fill_id)
			if obj.outl_id is None:	stroke = []
			else: stroke = self.get_stroke_prop(obj.outl_id)
			style = [fill, stroke, [], []]
		curve = model.Curve(config, parent, paths, trafo, style)
		self.methods.append_object(curve, parent)

	def create_rectangle(self, obj):
		config = self.pdxf_doc.config
		parent = self.parent_stack[-1]

		w, h = obj.rect_size
		x = y = 0.0
		if w < 0: x = w;w = -w
		if h < 0: y = h;h = -h
		mr = min(w, h) / 2.0
		r1, r2, r3, r4 = obj.radiuses
		radiuses = [r1 / mr, r2 / mr, r3 / mr, r4 / mr]

		trafo = deepcopy(obj.trafo)
		if not obj.style_id is None and obj.fill_id is None and obj.outl_id is None:
			style = [[], deepcopy(config.default_stroke), [], []]
		else:
			if obj.fill_id is None:	fill = []
			else: fill = self.get_fill_prop(obj.fill_id)
			if obj.outl_id is None:	stroke = []
			else: stroke = self.get_stroke_prop(obj.outl_id)
			style = [fill, stroke, [], []]

		rect = model.Rectangle(config, parent, [x, y, w, h], trafo, style, radiuses)
		self.methods.append_object(rect, parent)

	def create_ellipse(self, obj):pass
	def create_polygon(self, obj):pass
	def create_image(self, obj):pass
	def create_text(self, obj):pass
