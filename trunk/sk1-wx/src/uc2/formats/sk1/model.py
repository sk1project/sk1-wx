# -*- coding: utf-8 -*-
#
#	Copyright (C) 2013 by Igor E. Novikov
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.

from copy import deepcopy
import Image

from uc2 import _, uc2const
from uc2.formats.pdxf import const
from uc2.formats.sk1 import sk1const
from uc2.utils import Base64Encode, Base64Decode, SubFileDecode
from uc2.formats.generic import TextModelObject

from _sk1objs import Trafo, CreatePath, Point, Scale, Translation

# Document object enumeration
DOCUMENT = 1
LAYOUT = 2
GRID = 3
PAGES = 4
PAGE = 5
LAYER = 6
MASTERLAYER = 7
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
	PAGES: _('Pages'), PAGE: _('Page'), LAYER: _('Layer'), MASTERLAYER: _('MasterLayer'),
	GUIDELAYER: _('GuideLayer'), GUIDE: _('Guideline'), GUIDE: _('Guideline'),

	STYLE: _('Style'),
	GROUP: _('Group'), MASKGROUP: _('MaskGroup'),

	RECTANGLE:_('Rectangle'), ELLIPSE:_('Ellipse'), CURVE:_('Curve'),
	TEXT:_('Text'), BITMAPDATA:_('BitmapData'), IMAGE:_('Image'),
	}



class SK1ModelObject(TextModelObject):
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
		if not is_leaf: info = len(self.childs)
		return (is_leaf, name, info)

	def get_content(self):
		result = '' + self.string
		for child in self.childs:
			result += child.get_content()
		if self.end_string:
			result += self.end_string
		return result

	def write_content(self, fileobj):
		if not self.properties is None:
			self.properties.write_content(fileobj)
		fileobj.write(self.string)
		for child in self.childs:
			child.write_content(fileobj)
		if self.end_string:
			fileobj.write(self.end_string)

#--- STRUCTURAL OBJECTS

class SK1Document(SK1ModelObject):
	"""
	Represents SK1 model root object.
	"""

	string = '##sK1 1 2\ndocument()\n'
	doc_origin = sk1const.DOC_ORIGIN_LL
	doc_units = uc2const.UNIT_MM
	cid = DOCUMENT
	layout = None
	pages = None
	grid = None
	masterlayer = None
	guidelayer = None
	meta = None
	styles = {}

	def __init__(self, config):
		self.meta = MetaInfo()
		SK1ModelObject.__init__(self, config)

class MetaInfo:
	pass

class SK1Layout(SK1ModelObject):
	"""
	Represents Layout object.
	The object defines default page size as:
	(format_name,(width,height),orientation)
	"""

	string = "layout('A4',(595.276,841.89),0)\n"
	cid = LAYOUT
	format = 'A4'
	size = uc2const.PAGE_FORMATS['A4']
	orientation = uc2const.PORTRAIT

	def __init__(self, format='', size=(), orientation=uc2const.PORTRAIT):
		if format: self.format = format
		if size: self.size = size
		if orientation: self.orientation = orientation
		SK1ModelObject.__init__(self)

	def update(self):
		args = (self.format, self.size, self.orientation)
		self.string = 'layout' + args.__str__() + '\n'

class SK1Grid(SK1ModelObject):
	"""
	Represents Grid layer object.
	Grid values are defined as:
	(grid,visibility,grid_color,layer_name)
	where:
	grid=(start_x, start_y, dx, dy)
	grid_color=(colorspace,color values)
	"""
	string = 'grid((0,0,2.83465,2.83465),0,("RGB",0.83,0.87,0.91),\'Grid\')\n'
	cid = GRID
	geometry = sk1const.default_grid
	visible = 0
	grid_color = sk1const.default_grid_color
	name = 'Grid'
	is_GridLayer = 1

	def __init__(self, geometry=sk1const.default_grid, visible=0,
				grid_color=sk1const.default_grid_color, name=_("Grid")):
		if len(geometry) == 2:
			self.geometry = (0, 0) + geometry
		elif len(geometry) == 4:
			self.geometry = geometry
		else:
			self.geometry = sk1const.default_grid
		self.visible = visible
		self.grid_color = grid_color
		self.name = name
		SK1ModelObject.__init__(self)

	def update(self):
		args = (self.geometry, self.visible, self.grid_color, self.name)
		self.string = 'grid' + args.__str__() + '\n'

