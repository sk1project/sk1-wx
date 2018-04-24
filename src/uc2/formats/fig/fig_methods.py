# -*- coding: utf-8 -*-
#
#  Copyright (C) 2018 by Maxim S. Barabash
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


from uc2.formats.fig import fig_model
from uc2 import uc2const
from . import fig_const


def create_new_doc(config):
    doc = fig_model.FIGDocument(config)
    return doc


class FIGMethods(object):
    presenter = None
    model = None
    config = None

    def __init__(self, presenter):
        self.presenter = presenter

    def update(self):
        self.model = self.presenter.model
        self.config = self.presenter.config

    # ---DOCUMENT

    def get_doc_units(self):
        return self.model.units

    def set_doc_unit(self, units):
        self.model.units = units

    def get_doc_metainfo(self):
        return self.model.comment or ''

    def set_doc_metainfo(self, metainfo):
        if isinstance(metainfo, (list, tuple)):
            metainfo = '\n'.join(metainfo)
        self.model.comment = metainfo

    # --- PAGES

    def get_pages_obj(self):
        model = self.model
        paper_size = uc2const.PAGE_FORMATS.get(model.paper_size)
        if not paper_size:
            paper_size = uc2const.PAGE_FORMATS['A4']
        if model.orientation == fig_const.LANDSCAPE:
            size = max(paper_size), min(paper_size)
        else:
            size = min(paper_size), max(paper_size)
        return [model.paper_size, size, model.orientation]
