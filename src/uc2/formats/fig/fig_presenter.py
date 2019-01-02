# -*- coding: utf-8 -*-
#
#  Copyright (C) 2018 by Maxim S. Barabash
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
from uc2.formats.fig.fig_config import FIGConfig
from uc2.formats.fig.fig_methods import FIGMethods, create_new_doc
from uc2.formats.fig.fig_translators import SK2_to_FIG_Translator
from uc2.formats.fig.fig_translators import FIG_to_SK2_Translator
from uc2.formats.fig.fig_filters import FIGLoader, FIGSaver


class FIG_Presenter(TextModelPresenter):
    cid = uc2const.FIG

    config = None
    doc_file = ''
    resources = None
    cms = None

    def __init__(self, appdata, cnf=None, filepath=None):
        cnf = cnf or {}
        self.config = FIGConfig()
        config_file = os.path.join(appdata.app_config_dir, self.config.filename)
        self.config.load(config_file)
        self.config.update(cnf)
        self.appdata = appdata
        self.cms = self.appdata.app.default_cms
        self.loader = FIGLoader()
        self.saver = FIGSaver()
        self.methods = FIGMethods(self)
        self.resources = {}
        if filepath is None:
            self.new()
        else:
            self.load(filepath)

    def new(self):
        self.model = create_new_doc(self.config)
        self.update()

    def update(self, action=False):
        TextModelPresenter.update(self, action)
        self.methods.update()

    def translate_from_sk2(self, sk2_doc):
        translator = SK2_to_FIG_Translator()
        translator.translate(sk2_doc, self)

    def translate_to_sk2(self, sk2_doc):
        translator = FIG_to_SK2_Translator()
        translator.translate(self, sk2_doc)