class SK1Pages(SK1ModelObject):
	"""
	Represents container for Page objects.
	Has no any values and used to be a childs list holder.
	"""
	cid = PAGES
	page_counter = 0

	def __init__(self):
		SK1ModelObject.__init__(self)

	def write_content(self, fileobj):
		for child in self.childs:
			child.write_content(fileobj)

class SK1Page(SK1ModelObject):
	"""
	Represents Page object.
	Page values are defined as:
	(page_name,format_name,(width,height),orientation)
	"""
	string = "page('','A4',(595.276,841.89),0)\n"
	cid = PAGE
	name = ''
	format = 'A4'
	size = uc2const.PAGE_FORMATS['A4']
	orientation = uc2const.PORTRAIT

	def __init__(self, name='', format='', size=(), orientation=uc2const.PORTRAIT):
		if name:self.name = name
		if format:self.format = format
		if size:self.size = size
		if orientation:self.orientation = orientation
		SK1ModelObject.__init__(self)

	def update(self):
		args = (self.name, self.format, self.size, self.orientation)
		self.string = 'page' + args.__str__() + '\n'

class SK1Layer(SK1ModelObject):
	"""
	Represents Layer object.
	Layer values are defined as:
	(layer_name,visible,printable,locked,outlined,layer_color)
	"""
	string = "layer('Layer 1',1,1,0,0,(\"RGB\",0.196,0.314,0.635))\n"
	cid = LAYER
	name = ''
	layer_properties = []
	layer_color = sk1const.default_layer_color
	visible = 1
	printable = 1
	locked = 0
	outlined = 0
	is_MasterLayer = 0
	is_Page = 0

	def __init__(self, name=_("New Layer"),
					visible=1, printable=1, locked=0,
					outlined=0, outline_color=sk1const.default_layer_color,
					is_MasterLayer=0, is_Page=0):
		self.name = name
		self.visible = visible
		self.printable = printable
		self.locked = locked
		self.outlined = outlined
		self.is_MasterLayer = is_MasterLayer
		self.is_Page = is_Page
		SK1ModelObject.__init__(self)

	def update(self):
		args = (self.name, self.visible, self.printable, self.locked,
			self.outlined, self.layer_color)
		self.string = 'layer' + args.__str__() + '\n'

class SK1MasterLayer(SK1ModelObject):
	"""
	Represents MasterLayer object.
	Layer values are defined as:
	(layer_name,visible,printable,locked,outlined,layer_color)
	"""
	string = "masterlayer('MasterLayer 1',1,1,0,0,(\"RGB\",0.196,0.314,0.635))\n"
	cid = MASTERLAYER
	name = ''
	layer_properties = []
	layer_color = sk1const.default_layer_color
	visible = 1
	printable = 1
	locked = 0
	outlined = 0
	is_MasterLayer = 1
	is_Page = 0

	def __init__(self, name=_("MasterLayer"),
					visible=1, printable=1, locked=0,
					outlined=0, outline_color=sk1const.default_layer_color,
					is_MasterLayer=1, is_Page=0):
		self.name = name
		self.visible = visible
		self.printable = printable
		self.locked = locked
		self.outlined = outlined
		self.is_MasterLayer = is_MasterLayer
		self.is_Page = is_Page
		SK1ModelObject.__init__(self)

	def update(self):
		args = (self.name, self.visible, self.printable, self.locked,
			self.outlined, self.layer_color)
		self.string = 'masterlayer' + args.__str__() + '\n'

class SK1GuideLayer(SK1ModelObject):
	"""
	Represents GuideLayer object.
	Layer values are defined as:
	(layer_name,visible,printable,locked,outlined,layer_color)
	"""
	string = "guidelayer('Guide Lines',1,0,0,1,(\"RGB\",0.0,0.3,1.0))\n"
	cid = GUIDELAYER
	name = 'GuideLayer'
	layer_properties = []
	layer_color = sk1const.default_guidelayer_color
	visible = 1
	printable = 0
	locked = 0
	outlined = 0
	is_MasterLayer = 0
	is_Page = 0

	def __init__(self, name=_("GuideLayer"),
					visible=1, printable=0, locked=0,
					outlined=0, outline_color=sk1const.default_layer_color,
					is_MasterLayer=0, is_Page=0):
		self.name = name
		self.visible = visible
		self.printable = printable
		self.locked = locked
		self.outlined = outlined
		self.is_MasterLayer = is_MasterLayer
		self.is_Page = is_Page
		SK1ModelObject.__init__(self)

	def update(self):
		args = (self.name, self.visible, self.printable, self.locked,
			self.outlined, self.layer_color)
		self.string = 'guidelayer' + args.__str__() + '\n'

