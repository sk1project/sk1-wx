# -*- coding: utf-8 -*-
#
#  Copyright (C) 2011-2015 by Igor E. Novikov
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

import math
from copy import deepcopy
from base64 import b64decode, b64encode

from uc2 import _, cms, uc2const, libgeom, sk2const
from uc2.formats.generic import TextModelObject
from sk2_cids import *

GENERIC_FIELDS = ['cid', 'childs', 'parent', 'config']


class DocumentObject(TextModelObject):
    """
    Abstract parent class for all document 
    objects. Provides common object properties.
    """
    is_layer = False
    is_guide = False
    is_primitive = False
    is_curve = False
    is_rect = False
    is_pixmap = False
    is_circle = False
    is_polygon = False
    is_text = False
    is_group = False
    is_tpgroup = False
    is_container = False
    is_selectable = False

    def get_class_name(self):
        return CID_TO_NAME[self.cid]

    def resolve(self, name=''):
        is_leaf = True
        info = ''
        if self.cid < PRIMITIVE_CLASS:
            is_leaf = False
            info = '%d' % (len(self.childs))
        if self.cid == GUIDE:
            is_leaf = True
        if not name:
            name = self.get_class_name()
        return is_leaf, name, info

    def get_resources(self):
        return []

    def copy(self, src=None, dst=None):
        obj_copy = CID_TO_CLASS[self.cid](self.config)
        props = self.__dict__
        for item in props.keys():
            if item not in GENERIC_FIELDS and not item.startswith('cache'):
                obj_copy.__dict__[item] = deepcopy(props[item])
        for child in self.childs:
            obj_copy.childs.append(child.copy())
        return obj_copy

    def clear_color_cache(self):
        for child in self.childs:
            child.clear_color_cache()

    def is_closed(self):
        return False


class Document(DocumentObject):
    """
    Represents sK1 Document object.
    This is a root DOM instance of SK2 file format.
    """
    cid = DOCUMENT
    metainfo = None
    styles = {}
    profiles = []
    doc_origin = 1
    doc_units = uc2const.UNIT_MM
    resources = {}

    def __init__(self, config):
        self.cid = DOCUMENT
        self.childs = []
        self.metainfo = None
        self.config = config
        self.doc_origin = self.config.doc_origin
        self.doc_units = self.config.doc_units
        self.styles = {'Default Style': deepcopy([self.config.default_fill,
                                                  self.config.default_stroke,
                                                  [],
                                                  []])}
        self.resources = {}

    def update(self):
        if self.metainfo is None:
            self.metainfo = deepcopy([self.config.doc_author,
                                      self.config.doc_license,
                                      self.config.doc_keywords,
                                      self.config.doc_notes, ])
        if 'Default Text Style' not in self.styles:
            self.styles['Default Text Style'] = deepcopy([
                self.config.default_text_fill, [],
                self.config.default_text_style])
        elif len(self.styles['Default Text Style']) == 5:
            self.styles['Default Text Style'] += [True, ]
        DocumentObject.update(self)

    def get_def_style(self):
        return deepcopy(self.styles['Default Style'])

    def set_def_style(self, style):
        self.styles['Default Style'] = deepcopy(style)

    def get_text_style(self):
        return deepcopy(self.styles['Default Text Style'])

    def set_text_style(self, style):
        self.styles['Default Text Style'] = deepcopy(style)

    def get_style(self, name):
        if name in self.styles:
            return deepcopy(self.styles[name])
        return None

    def set_style(self, style, name):
        self.styles[name] = deepcopy(style)


class Pages(DocumentObject):
    """
    Represents container for pages. 
    Stores default page format value and page objects in childs list. 
    Also has a page counter field.
    Page format: [format name, (width, height), orientation]
    """
    cid = PAGES
    page_format = []
    page_counter = 0
    desktop_bg = [1.0, 1.0, 1.0]
    page_fill = [sk2const.FILL_SOLID, [1.0, 1.0, 1.0]]
    page_border = True

    def __init__(self, config, parent=None):
        self.cid = PAGES
        self.childs = []
        self.page_counter = 0
        self.parent = parent
        self.config = config
        fmt = self.config.page_format
        size = deepcopy(uc2const.PAGE_FORMATS[fmt])
        orient = config.page_orientation
        self.page_format = [fmt, size, orient]


