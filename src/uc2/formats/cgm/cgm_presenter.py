# -*- coding: utf-8 -*-
#
#  Copyright (C) 2017-2019 by Igor E. Novikov
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
from uc2.formats.cgm import cgm_model, cgm_filters, cgm_to_sk2, cgm_from_sk2
from uc2.formats.cgm.cgm_config import CGM_Config


class CGM_Presenter(BinaryModelPresenter):
    cid = uc2const.CGM

    config = None
    doc_file = ''
    model = None

    def __init__(self, appdata, cnf=None):
        cnf = cnf or {}
        self.config = CGM_Config()
        config_file = os.path.join(appdata.app_config_dir, 'cgm_config.xml')
        self.config.load(config_file)
        self.config.update(cnf)
        self.appdata = appdata
        self.loader = cgm_filters.CgmLoader()
        self.saver = cgm_filters.CgmSaver()
        self.new()

    def new(self):
        self.model = cgm_model.get_empty_cgm()

    def translate_from_sk2(self, sk2_doc):
        cgm_from_sk2.SK2_to_CGM_Translator().translate(sk2_doc, self)

    def translate_to_sk2(self, sk2_doc):
        cgm_to_sk2.CGM_to_SK2_Translator().translate(self, sk2_doc)