class SK1Guide(SK1ModelObject):
	"""
	Represents Guideline object.
	Guideline values are defined as:
	(point,orientation)
	"""
	string = "guide((0.0,0.0),0)\n"
	cid = GUIDE
	position = 0
	orientation = uc2const.HORIZONTAL
	is_GuideLine = 1

	def __init__(self, point=(), orientation=uc2const.HORIZONTAL):
		if point:
			if orientation == uc2const.VERTICAL:
				self.position = point[0]
			else:
				self.position = point[1]
		else:
			self.position = 0.0
		self.orientation = orientation
		SK1ModelObject.__init__(self)

	def update(self):
		if self.orientation == uc2const.VERTICAL:
			point = (self.position, 0.0)
		else:
			point = (0.0, self.position)
		args = (point, self.orientation)
		self.string = 'guide' + args.__str__() + '\n'

#--- PROPERTIES OBJECTS


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
			self.color = deepcopy(sk1const.fallback_sk1color)

	def copy(self):
		return SolidPattern(deepcopy(self.color))

class MultiGradient:

	colors = []

	def __init__(self, colors=[], duplicate=None):
		if not colors:
			start_color = deepcopy(sk1const.black_color)
			end_color = deepcopy(sk1const.white_color)
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
							round(self.direction.y, 10), self.border))

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
		fileobj.write('pgr(%g,%g,%g)\n' % (self.center.x, self.center.y, self.border))

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
		fileobj.write('pgc(%g,%g,%g,%g)\n' % (tuple(self.center) + (round(self.direction.x, 10),
											round(self.direction.y, 10))))

class HatchingPattern(Pattern):

	is_Hatching = 1

	def __init__(self, foreground=None, background=None,
					direction=Point(1, 0),
					spacing=5.0, width=0.5, duplicate=None):
		if foreground is None:	foreground = deepcopy(sk1const.black_color)
		self.foreground = foreground
		if background is None:	background = deepcopy(sk1const.white_color)
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
		return HatchingPattern(foreground, background, direction, spacing, width)

	def write_content(self, file):
		color = self.foreground.__str__()
		background = self.background.__str__()
		#TODO: check spacing field
		file.write('phs(%s,%s,%g,%g,%g,%g)\n'
						% (color, background, self.direction.x, self.direction.y,
						self.distance, self.width))

class ImageTilePattern(Pattern):

	is_Tiled = 1
	is_Image = 1
	data = None
	id = None

	def __init__(self, data=None, trafo=None, duplicate=None):
		if trafo is None: trafo = Trafo(1, 0, 0, -1, 0, 0)
		self.trafo = trafo
		self.data = data
		self.image = self.data

	def copy(self):
		trafo = Trafo(*self.trafo.coef())
		image = self.image.copy()
		return ImageTilePattern(image, trafo)

	def write_content(self, file):
		if self.image and not self.id:
			self.id = id(self.image)
		if self.image:
			file.write('bm(%d)\n' % (self.id))
			vfile = Base64Encode(file)
			if self.raw_image.mode == "CMYK":
				self.raw_image.save(vfile, 'JPEG', quality=100)
			else:
				self.raw_image.save(vfile, 'PNG')
			vfile.close()
			file.write('-\n')
			val = (self.id, self.trafo.coeff()).__str__()
			file.write('pit' + val + '\n')