# ================Structural Objects==================

class StructuralObject(DocumentObject):
    """
    Abstract parent for structural objects.
    """
    cid = STRUCTURAL_CLASS
    name = ''
    style = [[], [], [], []]


class Page(StructuralObject):
    """
    Represents document page.
    The object stores page name, page format and layer counter.
    All child layers are in childs list.
    Page format: [format name, (width, height), orientation]
    """
    cid = PAGE
    page_format = []
    name = ''

    layer_counter = 0

    def __init__(self, config, parent=None, name=''):
        self.cid = PAGE
        self.childs = []
        self.layer_counter = 0
        self.parent = parent
        self.config = config

        index = 1
        if parent:
            parent.page_counter += 1
            index = parent.page_counter
        if not name:
            self.name = _('Page') + ' ' + str(index)
        else:
            self.name = name
        if parent is None:
            fmt = self.config.page_format
            size = deepcopy(uc2const.PAGE_FORMATS[fmt])
            orient = config.page_orientation
            self.page_format = [fmt, size, orient]
        else:
            self.page_format = deepcopy(parent.page_format)

    def resolve(self, name=''):
        return StructuralObject.resolve(self, '%s' % self.name)


class Layer(StructuralObject):
    """
    Represents document layer.
    The object stores layer name and color used for contour view mode.
    All child objects are in childs list.
    """
    cid = LAYER
    color = ''
    properties = []
    name = ''
    is_layer = True

    def __init__(self, config, parent=None, name=''):
        self.cid = LAYER
        self.childs = []
        self.config = config

        index = 1
        if parent:
            parent.layer_counter += 1
            index = parent.layer_counter
        if not name:
            self.name = _('Layer') + ' ' + str(index)
        else:
            self.name = name

        self.parent = parent
        self.color = self.config.layer_color
        self.style = [[], deepcopy(self.config.default_stroke), [], []]
        self.properties = [] + self.config.layer_propeties
        self.childs = []

    def resolve(self, name=''):
        return StructuralObject.resolve(self, '%s' % self.name)

    def update(self):
        if isinstance(self.color, str):
            try:
                self.color = cms.hexcolor_to_rgba(self.color)
            except Exception:
                self.color = cms.hexcolor_to_rgba(self.config.layer_color)
        stroke = self.style[1]
        if stroke:
            stroke[2] = [uc2const.COLOR_RGB, self.color[:3], self.color[3], '']
        if len(self.properties) == 3:
            self.properties += [1, ]


class GuideLayer(Layer):
    """
    Represents guide line layer.
    This is a special layer to store document guide lines. 
    The object stores layer name and color used for guide line rendering.
    All child objects are in childs list.
    """
    cid = GUIDE_LAYER

    def __init__(self, config, parent=None, name=_('GuideLayer')):
        Layer.__init__(self, config, parent, name)
        self.cid = GUIDE_LAYER
        self.childs = []
        self.color = self.config.guide_layer_color
        self.properties = [] + self.config.guide_layer_propeties

    def update(self):
        Layer.update(self)
        if self.properties[3]:
            self.properties[3] = 0


class GridLayer(Layer):
    """
    Represents guide line layer.
    This is a special layer to manage document grid. 
    The object stores layer name and color used for grid rendering.
    All child objects are in childs list.
    """
    cid = GRID_LAYER
    grid = []

    def __init__(self, config, parent=None, name=_('GridLayer')):
        Layer.__init__(self, config, parent, name)
        self.cid = GRID_LAYER
        self.childs = []
        self.color = [] + self.config.grid_layer_color
        self.grid = [] + self.config.grid_layer_geometry
        self.properties = [] + self.config.grid_layer_propeties

    def update(self):
        Layer.update(self)
        if not self.properties[3]:
            self.properties[3] = 1


class LayerGroup(StructuralObject):
    """
    Represents container for regular layers.
    The object is not used yet. 
    All child layers are in childs list.
    """
    cid = LAYER_GROUP
    layer_counter = 0

    def __init__(self, config, parent=None):
        self.cid = LAYER_GROUP
        self.childs = []
        self.parent = parent
        self.config = config
        self.childs = []


