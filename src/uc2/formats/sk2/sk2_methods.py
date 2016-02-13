# -*- coding: utf-8 -*-
#
#	Copyright (C) 2011-2015 by Igor E. Novikov
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

from uc2 import _, uc2const
from uc2.formats.sk2 import sk2_model

def create_new_doc(config):
	doc = sk2_model.Document(config)

	layer = sk2_model.Layer(config)
	page = sk2_model.Page(config)
	add_child(page, layer)
	page.layer_counter += 1

	pages = sk2_model.Pages(config)
	add_child(pages, page)
	pages.page_counter += 1

	dl = sk2_model.DesktopLayers(config)
	ml = sk2_model.MasterLayers(config)
	gl = sk2_model.GridLayer(config)
	guide = sk2_model.GuideLayer(config)
	add_childs(doc, [pages, dl, ml, gl, guide])

	return doc

def add_childs(parent, childs=[]):
	if childs:
		for child in childs:
			parent.childs.append(child)
			child.parent = parent

def add_child(parent, child):
	add_childs(parent, [child, ])


class SK2_Methods:

	presenter = None

	def __init__(self, presenter):
		self.presenter = presenter

	def update(self):
		self.model = self.presenter.model
		self.config = self.presenter.model.config

	#---DOCUMENT

	def get_doc_origin(self):
		return self.presenter.model.doc_origin

	def set_doc_origin(self, origin):
		self.presenter.model.doc_origin = origin

	def get_doc_units(self):
		return self.presenter.model.doc_units

	def set_doc_units(self, units):
		self.presenter.model.doc_units = units

	def set_doc_metainfo(self, metainfo):
		self.presenter.model.metainfo = metainfo

	#---OBJECT

	def delete_object(self, obj):
		parent = obj.parent
		parent.childs.remove(obj)

	def insert_object(self, obj, parent, index=0):
		parent.childs.insert(index, obj)
		obj.parent = parent

	def append_object(self, obj, parent):
		parent.childs.append(obj)
		obj.parent = parent

	def append_objects(self, objs, parent):
		parent.childs += objs
		for obj in objs:
			obj.parent = parent

	#---PAGES

	def get_pages_obj(self):
		return self.model.childs[0]

	def get_pages(self):
		return self.get_pages_obj().childs

	def get_page(self, page_num=0):
		return self.get_pages_obj().childs[page_num]

	def delete_pages(self):
		pages = self.get_pages_obj()
		pages.childs = []
		pages.page_counter = 0

	def get_desktop_bg(self):
		pages = self.get_pages_obj()
		return deepcopy(pages.desktop_bg)

	def set_desktop_bg(self, color):
		pages = self.get_pages_obj()
		pages.desktop_bg = color

	def get_page_fill(self):
		pages = self.get_pages_obj()
		return deepcopy(pages.page_fill)

	def set_page_fill(self, page_fill):
		pages = self.get_pages_obj()
		pages.page_fill = page_fill

	def get_page_border(self):
		return self.get_pages_obj().page_border

	def get_default_page_format(self):
		pages = self.get_pages_obj()
		return deepcopy(pages.page_format)

	def set_default_page_size(self, width, height):
		parent = self.get_pages_obj()
		fmt = _('Custom size')
		size = (width, height)
		orient = uc2const.PORTRAIT
		if width > height:orient = uc2const.LANDSCAPE
		parent.page_format = [fmt, size, orient]

	def set_default_page_format(self, page_format):
		parent = self.get_pages_obj()
		parent.page_format = page_format

	def set_page_format(self, page, page_format):
		page.page_format = page_format

	def add_page(self, page_format=[]):
		parent = self.get_pages_obj()
		if page_format:
			page = sk2_model.Page(self.config)
			page.page_format = deepcopy(page_format)
		else:
			page = sk2_model.Page(self.config, parent)
		parent.childs.append(page)
		parent.page_counter += 1
		page.name = _('Page') + ' %i' % (parent.page_counter)
		return page

	def insert_page(self, index=0, page_format=[]):
		parent = self.get_pages_obj()
		if page_format:
			page = sk2_model.Page(self.config)
			page.page_format = deepcopy(page_format)
		else:
			page = sk2_model.Page(self.config, parent)

		if index < len(parent.childs):
			parent.childs.insert(index, page)
		else:
			parent.childs.append(page)

		parent.page_counter += 1
		page.name = _('Page') + ' %i' % (parent.page_counter)
		return page

	def delete_page(self, index=0):
		parent = self.get_pages_obj()
		pages = parent.childs
		if index < len(pages):
			pages.remove(pages[index])

	#---LAYERS

	def add_layer(self, page, layer_name=''):
		if not layer_name:
			layer_name = _('Layer') + ' %i' % (page.layer_counter + 1)
		layer = sk2_model.Layer(self.config, page, layer_name)
		page.childs.append(layer)
		page.layer_counter += 1
		return layer

	def insert_layer(self, page, layer_name='', index=0):
		if not layer_name:
			layer_name = _('Layer') + ' %i' % (page.layer_counter + 1)
		layer = sk2_model.Layer(self.config, page)
		layer.name = "" + layer_name
		if index < len(page.childs):
			page.childs.insert(index, layer)
		else:
			page.childs.append(layer)

		page.layer_counter += 1
		return layer

	def get_layer(self, page, layer_num=0):
		return page.childs[layer_num]

	def get_layers(self, page):
		return [] + page.childs

	def is_layer_visible(self, layer):
		if layer.properties[0]: return True
		return False

	def get_visible_layers(self, page, special=False):
		layers = []
		layers += self.get_desktop_layers() + page.childs
		layers += self.get_master_layers()
		if special:
			layers += [self.get_grid_layer(), self.get_guide_layer()]
		ret = []
		for item in layers:
			if self.is_layer_visible(item):
				ret.append(item)
		return ret

	def get_layer_color(self, layer):
		return deepcopy(layer.style[1][2])

	def set_layer_color(self, layer, color):
		layer.style[1][2] = deepcopy(color)
		layer.color = color[1] + [color[2], ]

	def get_layer_rgba_color(self, layer):
		return [] + layer.color

	def set_layer_rgba_color(self, layer, color):
		layer.color = deepcopy(color)
		layer.style[1][2] = [uc2const.COLOR_RGB, color[:-1], color[-1], '', '']

	def get_layer_properties(self, layer):
		return [] + layer.properties

	def set_layer_properties(self, layer, props):
		layer.properties = [] + props

	def get_desktop_layers(self):
		return self.model.childs[1].childs

	def get_master_layers(self):
		return self.model.childs[2].childs

	#---GRID

	def get_grid_layer(self):
		return self.model.childs[3]

	def get_grid_color(self):
		return self.get_layer_color(self.get_grid_layer())

	def get_grid_rgba_color(self):
		return self.get_layer_rgba_color(self.get_grid_layer())

	def set_grid_rgba_color(self, color):
		self.set_layer_rgba_color(self.get_grid_layer(), color)

	def set_grid_color(self, color):
		self.set_layer_color(self.get_grid_layer(), color)

	def get_grid_values(self):
		return [] + self.get_grid_layer().grid

	def set_grid_values(self, vals):
		grid = self.get_grid_layer()
		grid.grid = [] + vals

	def get_grid_properties(self):
		return self.get_layer_properties(self.get_grid_layer())

	def is_grid_visible(self):
		grid = self.get_grid_layer()
		if grid.properties[0]: return True
		return False

	def set_grid_properties(self, props):
		self.set_layer_properties(self.get_grid_layer(), props)

	#---GUIDE LAYER

	def get_guide_layer(self):
		return self.model.childs[4]

	#---RECTANGLE

	def set_rect_corners(self, obj, corners):
		obj.corners = corners
		obj.update()

	def set_rect(self, obj, rect):
		obj.set_rect(rect)
		obj.update()

	#---POLYGON

	def set_polygon_corners_num(self, obj, num):
		obj.corners_num = num
		obj.update()

	def set_polygon_properties(self, obj, angle1, angle2, coef1, coef2):
		obj.angle1 = angle1
		obj.angle2 = angle2
		obj.coef1 = coef1
		obj.coef2 = coef2
		obj.update()

	#---CIRCLE

	def set_circle_properties(self, obj, circle_type, angle1, angle2):
		obj.circle_type = circle_type
		obj.angle1 = angle1
		obj.angle2 = angle2
		obj.update()
