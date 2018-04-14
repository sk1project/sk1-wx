# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013 by Igor E. Novikov
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math
from copy import deepcopy

from uc2 import libgeom, uc2const, libimg, sk2const
from uc2.formats.sk2 import sk2_model

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

    def __init__(self):
        pass

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
        if not action:
            return
        if len(action) == 1:
            action[0]()
        else:
            action[0](*action[1:])

    def _clear_history_stack(self, stack):
        for obj in stack:
            if isinstance(obj, list):
                self._clear_history_stack(obj)
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

    def _set_default_page_format(self, page_format):
        self.methods.set_default_page_format(page_format)

    def _set_desktop_bg(self, color):
        self.methods.set_desktop_bg(color)

    def _set_page_border(self, border):
        self.methods.set_page_border(border)

    def _set_page_fill(self, page_fill):
        self.methods.set_page_fill(page_fill)

    def _set_layer_properties(self, layer, prop):
        layer.properties = prop

    def _set_layer_name(self, layer, name):
        layer.name = name

    def _set_grid_values(self, geom):
        self.methods.set_grid_values(geom)

    def _set_grid_color(self, color):
        self.methods.set_grid_rgba_color(color)

    def _set_guide_color(self, color):
        self.methods.set_guide_rgb_color(color)

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

    def _set_page_snapshot(self, layers):
        page = self.presenter.active_page
        page.childs = layers

    def _get_layers_snapshot(self):
        layers_snapshot = []
        layers = self.presenter.get_editable_layers()
        for layer in layers:
            layers_snapshot.append([layer, [] + layer.childs])
        return layers_snapshot

    def _set_layers_snapshot(self, layers_snapshot):
        for layer, childs in layers_snapshot:
            layer.childs = childs

    def _set_active_layer(self, layer):
        self.presenter.active_layer = layer

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
        self.model.set_def_style(style)

    def _set_obj_style(self, obj, style):
        obj.style = style
        obj.update()

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
            obj.clear_color_cache()

    def _fill_objs(self, objs, color):
        for obj in objs:
            style = deepcopy(obj.style)
            obj.clear_color_cache()
            if obj.is_pixmap:
                if color:
                    style[3][0] = deepcopy(color)
                else:
                    style[3][0] = []
            else:
                if color:
                    fill = style[0]
                    new_fill = []
                    if not fill:
                        new_fill.append(self.sk2_cfg.default_fill_rule)
                    else:
                        new_fill.append(fill[0])
                    new_fill.append(sk2const.FILL_SOLID)
                    new_fill.append(deepcopy(color))
                    style[0] = new_fill
                else:
                    style[0] = []
            obj.style = style
            obj.fill_trafo = []

    def _set_objs_fill_style(self, objs, fill_style):
        for obj in objs:
            if not obj.is_pixmap:
                style = deepcopy(obj.style)
                style[0] = deepcopy(fill_style)
                obj.style = style
                obj.clear_color_cache()

    def _set_paths_and_trafo(self, obj, paths, trafo):
        obj.paths = paths
        obj.trafo = trafo
        obj.update()

    def _set_paths(self, obj, paths):
        obj.paths = paths
        obj.update()

    def _set_text_trafos(self, obj, trafos):
        obj.trafos = trafos
        obj.update()

    def _set_text_markup(self, obj, markup):
        obj.markup = markup
        obj.update()

    def _apply_trafo(self, objs, trafo):
        before = []
        after = []
        for obj in objs:
            before.append(obj.get_trafo_snapshot())
            obj.apply_trafo(trafo)
            after.append(obj.get_trafo_snapshot())
        self.selection.update_bbox()
        return before, after

    def _apply_trafos(self, obj_trafo_list):
        before = []
        after = []
        for obj, trafo in obj_trafo_list:
            before.append(obj.get_trafo_snapshot())
            obj.apply_trafo(trafo)
            after.append(obj.get_trafo_snapshot())
        self.selection.update_bbox()
        return before, after

    def _set_bitmap_trafo(self, obj, trafo):
        obj.trafo = trafo
        obj.update()

    def _clear_trafo(self, objs):
        normal_trafo = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        before = []
        after = []
        for obj in objs:
            before.append(obj.get_trafo_snapshot())
            if obj.is_circle or obj.is_polygon or obj.is_text:
                obj.trafo = [] + obj.initial_trafo
            else:
                obj.trafo = [] + normal_trafo
            obj.fill_trafo = []
            obj.stroke_trafo = []
            obj.update()
            after.append(obj.get_trafo_snapshot())
        self.selection.update_bbox()
        return before, after

    def _set_snapshots(self, snapshots):
        for snapshot in snapshots:
            obj = snapshot[0]
            obj.set_trafo_snapshot(snapshot)
        self.selection.update_bbox()

    def _stroke_objs(self, objs, color):
        for obj in objs:
            style = deepcopy(obj.style)
            obj.clear_color_cache()
            if obj.is_pixmap:
                if color:
                    style[3][1] = deepcopy(color)
                else:
                    style[3][1] = []
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
            if not obj.is_pixmap:
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
        obj.clear_color_cache()
        if colorspace:
            obj.colorspace = colorspace

    def _set_alpha(self, obj, alphastr):
        obj.alpha_channel = alphastr
        obj.clear_color_cache()

    def _get_text_data(self, text_obj):
        text = text_obj.get_text()
        trafos = deepcopy(text_obj.trafos)
        markup = deepcopy(text_obj.markup)
        return text, trafos, markup

    def _set_text_data(self, text_obj, text, trafos, markup):
        text_obj.set_text(text)
        text_obj.trafos = trafos
        text_obj.markup = markup
        text_obj.update()

    def _set_tpgroup_data(self, tpgroup, text_obj, data):
        index = tpgroup.childs.index(text_obj)
        tpgroup.childs_data[index] = data
        path = tpgroup.childs[0]
        tpgroup.set_text_on_path(path, text_obj, data)
        tpgroup.update()