class Style:
	"""
	Represents object style.
	"""

	is_dynamic = 0
	name = ''

	fill_pattern = EmptyPattern
	fill_transform = 1
	line_pattern = SolidPattern(deepcopy(sk1const.black_color))
	line_width = 0.0
	line_join = sk1const.JoinMiter
	line_cap = sk1const.CapButt
	line_dashes = ()
	line_arrow1 = None
	line_arrow2 = None
	font = None
	font_size = 12.0

	def __init__(self, name='', duplicate=None, base_style=False, **kw):
		if name:
			self.name = name
		if base_style:
			self.fill_pattern = EmptyPattern
			self.fill_transform = 1
			color = deepcopy(sk1const.black_color)
			self.line_pattern = SolidPattern(color)
			self.line_width = 0.0
			self.line_join = sk1const.JoinMiter
			self.line_cap = sk1const.CapButt
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
			style_copy.font = '' + self.font
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
				if not pattern.color == sk1const.black_color:
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
				if not pattern.color == sk1const.black_color:
					write('lp(' + pattern.color.__str__() + ')\n')
			else:
				pattern.write_content(fileobj)
				write('lp()\n')
		if self.line_width :
			write('lw(%g)\n' % self.line_width)
		if not self.line_cap == sk1const.CapButt:
			write('lc(%d)\n' % self.line_cap)
		if not self.line_join == sk1const.JoinMiter:
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

#--- SELECTABLE OBJECTS

class SK1Group(SK1ModelObject):
	"""
	Represents Group object.
	All nested objects are in childs list.
	"""
	string = 'G()\n'
	end_string = 'G_()\n'
	cid = GROUP

	def __init__(self):
		SK1ModelObject.__init__(self)

class SK1MaskGroup(SK1ModelObject):
	"""
	Represents MaskGroup object.
	All nested objects are in childs list.
	The first object in childs list is the mask.
	"""
	string = 'M()\n'
	end_string = 'M_()\n'
	cid = MASKGROUP

	def __init__(self):
		SK1ModelObject.__init__(self)

#BlendGroup
#TextOnPath
#CompoundObject

#--- Primitive objects

class Rectangle(SK1ModelObject):
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
		SK1ModelObject.__init__(self)

	def update(self):
		if self.radius1 == self.radius2 == 0:
			args = self.trafo.coeff()
			self.string = 'r' + args.__str__() + '\n'
		else:
			args = self.trafo.coeff() + (self.radius1, self.radius2)
			self.string = 'r' + args.__str__() + '\n'

class Ellipse(SK1ModelObject):
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
	arc_type = sk1const.ArcPieSlice

	is_Ellipse = 1

	def __init__(self, trafo=None, start_angle=0.0, end_angle=0.0,
					arc_type=sk1const.ArcPieSlice, properties=None,
					duplicate=None):

		if trafo is not None and trafo.m11 == trafo.m21 == trafo.m12 == trafo.m22 == 0:
			trafo = Trafo(1, 0, 0, -1, trafo.v1, trafo.v2)
		self.trafo = trafo
		self.start_angle = start_angle
		self.end_angle = end_angle
		self.arc_type = arc_type
		self.properties = properties
		SK1ModelObject.__init__(self)

	def update(self):
		if self.start_angle == self.end_angle:
			args = self.trafo.coeff()
			self.string = 'e' + args.__str__() + '\n'
		else:
			args = self.trafo.coeff() + (self.start_angle, self.end_angle, self.arc_type)
			self.string = 'e' + args.__str__() + '\n'

