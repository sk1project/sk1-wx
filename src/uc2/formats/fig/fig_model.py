# -*- coding: utf-8 -*-
#
#  Copyright (C) 2018 by Maxim S. Barabash
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


from uc2.formats.generic import TextModelObject
from uc2.formats.fig import fig_const, figlib


FIG = 'FIG'
OBJ_FORWARD_ARROW = 'ForwardArrow'
OBJ_BACKWARD_ARROW = 'BackwardArrow'
OBJ_PICTURE = 'Picture'

OBJ_COLOR_DEF = 0
OBJ_ELLIPSE = 1
OBJ_POLYLINE = 2
OBJ_SPLINE = 3
OBJ_TEXT = 4
OBJ_ARC = 5
OBJ_COMPOUND = 6
OBJ_COMPOUND_ENDS = -6

STR_TERMINATOR = chr(1)


CID_TO_NAME = {
    FIG: FIG,
    OBJ_FORWARD_ARROW: OBJ_FORWARD_ARROW,
    OBJ_BACKWARD_ARROW: OBJ_BACKWARD_ARROW,
    OBJ_PICTURE: OBJ_PICTURE,
    OBJ_COLOR_DEF: 'COLOR',
    OBJ_ELLIPSE: 'ELLIPSE',
    OBJ_POLYLINE: 'POLYLINE',
    OBJ_SPLINE: 'SPLINE',
    OBJ_TEXT: 'TEXT',
    OBJ_ARC: 'ARC',
    OBJ_COMPOUND: 'COMPOUND'
}


class FIGModelObject(TextModelObject):
    """
    Generic FIG model object.
    Provides common functionality for all model objects.
    """
    comment = None

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def resolve(self):
        is_leaf = not bool(self.childs)
        name = CID_TO_NAME[self.cid]
        info = ''
        return is_leaf, name, info

    def parse(self, loader, chunk=None):
        chunk = chunk or loader.get_line()
        self.childs = []
        self.comment = loader.pop_comment()
        return chunk

    def save(self, saver):
        if self.comment:
            comment = self.comment.replace('\n', '\n# ')
            saver.write('# %s\n' % comment)


class FIGArrow(FIGModelObject):
    """
    Arrow line (Optional):

    type    name           (brief description)
    ----    ----           -------------------
    int    arrow_type      (enumeration type)
    int    arrow_style     (enumeration type)
    float  arrow_thickness (1/80 inch)
    float  arrow_width     (Fig units)
    float  arrow_height    (Fig units)
    """
    cid = None
    type = 0
    style = 0
    thickness = 1.0
    width = 0.0
    height = 0.0

    _names32 = (
        'type', 'style', 'thickness', 'width', 'height'
    )
    _frm32 = 'iifff'

    def parse(self, loader, chunk=None):
        chunk = chunk or loader.readln()
        s = figlib.unpack(self._frm32, chunk)
        data = dict(zip(self._names32, s))
        self.__dict__.update(data)

    def save(self, saver):
        FIGModelObject.save(self, saver)
        data = [getattr(self, name) for name in self._names32]
        line = figlib.pack(data, self._frm32)
        saver.write('%s\n' % line)


class FIGFArrow(FIGArrow):
    cid = OBJ_FORWARD_ARROW


class FIGBArrow(FIGArrow):
    cid = OBJ_BACKWARD_ARROW


class FIGPicture(FIGModelObject):
    """
    type    name           (brief description)
    ----    ----           -------------------
    boolean flipped        orientation = normal (0) or flipped (1)
    char    file[]         name of picture file to import
    """
    cid = OBJ_PICTURE
    flipped = 0
    file = ''
    _names32 = ('flipped', 'file')
    _frm32 = 'is'

    def parse(self, loader, chunk=None):
        chunk = chunk or loader.readln()
        s = figlib.unpack(self._frm32, chunk)
        data = dict(zip(self._names32, s))
        self.__dict__.update(data)

    def save(self, saver):
        FIGModelObject.save(self, saver)
        data = [getattr(self, name) for name in self._names32]
        line = figlib.pack(data, self._frm32)
        saver.write('\t %s\n' % line)


