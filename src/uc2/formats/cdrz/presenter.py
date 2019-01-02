# -*- coding: utf-8 -*-
#
#  Copyright (C) 2012 by Igor E. Novikov
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os

from uc2 import uc2const
from uc2.formats.generic import BinaryModelPresenter
from uc2.formats.cdrz.cdrz_config import CDRZ_Config
from uc2.formats.riff import model

from uc2.formats.cdrz.cdrz_filters import CDRZ_Loader, CDRZ_Saver


class CDRZ_Presenter(BinaryModelPresenter):
    cid = uc2const.CDRZ

    config = None
    doc_file = ''
    model = None
    version = 'CDRF'

    def __init__(self, appdata, cnf={}):
        self.config = CDRZ_Config()
        config_file = os.path.join(appdata.app_config_dir, 'cdr_config.xml')
        self.config.load(config_file)
        self.config.update(cnf)
        self.appdata = appdata
        self.doc_id = id(self)
        self.loader = CDRZ_Loader()
        self.saver = CDRZ_Saver()
        self.create_cache_structure()
        self.new()

    def new(self):
        self.model = model.RiffRootList()
        self.model.childs = []

    def load(self, path):
        BinaryModelPresenter.load(self, path)

    def create_cache_structure(self):
        doc_cache_dir = os.path.join(self.appdata.app_config_dir, 'docs_cache')
        self.doc_dir = os.path.join(doc_cache_dir, 'doc_' + self.doc_id)
        os.makedirs(self.doc_dir)

    def traslate_from_pdxf(self, pdxf_doc):
        pass

    def traslate_to_pdxf(self, pdxf_doc):
        pass
