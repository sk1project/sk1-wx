# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013-2021 by Ihor E. Novikov
#  Copyright (C) 2021 by Maxim S. Barabash
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

from generic import AbstractController
from sk1 import modes, config
from uc2 import libgeom, sk2const

EPSILON = 0.0001
MAX_RATIO_TRAFO = 15.0

MARK_TOP_LEFT_TRAFO = 0
MARK_TOP_TRAFO = 1
MARK_TOP_RIGHT_TRAFO = 2
MARK_LEFT_TRAFO = 3
MARK_TRAFO = 4
MARK_RIGHT_TRAFO = 5
MARK_BOTTOM_LEFT_TRAFO = 6
MARK_BOTTOM_TRAFO = 7
MARK_BOTTOM_RIGHT_TRAFO = 8
MARK_ROTATE = 9
MARK_TOP_LEFT_ROTATE = 10
MARK_TOP_SKEW = 11
MARK_TOP_RIGHT_ROTATE = 12
MARK_LEFT_SKEW = 13
MARK_RIGHT_SKEW = 14
MARK_BOTTOM_LEFT_ROTATE = 15
MARK_BOTTOM_SKEW = 16
MARK_BOTTOM_RIGHT_ROTATE = 17


class MoveController(AbstractController):
    mode = modes.MOVE_MODE

    # drawing data
    trafo = []
    old_selection = []

    # Flags
    copy = False  # entering into copy mode
    moved = False  # entering into moving mode

    def __init__(self, canvas, presenter):
        AbstractController.__init__(self, canvas, presenter)
        self.trafo = []
        self.old_selection = []

    def repaint(self):
        if self.end:
            self.canvas.renderer.cdc_draw_move_frame(self.trafo)
            self.end = []

    def _calc_trafo(self, point1, point2):
        start_point = self.canvas.win_to_doc(point1)
        end_point = self.canvas.win_to_doc(point2)
        dx = end_point[0] - start_point[0]
        dy = end_point[1] - start_point[1]
        return [1.0, 0.0, 0.0, 1.0, dx, dy]

    def mouse_down(self, event):
        self.snap = self.presenter.snap
        self.start = event.get_point()
        self.timer.stop()
        dpoint = self.canvas.win_to_doc(self.start)
        sel = self.selection.pick_at_point(dpoint, True)
        self.old_selection = [] + self.selection.objs
        if sel and sel[0] not in self.selection.objs:
            self.selection.clear()
            self.canvas.renderer.paint_selection()
            self.canvas.selection_repaint = False
            self.selection.set(sel)
        self.canvas.selection_repaint = False
        self.canvas.renderer.cdc_paint_doc()
        self.timer.start()

    def mouse_move(self, event):
        if self.start:
            self.moved = True
            new = event.get_point()
            if event.is_ctrl():
                change = [new[0] - self.start[0], new[1] - self.start[1]]
                if abs(change[0]) > abs(change[1]):
                    new[1] = self.start[1]
                else:
                    new[0] = self.start[0]
            self.end = new
            self.trafo = self._calc_trafo(self.start, self.end)
            bbox = self.presenter.selection.bbox
            self.trafo = self._snap(bbox, self.trafo)
        else:
            point = event.get_point()
            dpoint = self.canvas.win_to_doc(point)
            if self.selection.is_point_over_marker(dpoint):
                mark = self.selection.is_point_over_marker(dpoint)[0]
                self.canvas.resize_marker = mark
                self.canvas.restore_mode()
                self.canvas.set_temp_mode(modes.RESIZE_MODE)
            elif event.is_shift():
                self.canvas.set_temp_mode(modes.SELECT_MODE)
            elif self.presenter.methods.is_guide_editable() and \
                    self.presenter.snap.is_over_guide(point)[0]:
                self.canvas.restore_mode()
                self.canvas.set_temp_mode(modes.GUIDE_MODE)
            elif not self.selection.pick_at_point(dpoint, True):
                self.canvas.restore_mode()

    def mouse_up(self, event):
        if self.start:
            self.timer.stop()
            new = event.get_point()
            if event.is_ctrl():
                change = [new[0] - self.start[0], new[1] - self.start[1]]
                if abs(change[0]) > abs(change[1]):
                    new[1] = self.start[1]
                else:
                    new[0] = self.start[0]
            self.end = new
            self.canvas.selection_repaint = True
            if self.moved:
                self.trafo = self._calc_trafo(self.start, self.end)
                bbox = self.presenter.selection.bbox
                self.trafo = self._snap(bbox, self.trafo)
                self.api.transform_selected(self.trafo, self.copy)
            elif event.is_shift():
                self.presenter.selection.set(self.old_selection)
                self.canvas.select_at_point(event.get_point(), True)
                if not self.selection.is_point_over(event.get_point()):
                    self.canvas.restore_mode()
            else:
                sel = self.presenter.selection.objs
                self.presenter.selection.set(sel)
            if self.copy:
                self.canvas.restore_cursor()
            self.moved = False
            self.copy = False
            self.old_selection = []
            self.start = []
            self.end = []

    def mouse_right_up(self, event):
        if self.moved:
            self.copy = True
            cursor = self.app.cursors[modes.COPY_MODE]
            self.canvas.set_temp_cursor(cursor)
        else:
            AbstractController.mouse_right_up(self, event)

    def mouse_double_click(self, event):
        self.canvas.set_mode(modes.SHAPER_MODE)

    def _snap(self, bbox, trafo):
        result = [] + trafo
        points = libgeom.bbox_middle_points(bbox)
        tr_points = libgeom.apply_trafo_to_points(points, trafo)
        active_snap = [None, None]

        shift_x = []
        snap_x = []
        for point in [tr_points[0], tr_points[2], tr_points[1]]:
            flag, _wp, dp = self.snap.snap_point(point, False, snap_y=False)
            if flag:
                shift_x.append(dp[0] - point[0])
                snap_x.append(dp[0])
        if shift_x:
            if len(shift_x) > 1:
                if abs(shift_x[0]) < abs(shift_x[1]):
                    dx = shift_x[0]
                    active_snap[0] = snap_x[0]
                else:
                    dx = shift_x[1]
                    active_snap[0] = snap_x[1]
            else:
                dx = shift_x[0]
                active_snap[0] = snap_x[0]
            result[4] += dx

        shift_y = []
        snap_y = []
        pnts = [tr_points[1], tr_points[3], tr_points[2]]
        if len(self.selection.objs) == 1 and self.selection.objs[0].is_text:
            line_points = self.selection.objs[0].get_line_points()
            pnts = libgeom.apply_trafo_to_points(line_points, trafo) + pnts
        for point in pnts:
            flag, _wp, dp = self.snap.snap_point(point, False, snap_x=False)
            if flag:
                shift_y.append(dp[1] - point[1])
                snap_y.append(dp[1])
        if shift_y:
            if len(shift_y) > 1:
                if abs(shift_y[0]) < abs(shift_y[1]):
                    dy = shift_y[0]
                    active_snap[1] = snap_y[0]
                else:
                    dy = shift_y[1]
                    active_snap[1] = snap_y[1]
            else:
                dy = shift_y[0]
                active_snap[1] = snap_y[0]
            result[5] += dy

        self.snap.active_snap = [] + active_snap
        return result


