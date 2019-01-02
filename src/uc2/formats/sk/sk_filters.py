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
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import os
import sys

from uc2.formats.generic_filters import AbstractLoader, AbstractSaver
from uc2.formats.sk import sk_model, sk_const

LOG = logging.getLogger(__name__)

class SK_Loader(AbstractLoader):
    name = 'SK_Loader'

    paths = []
    options = {}
    pages = None

    string = ''
    line = ''
    active_layer = None
    parent_stack = []
    obj_style = []

    style_obj = None
    style_dict = {}
    pattern = None
    gradient = None

    def do_load(self):
        self.model = None
        self.paths = []
        self.options = {}
        self.parent_stack = []
        self.obj_style = []
        self.style_dict = {}
        self.fileptr.readline()
        self.style_obj = sk_model.Style()
        while True:
            self.line = self.fileptr.readline()
            if not self.line:
                break
            self.line = self.line.rstrip('\r\n')

            self.check_loading()

            if self.line:
                try:
                    code = compile('self.' + self.line, '<string>', 'exec')
                    exec code
                except Exception as e:
                    LOG.error('Parsing error in "%s"', self.line)
                    LOG.error('Error traceback: %s', e)

    def set_style(self, obj):
        obj.properties = self.style_obj
        self.style_obj = sk_model.Style()

    def add_object(self, obj, parent=''):
        if self.model is None:
            self.model = obj
        else:
            if not parent:
                if self.parent_stack:
                    parent = self.parent_stack[-1]
                else:
                    parent = self.active_layer
            obj.parent = parent
            obj.config = self.config
            parent.childs.append(obj)

    # ---PROPERTIES
    def gl(self, colors):
        self.gradient = sk_model.MultiGradient(colors)

    def pe(self):
        self.pattern = sk_model.EmptyPattern

    def ps(self, color):
        self.pattern = sk_model.SolidPattern(color)

    def pgl(self, dx, dy, border=0):
        if not self.gradient:
            self.gradient = sk_model.MultiGradient()
        self.pattern = sk_model.LinearGradient(self.gradient,
                                               sk_model.Point(dx, dy), border)

    def pgr(self, dx, dy, border=0):
        if not self.gradient:
            self.gradient = sk_model.MultiGradient()
        self.pattern = sk_model.RadialGradient(self.gradient,
                                               sk_model.Point(dx, dy), border)

    def pgc(self, cx, cy, dx, dy):
        if not self.gradient:
            self.gradient = sk_model.MultiGradient()
        self.pattern = sk_model.ConicalGradient(self.gradient,
                                                sk_model.Point(cx, cy),
                                                sk_model.Point(dx, dy))

    def phs(self, color, background, dx, dy, dist, width):
        self.pattern = sk_model.HatchingPattern(color, background,
                                                sk_model.Point(dx, dy), dist,
                                                width)

    def pit(self, obj_id, trafo):
        trafo = sk_model.Trafo(*trafo)
        if obj_id in self.presenter.resources:
            image = self.presenter.resources[obj_id]
            self.pattern = sk_model.ImageTilePattern(image, trafo)

    def fp(self, color=None):
        if color is None:
            self.style_obj.fill_pattern = self.pattern
        else:
            self.style_obj.fill_pattern = sk_model.SolidPattern(color)

    def fe(self):
        self.style_obj.fill_pattern = sk_model.EmptyPattern

    def ft(self, val):
        self.style_obj.fill_transform = val

    def lp(self, color=None):
        if color is None:
            self.style_obj.line_pattern = self.pattern
        else:
            self.style_obj.line_pattern = sk_model.SolidPattern(color)

    def le(self):
        self.style_obj.line_pattern = sk_model.EmptyPattern

    def lw(self, width):
        self.style_obj.line_width = width

    def lc(self, cap):
        cap = 1 if not 1 <= cap <= 3 else cap
        self.style_obj.line_cap = cap

    def lj(self, join):
        self.style_obj.line_join = join

    def ld(self, dashes):
        self.style_obj.line_dashes = dashes

    def la1(self, args=None):
        self.style_obj.line_arrow1 = args

    def la2(self, args=None):
        self.style_obj.line_arrow2 = args

    def Fs(self, size):
        self.style_obj.font_size = size

    def Fn(self, name, face=None):
        self.style_obj.font = name
        self.style_obj.font_face = face

    def dstyle(self, name=''):
        if name:
            self.style_obj.name = name
            self.model.styles[name] = self.style_obj
            self.style_obj = sk_model.Style()

    def style(self, name=''):
        if name and name in self.model.styles:
            stl = self.model.styles[name].copy()
            if not self.style_obj.fill_pattern.is_Empty:
                stl.fill_pattern = self.style_obj.fill_pattern
            if not self.style_obj.line_pattern.color == sk_const.black_color:
                stl.line_pattern = self.style_obj.line_pattern
            if not self.style_obj.line_width == 0.28:
                stl.line_width = self.style_obj.line_width
            if not self.style_obj.line_join == sk_const.JoinMiter:
                stl.line_join = self.style_obj.line_join
            if not self.style_obj.line_cap == sk_const.CapButt:
                stl.line_cap = self.style_obj.line_cap
            if self.style_obj.line_dashes:
                stl.line_dashes = self.style_obj.line_dashes
            if self.style_obj.font:
                stl.font = self.style_obj.font
            if not self.style_obj.font_size == 12.0:
                stl.font_size = self.style_obj.font_size
            self.style_obj = stl

    def use_style(self, name=''):
        self.style(name)

    # ---STRUCTURAL ELEMENTS
    def document(self, *args):
        self.add_object(sk_model.SKDocument(self.config))
        self.model.childs = []

    def layout(self, *args):
        if not isinstance(args[0], tuple):
            pformat = args[0]
            orientation = args[1]
            if pformat not in sk_const.PAGE_FORMATS.keys():
                pformat = 'A4'
            size = sk_const.PAGE_FORMATS[pformat]
        else:
            pformat = ''
            size = args[0]
            orientation = args[1]
        obj = sk_model.SKLayout(pformat, size, orientation)
        self.add_object(obj, self.model)
        self.model.layout = obj

    def grid(self, grid, visibility, grid_color, layer_name='Grid'):
        obj = sk_model.SKGrid(grid, visibility, grid_color, layer_name)
        self.add_object(obj, self.model)
        self.model.grid = obj

    def layer(self, name, p1, p2, p3, p4, layer_color):
        layer = sk_model.SKLayer(name, p1, p2, p3, p4, layer_color)
        self.active_layer = layer
        self.add_object(layer, self.model)

    def guidelayer(self, name, p1, p2, p3, p4, layer_color):
        glayer = sk_model.SKGuideLayer(name, p1, p2, p3, p4, layer_color)
        self.active_layer = glayer
        self.add_object(glayer, self.model)
        self.model.guidelayer = glayer

    def guide(self, point, orientation):
        self.add_object(sk_model.SKGuide(point, orientation))

    # ---GROUPS
    def G(self):
        group = sk_model.SKGroup()
        self.add_object(group)
        self.parent_stack.append(group)

    def G_(self):
        self.parent_stack = self.parent_stack[:-1]

    def M(self):
        mgroup = sk_model.SKMaskGroup()
        self.add_object(mgroup)
        self.parent_stack.append(mgroup)

    def M_(self):
        self.parent_stack = self.parent_stack[:-1]

    def B(self):
        group = sk_model.SKGroup()
        self.string = group.string
        self.line = ''
        self.add_object(group)
        self.parent_stack.append(group)

    def Bi(self, *args):
        self.string = ''

    def B_(self):
        self.parent_stack = self.parent_stack[:-1]

    def PT(self):
        group = sk_model.SKGroup()
        self.string = group.string
        self.line = ''
        self.add_object(group)
        self.parent_stack.append(group)

    def pt(self, *args):
        self.string = ''

    def PT_(self):
        self.parent_stack = self.parent_stack[:-1]

    def PC(self, *args):
        group = sk_model.SKGroup()
        self.string = group.string
        self.line = ''
        self.add_object(group)
        self.parent_stack.append(group)

    def PC_(self):
        self.parent_stack = self.parent_stack[:-1]

    # ---PRIMITIVES
    def r(self, m11, m12, m21, m22, dx, dy, radius1=0, radius2=0):
        trafo = sk_model.Trafo(m11, m12, m21, m22, dx, dy)
        obj = sk_model.SKRectangle(trafo, radius1, radius2)
        self.set_style(obj)
        self.add_object(obj)

    def e(self, m11, m12, m21, m22, dx, dy, start_angle=0.0, end_angle=0.0,
          arc_type=sk_const.ArcPieSlice):
        trafo = sk_model.Trafo(m11, m12, m21, m22, dx, dy)
        obj = sk_model.SKEllipse(trafo, start_angle, end_angle, arc_type)
        self.set_style(obj)
        self.add_object(obj)

    def b(self):
        self.paths = [[None, [], sk_const.CURVE_OPENED]]
        obj = sk_model.SKPolyBezier(paths_list=self.paths)
        self.set_style(obj)
        self.add_object(obj)

    def bs(self, x, y, cont):
        point = [x, y]
        path = self.paths[-1]
        points = path[1]
        if path[0] is None:
            path[0] = point
        else:
            points.append(point)

    def bc(self, x1, y1, x2, y2, x3, y3, cont):
        point = [[x1, y1], [x2, y2], [x3, y3], cont]
        path = self.paths[-1]
        points = path[1]
        if path[0] is None:
            path[0] = point[0]
        else:
            points.append(point)

    def bn(self):
        self.paths.append([None, [], sk_const.CURVE_OPENED])

    def bC(self):
        self.paths[-1][2] = sk_const.CURVE_CLOSED

    def txt(self, text, trafo, horiz_align=sk_const.ALIGN_LEFT,
            vert_align=sk_const.ALIGN_BASE):
        if not text:
            return
        obj = sk_model.SKText(text, trafo, horiz_align, vert_align)
        self.set_style(obj)
        self.add_object(obj)

    def bm(self, obj_id, filename=None):
        bmd_obj = sk_model.SKBitmapData(obj_id)
        self.add_object(bmd_obj)
        if filename is None:
            try:
                bmd_obj.read_data(self.fileptr)
            except Exception as e:
                LOG.error('Error reading bitmap "%s"', self.line)
                LOG.error('Error traceback: %s', e)
        elif self.filepath:
            image_dir = os.path.dirname(self.filepath)
            image_path = os.path.join(image_dir, filename)
            bmd_obj.load_data(image_path)
        if bmd_obj.raw_image:
            self.presenter.resources[obj_id] = bmd_obj.raw_image

    def im(self, trafo, obj_id):
        if len(trafo) == 2:
            trafo = (1.0, 0.0, 0.0, 1.0) + trafo
        trafo = sk_model.Trafo(*trafo)
        image = None
        if obj_id in self.presenter.resources:
            image = self.presenter.resources[obj_id]
        self.add_object(sk_model.SKImage(trafo, obj_id, image))

    def eps(self, *args):
        self.string = ''


class SK_Saver(AbstractSaver):
    name = 'SK_Saver'

    def do_save(self):
        self.model.write_content(self.fileptr)
