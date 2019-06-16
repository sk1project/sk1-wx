# -*- coding: utf-8 -*-
#
#  Copyright (C) 2009-2019 by Maxim S. Barabash
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

from uc2.formats.dst import dst_model, dst_const
from uc2 import _, uc2const, sk2const, cms, libgeom


class EmbroideryMachine(object):
    max_distance = dst_const.MAX_DISTANCE

    def __init__(self, dst_doc):
        self.dst_doc = dst_doc
        self.dst_mt = dst_doc.model
        self.x = 0
        self.y = 0
        self.header = dst_model.DstHeader()
        self.dst_mt.childs.append(self.header)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def jump_to(self, x, y):
        self._to(x, y, dst_const.CMD_JUMP, self.max_distance)

    def stitch_to(self, x, y):
        self._to(x, y, dst_const.CMD_STITCH, self.max_distance)

    def stop(self):
        stop = dst_model.DstStitch()
        stop.cid = dst_const.CMD_STOP
        self.dst_mt.childs.append(stop)

    def end(self):
        data_term = dst_model.DstStitch()
        data_term.cid = dst_const.DATA_TERMINATOR
        self.dst_mt.childs.append(data_term)

    def _to(self, x, y, cid, max_distance):
        end_point = (x, y)
        while True:
            current_point = (self.x, self.y)
            distance = libgeom.distance(current_point, end_point)
            print "##", distance
            if distance > 0:
                coef = min(distance, max_distance) / distance
                if coef != 1.0:
                    x, y = libgeom.midpoint(current_point, end_point, coef)

            cmd = dst_model.DstStitch()
            cmd.cid = cid
            cmd.dx = int(x) - self.x
            cmd.dy = int(y) - self.y

            self.dst_mt.childs.append(cmd)
            self.move(cmd.dx, cmd.dy)

            if distance < max_distance:
                break

    #
    # def color_change(self, dx, dy):
    #     self.move(dx, dy)
    #     self.end_stitch()
    #
    # def stop(self, dx, dy):
    #     self.move(dx, dy)
    #     self.end_stitch()
    #
    # def stitch(self, dx, dy):
    #     self.move(dx, dy)
    #     self.stitch_list.append([self.x, self.y])
    #
    # def sequin_eject(self, dx, dy):
    #     self.move(dx, dy)
    #
    # def end_stitch(self):
    #     pass


class SK2_to_DST_Translator(object):
    sk2_doc = None
    sk2_mtds = None
    dst_doc = None
    trafo = None
    palette = None
    processor = None

    def translate(self, sk2_doc, dst_doc):
        self.processor = EmbroideryMachine(dst_doc)
        self.trafo = [] + dst_const.SK2_to_DST_TRAFO
        self.sk2_doc = sk2_doc
        self.sk2_mtds = sk2_doc.methods
        self.dst_doc = dst_doc
        self.palette = []

        self.dst_doc.model.childs = []
        header = dst_model.DstHeader()
        self.dst_doc.model.childs.append(header)

        page = self.sk2_mtds.get_page()
        for layer in page.childs:
            if self.sk2_mtds.is_layer_visible(layer):
                self.translate_objs(layer.childs)

        self.processor.jump_to(0.0, 0.0)
        self.processor.stop()
        self.processor.end()

    def translate_objs(self, objs):
        for obj in objs:
            if obj.is_primitive:
                self.translate_primitive(obj)
            elif obj.is_group:
                self.translate_group(obj)

    def translate_group(self, obj):
        self.translate_objs(obj.childs)

    def translate_primitive(self, obj):
        curve = obj.to_curve()
        if curve.is_group:
            self.translate_group(curve)
            return
        curve.update()
        trafo = libgeom.multiply_trafo(curve.trafo, self.trafo)
        paths = libgeom.apply_trafo_to_paths(curve.paths, trafo)
        paths = libgeom.flat_paths(paths)
        self.translate_paths(obj.style, paths)

    def translate_paths(self, style, paths):
        if style[1]:
            self.translate_stroke(style, paths)

    def translate_stroke(self, style, paths):
        # print '---', style#, paths
        clr = self.sk2_doc.cms.get_rgb_color(style[1][2])
        hex_color = cms.rgb_to_hexcolor(clr[1])
        print 'hex_color', hex_color
        if not self.palette:
            self.palette.append(hex_color)

        if self.is_color_changed(hex_color):
            self.palette.append(hex_color)
            print 'new', hex_color

            self._chang_color()

        for path in paths:
            start_point = path[0]
            points = path[1]
            self.processor.jump_to(start_point[0], start_point[1])
            self.processor.stitch_to(start_point[0], start_point[1])

            for point in points:
                self.processor.stitch_to(point[0], point[1])

    def _chang_color(self):
        cmd = dst_model.DstStitch()
        cmd.cid = dst_const.CMD_CHANGE_COLOR
        self.dst_doc.model.childs.append(cmd)

    def is_color_changed(self, hex_color):
        return not (self.palette and self.palette[-1] == hex_color)

