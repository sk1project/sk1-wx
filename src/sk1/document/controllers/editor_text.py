# -*- coding: utf-8 -*-
#
#  Copyright (C) 2016 by Igor E. Novikov
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

from copy import deepcopy

from uc2 import libgeom

from sk1 import _, modes, config, events
from generic import AbstractController


class TextEditor(AbstractController):
    mode = modes.TEXT_EDITOR_MODE
    target = None
    selected_obj = None

    points = []
    selected_points = []
    spoint = None
    trafos = {}
    trafo_mode = modes.ET_MOVING_MODE
    move_flag = False
    initial_start = None

    def __init__(self, canvas, presenter):
        AbstractController.__init__(self, canvas, presenter)

    def start_(self):
        self.snap = self.presenter.snap
        self.target = self.selection.objs[0]
        self.selected_obj = None
        self.api.set_mode()
        self.update_points()
        self.selection.clear()
        self.trafo_mode = modes.ET_MOVING_MODE
        msg = _('Text in shaping')
        events.emit(events.APP_STATUS, msg)

    def stop_(self):
        if not self.selected_obj:
            self.selection.set([self.target, ])
        else:
            self.selection.set([self.selected_obj, ])
        self.target = None
        self.selected_obj = None
        self.points = []

    def escape_pressed(self):
        self.canvas.set_mode()

    def update_points(self):
        cv = self.canvas
        self.points = []
        index = 0
        for item in self.target.cache_layout_data:
            if index < len(self.target.cache_cpath) and \
                    self.target.cache_cpath[index]:
                x = item[0]
                y = item[4]
                trafo = self.target.trafo
                flag = False
                if index in self.target.trafos.keys():
                    trafo = self.target.trafos[index]
                    flag = True
                self.points.append(ControlPoint(cv, index, [x, y], trafo, flag))
            index += 1

    def set_mode(self, mode):
        if mode in modes.ET_MODES and not mode == self.trafo_mode:
            pass

    # ----- REPAINT
    def repaint(self):
        bbox = self.target.cache_layout_bbox
        self.canvas.renderer.draw_text_frame(bbox, self.target.trafo)
        for item in self.points:
            selected = False
            if item in self.selected_points:
                selected = True
            item.repaint(selected)

    def repaint_frame(self):
        self.canvas.renderer.cdc_draw_frame(self.start, self.end, True)

    def on_timer(self):
        if self.draw:
            self.repaint_frame()

    # ----- MOUSE CONTROLLING

    def mouse_down(self, event):
        self.timer.stop()
        self.initial_start = []
        self.start = []
        self.end = []
        self.draw = False
        self.move_flag = False
        self.start = event.get_point()
        self.initial_start = event.get_point()
        self.spoint = self.select_point_by_click(self.start)
        if not self.spoint:
            self.timer.start()

    def mouse_move(self, event):
        if not self.start:
            return
        if not self.move_flag and not self.spoint:
            self.end = event.get_point()
            self.draw = True
        elif self.move_flag:
            self.end = event.get_point()
            trafo = self.get_trafo(self.start, self.end,
                                   event.is_ctrl(), event.is_shift())
            self.apply_trafo_to_selected(trafo)
            self.start = self.end
            self.canvas.selection_redraw()
        elif self.spoint:
            if self.spoint not in self.selected_points:
                self.set_selected_points([self.spoint, ])
            self.move_flag = True
            self.trafos = deepcopy(self.target.trafos)
            self.canvas.selection_redraw()

    def mouse_up(self, event):
        self.timer.stop()
        self.end = event.get_point()
        if self.draw:
            self.draw = False
            points = self.select_points_by_bbox(self.start + self.end)
            self.set_selected_points(points, event.is_shift())
            self.canvas.selection_redraw()
        elif self.move_flag:
            self.move_flag = False
            trafo = self.get_trafo(self.start, self.end,
                                   event.is_ctrl(), event.is_shift())
            self.apply_trafo_to_selected(trafo, True)
            self.canvas.selection_redraw()
        elif self.spoint:
            self.set_selected_points([self.spoint, ], event.is_shift())
            self.canvas.selection_redraw()
        else:
            objs = self.canvas.pick_at_point(self.end)
            if objs and objs[0].is_primitive and not objs[0].is_pixmap:
                self.selected_obj = objs[0]
                self.start = []
                self.canvas.set_mode(modes.SHAPER_MODE)
                return
            else:
                self.set_selected_points([])
                self.canvas.selection_redraw()
        self.start = []

    # ----- POINT PROCESSING

    def set_selected_points(self, points, add=False):
        if add:
            for item in points:
                if item not in self.selected_points:
                    self.selected_points.append(item)
                else:
                    self.selected_points.remove(item)
        else:
            self.selected_points = points

    def select_points_by_bbox(self, bbox):
        ret = []
        bbox = libgeom.normalize_bbox(bbox)
        for item in self.points:
            if libgeom.is_point_in_bbox(item.get_screen_point(), bbox):
                ret.append(item)
        return ret

    def select_point_by_click(self, point):
        for item in self.points:
            ipoint = item.get_screen_point()
            bbox = libgeom.bbox_for_point(ipoint, config.point_sensitivity_size)
            if libgeom.is_point_in_bbox(point, bbox):
                return item
        return None

    def get_trafo(self, start, end, ctrl=False, shift=False):
        trafo = [1.0, 0.0, 0.0, 1.0]
        dchange = [0.0, 0.0]
        dstart = self.canvas.win_to_doc(start)
        dend = self.canvas.win_to_doc(end)
        if self.trafo_mode == modes.ET_MOVING_MODE:
            dchange = libgeom.sub_points(dend, dstart)
            if ctrl:
                change = libgeom.sub_points(end, self.initial_start)
                if abs(change[0]) > abs(change[1]):
                    dchange = [dchange[0], 0.0]
                else:
                    dchange = [0.0, dchange[1]]
        return trafo + dchange

    def apply_trafo_to_selected(self, trafo, final=False):
        trafos = deepcopy(self.target.trafos)
        for item in self.selected_points:
            index = item.index
            if index in trafos.keys():
                trafos[index] = libgeom.multiply_trafo(trafos[index], trafo)
            else:
                trafos[index] = libgeom.multiply_trafo(self.target.trafo, trafo)
            item.apply_trafo(trafo)
        if not final:
            self.api.set_temp_text_trafos(self.target, trafos)
        else:
            self.api.set_text_trafos(self.target, trafos, self.trafos)
            self.trafos = {}


class ControlPoint:
    canvas = None
    index = 0
    point = []
    trafo = []
    modified = False

    def __init__(self, canvas, index, point, trafo, modified=False):
        self.canvas = canvas
        self.index = index
        self.point = point
        self.trafo = trafo
        self.modified = modified

    def apply_trafo(self, trafo):
        self.trafo = libgeom.multiply_trafo(self.trafo, trafo)

    def get_point(self):
        return libgeom.apply_trafo_to_point(self.point, self.trafo)

    def get_screen_point(self):
        return self.canvas.point_doc_to_win(self.get_point())

    def repaint(self, selected=False):
        self.canvas.renderer.draw_text_point(self.get_screen_point(), selected)
