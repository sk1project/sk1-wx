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
from uc2.formats.generic import TextModelPresenter
from uc2.formats.gpl.gpl_config import GPL_Config
from uc2.formats.gpl.gpl_filters import GPL_Loader, GPL_Saver
from uc2.formats.gpl.gpl_model import GPL_Palette
from uc2.uc2const import COLOR_RGB

def create_new_palette(config):pass

class GPL_Presenter(TextModelPresenter):

	cid = uc2const.GPL

	config = None
	doc_file = ''
	resources = None
	cms = None

	def __init__(self, appdata, cnf={}, filepath=None):
		self.config = GPL_Config()
		config_file = os.path.join(appdata.app_config_dir, 'gpl_config.xml')
		self.config.load(config_file)
		self.config.update(cnf)
		self.appdata = appdata
		self.cms = self.appdata.app.default_cms
		self.loader = GPL_Loader()
		self.saver = GPL_Saver()
		if filepath is None:
			self.new()
		else:
			self.load(filepath)

	def new(self):
		self.model = GPL_Palette()
		self.update()

	def update(self):pass

	def convert_from_skp(self, skp_doc):
		skp_model = skp_doc.model
		self.model.name = '' + skp_model.name
		self.model.columns = skp_model.columns
		self.model.comments = '' + skp_model.comments
		for item in skp_model.colors:
			r, g, b = self.cms.get_rgb_color255(item)
			self.model.colors.append([r, g, b, '' + item[3]])

	def convert_to_skp(self, skp_doc):
		skp_model = skp_doc.model
		skp_model.name = '' + self.model.name
		skp_model.columns = self.model.columns
		skp_model.source = 'GIMP'
		skp_model.comments = '' + self.model.comments
		for item in self.model.colors:
			r, g, b, name = item
			r, g, b = cms.val_255_to_dec((r, g, b))
			skp_model.colors.append([COLOR_RGB, [r, g, b], 1.0, name])


