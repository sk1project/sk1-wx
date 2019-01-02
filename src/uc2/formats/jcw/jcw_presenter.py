# -*- coding: utf-8 -*-
#
#  Copyright (C) 2015 by Igor E. Novikov
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

from uc2 import uc2const, cms
from uc2.formats.generic import BinaryModelPresenter
from uc2.formats.jcw.jcw_config import JCW_Config
from uc2.formats.jcw.jcw_const import JCW_CMYK, JCW_RGB, JCW_NAMESIZE
from uc2.formats.jcw.jcw_filters import JCW_Loader, JCW_Saver
from uc2.formats.jcw.jcw_model import JCW_Palette, JCW_Color


class JCW_Presenter(BinaryModelPresenter):
    cid = uc2const.JCW

    config = None
    doc_file = ''
    model = None

    def __init__(self, appdata, cnf=None):
        cnf = cnf or {}
        self.config = JCW_Config()
        config_file = os.path.join(appdata.app_config_dir, self.config.filename)
        self.config.load(config_file)
        self.config.update(cnf)
        self.appdata = appdata
        self.cms = self.appdata.app.default_cms
        self.loader = JCW_Loader()
        self.saver = JCW_Saver()
        self.new()

    def new(self):
        self.model = JCW_Palette()

    def convert_from_skp(self, skp_doc):
        skp_model = skp_doc.model

        namesize = JCW_NAMESIZE
        for item in skp_model.colors:
            namesize = max(namesize, len(item[3]))

        if skp_model.colors[0][0] == uc2const.COLOR_CMYK:
            colorspace = JCW_CMYK
        else:
            colorspace = JCW_RGB

        self.model = JCW_Palette(colorspace, namesize)
        for color in skp_model.colors:
            if colorspace == JCW_CMYK:
                clr = self.cms.get_cmyk_color(color)
            else:
                clr = self.cms.get_rgb_color(color)
            if clr[3]:
                clr[3] = clr[3].encode('iso-8859-1', errors='ignore')
            if not clr[3]:
                if colorspace == JCW_CMYK:
                    clr[3] += cms.cmyk_to_hexcolor(color[1])
                else:
                    clr[3] += cms.rgb_to_hexcolor(color[1])

            self.model.childs.append(JCW_Color(colorspace, namesize, color))
        self.model.update_for_save()

    def convert_to_skp(self, skp_doc):
        skp_model = skp_doc.model
        if self.model.name:
            skp_model.name = self.model.name
        else:
            skp_model.name = self.model.resolve_name
        skp_model.source = self.config.source
        if self.doc_file:
            filename = os.path.basename(self.doc_file)
            if skp_model.comments:
                skp_model.comments += '\n'
            skp_model.comments += 'Converted from %s' % filename
        for item in self.model.childs:
            clr = item.get_color()
            if clr:
                skp_model.colors.append(clr)
