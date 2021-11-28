# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013 by Ihor E. Novikov
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
from uc2 import sk2const
from uc2.libgeom import (
    apply_trafo_to_paths,
    bezier_base_point,
    contra_point,
    is_point_in_rect2,
    midpoint,
    round_angle_point,
)

from .creators import AbstractCreator


class PolyLineCreator(AbstractCreator):
    mode = modes.LINE_MODE

    # drawing data
    paths = []
    path = [[], [], sk2const.CURVE_OPENED]
    points = []
    cursor = []
    obj = None

    # Actual event point
    point = []
    doc_point = []
    ctrl_mask = False
    alt_mask = False
    shift_mask = False

    # Drawing timer to avoid repainting overhead
    timer = None
    timer_callback = None

    # Flags
    draw = False  # entering into drawing mode
    create = False  # entering into continuous drawing mode

    def __init__(self, canvas, presenter):
        AbstractCreator.__init__(self, canvas, presenter)

    def escape_pressed(self):
        if self.draw:
            self.mouse_double_click(None)
        else:
            self.canvas.set_mode()

    def start_(self):
        self.snap = self.presenter.snap
        self.init_flags()
        self.init_data()
        self.init_timer()
        self.update_from_selection()
        self.presenter.selection.clear()
        self.on_timer()

    def stop_(self):
        if self.obj:
            self.presenter.selection.set([self.obj])
        self.init_flags()
        self.init_data()
        self.init_timer()
        self.canvas.renderer.paint_curve([])
        self.on_timer()

    def standby(self):
        self.init_timer()
        self.cursor = []
        self.on_timer()

    def restore(self):
        if self.path:
            point = self.points[-1] if self.points else self.path[0]
            self.point = self.canvas.point_doc_to_win(point)
        self.on_timer()

    def mouse_down(self, event):
        if not self.draw:
            self.draw = True
            self.clear_data()
        self.set_key_mask(event)
        self.point, self.doc_point = self._calc_points(event)
        self.add_point(self.point, self.doc_point)
        self.create = True
        self.init_timer()

    def mouse_up(self, event):
        if self.draw:
            self.set_key_mask(event)
            self.create = False
            self.cursor = self._calc_points(event)[0]
            self.on_timer()

    def mouse_double_click(self, event):
        if self.ctrl_mask:
            self.draw = False
            self.release_curve(False)
        else:
            self.release_curve()

    def mouse_move(self, event):
        if self.draw:
            self.set_key_mask(event)
            self.cursor = self._calc_points(event)[0]
            if self.create:
                self.set_drawing_timer()
            else:
                self.set_repaint_timer()
        else:
            self.init_timer()
            self.counter += 1
            if self.counter > 5:
                self.counter = 0
                point = event.get_point()
                dpoint = self.canvas.win_to_doc(point)
                if self.selection.is_point_over_marker(dpoint):
                    mark = self.selection.is_point_over_marker(dpoint)[0]
                    self.canvas.resize_marker = mark
                    self.cursor = []
                    self.canvas.set_temp_mode(modes.RESIZE_MODE)

    def repaint(self):
        if self.timer_callback is not None:
            self.timer_callback()

    def repaint_draw(self):
        if self.path[0] or self.paths:
            paths = self.canvas.paths_doc_to_win(self.paths)
            cursor = self.cursor
            self.canvas.renderer.paint_curve(paths, cursor)
        return True

    def continuous_draw(self):
        if self.create and self.cursor:
            self.point, self.doc_point = self._snap(self.cursor)
            self.add_point(self.point, self.doc_point)
        return self.repaint_draw()

    def init_timer(self):
        self.timer.stop()
        self.timer_callback = self.repaint_draw

    def on_timer(self):
        self.canvas.selection_redraw()

    def set_repaint_timer(self):
        if not self.timer.is_running():
            self.timer_callback = self.repaint_draw
            self.timer.start()

    def set_drawing_timer(self):
        if not self.timer.is_running():
            self.timer_callback = self.continuous_draw
            self.timer.start()

    def init_data(self):
        self.cursor = []
        self.paths = []
        self.points = []
        self.path = [[], [], sk2const.CURVE_OPENED]
        self.point = []
        self.doc_point = []
        self.obj = None
        self.timer_callback = None

    def clear_data(self):
        self.cursor = []
        self.points = []
        self.path = [[], [], sk2const.CURVE_OPENED]
        self.point = []
        self.doc_point = []

    def init_flags(self):
        self.create = False
        self.draw = False

    def set_key_mask(self, event):
        self.ctrl_mask = event.is_ctrl()
        self.alt_mask = event.is_alt()
        self.shift_mask = event.is_shift()

    def update_from_selection(self):
        sel_objs = self.selection.objs
        if len(sel_objs) == 1 and sel_objs[0].is_curve and self.obj is None:
            self.update_from_obj(sel_objs[0])

    def update_from_obj(self, obj):
        self.obj = obj
        self.paths = apply_trafo_to_paths(self.obj.paths, self.obj.trafo)
        path = self.paths[-1]
        if path[-1] == sk2const.CURVE_OPENED:
            self.path = path
            self.points = self.path[1]
            paths = self.canvas.paths_doc_to_win(self.paths)
            self.canvas.renderer.paint_curve(paths)
        else:
            paths = self.canvas.paths_doc_to_win(self.paths)
            self.canvas.renderer.paint_curve(paths)
        self.draw = True

    def add_point(self, point, doc_point):
        subpoint = bezier_base_point(point)
        if self.path[0]:
            w = h = config.curve_point_sensitivity_size
            start = self.canvas.point_doc_to_win(self.path[0])
            if self.points:
                p = self.canvas.point_doc_to_win(self.points[-1])
                last = bezier_base_point(p)
                if is_point_in_rect2(subpoint, start, w, h) and len(
                        self.points) > 1:
                    self.path[2] = sk2const.CURVE_CLOSED
                    if len(point) == 2:
                        self.points.append([] + self.path[0])
                    else:
                        p = doc_point
                        self.points.append(
                            [p[0], p[1], [] + self.path[0], p[3]])
                    if not self.ctrl_mask:
                        self.release_curve()
                    else:
                        self.draw = False
                        self.release_curve(False)
                    self.on_timer()
                elif not is_point_in_rect2(subpoint, last, w, h):
                    self.points.append(doc_point)
                    self.path[1] = self.points
            else:
                if not is_point_in_rect2(subpoint, start, w, h):
                    self.points.append(doc_point)
                    self.path[1] = self.points
        else:
            self.path[0] = doc_point
            self.paths.append(self.path)

    def release_curve(self, stop=True):
        if self.points:
            self.cursor = []
            flag = config.curve_autoclose_flag
            if flag and self.path[2] == sk2const.CURVE_OPENED:
                self.path[2] = sk2const.CURVE_CLOSED
                self.points.append([] + self.path[0])
            paths = self.paths
            obj = self.obj
            if stop:
                self.stop_()
            if obj is None:
                obj = self.api.create_curve(paths)
            else:
                self.api.update_curve(obj, paths)
            if not stop:
                self.obj = obj

    def _calc_points(self, event):
        start = self.point
        cursor = event.get_point()
        ctrl = event.is_ctrl()
        shift = event.is_shift()
        if not shift and start and cursor:
            if ctrl:  # restrict movement to horizontal or vertical
                fixed_angle = config.curve_fixed_angle
                cursor = round_angle_point(start, cursor, fixed_angle)
        return self._snap(cursor)

    def _snap(self, point):
        if self.check_snap and not self.shift_mask:
            snapped = self.snap.snap_point(point)[1:]
        else:
            snapped = [point, self.canvas.win_to_doc(point)]
        return snapped


