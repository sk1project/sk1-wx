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
import types, math

from uc2.formats.sk2 import sk2_model as model
from uc2.formats.sk2 import sk2_const
from uc2 import libgeom, uc2const, libimg

from sk1 import events, config, modes


class AbstractAPI:

	presenter = None
	view = None
	methods = None
	model = None
	app = None
	eventloop = None
	undo = []
	redo = []
	undo_marked = False
	selection = None
	callback = None
	sk2_cfg = None

	def do_undo(self):
		transaction_list = self.undo[-1][0]
		for transaction in transaction_list:
			self._do_action(transaction)
		tr = self.undo[-1]
		self.undo.remove(tr)
		self.redo.append(tr)
		self.eventloop.emit(self.eventloop.DOC_MODIFIED)
		if self.undo and self.undo[-1][2]:
			self.presenter.reflect_saving()
		if not self.undo and not self.undo_marked:
			self.presenter.reflect_saving()

	def do_redo(self):
		action_list = self.redo[-1][1]
		for action in action_list:
			self._do_action(action)
		tr = self.redo[-1]
		self.redo.remove(tr)
		self.undo.append(tr)
		self.eventloop.emit(self.eventloop.DOC_MODIFIED)
		if not self.undo or self.undo[-1][2]:
			self.presenter.reflect_saving()

	def _do_action(self, action):
		if not action: return
		if len(action) == 1:
			action[0]()
		elif len(action) == 2:
			action[0](action[1])
		elif len(action) == 3:
			action[0](action[1], action[2])
		elif len(action) == 4:
			action[0](action[1], action[2], action[3])
		elif len(action) == 5:
			action[0](action[1], action[2], action[3], action[4])
		elif len(action) == 6:
			action[0](action[1], action[2], action[3], action[4], action[5])

	def _clear_history_stack(self, stack):
		for obj in stack:
			if type(obj) == types.ListType:
				obj = self._clear_history_stack(obj)
		return []

	def add_undo(self, transaction):
		self.redo = self._clear_history_stack(self.redo)
		self.undo.append(transaction)
		self.eventloop.emit(self.eventloop.DOC_MODIFIED)

	def save_mark(self):
		for item in self.undo:
			item[2] = False
		for item in self.redo:
			item[2] = False

		if self.undo:
			self.undo[-1][2] = True
			self.undo_marked = True

	def _set_mode(self, mode):
		self.presenter.canvas.set_mode(mode)

	def _set_page_format(self, page, page_format):
		self.methods.set_page_format(page, page_format)

	def _set_layer_properties(self, layer, prop):
		layer.properties = prop

	def _set_guide_properties(self, guide, pos, orient):
		guide.position = pos
		guide.orientation = orient

	def _set_selection(self, objs):
		self.selection.objs = [] + objs
		self.selection.update()

	def _selection_update(self):
		self.selection.update()

	def _delete_object(self, obj):
		self.methods.delete_object(obj)
		if obj in self.selection.objs:
			self.selection.remove([obj])

	def _insert_object(self, obj, parent, index):
		self.methods.insert_object(obj, parent, index)

	def _get_pages_snapshot(self):
		return [] + self.presenter.get_pages()

	def _set_pages_snapshot(self, snapshot):
		model = self.presenter.model
		parent = model.childs[0]
		parent.childs = snapshot

	def _get_layers_snapshot(self):
		layers_snapshot = []
		layers = self.presenter.get_editable_layers()
		for layer in layers:
			layers_snapshot.append([layer, [] + layer.childs])
		return layers_snapshot

	def _set_layers_snapshot(self, layers_snapshot):
		for layer, childs in layers_snapshot:
			layer.childs = childs

	def _delete_objects(self, objs_list):
		for item in objs_list:
			obj = item[0]
			self.methods.delete_object(obj)
			if obj in self.selection.objs:
				self.selection.remove([obj])

	def _insert_objects(self, objs_list):
		for obj, parent, index in objs_list:
			self.methods.insert_object(obj, parent, index)

	def _normalize_rect(self, rect):
		x0, y0, x1, y1 = rect
		new_rect = [0, 0, 0, 0]
		if x0 < x1:
			new_rect[0] = x0
			new_rect[2] = x1 - x0
		else:
			new_rect[0] = x1
			new_rect[2] = x0 - x1
		if y0 < y1:
			new_rect[1] = y0
			new_rect[3] = y1 - y0
		else:
			new_rect[1] = y1
			new_rect[3] = y0 - y1
		return new_rect

	def _set_default_style(self, style):
		self.model.styles['Default Style'] = style

	def _get_objs_styles(self, objs):
		result = []
		for obj in objs:
			style = deepcopy(obj.style)
			fill_trafo = deepcopy(obj.fill_trafo)
			stroke_trafo = deepcopy(obj.stroke_trafo)
			result.append([obj, style, fill_trafo, stroke_trafo])
		return result

	def _set_objs_styles(self, objs_styles):
		for obj, style, fill_trafo, stroke_trafo in objs_styles:
			obj.style = style
			obj.fill_trafo = fill_trafo
			obj.stroke_trafo = stroke_trafo
			if obj.cid == model.PIXMAP:
				obj.cache_cdata = None

	def _fill_objs(self, objs, color):
		for obj in objs:
			style = deepcopy(obj.style)
			if obj.cid == model.PIXMAP:
				if color:
					style[3][0] = deepcopy(color)
				else:
					style[3][0] = []
				obj.cache_cdata = None
			else:
				if color:
					fill = style[0]
					new_fill = []
					if not fill:
						new_fill.append(self.sk2_cfg.default_fill_rule)
					else:
						new_fill.append(fill[0])
					new_fill.append(sk2_const.FILL_SOLID)
					new_fill.append(deepcopy(color))
					style[0] = new_fill
				else:
					style[0] = []
			obj.style = style
			obj.fill_trafo = []

	def _set_objs_fill_style(self, objs, fill_style):
		for obj in objs:
			if not obj.cid == model.PIXMAP:
				style = deepcopy(obj.style)
				style[0] = deepcopy(fill_style)
				obj.style = style

	def _set_paths_and_trafo(self, obj, paths, trafo):
		obj.paths = paths
		obj.trafo = trafo
		obj.update()

	def _set_paths(self, obj, paths):
		obj.paths = paths
		obj.update()

	def _apply_trafo(self, objs, trafo):
		before = []
		after = []
		for obj in objs:
			before.append(obj.get_trafo_snapshot())
			obj.apply_trafo(trafo)
			after.append(obj.get_trafo_snapshot())
		self.selection.update_bbox()
		return (before, after)

	def _set_bitmap_trafo(self, obj, trafo):
		obj.trafo = trafo
		obj.update()

	def _clear_trafo(self, objs):
		normal_trafo = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
		before = []
		after = []
		for obj in objs:
			before.append(obj.get_trafo_snapshot())
			if obj.cid in (model.CIRCLE, model.POLYGON):
				obj.trafo = [] + obj.initial_trafo
			else:
				obj.trafo = [] + normal_trafo
			obj.update()
			after.append(obj.get_trafo_snapshot())
		self.selection.update_bbox()
		return (before, after)

	def _set_snapshots(self, snapshots):
		for snapshot in snapshots:
			obj = snapshot[0]
			obj.set_trafo_snapshot(snapshot)
		self.selection.update_bbox()

	def _stroke_objs(self, objs, color):
		for obj in objs:
			style = deepcopy(obj.style)
			if obj.cid == model.PIXMAP:
				if color:
					style[3][1] = deepcopy(color)
				else:
					style[3][1] = []
				obj.cache_cdata = None
			else:
				if color:
					stroke = style[1]
					if not stroke:
						new_stroke = deepcopy(self.sk2_cfg.default_stroke)
					else:
						new_stroke = deepcopy(stroke)
					new_stroke[2] = deepcopy(color)
					style[1] = new_stroke
				else:
					style[1] = []
					obj.stroke_trafo = []
			obj.style = style

	def _set_objs_stroke_style(self, objs, stroke_style):
		for obj in objs:
			if not obj.cid == model.PIXMAP:
				style = deepcopy(obj.style)
				style[1] = deepcopy(stroke_style)
				obj.style = style

	def _set_parent(self, objs, parent):
		for obj in objs:
			obj.parent = parent

	def _restore_parents(self, parent_list):
		for obj, parent in parent_list:
			obj.parent = parent

	def _set_bitmap(self, obj, bmpstr, colorspace=None):
		obj.bitmap = bmpstr
		obj.cache_cdata = None
		obj.cache_gray_cdata = None
		if colorspace:
			obj.colorspace = colorspace

	def _set_alpha(self, obj, alphastr):
		obj.alpha_channel = alphastr
		obj.cache_cdata = None
		obj.cache_gray_cdata = None


