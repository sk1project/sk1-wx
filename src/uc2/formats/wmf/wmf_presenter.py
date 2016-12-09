# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2016 by Igor E. Novikov
#
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
#
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
#
# 	You should have received a copy of the GNU General Public License
# 	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os

from uc2 import _, uc2const, events
from uc2.formats.generic import BinaryModelPresenter
from uc2.formats.wmf.wmf_config import WMF_Config
from uc2.formats.wmf import wmflib, wmf_model, wmf_filters, wmf_translators

class WMF_Presenter(BinaryModelPresenter):

	cid = uc2const.WMF

	config = None
	doc_file = ''
	model = None

	def __init__(self, appdata, cnf={}):
		self.config = WMF_Config()
		config_file = os.path.join(appdata.app_config_dir, 'wmf_config.xml')
		self.config.load(config_file)
		self.config.update(cnf)
		self.appdata = appdata
		self.loader = wmf_filters.WMF_Loader()
		self.saver = wmf_filters.WMF_Saver()
		self.new()

	def new(self):
		self.model = wmf_model.META_Placeable_Record()
		header = wmf_model.META_Header_Record()
		self.model.childs.append(header)
		header.childs.append(wmflib.get_eof_rec())

	def translate_from_sk2(self, sk2_doc):
		translator = wmf_translators.SK2_to_WMF_Translator()
		translator.translate(sk2_doc, self)

	def translate_to_sk2(self, sk2_doc):
		translator = wmf_translators.WMF_to_SK2_Translator()
		translator.translate(self, sk2_doc)
