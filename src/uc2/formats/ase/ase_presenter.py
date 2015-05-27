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
from uc2.formats.generic import BinaryModelPresenter
from uc2.formats.ase.ase_config import ASE_Config
from uc2.formats.ase.ase_model import ASE_Palette
from uc2.formats.ase.ase_filters import ASE_Loader, ASE_Saver

class ASE_Presenter(BinaryModelPresenter):

	cid = uc2const.ASE

	config = None
	doc_file = ''
	model = None

	def __init__(self, appdata, cnf={}):
		self.config = ASE_Config()
		config_file = os.path.join(appdata.app_config_dir, self.config.filename)
		self.config.load(config_file)
		self.config.update(cnf)
		self.appdata = appdata
		self.loader = ASE_Loader()
		self.saver = ASE_Saver()
		self.new()

	def new(self):
		self.model = ASE_Palette()
		self.model.childs = []

	def convert_from_skp(self, skp_doc):
		pass

	def convert_to_skp(self, skp_doc):
		pass
