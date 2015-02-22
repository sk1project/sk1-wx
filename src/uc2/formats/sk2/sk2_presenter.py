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

import os

from uc2 import uc2const
from uc2.formats.generic import TextModelPresenter
from uc2.formats.sk2.sk2_config import SK2_Config
from uc2.formats.sk2.sk2_methods import create_new_doc, SK2_Methods
from uc2.formats.sk2.sk2_filters import SK2_Loader, SK2_Saver
from uc2.formats.sk2.sk2_cms import SK2_ColorManager

class SK2_Presenter(TextModelPresenter):

	cid = uc2const.SK1

	config = None
	doc_file = ''
	resources = None
	cms = None

	def __init__(self, appdata, cnf={}, filepath=None):
		self.config = SK2_Config()
		config_file = os.path.join(appdata.app_config_dir, 'sk2_config.xml')
		self.config.load(config_file)
		self.config.update(cnf)
		self.appdata = appdata
		self.loader = SK2_Loader()
		self.saver = SK2_Saver()
		self.methods = SK2_Methods(self)
		self.resources = {}
		if filepath is None:
			self.new()
		else:
			self.load(filepath)

	def new(self):
		self.model = create_new_doc(self.config)
		self.update()

#	def traslate_from_pdxf(self, pdxf_doc):
#		translator = PDXF_to_SK1_Translator()
#		model = pdxf_doc.model
#		objs = [] + model.childs[0].childs[0].childs + model.childs[1].childs
#		translator.translate(objs, self)
#
#	def traslate_to_pdxf(self, pdxf_doc):
#		translator = SK1_to_PDXF_Translator()
#		translator.translate(self, pdxf_doc)

	def update(self):
		TextModelPresenter.update(self)
		if not self.model is None:
			self.methods.update()