class FIGColorDef(FIGModelObject):
    """
    Color pseudo-object.

    First line:
    type   name            (brief description)
    ----   ----            -------------------
    int    cid             (always 0)
    int    idx             (color number, from 32-543 (512 total))
    string rgb values      (hexadecimal string describing red,
                            green and blue values (e.g. #330099) )
    """
    cid = OBJ_COLOR_DEF
    idx = None
    hexcolor = None
    _names32 = ('cid', 'idx', 'hexcolor')
    _frm32 = 'iis'

    def parse(self, loader, chunk=None):
        chunk = chunk or loader.readln()
        s = figlib.unpack(self._frm32, chunk.strip())
        data = dict(zip(self._names32, s))
        self.__dict__.update(data)

    def save(self, saver):
        FIGModelObject.save(self, saver)
        data = [getattr(self, name) for name in self._names32]
        line = figlib.pack(data, self._frm32)
        saver.write('%s\n' % line)


class FIGEllipse(FIGModelObject):
    """
    Ellipse which is a generalization of circle.

    First line:
    type   name               (brief description)
    ----   ----               -------------------
    int    cid                (always 1)
    int    sub_type           (1: ellipse defined by radii
                               2: ellipse defined by diameters
                               3: circle defined by radius
                               4: circle defined by diameter)
    int    line_style         (enumeration type)
    int    thickness          (1/80 inch)
    int    pen_color          (enumeration type, pen color)
    int    fill_color         (enumeration type, fill color)
    int    depth              (enumeration type)
    int    pen_style          (pen style, not used)
    int    area_fill          (enumeration type, -1 = no fill)
    float  style_val          (1/80 inch)

    int    direction          (always 1)
    float  angle              (radians, the angle of the x-axis)
    int    center_x, center_y (Fig units)
    int    radius_x, radius_y (Fig units)
    int    start_x, start_y   (Fig units; the 1st point entered)
    int    end_x, end_y       (Fig units; the last point entered)
    """
    cid = OBJ_ELLIPSE
    sub_type = fig_const.T_CIRCLE_BY_RAD
    line_style = fig_const.SOLID_LINE
    thickness = 1
    pen_color = fig_const.BLACK_COLOR
    fill_color = fig_const.WHITE_COLOR
    depth = 50
    pen_style = -1
    area_fill = fig_const.NO_FILL
    style_val = 0.0

    direction = 1
    angle = 0.0
    center_x = 0
    center_y = 0
    radius_x = 0
    radius_y = 0
    start_x = 0
    start_y = 0
    end_x = 0
    end_y = 0
    _names32 = (
        'cid', 'sub_type', 'line_style', 'thickness', 'pen_color',
        'fill_color', 'depth', 'pen_style', 'area_fill', 'style_val',
        'direction', 'angle', 'center_x', 'center_y', 'radius_x',
        'radius_y', 'start_x', 'start_y', 'end_x', 'end_y'
    )
    _frm32 = 'iiiiiiiiififiiiiiiii'

    def parse(self, loader, chunk=None):
        chunk = FIGModelObject.parse(self, loader, chunk)
        s = figlib.unpack(self._frm32, chunk)
        data = dict(zip(self._names32, s))
        self.__dict__.update(data)

    def save(self, saver):
        FIGModelObject.save(self, saver)
        data = [getattr(self, name) for name in self._names32]
        line = figlib.pack(data, self._frm32)
        saver.write('%s\n' % line)


