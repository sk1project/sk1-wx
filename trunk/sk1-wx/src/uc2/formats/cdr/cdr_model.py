# -*- coding: utf-8 -*-
#
#	Copyright (C) 2012 by Igor E. Novikov
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

import math
from copy import deepcopy

from uc2.utils import dword2py_int, long2py_float, word2py_int
from uc2.formats.riff.model import RiffList, RiffObject
from uc2.formats.cdr.cdr_const import CDR6, CDR7, CDR8, CDR9, CDR12, CDR13
from uc2.formats.cdr import cdr_const as const
from uc2.formats.sk2.sk2_const import NODE_CUSP, NODE_SMOOTH, NODE_SYMMETRICAL, \
									CURVE_CLOSED, CURVE_OPENED
from uc2.formats.cdr.cdr_utils import parse_matrix, parse_size_value, \
							parse_cdr_color



CDR_RECTANGLE = 1
CDR_ELLIPSE = 2
CDR_CURVE = 3
CDR_TEXT = 4
CDR_IMAGE = 5
CDR_POLYGON = 0x14


def find_chunk(chunks, chunk_tag):
	"""
	Finds chunk in chunk list by chunk tag.
	Returns first occurrence.
	"""
	for chunk in chunks:
		if chunk.chunk_tag == chunk_tag:
			return chunk
	return False

def parse_trafo(obj):
	"""
	Finds <trfd> chunk, parses trafo value and stores the value
	in object trafo field. 
	"""
	#Finds <loda> and <trfd> chunks
	lgob_chunk = find_chunk(obj.childs, 'lgob')
	trfl_chunk = find_chunk(lgob_chunk.childs, 'trfl')
	obj.trfd = find_chunk(trfl_chunk.childs, 'trfd')

	data = obj.loda.chunk

	for item in obj.loda.data_list:
		if item[0] == const.DATA_OUTL:
			obj.outl_id = str(data[item[1] + 8:item[1] + 12].encode('hex'))
		elif item[0] == const.DATA_FILD:
			obj.fill_id = str(data[item[1] + 8:item[1] + 12].encode('hex'))
		elif item[0] == const.DATA_STLT:
			obj.style_id = str(data[item[1] + 8:item[1] + 12].encode('hex'))

	obj.trafo = obj.trfd.trafo

def parse_rectangle(obj):
	data = obj.loda.chunk[8:]
	offset = 100
#		if self.version == CDR6: offset = 96

	for item in obj.loda.data_list:
		if item[0] == const.DATA_COORDS:
			offset = item[1]

	#Rectangle size
	w = parse_size_value(data[offset:offset + 4])
	h = parse_size_value(data[offset + 4:offset + 8])
	obj.rect_size = [w, h]
	obj.loda.cache_fields.append((offset + 8, 8, 'rect size'))

	#Radiuses of rectangle angles
	r1 = r2 = r3 = r4 = parse_size_value(data[offset + 8:offset + 12])
	if obj.version in [CDR6, CDR7]:
		obj.loda.cache_fields.append((offset + 16, 4, 'radius of angles'))
	else:
		r2 = parse_size_value(data[offset + 12:offset + 16])
		r3 = parse_size_value(data[offset + 16:offset + 20])
		r4 = parse_size_value(data[offset + 20:offset + 24])
		obj.loda.cache_fields.append((offset + 16, 16, 'radiuses of angles'))
	obj.radiuses = [r1, r2, r3, r4]

def parse_ellipse(obj):
	data = obj.loda.chunk
	offset = 108
	for item in obj.loda.data_list:
		if item[0] == const.DATA_COORDS:
			offset = item[1] + 8

	#Ellipse size
	w = parse_size_value(data[offset:offset + 4])
	h = parse_size_value(data[offset + 4:offset + 8])
	obj.ellipse_size = [w, h]
	obj.loda.cache_fields.append((offset, 8, 'ellipse size'))

	#Ellipse angles
	start = math.radians(long2py_float(data[offset + 8:offset + 12]) / 1000000.0)
	end = math.radians(long2py_float(data[offset + 12:offset + 16]) / 1000000.0)
	rot = math.radians(long2py_float(data[offset + 16:offset + 20]) / 1000000.0)
	obj.ellipse_angles = [start, end, rot]
	obj.loda.cache_fields.append((offset + 8, 12, 'ellipse angles'))

