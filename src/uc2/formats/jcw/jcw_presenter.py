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
from uc2.formats.generic import BinaryModelPresenter
from uc2.formats.jcw.jcw_config import JCW_Config
from uc2.formats.jcw.jcw_model import JCW_Palette
from uc2.formats.jcw.jcw_filters import JCW_Loader, JCW_Saver

class JCW_Presenter(BinaryModelPresenter):

	cid = uc2const.JCW

	config = None
	doc_file = ''
	model = None

	def __init__(self, appdata, cnf={}):
		self.config = JCW_Config()
		config_file = os.path.join(appdata.app_config_dir, self.config.filename)
		self.config.load(config_file)
		self.config.update(cnf)
		self.appdata = appdata
		self.loader = JCW_Loader()
		self.saver = JCW_Saver()
		self.new()

	def new(self):
		self.model = JCW_Palette()

	def convert_from_skp(self, skp_doc):pass

	def convert_to_skp(self, skp_doc):
		skp_model = skp_doc.model
		if self.model.name:
			skp_model.name = '' + self.model.name
		else:
			skp_model.name = '' + self.model.resolve_name
		skp_model.source = '' + self.config.source
		if self.doc_file:
			filename = os.path.basename(self.doc_file)
			if skp_model.comments:skp_model.comments += 'n'
			skp_model.comments += 'Converted from %s' % filename
		for item in self.model.childs:
			clr = item.get_color()
			if clr: skp_model.colors.append(clr)
