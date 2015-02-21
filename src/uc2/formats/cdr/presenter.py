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

from uc2 import _, uc2const, events
from uc2.formats.generic import BinaryModelPresenter
from uc2.formats.cdr.cdr_config import CDR_Config
from uc2.formats.riff import model
from uc2.formats.cdr.cdr_filters import CDR_Loader, CDR_Saver
from uc2.formats.cdr.cdr_translators import CDR_to_PDXF_Translator

class CDR_Presenter(BinaryModelPresenter):

	cid = uc2const.CDR

	config = None
	doc_file = ''
	model = None
	version = 'CDRC'

	def __init__(self, appdata, cnf={}):
		self.config = CDR_Config()
		config_file = os.path.join(appdata.app_config_dir, 'cdr_config.xml')
		self.config.load(config_file)
		self.config.update(cnf)
		self.appdata = appdata
		self.loader = CDR_Loader()
		self.saver = CDR_Saver()
		self.new()

	def new(self):
		self.model = model.RiffRootList()
		self.model.childs = []

	def load(self, path):
		BinaryModelPresenter.load(self, path)

	def traslate_from_pdxf(self, pdxf_doc):
		pass

	def traslate_to_pdxf(self, pdxf_doc):
		msg = _('Translation is under process...')
		events.emit(events.FILTER_INFO, msg, 0.95)
		translator = CDR_to_PDXF_Translator()
		translator.translate(self, pdxf_doc)