def parse_polygon(obj):
	data = obj.loda.chunk
	offset = 112
	if obj.version == CDR6:offset = 100
	if obj.version == CDR13:offset = 104

	#Polygon angles
	obj.plg_num = dword2py_int(data[offset:offset + 4])
	obj.loda.cache_fields.append((offset, 4, 'num of polygon edges'))

def parse_curve(obj):
	data = obj.loda.chunk
	offset = 108

	for item in obj.loda.data_list:
		if item[0] == const.DATA_COORDS:
			offset = item[1] + 8

	obj.paths = []
	path = []
	points = []
	point1 = []
	point2 = []

	pointnum = dword2py_int(data[offset:offset + 4])
	obj.num_of_points = pointnum
	obj.loda.cache_fields.append((offset, 4, 'num of points'))
	obj.loda.cache_fields.append((offset + 4, 8 * pointnum, 'curve points'))
	obj.loda.cache_fields.append((offset + 4 + pointnum * 8, pointnum, 'point flags'))

	for i in range (pointnum):
		x = parse_size_value(data[offset + 4 + i * 8:offset + 8 + i * 8])
		y = parse_size_value(data[offset + 8 + i * 8:offset + 12 + i * 8])

		point_type = ord(data[offset + 4 + pointnum * 8 + i])
		if point_type & 0x10 == 0 and point_type & 0x20 == 0:
			marker = NODE_CUSP
		if point_type & 0x10 == 0x10:
			marker = NODE_SMOOTH
		if point_type & 0x20 == 0x20:
			marker = NODE_SYMMETRICAL

		if point_type & 0x40 == 0 and point_type & 0x80 == 0:
			if path:
				path.append(deepcopy(points))
				path.append(CURVE_OPENED)
				obj.paths.append(deepcopy(path))
			path = []
			points = []
			point1 = []
			point2 = []
			path.append([x, y])
		if point_type & 0x40 == 0x40 and point_type & 0x80 == 0:
			points.append([x, y])
			point1 = []
			point2 = []
		if point_type & 0x40 == 0 and point_type & 0x80 == 0x80:
			points.append(deepcopy([point1, point2, [x, y], marker]))
			point1 = []
			point2 = []
		if point_type & 0x40 == 0x40 and point_type & 0x80 == 0x80:
			if point1:
				point2 = [x, y]
			else:
				point1 = [x, y]
		if point_type & 8 == 8:
			if path and points:
				path.append(deepcopy(points))
				path.append(CURVE_CLOSED)
				obj.paths.append(deepcopy(path))
				path = []
				points = []
	if path:
		path.append(deepcopy(points))
		path.append(CURVE_OPENED)
		obj.paths.append(deepcopy(path))

def parse_text(obj):pass
def parse_image(obj):pass

##############################################
#            Graphics objects
##############################################

class CdrGraphObj(RiffList):
	"""
	The class represents CDR Rectangle object.
	"""
	trfd = None
	loda = None
	style_id = None
	fill_id = None
	outl_id = None

	def __init__(self, chunk):
		RiffList.__init__(self, chunk)

	def update(self):
		#Finds <loda> and <trfd> chunks
		lgob_chunk = find_chunk(self.childs, 'lgob')
		trfl_chunk = find_chunk(lgob_chunk.childs, 'trfl')
		self.trfd = find_chunk(trfl_chunk.childs, 'trfd')

		data = self.loda.chunk

		for item in self.loda.data_list:
			if item[0] == const.DATA_OUTL:
				self.outl_id = str(data[item[1] + 8:item[1] + 12].encode('hex'))
			elif item[0] == const.DATA_FILD:
				self.fill_id = str(data[item[1] + 8:item[1] + 12].encode('hex'))
			elif item[0] == const.DATA_STLT:
				self.style_id = str(data[item[1] + 8:item[1] + 12].encode('hex'))

		self.trafo = self.trfd.trafo

class CdrRectangle(CdrGraphObj):
	"""
	The class represents CDR Rectangle object.
	"""

	def __init__(self, chunk):
		CdrGraphObj.__init__(self, chunk)

	def resolve(self):
		name = 'Rectangle'
		return (False, name, str(self.chunk_size))

	def update(self):
		CdrGraphObj.update(self)
		data = self.loda.chunk[8:]
		offset = 100
