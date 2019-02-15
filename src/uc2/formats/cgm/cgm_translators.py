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

from uc2.formats.cgm import cgm_const


class CGM_to_SK2_Translator(object):
    sk2_doc = None
    sk2_mtds = None
    page = None
    layer = None

    def translate(self, cgm_doc, sk2_doc):
        self.sk2_doc = sk2_doc
        self.sk2_mtds = sk2_doc.methods
        self.page = self.sk2_mtds.get_page()
        self.layer = self.sk2_mtds.get_layer(self.page)

        for element in cgm_doc.childs:
            if element.element_id == cgm_const.END_METAFILE:
                break
            sig = cgm_const.CGM_ID.get(
                element.element_id, '').replace(' ', '_').lower()
            if sig:
                mtd = getattr(self, '_' + sig, None)
                if mtd:
                    mtd(element)

        self.sk2_doc = None
        self.sk2_mtds = None
        self.page = None
        self.layer = None

    def _rectangle(self, element):
        pass

    def _circle(self, element):
        pass

    def _ellipse(self, element):
        pass

    def _line(self, element):
        pass

    def _polyline(self, element):
        pass

    def _polygon(self, element):
        pass


class SK2_to_CGM_Translator(object):
    def translate(self, sk2_doc, cgm_doc): pass