class MasterLayers(LayerGroup):
    """
    Represents container for master layers applied for all pages.
    This layer group is the top most.
    All child layers are in childs list.
    """
    cid = MASTER_LAYERS

    def __init__(self, config, parent=None):
        LayerGroup.__init__(self, config, parent)
        self.cid = MASTER_LAYERS
        self.childs = []


class DesktopLayers(LayerGroup):
    """
    Represents container for desktop layers applied for all pages.
    This layer group is the lowest.
    All child layers are in childs list.
    """
    cid = DESKTOP_LAYERS

    def __init__(self, config, parent=None):
        LayerGroup.__init__(self, config, parent)
        self.cid = DESKTOP_LAYERS
        self.childs = []


class Guide(StructuralObject):
    """
    Represents guideline object.
    The object is defined by 'orientation' in 'position' point.
    All child layers are in childs list.
    """
    cid = GUIDE
    orientation = uc2const.HORIZONTAL
    position = 0.0
    is_guide = True

    def __init__(self, config, parent=None, pos=0.0,
                 orient=uc2const.HORIZONTAL):
        self.config = config
        self.parent = parent
        self.cid = GUIDE
        self.position = pos
        self.orientation = orient
        self.childs = []


# ================Selectable Objects==================
class SelectableObject(DocumentObject):
    """
    Abstract parent class for selectable objects. 
    Provides common selectable object properties.
    """
    cid = SELECTABLE_CLASS
    trafo = []
    style = [[], [], [], []]

    cache_bbox = []
    is_selectable = True

    def to_curve(self): return None


# ---------------Compound objects---------------------
class Group(SelectableObject):
    """
    Represents group object. 
    All child objects are in childs list.
    """

    cid = GROUP
    childs = []
    is_group = True

    def __init__(self, config, parent=None, childs=None):
        childs = childs or []
        self.cid = GROUP
        self.childs = []
        self.config = config
        self.parent = parent
        self.childs += childs

    def apply_trafo(self, trafo):
        for child in self.childs:
            child.apply_trafo(trafo)
        self.update_bbox()

    def update_bbox(self):
        if self.childs:
            self.cache_bbox = deepcopy(self.childs[0].cache_bbox)
            for child in self.childs[1:]:
                self.cache_bbox = libgeom.sum_bbox(self.cache_bbox,
                                                   child.cache_bbox)

    def update(self):
        for child in self.childs:
            child.update()
        self.update_bbox()

    def get_trafo_snapshot(self):
        childs_snapshots = []
        for child in self.childs:
            childs_snapshots.append(child.get_trafo_snapshot())
        return self, None, [] + self.cache_bbox, childs_snapshots

    def set_trafo_snapshot(self, snapshot):
        self.cache_bbox, childs_snapshots = snapshot[2:]
        for item in childs_snapshots:
            item[0].set_trafo_snapshot(item)


class TP_Group(Group):
    """
    Represents text-on-path group object. 
    All child objects are in childs list. First child object is a reference 
    path and this path is not closed.
    Other child objects are text objects.
    Each text object has according record in childs_data list.
    First item int this lis is None (corresponds path obj)
    Record is a tuple: (base_point, align, side_flag)
        base_point - value from 0.0 to 1.0
        align - text align constant
        side_flag - if True, place text on other path side
    """

    cid = TP_GROUP
    childs = []
    childs_data = {}
    is_tpgroup = True

    def __init__(self, config, parent=None, childs=None, data=None):
        childs = childs or []
        data = data or []
        Group.__init__(self, config, parent, childs)
        self.cid = TP_GROUP
        self.childs_data = [None, ]
        if data:
            self.childs_data.append(data)

    def set_text_on_path(self, path_obj, text_obj, data):
        libgeom.set_text_on_path(path_obj, text_obj, data)