#		if self.version == CDR6: offset = 96

		for item in self.loda.data_list:
			if item[0] == const.DATA_COORDS:
				offset = item[1]

		#Rectangle size
		w = parse_size_value(data[offset:offset + 4])
		h = parse_size_value(data[offset + 4:offset + 8])
		self.rect_size = [w, h]
		self.loda.cache_fields.append((offset + 8, 8, 'rect size'))

		#Radiuses of rectangle angles
		r1 = r2 = r3 = r4 = parse_size_value(data[offset + 8:offset + 12])
		if self.version in [CDR6, CDR7]:
			self.loda.cache_fields.append((offset + 16, 4, 'radius of angles'))
		else:
			r2 = parse_size_value(data[offset + 12:offset + 16])
			r3 = parse_size_value(data[offset + 16:offset + 20])
			r4 = parse_size_value(data[offset + 20:offset + 24])
			self.loda.cache_fields.append((offset + 16, 16, 'radiuses of angles'))
		self.radiuses = [r1, r2, r3, r4]

	def translate(self, translator):
		translator.create_rectangle(self)

class CdrEllipse(CdrGraphObj):
	"""
	The class represents CDR Ellipse object.
	"""

	def __init__(self, chunk):
		CdrGraphObj.__init__(self, chunk)

	def resolve(self):
		name = 'Ellipse'
		return (False, name, str(self.chunk_size))

	def update(self):
		CdrGraphObj.update(self)
		data = self.loda.chunk
		offset = 108
		for item in self.loda.data_list:
			if item[0] == const.DATA_COORDS:
				offset = item[1] + 8

		#Ellipse size
		w = parse_size_value(data[offset:offset + 4])
		h = parse_size_value(data[offset + 4:offset + 8])
		self.ellipse_size = [w, h]
		self.loda.cache_fields.append((offset, 8, 'ellipse size'))

		#Ellipse angles
		start = math.radians(long2py_float(data[offset + 8:offset + 12]) / 1000000.0)
		end = math.radians(long2py_float(data[offset + 12:offset + 16]) / 1000000.0)
		rot = math.radians(long2py_float(data[offset + 16:offset + 20]) / 1000000.0)
		self.ellipse_angles = [start, end, rot]
		self.loda.cache_fields.append((offset + 8, 12, 'ellipse angles'))

	def translate(self, translator):
		translator.create_ellipse(self)

class CdrPolygon(CdrGraphObj):
	"""
	The class represents CDR Polygon object.
	"""

	def __init__(self, chunk):
		CdrGraphObj.__init__(self, chunk)

	def resolve(self):
		name = 'Polygon'
		return (False, name, str(self.chunk_size))

	def update(self):
		CdrGraphObj.update(self)
		data = self.loda.chunk
		offset = 112
		if self.version == CDR6:offset = 100
		if self.version == CDR13:offset = 104

		#Polygon angles
		self.plg_num = dword2py_int(data[offset:offset + 4])
		self.loda.cache_fields.append((offset, 4, 'num of polygon edges'))

	def translate(self, translator):
		translator.create_polygon(self)


