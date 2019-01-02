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

import os
from PIL import Image
from base64 import b64decode, b64encode
from cStringIO import StringIO
from copy import deepcopy

from uc2 import _, uc2const
from uc2.formats.generic import TextModelObject
from uc2.formats.sk import sk_const

# Document object enumeration
DOCUMENT = 1
LAYOUT = 2
GRID = 3
LAYER = 6
GUIDELAYER = 8
GUIDE = 9

STYLE = 10

GROUP = 20
MASKGROUP = 21

RECTANGLE = 30
ELLIPSE = 31
CURVE = 32
TEXT = 33
BITMAPDATA = 34
IMAGE = 35

CID_TO_NAME = {
    DOCUMENT: _('Document'), LAYOUT: _('Layout'), GRID: _('Grid'),
    LAYER: _('Layer'),
    GUIDELAYER: _('GuideLayer'), GUIDE: _('Guideline'),

    STYLE: _('Style'),
    GROUP: _('Group'), MASKGROUP: _('MaskGroup'),

    RECTANGLE: _('Rectangle'), ELLIPSE: _('Ellipse'), CURVE: _('Curve'),
    TEXT: _('Text'), BITMAPDATA: _('BitmapData'), IMAGE: _('Image'),
}


class Trafo(object):

    def __init__(self, m11, m12, m21, m22, v1, v2):
        self.m11 = m11
        self.m12 = m12
        self.m21 = m21
        self.m22 = m22
        self.v1 = v1
        self.v2 = v2

    def coeff(self):
        return self.m11, self.m12, self.m21, self.m22, self.v1, self.v2


class Scale(object):
    pass


class Translation(object):
    pass


def CreatePath():
    return ()