class Container(Group):
    """
    Represents container group object. 
    All child objects are in childs list. 
    First child object is a container.
    Other child objects are container's content.	
    """

    cid = CONTAINER
    cache_container = None
    is_container = True

    def __init__(self, config, parent=None, childs=None):
        childs = childs or []
        super(Container, self).__init__(config, parent, childs)
        self.cid = CONTAINER
        self.childs = []
        self.config = config
        self.parent = parent
        self.childs += childs

    def update(self):
        for child in self.childs:
            child.update()
        self.update_bbox()

    def update_bbox(self):
        self.cache_container = self.childs[0]
        self.cache_bbox = deepcopy(self.cache_container.cache_bbox)


class PrimitiveObject(SelectableObject):
    """
    Abstract parent class for graphics primitives. 
    Provides common primitive object properties.
    """

    cid = PRIMITIVE_CLASS

    fill_trafo = []
    stroke_trafo = []

    cache_paths = None
    cache_cpath = None
    cache_pattern_img = None
    cache_ps_pattern_img = None
    cache_gray_pattern_img = None
    is_primitive = True

    def get_initial_paths(self):
        pass

    def destroy(self):
        if self.cache_cpath is not None:
            del self.cache_cpath
        SelectableObject.destroy(self)

    def to_curve(self):
        curve = Curve(self.config)
        curve.paths = deepcopy(self.paths if self.is_curve
                               else self.cache_paths)
        curve.trafo = [] + self.trafo
        curve.fill_trafo = [] + self.fill_trafo
        curve.stroke_trafo = [] + self.stroke_trafo
        curve.style = deepcopy(self.style)
        curve.update()
        return curve

    def update(self):
        self.cache_pattern_img = None
        self.cache_ps_pattern_img = None
        self.cache_gray_pattern_img = None
        self.cache_paths = self.get_initial_paths()
        self.cache_cpath = libgeom.create_cpath(self.cache_paths)
        libgeom.apply_trafo(self.cache_cpath, self.trafo)
        self.update_bbox()

    def clear_color_cache(self):
        self.cache_pattern_img = None
        self.cache_ps_pattern_img = None
        self.cache_gray_pattern_img = None

    def update_bbox(self):
        self.cache_bbox = libgeom.get_cpath_bbox(self.cache_cpath)

    def apply_trafo(self, trafo):
        self.cache_cpath = libgeom.apply_trafo(self.cache_cpath, trafo)
        self.trafo = libgeom.multiply_trafo(self.trafo, trafo)
        if self.fill_trafo:
            self.fill_trafo = libgeom.multiply_trafo(self.fill_trafo, trafo)
        if self.stroke_trafo:
            self.stroke_trafo = libgeom.multiply_trafo(self.stroke_trafo, trafo)
        self.update_bbox()

    def get_trafo_snapshot(self):
        return (self, [] + self.trafo, [] + self.fill_trafo,
                [] + self.stroke_trafo, [] + self.cache_bbox,
                libgeom.copy_cpath(self.cache_cpath))

    def set_trafo_snapshot(self, snapshot):
        self.trafo, self.fill_trafo, self.stroke_trafo = snapshot[1:4]
        self.cache_bbox, self.cache_cpath = snapshot[4:]


# ---------------Primitives---------------------------

