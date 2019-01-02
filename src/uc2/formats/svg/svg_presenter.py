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
from uc2.formats.generic import TaggedModelPresenter
from uc2.formats.svg.svg_config import SVG_Config
from uc2.formats.svg.svg_methods import SVG_Methods, create_new_svg
from uc2.formats.svg.svg_translators import SK2_to_SVG_Translator
from uc2.formats.svg.svg_translators import SVG_to_SK2_Translator
from uc2.formats.xml_.xml_filters import Advanced_XML_Loader, Advanced_XML_Saver


class SVG_Presenter(TaggedModelPresenter):
    cid = uc2const.SVG

    config = None
    doc_file = ''
    resources = None
    cms = None

    def __init__(self, appdata, cnf=None, filepath=None):
        cnf = cnf or {}
        self.config = SVG_Config()
        config_file = os.path.join(appdata.app_config_dir, self.config.filename)
        self.config.load(config_file)
        self.config.update(cnf)
        self.appdata = appdata
        self.cms = self.appdata.app.default_cms
        self.loader = Advanced_XML_Loader()
        self.saver = Advanced_XML_Saver()
        self.methods = SVG_Methods(self)
        if filepath is None:
            self.new()
        else:
            self.load(filepath)

    def new(self):
        self.model = create_new_svg(self.config)
        self.update()

    def update(self, action=False):
        TaggedModelPresenter.update(self, action)
        self.methods.update()

    def translate_from_sk2(self, sk2_doc):
        translator = SK2_to_SVG_Translator()
        translator.translate(sk2_doc, self)

    def translate_to_sk2(self, sk2_doc):
        translator = SVG_to_SK2_Translator()
        translator.translate(self, sk2_doc)
