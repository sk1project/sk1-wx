# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2013 by Igor E. Novikov
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
from uc2.formats.generic import TextModelPresenter
from uc2.formats.sk1.methods import create_new_doc, SK1_Methods
from uc2.formats.sk1.sk1_config import SK1_Config
from uc2.formats.sk1.sk1_filters import SK1Loader, SK1Saver
from uc2.formats.sk1.sk1_translators import SK1_to_SK2_Translator
from uc2.formats.sk1.sk1_translators import SK2_to_SK1_Translator


class SK1Presenter(TextModelPresenter):
    cid = uc2const.SK1

    config = None
    doc_file = ''
    resources = None

    def __init__(self, appdata, cnf=None):
        cnf = cnf or {}
        self.config = SK1_Config()
        config_file = os.path.join(appdata.app_config_dir, 'sk1_config.xml')
        self.config.load(config_file)
        self.config.update(cnf)
        self.appdata = appdata
        self.loader = SK1Loader()
        self.saver = SK1Saver()
        self.methods = SK1_Methods(self)
        self.resources = {}
        self.new()

    def new(self):
        self.model = create_new_doc(self.config)
        self.update()

    def translate_from_sk2(self, sk2_doc):
        translator = SK2_to_SK1_Translator()
        translator.translate(sk2_doc, self)

    def translate_to_sk2(self, sk2_doc):
        translator = SK1_to_SK2_Translator()
        translator.translate(self, sk2_doc)

    def update(self, action=False):
        TextModelPresenter.update(self, action)
        if self.model is not None:
            self.methods.update()