class CdrCurve(CdrGraphObj):
	"""
	The class represents CDR Curve object.
	"""

	paths = []

	def __init__(self, chunk):
		CdrGraphObj.__init__(self, chunk)

	def resolve(self):
		name = 'Curve'
		return (False, name, str(self.chunk_size))

	def update(self):
		CdrGraphObj.update(self)
		data = self.loda.chunk
		offset = 108

		for item in self.loda.data_list:
			if item[0] == const.DATA_COORDS:
				offset = item[1] + 8

		self.paths = []
		path = []
		points = []
		point1 = []
		point2 = []

		pointnum = dword2py_int(data[offset:offset + 4])
		self.num_of_points = pointnum
		self.loda.cache_fields.append((offset, 4, 'num of points'))
		self.loda.cache_fields.append((offset + 4, 8 * pointnum, 'curve points'))
		self.loda.cache_fields.append((offset + 4 + pointnum * 8, pointnum, 'point flags'))

		for i in range (pointnum):
			x = parse_size_value(data[offset + 4 + i * 8:offset + 8 + i * 8])
			y = parse_size_value(data[offset + 8 + i * 8:offset + 12 + i * 8])

			point_type = ord(data[offset + 4 + pointnum * 8 + i])
			if point_type & 0x10 == 0 and point_type & 0x20 == 0:
				marker = NODE_CUSP
			if point_type & 0x10 == 0x10:
				marker = NODE_SMOOTH
			if point_type & 0x20 == 0x20:
				marker = NODE_SYMMETRICAL

			if point_type & 0x40 == 0 and point_type & 0x80 == 0:
				if path:
					path.append(deepcopy(points))
					path.append(CURVE_OPENED)
					self.paths.append(deepcopy(path))
				path = []
				points = []
				point1 = []
				point2 = []
				path.append([x, y])
			if point_type & 0x40 == 0x40 and point_type & 0x80 == 0:
				points.append([x, y])
				point1 = []
				point2 = []
			if point_type & 0x40 == 0 and point_type & 0x80 == 0x80:
				points.append(deepcopy([point1, point2, [x, y], marker]))
				point1 = []
				point2 = []
			if point_type & 0x40 == 0x40 and point_type & 0x80 == 0x80:
				if point1:
					point2 = [x, y]
				else:
					point1 = [x, y]
			if point_type & 8 == 8:
				if path and points:
					path.append(deepcopy(points))
					path.append(CURVE_CLOSED)
					self.paths.append(deepcopy(path))
					path = []
					points = []
		if path:
			path.append(deepcopy(points))
			path.append(CURVE_OPENED)
			self.paths.append(deepcopy(path))

	def translate(self, translator):
		translator.create_curve(self)

class CdrImage(CdrGraphObj):
	"""
	The class represents CDR Image object.
	"""

	def __init__(self, chunk):
		CdrGraphObj.__init__(self, chunk)

	def resolve(self):
		name = 'Image'
		return (False, name, str(self.chunk_size))

	def update(self):
		CdrGraphObj.update(self)

	def translate(self, translator):
		translator.create_image(self)

class CdrText(CdrGraphObj):
	"""
	The class represents CDR Text object.
	"""

	def __init__(self, chunk):
		CdrGraphObj.__init__(self, chunk)

	def resolve(self):
		name = 'Text'
		return (False, name, str(self.chunk_size))

	def update(self):
		CdrGraphObj.update(self)

	def translate(self, translator):
		translator.create_text(self)

obj_dict = {
		CDR_RECTANGLE:CdrRectangle,
		CDR_ELLIPSE:CdrEllipse,
		CDR_CURVE:CdrCurve,
		CDR_TEXT:CdrText,
		CDR_IMAGE:CdrImage,
		CDR_POLYGON:CdrPolygon,
		}

##############################################
#            Universal CDR object
##############################################
obj_parse = {
		CDR_RECTANGLE: (parse_rectangle, 'Rectangle'),
		CDR_ELLIPSE: (parse_ellipse, 'Ellipse'),
		CDR_CURVE: (parse_curve, 'Curve'),
		CDR_TEXT: (parse_text, 'Text'),
		CDR_IMAGE: (parse_image, 'Image'),
		CDR_POLYGON: (parse_polygon, 'Polygon'),
		}

class CdrUniObject(RiffList):
	"""
	The class represents universal CDR object.
	This is an universal graphics object representation and on model update 
	object specific fields will be created.
	"""
	trfd = None
	loda = None
	style_id = None
	fill_id = None
	outl_id = None

	def __init__(self, chunk):
		RiffList.__init__(self, chunk)

	def resolve(self):
		name = 'Object'
		if not self.obj_type is None and obj_parse.has_key(self.obj_type):
			name = obj_parse[self.obj_type][1]
		return (False, name, str(self.chunk_size))

	def do_update(self, presenter):
		RiffList.do_update(self, presenter)
		self.obj_type = None

		lgob_chunk = find_chunk(self.childs, 'lgob')
		self.loda = find_chunk(lgob_chunk.childs, 'loda')
		self.obj_type = dword2py_int(self.loda.chunk[0x18:0x1c])

		if not self.obj_type is None and obj_parse.has_key(self.obj_type):
			parse_trafo(self)
			obj_parse[self.obj_type][0](self)

	def translate(self, translator):
		if self.obj_type is None:
			return
		elif self.obj_type == CDR_RECTANGLE:
			translator.create_rectangle(self)
		elif self.obj_type == CDR_ELLIPSE:
			translator.create_ellipse(self)
		elif self.obj_type == CDR_CURVE:
			translator.create_curve(self)
		elif self.obj_type == CDR_TEXT:
			translator.create_text(self)
		elif self.obj_type == CDR_IMAGE:
			translator.create_image(self)
		elif self.obj_type == CDR_POLYGON:
			translator.create_polygon(self)