class Rectangle(PrimitiveObject):
    """
    Represents rectangle object. 
    The object is defined by start point (lower left corner)
    and width/height values (unsigned floats).
    'corners' list describes level of corner rounding (from 0.0 to 1.0).
    Corner order is clockwise from the lower left corner.
    """

    cid = RECTANGLE
    start = []
    width = 1.0
    height = 1.0
    corners = []
    is_rect = True

    def __init__(self, config, parent=None,
                 rect=[] + sk2const.STUB_RECT,
                 trafo=[] + sk2const.NORMAL_TRAFO,
                 style=[] + sk2const.EMPTY_STYLE,
                 corners=[] + sk2const.CORNERS,
                 ):
        self.cid = RECTANGLE
        self.parent = parent
        self.config = config
        self.set_rect(rect)
        self.trafo = trafo
        self.corners = corners
        self.style = style

    def get_rect(self):
        return self.start + [self.width, self.height]

    def set_rect(self, rect):
        self.start = rect[0:2]
        self.width = rect[2]
        self.height = rect[3]

    def is_closed(self):
        return True

    def get_initial_paths(self):
        return libgeom.get_rect_paths(self.start, self.width,
                                      self.height, self.corners)

    def get_corner_points(self):
        c0 = [] + self.start
        c1 = [self.start[0], self.start[1] + self.height]
        c2 = [self.start[0] + self.width, self.start[1] + self.height]
        c3 = [self.start[0] + self.width, self.start[1]]
        return [c0, c1, c2, c3]

    def get_stops(self):
        if self.width == self.height:
            p0, p1, p2, p3 = self.get_midpoints()
            return [[p0, ], [p1, ], [p2, ], [p3, ]]
        elif self.width > self.height:
            dx = self.width / 2.0 - self.height / 2.0
            p0, p1, p2, p3 = self.get_midpoints()
            p10 = [p1[0] - dx, p1[1]]
            p11 = [p1[0] + dx, p1[1]]
            p30 = [p3[0] + dx, p3[1]]
            p31 = [p3[0] - dx, p3[1]]
            return [[p0, ], [p10, p11], [p2, ], [p30, p31]]
        else:
            dy = self.height / 2.0 - self.width / 2.0
            p0, p1, p2, p3 = self.get_midpoints()
            p00 = [p0[0], p0[1] - dy]
            p01 = [p0[0], p0[1] + dy]
            p20 = [p2[0], p2[1] + dy]
            p21 = [p2[0], p2[1] - dy]
            return [[p00, p01], [p1, ], [p20, p21], [p3, ]]

    def get_midpoints(self):
        return [[self.start[0], self.start[1] + self.height / 2.0],
                [self.start[0] + self.width / 2.0, self.start[1] + self.height],
                [self.start[0] + self.width, self.start[1] + self.height / 2.0],
                [self.start[0] + self.width / 2.0, self.start[1]]]


class Circle(PrimitiveObject):
    """
    Represents circle/ellipse object. 
    It is assumed that initial object is a circle with 0.5 points radius and
    center at [0.5,0.5] point. Object is initialized by rect list:
    [x,y, width, height] where [x,y] is a circle/ellipse object center and
    width/height are object size. These values are stored as 'initial_trafo'
    field. Later transformations are collected separately.
    angle1/angle2 and circle_type are define segment properties.
    """

    cid = CIRCLE
    angle1 = 0.0
    angle2 = 0.0
    circle_type = sk2const.ARC_CHORD
    initial_trafo = sk2const.NORMAL_TRAFO
    is_circle = True

    def __init__(self, config, parent=None,
                 rect=[] + sk2const.STUB_RECT,
                 angle1=0.0,
                 angle2=0.0,
                 circle_type=sk2const.ARC_CHORD,
                 style=[] + sk2const.EMPTY_STYLE,
                 ):
        self.cid = CIRCLE
        self.parent = parent
        self.config = config
        self.angle1 = angle1
        self.angle2 = angle2
        self.trafo = [rect[2], 0.0, 0.0, rect[3], rect[0], rect[1]]
        self.initial_trafo = [] + self.trafo
        self.circle_type = circle_type
        self.style = style

    def is_closed(self):
        return self.circle_type != sk2const.ARC_ARC

    def get_center(self):
        return [0.5, 0.5]

    def get_initial_paths(self):
        return libgeom.get_circle_paths(self.angle1, self.angle2,
                                        self.circle_type)


