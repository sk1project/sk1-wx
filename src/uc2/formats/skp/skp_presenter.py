# -*- coding: utf-8 -*-
#
#	Copyright (C) 2015 by Igor E. Novikov
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

import os

from copy import deepcopy

from uc2 import uc2const
from uc2.formats.generic import TextModelPresenter
from uc2.formats.skp.skp_config import SKP_Config
from uc2.formats.skp.skp_filters import SKP_Loader, SKP_Saver
from uc2.formats.skp.skp_model import SK1Palette
from uc2.formats.sk2 import sk2_model, sk2_const

def create_new_palette(config):pass

class SKP_Presenter(TextModelPresenter):

	cid = uc2const.SKP

	config = None
	doc_file = ''
	resources = None
	cms = None

	def __init__(self, appdata, cnf={}, filepath=None):
		self.config = SKP_Config()
		config_file = os.path.join(appdata.app_config_dir, self.config.filename)
		self.config.load(config_file)
		self.config.update(cnf)
		self.appdata = appdata
		self.cms = self.appdata.app.default_cms
		self.loader = SKP_Loader()
		self.saver = SKP_Saver()
		if filepath is None:
			self.new()
		else:
			self.load(filepath)

	def new(self):
		self.model = SK1Palette()
		self.update()

	def update(self):
		TextModelPresenter.update(self)

	def translate_from_sk2(self, sk2_doc):
		doc_name = sk2_doc.doc_file.split('.')[0]
		if not doc_name: doc_name = 'Untitled'
		self.model.name = doc_name + ' palette'
		self.model.comments = 'The palette is extracted from "'
		self.model.comments += doc_name + '" document'
		self.model.source = 'Custom'
		self._extract_color(sk2_doc.model)

	def _extract_color(self, obj):
		if obj.cid > sk2_model.PRIMITIVE_CLASS:
			fill = obj.style[0]
			if fill and fill[1] == sk2_const.FILL_SOLID:
				if fill[2] not in self.model.colors:
					self.model.colors.append(deepcopy(fill[2]))
		for child in obj.childs:
			self._extract_color(child)

	def translate_to_sk2(self, sk2_doc):
		ncells = len(self.model.colors)
		if not ncells: return
		cellsize = self.config.large_cell
		if ncells > self.config.short_palette_size:
			cellsize = self.config.small_cell
		if self.model.columns < 2:
			columns = int(self.config.palette_width / cellsize)
		else:
			columns = self.model.columns
		rows = 1.0 * ncells / columns
		if rows > int(rows):
			rows = int(rows) + 1
		else:
			rows = int(rows)

		ext = uc2const.FORMAT_EXTENSION[uc2const.SK2][0]
		sk2_doc.doc_file = self.model.name + "." + ext
		sk2_doc.methods.set_doc_origin(sk2_const.DOC_ORIGIN_LU)
		sk2_doc.methods.set_doc_units(uc2const.UNIT_PX)
		page = sk2_doc.methods.get_page()

		orient = uc2const.PORTRAIT
		w = columns * cellsize + 1
		h = rows * cellsize + 1
		if w > h:orient = uc2const.LANDSCAPE
		sk2_doc.methods.set_page_format(page, ['Custom', (w, h), orient])
		sk2_doc.methods.set_default_page_format(['Custom', (w, h), orient])
		grid_layer = sk2_doc.methods.get_gird_layer()
		grid_layer.grid = [0, 0, uc2const.px_to_pt, uc2const.px_to_pt]
		grid_layer.properties = [1, 0, 0]

		layer = sk2_doc.methods.get_layer(page)
		cfg = sk2_doc.config

		x = x_orign = -(w / 2.0) + 0.5 - cellsize
		y = h / 2.0 - 0.5
		stroke = deepcopy(cfg.default_stroke)
		stroke[1] = 1.0
		index = 0

		for row in range(rows):
			y -= cellsize
			x = x_orign
			for column in range(columns):
				x += cellsize
				trafo = [cellsize, 0, 0, cellsize, x, y]
				color = deepcopy(self.model.colors[index])
				fill = [sk2_const.FILL_EVENODD, sk2_const.FILL_SOLID, color]
				style = [fill, deepcopy(stroke), [], []]
				layer.childs.append(sk2_model.Rectangle(cfg, layer,
											trafo=trafo, style=style))
				index += 1
				if index == ncells: break

		sk2_doc.update()



