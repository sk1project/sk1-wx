# -*- coding: utf-8 -*-
#
#  Copyright (C) 2009-2019 by Maxim S. Barabash
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
from uc2.formats.dst import dst_model
from uc2.formats.dst.dst_config import DST_Config
from uc2.formats.dst.dst_filters import DST_Loader, DST_Saver
from uc2.formats.dst.dst_to_sk2 import DST_to_SK2_Translator
from uc2.formats.dst.dst_from_sk2 import SK2_to_DST_Translator


class DstPresenter(BinaryModelPresenter):
    cid = uc2const.DST
    palette = None

    def __init__(self, appdata, cnf=None):
        self.config = DST_Config()
        # config_file = os.path.join(appdata.app_config_dir, self.config.filename)
        # self.config.load(config_file)
        self.config.update(cnf or {})
        self.appdata = appdata
        self.loader = DST_Loader()
        self.saver = DST_Saver()
        self.new()

    def new(self):
        self.model = dst_model.DstDocument()
        self.model.childs = []
        # self.model.childs = [dst_model.DstHeader()]

    def translate_from_sk2(self, sk2_doc):
        translator = SK2_to_DST_Translator()
        translator.translate(sk2_doc, self)

    def translate_to_sk2(self, sk2_doc):
        translator = DST_to_SK2_Translator()
        translator.translate(self, sk2_doc)