class Polygon(PrimitiveObject):
    """
    Represents polygon object. 
    It is assumed that initial object is a polygon with 0.5 points radius and
    center at [0.5,0.5] point. Object is initialized by rect list:
    [x,y, width, height] where [x,y] is a circle/ellipse object center and
    width/height are object size. These values are stored as 'initial_trafo'
    field. Later transformations are collected separately.
    angle1/angle2 and coef1/coef2 are define dorner and midpoint positions.
    """

    cid = POLYGON

    corners_num = 0
    angle1 = 0.0
    angle2 = 0.0
    coef1 = 1.0
    coef2 = 1.0
    initial_trafo = sk2const.NORMAL_TRAFO
    is_polygon = True

    def __init__(self, config, parent=None,
                 rect=[] + sk2const.STUB_RECT,
                 angel1=0.0,
                 angel2=0.0,
                 coef1=1.0,
                 coef2=1.0,
                 corners_num=0,
                 style=[] + sk2const.EMPTY_STYLE,
                 ):
        self.cid = POLYGON
        self.parent = parent
        self.config = config
        self.corners_num = corners_num
        if not corners_num:
            self.corners_num = config.default_polygon_num
        self.angle1 = angel1
        self.angle2 = angel2
        self.coef1 = coef1
        self.coef2 = coef2
        self.trafo = [rect[2], 0.0, 0.0, rect[3], rect[0], rect[1]]
        self.initial_trafo = [] + self.trafo
        self.style = style

    def is_closed(self):
        return True

    def get_initial_paths(self):
        return libgeom.get_polygon_paths(self.corners_num,
                                         self.angle1, self.angle2,
                                         self.coef1, self.coef2)

    def get_corner_radius(self):
        return 0.5

    def get_midpoint_radius(self):
        val = math.pi / float(self.corners_num)
        return self.get_corner_radius() * math.cos(val)

    def get_corner_angle(self, index):
        val = 2.0 * math.pi / float(self.corners_num) * float(
            index) + math.pi / 2.0
        if val > 2.0 * math.pi:
            val -= 2.0 * math.pi
        return val

    def get_midpoint_angle(self, index):
        val = self.get_corner_angle(index) + math.pi / float(self.corners_num)
        if val > 2.0 * math.pi:
            val -= 2.0 * math.pi
        return val


class Curve(PrimitiveObject):
    """
    Represents curve object. 
    
    It is assumed that curve is a list of paths:
    curve = [path0, path1, ...]
    
    Where path is defined as:
    [start_point, points, end_marker]
    start_pont - [x,y]
    end_marker - is closed CURVE_CLOSED = 1, if not CURVE_OPENED = 0
    
    Path points are defined as:
    [point0, point1,...]
    line point - [x,y]
    curve point - [[x1,y1],[x2,y2],[x3,y3], marker]
    marker - NODE_CUSP = 0; NODE_SMOOTH = 1; NODE_SYMMETRICAL = 2
    
    Curve affine transformation is stored and collected separately,
    i.e. curve points are not modified to avoid accurancy lost.	
    """

    cid = CURVE
    paths = []
    is_curve = True

    def __init__(self, config, parent=None,
                 paths=[] + sk2const.STUB_PATHS,
                 trafo=[] + sk2const.NORMAL_TRAFO,
                 style=[] + sk2const.EMPTY_STYLE):
        self.cid = CURVE
        self.config = config
        self.parent = parent
        self.paths = paths
        self.trafo = trafo
        self.style = style

    def get_initial_paths(self):
        return self.paths

    def is_closed(self):
        for path in self.paths:
            if path[2] == sk2const.CURVE_CLOSED:
                return True
        return False

    def to_curve(self):
        return self


