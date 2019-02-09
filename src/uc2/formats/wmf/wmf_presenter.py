# -*- coding: utf-8 -*-
#
#  Copyright (C) 2016 by Igor E. Novikov
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
from uc2.formats.wmf import wmf_model, wmf_filters, wmf_translators
from uc2.formats.wmf.wmf_config import WMF_Config


class WMF_Presenter(BinaryModelPresenter):
    cid = uc2const.WMF

    config = None
    doc_file = ''
    model = None

    def __init__(self, appdata, cnf=None):
        cnf = cnf or {}
        self.config = WMF_Config()
        config_file = os.path.join(appdata.app_config_dir, 'wmf_config.xml')
        self.config.load(config_file)
        self.config.update(cnf)
        self.appdata = appdata
        self.loader = wmf_filters.WMF_Loader()
        self.saver = wmf_filters.WMF_Saver()
        self.new()

    def new(self):
        self.model = wmf_model.get_empty_wmf()

    def translate_from_sk2(self, sk2_doc):
        translator = wmf_translators.SK2_to_WMF_Translator()
        translator.translate(sk2_doc, self)

    def translate_to_sk2(self, sk2_doc):
        translator = wmf_translators.WMF_to_SK2_Translator()
        translator.translate(self, sk2_doc)
