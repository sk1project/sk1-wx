# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2015-2021 by Ihor E. Novikov
# 	Copyright (C) 2021 by Maxim S. Barabash
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
# 	along with this program.  If not, see <https://www.gnu.org/licenses/>.

from generic import AbstractController
from sk1 import _, modes, config, events
from uc2 import libgeom

H_ORIENT = ['00', '11', '20', '31']
EPSILON = 0.000001


class RectEditor(AbstractController):
    mode = modes.RECT_EDITOR_MODE
    target = None
    points = []
    midpoints = []
    selected_obj = None

    resizing = False
    res_index = 0
    orig_rect = []

    rounding = False
    rnd_index = 0
    rnd_subindex = 0
    orig_corners = []
    start = []
    stop = []
    start2 = []
    stop2 = []

    def __init__(self, canvas, presenter):
        AbstractController.__init__(self, canvas, presenter)

    def start_(self):
        self.snap = self.presenter.snap
        self.target = self.selection.objs[0]
        self.resizing = False
        self.rounding = False
        self.selected_obj = None
        self.update_points()
        self.selection.clear()
        msg = _('Rectangle in editing')
        events.emit(events.APP_STATUS, msg)

    def stop_(self):
        self.selection.set([self.target, ])
        self.target = None
        self.selected_obj = None

    def update_points(self):
        self.points = []
        self.midpoints = []
        mps = self.target.get_midpoints()
        for item in mps:
            self.midpoints.append(MidPoint(self.canvas, self.target, item))
        corner_points = self.target.get_corner_points()
        stops = self.target.get_stops()
        for index in range(4):
            if not self.target.corners[index]:
                start = corner_points[index]
                stop = stops[index][0]
                stop2 = stops[index - 1]
                if len(stop2) == 2:
                    stop2 = stop2[1]
                else:
                    stop2 = stop2[0]
                coef = self.target.corners[index]
                self.points.append(ControlPoint(self.canvas, self.target, start,
                                                stop, stop2=stop2,
                                                coef=coef, index=index))
            elif self.target.corners[index] == 1.0:
                start = corner_points[index]
                stop = stops[index - 1]
                if len(stop) == 2:
                    stop = stop[1]
                    coef = self.target.corners[index]
                    self.points.append(ControlPoint(self.canvas, self.target,
                                                    start, stop, coef=coef,
                                                    index=index))
                elif not self.target.corners[index - 1] == 1.0:
                    stop = stop[0]
                    coef = self.target.corners[index]
                    self.points.append(ControlPoint(self.canvas, self.target,
                                                    start, stop, coef=coef,
                                                    index=index))

                stop = stops[index][0]
                start2 = []
                if len(stops[index]) == 1 and \
                        self.target.corners[index - 3] == 1.0:
                    start2 = corner_points[index - 3]
                coef = self.target.corners[index]
                self.points.append(ControlPoint(self.canvas, self.target, start,
                                                stop, start2=start2,
                                                coef=coef, index=index,
                                                subindex=1))
            else:
                start = corner_points[index]
                stop = stops[index - 1]
                if len(stop) == 2:
                    stop = stop[1]
                else:
                    stop = stop[0]
                coef = self.target.corners[index]
                self.points.append(ControlPoint(self.canvas, self.target, start,
                                                stop, coef=coef, index=index))

                stop = stops[index][0]
                self.points.append(ControlPoint(self.canvas, self.target, start,
                                                stop, coef=coef, index=index,
                                                subindex=1))
        msg = _('Rectangle in editing')
        events.emit(events.APP_STATUS, msg)

    def stop_(self):
        self.selection.set([self.target, ])
        self.target = None
        self.selected_obj = None

    def escape_pressed(self):
        self.canvas.set_mode()

    # ----- REPAINT

    def repaint(self):
        x0, y0, x1, y1 = self.target.cache_bbox
        p0 = self.canvas.point_doc_to_win([x0, y0])
        p1 = self.canvas.point_doc_to_win([x1, y1])
        self.canvas.renderer.draw_frame(p0, p1)
        for item in self.midpoints:
            item.repaint()
        for item in self.points:
            item.repaint()

    # ----- CHANGE APPLY
    def apply_resizing(self, point, final=False):
        wpoint = self.canvas.point_win_to_doc(point)
        invtrafo = libgeom.invert_trafo(self.target.trafo)
        wpoint = libgeom.apply_trafo_to_point(wpoint, invtrafo)
        rect = self.target.get_rect()
        corners = [] + self.target.corners
        if self.res_index == 0:
            rect[2] -= wpoint[0] - rect[0]
            rect[0] = wpoint[0]
            if rect[2] < 0:
                self.res_index = 2
                c0, c1, c2, c3 = corners
                corners = [c3, c2, c1, c0]
        elif self.res_index == 1:
            rect[3] = wpoint[1] - rect[1]
            if rect[3] < 0:
                self.res_index = 3
                c0, c1, c2, c3 = corners
                corners = [c1, c0, c3, c2]
        elif self.res_index == 2:
            rect[2] = wpoint[0] - rect[0]
            if rect[2] < 0:
                self.res_index = 0
                c0, c1, c2, c3 = corners
                corners = [c3, c2, c1, c0]
        elif self.res_index == 3:
            rect[3] -= wpoint[1] - rect[1]
            rect[1] = wpoint[1]
            if rect[3] < 0:
                self.res_index = 1
                c0, c1, c2, c3 = corners
                corners = [c1, c0, c3, c2]
        rect = libgeom.normalize_rect(rect)
        if final:
            self.api.set_rect_final(self.target, rect, self.orig_rect)
            if not corners == self.orig_corners:
                self.api.set_rect_corners_final(corners, self.orig_corners,
                                                self.target)
                self.orig_corners = [] + self.target.corners
            self.orig_rect = self.target.get_rect()
        else:
            self.api.set_rect(self.target, rect)
            if not corners == self.target.corners:
                self.api.set_rect_corners(corners, self.target)
        self.update_points()

    def apply_rounding(self, point, final=False, inplace=False):
        wpoint = self.canvas.point_win_to_doc(point)
        invtrafo = libgeom.invert_trafo(self.target.trafo)
        wpoint = libgeom.apply_trafo_to_point(wpoint, invtrafo)
        corners = [] + self.target.corners
        name = str(self.rnd_index) + str(self.rnd_subindex)

        if self.stop2:
            val = abs(wpoint[0] - self.start[0])
            val2 = abs(wpoint[1] - self.start[1])
            start = self.start
            if val > val2:
                if self.rnd_index in (0, 2):
                    stop = self.stop2
                    res = (wpoint[0] - start[0]) / (stop[0] - start[0])
                else:
                    stop = self.stop
                    res = (wpoint[0] - start[0]) / (stop[0] - start[0])
            else:
                if self.rnd_index in (0, 2):
                    stop = self.stop
                    res = (wpoint[1] - start[1]) / (stop[1] - start[1])
                else:
                    stop = self.stop2
                    res = (wpoint[1] - start[1]) / (stop[1] - start[1])
        else:
            start = self.start
            stop = self.stop
            if name in H_ORIENT:
                res = (wpoint[0] - start[0]) / (stop[0] - start[0])
            else:
                res = (wpoint[1] - start[1]) / (stop[1] - start[1])

        res = 0.0 if res < 0.0 else res
        res = 1.0 if res > 1.0 else res

        if inplace:
            corners[self.rnd_index] = res
        else:
            corners = [res, res, res, res]
        if final:
            self.api.set_rect_corners_final(corners, self.orig_corners,
                                            self.target)
        else:
            self.api.set_rect_corners(corners, self.target)
        self.update_points()

    # ----- MOUSE CONTROLLING
    def mouse_down(self, event):
        self.resizing = False
        self.rounding = False
        self.selected_obj = None
        self.end = event.get_point()
        for item in self.points:
            if item.is_pressed(self.end):
                self.rounding = True
                self.rnd_index = item.index
                self.rnd_subindex = item.subindex
                self.orig_corners = [] + self.target.corners
                self.start = [] + item.start
                self.start2 = [] + item.start2
                self.stop = [] + item.stop
                self.stop2 = [] + item.stop2
                return
        for item in self.midpoints:
            if item.is_pressed(self.end):
                self.resizing = True
                self.res_index = self.midpoints.index(item)
                self.orig_rect = self.target.get_rect()
                self.orig_corners = [] + self.target.corners
                return
        objs = self.canvas.pick_at_point(self.end)

        if objs and not objs[0] == self.target:
            self.selected_obj = objs[0]

    def mouse_up(self, event):
        if self.resizing:
            self.resizing = False
            self.apply_resizing(self.end, True)
        elif self.rounding:
            self.rounding = False
            self.apply_rounding(self.end, True, event.is_ctrl())
        elif self.selected_obj:
            self.target = self.selected_obj
            self.canvas.set_mode(modes.SHAPER_MODE)
        self.end = []

    def mouse_move(self, event):
        self.end = event.get_point()
        is_snapping = not event.is_shift()
        if self.resizing:
            if is_snapping:
                self.end = self._snap_midpoints(self.end)
            self.apply_resizing(self.end)
        elif self.rounding:
            if is_snapping:
                self.end = self._snap_respoints(self.end)
            self.apply_rounding(self.end, inplace=event.is_ctrl())

    def mouse_double_click(self, event):
        self.canvas.set_mode()

    def _snap_respoints(self, point):
        p0 = None
        rnd_index = self.rnd_index
        rnd_subindex = self.rnd_subindex

        if self.stop2:
            for item in self.points:
                if item.is_pressed(self.end):
                    p0 = item.get_screen_point()
                    rnd_index = item.index
                    rnd_subindex = item.subindex
                    break

        if p0 is None:
            for p in self.points:
                if p.index == rnd_index and p.subindex == rnd_subindex:
                    p0 = p.get_screen_point()
                    break

        if p0:
            cp = None
            index = rnd_index - (1 - rnd_subindex)
            p1 = self.midpoints[index].get_screen_point()
            flag, wp, dp = self.snap.snap_point(p0, snap_x=False)
            self.snap.active_snap = [None, None]
            if flag:
                cp = x_intersect(p0, p1, wp[1])
            if cp:
                closest_point = project_point_to_line(point, p0, p1)
                d = libgeom.distance(cp, closest_point)
                if d < config.point_sensitivity_size * 2:
                    self.snap.active_snap = [None, dp[1]]
                    point = cp
            else:
                flag, wp, dp = self.snap.snap_point(p0, snap_y=False)
                self.snap.active_snap = [None, None]
                if flag:
                    cp = y_intersect(p0, p1, wp[0])
                if cp:
                    closest_point = project_point_to_line(point, p0, p1)
                    d = libgeom.distance(cp, closest_point)
                    if d < config.point_sensitivity_size * 2:
                        self.snap.active_snap = [dp[0], None]
                        point = cp
        return point

    def _snap_midpoints(self, point):
        p0 = None
        p1 = None
        if self.res_index == 1:
            p0 = self.midpoints[1].get_screen_point()
            p1 = self.midpoints[3].get_screen_point()
        elif self.res_index == 3:
            p0 = self.midpoints[3].get_screen_point()
            p1 = self.midpoints[1].get_screen_point()
        elif self.res_index == 2:
            p0 = self.midpoints[2].get_screen_point()
            p1 = self.midpoints[0].get_screen_point()
        elif self.res_index == 0:
            p0 = self.midpoints[0].get_screen_point()
            p1 = self.midpoints[2].get_screen_point()

        if p0 is not None:
            cp = None
            flag, wp, dp = self.snap.snap_point(p0)
            if flag and self.snap.active_snap[1] is not None:
                cp = x_intersect(p0, p1, wp[1])
            if not cp and flag and self.snap.active_snap[0] is not None:
                cp = y_intersect(p0, p1, wp[0])
            if cp:
                closest_point = project_point_to_line(point, p0, p1)
                d = libgeom.distance(cp, closest_point)
                if d < config.point_sensitivity_size * 2:
                    point = cp
            else:
                self.snap.active_snap = [None, None]
        return point


