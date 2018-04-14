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


from sk1 import modes
from uc2 import uc2const


class AppInspector:
    def __init__(self, app):
        self.app = app
        self.mw = None

    def update(self):
        self.mw = self.app.mw

    def is_doc(self):
        return not self.app.docs == []

    def is_not_doc(self):
        return self.app.docs == []

    def is_others(self):
        return len(self.app.docs) > 1

    def is_doc_saved(self, doc=None):
        if doc:
            return doc.saved
        elif self.app.current_doc:
            return self.app.current_doc.saved
        else:
            return True

    def is_doc_not_saved(self, doc=None):
        return not self.is_doc_saved(doc)

    def is_any_doc_not_saved(self):
        if self.app.docs:
            for doc in self.app.docs:
                if not doc.saved:
                    return True
        return False

    def is_mode(self, *args):
        if self.is_not_doc():
            return False
        if self.app.current_doc.canvas.mode in args:
            return True
        return False

    def is_file_history(self):
        return self.app.history.is_history()

    def is_undo(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        if doc.api.undo:
            return True
        return False

    def is_redo(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        if doc.api.redo:
            return True
        return False

    def is_history(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        if self.is_undo(doc) or self.is_redo(doc):
            return True
        return False

    def is_selection(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        elif doc.selection is None:
            return False
        elif doc.selection.objs:
            return True
        return False

    def is_obj_selection(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        elif doc.selection is None:
            return False
        elif doc.canvas.mode == modes.TEXT_EDIT_MODE:
            return doc.canvas.controller.is_selected()
        elif doc.selection.objs:
            return True
        return False

    def is_text_selection(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        elif doc.selection is None:
            return False
        elif doc.canvas.mode == modes.TEXT_EDIT_MODE:
            return doc.canvas.controller.is_selected()
        return False

    def is_selected_node(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return len(doc.canvas.controller.selected_nodes) > 0
        return False

    def can_be_selected(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        check = doc.canvas.mode != modes.BEZIER_EDITOR_MODE
        if doc.canvas.mode in modes.EDIT_MODES and check:
            return False
        return doc.selection.can_be_any_selected()

    def can_be_deleted(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return self.is_selected_node(doc)
        elif doc.canvas.mode == modes.TEXT_EDIT_MODE:
            return True
        return self.is_selection(doc)

    def can_be_selected_all_nodes(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            sel_num = len(doc.canvas.controller.selected_nodes)
            all_num = doc.canvas.controller.count_all_nodes()
            return sel_num < all_num
        return False

    def can_be_reversed_paths(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return True
        return False

    def is_subpath_selected(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return doc.canvas.controller.is_subpath_selected()
        return False

    def can_be_deleted_node(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return self.is_selected_node(doc)
        return False

    def can_be_added_node(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return doc.canvas.controller.new_node is not None
        return False

    def can_be_added_seg(self, doc=None):
        return self.can_be_joined_nodes(doc)

    def can_be_deleted_seg(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return doc.canvas.controller.can_be_deleted_seg()
        return False

    def can_be_joined_nodes(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return doc.canvas.controller.can_be_joined_nodes()
        return False

    def can_be_splited_nodes(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return doc.canvas.controller.can_be_splited_nodes()
        return False

    def can_be_seg_line(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return doc.canvas.controller.can_be_line()
        return False

    def can_be_seg_curve(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return doc.canvas.controller.can_be_curve()
        return False

    def can_be_node_cusp(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return doc.canvas.controller.can_be_cusp()
        return False

    def can_be_node_smooth(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return doc.canvas.controller.can_be_smooth()
        return False

    def can_be_node_symmetrical(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        if doc.canvas.mode == modes.BEZIER_EDITOR_MODE:
            return doc.canvas.controller.can_be_symmetrical()
        return False

    def is_clipboard(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        if doc.canvas.mode == modes.TEXT_EDIT_MODE:
            return True
        elif self.app.clipboard.contents:
            return True
        return False

    def is_draft_view(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        return self.app.current_doc.canvas.draft_view

    def is_stroke_view(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        return self.app.current_doc.canvas.stroke_view

    def is_guides_visible(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        methods = self.app.current_doc.methods
        guide_layer = methods.get_guide_layer()
        if guide_layer.properties[0]:
            return True
        return False

    def is_grid_visible(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        methods = self.app.current_doc.methods
        grid_layer = methods.get_grid_layer()
        if grid_layer.properties[0]:
            return True
        return False

    def is_draw_page_border(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        return self.app.current_doc.methods.get_page_border()

    def is_show_snapping(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        return self.app.current_doc.canvas.show_snapping

    def is_snap_to_grid(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        return self.app.current_doc.snap.snap_to_grid

    def is_snap_to_guides(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        return self.app.current_doc.snap.snap_to_guides

    def is_snap_to_objects(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        return self.app.current_doc.snap.snap_to_objects

    def is_snap_to_page(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        return self.app.current_doc.snap.snap_to_page

    def can_be_next_page(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        return True

    def can_be_previous_page(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        pages = doc.get_pages()
        if pages.index(doc.active_page):
            return True
        return False

    def can_goto_page(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        if len(doc.get_pages()) > 1:
            return True
        return False

    def can_delete_page(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        pages = doc.get_pages()
        if len(pages) - 1:
            return True
        return False

    def is_obj_primitive(self, obj):
        return obj.is_primitive

    def is_obj_curve(self, obj):
        return obj.is_curve

    def is_obj_rect(self, obj):
        return obj.is_rect

    def is_obj_circle(self, obj):
        return obj.is_circle

    def is_obj_polygon(self, obj):
        return obj.is_polygon

    def is_obj_text(self, obj):
        return obj.is_text

    def is_obj_pixmap(self, obj):
        return obj.is_pixmap

    def can_clear_trafo(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        elif self.is_selection(doc):
            objs = doc.selection.objs
            ret = False
            for obj in objs:
                if self.is_obj_primitive(obj):
                    if not obj.trafo == [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]:
                        ret = True
                        break
            return ret
        return False

    def is_container_selected(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        elif self.is_selection(doc):
            objs = doc.selection.objs
            if len(objs) == 1 and objs[0].is_container:
                return True
        return False

    def is_pixmap_selected(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        elif self.is_selection(doc):
            objs = doc.selection.objs
            if len(objs) == 1 and objs[0].is_pixmap:
                return True
        return False

    def is_pixmap_alpha(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        elif self.is_selection(doc):
            objs = doc.selection.objs
            if len(objs) == 1 and objs[0].is_pixmap:
                if objs[0].alpha_channel:
                    return True
        return False

    def can_be_cmyk(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        elif self.is_selection(doc):
            objs = doc.selection.objs
            if len(objs) == 1 and objs[0].is_pixmap:
                if not objs[0].colorspace == uc2const.IMAGE_CMYK:
                    return True
        return False

    def can_be_rgb(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        elif self.is_selection(doc):
            objs = doc.selection.objs
            if len(objs) == 1 and objs[0].is_pixmap:
                if not objs[0].colorspace == uc2const.IMAGE_RGB:
                    return True
        return False

    def can_be_lab(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        elif self.is_selection(doc):
            objs = doc.selection.objs
            if len(objs) == 1 and objs[0].is_pixmap:
                if not objs[0].colorspace == uc2const.IMAGE_LAB:
                    return True
        return False

    def can_be_gray(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        elif self.is_selection(doc):
            objs = doc.selection.objs
            if len(objs) == 1 and objs[0].is_pixmap:
                if not objs[0].colorspace == uc2const.IMAGE_GRAY:
                    return True
        return False

    def can_be_bw(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        elif self.is_selection(doc):
            objs = doc.selection.objs
            if len(objs) == 1 and objs[0].is_pixmap:
                if not objs[0].colorspace == uc2const.IMAGE_MONO:
                    return True
        return False

    def can_be_combined(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        elif self.is_selection(doc):
            result = True
            objs = doc.selection.objs
            if len(objs) < 2:
                return False
            for obj in objs:
                if not obj.is_primitive or obj.is_pixmap:
                    result = False
                    break
            return result
        else:
            return False

    def can_be_breaked(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        elif self.is_selection(doc):
            result = False
            objs = doc.selection.objs
            if len(objs) == 1 and objs[0].is_curve:
                if len(objs[0].paths) > 1:
                    result = True
            return result
        else:
            return False

    def can_be_curve(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        elif self.is_selection(doc):
            result = False
            for obj in doc.selection.objs:
                if obj.is_primitive and not obj.is_curve and not obj.is_pixmap:
                    result = True
                    break
            return result
        else:
            return False

    def is_stroke(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        elif self.is_selection(doc):
            result = False
            for obj in doc.selection.objs:
                if obj.is_primitive and not obj.is_pixmap:
                    if obj.style[1] and obj.style[1][1]:
                        result = True
                        break
            return result
        else:
            return False

    def can_be_grouped(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        elif self.is_selection(doc):
            result = False
            if len(doc.selection.objs) > 1:
                result = True
            return result
        else:
            return False

    def can_be_ungrouped(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        elif self.is_selection(doc) and len(doc.selection.objs) == 1:
            result = False
            if doc.selection.objs[0].is_group:
                result = True
            return result
        else:
            return False

    def can_be_ungrouped_all(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        elif self.is_selection(doc):
            result = False
            for obj in doc.selection.objs:
                if obj.is_group:
                    result = True
                    break
            return result
        else:
            return False

    def can_be_lower(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        elif self.is_selection(doc):
            objs = doc.selection.objs
            if len(objs) == 1:
                if objs[0].parent.childs.index(objs[0]):
                    return True
        return False

    def can_be_raised(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        elif self.is_selection(doc):
            objs = doc.selection.objs
            if len(objs) == 1:
                obj = objs[0]
                parent = objs[0].parent
                if parent.childs.index(obj) < len(parent.childs) - 1:
                    return True
        return False

    def can_be_straighten_text(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        elif self.is_selection(doc):
            objs = doc.selection.objs
            if len(objs) == 1:
                obj = objs[0]
                if obj.is_text and obj.trafos:
                    return True
        elif doc.canvas.mode in (modes.TEXT_EDIT_MODE, modes.TEXT_EDITOR_MODE):
            if doc.canvas.controller.target.trafos:
                return True
        return False

    def can_be_markup_cleared(self, doc=None):
        doc = doc or self.app.current_doc
        if doc is None:
            return False
        elif self.is_selection(doc):
            objs = doc.selection.objs
            if len(objs) == 1:
                obj = objs[0]
                if obj.is_text and obj.markup:
                    return True
        elif doc.canvas.mode in (modes.TEXT_EDIT_MODE, modes.TEXT_EDITOR_MODE):
            if doc.canvas.controller.target.markup:
                return True
        return False