class FIGArc(FIGModelObject):
    """
    ARC

    First line:
    type   name               (brief description)
    ----   ----               -------------------
    int    object_code        (always 5)
    int    sub_type           (1: open ended arc
                               2: pie-wedge (closed) )
    int    line_style         (enumeration type)
    int    line_thickness     (1/80 inch)
    int    pen_color          (enumeration type, pen color)
    int    fill_color         (enumeration type, fill color)
    int    depth              (enumeration type)
    int    pen_style          (pen style, not used)
    int    area_fill          (enumeration type, -1 = no fill)
    float  style_val          (1/80 inch)

    int    cap_style          (enumeration type)
    int    direction          (0: clockwise, 1: counterclockwise)
    int    forward_arrow      (0: no forward arrow, 1: on)
    int    backward_arrow     (0: no backward arrow, 1: on)

    float  center_x, center_y (center of the arc)
    int    x1, y1             (Fig units, the 1st point the user entered)
    int    x2, y2             (Fig units, the 2nd point)
    int    x3, y3             (Fig units, the last point)

    Forward arrow line (Optional; absent if forward_arrow is 0):
    type    name              (brief description)
    ----    ----              -------------------
    int    arrow_type         (enumeration type)
    int    arrow_style        (enumeration type)
    float  arrow_thickness    (1/80 inch)
    float  arrow_width        (Fig units)
    float  arrow_height       (Fig units)

    Backward arrow line (Optional; absent if backward_arrow is 0):
    type    name              (brief description)
    ----    ----              -------------------
    int    arrow_type         (enumeration type)
    int    arrow_style        (enumeration type)
    float  arrow_thickness    (1/80 inch)
    float  arrow_width        (Fig units)
    float  arrow_height       (Fig units)
    """
    cid = OBJ_ARC
    sub_type = fig_const.T_OPEN_ARC
    line_style = fig_const.SOLID_LINE
    thickness = 1
    pen_color = fig_const.BLACK_COLOR
    fill_color = fig_const.WHITE_COLOR
    depth = 50
    pen_style = -1
    area_fill = fig_const.NO_FILL
    style_val = 0.0

    cap_style = -1
    direction = -1
    forward_arrow = 0
    backward_arrow = 0
    center_x = 0
    center_y = 0

    x1 = 0
    y1 = 0
    x2 = 0
    y2 = 0
    x3 = 0
    y3 = 0
    _names32 = (
        'cid', 'sub_type', 'line_style', 'thickness', 'pen_color', 'fill_color',
        'depth', 'pen_style', 'area_fill', 'style_val', 'cap_style',
        'direction', 'forward_arrow', 'backward_arrow', 'center_x', 'center_y',
        'x1', 'y1', 'x2', 'y2', 'x3', 'y3'
    )
    _frm32 = 'iiiiiiiiifiiiiffiiiiii'

    def parse(self, loader, chunk=None):
        chunk = FIGModelObject.parse(self, loader, chunk)
        s = figlib.unpack(self._frm32, chunk)
        data = dict(zip(self._names32, s))
        self.__dict__.update(data)

        if self.forward_arrow:
            fa = FIGFArrow()
            fa.parse(loader)
            self.childs.append(fa)
        if self.backward_arrow:
            fb = FIGBArrow()
            fb.parse(loader)
            self.childs.append(fb)

    def save(self, saver):
        FIGModelObject.save(self, saver)
        data = [getattr(self, name) for name in self._names32]
        line = figlib.pack(data, self._frm32)
        saver.write('%s\n' % line)
        for item in self.childs:
            item.save(saver)


