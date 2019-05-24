# -*- coding: utf-8 -*-
#
#  Copyright (C) 2019 by Maxim S. Barabash
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
from uc2.formats.xar import xar_filters, xar_translators
from uc2.formats.xar import xar_method
from uc2.formats.xar.xar_config import XAR_Config


class XAR_Presenter(BinaryModelPresenter):
    cid = uc2const.XAR

    config = None
    doc_file = ''
    model = None

    def __init__(self, appdata, cnf=None):
        cnf = cnf or {}
        self.config = XAR_Config()
        config_file = os.path.join(appdata.app_config_dir, 'xar_config.xml')
        self.config.load(config_file)
        self.config.update(cnf)
        self.appdata = appdata
        self.loader = xar_filters.XARLoader()
        self.saver = xar_filters.XARSaver()
        self.methods = xar_method.XARMethods(self)
        self.new()

    def new(self):
        self.model = xar_method.create_new_doc(self.config)

    def translate_from_sk2(self, sk2_doc):
        translator = xar_translators.SK2_to_XAR_Translator()
        translator.translate(sk2_doc, self)

    def translate_to_sk2(self, sk2_doc):
        translator = xar_translators.XAR_to_SK2_Translator()
        translator.translate(self, sk2_doc)
