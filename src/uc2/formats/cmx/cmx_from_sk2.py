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
from uc2.formats.cmx import cmx_model, cmx_const, cmx_instr
from uc2.formats.sk2.crenderer import CairoRenderer

LOG = logging.getLogger(__name__)
mkinstr = cmx_instr.make_instruction


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
        index = 0
        cmx_pages = self.cmx_model.chunk_map['pages']
        for page in self.sk2_mtds.get_pages():
            cmx_page = cmx_pages[index][0]
            rlsts = cmx_pages[index][1:]
            if self.cmx_cfg.v1:
                self.make_v1_page(page, index + 1, cmx_page, rlsts)

            index += 1

    def make_v1_page(self, page, page_num, cmx_page, rlst):
        kwargs = {
            'page_number': page_num,
            'flags': 0,
            'bbox': (0, 0, 0, 0),
            'tail': '\x00\x00\x01\x00\x00\x00',
        }
        page_instr = mkinstr(self.cmx_cfg,
                             identifier=cmx_const.BEGIN_PAGE, **kwargs)
        cmx_page.add(page_instr)

        layer_count = 1
        for layer in page.childs:
            kwargs = {
                'page_number': page_num,
                'layer_number': layer_count,
                'flags': 0,
                'tally': 0,
                'layer_name': layer.name,
                'tail': '\x01\x00\x00\x00',
            }
            layer_instr = mkinstr(self.cmx_cfg,
                                  identifier=cmx_const.BEGIN_LAYER, **kwargs)
            page_instr.add(layer_instr)

            for obj in layer.childs:
                self.make_v1_objects(layer_instr, obj)

            layer_count += 1

            layer_instr.add(
                mkinstr(self.cmx_cfg, identifier=cmx_const.END_LAYER))

        page_instr.add(
            mkinstr(self.cmx_cfg, identifier=cmx_const.END_PAGE))

    def make_v1_objects(self, parent_instr, obj):
        if obj.is_group and obj.childs:
            kwargs = {
                'bbox': (0, 0, 0, 0),
                'tail': '\x00\x00',
            }
            group_instr = mkinstr(self.cmx_cfg,
                                  identifier=cmx_const.BEGIN_GROUP, **kwargs)
            parent_instr.add(group_instr)

            for item in obj.childs:
                self.make_v1_objects(group_instr, item)

            group_instr.add(
                mkinstr(self.cmx_cfg, identifier=cmx_const.END_PAGE))

        elif obj.is_primitive:
            curve = obj.to_curve()
            if not curve:
                return
            elif curve.is_group:
                self.make_v1_objects(parent_instr, curve)
            else:
                # TODO: curve processing
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