class FIGPolyline(FIGModelObject):
    """
    Polyline which includes polygon and box.

    First line:
    type   name               (brief description)
    ----   ----               -------------------
    int    cid                (always 2)
    int    sub_type           (1: polyline
                               2: box
                               3: polygon
                               4: arc-box
                               5: imported-picture bounding-box)
    int    line_style         (enumeration type)
    int    thickness          (1/80 inch)
    int    pen_color          (enumeration type, pen color)
    int    fill_color         (enumeration type, fill color)
    int    depth              (enumeration type)
    int    pen_style          (pen style, not used)
    int    area_fill          (enumeration type, -1 = no fill)
    float  style_val          (1/80 inch)

    int    join_style         (enumeration type)

    int    cap_style          (enumeration type, only used for POLYLINE)
    int    radius             (1/80 inch, radius of arc-boxes)
    int    forward_arrow      (0: off, 1: on)
    int    backward_arrow     (0: off, 1: on)

    int    npoints            (number of points in line)

    Forward arrow line: same as ARC object

    Backward arrow line: same as ARC object

    For picture (type 5) the following line follows:
    type    name              (brief description)
    ----    ----              -------------------
    boolean flipped           orientation = normal (0) or flipped (1)
    char    file[]            name of picture file to import

    Points line(s).  The x,y coordinates follow, any number to a line, with
    as many lines as are necessary:
    type    name              (brief description)
    ----    ----              -------------------
    int    x1, y1             (fig units)
    int    x2, y2             (fig units)
      .
      .
    int    xnpoints ynpoints  (this will be the same as the 1st
                               point for polygon and box)
    """
    cid = OBJ_POLYLINE
    sub_type = fig_const.T_POLYLINE
    line_style = fig_const.SOLID_LINE
    thickness = 1
    pen_color = fig_const.BLACK_COLOR
    fill_color = fig_const.WHITE_COLOR
    depth = 50
    pen_style = -1
    area_fill = fig_const.NO_FILL
    style_val = 0.0

    join_style = -1
    cap_style = -1  # T_POLYLINE
    radius = -1     # T_ARC_BOX
    forward_arrow = 0
    backward_arrow = 0
    npoints = 0

    points = None

    _names32 = (
        'cid', 'sub_type', 'line_style', 'thickness', 'pen_color', 'fill_color',
        'depth', 'pen_style', 'area_fill', 'style_val', 'join_style',
        'cap_style', 'radius', 'forward_arrow', 'backward_arrow', 'npoints'
    )
    _frm32 = 'iiiiiiiiifiiiiii'

    def parse(self, loader, chunk=None):
        chunk = FIGModelObject.parse(self, loader, chunk)
        s = figlib.unpack(self._frm32, chunk)
        data = dict(zip(self._names32, s))
        self.__dict__.update(data)

        if self.forward_arrow:
            fa = FIGFArrow()
            fa.parse(loader)
            self.childs.append(fa)
        if self.backward_arrow:
            fb = FIGBArrow()
            fb.parse(loader)
            self.childs.append(fb)
        if self.sub_type == fig_const.T_PIC_BOX:
            picture = FIGPicture()
            picture.parse(loader)
            self.childs.append(picture)

        self.points = []
        while len(self.points) < self.npoints:
            line = loader.readln()
            if line is None:
                raise Exception('Line is corrupted')
            data = line.split()
            items = ([int(x), int(y)] for x, y in figlib.list_chunks(data, 2))
            self.points.extend(items)

    def save(self, saver):
        FIGModelObject.save(self, saver)
        data = [getattr(self, name) for name in self._names32]
        line = figlib.pack(data, self._frm32)
        saver.write('%s\n' % line)
        for item in self.childs:
            item.save(saver)
        for chunk in figlib.list_chunks(self.points, 6):
            flat_list = [str(int(item)) for items in chunk for item in items]
            line = ' '.join(flat_list)
            saver.write('\t %s\n' % line)