class ControlPoint:
    canvas = None
    target = None
    start = []
    stop = []
    start2 = []
    stop2 = []
    coef = 0.0
    index = 0
    subindex = 0

    def __init__(self, canvas, target, start, stop, start2=None, stop2=None,
                 coef=0.0, index=0, subindex=0):
        self.canvas = canvas
        self.target = target
        self.start = start
        self.start2 = start2 or []
        self.stop = stop
        self.stop2 = stop2 or []
        self.coef = coef
        self.index = index
        self.subindex = subindex

    def get_point(self):
        p = libgeom.midpoint(self.start, self.stop, self.coef)
        return libgeom.apply_trafo_to_point(p, self.target.trafo)

    def get_screen_point(self):
        return self.canvas.point_doc_to_win(self.get_point())

    def is_pressed(self, win_point):
        wpoint = self.canvas.point_doc_to_win(self.get_point())
        bbox = libgeom.bbox_for_point(wpoint, config.point_sensitivity_size)
        return libgeom.is_point_in_bbox(win_point, bbox)

    def repaint(self):
        self.canvas.renderer.draw_rect_point(self.get_screen_point())


class MidPoint:
    canvas = None
    target = None
    point = []
    callback = None

    def __init__(self, canvas, target, point):
        self.canvas = canvas
        self.target = target
        self.point = point

    def get_point(self):
        return libgeom.apply_trafo_to_point(self.point, self.target.trafo)

    def get_screen_point(self):
        return self.canvas.point_doc_to_win(self.get_point())

    def is_pressed(self, win_point):
        wpoint = self.canvas.point_doc_to_win(self.get_point())
        bbox = libgeom.bbox_for_point(wpoint, config.point_sensitivity_size)
        return libgeom.is_point_in_bbox(win_point, bbox)

    def repaint(self):
        self.canvas.renderer.draw_rect_midpoint(self.get_screen_point())


