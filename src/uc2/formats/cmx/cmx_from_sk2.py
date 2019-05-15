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

from uc2 import libimg
from uc2.formats.cmx import cmx_model, cmx_const
from uc2.formats.sk2.crenderer import CairoRenderer

LOG = logging.getLogger(__name__)


class SK2_to_CMX_Translator(object):
    root = None
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
        self.sk2_model = self.root = sk2_doc.model
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

    def _make_preview(self):
        return libimg.generate_preview(
            self.sk2_doc, CairoRenderer, size=self.cmx_cfg.preview_size,
            transparent=False, img_format='BMP', encoded=False)

    def make_el(self, cmx_id, **kwargs):
        kwargs['identifier'] = cmx_id
        return cmx_model.make_cmx_chunk(self.cmx_cfg, **kwargs)

    def make_template(self):
        self.cmx_model.add(self.make_el(cmx_const.CONT_ID))
        self.cmx_model.add(self.make_el(cmx_const.CCMM_ID))
        self.cmx_model.add(self.make_el(cmx_const.DISP_ID,
                                        bmp=self._make_preview()))
        if self.cmx_cfg.pack:
            self.root = self.make_el(cmx_const.PACK_ID)
            self.cmx_model.add(self.root)

        for _page in self.sk2_mtds.get_pages():
            self.root.add(self.make_el(cmx_const.PAGE_ID))
            self.root.add(self.make_el(cmx_const.RLST_ID))
            if not self.cmx_cfg.v1:
                self.root.add(self.make_el(cmx_const.RLST_ID))

        cmx_ids = [cmx_const.ROTL_ID, cmx_const.ROTT_ID, cmx_const.RPEN_ID,
                   cmx_const.RDOT_ID, cmx_const.ROTA_ID, cmx_const.RCLR_ID,
                   cmx_const.RSCR_ID, cmx_const.INDX_ID]
        for cmx_id in cmx_ids:
            self.root.add(self.make_el(cmx_id))
        self.cmx_model.update_map()

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
        info = self.make_el(cmx_const.INFO_ID)
        self.cmx_model.add(info)

        metainfo = self.sk2_model.metainfo
        keys = metainfo[2] or ''
        notes = metainfo[3] or self._default_notes()

        info.add(self.make_el(cmx_const.IKEY_ID, text=keys))
        info.add(self.make_el(cmx_const.ICMT_ID, text=notes))