class PolyBezier(SK1ModelObject):
	"""
	Represents Bezier curve object.
	b()             start a bezier obj
	bs(X, Y, CONT)  append a line segment
	bc(X1, Y1, X2, Y2, X3, Y3, CONT)  append a bezier segment
	bn()	        start a new path
	bC()            close path
	"""
	string = ''
	cid = CURVE
	style = []
	properties = None
	paths = ()

	is_Bezier = 1

	def __init__(self, paths=None, properties=None, duplicate=None, paths_list=[]):
		if paths:
			if isinstance(paths, tuple):
				self.paths = paths
			elif isinstance(paths, list):
				self.paths = tuple(paths)
			else:
				self.paths = (CreatePath(),)
		else:
			self.paths = None
		self.properties = properties
		self.paths_list = paths_list
		SK1ModelObject.__init__(self)

	def set_paths_from_list(self):
		self.paths = ()
		for path in self.paths_list:
			p = CreatePath()
			p.AppendLine(Point(*path[0]))
			points = path[1]
			for point in points:
				if len(point) == 2:
					p.AppendLine(Point(*point))
				else:
					point0 = Point(*point[0])
					point1 = Point(*point[1])
					point2 = Point(*point[2])
					p.AppendBezier(point0, point1, point2, point[3])
			if path[2]:
				p.ClosePath()
			self.paths = self.paths + (p,)

	def get_line_point(self, x, y, arg):
		return [x, y]

	def get_segment_point(self, x0, y0, x1, y1, x2, y2, cont):
		return [[x0, y0], [x1, y1], [x2, y2], cont]

	def set_list_from_paths(self):
		self.paths_list = []
		for path in self.paths:
			path_list = [None, [], const.CURVE_OPENED]
			plist = path.get_save()
			points = path_list[1]
			start = True
			for item in plist:
				if len(item) == 3:
					point = self.get_line_point(*item)
					if start:
						start = False
						path_list[0] = point
					else:
						points.append(point)
				elif len(item) == 7:
					points.append(self.get_segment_point(*item))
			if path.closed:path_list[2] = const.CURVE_CLOSED
			self.paths_list.append(path_list)

	def add_line(self, point):
		x, y = point
		self.string += 'bs' + (x, y, 0).__str__() + '\n'

	def add_segment(self, point):
		point0, point1, point2, cont = point
		args = (point0[0], point0[1], point1[0], point1[1], point2[0], point2[1], cont)
		self.string += 'bc' + args.__str__() + '\n'

	def update_from_list(self):
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
			if path[2] == const.CURVE_CLOSED:
				self.string += 'bC()\n'

	def update(self):
		if self.paths and not self.paths_list:
			self.set_list_from_paths()
		if self.paths_list and not self.paths:
			self.set_paths_from_list()
		self.update_from_list()


class SK1Text(SK1ModelObject):
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
	horiz_align = None
	vert_align = None
	chargap = None
	wordgap = None
	linegap = None

	def __init__(self, text, trafo, horiz_align, vert_align, chargap, wordgap, linegap):
		self.text = text
		self.trafo = trafo
		self.horiz_align = horiz_align
		self.vert_align = vert_align
		self.chargap = chargap
		self.wordgap = wordgap
		self.linegap = linegap
		SK1ModelObject.__init__(self)

	def update(self):
		text = self._encode_text(self.text)
		args = (text, self.trafo, self.horiz_align, self.vert_align,
			self.chargap, self.wordgap, self.linegap)
		self.string = 'txt' + args.__str__() + '\n'

	def _encode_text(self, text):
		output = ''
		for char in text:
			output += '\u0%x' % ord(char)
		return output


class SK1BitmapData(SK1ModelObject):
	"""
	Bitmap image data. Object is defined as:
	
	bm(ID)	
	
	The bitmap data follows as a base64 encoded JPEG file.
	"""
	string = ''
	cid = BITMAPDATA
	raw_image = None
	id = ''

	def __init__(self, id=''):
		if id: self.id = id
		SK1ModelObject.__init__(self)

	def read_data(self, fileobj):
		decoder = Base64Decode(SubFileDecode(fileobj, '-'))
		self.raw_image = Image.open(decoder)
		self.raw_image.load()

	def update(self):
		self.string = 'bm(%d)\n' % (self.id)
		self.end_string = '-\n'

	def write_content(self, fileobj):
		fileobj.write(self.string)
		vfile = Base64Encode(fileobj)
		if self.raw_image.mode == "CMYK":
			self.raw_image.save(vfile, 'JPEG', quality=100)
		else:
			self.raw_image.save(vfile, 'PNG')
		vfile.close()
		fileobj.write(self.end_string)


class SK1Image(SK1ModelObject):
	"""
	Image object. ID has to be the id of a previously defined
	bitmap data object (defined by bm). The object is defined as:
	im(TRAFO, ID)
	"""
	string = ''
	cid = IMAGE
	trafo = ()
	id = ''
	image = None

	def __init__(self, trafo=None, id='', image=None):
		self.trafo = trafo
		self.id = id
		self.image = image
		SK1ModelObject.__init__(self)

	def update(self):
		if self.image and not self.id:
			self.id = id(self.image)
		self.string = 'im' + (self.trafo.coeff(), self.id).__str__() + '\n'

	def write_content(self, fileobj):
		if self.image:
			fileobj.write('bm(%d)\n' % (self.id))
			vfile = Base64Encode(fileobj)
			if self.raw_image.mode == "CMYK":
				self.raw_image.save(vfile, 'JPEG', quality=100)
			else:
				self.raw_image.save(vfile, 'PNG')
			vfile.close()
			fileobj.write('-\n')
			fileobj.write(self.string)
