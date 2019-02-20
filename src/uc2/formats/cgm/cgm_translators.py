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

import copy

from uc2 import utils
from uc2.formats.cgm import cgm_const


class CGM_to_SK2_Translator(object):
    sk2_doc = None
    sk2_mtds = None
    page = None
    layer = None
    cgm = None

    def translate(self, cgm_doc, sk2_doc):
        self.sk2_doc = sk2_doc
        self.sk2_model = sk2_doc.model
        self.sk2_mtds = sk2_doc.methods
        self.page = self.sk2_mtds.get_page()
        self.layer = self.sk2_mtds.get_layer(self.page)

        self.cgm = copy.deepcopy(cgm_const.CGM_INIT)

        for element in cgm_doc.childs:
            if element.element_id == cgm_const.END_METAFILE:
                break
            signature = cgm_const.CGM_ID.get(
                element.element_id, '').replace(' ', '_').lower()
            if signature:
                mtd = getattr(self, '_' + signature, None)
                if mtd:
                    mtd(element)

        self.sk2_doc = None
        self.sk2_mtds = None
        self.page = None
        self.layer = None

    def extract_title(self, params):
        """Extracts first byte size defined title.

        :param element: CgmElement params
        :return: str
        """
        if params:
            sz = utils.byte2py_int(params[0])
            return params[1:1 + sz]
        return ''

    # Metafile description
    def _begin_metafile(self, element):
        self.sk2_model.metainfo[3] = self.extract_title(element.params)

    def _metafile_description(self, element):
        if self.sk2_model.metainfo[3]:
            self.sk2_model.metainfo[3] += '\n\n'
        self.sk2_model.metainfo[3] += self.extract_title(element.params)

    def _vdc_type(self, element):
        if element.params:
            self.cgm['vdc.type'] = utils.uint16_be(element.params[:2])
        if self.cgm['vdc.type'] == cgm_const.VDC_TYPE_INT:
            self.cgm['vdc.size'] = self.cgm['vdc.intsize']
            self.cgm['vdc.prec'] = self.cgm['vdc.intprec']
            self.cgm['vdc.extend'] = self.cgm['vdc.intextend']
        else:
            self.cgm['vdc.size'] = self.cgm['vdc.realsize']
            self.cgm['vdc.prec'] = self.cgm['vdc.realprec']
            self.cgm['vdc.extend'] = self.cgm['vdc.realextend']

    def _application_data(self, element):
        if self.sk2_model.metainfo[3]:
            self.sk2_model.metainfo[3] += '\n\n'
        self.sk2_model.metainfo[3] += self.extract_title(element.params[2:])

    # Structural elements
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