class PathsCreator(PolyLineCreator):
    mode = modes.CURVE_MODE
    curve_point = []
    control_point0 = []
    control_point1 = []
    control_point2 = []
    curve_point_doc = []
    control_point0_doc = []
    control_point1_doc = []
    control_point2_doc = []
    point_doc = []

    def __init__(self, canvas, presenter):
        PolyLineCreator.__init__(self, canvas, presenter)

    def standby(self):
        self.init_timer()
        self.cursor = []
        self.on_timer()

    def restore(self):
        self.point = self.canvas.point_doc_to_win(self.point_doc)
        self.curve_point = self.canvas.point_doc_to_win(self.curve_point_doc)
        self.control_point0 = self.canvas.point_doc_to_win(
            self.control_point0_doc)
        self.control_point1 = self.canvas.point_doc_to_win(
            self.control_point1_doc)
        self.control_point2 = self.canvas.point_doc_to_win(
            self.control_point2_doc)
        self.on_timer()

    def update_from_obj(self, obj):
        self.obj = obj
        self.paths = apply_trafo_to_paths(self.obj.paths, self.obj.trafo)
        path = self.paths[-1]
        if path[-1] == sk2const.CURVE_OPENED:
            self.path = path
            self.points = self.path[1]
            paths = self.canvas.paths_doc_to_win(self.paths)
            self.canvas.renderer.paint_curve(paths)
            last = bezier_base_point(self.points[-1])
            self.control_point0 = self.canvas.point_doc_to_win(last)
            self.control_point0_doc = [] + last
            self.point = [] + self.control_point0
            self.point_doc = [] + last
            self.control_point2 = [] + self.control_point0
            self.control_point2_doc = [] + last
            self.curve_point = [] + self.control_point0
            self.curve_point_doc = [] + last
        else:
            paths = self.canvas.paths_doc_to_win(self.paths)
            self.canvas.renderer.paint_curve(paths)
        self.draw = True

    def mouse_down(self, event):
        if not self.draw:
            self.draw = True
            self.clear_data()
        self.curve_point, self.curve_point_doc = self._calc_points(event)
        self.control_point2 = [] + self.curve_point
        self.control_point2_doc = [] + self.curve_point_doc
        self.create = True
        self.init_timer()

    def mouse_up(self, event):
        if not self.draw:
            return
        self.create = False
        self.set_key_mask(event)
        self.control_point2, self.control_point2_doc = self._calc_points(event)
        self.cursor = [] + self.control_point2
        if self.path[0]:
            if self.alt_mask:
                self.point, self.point_doc = self._calc_points(event)
                self.add_point([] + self.point, [] + self.point_doc)
                self.control_point0 = [] + self.point
                self.cursor = event.get_point()
                self.curve_point = [] + self.point
            elif self.control_point2:
                self.point = [] + self.curve_point
                self.point_doc = [] + self.curve_point_doc
                self.control_point1 = contra_point(self.control_point2,
                                                   self.curve_point)
                self.control_point1_doc = contra_point(
                    self.control_point2_doc,
                    self.curve_point_doc)

                node_type = sk2const.NODE_SYMMETRICAL
                if len(self.points):
                    bp_doc = bezier_base_point(self.points[-1])
                else:
                    bp_doc = self.path[0]
                if self.control_point0_doc == bp_doc and \
                        self.control_point1_doc == self.curve_point_doc:
                    node_type = sk2const.NODE_CUSP
                    p0d = midpoint(bp_doc, self.curve_point_doc, 1.0 / 3.0)
                    self.control_point0_doc = p0d
                    p1d = midpoint(bp_doc, self.curve_point_doc, 2.0 / 3.0)
                    self.control_point1_doc = p1d
                    self.control_point0 = self.canvas.doc_to_win(p0d)
                    self.control_point1 = self.canvas.doc_to_win(p1d)

                self.add_point([self.control_point0,
                                self.control_point1,
                                self.curve_point, node_type],
                               [self.control_point0_doc,
                                self.control_point1_doc,
                                self.curve_point_doc, node_type])

                self.control_point0 = [] + self.control_point2
                self.control_point0_doc = [] + self.control_point2_doc
                snapped = self._calc_points(event)
                self.cursor = [] + snapped[0]
                self.curve_point, self.curve_point_doc = snapped
        else:
            self.point, self.point_doc = self._calc_points(event)
            self.add_point(self.point, self.point_doc)
            self.control_point0 = [] + self.point
            self.control_point0_doc = [] + self.point_doc
        self.on_timer()

    def mouse_move(self, event):
        self.set_key_mask(event)
        if self.draw:
            snapped = self._calc_points(event)
            self.cursor = [] + snapped[0]
            self.control_point2, self.control_point2_doc = snapped
            if not self.create:
                self.curve_point = [] + self.control_point2
                self.curve_point_doc = [] + self.control_point2_doc
            self.set_repaint_timer()
        else:
            self.init_timer()
            self.counter += 1
            if self.counter > 5:
                self.counter = 0
                point = event.get_point()
                dpoint = self.canvas.win_to_doc(point)
                if self.selection.is_point_over_marker(dpoint):
                    mark = self.selection.is_point_over_marker(dpoint)[0]
                    self.canvas.resize_marker = mark
                    self.cursor = []
                    self.canvas.set_temp_mode(modes.RESIZE_MODE)

    def repaint_draw(self):
        if self.path[0] or self.paths:
            paths = self.canvas.paths_doc_to_win(self.paths)
            cursor = self.cursor
            if not self.path[0]:
                cursor = []
            elif cursor and not self.create:
                snapped = self.snap.snap_point(cursor)[1:]
                self.curve_point, self.curve_point_doc = snapped
            path = []
            if self.control_point0 and not self.alt_mask:
                if not self.control_point2_doc:
                    return True
                self.control_point1_doc = contra_point(self.control_point2_doc,
                                                       self.curve_point_doc)
                path = [self.point_doc, [self.control_point0_doc,
                                         self.control_point1_doc,
                                         self.curve_point_doc],
                        sk2const.CURVE_OPENED]
                path = self.canvas.paths_doc_to_win([path, ])[0]
            cpoint = []
            if self.create:
                cpoint = self.canvas.doc_to_win(self.control_point2_doc)
            self.canvas.renderer.paint_curve(paths, cursor, path, cpoint)
        return True

    def init_data(self):
        PolyLineCreator.init_data(self)
        self.curve_point = []
        self.control_point0 = []
        self.control_point1 = []
        self.control_point2 = []
        self.curve_point_doc = []
        self.control_point0_doc = []
        self.control_point1_doc = []
        self.control_point2_doc = []

    def _calc_points(self, event):
        if self.curve_point != self.control_point2:
            start = self.curve_point
        else:
            start = self.point
        cursor = event.get_point()
        ctrl = event.is_ctrl()
        shift = event.is_shift()
        if not shift and start and cursor:
            if ctrl:  # restrict movement to horizontal or vertical
                fixed_angle = config.curve_fixed_angle
                cursor = round_angle_point(start, cursor, fixed_angle)
        return self._snap(cursor)