class PresenterAPI(AbstractAPI):
    def __init__(self, presenter):
        AbstractAPI.__init__(self)
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

    def set_mode(self, mode=modes.SELECT_MODE):
        transaction = [
            [[self._set_mode, mode],
             [self._selection_update, ]],
            [[self._set_mode, mode],
             [self._selection_update, ]],
            False]
        self.add_undo(transaction)

    # --- DOCUMENT

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

    def set_doc_metainfo(self, metainfo):
        cur_metainfo = self.model.metainfo
        transaction = [
            [[self.methods.set_doc_metainfo, cur_metainfo]],
            [[self.methods.set_doc_metainfo, metainfo]],
            False]
        self.methods.set_doc_metainfo(metainfo)
        self.add_undo(transaction)

    # --- PAGES

    def set_active_page(self, index):
        if not self.undo:
            self.presenter.set_active_page(index)
            self.selection.clear()
        else:
            pages = self.presenter.get_pages()
            active_index_before = pages.index(self.presenter.active_page)
            sel_before = [] + self.selection.objs
            active_index_after = index

            self.presenter.canvas.set_mode()
            self.selection.clear()
            self.presenter.set_active_page(index)

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
        if index == 0 and len(pages) == 1:
            return

        before = self._get_pages_snapshot()
        sel_before = [] + self.selection.objs
        active_index_before = pages.index(self.presenter.active_page)

        self.presenter.canvas.set_mode()
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
        if position == uc2const.AFTER:
            active_index_after += 1

        for item in range(number):
            page = self.methods.insert_page(active_index_after + item)
            self.methods.add_layer(page)
            page.do_update()

        self.presenter.canvas.set_mode()
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

        self.presenter.canvas.set_mode()
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

    def set_desktop_bg(self, color):
        color_before = self.methods.get_desktop_bg()
        color_after = color
        self._set_desktop_bg(color_after)
        transaction = [
            [[self._set_desktop_bg, color_before]],
            [[self._set_desktop_bg, color_after]],
            False]
        self.add_undo(transaction)

    def set_page_border(self, border):
        border_before = self.methods.get_page_border()
        border_after = border
        self._set_page_border(border_after)
        transaction = [
            [[self._set_page_border, border_before]],
            [[self._set_page_border, border_after]],
            False]
        self.add_undo(transaction)

    def set_page_fill(self, page_fill):
        page_fill_before = self.methods.get_page_fill()
        page_fill_after = page_fill
        self._set_page_fill(page_fill)
        transaction = [
            [[self._set_page_fill, page_fill_before]],
            [[self._set_page_fill, page_fill_after]],
            False]
        self.add_undo(transaction)

    def set_default_page_format(self, page_format):
        format_before = self.methods.get_default_page_format()
        format_after = page_format
        self._set_default_page_format(format_after)
        transaction = [
            [[self._set_default_page_format, format_before]],
            [[self._set_default_page_format, format_after]],
            False]
        self.add_undo(transaction)

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

    # --- LAYERS

    def create_layer(self, name=''):
        page = self.presenter.active_page
        new_layer = sk2_model.Layer(self.sk2_cfg, page, name)
        page.childs += [new_layer, ]
        objs_list = [[new_layer, page, page.childs.index(new_layer)], ]
        active_layer_before = self.presenter.active_layer
        self.presenter.active_layer = new_layer
        sel = [] + self.selection.objs
        transaction = [
            [[self._delete_objects, objs_list],
             [self._set_selection, sel],
             [self._set_active_layer, active_layer_before]],
            [[self._insert_objects, objs_list],
             [self._set_selection, sel],
             [self._set_active_layer, new_layer]],
            False]
        self.add_undo(transaction)
        self.selection.update()

    def delete_layer(self, layer):
        page = layer.parent
        indx = page.childs.index(layer)
        objs_list = [[layer, page, indx], ]
        page.childs.remove(layer)
        active_layer_before = self.presenter.active_layer
        active_layer_after = self.presenter.active_layer
        if self.presenter.active_layer == layer:
            self.presenter.active_layer = page.childs[-1]
            active_layer_after = self.presenter.active_layer
        sel = [] + self.selection.objs
        self.selection.clear()
        transaction = [
            [[self._insert_objects, objs_list],
             [self._set_selection, sel],
             [self._set_active_layer, active_layer_before]],
            [[self._delete_objects, objs_list],
             [self._set_selection, []],
             [self._set_active_layer, active_layer_after]],
            False]
        self.add_undo(transaction)
        self.selection.update()

    def set_active_layer(self, layer):
        if not layer == self.presenter.active_layer and \
                layer.properties[0] and layer.properties[1]:
            active_layer_before = self.presenter.active_layer
            active_layer_after = layer
            self.presenter.active_layer = layer
            sel = [] + self.selection.objs
            transaction = [
                [[self._set_selection, sel],
                 [self._set_active_layer, active_layer_before]],
                [[self._set_selection, sel],
                 [self._set_active_layer, active_layer_after]],
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

    def set_layer_name(self, layer, name):
        before = layer.name
        after = name
        self._set_layer_name(layer, name)
        transaction = [
            [[self._set_layer_name, layer, before], ],
            [[self._set_layer_name, layer, after], ],
            False]
        self.add_undo(transaction)
        self.selection.update()

    def layer_raise(self, layer):
        page = self.presenter.active_page
        layers_before = self.presenter.get_layers()
        index = layers_before.index(layer)
        layers_after = [] + layers_before
        layers_after.remove(layer)
        layers_after.insert(index + 1, layer)
        page.childs = layers_after
        transaction = [
            [[self._set_page_snapshot, layers_before]],
            [[self._set_page_snapshot, layers_after]],
            False]
        self.add_undo(transaction)
        self.selection.update()

    def layer_to_top(self, layer):
        page = self.presenter.active_page
        layers_before = self.presenter.get_layers()
        layers_after = [] + layers_before
        layers_after.remove(layer)
        layers_after.append(layer)
        page.childs = layers_after
        transaction = [
            [[self._set_page_snapshot, layers_before]],
            [[self._set_page_snapshot, layers_after]],
            False]
        self.add_undo(transaction)
        self.selection.update()

    def layer_lower(self, layer):
        page = self.presenter.active_page
        layers_before = self.presenter.get_layers()
        index = layers_before.index(layer)
        layers_after = [] + layers_before
        layers_after.remove(layer)
        layers_after.insert(index - 1, layer)
        page.childs = layers_after
        transaction = [
            [[self._set_page_snapshot, layers_before]],
            [[self._set_page_snapshot, layers_after]],
            False]
        self.add_undo(transaction)
        self.selection.update()

    def layer_to_bottom(self, layer):
        page = self.presenter.active_page
        layers_before = self.presenter.get_layers()
        layers_after = [] + layers_before
        layers_after.remove(layer)
        layers_after = [layer, ] + layers_after
        page.childs = layers_after
        transaction = [
            [[self._set_page_snapshot, layers_before]],
            [[self._set_page_snapshot, layers_after]],
            False]
        self.add_undo(transaction)
        self.selection.update()

    # --- GRID

    def set_grid_values(self, geom):
        before = self.methods.get_grid_values()
        after = geom
        self.methods.set_grid_values(after)
        transaction = [
            [[self._set_grid_values, before]],
            [[self._set_grid_values, after]],
            False]
        self.add_undo(transaction)
        self.selection.update()

    def set_grid_color(self, color):
        before = self.methods.get_grid_rgba_color()
        after = color
        self.methods.set_grid_rgba_color(after)
        transaction = [
            [[self._set_grid_color, before]],
            [[self._set_grid_color, after]],
            False]
        self.add_undo(transaction)
        self.selection.update()

    # --- GUIDES

    def set_guide_color(self, color):
        before = self.methods.get_guide_rgb_color()
        after = color
        self.methods.set_guide_rgb_color(after)
        transaction = [
            [[self._set_guide_color, before]],
            [[self._set_guide_color, after]],
            False]
        self.add_undo(transaction)
        self.selection.update()

    def create_guides(self, vals=None):
        if vals:
            objs_list = []
            parent = self.methods.get_guide_layer()
            for val in vals:
                pos, orient = val
                obj = sk2_model.Guide(self.sk2_cfg, parent, pos, orient)
                objs_list.append([obj, parent, -1])
                obj.update()
            self._insert_objects(objs_list)
            transaction = [
                [[self._delete_objects, objs_list]],
                [[self._insert_objects, objs_list]],
                False]
            self.add_undo(transaction)
            self.selection.update()

    def set_guide_properties(self, guide, pos, orient):
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

    def delete_guides(self, objs=None):
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
            if child.is_guide:
                guides.append(child)
        self.delete_guides(guides)

    # --- OBJECT

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
        if objs is None:
            objs = self.app.clipboard.get()
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

    def trasform_objs(self, obj_trafo_list):
        before, after = self._apply_trafos(obj_trafo_list)
        sel_before = [] + self.selection.objs
        sel_after = [] + sel_before
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
                if obj.is_primitive:
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
            dx = center_x - m11 * center_x + m21 * center_y
            dy = center_y - m21 * center_x - m11 * center_y

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
                if obj.is_primitive and not obj.is_curve:
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

    # --- OBJECT STYLE

    def set_default_style(self, style):
        style_before = self.model.get_def_style()
        self._set_default_style(style)
        transaction = [
            [[self._set_default_style, style_before]],
            [[self._set_default_style, style]],
            False]
        self.add_undo(transaction)

    def set_obj_style(self, obj, style):
        style_before = obj.style
        sel_before = sel_after = [] + self.selection.objs
        self._set_obj_style(obj, style)
        transaction = [
            [[self._set_obj_style, obj, style_before],
             [self._set_selection, sel_before]],
            [[self._set_obj_style, obj, style],
             [self._set_selection, sel_after]],
            False]
        self.add_undo(transaction)
        self.selection.update()

    def _get_primitive_objs(self, objs, exclude_pixmap=False):
        ret = []
        for obj in objs:
            if obj.is_primitive:
                if exclude_pixmap and obj.is_pixmap:
                    continue
                ret.append(obj)
            else:
                ret += self._get_primitive_objs(obj.childs, exclude_pixmap)
        return ret

    def fill_selected(self, color, objs=None):
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

    def set_fill_style(self, fill_style, objs=None):
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

    def stroke_selected(self, color, objs=None):
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

    def set_stroke_style(self, stroke_style, objs=None):
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

    # --- GROUP

    def group_selected(self):
        if self.selection.objs:
            before = self._get_layers_snapshot()
            objs = [] + self.selection.objs
            sel_before = [] + self.selection.objs

            parent = objs[-1].parent
            group = sk2_model.Group(objs[-1].config, parent, objs)
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
            if not obj.is_group:
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
                if obj.is_group:
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

    # --- CONTAINER

    def pack_container(self, container):
        if self.selection.objs:
            before = self._get_layers_snapshot()
            objs = [] + [container] + self.selection.objs
            sel_before = [] + self.selection.objs

            parent = container.parent
            group = sk2_model.Container(container.config, parent, objs)
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

    # --- CURVE

    def create_curve(self, paths, style=None):
        parent = self.presenter.active_layer
        obj = sk2_model.Curve(self.sk2_cfg, parent, paths)
        if style is None:
            obj.style = self.model.get_def_style()
        else:
            obj.style = style
        obj.update()
        self.insert_object(obj, parent, len(parent.childs))
        return obj

    def update_curve(self, obj, paths, trafo=None):
        trafo = trafo or [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
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

    def extract_subpaths(self, target, indexes):
        before = self._get_layers_snapshot()

        parent = target.parent
        parent_index = parent.childs.index(target)
        cfg = target.config

        paths = libgeom.get_transformed_paths(target)

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
            curve1 = sk2_model.Curve(cfg, parent)
            curve1.paths = p1
            curve1.style = deepcopy(target.style)
            if target.fill_trafo:
                curve1.fill_trafo = [] + target.fill_trafo
            if target.stroke_trafo:
                curve1.stroke_trafo = [] + target.stroke_trafo
            parent.childs.insert(parent_index, curve1)
            curve1.update()
        if p0:
            curve0 = sk2_model.Curve(cfg, parent)
            curve0.paths = p0
            curve0.style = deepcopy(target.style)
            if target.fill_trafo:
                curve0.fill_trafo = [] + target.fill_trafo
            if target.stroke_trafo:
                curve0.stroke_trafo = [] + target.stroke_trafo
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

    def break_apart_selected(self):
        before = self._get_layers_snapshot()
        sel_before = [] + self.selection.objs
        obj = self.selection.objs[0]

        parent = obj.parent
        index = parent.childs.index(obj)
        cfg = obj.config

        paths = libgeom.get_transformed_paths(obj)

        objs = []

        obj.parent.childs.remove(obj)
        for path in paths:
            if path and path[1]:
                curve = sk2_model.Curve(cfg, parent)
                curve.paths = [path, ]
                curve.style = deepcopy(obj.style)
                if obj.fill_trafo:
                    curve.fill_trafo = [] + obj.fill_trafo
                if obj.stroke_trafo:
                    curve.stroke_trafo = [] + obj.stroke_trafo
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

    def combine_selected(self):
        before = self._get_layers_snapshot()
        sel_before = [] + self.selection.objs
        objs = self.selection.objs
        parent = objs[0].parent
        index = parent.childs.index(objs[0])

        style = deepcopy(objs[0].style)
        parent = objs[0].parent
        cfg = objs[0].config
        paths = []
        for obj in objs:
            for item in libgeom.get_transformed_paths(obj):
                if item[1]:
                    paths.append(item)
        result = sk2_model.Curve(cfg, parent)
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

    def flat_curve_selected(self):
        if self.selection.objs:
            before = self._get_layers_snapshot()
            sel = self.selection.objs
            objs = [] + sel
            sel_before = [] + sel

            for obj in objs:
                if obj.is_primitive and obj.is_curve:
                    curve = obj.copy()
                    curve.paths = libgeom.flat_paths(curve.paths)
                    parent = obj.parent
                    curve.parent = parent
                    parent.childs[parent.childs.index(obj)] = curve
                    sel.objs[sel.index(obj)] = curve

            after = self._get_layers_snapshot()
            sel_after = [] + sel
            transaction = [
                [[self._set_layers_snapshot, before],
                 [self._set_selection, sel_before]],
                [[self._set_layers_snapshot, after],
                 [self._set_selection, sel_after]],
                False]
            self.add_undo(transaction)
            self.selection.update()

    # --- RECTANGLE

    def create_rectangle(self, rect):
        rect = self._normalize_rect(rect)
        parent = self.presenter.active_layer
        obj = sk2_model.Rectangle(self.sk2_cfg, parent, rect)
        obj.style = self.model.get_def_style()
        obj.update()
        self.insert_object(obj, parent, len(parent.childs))

    def set_rect(self, obj, rect):
        self.methods.set_rect(obj, rect)
        self.eventloop.emit(self.eventloop.DOC_MODIFIED)
        self.selection.update()

    def set_rect_final(self, obj, rect, rect_before):
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

    def set_rect_corners_final(self, corners, corners_before=None, obj=None):
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

    # --- CIRCLE

    def create_ellipse(self, rect):
        rect = self._normalize_rect(rect)
        parent = self.presenter.active_layer
        obj = sk2_model.Circle(self.sk2_cfg, parent, rect)
        obj.style = self.model.get_def_style()
        obj.update()
        self.insert_object(obj, parent, len(parent.childs))

    def set_circle_properties(self, circle_type, angle1, angle2, obj=None):
        if obj is None:
            sel = [] + self.selection.objs
            obj = sel[0]
        mtds = self.methods
        mtds.set_circle_properties(obj, circle_type, angle1, angle2)
        self.eventloop.emit(self.eventloop.DOC_MODIFIED)
        self.selection.update()

    def set_circle_properties_final(self, circle_type, angle1, angle2,
                                    type_before=None, angle1_before=None,
                                    angle2_before=None, obj=None):
        if obj is None:
            sel = [] + self.selection.objs
            obj = sel[0]
            if type_before is None:
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
        else:
            if type_before is None:
                type_before = obj.circle_type
                angle1_before = obj.angle1
                angle2_before = obj.angle2
            mtds = self.methods
            mtds.set_circle_properties(obj, circle_type, angle1, angle2)
            transaction = [
                [[mtds.set_circle_properties, obj, type_before,
                  angle1_before, angle2_before], ],
                [[mtds.set_circle_properties, obj, circle_type,
                  angle1, angle2], ],
                False]
            self.add_undo(transaction)
            self.selection.update()

    # --- POLYGON

    def create_polygon(self, rect):
        rect = self._normalize_rect(rect)
        parent = self.presenter.active_layer
        obj = sk2_model.Polygon(self.sk2_cfg, parent, rect,
                                corners_num=config.default_polygon_num)
        obj.style = self.model.get_def_style()
        obj.update()
        self.insert_object(obj, parent, len(parent.childs))

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

    def set_polygon_properties(self, props, obj=None):
        if obj is None:
            sel = [] + self.selection.objs
            obj = sel[0]
        self.methods.set_polygon_properties(obj, *props)
        self.eventloop.emit(self.eventloop.DOC_MODIFIED)
        self.selection.update()

    def set_polygon_properties_final(self, props, props_before=None, obj=None):
        if obj is None:
            sel = [] + self.selection.objs
            obj = sel[0]
            if not props_before:
                props_before = [obj.angle1, obj.angle2, obj.coef1, obj.coef2]
            self.methods.set_polygon_properties(obj, *props)
            transaction = [
                [[self.methods.set_rect_corners, obj, ] + props_before,
                 [self._set_selection, sel], ],
                [[self.methods.set_rect_corners, obj, ] + props,
                 [self._set_selection, sel]],
                False]
            self.add_undo(transaction)
            self.selection.update()
        else:
            if not props_before:
                props_before = [obj.angle1, obj.angle2, obj.coef1, obj.coef2]
            self.methods.set_polygon_properties(obj, *props)
            transaction = [
                [[self.methods.set_rect_corners, obj, ] + props_before, ],
                [[self.methods.set_rect_corners, obj, ] + props, ],
                False]
            self.add_undo(transaction)
            self.selection.update()

    # --- PIXMAP

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
        pass
        # if not v_dpi:
        #     v_dpi = h_dpi
        # sel_before = [] + self.selection.objs
        # obj = sel_before[0]
        # trafo_before = obj.trafo
        # trafo_after = [] + obj.trafo

    # --- TEXT

    def create_text(self, doc_point):
        parent = self.presenter.active_layer
        if self.presenter.text_obj_style:
            style = deepcopy(self.presenter.text_obj_style)
        else:
            style = self.model.get_text_style()
        obj = sk2_model.Text(self.sk2_cfg, parent, doc_point, style=style)
        obj.update()
        self.insert_object(obj, parent, len(parent.childs))
        return obj

    def change_text(self, obj, text_after, trafos_after, markup_after):
        sel_before = [] + self.selection.objs
        text_before, trafos_before, markup_before = self._get_text_data(obj)
        self._set_text_data(obj, text_after, trafos_after, markup_after)
        transaction = [
            [[self._set_text_data, obj, text_before, trafos_before,
              markup_before],
             [self._set_selection, sel_before]],
            [[self._set_text_data, obj, text_after, trafos_after, markup_after],
             [self._set_selection, sel_before]],
            False]
        self.add_undo(transaction)
        self.selection.update()

    def set_temp_text_trafos(self, obj, trafos):
        self._set_text_trafos(obj, trafos)
        self.eventloop.emit(self.eventloop.DOC_MODIFIED)
        self.selection.update()

    def set_text_trafos(self, obj, trafos, trafos_before):
        sel_before = [] + self.selection.objs
        self._set_text_trafos(obj, trafos)
        transaction = [
            [[self._set_text_trafos, obj, trafos_before],
             [self._set_selection, sel_before]],
            [[self._set_text_trafos, obj, trafos],
             [self._set_selection, sel_before]],
            False]
        self.add_undo(transaction)
        self.selection.update()

    def straighten_text(self, obj=None):
        if not obj:
            sel_before = [] + self.selection.objs
            obj = sel_before[0]
        self.set_text_trafos(obj, {}, obj.trafos)

    def place_text_on_path(self, path, text_obj, childs_data):
        before = self._get_layers_snapshot()
        objs = [path, text_obj]
        sel_before = [path, text_obj]
        trafos_before = deepcopy(text_obj.trafos)

        parent = objs[-1].parent
        group = sk2_model.TP_Group(objs[-1].config, parent, objs, childs_data)
        group.set_text_on_path(path, text_obj, childs_data)
        group.update()
        for obj in objs:
            obj.parent.childs.remove(obj)
        parent.childs.append(group)
        parent_list = []
        for obj in objs:
            parent_list.append([obj, obj.parent])
            obj.parent = group

        after = self._get_layers_snapshot()
        trafos_after = deepcopy(text_obj.trafos)
        sel_after = [group]
        self.selection.set([group])
        transaction = [
            [[self._set_layers_snapshot, before],
             [self._restore_parents, parent_list],
             [self._set_text_trafos, text_obj, trafos_before],
             [self._set_selection, sel_before]],
            [[self._set_layers_snapshot, after],
             [self._set_parent, sel_after, group],
             [self._set_text_trafos, text_obj, trafos_after],
             [self._set_selection, sel_after]],
            False]
        self.add_undo(transaction)
        self.selection.update()

    def change_tpgroup(self, tpgroup, text_obj, data):
        if text_obj not in tpgroup.childs:
            return
        sel = [] + self.selection.objs
        index = tpgroup.childs.index(text_obj)
        data_before = tpgroup.childs_data[index]
        self._set_tpgroup_data(tpgroup, text_obj, data)
        transaction = [
            [[self._set_tpgroup_data, tpgroup, text_obj, data_before],
             [self._set_selection, sel]],
            [[self._set_tpgroup_data, tpgroup, text_obj, data],
             [self._set_selection, sel]],
            False]
        self.add_undo(transaction)
        self.selection.update()

    def place_text_on_circle(self, circle, text_obj, position, side_flag):
        mtds = self.methods
        childs_data = [0.5, sk2const.TEXT_ALIGN_CENTER, side_flag]
        before = self._get_layers_snapshot()
        objs = [circle, text_obj]
        sel_before = [circle, text_obj]
        trafos_before = deepcopy(text_obj.trafos)
        type_before = type_after = circle.circle_type
        angle1_before = circle.angle1
        angle2_before = circle.angle2

        angle1_after = angle2_after = position * math.pi / 2.0
        mtds.set_circle_properties(circle, type_after,
                                   angle1_after, angle2_after)

        parent = text_obj.parent
        group = sk2_model.TP_Group(text_obj.config, parent, objs, childs_data)
        group.set_text_on_path(circle, text_obj, childs_data)
        group.update()
        for obj in objs:
            obj.parent.childs.remove(obj)
        parent.childs.append(group)
        parent_list = []
        for obj in objs:
            parent_list.append([obj, obj.parent])
            obj.parent = group

        after = self._get_layers_snapshot()
        trafos_after = deepcopy(text_obj.trafos)
        sel_after = [group]
        self.selection.set([group])
        transaction = [
            [[self._set_layers_snapshot, before],
             [self._restore_parents, parent_list],
             [mtds.set_circle_properties, circle, type_before,
              angle1_before, angle2_before],
             [self._set_text_trafos, text_obj, trafos_before],
             [self._set_selection, sel_before]],
            [[self._set_layers_snapshot, after],
             [self._set_parent, sel_after, group],
             [mtds.set_circle_properties, circle, type_after,
              angle1_after, angle2_after],
             [self._set_text_trafos, text_obj, trafos_after],
             [self._set_selection, sel_after]],
            False]
        self.add_undo(transaction)
        self.selection.update()

    def change_tcgroup(self, tpgroup, text_obj, position, side_flag):
        if text_obj not in tpgroup.childs:
            return
        mtds = self.methods
        data = [0.5, sk2const.TEXT_ALIGN_CENTER, side_flag]
        circle = tpgroup.childs[0]
        type_before = type_after = circle.circle_type
        angle1_before = circle.angle1
        angle2_before = circle.angle2
        angle1_after = angle2_after = position * math.pi / 2.0
        mtds.set_circle_properties(circle, type_after,
                                   angle1_after, angle2_after)
        sel = [] + self.selection.objs
        index = tpgroup.childs.index(text_obj)
        data_before = tpgroup.childs_data[index]
        self._set_tpgroup_data(tpgroup, text_obj, data)
        transaction = [
            [[self._set_tpgroup_data, tpgroup, text_obj, data_before],
             [mtds.set_circle_properties, circle, type_before,
              angle1_before, angle2_before],
             [self._set_selection, sel]],
            [[self._set_tpgroup_data, tpgroup, text_obj, data],
             [mtds.set_circle_properties, circle, type_after,
              angle1_after, angle2_after],
             [self._set_selection, sel]],
            False]
        self.add_undo(transaction)
        self.selection.update()

    def set_text_markup(self, obj, markup, markup_before):
        sel_before = [] + self.selection.objs
        self._set_text_markup(obj, markup)
        transaction = [
            [[self._set_text_markup, obj, markup_before],
             [self._set_selection, sel_before]],
            [[self._set_text_markup, obj, markup],
             [self._set_selection, sel_before]],
            False]
        self.add_undo(transaction)
        self.selection.update()

    def clear_text_markup(self, obj=None):
        if not obj:
            sel_before = [] + self.selection.objs
            obj = sel_before[0]
        self.set_text_markup(obj, [], obj.markup)
