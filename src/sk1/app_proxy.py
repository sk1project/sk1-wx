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

import math
from copy import deepcopy

import wal

from uc2 import uc2const
from uc2.formats.sk2 import sk2_model, sk2_const
from uc2.libgeom import stroke_to_curve, apply_trafo_to_paths

from sk1 import _, dialogs, modes, events, config
from sk1.dialogs import yesno_dialog, error_dialog
from sk1.prefs import get_prefs_dialog

class AppProxy:

	def __init__(self, app):
		self.app = app

	def update(self):
		self.insp = self.app.insp
		self.mw = self.app.mw

	def stub(self, *args):
		dialogs.msg_dialog(self.mw, self.app.appdata.app_name,
				'Sorry, but this feature is not implemented yet!\n' +
				'Be patient and watch project development of regularly updating the source code!')

	def fill_dialog(self, default_style=False):
		doc = self.app.current_doc
		objs = []
		if default_style:
			fill_style = doc.model.styles['Default Style'][0]
			default_style = True
			title = _('Default document fill')
		else:
			fill_style = None
			title = _('Fill')
			if doc.selection.objs:
				style = self._get_style(doc.selection.objs)
				if not style is None:
					fill_style = style[0]
			elif doc.canvas.mode in modes.EDIT_MODES and \
			doc.canvas.controller.target:
				objs.append(doc.canvas.controller.target)
				style = self._get_style(objs)
				if not style is None:
					fill_style = style[0]
		if fill_style is None:
			txt = _('Do you wish to change default fill style for this document?')
			txt += '\n'
			txt += _('This style will be applied to newly created objects.')
			title = self.app.appdata.app_name
			if dialogs.yesno_dialog(self.mw, title, txt):
				fill_style = doc.model.styles['Default Style'][0]
				default_style = True
				title = _('Default document fill')
			else: return
		new_fill_style = dialogs.fill_dlg(self.mw, doc, fill_style, title)
		if not new_fill_style is None:
			if default_style:
				new_style = doc.model.get_def_style()
				new_style[0] = new_fill_style
				doc.api.set_default_style(new_style)
			else:
				doc.api.set_fill_style(new_fill_style, objs)

	def _get_style(self, objs):
		ret = None
		for obj in objs:
			if obj.cid > sk2_model.PRIMITIVE_CLASS:
				if not obj.cid == sk2_model.PIXMAP:
					ret = obj.style
					break
			else:
				ret = self._get_style(obj.childs)
				if not ret is None: break
		return ret

	def stroke_dialog(self, default_style=False):
		doc = self.app.current_doc
		objs = []
		if default_style:
			stroke_style = doc.model.styles['Default Style'][1]
			default_style = True
			title = _('Default document stroke')
		else:
			stroke_style = None
			title = _('Stroke')
			if doc.selection.objs:
				style = self._get_style(doc.selection.objs)
				if not style is None:
					stroke_style = style[1]
			elif doc.canvas.mode in modes.EDIT_MODES and \
			doc.canvas.controller.target:
				objs.append(doc.canvas.controller.target)
				style = self._get_style(objs)
				if not style is None:
					stroke_style = style[1]
		if stroke_style is None:
			txt = _('Do you wish to change default stroke style for this document?')
			txt += '\n'
			txt += _('This style will be applied to newly created objects.')
			title = self.app.appdata.app_name
			if dialogs.yesno_dialog(self.mw, title, txt):
				stroke_style = doc.model.styles['Default Style'][1]
				default_style = True
				title = _('Default document stroke')
			else: return
		new_stroke_style = dialogs.stroke_dlg(self.mw, doc, stroke_style, title)
		if not new_stroke_style is None:
			if default_style:
				new_style = doc.model.get_def_style()
				new_style[1] = new_stroke_style
				doc.api.set_default_style(new_style)
			else:
				doc.api.set_stroke_style(new_stroke_style, objs)

	def copy_fill(self):
		doc = self.app.current_doc
		doc.canvas.set_temp_mode(modes.PICK_MODE, self.select_fill_donor)

	def select_fill_donor(self, objs):
		if len(objs) == 1 and objs[0].cid > sk2_model.PRIMITIVE_CLASS and not \
		objs[0].cid == sk2_model.PIXMAP:
			style = self._get_style(objs)
			if not style is None:
				fill_style = deepcopy(style[0])
				if fill_style and fill_style[1] == sk2_const.FILL_GRADIENT:
					fill_style[2][1] = []
				self.app.current_doc.api.set_fill_style(fill_style)
				return False

		if not len(objs):
			txt = _("There is no selected object.")
		else:
			txt = _("Selected object cannot be source of fill property.")
		txt += '\n' + _('Do you want to try again?')
		return yesno_dialog(self.app.mw, self.app.appdata.app_name, txt)

	def copy_stroke(self):
		doc = self.app.current_doc
		doc.canvas.set_temp_mode(modes.PICK_MODE, self.select_stroke_donor)

	def select_stroke_donor(self, objs):
		if len(objs) == 1 and objs[0].cid > sk2_model.PRIMITIVE_CLASS and not \
		objs[0].cid == sk2_model.PIXMAP:
			style = self._get_style(objs)
			if not style is None:
				stroke_style = deepcopy(style[1])
				self.app.current_doc.api.set_stroke_style(stroke_style)
				return False

		if not len(objs):
			txt = _("There is no selected object.")
		else:
			txt = _("Selected object cannot be source of stroke property.")
		txt += '\n' + _('Do you want to try again?')
		return yesno_dialog(self.app.mw, self.app.appdata.app_name, txt)

	def move_up(self):
		self.app.current_doc.api.move_selected(0.0, config.obj_jump)

	def move_down(self):
		self.app.current_doc.api.move_selected(0.0, -1.0 * config.obj_jump)

	def move_left(self):
		self.app.current_doc.api.move_selected(-1.0 * config.obj_jump, 0.0)

	def move_right(self):
		self.app.current_doc.api.move_selected(config.obj_jump, 0.0)

	def new(self): self.app.new()
	def open(self): self.app.open()
	def clear_log(self): self.app.history.clear_history()
	def view_log(self): dialogs.log_viewer_dlg(self.mw)
	def save(self): self.app.save()
	def save_as(self): self.app.save_as()
	def save_selected(self): self.app.save_selected()
	def save_all(self): self.app.save_all()
	def close(self): self.app.close()
	def close_all(self): self.app.close_all()
	def import_file(self): self.app.import_file()
	def export_as(self): self.app.export_as()
	def exit(self): self.app.exit()

	def set_mode(self, mode): self.app.current_doc.canvas.set_mode(mode)
	def open_url(self, url): self.app.open_url(url)
	def about(self): dialogs.about_dialog(self.app, self.mw)
	def properties(self): dialogs.docprops_dlg(self.app, self.mw)

	def set_text_mode(self):
		if not self.app.current_doc.canvas.mode in modes.TEXT_MODES:
			self.app.current_doc.canvas.set_mode(modes.TEXT_MODE)

	def undo(self):
		self.app.current_doc.api.do_undo()
		canvas = self.app.current_doc.canvas
		if canvas.mode == modes.BEZIER_EDITOR_MODE:
			canvas.controller.update_paths()
	def redo(self):
		self.app.current_doc.api.do_redo()
		canvas = self.app.current_doc.canvas
		if canvas.mode == modes.BEZIER_EDITOR_MODE:
			canvas.controller.update_paths()

	def clear_history(self):
		self.app.current_doc.api.clear_history()

	def cut(self):
		doc = self.app.current_doc
		if doc.canvas.mode == modes.TEXT_EDIT_MODE:
			text = doc.canvas.controller.get_selected()
			wal.set_text_to_clipboard(text)
			doc.canvas.controller.delete_selected()
		else:
			self.app.current_doc.api.cut_selected()

	def copy(self):
		doc = self.app.current_doc
		if doc.canvas.mode == modes.TEXT_EDIT_MODE:
			text = doc.canvas.controller.get_selected()
			wal.set_text_to_clipboard(text)
		else:
			self.app.current_doc.api.copy_selected()

	def paste(self):
		doc = self.app.current_doc
		if doc.canvas.mode == modes.TEXT_EDIT_MODE:
			doc.canvas.controller.replace_selected(wal.get_text_from_clipboar())
		else:
			doc.api.paste_selected()

	def delete(self):
		canvas = self.app.current_doc.canvas
		if canvas.mode == modes.BEZIER_EDITOR_MODE:
			canvas.controller.delete_selected_nodes()
		elif canvas.mode == modes.TEXT_EDIT_MODE:
			canvas.controller.key_del()
		else:
			self.app.current_doc.api.delete_selected()

	def duplicate(self): self.app.current_doc.api.duplicate_selected()
	def select_all(self):
		canvas = self.app.current_doc.canvas
		if canvas.mode == modes.BEZIER_EDITOR_MODE:
			canvas.controller.select_all_nodes()
		elif canvas.mode == modes.TEXT_EDIT_MODE:
			canvas.controller.select_all()
		else:
			self.app.current_doc.selection.select_all()

	def deselect(self, *args):
		canvas = self.app.current_doc.canvas
		if canvas.mode == modes.BEZIER_EDITOR_MODE:
			canvas.controller.set_selected_nodes()
		elif canvas.mode == modes.TEXT_EDIT_MODE:
			canvas.controller.deselect()
		else:
			self.app.current_doc.selection.clear()

	def invert_selection(self):
		canvas = self.app.current_doc.canvas
		if canvas.mode == modes.BEZIER_EDITOR_MODE:
			canvas.controller.select_all_nodes(True)
		else:
			self.app.current_doc.selection.invert_selection()

	def zoom_in(self): self.app.current_doc.canvas.zoom_in()
	def zoom_out(self): self.app.current_doc.canvas.zoom_out()
	def previous_zoom(self): self.app.current_doc.canvas.zoom_previous()
	def fit_zoom_to_page(self): self.app.current_doc.canvas.zoom_fit_to_page()
	def zoom_100(self): self.app.current_doc.canvas.zoom_100()
	def zoom_selected(self): self.app.current_doc.canvas.zoom_selected()
	def force_redraw(self): self.app.current_doc.canvas.force_redraw()
	def preferences(self): get_prefs_dialog(self.mw)

	def stroke_view(self):
		if self.insp.is_doc():
			canvas = self.app.current_doc.canvas
			if canvas.stroke_view:
				canvas.stroke_view = False
			else:
				canvas.stroke_view = True
			canvas.force_redraw()

	def draft_view(self):
		if self.insp.is_doc():
			canvas = self.app.current_doc.canvas
			if canvas.draft_view:
				canvas.draft_view = False
				canvas.force_redraw()
			else:
				canvas.draft_view = True
			canvas.force_redraw()

	def show_snapping(self):
		if self.insp.is_doc():
			canvas = self.app.current_doc.canvas
			if canvas.show_snapping:
				canvas.show_snapping = False
			else:
				canvas.show_snapping = True
				self.app.current_doc.snap.active_snap = [None, None]

	def show_grid(self):
		if self.insp.is_doc():
			methods = self.app.current_doc.methods
			api = self.app.current_doc.api
			grid_layer = methods.get_grid_layer()
			prop = [] + grid_layer.properties
			prop[0] = abs(prop[0] - 1)
			api.set_layer_properties(grid_layer, prop)

	def show_guides(self):
		if self.insp.is_doc():
			methods = self.app.current_doc.methods
			api = self.app.current_doc.api
			guide_layer = methods.get_guide_layer()
			prop = [] + guide_layer.properties
			prop[0] = abs(prop[0] - 1)
			api.set_layer_properties(guide_layer, prop)
			self.app.current_doc.snap.update_guides_grid()

	def snap_to_grid(self):
		if self.insp.is_doc():
			snap = self.app.current_doc.snap
			snap.snap_to_grid = not snap.snap_to_grid
			snap.update_grid()
			events.emit(events.SNAP_CHANGED)

	def snap_to_guides(self):
		if self.insp.is_doc():
			snap = self.app.current_doc.snap
			snap.snap_to_guides = not snap.snap_to_guides
			snap.update_guides_grid()
			events.emit(events.SNAP_CHANGED)

	def snap_to_objects(self):
		if self.insp.is_doc():
			snap = self.app.current_doc.snap
			snap.snap_to_objects = not snap.snap_to_objects
			snap.update_objects_grid()
			events.emit(events.SNAP_CHANGED)

	def snap_to_page(self):
		if self.insp.is_doc():
			snap = self.app.current_doc.snap
			snap.snap_to_page = not snap.snap_to_page
			snap.update_page_grid()
			events.emit(events.SNAP_CHANGED)

	def draw_page_border(self):
		if self.insp.is_doc():
			methods = self.app.current_doc.methods
			api = self.app.current_doc.api
			border = methods.get_page_border()
			api.set_page_border(not border)

	#---Page management
	def next_page(self):
		doc = self.app.current_doc
		pages = doc.get_pages()
		if pages.index(doc.active_page) < len(pages) - 1:
			self.app.current_doc.next_page()
		else:
			self.insert_page()

	def previous_page(self):
		self.app.current_doc.previous_page()

	def delete_page(self):
		index = dialogs.delete_page_dlg(self.mw, self.app.current_doc)
		if index >= 0: self.app.current_doc.api.delete_page(index)

	def insert_page(self):
		ret = dialogs.insert_page_dlg(self.mw, self.app.current_doc)
		if ret: self.app.current_doc.api.insert_page(*ret)

	def goto_start(self): self.goto_page(0)
	def goto_end(self): self.goto_page(len(self.app.current_doc.get_pages()) - 1)

	def goto_page(self, index=None):
		if index is None:
			index = dialogs.goto_page_dlg(self.mw, self.app.current_doc)
			if index is None:return
		if index >= 0:
			self.app.current_doc.goto_page(index)

	def create_page_border(self):
		api = self.app.current_doc.api
		w, h = self.app.current_doc.get_page_size()
		api.create_rectangle([-w / 2.0, -h / 2.0, w / 2.0, h / 2.0])

	def create_guide_border(self):
		api = self.app.current_doc.api
		w, h = self.app.current_doc.get_page_size()
		shift = config.page_border
		api.create_guides([[shift - w / 2.0, uc2const.VERTICAL],
						[shift - h / 2.0, uc2const.HORIZONTAL],
						[w / 2.0 - shift, uc2const.VERTICAL],
						[h / 2.0 - shift, uc2const.HORIZONTAL]])

	def create_guides_at_center(self):
		self.app.current_doc.api.create_guides([[0, uc2const.VERTICAL],
											[ 0, uc2const.HORIZONTAL]])

	def remove_all_guides(self, *args):
		self.app.current_doc.api.delete_all_guides()

	def clear_trafo(self):self.app.current_doc.api.clear_trafo()
	def rotate_left(self):self.app.current_doc.api.rotate_selected(math.pi / 2.0)
	def rotate_right(self):self.app.current_doc.api.rotate_selected(-math.pi / 2.0)
	def mirror_h(self):self.app.current_doc.api.mirror_selected(False)
	def mirror_v(self):self.app.current_doc.api.mirror_selected()

	def convert_to_curve(self):self.app.current_doc.api.convert_to_curve_selected()

	def convert_stroke_to_curve(self):
		doc = self.app.current_doc
		selection = self.app.current_doc.selection
		doc.canvas.set_mode(modes.WAIT_MODE)
		try:
			objs = []
			for obj in selection.objs:
				if obj.is_primitive() and not obj.is_pixmap() and obj.style[1] \
				and obj.style[1][1]:
					pths = apply_trafo_to_paths(obj.get_initial_paths(), obj.trafo)
					style = doc.model.get_def_style()
					style[0] = [sk2_const.FILL_SOLID, deepcopy(obj.style[1][2])]
					pths = stroke_to_curve(pths, obj.style[1])
					objs.append(doc.api.create_curve(pths, style))
			selection.set(objs)
		except:
			doc.canvas.set_mode()
			msg = _('Error occurred during this operation.')
			msg += '\n' + _('Perhaps this was due to the imperfection of the algorithm.')
			error_dialog(self.app.mw, self.app.appdata.app_name, msg)
		doc.canvas.set_mode()

	def group(self):self.app.current_doc.api.group_selected()
	def ungroup(self):self.app.current_doc.api.ungroup_selected()
	def ungroup_all(self):self.app.current_doc.api.ungroup_all()
	def combine_selected(self):self.app.current_doc.api.combine_selected()
	def break_apart_selected(self):self.app.current_doc.api.break_apart_selected()

	def raise_to_top(self):self.app.current_doc.api.raise_to_top()
	def raise_obj(self):self.app.current_doc.api.raise_obj()
	def lower_obj(self):self.app.current_doc.api.lower_obj()
	def lower_to_bottom(self):self.app.current_doc.api.lower_to_bottom()

	def set_container(self):
		doc = self.app.current_doc
		doc.canvas.set_temp_mode(modes.PICK_MODE, self.select_container)

	def select_container(self, objs):
		selection = self.app.current_doc.selection
		if len(objs) == 1 and objs[0].cid > sk2_model.PRIMITIVE_CLASS and not \
		objs[0] in selection.objs and not objs[0].cid == sk2_model.PIXMAP:
			self.app.current_doc.api.pack_container(objs[0])
			return False

		if not len(objs):
			txt = _("There is no selected object.")
		elif objs[0] in selection.objs:
			txt = _("Object from current selection cannot be container.")
		else:
			txt = _("Selected object cannot be container.")

		txt += '\n' + _('Do you want to try again?')

		return yesno_dialog(self.app.mw, self.app.appdata.app_name, txt)


	def unpack_container(self):self.app.current_doc.api.unpack_container()

	def select_all_nodes(self):
		canvas = self.app.current_doc.canvas
		if canvas.mode == modes.BEZIER_EDITOR_MODE:
			canvas.controller.select_all_nodes()

	def reverse_all_paths(self):
		canvas = self.app.current_doc.canvas
		if canvas.mode == modes.BEZIER_EDITOR_MODE:
			canvas.controller.reverse_all_paths()

	def select_subpath_nodes(self):
		canvas = self.app.current_doc.canvas
		if canvas.mode == modes.BEZIER_EDITOR_MODE:
			canvas.controller.select_all_nodes_in_subpaths()

	def delete_subpaths(self):
		canvas = self.app.current_doc.canvas
		if canvas.mode == modes.BEZIER_EDITOR_MODE:
			canvas.controller.delete_selected_subpaths()

	def reverse_subpaths(self):
		canvas = self.app.current_doc.canvas
		if canvas.mode == modes.BEZIER_EDITOR_MODE:
			canvas.controller.reverse_selected_subpaths()

	def extract_subpaths(self):
		canvas = self.app.current_doc.canvas
		if canvas.mode == modes.BEZIER_EDITOR_MODE:
			canvas.controller.extract_selected_subpaths()

	def add_node(self):
		canvas = self.app.current_doc.canvas
		if canvas.mode == modes.BEZIER_EDITOR_MODE:
			canvas.controller.insert_new_node()

	def delete_node(self):
		canvas = self.app.current_doc.canvas
		if canvas.mode == modes.BEZIER_EDITOR_MODE:
			canvas.controller.delete_selected_nodes()

	def add_seg(self):
		canvas = self.app.current_doc.canvas
		if canvas.mode == modes.BEZIER_EDITOR_MODE:
			canvas.controller.add_seg()

	def delete_seg(self):
		canvas = self.app.current_doc.canvas
		if canvas.mode == modes.BEZIER_EDITOR_MODE:
			canvas.controller.delete_seg()

	def join_nodes(self):
		canvas = self.app.current_doc.canvas
		if canvas.mode == modes.BEZIER_EDITOR_MODE:
			canvas.controller.join_nodes()

	def split_nodes(self):
		canvas = self.app.current_doc.canvas
		if canvas.mode == modes.BEZIER_EDITOR_MODE:
			canvas.controller.split_nodes()

	def seg_to_line(self):
		canvas = self.app.current_doc.canvas
		if canvas.mode == modes.BEZIER_EDITOR_MODE:
			canvas.controller.convert_to_line()

	def seg_to_curve(self):
		canvas = self.app.current_doc.canvas
		if canvas.mode == modes.BEZIER_EDITOR_MODE:
			canvas.controller.convert_to_curve()

	def make_node_cusp(self):
		canvas = self.app.current_doc.canvas
		if canvas.mode == modes.BEZIER_EDITOR_MODE:
			canvas.controller.set_connection_type()

	def make_node_smooth(self):
		canvas = self.app.current_doc.canvas
		if canvas.mode == modes.BEZIER_EDITOR_MODE:
			canvas.controller.set_connection_type(sk2_const.NODE_SMOOTH)

	def make_node_symmetrical(self):
		canvas = self.app.current_doc.canvas
		if canvas.mode == modes.BEZIER_EDITOR_MODE:
			canvas.controller.set_connection_type(sk2_const.NODE_SYMMETRICAL)

	def conv_to_cmyk(self):self.app.current_doc.api.convert_bitmap(uc2const.IMAGE_CMYK)
	def conv_to_rgb(self):self.app.current_doc.api.convert_bitmap(uc2const.IMAGE_RGB)
	def conv_to_lab(self):self.app.current_doc.api.convert_bitmap(uc2const.IMAGE_LAB)
	def conv_to_gray(self):self.app.current_doc.api.convert_bitmap(uc2const.IMAGE_GRAY)
	def conv_to_bw(self):self.app.current_doc.api.convert_bitmap(uc2const.IMAGE_MONO)
	def invert_bitmap(self):self.app.current_doc.api.invert_bitmap()
	def remove_alpha(self):self.app.current_doc.api.remove_alpha()
	def invert_alpha(self):self.app.current_doc.api.invert_alpha()

	def fill_selected(self, color):
		doc = self.app.current_doc
		canvas = doc.canvas
		if canvas.mode in modes.EDIT_MODES and canvas.controller.target:
			doc.api.fill_selected(color, [canvas.controller.target, ])
		elif not doc.selection.objs:
			txt = _('Do you wish to change default fill color for this document?')
			txt += '\n'
			txt += _('This style will be applied to newly created objects.')
			title = self.app.appdata.app_name
			if dialogs.yesno_dialog(self.mw, title, txt):
				new_style = doc.model.get_def_style()
				if color:
					fill_style = [sk2_const.FILL_EVENODD, sk2_const.FILL_SOLID,
							deepcopy(color)]
					new_style[0] = fill_style
				else:
					new_style[0] = []
				doc.api.set_default_style(new_style)
		else:
			doc.api.fill_selected(color)

	def stroke_selected(self, color):
		doc = self.app.current_doc
		canvas = doc.canvas
		if canvas.mode in modes.EDIT_MODES and canvas.controller.target:
			doc.api.stroke_selected(color, [canvas.controller.target, ])
		elif not doc.selection.objs:
			txt = _('Do you wish to change default stroke color for this document?')
			txt += '\n'
			txt += _('This style will be applied to newly created objects.')
			title = self.app.appdata.app_name
			if dialogs.yesno_dialog(self.mw, title, txt):
				new_style = doc.model.get_def_style()
				if color:
					if new_style[1]:
						new_style[1][2] = deepcopy(color)
					else:
						new_style[1] = [sk2_const.STROKE_MIDDLE,
									0.1 * uc2const.mm_to_pt,
									deepcopy(color), [], sk2_const.CAP_BUTT,
									sk2_const.JOIN_MITER,
									1.0 / math.sin(45.0 / 2.0),
									0, 0, []
									]
				else:
					new_style[1] = []
				doc.api.set_default_style(new_style)
		else:
			doc.api.stroke_selected(color)

	def show_plugin(self, *args):
		self.app.plg_area.show_plugin(*args)