##############################################
#            Structural objects
##############################################
class CdrPage(RiffList):
	"""
	The class represents CDR page object.
	All graphics objects on page are members of CdrPage childs list.
	"""

	def __init__(self, chunk):
		RiffList.__init__(self, chunk)

	def resolve(self):
		name = 'Page'
		return (False, name, str(self.chunk_size))

	def translate(self, translator):
		if translator.start_page(self):
			gobj_chunk = find_chunk(self.childs, 'gobj')
			layers = [] + gobj_chunk.childs
			layers.reverse()
			for layer in layers:
				layer.translate(translator)
			translator.close_page()


class CdrLayer(RiffList):
	"""
	The class represents CDR layer object.
	All graphics objects on layer are members of CdrLayer childs list.
	"""

	layer_name = ''

	def __init__(self, chunk):
		RiffList.__init__(self, chunk)

	def resolve(self):
		name = 'Layer'
		if self.layer_name: name += ' "%s"' % (self.layer_name)
		return (False, name, str(self.chunk_size))

	def update(self):
		#Finds <loda> chunk
		lgob_chunk = find_chunk(self.childs, 'lgob')
		self.loda = find_chunk(lgob_chunk.childs, 'loda')

		for item in self.loda.data_list:
			if item[0] == const.DATA_NAME:
				offset = item[1] + 8

		try:
			#Gets layer name
			data = self.loda.chunk[offset:]
			zero = '00'.decode('hex')
			self.layer_name = data.rstrip(zero).decode(self.config.system_encoding)
			if self.version in [CDR12, CDR13]:
				self.layer_name = (data.rstrip(zero) + zero).decode('utf-16')
			self.loda.cache_fields.append((offset, len(data), 'layer name'))
		except:
			self.layer_name = ''

	def translate(self, translator):
		translator.start_layer(self)
		objs = [] + self.childs
		objs.reverse()
		for obj in objs:
			obj.translate(translator)
		translator.close_layer()


class CdrGroup(RiffList):
	"""
	The class represents CDR group object.
	All graphics objects in group are members of CdrGroup childs list.
	"""

	def __init__(self, chunk):
		RiffList.__init__(self, chunk)

	def resolve(self):
		name = 'Group'
		return (False, name, str(self.chunk_size))

	def translate(self, translator):
		translator.start_group()
		objs = [] + self.childs
		objs.reverse()
		for obj in objs:
			obj.translate(translator)
		translator.close_group()

class CdrDocList(RiffList):
	"""
	The class represents CDR <doc > list.	
	The object extracts default page size from child <mcfg> chunk.
	"""

	def __init__(self, chunk):
		RiffList.__init__(self, chunk)

	def update(self):
		mcfg = find_chunk(self.childs, 'mcfg')
		data = mcfg.chunk
		offset = 12
		if self.version == CDR7: offset = 8
		if self.version == CDR6: offset = 36
		if self.version == CDR13: offset = 20
		self.page_width = parse_size_value(data[offset:offset + 4])
		mcfg.cache_fields.append((offset, 4, 'page width'))
		self.page_height = parse_size_value(data[offset + 4:offset + 8])
		mcfg.cache_fields.append((offset + 4, 4, 'page height'))

	def translate(self, translator):
		for child in self.childs:
			child.translate(translator)
		translator.set_doc_properties(self)