class FIGSpline(FIGModelObject):
    """
    SPLINE

    First line:
    type   name             (brief description)
    ----   ----             -------------------
    int    cid              (always 3)
    int    sub_type         (0: open approximated spline
                             1: closed approximated spline
                             2: open   interpolated spline
                             3: closed interpolated spline
                             4: open   x-spline
                             5: closed x-spline)
    int    line_style        (See the end of this section)
    int    thickness         (1/80 inch)
    int    pen_color         (enumeration type, pen color)
    int    fill_color        (enumeration type, fill color)
    int    depth             (enumeration type)
    int    pen_style         (pen style, not used)
    int    area_fill         (enumeration type, -1 = no fill)
    float  style_val         (1/80 inch)

    int    cap_style         (enumeration type, only used for open splines)
    int    forward_arrow     (0: off, 1: on)
    int    backward_arrow    (0: off, 1: on)

    int    npoints           (number of control points in spline)

    Forward arrow line: same as ARC object

    Backward arrow line: same as ARC object

    Points line: same as POLYLINE object

    Control points line :

    There is one shape factor for each point. The value of this factor
    must be between -1 (which means that the spline is interpolated at
    this point) and 1 (which means that the spline is approximated at
    this point). The spline is always smooth in the neighbourhood of a
    control point, except when the value of the factor is 0 for which
    there is a first-order discontinuity (i.e. angular point).
    """
    cid = OBJ_SPLINE

    sub_type = fig_const.T_OPEN_APPROX
    line_style = fig_const.SOLID_LINE
    thickness = 1
    pen_color = fig_const.BLACK_COLOR
    fill_color = fig_const.WHITE_COLOR
    depth = 50
    pen_style = -1
    area_fill = fig_const.NO_FILL
    style_val = 0.0

    cap_style = -1
    forward_arrow = 0
    backward_arrow = 0

    npoints = 0

    points = None
    control_points = None

    _names32 = (
        'cid', 'sub_type', 'line_style', 'thickness', 'pen_color', 'fill_color',
        'depth', 'pen_style', 'area_fill', 'style_val', 'cap_style',
        'forward_arrow', 'backward_arrow', 'npoints'
    )
    _frm32 = 'iiiiiiiiifiiii'

    def parse(self, loader, chunk=None):
        chunk = FIGModelObject.parse(self, loader, chunk)
        s = figlib.unpack(self._frm32, chunk)
        data = dict(zip(self._names32, s))
        self.__dict__.update(data)
        self.sub_type = figlib.spline_sub_type(self.sub_type, loader.version)

        if self.forward_arrow:
            fa = FIGFArrow()
            fa.parse(loader)
            self.childs.append(fa)
        if self.backward_arrow:
            fb = FIGBArrow()
            fb.parse(loader)
            self.childs.append(fb)

        self.points = []
        while len(self.points) < self.npoints:
            line = loader.readln()
            if line is None:
                raise Exception('Line is corrupted')
            data = line.split()
            items = ([int(x), int(y)] for x, y in figlib.list_chunks(data, 2))
            self.points.extend(items)

        if self.sub_type in fig_const.T_INTERPOLATED:
            self.control_points = []
            ncontrols = self.npoints * 2
            while len(self.control_points) < ncontrols:
                line = loader.readln()
                if line is None:
                    raise Exception('Line is corrupted')
                data = line.split()
                items = ([float(x), float(y)] for x, y in
                         figlib.list_chunks(data, 2))
                self.control_points.extend(items)
        elif self.sub_type in fig_const.T_XSPLINE:
            self.control_points = []
            while len(self.control_points) < self.npoints:
                line = loader.readln()
                if line is None:
                    raise Exception('Line is corrupted')
                items = map(float, line.split())
                self.control_points.extend(items)

    def save(self, saver):
        FIGModelObject.save(self, saver)
        data = [getattr(self, name) for name in self._names32]
        line = figlib.pack(data, self._frm32)
        saver.write('%s\n' % line)
        for item in self.childs:
            item.save(saver)

        for chunk in figlib.list_chunks(self.points, 6):
            flat_list = [str(int(item)) for items in chunk for item in items]
            line = ' '.join(flat_list)
            saver.write('\t %s\n' % line)
        if self.sub_type in fig_const.T_INTERPOLATED:
            for chunk in figlib.list_chunks(self.control_points, 4):
                flat_list = ['{:1.2f} {:1.2f}'.format(*item) for item in chunk]
                line = ' '.join(flat_list)
                saver.write('\t %s\n' % line)
        elif self.sub_type in fig_const.T_XSPLINE:
            for chunk in figlib.list_chunks(self.control_points, 8):
                flat_list = ['%1.3f' % item for item in chunk]
                line = ' '.join(flat_list)
                saver.write('\t %s\n' % line)


