# -*- coding: utf-8 -*-
#
#	Copyright (C) 2014 by Igor E. Novikov
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
from uc2.formats.sk1 import model

def create_new_doc(config):
	doc = model.SK1Document(config)
	layout = model.SK1Layout()
	doc.childs.append(layout)
	doc.layout = layout
	pages = model.SK1Pages()
	doc.childs.append(pages)
	doc.pages = pages
	page = model.SK1Page()
	pages.childs.append(page)
	page.childs.append(model.SK1Layer())
	mlayer = model.SK1MasterLayer()
	doc.childs.append(mlayer)
	doc.masterlayer = mlayer
	grid = model.SK1Grid()
	doc.childs.append(grid)
	doc.grid = grid
	glayer = model.SK1GuideLayer()
	doc.childs.append(glayer)
	doc.guidelayer = glayer
	return doc


class SK1_Methods:

	presenter = None

	def __init__(self, presenter):
		self.presenter = presenter

	def update(self):
		self.model = self.presenter.model
		self.config = self.presenter.model.config

	def set_doc_origin(self, origin):
		self.presenter.model.doc_origin = origin

	def set_doc_units(self, units):
		self.presenter.model.doc_units = units

	#--- Generic object methods

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

	#--- Page methods

	def get_pages(self):
		return self.model.pages.childs

	def get_page(self, page_num=0):
		return self.presenter.model.pages.childs[page_num]

	def delete_pages(self):
		self.model.childs[0].childs = []
		self.model.childs[0].page_counter = 0

	#--- Layer methods

	def get_layer(self, page, layer_num=0):
		return page.childs[layer_num]

	def is_layer_visible(self, layer):
		if layer.visible: return True
		return False

	def get_gird_layer(self):
		return self.model.grid

	def get_guide_layer(self):
		return self.model.guidelayer

	def get_master_layer(self):
		return self.model.masterlayer
