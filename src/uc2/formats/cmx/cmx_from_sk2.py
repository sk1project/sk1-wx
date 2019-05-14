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

import logging

from uc2.formats.cmx import cmx_model, cmx_const

LOG = logging.getLogger(__name__)


class SK2_to_CMX_Translator(object):
    cmx_doc = None
    cmx_model = None
    sk2_doc = None
    sk2_model = None
    sk2_mtds = None
    cmx_cfg = None

    def translate(self, sk2_doc, cmx_doc):
        self.cmx_doc = cmx_doc
        self.cmx_model = cmx_doc.model
        self.cmx_cfg = cmx_doc.config
        self.sk2_doc = sk2_doc
        self.sk2_model = sk2_doc.model
        self.sk2_mtds = sk2_doc.methods

        self.make_template()
        self.translate_doc()
        self.index_model()
        self.add_info()
        self.cmx_doc.update()

        self.cmx_doc = None
        self.cmx_model = None
        self.cmx_cfg = None
        self.sk2_doc = None
        self.sk2_model = None
        self.sk2_mtds = None

    def make_template(self):
        self.cmx_model.add(cmx_model.CmxCont(self.cmx_cfg))
        self.cmx_model.add(cmx_model.CmxCcmm(self.cmx_cfg))

    def translate_doc(self):
        pass

    def index_model(self):
        pass

    def _default_notes(self):
        appdata = self.sk2_doc.appdata
        name = "Created by %s" % appdata.app_name
        ver = "%s%s" % (appdata.version, appdata.revision)
        link = "(https://%s/)" % appdata.app_domain
        return "%s %s %s" % (name, ver, link)

    def add_info(self):
        pass
        info = cmx_model.CmxList(self.cmx_cfg, name=cmx_const.INFO_ID)
        self.cmx_model.add(info)
        metainfo = self.sk2_model.metainfo
        keys = metainfo[2] or ''
        notes = metainfo[3] or self._default_notes()
        info.add(cmx_model.CmxInfoElement(
            self.cmx_cfg, identifier=cmx_const.IKEY_ID, text=keys))
        info.add(cmx_model.CmxInfoElement(
            self.cmx_cfg, identifier=cmx_const.ICMT_ID, text=notes))