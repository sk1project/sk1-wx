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

from uc2.formats.xml_.xml_model import XMLObject
from uc2.utils import generate_guid
from uc2.uc2const import COLOR_RGB, COLOR_CMYK, COLOR_SPOT, COLOR_GRAY
from uc2.cms import verbose_color

CS_MATCH = {
	COLOR_RGB:'RGB',
	COLOR_CMYK:'CMYK',
	COLOR_GRAY:'Gray',
	}

def create_new_palette(config):
	model = XMLObject('palette')
	model.attrs['name'] = '' + config.default_name
	model.attrs['guid'] = generate_guid()
	colors = XMLObject('colors')
	model.childs.append(colors)
	page = XMLObject('page')
	colors.childs.append(page)
	return model

class CorelPalette_Methods:

	presenter = None

	def __init__(self, presenter):
		self.presenter = presenter

	def update(self):
		self.model = self.presenter.model
		self.config = self.presenter.config
		self.cms = self.presenter.cms

	def get_colors_obj(self):
		for child in self.model.childs:
			if child.tag == 'colors':
				return child

	def get_page_obj(self):
		colors = self.get_colors_obj()
		for child in colors.childs:
			if child.tag == 'page':
				return child

	def set_palette_name(self, name):
		self.model.attrs['name'] = name

	def set_palette_comments(self, comments):
		self.model.comments = comments

	def get_tints(self, color_vals):
		tints = ''
		for item in color_vals:
			tints += str(round(item, 6)) + ','
		return tints[:-1]

	def get_color_name(self, color):
		if not len(color) < 4 and color[3]:
			return color[3]
		else:
			return verbose_color(color)

	def add_color(self, color):
		if color[0] == COLOR_SPOT:
			self.add_spot_color(color)
			return
		if not color[0] in [COLOR_RGB, COLOR_CMYK, COLOR_GRAY]:
			color = self.cms.get_rgb_color(color)
		page = self.get_page_obj()
		clr = XMLObject('color')
		clr.attrs['cs'] = CS_MATCH[color[0]].encode(self.config.encoding)
		name = self.get_color_name(color)
		clr.attrs['name'] = name.encode(self.config.encoding)
		clr.attrs['tints'] = self.get_tints(color[1])
		page.childs.append(clr)

	def add_spot_color(self, color):pass
