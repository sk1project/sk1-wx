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

import sys, os

from uc2 import _, events, msgconst, uc2const
from uc2.formats.pdxf import const
from uc2.formats.sk1 import sk1const
from uc2.formats.loader import AbstractLoader
from uc2.formats.sk1.model import SK1Document, SK1Layout, SK1Grid, SK1Pages, \
SK1Page, SK1Layer, SK1MasterLayer, SK1GuideLayer, SK1Guide, SK1Group, \
SK1MaskGroup, Rectangle, Ellipse, PolyBezier, SK1Text, SK1BitmapData, SK1Image, \
MultiGradient, EmptyPattern, SolidPattern, LinearGradient, RadialGradient, \
ConicalGradient, HatchingPattern, ImageTilePattern, Style, Trafo, Point

class SK1_Loader(AbstractLoader):

	name = 'SK1_Loader'

	paths = []
	options = {}
	pages = None

	string = ''
	line = ''
	active_page = None
	active_layer = None
	parent_stack = []
	obj_style = []

	style = None
	style_dict = {}
	pattern = None
	gradient = None

	def do_load(self):
		self.file.readline()
		self.style = Style()
		while True:
			self.line = self.file.readline()
			if not self.line: break
			self.line = self.line.rstrip('\r\n')

			self.check_loading()

			if self.line:
				try:
					code = compile('self.' + self.line, '<string>', 'exec')
					exec code
				except:
					print 'error>>', self.line
					errtype, value, traceback = sys.exc_info()
					print errtype, value, traceback

	def set_style(self, obj):
		obj.properties = self.style
		self.style = Style()

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

	#---PROPERTIES
	def gl(self, colors):
		self.gradient = MultiGradient(colors)

	def pe(self):
		self.pattern = EmptyPattern

	def ps(self, color):
		self.pattern = SolidPattern(color)

	def pgl(self, dx, dy, border=0):
		if not self.gradient: self.gradient = MultiGradient()
		self.pattern = LinearGradient(self.gradient, Point(dx, dy), border)

	def pgr(self, dx, dy, border=0):
		if not self.gradient: self.gradient = MultiGradient()
		self.pattern = RadialGradient(self.gradient, Point(dx, dy), border)

	def pgc(self, cx, cy, dx, dy):
		if not self.gradient: self.gradient = MultiGradient()
		self.pattern = ConicalGradient(self.gradient, Point(cx, cy), Point(dx, dy))

	def phs(self, color, background, dx, dy, dist, width):
		self.pattern = HatchingPattern(color, background, Point(dx, dy), dist, width)

	def pit(self, id, trafo):
		trafo = Trafo(*trafo)
		if self.presenter.resources.has_key(id):
			image = self.presenter.resources[id]
			self.pattern = ImageTilePattern(image, trafo)

	def fp(self, color=None):
		if color is None:
			self.style.fill_pattern = self.pattern
		else:
			self.style.fill_pattern = SolidPattern(color)

	def fe(self):
		self.style.fill_pattern = EmptyPattern

	def ft(self, bool):
		self.style.fill_transform = bool

	def lp(self, color=None):
		if color is None:
			self.style.line_pattern = self.pattern
		else:
			self.style.line_pattern = SolidPattern(color)

	def le(self):
		self.style.line_pattern = EmptyPattern

	def lw(self, width):
		self.style.line_width = width

	def lc(self, cap):
		if not 1 <= cap <= 3: cap = 1
		self.style.line_cap = cap

	def lj(self, join):
		self.style.line_join = join

	def ld(self, dashes):
		self.style.line_dashes = dashes

	def la1(self, args=None):
		self.style.line_arrow1 = args

	def la2(self, args=None):
		self.style.line_arrow2 = args

	def Fs(self, size):
		self.style.font_size = size

	def Fn(self, name):
		self.style.font = name

	def dstyle(self, name=''):
		if name:
			self.style.name = name
			self.model.styles[name] = self.style
			self.style = Style()

	def style(self, name=''):
		pass

	def use_style(self, name=''):
		pass

	#---STRUCTURAL ELEMENTS
	def document(self, *args):
		self.add_object(SK1Document(self.config))

	def layout(self, *args):
		if len(args) > 2:
			format = args[0]
			size = args[1]
			orientation = args[2]
		else:
			if isinstance(args[0], str):
				format = args[0]
				orientation = args[1]
				if not format in uc2const.PAGE_FORMAT_NAMES: format = 'A4'
				size = uc2const.PAGE_FORMATS[format]
			else:
				format = ''
				size = args[0]
				orientation = args[1]
		obj = SK1Layout(format, size, orientation)
		self.add_object(obj, self.model)
		self.model.layout = obj

	def grid(self, grid, visibility, grid_color, layer_name):
		obj = SK1Grid(grid, visibility, grid_color, layer_name)
		self.add_object(obj, self.model)
		self.model.grid = obj

	def add_pages(self, *args):
		self.pages = SK1Pages()
		self.add_object(self.pages, self.model)
		self.model.pages = self.pages

	def page(self, name='', format='', size='', orientation=0):
		if self.pages is None:
			self.add_pages()
		if not format and not size:
			format = '' + self.model.layout.format
			size = () + self.model.layout.size
			orientation = self.model.layout.orientation
		page = SK1Page(name, format, size, orientation)
		self.active_page = page
		self.active_layer = None
		self.parent_stack = []
		self.add_object(page, self.pages)

	def layer(self, name, p1, p2, p3, p4, layer_color):
		if self.active_page is None:
			self.page()
		layer = SK1Layer(name, p1, p2, p3, p4, layer_color)
		self.active_layer = layer
		self.add_object(layer, self.active_page)

	def masterlayer(self, name, p1, p2, p3, p4, layer_color):
		mlayer = SK1MasterLayer(name, p1, p2, p3, p4, layer_color)
		self.active_layer = mlayer
		self.add_object(mlayer, self.model)
		self.model.masterlayer = mlayer

	def guidelayer(self, name, p1, p2, p3, p4, layer_color):
		glayer = SK1GuideLayer(name, p1, p2, p3, p4, layer_color)
		self.active_layer = glayer
		self.add_object(glayer, self.model)
		self.model.guidelayer = glayer

	def guide(self, point, orientation):
		self.add_object(SK1Guide(point, orientation))

	#---GROUPS
	def G(self):
		group = SK1Group()
		self.add_object(group)
		self.parent_stack.append(group)

	def G_(self):
		self.parent_stack = self.parent_stack[:-1]

	def M(self):
		mgroup = SK1MaskGroup()
		self.add_object(mgroup)
		self.parent_stack.append(mgroup)

	def M_(self):
		self.parent_stack = self.parent_stack[:-1]

	def B(self):
		group = SK1Group()
		self.string = group.string
		self.line = ''
		self.add_object(group)
		self.parent_stack.append(group)

	def Bi(self, *args):self.string = ''

	def B_(self):
		self.parent_stack = self.parent_stack[:-1]

	def PT(self):
		group = SK1Group()
		self.string = group.string
		self.line = ''
		self.add_object(group)
		self.parent_stack.append(group)

	def pt(self, *args):self.string = ''

	def PT_(self):
		self.parent_stack = self.parent_stack[:-1]

	def PC(self, *args):
		group = SK1Group()
		self.string = group.string
		self.line = ''
		self.add_object(group)
		self.parent_stack.append(group)

	def PC_(self):
		self.parent_stack = self.parent_stack[:-1]

	#---PRIMITIVES
	def r(self, m11, m12, m21, m22, dx, dy, radius1=0, radius2=0):
		trafo = Trafo(m11, m12, m21, m22, dx, dy)
		obj = Rectangle(trafo, radius1, radius2)
		self.set_style(obj)
		self.add_object(obj)

	def e(self, m11, m12, m21, m22, dx, dy, start_angle=0.0, end_angle=0.0,
		arc_type=sk1const.ArcPieSlice):
		trafo = Trafo(m11, m12, m21, m22, dx, dy)
		obj = Ellipse(trafo, start_angle, end_angle, arc_type)
		self.set_style(obj)
		self.add_object(obj)

	def b(self):
		self.paths = [[None, [], const.CURVE_OPENED]]
		obj = PolyBezier(paths_list=self.paths)
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
		self.paths.append([None, [], const.CURVE_OPENED])

	def bC(self):
		self.paths[-1][2] = const.CURVE_CLOSED

	def txt(self, text, trafo, horiz_align, vert_align, chargap, wordgap, linegap):
		if text: text = self._decode_text(text)
		obj = SK1Text(text, trafo, horiz_align, vert_align, chargap, wordgap, linegap)
		self.set_style(obj)
		self.add_object(obj)

	def _decode_text(self, text):
		output = ''
		for word in text.split('\u')[1:]:
				num = int(word, 16)
				if num > 256:
					output += ('\u' + word).decode('raw_unicode_escape')
				else:
					output += chr(int(num)).decode('latin1')
		return output

	def bm(self, id):
		bmd_obj = SK1BitmapData(id)
		self.add_object(bmd_obj)
		try:
			bmd_obj.read_data(self.file)
		except:
			print 'error>>', self.line
			errtype, value, traceback = sys.exc_info()
			print errtype, value, traceback
		self.presenter.resources[id] = bmd_obj.raw_image

	def im(self, trafo, id):
		trafo = Trafo(*trafo)
		image = None
		if self.presenter.resources.has_key(id):
			image = self.presenter.resources[id]
		self.add_object(SK1Image(trafo, id, image))

	def eps(self, *args):self.string = ''


class SK1_Saver:

	name = 'SK1_Saver'

	def __init__(self):
		pass

	def save(self, presenter, path):

		try:
			file = open(path, 'wb')
		except:
			errtype, value, traceback = sys.exc_info()
			msg = _('Cannot open %s file for writing') % (path)
			events.emit(events.MESSAGES, msgconst.ERROR, msg)
			raise IOError(errtype, msg + '\n' + value, traceback)

		presenter.update()
		presenter.model.write_content(file)
		file.close()