DUPLICATE_MODES = {
    MARK_TOP_LEFT_TRAFO: modes.RESIZE_MODE1_COPY,
    MARK_TOP_TRAFO: modes.RESIZE_MODE2_COPY,
    MARK_TOP_RIGHT_TRAFO: modes.RESIZE_MODE3_COPY,
    MARK_LEFT_TRAFO: modes.RESIZE_MODE4_COPY,
    MARK_RIGHT_TRAFO: modes.RESIZE_MODE4_COPY,
    MARK_BOTTOM_LEFT_TRAFO: modes.RESIZE_MODE3_COPY,
    MARK_BOTTOM_TRAFO: modes.RESIZE_MODE2_COPY,
    MARK_BOTTOM_RIGHT_TRAFO: modes.RESIZE_MODE1_COPY,
    MARK_ROTATE: modes.RESIZE_MODE,
    MARK_TOP_LEFT_ROTATE: modes.RESIZE_MODE10_COPY,
    MARK_TOP_SKEW: modes.RESIZE_MODE11_COPY,
    MARK_TOP_RIGHT_ROTATE: modes.RESIZE_MODE10_COPY,
    MARK_LEFT_SKEW: modes.RESIZE_MODE13_COPY,
    MARK_RIGHT_SKEW: modes.RESIZE_MODE13_COPY,
    MARK_BOTTOM_LEFT_ROTATE: modes.RESIZE_MODE10_COPY,
    MARK_BOTTOM_SKEW: modes.RESIZE_MODE11_COPY,
    MARK_BOTTOM_RIGHT_ROTATE: modes.RESIZE_MODE10_COPY,
}

REGULAR_MODES = {
    MARK_TOP_LEFT_TRAFO: modes.RESIZE_MODE1,
    MARK_TOP_TRAFO: modes.RESIZE_MODE2,
    MARK_TOP_RIGHT_TRAFO: modes.RESIZE_MODE3,
    MARK_LEFT_TRAFO: modes.RESIZE_MODE4,
    MARK_RIGHT_TRAFO: modes.RESIZE_MODE4,
    MARK_BOTTOM_LEFT_TRAFO: modes.RESIZE_MODE3,
    MARK_BOTTOM_TRAFO: modes.RESIZE_MODE2,
    MARK_BOTTOM_RIGHT_TRAFO: modes.RESIZE_MODE1,
    MARK_ROTATE: modes.RESIZE_MODE,
    MARK_TOP_LEFT_ROTATE: modes.RESIZE_MODE10,
    MARK_TOP_SKEW: modes.RESIZE_MODE11,
    MARK_TOP_RIGHT_ROTATE: modes.RESIZE_MODE10,
    MARK_LEFT_SKEW: modes.RESIZE_MODE13,
    MARK_RIGHT_SKEW: modes.RESIZE_MODE13,
    MARK_BOTTOM_LEFT_ROTATE: modes.RESIZE_MODE10,
    MARK_BOTTOM_SKEW: modes.RESIZE_MODE11,
    MARK_BOTTOM_RIGHT_ROTATE: modes.RESIZE_MODE10,
}