class CdrObject(RiffList):
	"""
	The class represents CDR object.
	This is a temporary object and on model update is replaced by according
	graphics object specific instance.
	"""

	def __init__(self, chunk):
		RiffList.__init__(self, chunk)

	def resolve(self):
		name = 'Object'
		return (False, name, str(self.chunk_size))

	def do_update(self, presenter):
		type = None

		lgob_chunk = find_chunk(self.childs, 'lgob')
		loda_chunk = find_chunk(lgob_chunk.childs, 'loda')
		type = dword2py_int(loda_chunk.chunk[0x18:0x1c])

		if not type is None and obj_dict.has_key(type):
			new_obj = obj_dict[type](self.chunk)
			new_obj.parent = self.parent
			new_obj.version = self.version
			new_obj.childs = self.childs
			new_obj.loda = loda_chunk

			index = self.parent.childs.index(self)
			self.parent.childs.insert(index, new_obj)
			self.parent.childs.remove(self)
			new_obj.do_update(presenter)
		else:
			RiffList.do_update(self, presenter)

##############################################
#            Property objects
##############################################

class CdrBMPStorage(RiffObject):
	"""
	The class represents CDR bitmap object.
	This is bitmap storage with object identifier.
	"""

	def __init__(self, chunk):
		RiffObject.__init__(self, chunk)

	def resolve(self):
		name = 'Bitmap'
		return (True, name, str(self.chunk_size))

class CdrFontProperty(RiffObject):
	"""
	The class represents CDR font property.
	This is a record about used font with object identifier.
	"""

	def __init__(self, chunk):
		RiffObject.__init__(self, chunk)

	def resolve(self):
		name = 'FontProperty'
		return (True, name, str(self.chunk_size))

	def update(self):
		data = self.chunk[8:]
		self.font_id = str(data[0:2].encode('hex'))
		self.cache_fields.append((8, 2, 'font id'))

		self.encoding = word2py_int(data[2:4])
		self.cache_fields.append((10, 2, 'font encoding'))

		self.font_flags = str(data[4:18].encode('hex'))
		self.cache_fields.append((12, 14, 'font flags'))

		try:
			#Gets font name
			data = data[18:52]
			zero = '00'.decode('hex')
			if not self.version in [CDR6, CDR7, CDR8, CDR9]:
				self.font_name = (data.rstrip(zero) + zero).decode('utf-16')
			else:
				self.font_name = data.rstrip(zero).decode(self.config.system_encoding)

			self.cache_fields.append((26, len(data), 'font name'))
		except:
			self.font_name = ''

	def translate(self, translator):
		translator.add_font_prop(self)

class CdrFillProperty(RiffObject):
	"""
	The class represents CDR fill property.
	This is a record about used fill color/pattern with object identifier.
	"""

	def __init__(self, chunk):
		RiffObject.__init__(self, chunk)

	def resolve(self):
		name = 'FillProperty'
		return (True, name, str(self.chunk_size))

	def update(self):
		self.fill_id = str(self.chunk[8:12].encode('hex'))
		self.cache_fields.append((8, 4, 'fill id'))

		offset = 12
		if self.version == CDR13: offset += 8
		self.fill_type = ord(self.chunk[offset])

		self.cache_fields.append((offset, 1, 'fill type'))

		if not self.fill_type == 1:
			self.fill_color = []
			return

		offset = 16
		if self.version == CDR13: offset = 35
		self.color_space_type = ord(self.chunk[offset])
		self.cache_fields.append((offset, 1, 'color space type'))

		offset = 24
		if self.version == CDR13: offset = 43

		self.fill_color = parse_cdr_color(self.color_space_type, self.chunk[offset:offset + 4])
		if self.fill_color:
			self.cache_fields.append((offset, 4, 'color value'))

	def translate(self, translator):
		translator.add_fill_prop(self)