def x_intersect(p0, p1, y=0):
    """
    Calculates the coordinates of the intersect line and horizontal line.
    Horizontal line defined by y coordinate.
    :param p0: Start point of the line.
    :param p1: End point of the line.
    :param y: Horizontal line coordinate.
    :return: intersect point or None
    """
    dx = p1[0] - p0[0]
    dy = p0[1] - p1[1]
    # If the line is parallel to the horizontal
    if abs(dy) < EPSILON:
        return None
    c1 = p0[0] * p1[1] - p1[0] * p0[1]
    return [(-y * dx - c1) / dy, y]


def y_intersect(p0, p1, x=0):
    """
    Calculates the coordinates of the intersect line and vertical line.
    Vertical line defined by x coordinate.
    :param p0: Start point of the line.
    :param p1: End point of the line.
    :param x: Vertical line coordinate.
    :return: intersect point or None
    """
    dx = p1[0] - p0[0]
    dy = p0[1] - p1[1]
    # If the line is parallel to the vertical
    if abs(dx) < EPSILON:
        return None
    c1 = p0[0] * p1[1] - p1[0] * p0[1]
    return [x, (-x * dy - c1) / dx]


def project_point_to_line(point, p0, p1):
    """
    Calculates the coordinates of the orthogonal projection to line.
    Line defined by two coordinate.
    :param p0: Start point of the line on that the point is projected.
    :param p1: End point of the line on that the point is projected.
    :param point: Point to project.
    :return: project point
    """
    x1, y1 = p0
    x2, y2 = p1
    x3, y3 = point

    dx = x2 - x1
    dy = y2 - y1

    v = dx * dx + dy * dy
    # If the segment has length 0 the projection is equal to that point
    if v < EPSILON:
        return [x3, y3]

    k = (dy * (x3 - x1) - dx * (y3 - y1)) / v
    x4 = x3 - k * dy
    y4 = y3 + k * dx
    return [x4, y4]
