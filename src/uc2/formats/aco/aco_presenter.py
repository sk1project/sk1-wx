# -*- coding: utf-8 -*-
#
#  Copyright (C) 2017 by Igor E. Novikov
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
from uc2.formats.aco.aco_config import ACO_Config
from uc2.formats.aco.aco_filters import ACO_Loader, ACO_Saver
from uc2.formats.aco.aco_model import ACO_Palette


class ACO_Presenter(BinaryModelPresenter):
    cid = uc2const.ACO

    config = None
    doc_file = ''
    model = None

    def __init__(self, appdata, cnf=None):
        cnf = cnf or {}
        self.config = ACO_Config()
        config_file = os.path.join(appdata.app_config_dir, self.config.filename)
        self.config.load(config_file)
        self.config.update(cnf)
        self.appdata = appdata
        self.loader = ACO_Loader()
        self.saver = ACO_Saver()
        self.new()

    def new(self):
        self.model = ACO_Palette()

    def convert_from_skp(self, skp_doc):
        self.model.set_color_list(skp_doc.model.colors)

    def convert_to_skp(self, skp_doc):
        skp_model = skp_doc.model
        skp_model.name = 'ACO palette'
        skp_model.source = self.config.source
        skp_model.comments = ''
        skp_model.colors = self.model.get_color_list()
