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

import os

from uc2 import uc2const
from uc2.formats.generic import TextModelPresenter
from uc2.formats.plt.plt_config import PLT_Config
from uc2.formats.plt import model
from uc2.formats.plt.plt_filters import PLT_Loader, PLT_Saver
from uc2.formats.plt.plt_translators import SK2_to_PLT_Translator
from uc2.formats.plt.plt_translators import PLT_to_SK2_Translator

class PLT_Presenter(TextModelPresenter):

	cid = uc2const.PLT

	config = None
	doc_file = ''
	model = None

	def __init__(self, appdata, cnf={}):
		self.config = PLT_Config()
		config_file = os.path.join(appdata.app_config_dir, 'plt_config.xml')
		self.config.load(config_file)
		self.config.update(cnf)
		self.appdata = appdata
		self.loader = PLT_Loader()
		self.saver = PLT_Saver()
		self.new()

	def new(self):
		self.model = model.PltHeader()
		childs = []
		childs.append(model.PltStart())
		childs.append(model.PltJobs())
		childs.append(model.PltEnd())
		self.model.childs = childs

	def get_jobs(self):
		return self.model.childs[1].childs

	def traslate_from_pdxf(self, sk2_doc):
		translator = SK2_to_PLT_Translator()
		model = sk2_doc.model
		objs = [] + model.childs[0].childs[0].childs + model.childs[1].childs
		translator.translate(objs, self)

	def traslate_to_sk2(self, sk2_doc):
		translator = PLT_to_SK2_Translator()
		translator.translate(self, sk2_doc)

