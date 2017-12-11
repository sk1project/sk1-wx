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
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from copy import deepcopy

from uc2.formats.svg import svg_const
from uc2.formats.svg.svglib import create_xmlobj, create_nl


def create_new_svg(config):
    doc = create_xmlobj('svg', deepcopy(svg_const.SVG_ATTRS))
    defs = create_xmlobj('defs', {'id': 'defs1'})
    doc.childs.append(create_nl())
    doc.childs.append(defs)
    return doc


class SVG_Methods:
    presenter = None
    model = None
    config = None

    def __init__(self, presenter):
        self.presenter = presenter

    def update(self):
        self.model = self.presenter.model
        self.config = self.presenter.config

    def doc_units(self):
        for item in self.model.childs:
            if item.tag == 'sodipodi:namedview':
                if 'inkscape:document-units' in item.attrs:
                    return item.attrs['inkscape:document-units']
        return 'px'