class TransformController(AbstractController):
    mode = modes.RESIZE_MODE

    # drawing data
    frame = []
    painter = None
    trafo = None

    # Actual event point
    offset_start = None

    # Flags
    copy = False  # entering into copy mode
    moved = False  # entering into moving mode

    def __init__(self, canvas, presenter):
        AbstractController.__init__(self, canvas, presenter)
        self.frame = []
        self._calc_trafo_handlers = {
            MARK_TOP_LEFT_TRAFO: self._calc_top_left_scale_trafo,
            MARK_TOP_TRAFO: self._calc_top_scale_trafo,
            MARK_TOP_RIGHT_TRAFO: self._calc_top_right_scale_trafo,
            MARK_LEFT_TRAFO: self._calc_left_scale_trafo,
            MARK_RIGHT_TRAFO: self._calc_right_scale_trafo,
            MARK_BOTTOM_LEFT_TRAFO: self._calc_bottom_left_scale_trafo,
            MARK_BOTTOM_TRAFO: self._calc_bottom_scale_trafo,
            MARK_BOTTOM_RIGHT_TRAFO: self._calc_bottom_right_scale_trafo,
            MARK_TOP_SKEW: self._calc_top_skew_trafo,
            MARK_BOTTOM_SKEW: self._calc_bottom_skew_trafo,
            MARK_LEFT_SKEW: self._calc_left_skew_trafo,
            MARK_RIGHT_SKEW: self._calc_right_skew_trafo,
            MARK_TOP_LEFT_ROTATE: self._calc_top_left_rotate_trafo,
            MARK_TOP_RIGHT_ROTATE: self._calc_top_right_rotate_trafo,
            MARK_BOTTOM_LEFT_ROTATE: self._calc_bottom_left_rotate_trafo,
            MARK_BOTTOM_RIGHT_ROTATE: self._calc_bottom_right_rotate_trafo,
        }

    def repaint(self):
        if self.painter is not None:
            self.painter()

    def mouse_move(self, event):
        is_constraining = event.is_ctrl()
        is_snapping = not event.is_shift()

        if not self.start:
            point = self.canvas.win_to_doc(event.get_point())
            ret = self.selection.is_point_over_marker(point)
            if not ret:
                self.canvas.restore_mode()
            elif not ret[0] == self.canvas.resize_marker:
                self.canvas.resize_marker = ret[0]
                self.set_cursor()

        else:
            self.end = event.get_point()
            if not self.canvas.resize_marker == MARK_ROTATE:
                self.trafo = self._calc_trafo(event)
                self.moved = True
            else:
                start = self.canvas.win_to_doc(self.start)
                end = self.canvas.win_to_doc(self.end)

                center = libgeom.bbox_center(self.selection.bbox)
                offset = libgeom.add_points(center, self.offset_start)
                dp = libgeom.sub_points(end, start)
                cursor = libgeom.add_points(offset, dp)

                if is_constraining:
                    step = config.rotation_step
                    cursor = libgeom.round_angle_point(center, cursor, step)
                if is_snapping:
                    cursor = self.snap.snap_point(cursor, False)[2]

                center_offset = libgeom.sub_points(cursor, center)
                self.selection.center_offset = center_offset
                self.canvas.selection_redraw()

    def mouse_down(self, event):
        self.snap = self.presenter.snap
        self.start = event.get_point()
        self.timer.stop()
        if not self.canvas.resize_marker == MARK_ROTATE:
            self.painter = self._draw_frame
            self.canvas.renderer.cdc_paint_doc()
            self.canvas.selection_repaint = False
        else:
            self.painter = None  # draw center
            self.offset_start = [] + self.selection.center_offset
            self.canvas.selection_repaint = True
        self.timer.start()

    def mouse_up(self, event):
        self.timer.stop()
        self.end = event.get_point()
        if not self.canvas.resize_marker == MARK_ROTATE:
            self.canvas.selection_repaint = True
            if self.moved:
                self.canvas.renderer.hide_move_frame()
                self.trafo = self._calc_trafo(event)
                self.api.transform_selected(self.trafo, self.copy)

            point = self.canvas.win_to_doc(event.get_point())
            if not self.selection.is_point_over_marker(point):
                self.canvas.restore_mode()
            else:
                self.selection.update()
        self.moved = False
        self.copy = False
        self.start = []
        self.end = []
        self.offset_start = []

    def mouse_right_up(self, event):
        if self.moved:
            self.copy = True
            self.set_cursor()
        else:
            AbstractController.mouse_right_up(self, event)

    def set_cursor(self):
        mark = self.canvas.resize_marker
        self.mode = DUPLICATE_MODES.get(mark, self.mode) if self.copy \
            else REGULAR_MODES.get(mark, self.mode)
        self.canvas.set_canvas_cursor(self.mode)

    def _calc_trafo(self, event):
        mark = self.canvas.resize_marker
        handler = self._calc_trafo_handlers.get(mark)
        if handler:
            trafo = handler(event)
        else:
            trafo = [] + sk2const.NORMAL_TRAFO
        return trafo

    def _calc_top_left_scale_trafo(self, event):
        is_centering = event.is_shift()
        is_constraining = event.is_ctrl()
        is_snapping = True

        m11, m21, m12, m22, dx, dy = sk2const.NORMAL_TRAFO
        start_point = self.canvas.win_to_doc(self.start)
        end_point = self.canvas.win_to_doc(self.end)
        bbox = self.presenter.selection.bbox
        bbox_points = libgeom.bbox_points(bbox)
        point = bbox_points[1]
        base_x, base_y = bbox_points[2]
        w, h = libgeom.bbox_size(bbox)

        if is_centering:
            shift_x = w / 2.0 + self.selection.center_offset[0]
            shift_y = h / 2.0 - self.selection.center_offset[1]

            ratio_x = w / shift_x if shift_x else 1.0
            ratio_y = h / shift_y if shift_y else 1.0

            ratio_x = ratio_x if abs(ratio_x) < MAX_RATIO_TRAFO else 1.0
            ratio_y = ratio_y if abs(ratio_y) < MAX_RATIO_TRAFO else 1.0

            shift_x = w - shift_x
            shift_y = shift_y - h
        else:
            shift_x, ratio_x = 0.0, 1.0
            shift_y, ratio_y = 0.0, 1.0

        change_x = w + (start_point[0] - end_point[0]) * ratio_x
        change_y = h + (end_point[1] - start_point[1]) * ratio_y

        if is_constraining:
            if w < h:
                m11 = m22 = change_x / w if w and change_x else 1.0
            else:
                m11 = m22 = change_y / h if h and change_y else 1.0
        else:
            m11 = change_x / w if w and change_x else 1.0
            m22 = change_y / h if h and change_y else 1.0

        dx = base_x - base_x * m11 + shift_x * (m11 - 1.0)
        dy = base_y - base_y * m22 + shift_y * (m22 - 1.0)

        if is_snapping:
            trafo = [m11, m21, m12, m22, dx, dy]
            p = libgeom.apply_trafo_to_point(point, trafo)
            flag, _wp, end_point = self.snap.snap_point(p, False)
            start_point = point
            if flag:
                change_x = w + (start_point[0] - end_point[0]) * ratio_x
                change_y = h + (end_point[1] - start_point[1]) * ratio_y

                if is_constraining:
                    if self.snap.active_snap[0] is not None:
                        m11 = m22 = change_x / w if w and change_x else 1.0
                    else:
                        m11 = m22 = change_y / h if h and change_y else 1.0
                else:
                    m11 = change_x / w if w and change_x else 1.0
                    m22 = change_y / h if h and change_y else 1.0

                dx = base_x - base_x * m11 + shift_x * (m11 - 1.0)
                dy = base_y - base_y * m22 + shift_y * (m22 - 1.0)

        return [m11 or EPSILON, m21, m12, m22 or EPSILON, dx, dy]

    def _calc_bottom_left_scale_trafo(self, event):
        is_centering = event.is_shift()
        is_constraining = event.is_ctrl()
        is_snapping = True

        m11, m21, m12, m22, dx, dy = sk2const.NORMAL_TRAFO
        start_point = self.canvas.win_to_doc(self.start)
        end_point = self.canvas.win_to_doc(self.end)
        bbox = self.presenter.selection.bbox
        bbox_points = libgeom.bbox_points(bbox)
        point = bbox_points[0]
        base_x, base_y = bbox_points[3]
        w, h = libgeom.bbox_size(bbox)

        if is_centering:
            shift_x = w / 2.0 + self.selection.center_offset[0]
            shift_y = h / 2.0 + self.selection.center_offset[1]

            ratio_x = w / shift_x if shift_x else 1.0
            ratio_y = h / shift_y if shift_y else 1.0

            ratio_x = ratio_x if abs(ratio_x) < MAX_RATIO_TRAFO else 1.0
            ratio_y = ratio_y if abs(ratio_y) < MAX_RATIO_TRAFO else 1.0

            shift_x = w - shift_x
            shift_y = h - shift_y
        else:
            shift_x, ratio_x = 0.0, 1.0
            shift_y, ratio_y = 0.0, 1.0

        change_x = w + (start_point[0] - end_point[0]) * ratio_x
        change_y = h + (start_point[1] - end_point[1]) * ratio_y

        if is_constraining:
            if w < h:
                m11 = m22 = change_x / w if w and change_x else 1.0
            else:
                m11 = m22 = change_y / h if h and change_y else 1.0
        else:
            m11 = change_x / w if w and change_x else 1.0
            m22 = change_y / h if h and change_y else 1.0

        dx = base_x - base_x * m11 + shift_x * (m11 - 1.0)
        dy = base_y - base_y * m22 + shift_y * (m22 - 1.0)

        if is_snapping:
            trafo = [m11, m21, m12, m22, dx, dy]
            p = libgeom.apply_trafo_to_point(point, trafo)
            flag, _wp, end_point = self.snap.snap_point(p, False)
            start_point = point
            if flag:
                change_x = w + (start_point[0] - end_point[0]) * ratio_x
                change_y = h + (start_point[1] - end_point[1]) * ratio_y

                if is_constraining:
                    if self.snap.active_snap[0] is not None:
                        m11 = m22 = change_x / w if w and change_x else 1.0
                    else:
                        m11 = m22 = change_y / h if h and change_y else 1.0
                else:
                    m11 = change_x / w if w and change_x else 1.0
                    m22 = change_y / h if h and change_y else 1.0

                dx = base_x - base_x * m11 + shift_x * (m11 - 1.0)
                dy = base_y - base_y * m22 + shift_y * (m22 - 1.0)

        return [m11 or EPSILON, m21, m12, m22 or EPSILON, dx, dy]

    def _calc_top_right_scale_trafo(self, event):
        is_centering = event.is_shift()
        is_constraining = event.is_ctrl()
        is_snapping = True

        m11, m21, m12, m22, dx, dy = sk2const.NORMAL_TRAFO
        start_point = self.canvas.win_to_doc(self.start)
        end_point = self.canvas.win_to_doc(self.end)
        bbox = self.presenter.selection.bbox
        bbox_points = libgeom.bbox_points(bbox)
        point = bbox_points[3]
        base_x, base_y = bbox_points[0]
        w, h = libgeom.bbox_size(bbox)

        if is_centering:
            shift_x = w / 2.0 - self.selection.center_offset[0]
            shift_y = h / 2.0 - self.selection.center_offset[1]

            ratio_x = w / shift_x if shift_x else 1.0
            ratio_y = h / shift_y if shift_y else 1.0

            ratio_x = ratio_x if abs(ratio_x) < MAX_RATIO_TRAFO else 1.0
            ratio_y = ratio_y if abs(ratio_y) < MAX_RATIO_TRAFO else 1.0

            shift_x = shift_x - w
            shift_y = shift_y - h
        else:
            shift_x, ratio_x = 0.0, 1.0
            shift_y, ratio_y = 0.0, 1.0

        change_x = w + (end_point[0] - start_point[0]) * ratio_x
        change_y = h + (end_point[1] - start_point[1]) * ratio_y

        if is_constraining:
            if w < h:
                m11 = m22 = change_x / w if w and change_x else 1.0
            else:
                m11 = m22 = change_y / h if h and change_y else 1.0
        else:
            m11 = change_x / w if w and change_x else 1.0
            m22 = change_y / h if h and change_y else 1.0

        dx = base_x - base_x * m11 + shift_x * (m11 - 1.0)
        dy = base_y - base_y * m22 + shift_y * (m22 - 1.0)

        if is_snapping:
            trafo = [m11, m21, m12, m22, dx, dy]
            p = libgeom.apply_trafo_to_point(point, trafo)
            flag, _wp, end_point = self.snap.snap_point(p, False)
            start_point = point
            if flag:
                change_x = w + (end_point[0] - start_point[0]) * ratio_x
                change_y = h + (end_point[1] - start_point[1]) * ratio_y

                if is_constraining:
                    if self.snap.active_snap[0] is not None:
                        m11 = m22 = change_x / w if w and change_x else 1.0
                    else:
                        m11 = m22 = change_y / h if h and change_y else 1.0
                else:
                    m11 = change_x / w if w and change_x else 1.0
                    m22 = change_y / h if h and change_y else 1.0

                dx = base_x - base_x * m11 + shift_x * (m11 - 1.0)
                dy = base_y - base_y * m22 + shift_y * (m22 - 1.0)

        return [m11 or EPSILON, m21, m12, m22 or EPSILON, dx, dy]

    def _calc_bottom_right_scale_trafo(self, event):
        is_centering = event.is_shift()
        is_constraining = event.is_ctrl()
        is_snapping = True

        m11, m21, m12, m22, dx, dy = sk2const.NORMAL_TRAFO
        start_point = self.canvas.win_to_doc(self.start)
        end_point = self.canvas.win_to_doc(self.end)
        bbox = self.presenter.selection.bbox
        bbox_points = libgeom.bbox_points(bbox)
        point = bbox_points[2]
        base_x, base_y = bbox_points[1]
        w, h = libgeom.bbox_size(bbox)

        if is_centering:
            shift_x = w / 2.0 - self.selection.center_offset[0]
            shift_y = h / 2.0 + self.selection.center_offset[1]

            ratio_x = w / shift_x if shift_x else 1.0
            ratio_y = h / shift_y if shift_y else 1.0

            ratio_x = ratio_x if abs(ratio_x) < MAX_RATIO_TRAFO else 1.0
            ratio_y = ratio_y if abs(ratio_y) < MAX_RATIO_TRAFO else 1.0

            shift_x = shift_x - w
            shift_y = h - shift_y
        else:
            shift_x, ratio_x = 0.0, 1.0
            shift_y, ratio_y = 0.0, 1.0

        change_x = w + (end_point[0] - start_point[0]) * ratio_x
        change_y = h + (start_point[1] - end_point[1]) * ratio_y
        if is_constraining:
            if w < h:
                m11 = m22 = change_x / w if w and change_x else 1.0
            else:
                m11 = m22 = change_y / h if h and change_y else 1.0
        else:
            m11 = change_x / w if w and change_x else 1.0
            m22 = change_y / h if h and change_y else 1.0

        dx = base_x - base_x * m11 + shift_x * (m11 - 1.0)
        dy = base_y - base_y * m22 + shift_y * (m22 - 1.0)

        if is_snapping:
            trafo = [m11, m21, m12, m22, dx, dy]
            p = libgeom.apply_trafo_to_point(point, trafo)
            flag, _wp, end_point = self.snap.snap_point(p, False)
            start_point = point
            if flag:
                change_x = w + (end_point[0] - start_point[0]) * ratio_x
                change_y = h + (start_point[1] - end_point[1]) * ratio_y

                if is_constraining:
                    if self.snap.active_snap[0] is not None:
                        m11 = m22 = change_x / w if w and change_x else 1.0
                    else:
                        m11 = m22 = change_y / h if h and change_y else 1.0
                else:
                    m11 = change_x / w if w and change_x else 1.0
                    m22 = change_y / h if h and change_y else 1.0

                dx = base_x - base_x * m11 + shift_x * (m11 - 1.0)
                dy = base_y - base_y * m22 + shift_y * (m22 - 1.0)

        return [m11 or EPSILON, m21, m12, m22 or EPSILON, dx, dy]

    def _calc_top_scale_trafo(self, event):
        is_centering = event.is_shift()
        is_constraining = event.is_ctrl()
        is_snapping = not is_constraining

        m11, m21, m12, m22, dx, dy = sk2const.NORMAL_TRAFO
        start_point = self.canvas.win_to_doc(self.start)
        end_point = self.canvas.win_to_doc(self.end)
        bbox = self.presenter.selection.bbox
        middle_points = libgeom.bbox_middle_points(bbox)
        point = middle_points[1]
        base_y = bbox[1]
        w, h = libgeom.bbox_size(bbox)

        if is_centering:
            shift_y = h / 2.0 - self.selection.center_offset[1]
            ratio_y = h / shift_y if shift_y else 1.0
            ratio_y = ratio_y if abs(ratio_y) < MAX_RATIO_TRAFO else 1.0
            shift_y = shift_y - h
        else:
            shift_y, ratio_y = 0.0, 1.0

        change_y = h + (end_point[1] - start_point[1]) * ratio_y
        if is_constraining and h and change_y:
            if -h < change_y < h:
                change_y = 1.0 / (h // change_y) * h
            else:
                change_y = h + (change_y - h / 2) // h * h

        m22 = change_y / h if h and change_y else 1.0
        dy = base_y - base_y * m22 + shift_y * (m22 - 1.0)

        if is_snapping:
            trafo = [m11, m21, m12, m22, dx, dy]
            p = libgeom.apply_trafo_to_point(point, trafo)
            flag, _wp, end_point = self.snap.snap_point(p, False)
            start_point = point
            if flag:
                change_y = h + (end_point[1] - start_point[1]) * ratio_y
                m22 = change_y / h if h else 1.0
                dy = base_y - base_y * m22 + shift_y * (m22 - 1.0)

        return [m11 or EPSILON, m21, m12, m22 or EPSILON, dx, dy]

    def _calc_left_scale_trafo(self, event):
        is_centering = event.is_shift()
        is_constraining = event.is_ctrl()
        is_snapping = not is_constraining

        m11, m21, m12, m22, dx, dy = sk2const.NORMAL_TRAFO
        start_point = self.canvas.win_to_doc(self.start)
        end_point = self.canvas.win_to_doc(self.end)
        bbox = self.presenter.selection.bbox
        middle_points = libgeom.bbox_middle_points(bbox)
        point = middle_points[0]
        base_x = bbox[2]
        w = libgeom.bbox_size(bbox)[0]

        if is_centering:
            shift_x = w / 2.0 + self.selection.center_offset[0]
            ratio_x = w / shift_x if shift_x else 1.0
            ratio_x = ratio_x if abs(ratio_x) < MAX_RATIO_TRAFO else 1.0
            shift_x = w - shift_x
        else:
            shift_x, ratio_x = 0.0, 1.0

        change_x = w + (start_point[0] - end_point[0]) * ratio_x
        if is_constraining and w and change_x:
            if -w < change_x < w:
                change_x = 1.0 / (w // change_x) * w
            else:
                change_x = w + (change_x - w / 2) // w * w

        m11 = change_x / w if w and change_x else 1.0
        dx = base_x - base_x * m11 + shift_x * (m11 - 1.0)

        if is_snapping:
            trafo = [m11, m21, m12, m22, dx, dy]
            p = libgeom.apply_trafo_to_point(point, trafo)
            flag, _wp, end_point = self.snap.snap_point(p, False)
            start_point = point
            if flag:
                change_x = w + (start_point[0] - end_point[0]) * ratio_x
                m11 = change_x / w if w else 1.0
                dx = base_x - base_x * m11 + shift_x * (m11 - 1.0)

        return [m11 or EPSILON, m21, m12, m22 or EPSILON, dx, dy]

    def _calc_right_scale_trafo(self, event):
        is_centering = event.is_shift()
        is_constraining = event.is_ctrl()
        is_snapping = not is_constraining

        m11, m21, m12, m22, dx, dy = sk2const.NORMAL_TRAFO
        start_point = self.canvas.win_to_doc(self.start)
        end_point = self.canvas.win_to_doc(self.end)
        bbox = self.presenter.selection.bbox
        point = libgeom.bbox_middle_points(bbox)[2]
        base_x = bbox[0]
        w = libgeom.bbox_size(bbox)[0]

        if is_centering:
            shift_x = w / 2.0 - self.selection.center_offset[0]
            ratio_x = w / shift_x if shift_x else 1.0
            ratio_x = ratio_x if abs(ratio_x) < MAX_RATIO_TRAFO else 1.0
            shift_x = shift_x - w
        else:
            shift_x, ratio_x = 0.0, 1.0

        change_x = w + (end_point[0] - start_point[0]) * ratio_x
        if is_constraining and w and change_x:
            if -w < change_x < w:
                change_x = 1.0 / (w // change_x) * w
            else:
                change_x = w + (change_x - w / 2) // w * w

        m11 = change_x / w if w and change_x else 1.0
        dx = base_x - base_x * m11 + shift_x * (m11 - 1.0)

        if is_snapping:
            trafo = [m11, m21, m12, m22, dx, dy]
            p = libgeom.apply_trafo_to_point(point, trafo)
            flag, _wp, end_point = self.snap.snap_point(p, False)
            start_point = point
            if flag:
                change_x = w + (end_point[0] - start_point[0]) * ratio_x
                m11 = change_x / w if w else 1.0
                dx = base_x - base_x * m11 + shift_x * (m11 - 1.0)

        return [m11 or EPSILON, m21, m12, m22 or EPSILON, dx, dy]

    def _calc_bottom_scale_trafo(self, event):
        is_centering = event.is_shift()
        is_constraining = event.is_ctrl()
        is_snapping = not is_constraining

        m11, m21, m12, m22, dx, dy = sk2const.NORMAL_TRAFO
        start_point = self.canvas.win_to_doc(self.start)
        end_point = self.canvas.win_to_doc(self.end)
        bbox = self.presenter.selection.bbox
        middle_points = libgeom.bbox_middle_points(bbox)
        point = middle_points[3]
        base_y = bbox[3]
        h = libgeom.bbox_size(bbox)[1]

        if is_centering:
            shift_y = h / 2.0 + self.selection.center_offset[1]
            ratio_y = h / shift_y if shift_y else 1.0
            ratio_y = ratio_y if abs(ratio_y) < MAX_RATIO_TRAFO else 1.0
            shift_y = h - shift_y
        else:
            shift_y, ratio_y = 0.0, 1.0

        change_y = h + (start_point[1] - end_point[1]) * ratio_y
        if is_constraining and h and change_y:
            if -h < change_y < h:
                change_y = 1.0 / (h // change_y) * h
            else:
                change_y = h + (change_y - h / 2) // h * h

        m22 = change_y / h if h and change_y else 1.0
        dy = base_y - base_y * m22 + shift_y * (m22 - 1.0)

        if is_snapping:
            trafo = [m11, m21, m12, m22, dx, dy]
            p = libgeom.apply_trafo_to_point(point, trafo)
            flag, _wp, end_point = self.snap.snap_point(p, False)
            start_point = point
            if flag:
                change_y = h + (start_point[1] - end_point[1]) * ratio_y
                m22 = change_y / h if h else 1.0
                dy = base_y - base_y * m22 + shift_y * (m22 - 1.0)

        return [m11 or EPSILON, m21, m12, m22 or EPSILON, dx, dy]

    def _calc_top_skew_trafo(self, event):
        is_centering = event.is_shift()
        is_constraining = event.is_ctrl()

        start_point = self.canvas.win_to_doc(self.start)
        end_point = self.canvas.win_to_doc(self.end)
        bbox = self.presenter.selection.bbox
        h = libgeom.bbox_size(bbox)[1]
        m11, m21, m12, m22, dx, dy = sk2const.NORMAL_TRAFO
        change_x = end_point[0] - start_point[0]

        cy = bbox[1]
        if is_centering:
            center_offset = self.presenter.selection.center_offset
            cy = libgeom.add_points(libgeom.bbox_center(bbox), center_offset)[1]

        if is_constraining:
            step = math.radians(config.skew_fixed_angle)
            angle = (math.atan2(change_x, h) + step / 2.0) // step * step
            m12 = math.tan(angle)
        else:
            m12 = change_x / h if h else 1.0

        dx = -cy * m12
        return [m11 or EPSILON, m21, m12, m22 or EPSILON, dx, dy]

    def _calc_bottom_skew_trafo(self, event):
        is_centering = event.is_shift()
        is_constraining = event.is_ctrl()

        start_point = self.canvas.win_to_doc(self.start)
        end_point = self.canvas.win_to_doc(self.end)
        bbox = self.presenter.selection.bbox
        h = libgeom.bbox_size(bbox)[1]
        m11, m21, m12, m22, dx, dy = sk2const.NORMAL_TRAFO
        change_x = start_point[0] - end_point[0]

        cy = bbox[3]
        if is_centering:
            center_offset = self.presenter.selection.center_offset
            cy = libgeom.add_points(libgeom.bbox_center(bbox), center_offset)[1]

        if is_constraining:
            step = math.radians(config.skew_fixed_angle)
            angle = (math.atan2(change_x, h) + step / 2.0) // step * step
            m12 = math.tan(angle)
        else:
            m12 = change_x / h if h else 1.0

        dx = -cy * m12
        return [m11 or EPSILON, m21, m12, m22 or EPSILON, dx, dy]

    def _calc_left_skew_trafo(self, event):
        is_centering = event.is_shift()
        is_constraining = event.is_ctrl()

        start_point = self.canvas.win_to_doc(self.start)
        end_point = self.canvas.win_to_doc(self.end)
        bbox = self.presenter.selection.bbox
        h = libgeom.bbox_size(bbox)[1]
        m11, m21, m12, m22, dx, dy = sk2const.NORMAL_TRAFO
        change_y = start_point[1] - end_point[1]

        cx = bbox[2]
        if is_centering:
            center_offset = self.presenter.selection.center_offset
            cx = libgeom.add_points(libgeom.bbox_center(bbox), center_offset)[0]

        if is_constraining:
            step = math.radians(config.skew_fixed_angle)
            angle = (math.atan2(change_y, h) + step / 2.0) // step * step
            m21 = math.tan(angle)
        else:
            m21 = change_y / h if h else 1.0

        dy = -cx * m21
        return [m11 or EPSILON, m21, m12, m22 or EPSILON, dx, dy]

    def _calc_right_skew_trafo(self, event):
        is_centering = event.is_shift()
        is_constraining = event.is_ctrl()

        start_point = self.canvas.win_to_doc(self.start)
        end_point = self.canvas.win_to_doc(self.end)
        bbox = self.presenter.selection.bbox
        h = libgeom.bbox_size(bbox)[1]
        m11, m21, m12, m22, dx, dy = sk2const.NORMAL_TRAFO
        change_y = end_point[1] - start_point[1]

        cx = bbox[0]
        if is_centering:
            center_offset = self.presenter.selection.center_offset
            cx = libgeom.add_points(libgeom.bbox_center(bbox), center_offset)[0]

        if is_constraining:
            step = math.radians(config.skew_fixed_angle)
            angle = (math.atan2(change_y, h) + step / 2.0) // step * step
            m21 = math.tan(angle)
        else:
            m21 = change_y / h if h else 1.0

        dy = -cx * m21
        return [m11 or EPSILON, m21, m12, m22 or EPSILON, dx, dy]

    def _calc_top_left_rotate_trafo(self, event):
        is_centering = not event.is_shift()
        is_constraining = event.is_ctrl()

        start_point = self.canvas.win_to_doc(self.start)
        end_point = self.canvas.win_to_doc(self.end)
        bbox = self.presenter.selection.bbox

        if is_centering:
            bbox_center = libgeom.bbox_center(bbox)
            center_offset = self.selection.center_offset
            center = libgeom.add_points(bbox_center, center_offset)
        else:
            center = libgeom.bbox_points(bbox)[2]

        a1 = libgeom.get_point_angle(start_point, center)
        a2 = libgeom.get_point_angle(end_point, center)
        angle = a2 - a1
        if is_constraining:
            step = math.radians(config.rotation_step)
            angle = (angle + step / 2.0) // step * step

        return libgeom.trafo_rotate(angle, center[0], center[1])

    def _calc_top_right_rotate_trafo(self, event):
        is_centering = not event.is_shift()
        is_constraining = event.is_ctrl()

        start_point = self.canvas.win_to_doc(self.start)
        end_point = self.canvas.win_to_doc(self.end)
        bbox = self.presenter.selection.bbox

        if is_centering:
            bbox_center = libgeom.bbox_center(bbox)
            center_offset = self.selection.center_offset
            center = libgeom.add_points(bbox_center, center_offset)
        else:
            center = libgeom.bbox_points(bbox)[0]

        a1 = libgeom.get_point_angle(start_point, center)
        a2 = libgeom.get_point_angle(end_point, center)
        angle = a2 - a1
        if is_constraining:
            step = math.radians(config.rotation_step)
            angle = (angle + step / 2.0) // step * step

        return libgeom.trafo_rotate(angle, center[0], center[1])

    def _calc_bottom_left_rotate_trafo(self, event):
        is_centering = not event.is_shift()
        is_constraining = event.is_ctrl()

        start_point = self.canvas.win_to_doc(self.start)
        end_point = self.canvas.win_to_doc(self.end)
        bbox = self.presenter.selection.bbox

        if is_centering:
            bbox_center = libgeom.bbox_center(bbox)
            center_offset = self.selection.center_offset
            center = libgeom.add_points(bbox_center, center_offset)
        else:
            center = libgeom.bbox_points(bbox)[3]

        a1 = libgeom.get_point_angle(start_point, center)
        a2 = libgeom.get_point_angle(end_point, center)
        angle = a2 - a1
        if is_constraining:
            step = math.radians(config.rotation_step)
            angle = (angle + step / 2.0) // step * step

        return libgeom.trafo_rotate(angle, center[0], center[1])

    def _calc_bottom_right_rotate_trafo(self, event):
        is_centering = not event.is_shift()
        is_constraining = event.is_ctrl()

        start_point = self.canvas.win_to_doc(self.start)
        end_point = self.canvas.win_to_doc(self.end)
        bbox = self.presenter.selection.bbox

        if is_centering:
            bbox_center = libgeom.bbox_center(bbox)
            center_offset = self.selection.center_offset
            center = libgeom.add_points(bbox_center, center_offset)
        else:
            center = libgeom.bbox_points(bbox)[1]

        a1 = libgeom.get_point_angle(start_point, center)
        a2 = libgeom.get_point_angle(end_point, center)
        angle = a2 - a1
        if is_constraining:
            step = math.radians(config.rotation_step)
            angle = (angle + step / 2.0) // step * step

        return libgeom.trafo_rotate(angle, center[0], center[1])

    def _draw_frame(self, *_args):
        if self.end:
            self.canvas.renderer.cdc_draw_move_frame(self.trafo)
            self.end = []
