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

from uc2 import uc2const
from uc2.formats.generic import TextModelPresenter
from uc2.formats.skp.skp_config import SKP_Config
from uc2.formats.skp.skp_filters import SKP_Loader, SKP_Saver

def create_new_palette(config):pass

class SKP_Presenter(TextModelPresenter):

	cid = uc2const.SKP

	config = None
	doc_file = ''
	resources = None
	cms = None

	def __init__(self, appdata, cnf={}, filepath=None):
		self.config = SKP_Config()
		config_file = os.path.join(appdata.app_config_dir, 'skp_config.xml')
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
		self.model = create_new_palette(self.config)
		self.update()

	def update(self):
		TextModelPresenter.update(self)
		if not self.model is None:
			self.methods.update()