class Point(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y


class SKModelObject(TextModelObject):
    """
    Abstract class for SK1 model objects.
    Defines common object functionality
    """

    objects = []
    properties = None

    def __init__(self, config=None, string=''):
        self.config = config
        self.childs = []
        self.objects = self.childs
        if string:
            self.string = string

    def resolve(self):
        is_leaf = True
        if self.cid < RECTANGLE: is_leaf = False
        if self.cid == GUIDE or self.cid == LAYOUT: is_leaf = True
        name = CID_TO_NAME[self.cid]
        info = ''
        if not is_leaf:
            info = len(self.childs)
        return is_leaf, name, info

    def get_content(self):
        result = self.string
        for child in self.childs:
            result += child.get_content()
        if self.end_string:
            result += self.end_string
        return result

    def write_content(self, fileobj):
        if self.properties is not None:
            self.properties.write_content(fileobj)
        fileobj.write(self.string)
        for child in self.childs:
            child.write_content(fileobj)
        if self.end_string:
            fileobj.write(self.end_string)


# --- STRUCTURAL OBJECTS
class MetaInfo(object):
    pass


class SKDocument(SKModelObject):
    """
    Represents SK1 model root object.
    """

    string = '##Sketch 1 2\ndocument()\n'
    doc_units = uc2const.UNIT_MM
    cid = DOCUMENT
    layout = None
    grid = None
    guidelayer = None
    meta = None
    styles = {}

    def __init__(self, config=None):
        self.meta = MetaInfo()
        SKModelObject.__init__(self, config)


class SKLayout(SKModelObject):
    """
    Represents Layout object.
    The object defines default page size as:
        (format_name,orientation)
    for known page format or:
        ((width,height),orientation)
    for user defined page format.
    """

    string = "layout('A4',0)\n"
    cid = LAYOUT
    format = 'A4'
    size = sk_const.PAGE_FORMATS['A4']
    orientation = uc2const.PORTRAIT

    def __init__(self, fmt='', size=(), orientation=uc2const.PORTRAIT):
        self.format = fmt
        self.size = size
        self.orientation = orientation
        SKModelObject.__init__(self)

    def update(self):
        if self.format in sk_const.PAGE_FORMATS.keys():
            args = (self.format, self.orientation)
        else:
            args = (self.size, self.orientation)
        self.string = 'layout' + args.__str__() + '\n'


class SKLayer(SKModelObject):
    """
    Represents Layer object.
    Layer values are defined as:
    (layer_name,visible,printable,locked,outlined,layer_color)
    """
    string = "layer('Layer 1',1,1,0,0,(0.196,0.314,0.635))\n"
    cid = LAYER
    name = ''
    layer_properties = []
    layer_color = sk_const.default_layer_color
    visible = 1
    printable = 1
    locked = 0
    outlined = 0

    def __init__(self, name=_("New Layer"),
                 visible=1, printable=1, locked=0,
                 outlined=0, outline_color=sk_const.default_layer_color):
        self.name = name
        self.visible = visible
        self.printable = printable
        self.locked = locked
        self.outlined = outlined
        self.layer_color = outline_color
        SKModelObject.__init__(self)

    def update(self):
        args = (self.name, self.visible, self.printable, self.locked,
                self.outlined, self.layer_color)
        self.string = 'layer' + args.__str__() + '\n'


class SKGuideLayer(SKModelObject):
    """
    Represents GuideLayer object.
    Layer values are defined as:
    (layer_name,visible,printable,locked,outlined,layer_color)
    """
    string = "guidelayer('Guide Lines',1,0,0,1,(0.0,0.3,1.0))\n"
    cid = GUIDELAYER
    name = 'GuideLayer'
    layer_properties = []
    layer_color = sk_const.default_guidelayer_color
    visible = 1
    printable = 0
    locked = 0
    outlined = 0

    def __init__(self, name=_("GuideLayer"),
                 visible=1, printable=0, locked=0,
                 outlined=0, outline_color=sk_const.default_layer_color):
        self.name = name
        self.visible = visible
        self.printable = printable
        self.locked = locked
        self.outlined = outlined
        self.layer_color = outline_color
        SKModelObject.__init__(self)

    def update(self):
        args = (self.name, self.visible, self.printable, self.locked,
                self.outlined, self.layer_color)
        self.string = 'guidelayer' + args.__str__() + '\n'


class SKGrid(SKModelObject):
    """
    Represents Grid layer object.
    Grid values are defined as:
    (grid,visibility,grid_color,layer_name)
    where:
    grid=(start_x, start_y, dx, dy)
    grid_color=(color values)
    """
    string = 'grid((0,0,2.83465,2.83465),0,(0.83,0.87,0.91),\'Grid\')\n'
    cid = GRID
    geometry = sk_const.default_grid
    visible = 0
    printable = 0
    locked = 0
    grid_color = sk_const.default_grid_color
    name = 'Grid'
    is_GridLayer = 1

    def __init__(self, geometry=sk_const.default_grid, visible=0,
                 grid_color=sk_const.default_grid_color, name=_("Grid")):
        if len(geometry) == 2:
            self.geometry = (0, 0) + geometry
        elif len(geometry) == 4:
            self.geometry = geometry
        else:
            self.geometry = sk_const.default_grid
        self.visible = visible
        self.grid_color = grid_color
        self.name = name
        SKModelObject.__init__(self)

    def update(self):
        args = (self.geometry, self.visible, self.grid_color, self.name)
        self.string = 'grid' + args.__str__() + '\n'


class SKGuide(SKModelObject):
    """
    Represents Guideline object.
    Guideline values are defined as:
    (position,orientation)
    """
    string = "guide(0.0,0)\n"
    cid = GUIDE
    position = 0
    orientation = uc2const.HORIZONTAL
    is_GuideLine = 1

    def __init__(self, position, orientation=uc2const.HORIZONTAL):
        self.position = position
        self.orientation = orientation
        SKModelObject.__init__(self)

    def update(self):
        args = (self.position, self.orientation)
        self.string = 'guide' + args.__str__() + '\n'


# --- PROPERTIES OBJECTS

class Pattern:
    is_procedural = 1
    is_Empty = 0
    is_Solid = 0
    is_Gradient = 0
    is_RadialGradient = 0
    is_AxialGradient = 0
    is_ConicalGradient = 0
    is_Hatching = 0
    is_Tiled = 0
    is_Image = 0

    name = ''


class EmptyPattern_(Pattern):
    is_procedural = 0
    is_Empty = 1


EmptyPattern = EmptyPattern_()


class SolidPattern(Pattern):
    is_procedural = 0
    is_Solid = 1
    color = ()

    def __init__(self, color=None, duplicate=None):
        if color:
            self.color = color
        else:
            self.color = deepcopy(sk_const.fallback_skcolor)

    def copy(self):
        return SolidPattern(deepcopy(self.color))


class MultiGradient:
    colors = []

    def __init__(self, colors=None, duplicate=None):
        colors = colors or []
        if not colors:
            start_color = deepcopy(sk_const.black_color)
            end_color = deepcopy(sk_const.white_color)
            colors = [(0, start_color), (1, end_color)]
        self.colors = colors

    def copy(self):
        return MultiGradient(deepcopy(self.colors))

    def write_content(self, fileobj):
        val = self.colors.__str__()
        write = fileobj.write
        write('gl(' + val + ')\n')


def CreateSimpleGradient(start_color, end_color):
    return MultiGradient([(0, start_color), (1, end_color)])


class GradientPattern(Pattern):
    is_Gradient = 1


class LinearGradient(GradientPattern):
    is_AxialGradient = 1

    def __init__(self, gradient=None, direction=Point(0, -1),
                 border=0, duplicate=None):
        self.gradient = gradient
        self.direction = direction
        self.border = border

    def copy(self):
        gradient = self.gradient.copy()
        direction = Point(self.direction.x, self.direction.y)
        border = self.border
        return LinearGradient(gradient, direction, border)

    def write_content(self, fileobj):
        self.gradient.write_content(fileobj)
        fileobj.write('pgl(%g,%g,%g)\n' % (round(self.direction.x, 10),
                                           round(self.direction.y, 10),
                                           self.border))


class RadialGradient(GradientPattern):
    is_RadialGradient = 1

    def __init__(self, gradient=None, center=Point(0.5, 0.5),
                 border=0, duplicate=None):
        self.gradient = gradient
        self.center = center
        self.border = border

    def copy(self):
        gradient = self.gradient.copy()
        center = Point(self.center.x, self.center.y)
        border = self.border
        return RadialGradient(gradient, center, border)

    def write_content(self, fileobj):
        self.gradient.write_content(fileobj)
        fileobj.write('pgr(%g,%g,%g)\n' % (self.center.x,
                                           self.center.y, self.border))


class ConicalGradient(GradientPattern):
    is_ConicalGradient = 1

    def __init__(self, gradient=None,
                 center=Point(0.5, 0.5), direction=Point(1, 0),
                 duplicate=None):
        self.gradient = gradient
        self.center = center
        self.direction = direction

    def copy(self):
        gradient = self.gradient.copy()
        center = Point(self.center.x, self.center.y)
        direction = Point(self.direction.x, self.direction.y)
        return ConicalGradient(gradient, center, direction)

    def write_content(self, fileobj):
        self.gradient.write_content(fileobj)
        fileobj.write('pgc(%g,%g,%g,%g)\n' % (self.center.x, self.center.y,
                                              round(self.direction.x, 10),
                                              round(self.direction.y, 10)))


class HatchingPattern(Pattern):
    is_Hatching = 1

    def __init__(self, foreground=None, background=None,
                 direction=Point(1, 0),
                 spacing=5.0, width=0.5, duplicate=None):
        if foreground is None:
            foreground = deepcopy(sk_const.black_color)
        self.foreground = foreground
        if background is None:
            background = deepcopy(sk_const.white_color)
        self.background = background
        self.spacing = spacing
        self.width = width
        self.direction = direction

    def copy(self):
        foreground = deepcopy(self.foreground)
        background = deepcopy(self.background)
        spacing = self.spacing
        width = self.width
        direction = Point(self.direction.x, self.direction.y)
        return HatchingPattern(foreground, background, direction, spacing,
                               width)

    def write_content(self, fileptr):
        color = self.foreground.__str__()
        background = self.background.__str__()
        # TODO: check spacing field
        fileptr.write('phs(%s,%s,%g,%g,%g,%g)\n'
                      % (color, background,
                         self.direction.x, self.direction.y,
                         self.spacing, self.width))


class ImageTilePattern(Pattern):
    is_Tiled = 1
    is_Image = 1
    data = None
    bid = None
    raw_image = None

    def __init__(self, data=None, trafo=None, duplicate=None):
        if trafo is None:
            trafo = Trafo(1, 0, 0, -1, 0, 0)
        self.trafo = trafo
        self.data = data
        self.image = self.data

    def copy(self):
        trafo = Trafo(*self.trafo.coef())
        image = self.image.copy()
        return ImageTilePattern(image, trafo)

    def write_content(self, fileptr):
        if self.image and not self.bid:
            self.bid = id(self.image)
        if self.image:
            fileptr.write('bm(%d)\n' % self.bid)

            image_stream = StringIO()
            if self.raw_image.mode == "CMYK":
                self.raw_image.save(image_stream, 'JPEG', quality=100)
            else:
                self.raw_image.save(image_stream, 'PNG')
            fileptr.write(b64encode(image_stream.getvalue()))

            fileptr.write('-\n')
            val = (self.bid, self.trafo.coeff()).__str__()
            fileptr.write('pit' + val + '\n')


class Style:
    """
    Represents object style.
    """

    is_dynamic = 0
    name = ''

    fill_pattern = EmptyPattern
    fill_transform = 1
    line_pattern = SolidPattern(deepcopy(sk_const.black_color))
    line_width = 0.28
    line_join = sk_const.JoinMiter
    line_cap = sk_const.CapButt
    line_dashes = ()
    line_arrow1 = None
    line_arrow2 = None
    font = None
    font_face = None
    font_size = 12.0

    def __init__(self, name='', duplicate=None, base_style=False, **kw):
        if name:
            self.name = name
        if base_style:
            self.fill_pattern = EmptyPattern
            self.fill_transform = 1
            color = deepcopy(sk_const.black_color)
            self.line_pattern = SolidPattern(color)
            self.line_width = 0.0
            self.line_join = sk_const.JoinMiter
            self.line_cap = sk_const.CapButt
            self.line_dashes = ()
            self.line_arrow1 = None
            self.line_arrow2 = None
            self.font = None
            self.font_size = 12.0
        else:
            for key, value in kw.items():
                setattr(self, key, value)

    def copy(self):
        style_copy = Style(self.name + '')
        pattern = self.fill_pattern
        if pattern is None:
            style_copy.fill_pattern = None
        elif pattern is EmptyPattern:
            style_copy.fill_pattern = EmptyPattern
        else:
            style_copy.fill_pattern = pattern.copy()
        pattern = self.line_pattern
        if pattern is None:
            style_copy.line_pattern = None
        elif pattern is EmptyPattern:
            style_copy.line_pattern = EmptyPattern
        else:
            style_copy.line_pattern = pattern.copy()
        style_copy.fill_transform = self.fill_transform
        style_copy.line_width = self.line_width
        style_copy.line_join = self.line_join
        style_copy.line_cap = self.line_cap
        if self.line_dashes:
            style_copy.line_dashes = deepcopy(self.line_dashes)
        if self.line_arrow1:
            style_copy.line_arrow1 = deepcopy(self.line_arrow1)
        if self.line_arrow2:
            style_copy.line_arrow2 = deepcopy(self.line_arrow2)
        if self.font:
            style_copy.font = self.font
        style_copy.font_size = self.font_size
        return style_copy

    def __str__(self):
        result = '<uc2.formats.sk1.model.Style instance>:\n'
        for item in self.__dict__.keys():
            result += item + '=' + str(self.__dict__[item]) + '\n'
        return result

    def write_content(self, fileobj):
        write = fileobj.write
        if hasattr(self, 'fill_pattern'):
            pattern = self.fill_pattern
            if pattern is EmptyPattern:
                write('fe()\n')
            elif isinstance(pattern, SolidPattern):
                write('fp(' + pattern.color.__str__() + ')\n')
            else:
                pattern.write_content(fileobj)
                write('fp()\n')
        if not self.fill_transform:
            write('ft(%d)\n' % self.fill_transform)
        if hasattr(self, 'line_pattern'):
            pattern = self.line_pattern
            if pattern is EmptyPattern:
                write('le()\n')
            elif isinstance(pattern, SolidPattern):
                write('lp(' + pattern.color.__str__() + ')\n')
            else:
                pattern.write_content(fileobj)
                write('lp()\n')
        if self.line_width:
            write('lw(%g)\n' % self.line_width)
        if not self.line_cap == sk_const.CapButt:
            write('lc(%d)\n' % self.line_cap)
        if not self.line_join == sk_const.JoinMiter:
            write('lj(%d)\n' % self.line_join)
        if self.line_dashes:
            write('ld(' + self.line_dashes.__str__() + ')\n')
        if self.line_arrow1:
            if self.line_arrow1 is not None:
                write('la1(' + self.line_arrow1.__str__() + ')\n')
            else:
                write('la1()\n')
        if self.line_arrow2:
            if self.line_arrow2 is not None:
                write('la2(' + self.line_arrow2.__str__() + ')\n')
            else:
                write('la2()\n')
        if self.font:
            write('Fn(\'%s\')\n' % self.font)
        if not self.font_size == 12:
            write('Fs(%g)\n' % self.font_size)


# --- SELECTABLE OBJECTS

class SKGroup(SKModelObject):
    """
    Represents Group object.
    All nested objects are in childs list.
    """
    string = 'G()\n'
    end_string = 'G_()\n'
    cid = GROUP

    def __init__(self):
        SKModelObject.__init__(self)


class SKMaskGroup(SKModelObject):
    """
    Represents MaskGroup object.
    All nested objects are in childs list.
    The first object in childs list is the mask.
    """
    string = 'M()\n'
    end_string = 'M_()\n'
    cid = MASKGROUP

    def __init__(self):
        SKModelObject.__init__(self)


# BlendGroup
# TextOnPath
# CompoundObject

# --- Primitive objects

class SKRectangle(SKModelObject):
    """
    Represents Rectangle object.
    r(TRAFO [, RADIUS1, RADIUS2])
    """
    string = ''
    cid = RECTANGLE
    style = []
    properties = None
    trafo = None
    radius1 = 0
    radius2 = 0

    is_Rectangle = 1

    def __init__(self, trafo=None, radius1=0, radius2=0,
                 properties=None, duplicate=None):

        if trafo is not None and trafo.m11 == trafo.m21 == trafo.m12 == trafo.m22 == 0:
            trafo = Trafo(1, 0, 0, -1, trafo.v1, trafo.v2)
        self.trafo = trafo
        self.radius1 = radius1
        self.radius2 = radius2
        self.properties = properties
        SKModelObject.__init__(self)

    def update(self):
        if self.radius1 == self.radius2 == 0:
            args = self.trafo.coeff()
            self.string = 'r' + args.__str__() + '\n'
        else:
            args = self.trafo.coeff() + (self.radius1, self.radius2)
            self.string = 'r' + args.__str__() + '\n'


class SKEllipse(SKModelObject):
    """
    Represents Ellipse object.
    e(TRAFO, [start_angle, end_angle, arc_type])
    """
    string = ''
    cid = ELLIPSE
    style = []
    properties = None
    trafo = None
    start_angle = 0.0
    end_angle = 0.0
    arc_type = sk_const.ArcPieSlice

    is_Ellipse = 1

    def __init__(self, trafo=None, start_angle=0.0, end_angle=0.0,
                 arc_type=sk_const.ArcPieSlice, properties=None,
                 duplicate=None):

        if trafo is not None and trafo.m11 == trafo.m21 == trafo.m12 == trafo.m22 == 0:
            trafo = Trafo(1, 0, 0, -1, trafo.v1, trafo.v2)
        self.trafo = trafo
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.arc_type = arc_type
        self.properties = properties
        SKModelObject.__init__(self)

    def update(self):
        if self.start_angle == self.end_angle:
            args = self.trafo.coeff()
            self.string = 'e' + args.__str__() + '\n'
        else:
            args = self.trafo.coeff() + (
                self.start_angle, self.end_angle, self.arc_type)
            self.string = 'e' + args.__str__() + '\n'


class SKPolyBezier(SKModelObject):
    """
    Represents Bezier curve object.
    b()			 start a bezier obj
    bs(X, Y, CONT)  append a line segment
    bc(X1, Y1, X2, Y2, X3, Y3, CONT)  append a bezier segment
    bn()			start a new path
    bC()			close path
    """
    string = ''
    cid = CURVE
    style = []
    properties = None
    paths = None

    is_Bezier = 1

    def __init__(self, paths_list=[], properties=None):
        self.properties = properties
        self.paths_list = paths_list
        SKModelObject.__init__(self)

    def get_line_point(self, x, y, arg):
        return [x, y]

    def get_segment_point(self, x0, y0, x1, y1, x2, y2, cont):
        return [[x0, y0], [x1, y1], [x2, y2], cont]

    def add_line(self, point):
        x, y = point
        self.string += 'bs' + (x, y, 0).__str__() + '\n'

    def add_segment(self, point):
        point0, point1, point2, cont = point
        args = (
            point0[0], point0[1], point1[0], point1[1], point2[0], point2[1],
            cont)
        self.string += 'bc' + args.__str__() + '\n'

    def update(self):
        self.string = 'b()\n'
        start = True
        for path in self.paths_list:
            if start:
                start = False
            else:
                self.string += 'bn()\n'
            self.add_line(path[0])
            for point in path[1]:
                if len(point) == 2:
                    self.add_line(point)
                else:
                    self.add_segment(point)
            if path[2] == sk_const.CURVE_CLOSED:
                self.add_line(path[0])
                self.string += 'bC()\n'


class SKText(SKModelObject):
    """
    Represents Text object.
    txt(TEXT, TRAFO[, HORIZ_ALIGN, VERT_ALIGN])
    """
    string = ''
    cid = TEXT
    style = []
    text = ''
    trafo = ()
    properties = None
    horiz_align = sk_const.ALIGN_LEFT
    vert_align = sk_const.ALIGN_BASE

    def __init__(self, text, trafo, horiz_align=sk_const.ALIGN_LEFT,
                 vert_align=sk_const.ALIGN_BASE):
        self.text = text
        self.trafo = trafo
        self.horiz_align = horiz_align
        self.vert_align = vert_align
        SKModelObject.__init__(self)

    def update(self):
        args = (self.text, self.trafo, self.horiz_align, self.vert_align)
        self.string = 'txt' + args.__str__() + '\n'


class SKBitmapData(SKModelObject):
    """
    Bitmap image data. Object is defined as:

    bm(BID)

    The bitmap data follows as a base64 encoded JPEG file.
    """
    string = ''
    cid = BITMAPDATA
    raw_image = None
    bid = ''

    def __init__(self, bid=''):
        if bid: self.bid = bid
        SKModelObject.__init__(self)

    def read_data(self, fileptr):
        raw = ''
        while True:
            line = fileptr.readline().strip()
            if line == '-': break
            raw += line
        self.raw_image = Image.open(StringIO(b64decode(raw)))
        self.raw_image.load()

    def load_data(self, image_path):
        if os.path.lexists(image_path):
            self.raw_image = Image.open(image_path)
            self.raw_image.load()

    def update(self):
        self.string = 'bm(%d)\n' % (self.bid)
        self.end_string = '-\n'

    def write_content(self, fileptr):
        return


class SKImage(SKModelObject):
    """
    Image object. ID has to be the bid of a previously defined
    bitmap data object (defined by bm). The object is defined as:
    im(TRAFO, BID)
    """
    string = ''
    cid = IMAGE
    trafo = ()
    bid = ''
    image = None

    def __init__(self, trafo=None, bid='', image=None):
        self.trafo = trafo
        self.bid = bid
        self.image = image
        SKModelObject.__init__(self)

    def update(self):
        if self.image and not self.bid:
            self.bid = id(self.image)
        self.string = 'im' + (self.trafo.coeff(), self.bid).__str__() + '\n'

    def write_content(self, fileptr):
        if self.image:
            fileptr.write('bm(%d)\n' % (self.bid))

            image_stream = StringIO()
            self.image.save(image_stream, 'PNG')
            fileptr.write(b64encode(image_stream.getvalue()))

            fileptr.write('-\n')
            fileptr.write(self.string)