class PresenterAPI(AbstractAPI):

	def __init__(self, presenter):
		self.presenter = presenter
		self.selection = presenter.selection
		self.methods = self.presenter.methods
		self.model = presenter.model
		self.sk2_cfg = presenter.doc_presenter.config
		self.view = presenter.canvas

		self.eventloop = presenter.eventloop
		self.app = presenter.app
		self.undo = []
		self.redo = []

	def destroy(self):
		self.undo = self._clear_history_stack(self.undo)
		self.redo = self._clear_history_stack(self.redo)

		items = self.__dict__.keys()
		for item in items:
			self.__dict__[item] = None

	def clear_history(self):
		self.undo = self._clear_history_stack(self.undo)
		self.redo = self._clear_history_stack(self.redo)
		events.emit(events.DOC_MODIFIED, self.presenter)
		self.presenter.reflect_saving()

	def set_page_format(self, page_format):
		page = self.presenter.active_page
		format_before = page.page_format
		format_after = page_format
		self._set_page_format(page, format_after)
		transaction = [
			[[self._set_page_format, page, format_before]],
			[[self._set_page_format, page, format_after]],
			False]
		self.add_undo(transaction)

	def set_doc_origin(self, origin):
		cur_origin = self.model.doc_origin
		transaction = [
			[[self.methods.set_doc_origin, cur_origin]],
			[[self.methods.set_doc_origin, origin]],
			False]
		self.methods.set_doc_origin(origin)
		self.add_undo(transaction)

	def set_doc_units(self, units):
		cur_units = self.model.doc_units
		transaction = [
			[[self.methods.set_doc_units, cur_units]],
			[[self.methods.set_doc_units, units]],
			False]
		self.methods.set_doc_units(units)
		self.add_undo(transaction)

	def insert_object(self, obj, parent, index):
		sel_before = [] + self.selection.objs
		self._insert_object(obj, parent, index)
		self.selection.set([obj])
		sel_after = [] + self.selection.objs
		transaction = [
			[[self._delete_object, obj],
			[self._set_selection, sel_before]],
			[[self._insert_object, obj, parent, index],
			[self._set_selection, sel_after]],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def delete_object(self, obj, parent, index):
		sel_before = [] + self.selection.objs
		self._delete_object(obj)
		sel_after = []
		transaction = [
			[[self._insert_object, obj, parent, index],
			[self._set_selection, sel_before]],
			[[self._delete_object, obj],
			[self._set_selection, sel_after]],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def insert_objects(self, objs_list):
		sel_before = [] + self.selection.objs
		self._insert_objects(objs_list)
		sel_after = [] + objs_list
		transaction = [
			[[self._delete_objects, objs_list],
			[self._set_selection, sel_before]],
			[[self._insert_objects, objs_list],
			[self._set_selection, sel_after]],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def delete_objects(self, objs_list):
		sel_before = [] + self.selection.objs
		self._delete_objects(objs_list)
		sel_after = []
		transaction = [
			[[self._insert_objects, objs_list],
			[self._set_selection, sel_before]],
			[[self._delete_objects, objs_list],
			[self._set_selection, sel_after]],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def delete_selected(self):
		if self.selection.objs:
			before = self._get_layers_snapshot()
			sel_before = [] + self.selection.objs
			for obj in self.selection.objs:
				self.methods.delete_object(obj)
			after = self._get_layers_snapshot()
			sel_after = []
			transaction = [
				[[self._set_layers_snapshot, before],
				[self._set_selection, sel_before]],
				[[self._set_layers_snapshot, after],
				[self._set_selection, sel_after]],
				False]
			self.add_undo(transaction)
		self.selection.clear()

	def cut_selected(self):
		self.copy_selected()
		self.delete_selected()

	def copy_selected(self):
		if self.selection.objs:
			self.app.clipboard.set(self.selection.objs)

	def paste_selected(self, objs=None):
		if objs is None: objs = self.app.clipboard.get()
		sel_before = [] + self.selection.objs
		before = self._get_layers_snapshot()
		self.methods.append_objects(objs, self.presenter.active_layer)
		after = self._get_layers_snapshot()
		sel_after = [] + objs
		transaction = [
			[[self._set_layers_snapshot, before],
			[self._set_selection, sel_before]],
			[[self._set_layers_snapshot, after],
			[self._set_selection, sel_after]],
			False]
		self.add_undo(transaction)
		for obj in objs:
			obj.do_update()
		self.selection.set(objs)
		self.selection.update()

	#---------------- CREATORS -------------------
	def create_rectangle(self, rect):
		rect = self._normalize_rect(rect)
		parent = self.presenter.active_layer
		obj = model.Rectangle(self.sk2_cfg, parent, rect)
		obj.style = deepcopy(self.model.styles['Default Style'])
		obj.update()
		self.insert_object(obj, parent, len(parent.childs))

	def create_ellipse(self, rect):
		rect = self._normalize_rect(rect)
		parent = self.presenter.active_layer
		obj = model.Circle(self.sk2_cfg, parent, rect)
		obj.style = deepcopy(self.model.styles['Default Style'])
		obj.update()
		self.insert_object(obj, parent, len(parent.childs))

	def create_polygon(self, rect):
		rect = self._normalize_rect(rect)
		parent = self.presenter.active_layer
		obj = model.Polygon(self.sk2_cfg, parent, rect,
						corners_num=config.default_polygon_num)
		obj.style = deepcopy(self.model.styles['Default Style'])
		obj.update()
		self.insert_object(obj, parent, len(parent.childs))

	def create_text(self, rect, width=0):pass
#		rect = self._normalize_rect(rect)
#		parent = self.presenter.active_layer
#		if width == 0: width = rect[2]
#		text = dialogs.text_edit_dialog(self.app.mw)
#		if text:
#			obj = model.Text(self.sk2_cfg, parent, rect, text, width)
#			obj.style = deepcopy(self.model.styles['Default Style'])
#			obj.update()
#			self.insert_object(obj, parent, len(parent.childs))

	def create_curve(self, paths):
		parent = self.presenter.active_layer
		obj = model.Curve(self.sk2_cfg, parent, paths)
		obj.style = deepcopy(self.model.styles['Default Style'])
		obj.update()
		self.insert_object(obj, parent, len(parent.childs))

	def update_curve(self, obj, paths, trafo=[1.0, 0.0, 0.0, 1.0, 0.0, 0.0]):
		sel_before = [obj, ]
		sel_after = [obj, ]
		trafo_before = obj.trafo
		paths_before = obj.paths
		trafo_after = trafo
		paths_after = paths
		self._set_paths_and_trafo(obj, paths_after, trafo_after)
		transaction = [
			[[self._set_paths_and_trafo, obj, paths_before, trafo_before],
			[self._set_selection, sel_before]],
			[[self._set_paths_and_trafo, obj, paths_after, trafo_after],
			[self._set_selection, sel_after]],
			False]
		self._set_selection(sel_after)
		self.add_undo(transaction)

	def create_guides(self, vals=[]):
		if vals:
			objs_list = []
			parent = self.methods.get_guide_layer()
			for val in vals:
				pos, orient = val
				obj = model.Guide(self.sk2_cfg, parent, pos, orient)
				objs_list.append([obj, parent, -1])
				obj.update()
			self._insert_objects(objs_list)
			transaction = [
				[[self._delete_objects, objs_list]],
				[[self._insert_objects, objs_list]],
				False]
			self.add_undo(transaction)
			self.selection.update()

#///////////////////////////////////////////

	#FIXME: Add undo for operation!
	def edit_text(self):pass
#		if self.selection.objs:
#			obj = self.selection.objs[0]
#			obj.text = dialogs.text_edit_dialog(self.app.mw, obj.text)
#			obj.update()

	def set_default_style(self, style):
		style_before = self.model.styles['Default Style']
		self._set_default_style(style)
		transaction = [
			[[self._set_default_style, style_before]],
			[[self._set_default_style, style]],
			False]
		self.add_undo(transaction)

	def _get_primitive_objs(self, objs, exclude_pixmap=False):
		ret = []
		for obj in objs:
			if obj.cid > model.PRIMITIVE_CLASS:
				if exclude_pixmap and obj.cid == model.PIXMAP: continue
				ret.append(obj)
			else:
				ret += self._get_primitive_objs(obj.childs, exclude_pixmap)
		return ret

	def fill_selected(self, color, objs=[]):
		if objs:
			color = deepcopy(color)
			objs = self._get_primitive_objs(objs)
			initial_styles = self._get_objs_styles(objs)
			self._fill_objs(objs, color)
			transaction = [
				[[self._set_objs_styles, initial_styles], ],
				[[self._fill_objs, objs, color], ],
				False]
			self.add_undo(transaction)
			self.selection.update()
		elif self.selection.objs:
			color = deepcopy(color)
			sel_before = [] + self.selection.objs
			objs = self._get_primitive_objs(self.selection.objs)
			initial_styles = self._get_objs_styles(objs)
			self._fill_objs(objs, color)
			sel_after = [] + self.selection.objs
			transaction = [
				[[self._set_objs_styles, initial_styles],
				[self._set_selection, sel_before]],
				[[self._fill_objs, objs, color],
				[self._set_selection, sel_after]],
				False]
			self.add_undo(transaction)
			self.selection.update()

	def set_temp_style(self, obj, style):
		obj.style = style
		self.eventloop.emit(self.eventloop.DOC_MODIFIED)
		self.selection.update()

	def set_fill_style(self, fill_style, objs=[]):
		if objs:
			objs = self._get_primitive_objs(objs, True)
			initial_styles = self._get_objs_styles(objs)
			self._set_objs_fill_style(objs, fill_style)
			after_styles = self._get_objs_styles(objs)
			transaction = [
				[[self._set_objs_styles, initial_styles], ],
				[[self._set_objs_styles, after_styles], ],
				False]
			self.add_undo(transaction)
			self.selection.update()
		elif self.selection.objs:
			sel_before = [] + self.selection.objs
			objs = self._get_primitive_objs(self.selection.objs, True)
			initial_styles = self._get_objs_styles(objs)
			self._set_objs_fill_style(objs, fill_style)
			after_styles = self._get_objs_styles(objs)
			sel_after = [] + self.selection.objs
			transaction = [
				[[self._set_objs_styles, initial_styles],
				[self._set_selection, sel_before]],
				[[self._set_objs_styles, after_styles],
				[self._set_selection, sel_after]],
				False]
			self.add_undo(transaction)
			self.selection.update()

	def stroke_selected(self, color, objs=[]):
		if objs:
			color = deepcopy(color)
			objs = self._get_primitive_objs(objs)
			initial_styles = self._get_objs_styles(objs)
			self._stroke_objs(objs, color)
			transaction = [
				[[self._set_objs_styles, initial_styles], ],
				[[self._stroke_objs, objs, color], ],
				False]
			self.add_undo(transaction)
			self.selection.update()
		elif self.selection.objs:
			color = deepcopy(color)
			sel_before = [] + self.selection.objs
			objs = self._get_primitive_objs(self.selection.objs)
			initial_styles = self._get_objs_styles(objs)
			self._stroke_objs(objs, color)
			sel_after = [] + self.selection.objs
			transaction = [
				[[self._set_objs_styles, initial_styles],
				[self._set_selection, sel_before]],
				[[self._stroke_objs, objs, color],
				[self._set_selection, sel_after]],
				False]
			self.add_undo(transaction)
			self.selection.update()

	def set_stroke_style(self, stroke_style, objs=[]):
		if objs:
			objs = self._get_primitive_objs(objs, True)
			initial_styles = self._get_objs_styles(objs)
			self._set_objs_stroke_style(objs, stroke_style)
			after_styles = self._get_objs_styles(objs)
			transaction = [
				[[self._set_objs_styles, initial_styles], ],
				[[self._set_objs_styles, after_styles], ],
				False]
			self.add_undo(transaction)
			self.selection.update()
		elif self.selection.objs:
			sel_before = [] + self.selection.objs
			objs = self._get_primitive_objs(self.selection.objs, True)
			initial_styles = self._get_objs_styles(objs)
			self._set_objs_stroke_style(objs, stroke_style)
			after_styles = self._get_objs_styles(objs)
			sel_after = [] + self.selection.objs
			transaction = [
				[[self._set_objs_styles, initial_styles],
				[self._set_selection, sel_before]],
				[[self._set_objs_styles, after_styles],
				[self._set_selection, sel_after]],
				False]
			self.add_undo(transaction)
			self.selection.update()

	def set_mode(self, mode=modes.SELECT_MODE):
		transaction = [
			[[self._set_mode, mode],
			[self._selection_update, ]],
			[[self._set_mode, mode],
			[self._selection_update, ]],
			False]
		self.add_undo(transaction)

	def set_temp_paths(self, obj, paths):
		self._set_paths(obj, paths)
		self.eventloop.emit(self.eventloop.DOC_MODIFIED)
		self.selection.update()

	def set_new_paths(self, obj, new_paths, old_paths):
		self._set_paths(obj, new_paths)
		transaction = [
			[[self._set_paths, obj, old_paths],
			[self._selection_update, ]],
			[[self._set_paths, obj, new_paths],
			[self._selection_update, ]],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def transform_selected(self, trafo, copy=False):
		if self.selection.objs:
			sel_before = [] + self.selection.objs
			objs = [] + self.selection.objs
			if copy:
				copied_objs = []
				for obj in objs:
					copied_obj = obj.copy()
					copied_obj.update()
					copied_objs.append(copied_obj)
				self._apply_trafo(copied_objs, trafo)
				before = self._get_layers_snapshot()
				self.methods.append_objects(copied_objs,
										self.presenter.active_layer)
				after = self._get_layers_snapshot()
				sel_after = [] + copied_objs
				transaction = [
					[[self._set_layers_snapshot, before],
					[self._set_selection, sel_before]],
					[[self._set_layers_snapshot, after],
					[self._set_selection, sel_after]],
					False]
				self.add_undo(transaction)
				self.selection.set(copied_objs)
			else:
				before, after = self._apply_trafo(objs, trafo)
				sel_after = [] + objs
				transaction = [
					[[self._set_snapshots, before],
					[self._set_selection, sel_before]],
					[[self._set_snapshots, after],
					[self._set_selection, sel_after]],
					False]
				self.add_undo(transaction)
			self.selection.update()

	def move_selected(self, x, y, copy=False):
		trafo = [1.0, 0.0, 0.0, 1.0, x, y]
		self.transform_selected(trafo, copy)

	def duplicate_selected(self):
		trafo = [1.0, 0.0, 0.0, 1.0, config.obj_jump, config.obj_jump]
		self.transform_selected(trafo, True)

	def clear_trafo(self):
		normal_trafo = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
		if self.selection.objs:
			sel_before = [] + self.selection.objs
			objs = [] + self.selection.objs
			cleared_objs = []
			for obj in objs:
				if obj.cid > model.PRIMITIVE_CLASS:
					if not obj.trafo == normal_trafo:
						cleared_objs.append(obj)
			if cleared_objs:
				before, after = self._clear_trafo(cleared_objs)
				transaction = [
					[[self._set_snapshots, before],
					[self._set_selection, sel_before]],
					[[self._set_snapshots, after],
					[self._set_selection, sel_before]],
					False]
				self.add_undo(transaction)
				self.selection.update()

	def rotate_selected(self, angle=0, copy=False):
		if self.selection.objs:
			bbox = self.selection.bbox
			w = bbox[2] - bbox[0]
			h = bbox[3] - bbox[1]

			x0, y0 = bbox[:2]
			shift_x, shift_y = self.selection.center_offset
			center_x = x0 + w / 2.0 + shift_x
			center_y = y0 + h / 2.0 + shift_y

			m21 = math.sin(angle)
			m11 = m22 = math.cos(angle)
			m12 = -m21
			dx = center_x - m11 * center_x + m21 * center_y;
			dy = center_y - m21 * center_x - m11 * center_y;

			trafo = [m11, m21, m12, m22, dx, dy]
			self.transform_selected(trafo, copy)

	def mirror_selected(self, vertical=True, copy=False):
		if self.selection.objs:
			m11 = m22 = 1.0
			dx = dy = 0.0
			bbox = self.selection.bbox
			w = bbox[2] - bbox[0]
			h = bbox[3] - bbox[1]
			x0, y0 = bbox[:2]
			if vertical:
				m22 = -1
				dy = 2 * y0 + h
			else:
				m11 = -1
				dx = 2 * x0 + w

			trafo = [m11, 0.0, 0.0, m22, dx, dy]
			self.transform_selected(trafo, copy)

	def convert_to_curve_selected(self):
		if self.selection.objs:
			before = self._get_layers_snapshot()
			objs = [] + self.selection.objs
			sel_before = [] + self.selection.objs

			for obj in objs:
				if obj.cid > model.PRIMITIVE_CLASS and not obj.cid == model.CURVE:
					curve = obj.to_curve()
					if curve is not None:
						parent = obj.parent
						index = parent.childs.index(obj)
						curve.parent = parent
						parent.childs[index] = curve
						sel_id = self.selection.objs.index(obj)
						self.selection.objs[sel_id] = curve

			after = self._get_layers_snapshot()
			sel_after = [] + self.selection.objs
			transaction = [
				[[self._set_layers_snapshot, before],
				[self._set_selection, sel_before]],
				[[self._set_layers_snapshot, after],
				[self._set_selection, sel_after]],
				False]
			self.add_undo(transaction)
			self.selection.update()

	def group_selected(self):
		if self.selection.objs:
			before = self._get_layers_snapshot()
			objs = [] + self.selection.objs
			sel_before = [] + self.selection.objs

			parent = objs[-1].parent
			group = model.Group(objs[-1].config, parent, objs)
			group.update()
			for obj in objs:
				obj.parent.childs.remove(obj)
			parent.childs.append(group)
			parent_list = []
			for obj in objs:
				parent_list.append([obj, obj.parent])
				obj.parent = group

			after = self._get_layers_snapshot()
			sel_after = [group]
			self.selection.set([group])
			transaction = [
				[[self._set_layers_snapshot, before],
				[self._restore_parents, parent_list],
				[self._set_selection, sel_before]],
				[[self._set_layers_snapshot, after],
				[self._set_parent, sel_after, group],
				[self._set_selection, sel_after]],
				False]
			self.add_undo(transaction)
			self.selection.update()

	def ungroup_selected(self):
		if self.selection.objs:
			group = self.selection.objs[0]
			before = self._get_layers_snapshot()
			objs = [] + group.childs
			sel_before = [] + self.selection.objs
			parent = group.parent
			index = parent.childs.index(group)

			child_list = parent.childs[:index] + objs
			child_list += parent.childs[index + 1:]
			parent.childs = child_list

			parent_list = []
			for obj in objs:
				obj.parent = parent
				parent_list.append([obj, group])

			after = self._get_layers_snapshot()
			sel_after = objs
			self.selection.set(sel_after)
			transaction = [
				[[self._set_layers_snapshot, before],
				[self._set_parent, sel_after, group],
				[self._set_selection, sel_before]],
				[[self._set_layers_snapshot, after],
				[self._restore_parents, parent_list],
				[self._set_selection, sel_after]],
				False]
			self.add_undo(transaction)
			self.selection.update()

	def _ungroup_tree(self, group, objs_list, parent_list):
		for obj in group.childs:
			if not obj.cid == model.GROUP:
				objs_list += [obj]
				parent_list += [[obj, obj.parent]]
			else:
				self._ungroup_tree(obj, objs_list, parent_list)

	def ungroup_all(self):
		if self.selection.objs:
			parent_list_before = []
			parent_list_after = []
			sel_after = []

			sel_before = [] + self.selection.objs
			before = self._get_layers_snapshot()

			for obj in self.selection.objs:
				if obj.cid == model.GROUP:
					objs_list = []
					self._ungroup_tree(obj, objs_list, parent_list_before)
					index = obj.parent.childs.index(obj)
					parent = obj.parent

					child_list = parent.childs[:index] + objs_list
					child_list += parent.childs[index + 1:]
					parent.childs = child_list

					for item in objs_list:
						item.parent = parent
						sel_after.append(item)
				else:
					sel_after.append(obj)

			after = self._get_layers_snapshot()
			self.selection.set(sel_after)
			transaction = [
				[[self._set_layers_snapshot, before],
				[self._restore_parents, parent_list_before],
				[self._set_selection, sel_before]],
				[[self._set_layers_snapshot, after],
				[self._restore_parents, parent_list_after],
				[self._set_selection, sel_after]],
				False]
			self.add_undo(transaction)
			self.selection.update()

	def pack_container(self, container):
		if self.selection.objs:
			before = self._get_layers_snapshot()
			objs = [] + [container] + self.selection.objs
			sel_before = [] + self.selection.objs

			parent = container.parent
			group = model.Container(container.config, parent, objs)
			group.update()
			for obj in objs:
				obj.parent.childs.remove(obj)
			parent.childs.append(group)
			parent_list = []
			for obj in objs:
				parent_list.append([obj, obj.parent])
				obj.parent = group

			after = self._get_layers_snapshot()
			sel_after = [group]
			self.selection.set([group])
			transaction = [
				[[self._set_layers_snapshot, before],
				[self._restore_parents, parent_list],
				[self._set_selection, sel_before]],
				[[self._set_layers_snapshot, after],
				[self._set_parent, sel_after, group],
				[self._set_selection, sel_after]],
				False]
			self.add_undo(transaction)
			self.selection.update()

	def unpack_container(self):
		group = self.selection.objs[0]
		before = self._get_layers_snapshot()
		objs = [] + group.childs
		sel_before = [] + self.selection.objs
		parent = group.parent
		index = parent.childs.index(group)

		objs.reverse()
		parent.childs.remove(group)
		parent_list = []

		for obj in objs:
			parent.childs.insert(index, obj)
			obj.parent = parent
			parent_list.append([obj, group])

		after = self._get_layers_snapshot()
		sel_after = objs
		self.selection.set(sel_after)
		transaction = [
			[[self._set_layers_snapshot, before],
			[self._set_parent, sel_after, group],
			[self._set_selection, sel_before]],
			[[self._set_layers_snapshot, after],
			[self._restore_parents, parent_list],
			[self._set_selection, sel_after]],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def combine_selected(self):
		before = self._get_layers_snapshot()
		sel_before = [] + self.selection.objs
		objs = self.selection.objs
		parent = objs[0].parent
		index = parent.childs.index(objs[0])

		style = deepcopy(objs[0].style)
		parent = objs[0].parent
		config = objs[0].config
		paths = []
		for obj in objs:
			for item in libgeom.get_transformed_path(obj):
				if item[1]:paths.append(item)
		result = model.Curve(config, parent)
		result.paths = paths
		result.style = style
		result.update()

		for obj in objs:
			obj.parent.childs.remove(obj)

		parent.childs.insert(index, result)
		after = self._get_layers_snapshot()
		self.selection.set([result, ])
		transaction = [
			[[self._set_layers_snapshot, before],
			[self._set_selection, sel_before]],
			[[self._set_layers_snapshot, after],
			[self._set_selection, [result, ]]],
			False]
		self.add_undo(transaction)
		self.selection.update()


	def break_apart_selected(self):
		before = self._get_layers_snapshot()
		sel_before = [] + self.selection.objs
		obj = self.selection.objs[0]

		parent = obj.parent
		index = parent.childs.index(obj)
		config = obj.config

		paths = libgeom.get_transformed_path(obj)

		objs = []

		obj.parent.childs.remove(obj)
		for path in paths:
			if path and path[1]:
				curve = model.Curve(config, parent)
				curve.paths = [path, ]
				curve.style = deepcopy(obj.style)
				if obj.fill_trafo: curve.fill_trafo = [] + obj.fill_trafo
				if obj.stroke_trafo: curve.stroke_trafo = [] + obj.stroke_trafo
				objs += [curve, ]
				parent.childs.insert(index, curve)
				curve.update()

		after = self._get_layers_snapshot()
		self.selection.set(objs)
		transaction = [
			[[self._set_layers_snapshot, before],
			[self._set_selection, sel_before]],
			[[self._set_layers_snapshot, after],
			[self._set_selection, objs]],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def extract_subpaths(self, target, indexes):
		before = self._get_layers_snapshot()

		parent = target.parent
		parent_index = parent.childs.index(target)
		config = target.config

		paths = libgeom.get_transformed_path(target)

		p0 = []
		p1 = []

		target.parent.childs.remove(target)

		for index in range(len(paths)):
			if index in indexes:
				p1.append(paths[index])
			else:
				p0.append(paths[index])

		curve0 = curve1 = None

		if p1:
			curve1 = model.Curve(config, parent)
			curve1.paths = p1
			curve1.style = deepcopy(target.style)
			if target.fill_trafo: curve1.fill_trafo = [] + target.fill_trafo
			if target.stroke_trafo: curve1.stroke_trafo = [] + target.stroke_trafo
			parent.childs.insert(parent_index, curve1)
			curve1.update()
		if p0:
			curve0 = model.Curve(config, parent)
			curve0.paths = p0
			curve0.style = deepcopy(target.style)
			if target.fill_trafo: curve0.fill_trafo = [] + target.fill_trafo
			if target.stroke_trafo: curve0.stroke_trafo = [] + target.stroke_trafo
			parent.childs.insert(parent_index, curve0)
			curve0.update()

		after = self._get_layers_snapshot()
		transaction = [
			[[self._set_layers_snapshot, before],
			[self._set_selection, []]],
			[[self._set_layers_snapshot, after],
			[self._set_selection, []]],
			False]
		self.add_undo(transaction)
		self.selection.update()
		return curve0, curve1

	def set_active_page(self, index):
		if not self.undo:
			self.presenter.set_active_page(index)
			self.selection.clear()
		else:
			pages = self.presenter.get_pages()
			active_index_before = pages.index(self.presenter.active_page)
			sel_before = [] + self.selection.objs
			active_index_after = index

			self.presenter.set_active_page(index)
			self.selection.clear()

			transaction = [
				[[self._set_selection, sel_before],
				[self.presenter.set_active_page, active_index_before]],
				[[self._set_selection, []],
				[self.presenter.set_active_page, active_index_after]],
				False]
			self.add_undo(transaction)
			self.selection.update()

	def delete_page(self, index):
		pages = self.presenter.get_pages()
		if index == 0 and len(pages) == 1: return

		before = self._get_pages_snapshot()
		sel_before = [] + self.selection.objs
		active_index_before = pages.index(self.presenter.active_page)

		self.methods.delete_page(index)

		active_index_after = 0

		if index == active_index_before:
			if index:
				active_index_after = index - 1
		else:
			pages = self.presenter.get_pages()
			active_index_after = pages.index(self.presenter.active_page)

		self.selection.clear()
		self.presenter.set_active_page(active_index_after)

		after = self._get_pages_snapshot()

		transaction = [
			[[self._set_pages_snapshot, before],
			[self._set_selection, sel_before],
			[self.presenter.set_active_page, active_index_before]],
			[[self._set_pages_snapshot, after],
			[self._set_selection, []],
			[self.presenter.set_active_page, active_index_after]],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def insert_page(self, number, target, position):
		pages = self.presenter.get_pages()

		before = self._get_pages_snapshot()
		sel_before = [] + self.selection.objs
		active_index_before = pages.index(self.presenter.active_page)

		active_index_after = target
		if position == uc2const.AFTER: active_index_after += 1

		for item in range(number):
			page = self.methods.insert_page(active_index_after + item)
			self.methods.add_layer(page)
			page.do_update()

		self.selection.clear()
		self.presenter.set_active_page(active_index_after)

		after = self._get_pages_snapshot()

		transaction = [
			[[self._set_pages_snapshot, before],
			[self._set_selection, sel_before],
			[self.presenter.set_active_page, active_index_before]],
			[[self._set_pages_snapshot, after],
			[self._set_selection, []],
			[self.presenter.set_active_page, active_index_after]],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def add_pages(self, new_pages):
		pages = self.presenter.get_pages()
		parent = pages[0].parent

		before = self._get_pages_snapshot()
		sel_before = [] + self.selection.objs
		active_index_before = pages.index(self.presenter.active_page)

		active_index_after = len(pages)

		pages += new_pages
		parent.do_update()

		self.selection.clear()
		self.presenter.set_active_page(active_index_after)

		after = self._get_pages_snapshot()

		transaction = [
			[[self._set_pages_snapshot, before],
			[self._set_selection, sel_before],
			[self.presenter.set_active_page, active_index_before]],
			[[self._set_pages_snapshot, after],
			[self._set_selection, []],
			[self.presenter.set_active_page, active_index_after]],
			False]
		self.add_undo(transaction)
		self.selection.update()


	def set_layer_properties(self, layer, prop):
		before = layer.properties
		after = prop
		sel_before = [] + self.selection.objs

		self.selection.clear()
		self._set_layer_properties(layer, prop)

		transaction = [
			[[self._set_layer_properties, layer, before],
			[self._set_selection, sel_before], ],
			[[self._set_layer_properties, layer, after],
			[self._set_selection, []]],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def set_guide_propeties(self, guide, pos, orient):
		pos_before = guide.position
		orient_before = guide.orientation
		self._set_guide_properties(guide, pos, orient)
		pos_after = pos
		orient_after = orient
		transaction = [
			[[self._set_guide_properties, guide, pos_before, orient_before], ],
			[[self._set_guide_properties, guide, pos_after, orient_after], ],
			False]
		self.add_undo(transaction)

	def delete_guides(self, objs=[]):
		if objs:
			objs_list = []
			parent = self.methods.get_guide_layer()
			for obj in objs:
				objs_list.append([obj, parent, -1])
			self._delete_objects(objs_list)
			transaction = [
				[[self._insert_objects, objs_list]],
				[[self._delete_objects, objs_list]],
				False]
			self.add_undo(transaction)

	def delete_all_guides(self):
		guides = []
		guide_layer = self.methods.get_guide_layer()
		for child in guide_layer.childs:
			if child.cid == model.GUIDE:
				guides.append(child)
		self.delete_guides(guides)

	def set_rect(self, rect, obj):
		self.methods.set_rect(obj, rect)
		self.eventloop.emit(self.eventloop.DOC_MODIFIED)
		self.selection.update()

	def set_rect_final(self, rect, rect_before, obj):
		if not rect_before:
			rect_before = obj.get_rect()
		self.methods.set_rect(obj, rect)
		transaction = [
			[[self.methods.set_rect, obj, rect_before], ],
			[[self.methods.set_rect, obj, rect], ],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def set_rect_corners(self, corners, obj=None):
		if obj is None:
			sel = [] + self.selection.objs
			obj = sel[0]
		self.methods.set_rect_corners(obj, corners)
		self.eventloop.emit(self.eventloop.DOC_MODIFIED)
		self.selection.update()

	def set_rect_corners_final(self, corners, corners_before=[], obj=None):
		if obj is None:
			sel = [] + self.selection.objs
			obj = sel[0]
			if not corners_before:
				corners_before = obj.corners
			self.methods.set_rect_corners(obj, corners)
			transaction = [
				[[self.methods.set_rect_corners, obj, corners_before],
				[self._set_selection, sel], ],
				[[self.methods.set_rect_corners, obj, corners],
				[self._set_selection, sel]],
				False]
		else:
			if not corners_before:
				corners_before = obj.corners
			self.methods.set_rect_corners(obj, corners)
			transaction = [
				[[self.methods.set_rect_corners, obj, corners_before], ],
				[[self.methods.set_rect_corners, obj, corners], ],
				False]
		self.add_undo(transaction)
		self.selection.update()

	def set_polygon_corners_num(self, num):
		sel = [] + self.selection.objs
		obj = sel[0]
		num_before = obj.corners_num
		self.methods.set_polygon_corners_num(obj, num)
		transaction = [
			[[self.methods.set_polygon_corners_num, obj, num_before],
			[self._set_selection, sel], ],
			[[self.methods.set_polygon_corners_num, obj, num],
			[self._set_selection, sel]],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def set_circle_properties(self, circle_type, angle1, angle2):
		sel = [] + self.selection.objs
		obj = sel[0]
		type_before = obj.circle_type
		angle1_before = obj.angle1
		angle2_before = obj.angle2
		mtds = self.methods
		mtds.set_circle_properties(obj, circle_type, angle1, angle2)
		transaction = [
			[[mtds.set_circle_properties, obj, type_before,
											angle1_before, angle2_before],
			[self._set_selection, sel], ],
			[[mtds.set_circle_properties, obj, circle_type, angle1, angle2],
			[self._set_selection, sel]],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def raise_to_top(self):
		before = self._get_layers_snapshot()
		sel_before = [] + self.selection.objs
		obj = sel_before[0]
		childs = obj.parent.childs
		index = childs.index(obj)
		new_childs = childs[:index] + childs[index + 1:] + [obj, ]
		obj.parent.childs = new_childs
		after = self._get_layers_snapshot()
		transaction = [
			[[self._set_layers_snapshot, before],
			[self._set_selection, sel_before]],
			[[self._set_layers_snapshot, after],
			[self._set_selection, sel_before]],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def raise_obj(self):
		before = self._get_layers_snapshot()
		sel_before = [] + self.selection.objs
		obj = sel_before[0]
		childs = obj.parent.childs
		index = childs.index(obj)

		new_childs = childs[:index] + [childs[index + 1], obj]
		new_childs += childs[index + 2:]

		obj.parent.childs = new_childs
		after = self._get_layers_snapshot()
		transaction = [
			[[self._set_layers_snapshot, before],
			[self._set_selection, sel_before]],
			[[self._set_layers_snapshot, after],
			[self._set_selection, sel_before]],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def lower_obj(self):
		before = self._get_layers_snapshot()
		sel_before = [] + self.selection.objs
		obj = sel_before[0]
		childs = obj.parent.childs
		index = childs.index(obj)

		new_childs = childs[:index - 1] + [obj, childs[index - 1]]
		new_childs += childs[index + 1:]

		obj.parent.childs = new_childs
		after = self._get_layers_snapshot()
		transaction = [
			[[self._set_layers_snapshot, before],
			[self._set_selection, sel_before]],
			[[self._set_layers_snapshot, after],
			[self._set_selection, sel_before]],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def lower_to_bottom(self):
		before = self._get_layers_snapshot()
		sel_before = [] + self.selection.objs
		obj = sel_before[0]
		childs = obj.parent.childs
		index = childs.index(obj)
		new_childs = [obj, ] + childs[:index] + childs[index + 1:]
		obj.parent.childs = new_childs
		after = self._get_layers_snapshot()
		transaction = [
			[[self._set_layers_snapshot, before],
			[self._set_selection, sel_before]],
			[[self._set_layers_snapshot, after],
			[self._set_selection, sel_before]],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def convert_bitmap(self, colorspace):
		cms = self.presenter.cms
		sel_before = [] + self.selection.objs
		obj = sel_before[0]
		old_bmpstr = obj.bitmap
		old_colorspace = obj.colorspace
		new_bmpstr = libimg.convert_image(cms, obj, colorspace)
		self._set_bitmap(obj, new_bmpstr, colorspace)
		transaction = [
			[[self._set_bitmap, obj, old_bmpstr, old_colorspace],
			[self._set_selection, sel_before]],
			[[self._set_bitmap, obj, new_bmpstr, colorspace],
			[self._set_selection, sel_before]],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def invert_bitmap(self):
		sel_before = [] + self.selection.objs
		obj = sel_before[0]
		old_bmpstr = obj.bitmap
		new_bmpstr = libimg.invert_image(self.presenter.cms, old_bmpstr)
		self._set_bitmap(obj, new_bmpstr)
		transaction = [
			[[self._set_bitmap, obj, old_bmpstr],
			[self._set_selection, sel_before]],
			[[self._set_bitmap, obj, new_bmpstr],
			[self._set_selection, sel_before]],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def remove_alpha(self):
		sel_before = [] + self.selection.objs
		obj = sel_before[0]
		old_alphastr = obj.alpha_channel
		new_alphastr = ''
		self._set_alpha(obj, new_alphastr)
		transaction = [
			[[self._set_alpha, obj, old_alphastr],
			[self._set_selection, sel_before]],
			[[self._set_alpha, obj, new_alphastr],
			[self._set_selection, sel_before]],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def invert_alpha(self):
		sel_before = [] + self.selection.objs
		obj = sel_before[0]
		old_alphastr = obj.alpha_channel
		new_alphastr = libimg.invert_image(self.presenter.cms, old_alphastr)
		self._set_alpha(obj, new_alphastr)
		transaction = [
			[[self._set_alpha, obj, old_alphastr],
			[self._set_selection, sel_before]],
			[[self._set_alpha, obj, new_alphastr],
			[self._set_selection, sel_before]],
			False]
		self.add_undo(transaction)
		self.selection.update()

	def set_bitmap_dpi(self, h_dpi, v_dpi=None):
		#TODO: finish implementation
		if not v_dpi:v_dpi = h_dpi
		sel_before = [] + self.selection.objs
		obj = sel_before[0]
		trafo_before = obj.trafo
		trafo_after = [] + obj.trafo







