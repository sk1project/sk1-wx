# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013-2021 by Ihor E. Novikov
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
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.


from sk1 import config, modes
from uc2 import sk2const, uc2const


def verify_call(fn):
    def wrapper(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        return bool(fn(self, doc))
    return wrapper


class AppInspector:
    def __init__(self, app):
        self.app = app
        self.mw = None

    def update(self):
        self.mw = self.app.mw

    def is_doc(self):
        return bool(self.app.docs)

    def is_not_doc(self):
        return not self.is_doc()

    def is_cms(self):
        return False if not self.is_doc() else config.cms_use

    def is_cms_proofing(self):
        return False if not self.is_doc() else config.cms_proofing

    def is_others(self):
        return len(self.app.docs) > 1

    @verify_call
    def is_doc_saved(self, doc=None):
        return doc.saved if doc else False

    def is_doc_not_saved(self, doc=None):
        return not self.is_doc_saved(doc)

    def is_any_doc_not_saved(self):
        return any([doc.saved for doc in self.app.docs])

    def is_mode(self, *args):
        return True if self.is_doc() and self.app.current_doc.canvas.mode in args else False

    def is_file_history(self):
        return self.app.history.is_history()

    @verify_call
    def is_undo(self, doc=None):
        return bool(doc.api.undo)

    @verify_call
    def is_redo(self, doc=None):
        return bool(doc.api.redo)

    @verify_call
    def is_history(self, doc=None):
        return self.is_undo(doc) or self.is_redo(doc)

    @verify_call
    def is_selection(self, doc=None):
        return False if doc.selection is None else bool(doc.selection.objs)

    @verify_call
    def is_obj_selection(self, doc=None):
        if doc.canvas.mode == modes.TEXT_EDIT_MODE:
            return doc.canvas.controller.is_selected()
        return False if doc.selection is None else bool(doc.selection.objs)

    @verify_call
    def is_text_selection(self, doc=None):
        if doc.canvas.mode == modes.TEXT_EDIT_MODE:
            return doc.canvas.controller.is_selected()

    @verify_call
    def is_selected_node(self, doc=None):
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return len(doc.canvas.controller.selected_nodes) > 0

    @verify_call
    def can_be_selected(self, doc=None):
        check = doc.canvas.mode != modes.BEZIER_EDITOR_MODE
        if doc.canvas.mode in modes.EDIT_MODES and check:
            return False
        return doc.selection.can_be_any_selected()

    @verify_call
    def can_be_deleted(self, doc=None):
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return self.is_selected_node(doc)
        elif doc.canvas.mode == modes.TEXT_EDIT_MODE:
            return True
        return self.is_selection(doc)

    @verify_call
    def can_be_selected_all_nodes(self, doc=None):
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            sel_num = len(doc.canvas.controller.selected_nodes)
            all_num = doc.canvas.controller.count_all_nodes()
            return sel_num < all_num

    @verify_call
    def can_be_reversed_paths(self, doc=None):
        return doc.canvas.mode == modes.BEZIER_EDITOR_MODE

    @verify_call
    def is_subpath_selected(self, doc=None):
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return doc.canvas.controller.is_subpath_selected()

    @verify_call
    def can_be_deleted_node(self, doc=None):
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return self.is_selected_node(doc)

    @verify_call
    def can_be_added_node(self, doc=None):
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return doc.canvas.controller.new_node is not None

    def can_be_added_seg(self, doc=None):
        return self.can_be_joined_nodes(doc)

    @verify_call
    def can_be_deleted_seg(self, doc=None):
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return doc.canvas.controller.can_be_deleted_seg()

    @verify_call
    def can_be_joined_nodes(self, doc=None):
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return doc.canvas.controller.can_be_joined_nodes()

    @verify_call
    def can_be_splited_nodes(self, doc=None):
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return doc.canvas.controller.can_be_splited_nodes()

    @verify_call
    def can_be_seg_line(self, doc=None):
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return doc.canvas.controller.can_be_line()

    @verify_call
    def can_be_seg_curve(self, doc=None):
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return doc.canvas.controller.can_be_curve()

    @verify_call
    def can_be_node_cusp(self, doc=None):
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return doc.canvas.controller.can_be_cusp()

    @verify_call
    def can_be_node_smooth(self, doc=None):
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return doc.canvas.controller.can_be_smooth()

    @verify_call
    def can_be_node_symmetrical(self, doc=None):
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return doc.canvas.controller.can_be_symmetrical()

    @verify_call
    def is_clipboard(self, doc=None):
        return True if doc.canvas.mode == modes.TEXT_EDIT_MODE or \
                       self.app.clipboard.contents else False

    @verify_call
    def is_draft_view(self, doc=None):
        return doc.canvas.draft_view

    @verify_call
    def is_stroke_view(self, doc=None):
        return doc.canvas.stroke_view

    @verify_call
    def is_guides_visible(self, doc=None):
        return doc.methods.is_guide_visible()

    @verify_call
    def is_guides_editable(self, doc=None):
        return doc.methods.is_guide_editable()

    def is_guide_lock(self, doc=None):
        return not self.is_guides_editable(doc)

    @verify_call
    def is_grid_visible(self, doc=None):
        methods = doc.methods
        grid_layer = methods.get_grid_layer()
        return bool(grid_layer.properties[0])

    @verify_call
    def is_draw_page_border(self, doc=None):
        return doc.methods.get_page_border()

    @verify_call
    def is_show_snapping(self, doc=None):
        return doc.canvas.show_snapping

    @verify_call
    def is_snap_to_grid(self, doc=None):
        return doc.snap.snap_to_grid

    @verify_call
    def is_snap_to_guides(self, doc=None):
        return doc.snap.snap_to_guides

    @verify_call
    def is_snap_to_objects(self, doc=None):
        return doc.snap.snap_to_objects

    @verify_call
    def is_snap_to_page(self, doc=None):
        return doc.snap.snap_to_page

    @verify_call
    def can_be_next_page(self, _doc=None):
        return True

    @verify_call
    def can_be_previous_page(self, doc=None):
        pages = doc.get_pages()
        return bool(pages.index(doc.active_page))

    @verify_call
    def can_goto_page(self, doc=None):
        return len(doc.get_pages()) > 1

    @verify_call
    def can_delete_page(self, doc=None):
        return bool(len(doc.get_pages()) - 1)

    @staticmethod
    def is_obj_primitive(obj):
        return obj.is_primitive

    @staticmethod
    def is_obj_curve(obj):
        return obj.is_curve

    @staticmethod
    def is_obj_rect(obj):
        return obj.is_rect

    @staticmethod
    def is_obj_circle(obj):
        return obj.is_circle

    @staticmethod
    def is_obj_polygon(obj):
        return obj.is_polygon

    @staticmethod
    def is_obj_text(obj):
        return obj.is_text

    @staticmethod
    def is_obj_pixmap(obj):
        return obj.is_pixmap

    @verify_call
    def can_clear_trafo(self, doc=None):
        if self.is_selection(doc):
            for obj in doc.selection.objs:
                if self.is_obj_primitive(obj):
                    if not obj.trafo == sk2const.NORMAL_TRAFO:
                        return True

    @verify_call
    def can_inline_trafo(self, doc=None):
        if self.is_selection(doc):
            for obj in doc.selection.objs:
                if obj.is_curve:
                    if not obj.trafo == sk2const.NORMAL_TRAFO:
                        return True

    @verify_call
    def is_container_selected(self, doc=None):
        if self.is_selection(doc):
            objs = doc.selection.objs
            return len(objs) == 1 and objs[0].is_container

    @verify_call
    def is_pixmap_selected(self, doc=None):
        if self.is_selection(doc):
            objs = doc.selection.objs
            return len(objs) == 1 and objs[0].is_pixmap

    @verify_call
    def is_pixmap_alpha(self, doc=None):
        if self.is_selection(doc):
            objs = doc.selection.objs
            return len(objs) == 1 and objs[0].is_pixmap and objs[0].has_alpha()

    @verify_call
    def can_be_cmyk(self, doc=None):
        if self.is_selection(doc):
            objs = doc.selection.objs
            if len(objs) == 1 and objs[0].is_pixmap:
                return not objs[0].colorspace == uc2const.IMAGE_CMYK

    @verify_call
    def can_be_rgb(self, doc=None):
        if self.is_selection(doc):
            objs = doc.selection.objs
            if len(objs) == 1 and objs[0].is_pixmap:
                return not objs[0].colorspace == uc2const.IMAGE_RGB

    @verify_call
    def can_be_lab(self, doc=None):
        if self.is_selection(doc):
            objs = doc.selection.objs
            if len(objs) == 1 and objs[0].is_pixmap:
                return not objs[0].colorspace == uc2const.IMAGE_LAB

    @verify_call
    def can_be_gray(self, doc=None):
        if self.is_selection(doc):
            objs = doc.selection.objs
            if len(objs) == 1 and objs[0].is_pixmap:
                return not objs[0].colorspace == uc2const.IMAGE_GRAY

    @verify_call
    def can_be_bw(self, doc=None):
        if self.is_selection(doc):
            objs = doc.selection.objs
            if len(objs) == 1 and objs[0].is_pixmap:
                return not objs[0].colorspace == uc2const.IMAGE_MONO

    @verify_call
    def can_be_combined(self, doc=None):
        if self.is_selection(doc) and len(doc.selection.objs) > 1:
            return all([obj.is_primitive and not obj.is_pixmap for obj in doc.selection.objs])

    @verify_call
    def can_be_breaked(self, doc=None):
        if self.is_selection(doc) and len(doc.selection.objs) == 1:
            obj = doc.selection.objs[0]
            return obj.is_curve and len(obj.paths) > 1

    @verify_call
    def can_be_curve(self, doc=None):
        if self.is_selection(doc):
            for obj in doc.selection.objs:
                if obj.is_primitive and not obj.is_curve and not obj.is_pixmap:
                    return True

    @verify_call
    def is_stroke(self, doc=None):
        if self.is_selection(doc):
            for obj in doc.selection.objs:
                if obj.is_primitive and not obj.is_pixmap and obj.style[1] and obj.style[1][1]:
                    return True

    @verify_call
    def can_be_grouped(self, doc=None):
        if self.is_selection(doc):
            return len(doc.selection.objs) > 1

    @verify_call
    def can_be_ungrouped(self, doc=None):
        if self.is_selection(doc) and len(doc.selection.objs) == 1:
            return doc.selection.objs[0].is_group

    @verify_call
    def can_be_ungrouped_all(self, doc=None):
        if self.is_selection(doc):
            for obj in doc.selection.objs:
                if obj.is_group:
                    return True

    @verify_call
    def can_be_lower(self, doc=None):
        if self.is_selection(doc) and len(doc.selection.objs) == 1:
            obj = doc.selection.objs[0]
            return bool(obj.parent.childs.index(obj))

    @verify_call
    def can_be_raised(self, doc=None):
        if self.is_selection(doc) and len(doc.selection.objs) == 1:
            obj = doc.selection.objs[0]
            return obj.parent.childs.index(obj) < len(obj.parent.childs) - 1

    @verify_call
    def can_be_straighten_text(self, doc=None):
        if self.is_selection(doc) and len(doc.selection.objs) == 1:
            obj = doc.selection.objs[0]
            if obj.is_text and obj.trafos:
                return True
        elif doc.canvas.mode in (modes.TEXT_EDIT_MODE, modes.TEXT_EDITOR_MODE):
            if doc.canvas.controller.target.trafos:
                return True

    @verify_call
    def can_be_markup_cleared(self, doc=None):
        if self.is_selection(doc) and len(doc.selection.objs) == 1:
            obj = doc.selection.objs[0]
            if obj.is_text and obj.markup:
                return True
        elif doc.canvas.mode in (modes.TEXT_EDIT_MODE, modes.TEXT_EDITOR_MODE):
            if doc.canvas.controller.target.markup:
                return True