class Text(PrimitiveObject):
    """
    Represents text object. 
    Text content is stored in 'text' field as a base64 encoded string
    to resolve EOL and other special character issues.
    'trafos' contains glyph specific transformations.
    'markup' list contains text markup description.
    'width' field defines text block mode in case of -1.
    For any other positive values paragraph mode is defined.
    """

    cid = TEXT_BLOCK
    text = ""
    width = -1
    markup = []
    initial_trafo = sk2const.NORMAL_TRAFO
    trafos = None

    cache_glyphs = []
    cache_line_points = []
    cache_layout_data = ()
    cache_layout_bbox = []
    cache_clusters = []
    is_text = True

    def __init__(self, config, parent=None,
                 point=None,
                 text="",
                 width=sk2const.TEXTBLOCK_WIDTH,
                 trafo=[] + sk2const.NORMAL_TRAFO,
                 style=[] + sk2const.EMPTY_STYLE):

        point = point or [0.0, 0.0]
        self.config = config
        self.parent = parent
        self.text = b64encode(text)
        self.width = width
        self.trafo = trafo[:4] + [trafo[4] + point[0], trafo[5] + point[1]]
        self.initial_trafo = [] + self.trafo
        self.style = style
        self.markup = []
        self.trafos = {}

    def get_text(self):
        return b64decode(self.text).decode('utf-8')

    def set_text(self, text):
        text = text.encode('utf-8') if isinstance(text, unicode) else text
        self.text = b64encode(text)

    def is_closed(self):
        return True

    def is_textblock(self):
        return self.width == sk2const.TEXTBLOCK_WIDTH

    def get_glyphs(self):
        glyphs, points, data, bbox, cl = libgeom.get_text_glyphs(
            self.get_text(),
            self.width, self.style[2], self.markup)
        self.cache_line_points = points
        self.cache_layout_data = data
        self.cache_clusters = cl
        dx = 0.0
        if self.style[2][3] == sk2const.TEXT_ALIGN_CENTER:
            dx = -bbox[2] / 2.0
        if self.style[2][3] == sk2const.TEXT_ALIGN_RIGHT:
            dx = -bbox[2]
        bbox[0] += dx
        bbox[2] += dx
        self.cache_layout_bbox = libgeom.normalize_bbox(bbox)
        return glyphs

    def get_line_points(self):
        return libgeom.apply_trafo_to_points(self.cache_line_points, self.trafo)

    def to_curve(self):
        group = Group(self.config)
        subgroup = Group(self.config, group)
        for item in self.cache_cpath:
            paths = None
            if item:
                paths = libgeom.get_paths_from_glyph(item)
            if not paths:
                if len(subgroup.childs) == 1:
                    subgroup.childs[0].parent = group
                    group.childs.append(subgroup.childs[0])
                    subgroup.childs = []
                elif len(subgroup.childs) > 1:
                    subgroup.update()
                    group.childs.append(subgroup)
                    subgroup = Group(self.config, group)
            else:
                curve = Curve(self.config, group)
                curve.paths = paths
                curve.fill_trafo = [] + self.fill_trafo
                curve.stroke_trafo = [] + self.stroke_trafo
                curve.style = deepcopy(self.style)
                curve.update()
                subgroup.childs.append(curve)

        if subgroup not in group.childs:
            if len(subgroup.childs) == 1:
                subgroup.childs[0].parent = group
                group.childs.append(subgroup.childs[0])
                subgroup.childs = []
            elif len(subgroup.childs) > 1:
                subgroup.update()
                group.childs.append(subgroup)

        group.update()
        return group

    def get_transformed_paths(self):
        ret = []
        for item in self.cache_cpath:
            if item:
                paths = libgeom.get_paths_from_glyph(item)
                if paths:
                    ret += paths
        return ret

    def update(self):
        self.cache_cpath = self.get_glyphs()
        index = 0
        for item in self.cache_cpath:
            if item:
                if index not in self.trafos:
                    libgeom.apply_trafo(item, self.trafo)
                else:
                    libgeom.apply_trafo(item, self.trafos[index])
            index += 1
        self.update_bbox()

    def update_bbox(self):
        self.cache_bbox = []
        index = 0
        if not self.trafos or 0 not in self.trafos:
            bp = [0.0, 0.0]
            self.cache_bbox = 2 * libgeom.apply_trafo_to_point(bp, self.trafo)
        for item in self.cache_cpath:
            bbox = []
            if not item:
                if not self.trafos:
                    data = self.cache_layout_data[index]
                    bp = [data[0], data[4]]
                    bbox = 2 * libgeom.apply_trafo_to_point(bp, self.trafo)
            else:
                bbox = libgeom.get_cpath_bbox(item)
            if bbox:
                if not self.cache_bbox:
                    self.cache_bbox = bbox
                else:
                    self.cache_bbox = libgeom.sum_bbox(self.cache_bbox, bbox)
            index += 1

    def apply_trafo(self, trafo):
        for i in self.trafos.keys():
            self.trafos[i] = libgeom.multiply_trafo(self.trafos[i], trafo)
        for i in range(len(self.cache_cpath)):
            if self.cache_cpath[i] is None:
                continue
            self.cache_cpath[i] = libgeom.apply_trafo(self.cache_cpath[i],
                                                      trafo)
        self.trafo = libgeom.multiply_trafo(self.trafo, trafo)
        if self.fill_trafo:
            self.fill_trafo = libgeom.multiply_trafo(self.fill_trafo, trafo)
        if self.stroke_trafo:
            self.stroke_trafo = libgeom.multiply_trafo(self.stroke_trafo, trafo)
        self.update_bbox()

    def get_trafo_snapshot(self):
        cpaths = []
        for i in range(len(self.cache_cpath)):
            if self.cache_cpath[i] is None:
                cpaths.append(None)
            else:
                cpaths.append(libgeom.copy_cpath(self.cache_cpath[i]))
        trafos = deepcopy(self.trafos)
        return (self, [] + self.trafo, [] + self.fill_trafo,
                [] + self.stroke_trafo, [] + self.cache_bbox, cpaths, trafos)

    def set_trafo_snapshot(self, snapshot):
        self.trafo, self.fill_trafo, self.stroke_trafo = snapshot[1:4]
        self.cache_bbox, self.cache_cpath, self.trafos = snapshot[4:]