class CdrOutlineProperty(RiffObject):
	"""
	The class represents CDR outline property.
	This is a record about used outline pattern with object identifier.
	"""
	stroke_dashes = []

	def __init__(self, chunk):
		RiffObject.__init__(self, chunk)

	def resolve(self):
		name = 'OutlineProperty'
		return (True, name, str(self.chunk_size))

	def update(self):
		self.stroke_id = str(self.chunk[8:12].encode('hex'))
		self.cache_fields.append((8, 4, 'outline id'))

		data = self.chunk[8:]

		ls_offset = 4
		lc_offset = 6
		ct_offset = 8
		lw_offset = 12
		offset = 28
		dash_offset = 104

		if self.version == CDR13:
			ls_offset = 24
			lc_offset = 26
			ct_offset = 28
			lw_offset = 30
			offset = 40
			dash_offset = 116

		self.stroke_spec = ord(data[ls_offset])
		self.cache_fields.append((ls_offset + 8, 1, 'outline specification'))

		self.stroke_caps = ord(data[lc_offset])
		self.cache_fields.append((lc_offset + 8, 1, 'outline caps'))

		self.stroke_join = ord(data[ct_offset])
		self.cache_fields.append((ct_offset + 8, 1, 'outline corners'))

		self.stroke_width = parse_size_value(data[lw_offset:lw_offset + 4])
		self.cache_fields.append((lw_offset + 8, 1, 'outline width'))

		dashnum = word2py_int(data[dash_offset:dash_offset + 2])
		self.cache_fields.append((dash_offset + 8, 2, 'number of dash records'))

		if dashnum > 0:
			self.stroke_dashes = range(dashnum)
			for i in self.stroke_dashes:
				dash = word2py_int(data[dash_offset + 2 + i * 2:dash_offset + 4 + i * 2])
				self.stroke_dashes[i] = dash
			self.cache_fields.append((dash_offset + 10, 2 * dashnum, 'dash records'))

		offset += 0x30
		self.color_space_type = ord(data[offset])
		self.cache_fields.append((offset + 8, 1, 'color space type'))

		offset += 16
		self.stroke_color = parse_cdr_color(self.color_space_type, self.chunk[offset:offset + 4])
		if self.stroke_color:
			self.cache_fields.append((offset, 4, 'color value'))

	def translate(self, translator):
		translator.add_stroke_prop(self)


class CdrLodaProperty(RiffObject):
	"""
	The class represent CDR <loda> chunk - main source of data in CDR
	document model.
	The object does initial generic parsing of <loda> chunk header.
	"""

	def __init__(self, chunk):
		RiffObject.__init__(self, chunk)

		data = self.chunk

		#<loda> chunk header processing
		self.data_num = dword2py_int(data[12:16])
		self.cache_fields.append((12, 4, 'number of data'))

		self.data_start = dword2py_int(data[16:20])
		self.cache_fields.append((16, 4, 'data start'))

		self.data_type_start = dword2py_int(data[20:24])
		self.cache_fields.append((20, 4, 'data types start'))

		self.object_type = dword2py_int(data[24:28])
		self.cache_fields.append((24, 4, 'object type'))

		self.data_list = []

		num = self.data_num
		start = self.data_start + 8
		start_t = self.data_type_start + 8

		self.cache_fields.append((start, 4 * num, 'data offsets'))
		self.cache_fields.append((start_t, 4 * num, 'data type offsets'))

		for i in range(self.data_num):
			offset = dword2py_int(data[start + i * 4:start + i * 4 + 4])
			argtype = dword2py_int(data[start_t + (num - 1 - i) * 4:start_t + (num - 1 - i) * 4 + 4])
			self.data_list.append([argtype, offset])

class CdrTrafoProperty(RiffObject):
	"""
	The class represent CDR <trfd> chunk - source of affine trasformation
	matrix in CDR document model.
	The object does parsing of <trfd> chunk.
	"""
	trafo = []

	def __init__(self, chunk):
		RiffObject.__init__(self, chunk)

	def update(self):

		data = self.chunk[8:]

		#<trfd> chunk header processing
		self.data_num = dword2py_int(data[4:8])
		self.cache_fields.append((12, 4, 'number of data'))

		self.data_start = dword2py_int(data[8:12])
		self.cache_fields.append((16, 4, 'data start'))

		self.data_type_start = dword2py_int(data[12:16])
		self.cache_fields.append((20, 4, 'data types start'))

		#transformation matrix processing
		start = 32 + 8
		if self.version == CDR13: start += 8
		data = self.chunk[start:start + 48]
		self.cache_fields.append((start, 48, 'trafo matrix'))
		self.trafo = parse_matrix(data)


generic_dict = {
		'doc ':CdrDocList,
		'page':CdrPage,
		'layr':CdrLayer,
		'grp ':CdrGroup,
		'obj ':CdrUniObject,
		'bmp ':CdrBMPStorage,
		'font':CdrFontProperty,
		'fild':CdrFillProperty,
		'fill':CdrFillProperty,
		'outl':CdrOutlineProperty,
		'loda':CdrLodaProperty,
		'trfd':CdrTrafoProperty,
		}