class FIGText(FIGModelObject):
    """
    Text

    type   name               (brief description)
    ----   ----               -------------------
    int    cid                (always 4)
    int    sub_type           (0: Left justified
                               1: Center justified
                               2: Right justified)
    int    color              (enumeration type)
    int    depth              (enumeration type)
    int    pen_style          (enumeration , not used)
    int    font               (enumeration type)
    float  font_size          (font size in points)
    float  angle              (radians, the angle of the text)
    int    font_flags         (bit vector)
    float  height             (Fig units)
    float  length             (Fig units)
    int    x, y               (Fig units, coordinate of the origin
                               of the string.  If sub_type = 0, it is
                               the lower left corner of the string.
                               If sub_type = 1, it is the lower
                               center.  Otherwise it is the lower
                               right corner of the string.)
    char   string[]           (ASCII characters; starts after a blank
                               character following the last number and
                               ends before the sequence '\\001'.  This
                               sequence is not part of the string.
                               Characters above octal 177 are
                               represented by \\xxx where xxx is the
                               octal value.  This permits fig files to
                               be edited with 7-bit editors and sent
                               by e-mail without data loss.
                               Note that the string may contain '\\n'.)
    """
    cid = OBJ_TEXT
    sub_type = fig_const.T_LEFT_JUSTIFIED
    color = fig_const.BLACK_COLOR
    depth = 50
    pen_style = -1
    font = fig_const.DEFAULT_FONT
    font_size = 12
    angle = 0.0
    font_flags = fig_const.PSFONT_TEXT
    height = 0
    length = 0
    x = 0
    y = 0
    string = ''

    _names32 = (
        'cid', 'sub_type', 'color', 'depth', 'pen_style', 'font', 'font_size',
        'angle', 'font_flags', 'height', 'length', 'x', 'y', 'string'
    )
    _frm32 = 'iiiiiiffiffiis'

    def parse(self, loader, chunk=None):
        chunk = FIGModelObject.parse(self, loader, chunk)
        s = figlib.unpack(self._frm32, chunk)
        data = dict(zip(self._names32, s))
        text = data.pop('string').rstrip()
        self.__dict__.update(data)

        while not text.endswith(STR_TERMINATOR):
            line = loader.readln(strip=False).rstrip()
            if not line:
                raise Exception('Premature end of string')
            text += line

        self.string = text[:-len(STR_TERMINATOR)]

    def save(self, saver):
        FIGModelObject.save(self, saver)
        data = [getattr(self, name) for name in self._names32]
        line = figlib.pack(data, self._frm32)
        saver.write('{}{}\n'.format(line, STR_TERMINATOR))


class FIGCompound(FIGModelObject):
    """
    COMPOUND

    A line with object code 6 signifies the start of a compound.
    There are four more numbers on this line which indicate the
    upper left corner and the lower right corner of the bounding
    box of this compound.  A line with object code -6 signifies
    the end of the compound.  Compound may be nested.

    First line:
    type   name                  (brief description)
    ----   ----                  -------------------
    int    cid                   (always 6)
    int    upperleft_corner_x    (Fig units)
    int    upperleft_corner_y    (Fig units)
    int    lowerright_corner_x   (Fig units)
    int    lowerright_corner_y   (Fig units)
    """
    cid = OBJ_COMPOUND
    upperleft_corner_x = 0
    upperleft_corner_y = 0
    lowerright_corner_x = 0
    lowerright_corner_y = 0

    _names32 = (
        'cid',
        'upperleft_corner_x', 'upperleft_corner_y',
        'lowerright_corner_x', 'lowerright_corner_y'
    )
    _frm32 = 'iiiii'

    def parse(self, loader, chunk=None):
        chunk = FIGModelObject.parse(self, loader, chunk)
        s = figlib.unpack(self._frm32, chunk)
        data = dict(zip(self._names32, s))
        self.__dict__.update(data)

    def save(self, saver):
        FIGModelObject.save(self, saver)
        data = [getattr(self, name) for name in self._names32]
        line = figlib.pack(data, self._frm32)
        saver.write('%s\n' % line)
        for child in self.childs:
            child.save(saver)
        saver.write('%s\n' % OBJ_COMPOUND_ENDS)


