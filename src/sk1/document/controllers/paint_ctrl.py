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
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import math
from creators import AbstractCreator
from sk1 import modes, config
from uc2 import sk2const
from uc2.libgeom import apply_trafo_to_paths, is_point_in_rect2
from uc2.libgeom import contra_point, bezier_base_point, midpoint
from uc2.libgeom import get_point_angle, distance, add_points


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
        if self.point:
            point = self.points[-1] if self.points else self.path[0]
            self.point = self.canvas.point_doc_to_win(point)
        self.on_timer()

    def mouse_down(self, event):
        if not self.draw:
            self.draw = True
            self.clear_data()
        self.point, self.doc_point = self._calc_points(event)
        self.add_point(self.point, self.doc_point)
        self.create = True
        self.init_timer()

    def mouse_up(self, event):
        if self.draw:
            self.create = False
            self.ctrl_mask = event.is_ctrl()
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

    def wheel(self, event):
        self.init_timer()
        AbstractCreator.wheel(self, event)
        self.restore()

    def repaint(self):
        if self.timer_callback is not None:
            self.timer_callback()

    def repaint_draw(self):
        if self.path[0] or self.paths:
            paths = self.canvas.paths_doc_to_win(self.paths)
            if self.cursor:
                cursor = self.snap.snap_point(self.cursor)[1]
            else:
                cursor = []
            if not self.path[0]:
                cursor = []
            self.canvas.renderer.paint_curve(paths, cursor)
        return True

    def continuous_draw(self):
        if self.create and self.cursor:
            self.point, self.doc_point = self.snap.snap_point(self.cursor)[1:]
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

        if start and cursor:
            if ctrl:  # restrict movement to horizontal or vertical
                # calculate the limiting angle
                angle = get_point_angle(cursor, start)
                fixed_angle = math.pi * 15.0 / 180.0  # TODO: configure 15
                angle = angle // fixed_angle * fixed_angle

                r = distance(cursor, start)
                # calculate point on circle
                x = r * math.cos(angle)
                y = r * math.sin(angle)
                cursor = add_points([x, y], start)
        return self.snap.snap_point(cursor)[1:]


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
        p = event.get_point()
        self.curve_point, self.curve_point_doc = self.snap.snap_point(p)[1:]
        # self.control_point2 = []
        # self.control_point2_doc = []
        self.control_point2 = self.curve_point
        self.control_point2_doc = self.curve_point_doc
        self.create = True
        self.init_timer()

    def mouse_up(self, event):
        if not self.draw:
            return
        self.create = False
        self.ctrl_mask = False
        self.alt_mask = False
        p = event.get_point()
        p1, p2 = self.snap.snap_point(p)[1:]
        self.control_point2, self.control_point2_doc = p1, p2
        self.ctrl_mask = event.is_ctrl()
        self.alt_mask = event.is_alt()
        if self.path[0]:
            if self.alt_mask:
                p = event.get_point()
                self.point, self.point_doc = self.snap.snap_point(p)[1:]
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
                p = event.get_point()
                self.cursor = [] + p
                p1, p2 = self.snap.snap_point(p)[1:]
                self.curve_point, self.curve_point_doc = p1, p2
        else:
            p = event.get_point()
            self.point, self.point_doc = self.snap.snap_point(p)[1:]
            self.add_point(self.point, self.point_doc)
            self.control_point0 = [] + self.point
            self.control_point0_doc = [] + self.point_doc
        self.on_timer()

    def mouse_move(self, event):
        if self.draw:
            self.cursor = event.get_point()
            snapped = self.snap.snap_point(self.cursor)[1:]
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

    def wheel(self, event):
        self.cursor = event.get_point()
        PolyLineCreator.wheel(self, event)

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
            if self.control_point0:
                if not self.control_point2_doc:
                    return True
                self.control_point1_doc = contra_point(self.control_point2_doc,
                                                       self.curve_point_doc)
                path = [self.point_doc, [self.control_point0_doc,
                                         self.control_point1_doc,
                                         self.curve_point_doc], 0]
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
