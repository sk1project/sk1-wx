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


class CMX_to_SK2_Translator(object):
    sk2_doc = None
    sk2_model = None
    sk2_mtds = None
    cmx_defaults = None

    def translate(self, cmx_doc, sk2_doc):
        self.sk2_doc = sk2_doc
        self.sk2_model = sk2_doc.model
        self.sk2_mtds = sk2_doc.methods