class Pixmap(PrimitiveObject):
    """
    Represents pixmap object. 
    Raster graphics is stored as a TIFF bitmaps for CMYK colorspace and as 
    a PNG bitmap for others. 'bitmap' field contains raster info, but
    transparency data is stored as a grayscale image in 'alpha_channel'.
    Images are stored as a base64 encoded string to resolve EOL and other 
    special character issues. 'colorspace' describes 'bitmap' type. 
    Possible types are: monochrome, grayscale, RGB and CMYK.
    For monochrome and grayscale colorspaces is available duotone mode. Duotone
    colors (foreground and background) are defined in 'style' field.
    It is assumed that initial lower left corner of pixmap is [0.0,0.0] point 
    and pixmap size is defined by 72 dpi resolution.
    """

    cid = PIXMAP

    bitmap = ''
    alpha_channel = ''
    size = (100, 100)
    colorspace = None

    cache_paths = None
    cache_cpath = None
    cache_cdata = None
    cache_ps_cdata = None
    cache_gray_cdata = None
    is_pixmap = True

    def __init__(self, config, parent=None,
                 bitmap='',
                 alpha_channel='',
                 size=(100, 100),
                 trafo=[] + sk2const.NORMAL_TRAFO,
                 style=[] + sk2const.EMPTY_STYLE):
        self.cid = PIXMAP
        self.config = config
        self.parent = parent
        self.bitmap = bitmap
        self.alpha_channel = alpha_channel
        self.size = size
        self.trafo = trafo
        self.style = style

    def get_size(self):
        width = float(self.size[0]) * uc2const.px_to_pt
        height = float(self.size[1]) * uc2const.px_to_pt
        return width, height

    def get_initial_paths(self):
        width, height = self.get_size()
        return libgeom.get_rect_paths([0, 0], width, height,
                                      [] + sk2const.CORNERS)

    def get_resolution(self):
        path = libgeom.apply_trafo_to_paths(self.cache_paths, self.trafo)[0]
        p0 = path[0]
        p1 = path[1][0]
        p2, p3 = path[1][-2:]
        m11 = (libgeom.distance(p0, p1)) / float(self.size[1])
        m22 = (libgeom.distance(p2, p3)) / float(self.size[0])
        v_dpi = int(round(uc2const.in_to_pt / m11))
        h_dpi = int(round(uc2const.in_to_pt / m22))
        return h_dpi, v_dpi

    def update(self):
        self.clear_color_cache()
        PrimitiveObject.update(self)

    def clear_color_cache(self):
        self.cache_cdata = None
        self.cache_ps_cdata = None
        self.cache_gray_cdata = None


CID_TO_CLASS = {
    DOCUMENT: Document,

    METAINFO: None, STYLES: None, STYLE: None,
    PROFILES: None, PROFILE: None, FONTS: None,
    FONT: None, IMAGES: None, IMAGE: None,

    PAGES: Pages, PAGE: Page, LAYER_GROUP: LayerGroup,
    MASTER_LAYERS: MasterLayers, LAYER: Layer,
    GRID_LAYER: GridLayer, GUIDE_LAYER: GuideLayer,
    DESKTOP_LAYERS: DesktopLayers, GUIDE: Guide,

    GROUP: Group, TP_GROUP: TP_Group, CONTAINER: Container,

    RECTANGLE: Rectangle, CIRCLE: Circle,
    POLYGON: Polygon, CURVE: Curve, PIXMAP: Pixmap,
    TEXT_BLOCK: Text, TEXT_COLUMN: Text,
}
