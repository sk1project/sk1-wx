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

from uc2 import uc2const, cms
from uc2.formats.generic import TaggedModelPresenter
from uc2.formats.scribus_pal.scribus_pal_config import ScribusPalette_Config
from uc2.formats.scribus_pal.scribus_pal_filters import ScribusPalette_Loader, \
ScribusPalette_Saver
from uc2.formats.scribus_pal.scribus_pal_model import ScribusPalette, SPColor
from uc2.uc2const import COLOR_RGB, COLOR_CMYK, COLOR_SPOT, COLOR_REG

def create_new_palette(config):pass

class ScribusPalette_Presenter(TaggedModelPresenter):

	cid = uc2const.SCRIBUS_PAL

	config = None
	doc_file = ''
	resources = None
	cms = None

	def __init__(self, appdata, cnf={}, filepath=None):
		self.config = ScribusPalette_Config()
		config_file = os.path.join(appdata.app_config_dir, self.config.filename)
		self.config.load(config_file)
		self.config.update(cnf)
		self.appdata = appdata
		self.cms = self.appdata.app.default_cms
		self.loader = ScribusPalette_Loader()
		self.saver = ScribusPalette_Saver()
		if filepath is None:
			self.new()
		else:
			self.load(filepath)

	def new(self):
		self.model = ScribusPalette()
		self.update()

	def update(self):pass

	def convert_from_skp(self, skp_doc):
		sp = self.model
		skp = skp_doc.model
		sp.Name = skp.name.encode('utf-8')
		if skp.source:
			sp.comments += 'Palette source: ' + skp.source + '\n'
		if skp.comments:
			for item in skp.comments.splitlines():
				sp.comments += item + '\n'
		sp.comments = sp.comments.encode('utf-8')
		for item in skp.colors:
			obj = SPColor()
			if item[0] == COLOR_SPOT:
				obj.Spot = '1'
				if item[1][1]: obj.CMYK = cms.cmyk_to_hexcolor(item[1][1])
				else: obj.RGB = cms.rgb_to_hexcolor(item[1][0])
				obj.NAME = '' + item[3].encode('utf-8')
				if item[3] == COLOR_REG:
					obj.Register = '1'
			elif item[0] == COLOR_CMYK:
				obj.CMYK = cms.cmyk_to_hexcolor(item[1])
				obj.NAME = '' + item[3].encode('utf-8')
			elif item[0] == COLOR_RGB:
				obj.RGB = cms.rgb_to_hexcolor(item[1])
				obj.NAME = '' + item[3].encode('utf-8')
			else:
				clr = self.cms.get_rgb_color(item)
				obj.RGB = cms.rgb_to_hexcolor(clr[1])
				obj.NAME = '' + clr[3].encode('utf-8')
			sp.childs.append(obj)

	def convert_to_skp(self, skp_doc):
		skp = skp_doc.model
		skp.name = self.model.Name.decode('utf-8')
		if not skp.name:
			if self.doc_file:
				name = os.path.basename(self.doc_file)
				skp.name = name.replace('.xml', '').replace('_', ' ')
			else:
				skp.name = self.config.default_name
		if self.doc_file:
			filename = os.path.basename(self.doc_file)
			skp.comments = 'Converted from %s' % filename
		skp.source = '' + self.config.source
		for item in self.model.childs:
			color = None
			if item.Register == '1':
				color = cms.get_registration_black()
			if item.Spot == '1':
				rgb = []
				cmyk = []
				if item.RGB: rgb = cms.hexcolor_to_rgb(item.RGB)
				if item.CMYK: cmyk = cms.hexcolor_to_cmyk(item.CMYK)
				name = item.NAME.decode('utf-8')
				color = [COLOR_SPOT, [rgb, cmyk], 1.0, name]
			elif item.CMYK:
				cmyk = cms.hexcolor_to_cmyk(item.CMYK)
				name = item.NAME.decode('utf-8')
				color = [COLOR_CMYK, cmyk, 1.0, name]
			elif item.RGB:
				rgb = cms.hexcolor_to_rgb(item.RGB)
				name = item.NAME.decode('utf-8')
				color = [COLOR_RGB, rgb, 1.0, name]
			else:
				continue
			skp.colors.append(color)


