# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2018 by Igor E. Novikov
#
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
#
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
#
# 	You should have received a copy of the GNU General Public License
# 	along with this program.  If not, see <https://www.gnu.org/licenses/>.

from uc2 import uc2const
from uc2.formats.generic import TextModelPresenter
from uc2.formats.md.md_model import MdLoader, MdModel, MdSaver


class MdPresenter(TextModelPresenter):
    cid = uc2const.MD

    config = None
    doc_file = ''
    model = None

    def __init__(self, appdata, cnf=None):
        cnf = cnf or {}
        self.config = cnf
        self.appdata = appdata
        self.loader = MdLoader()
        self.saver = MdSaver()
        self.new()

    def new(self):
        self.model = MdModel
