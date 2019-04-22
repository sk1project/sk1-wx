# -*- coding: utf-8 -*-
#
#  Copyright (C) 2012 by Igor E. Novikov
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

from copy import deepcopy

from uc2 import _, events
from uc2 import libgeom
from uc2.formats.plt import plt_model
from uc2.formats.plt.plt_const import SK2_to_PLT_TRAFO, PLT_to_SK2_TRAFO
from uc2.formats.sk2 import sk2_model


class PLT_to_SK2_Translator(object):
    def translate(self, plt_doc, sk2_doc):
        jobs = plt_doc.get_jobs()
        page = sk2_doc.methods.get_page()
        layer = sk2_doc.methods.get_layer(page)

        style = [deepcopy(sk2_doc.config.default_fill),
                 deepcopy(sk2_doc.config.default_stroke),
                 deepcopy(sk2_doc.config.default_text_style), []]

        for job in jobs:
            if job.cid == plt_model.JOB:
                curve = sk2_model.Curve(sk2_doc.config)
                curve.paths = [deepcopy(job.cache_path), ]
                curve.trafo = [] + PLT_to_SK2_TRAFO
                curve.style = deepcopy(style)
                sk2_doc.methods.append_object(curve, layer)

        sk2_doc.model.do_update()


class SK2_to_PLT_Translator(object):
    jobs = []
    plt_doc = None
    obj_stack = []
    counter = 0
    position = 0

    def translate(self, objs, plt_doc):
        self.plt_doc = plt_doc
        self.jobs = plt_doc.get_jobs()
        self.obj_stack = []
        self.recursive_processing(objs)
        self.create_jobs()
        self.plt_doc.model.do_update()

    def recursive_processing(self, objs):
        for obj in objs:
            if obj.is_primitive:
                curve = obj.to_curve()
                if not curve:
                    continue
                if not curve.is_primitive:
                    self.recursive_processing(curve.childs)
                else:
                    self.obj_stack.append(curve)
            else:
                self.recursive_processing(obj.childs)

    def create_jobs(self):
        if self.obj_stack:
            m11, m21, m12, m22, dx, dy = SK2_to_PLT_TRAFO

            if self.plt_doc.config.plt_force_zero:
                bbox = []
                bbox += self.obj_stack[0].cache_bbox
                for obj in self.obj_stack:
                    bbox = libgeom.sum_bbox(bbox, obj.cache_bbox)

                dx = -bbox[0] * m11
                dy = -bbox[1] * m22

            trafo = [m11 * self.plt_doc.config.plt_scale,
                     m21, m12,
                     m22 * self.plt_doc.config.plt_scale,
                     dx, dy]

            obj_num = len(self.obj_stack)
            for obj in self.obj_stack:

                self.counter += 1
                position = float(self.counter) / obj_num
                if position - self.position > 0.05:
                    msg = _('Saving in progress...')
                    events.emit(events.FILTER_INFO, msg, position)
                    self.position = position

                paths = libgeom.get_flattened_paths(
                    obj, trafo, self.plt_doc.config.plt_tolerance)
                if paths is None:
                    continue
                for path in paths:
                    if self.plt_doc.config.plt_optimize:
                        rl = self.plt_doc.config.plt_rounding_level
                        path[0] = [round(x / rl) * rl for x in path[0]]
                        start0, start1 = [], path[0]
                        points = []
                        for point in path[1]:
                            point = [round(x / rl) * rl for x in point]
                            if not point == start1:
                                if point == start0:
                                    points = points[:-1]
                                    if len(points) > 1:
                                        start0, start1 = points[-1], start0
                                    elif points:
                                        start0, start1 = [], start0
                                    continue
                                start0, start1 = start1, point
                                points.append(point)
                        path[1] = points

                    if path and path[1]:
                        self.jobs.append(plt_model.PltJob('', path))