class FIGDocument(FIGModelObject):
    """
        string  orientation         ("Landscape" or "Portrait")
        string  justification       ("Center" or "Flush Left")
        string  units               ("Metric" or "Inches")
        string  papersize           ("Letter", "Legal", "Ledger", "Tabloid",
                                     "A", "B", "C", "D", "E",
                                     "A4", "A3", "A2", "A1", "A0" and "B5")
        float   magnification       (export and print magnification, %)
        string  multiple-page       ("Single" or "Multiple" pages)
        int     transparent color   (color number for transparent color for GIF
                                     export. -3=background, -2=None, -1=Default,
                                     0-31 for standard colors or
                                     32- for user colors)
        # optional comment          (An optional set of comments may be here,
                                     which are associated with the whole figure)
        int resolution coord_system (Fig units/inch and coordinate system:
                                     1: origin at lower left corner (NOT USED)
                                     2: upper left)

    Fig_resolution is the resolution of the figure in the file.
    Xfig will always write the file with a resolution of 1200ppi so it
    will scale the figure upon reading it in if its resolution is different
    from 1200ppi.  Pixels are assumed to be square.

    Xfig will read the orientation string and change the canvas to match
    either the Landscape or Portrait mode of the figure file.

    The units specification is self-explanatory.

    The coordinate_system variable is ignored - the origin is ALWAYS the
    upper-left corner.

    ** Coordinates are given in "fig_resolution" units.
    ** Line thicknesses are given in 1/80 inch (0.3175mm) or 1 screen pixel.
       When exporting to EPS, PostScript or any bitmap format (e.g. GIF),  the
       line thickness is reduced to 1/160 inch (0.159mm) to "lighten" the look.
    ** dash-lengths/dot-gaps are given in 80-ths of an inch.
    """
    cid = FIG
    version = 3.2
    orientation = fig_const.LANDSCAPE
    justification = fig_const.CENTER_JUSTIFIED
    units = fig_const.INCHES
    paper_size = 'Letter'
    magnification = 100.0
    multiple_page = fig_const.SINGLE
    transparent_color = fig_const.DEFAULT_COLOR
    resolution = fig_const.DEFAULT_RESOLUTION
    coord_system = fig_const.DEFAULT_COORD_SYSTEM

    def __init__(self, config):
        self.config = config
        self.childs = []

    def save(self, saver):
        magic = '#FIG %s %s %s %s' % (
            self.version,
            saver.presenter.appdata.app_name,
            saver.presenter.appdata.version,
            saver.presenter.appdata.app_domain
        )
        saver.write('%s\n' % magic)
        saver.write('%s\n' % fig_const.ORIENTATION[self.orientation])
        saver.write('%s\n' % fig_const.JUSTIFICATION[self.justification])
        saver.write('%s\n' % fig_const.UNITS[self.units])
        if self.version >= 3.2:
            saver.write('%s\n' % self.paper_size)
            saver.write('%3.2f\n' % self.magnification)
            saver.write('%s\n' % fig_const.MULTIPLE_PAGE[self.multiple_page])
            saver.write('%i\n' % self.transparent_color)
            FIGModelObject.save(self, saver)
        saver.write('%i %i\n' % (self.resolution, self.coord_system))

        for child in self.childs:
            child.save(saver)

    def parse(self, loader, chunk=None):
        self.version = loader.version
        loader.stack.append(self.childs)
        self.read_header(loader)
        self.read_obj(loader)

    def read_obj(self, loader):
        cid_map = {
            OBJ_COLOR_DEF: FIGColorDef,
            OBJ_ELLIPSE: FIGEllipse,
            OBJ_POLYLINE: FIGPolyline,
            OBJ_SPLINE: FIGSpline,
            OBJ_TEXT: FIGText,
            OBJ_ARC: FIGArc,
            OBJ_COMPOUND: FIGCompound
        }

        while True:
            line = loader.get_line(strip=False)
            if line is None:
                break
            childs = loader.stack[-1]
            cid = int(line.split(' ', 1)[0])
            obj_class = cid_map.get(cid)
            if obj_class:
                obj = obj_class()
                obj.parse(loader, line)
                childs.append(obj)
            if cid == OBJ_COMPOUND:
                loader.stack.append(obj.childs)
            elif cid == OBJ_COMPOUND_ENDS:
                loader.stack.pop()

    def read_header(self, loader):
        if loader.version >= 3.0:
            if loader.startswith_line('land'):
                self.orientation = fig_const.LANDSCAPE
            else:
                self.orientation = fig_const.PORTRAIT

            if loader.startswith_line('cent'):
                self.justification = fig_const.CENTER_JUSTIFIED
            else:
                self.justification = fig_const.FLUSH_LEFT_JUSTIFIED

            if loader.startswith_line('metric'):
                self.units = fig_const.METRIC
            else:
                self.units = fig_const.INCHES

        if loader.version >= 3.2:
            self.paper_size, = figlib.unpack('s', loader.get_line())
            self.magnification, = figlib.unpack('f', loader.get_line())
            if loader.startswith_line('multiple'):
                self.multiple_page = fig_const.MULTIPLE
            else:
                self.multiple_page = fig_const.SINGLE
            self.transparent_color, = figlib.unpack('i', loader.get_line())

        data = figlib.unpack('ii', loader.get_line())
        self.resolution, self.coord_system = data
        self.comment = loader.pop_comment()
