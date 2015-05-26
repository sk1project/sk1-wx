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

from uc2.formats.xml_.xml_model import XMLObject
from uc2.utils import generate_guid
from uc2.uc2const import COLOR_RGB, COLOR_CMYK, COLOR_SPOT, COLOR_GRAY, COLOR_LAB
from uc2.cms import verbose_color

CS_MATCH = {
	COLOR_RGB:'RGB',
	COLOR_CMYK:'CMYK',
	COLOR_GRAY:'Gray',
	COLOR_LAB:'LAB',
	'Gray':COLOR_GRAY,
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

		self.localizations = {}
		for resource in self.get_localization().childs:
			text = ''
			for item in resource.childs:
				if item.tag == 'EN':
					text += item.content
					break
			self.localizations[resource.attrs['id']] = text

		self.colorspaces = {}
		for cs in self.get_colorspaces().childs:
			vals = [[], []]
			if len(cs.childs) == 1 and cs.childs[0].attrs['cs'] == 'LAB':
				encoding = self.config.encoding
				vals = self.get_color_vals(cs.childs[0].attrs['tints'])
				name = ('' + cs.attrs['name']).decode(encoding)
				palette_name = self.get_palette_name().decode(encoding)
				vals = [COLOR_LAB, vals, 1.0, name, palette_name]
			else:
				for item in cs.childs:
					if item.attrs['cs'] == 'RGB':
						vals[0] = self.get_color_vals(item.attrs['tints'])
					if item.attrs['cs'] == 'CMYK':
						vals[1] = self.get_color_vals(item.attrs['tints'])
			if vals[0] or vals[1]:
				self.colorspaces[cs.attrs['name']] = vals

	def clear_model(self):
		colorspaces = self.get_colorspaces()
		localization = self.get_localization()
		if not len(colorspaces.childs):
			self.model.childs.remove(colorspaces)
		if not len(localization.childs):
			self.model.childs.remove(localization)

	def get_colors_obj(self):
		for child in self.model.childs:
			if child.tag == 'colors':
				return child

	def get_page_obj(self, index=0):
		colors = self.get_colors_obj()
		return colors.childs[index]

	def get_colorspaces(self):
		colorspaces = None
		for child in self.model.childs:
			if child.tag == 'colorspaces':
				colorspaces = child
		if not colorspaces:
			colorspaces = XMLObject('colorspaces')
			self.model.childs = [colorspaces, ] + self.model.childs
		return colorspaces

	def get_localization(self):
		localization = None
		for child in self.model.childs:
			if child.tag == 'localization':
				localization = child
		if not localization:
			localization = XMLObject('localization')
			self.model.childs += [localization, ]
		return localization

	def set_palette_name(self, name):
		self.model.attrs['name'] = name

	def get_palette_name(self):
		if 'name' in self.model.attrs.keys():
			return self.model.attrs['name']
		elif 'resid' in self.model.attrs.keys() \
			and self.model.attrs['resid'] in self.localizations.keys():
			return '' + self.localizations[self.model.attrs['resid']]
		else:
			return '' + self.model.config.default_name

	def set_palette_comments(self, comments):
		self.model.comments = comments

	def get_tints(self, color_vals):
		tints = ''
		for item in color_vals:
			tints += str(round(item, 6)) + ','
		return tints[:-1]

	def get_color_vals(self, tints):
		ret = []
		for item in tints.split(','):
			ret.append(float(item))
		return ret

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

	def add_spot_color(self, color):
		page = self.get_page_obj()
		clr = XMLObject('color')
		name = color[3].encode(self.config.encoding)
		clr.attrs['cs'] = '' + name
		clr.attrs['name'] = '' + name
		clr.attrs['tints'] = '1'
		page.childs.append(clr)

		colorspaces = self.get_colorspaces()
		fixed_id = len(colorspaces.childs) + 1
		cs = XMLObject('color')
		cs.attrs['fixedID'] = str(fixed_id)
		cs.attrs['version'] = '1500'
		cs.attrs['name'] = '' + name
		colorspaces.childs.append(cs)

		if color[1][1]:
			clr = XMLObject('color')
			clr.attrs['cs'] = 'CMYK'.encode(self.config.encoding)
			clr.attrs['tints'] = self.get_tints(color[1][1])
			cs.childs.append(clr)

		if color[1][0]:
			clr = XMLObject('color')
			clr.attrs['cs'] = 'RGB'.encode(self.config.encoding)
			clr.attrs['tints'] = self.get_tints(color[1][0])
			cs.childs.append(clr)

	def convert_color(self, color):
		if color.attrs['cs'] in CS_MATCH.keys():
			cs = CS_MATCH[color.attrs['cs']]
			vals = self.get_color_vals(color.attrs['tints'])
			name = ''
			if 'name' in color.attrs.keys():
				name = '' + color.attrs['name']
			elif 'resid' in color.attrs.keys():
				name = '' + self.localizations[color.attrs['resid']]
			return [cs, vals, 1.0, name]
		elif color.attrs['cs'] in self.colorspaces.keys():
			cs = COLOR_SPOT
			vals = deepcopy(self.colorspaces[color.attrs['cs']])
			if vals[0] == COLOR_LAB: return vals
			name = ('' + color.attrs['cs']).decode(self.config.encoding)
			palette_name = self.get_palette_name().decode(self.config.encoding)
			return [cs, vals, 1.0, name, palette_name]
		else:
			return None

	def get_colors(self):
		ret = []
		for page in self.get_colors_obj().childs:
			for color in page.childs:
				clr = self.convert_color(color)
				if clr: ret.append(clr)
		return ret
