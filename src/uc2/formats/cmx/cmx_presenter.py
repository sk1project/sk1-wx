# -*- coding: utf-8 -*-
#
#  Copyright (C) 2019 by Igor E. Novikov
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
from uc2.formats.cmx import cmx_model, cmx_filters, cmx_to_sk2, cmx_from_sk2
from uc2.formats.cmx.cmx_config import CMX_Config


class CMX_Presenter(BinaryModelPresenter):
    cid = uc2const.CMX

    config = None
    doc_file = ''
    model = None

    def __init__(self, appdata, cnf=None):
        cnf = cnf or {}
        self.config = CMX_Config()
        config_file = os.path.join(appdata.app_config_dir, 'cmx_config.xml')
        self.config.load(config_file)
        self.config.update(cnf)
        self.appdata = appdata
        self.loader = cmx_filters.CmxLoader()
        self.saver = cmx_filters.CmxSaver()
        self.new()

    def new(self):
        self.model = cmx_model.CmxRoot(self.config)

    def translate_from_sk2(self, sk2_doc):
        cmx_from_sk2.SK2_to_CMX_Translator().translate(sk2_doc, self)

    def translate_to_sk2(self, sk2_doc):
        cmx_to_sk2.CMX_to_SK2_Translator().translate(self, sk2_doc)
