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
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from uc2.formats.sk import sk_model


def create_new_doc(config):
    doc = sk_model.SKDocument(config)
    layout = sk_model.SKLayout()
    doc.childs.append(layout)
    doc.layout = layout
    doc.childs.append(sk_model.SKLayer())
    grid = sk_model.SKGrid()
    doc.childs.append(grid)
    doc.grid = grid
    glayer = sk_model.SKGuideLayer()
    doc.childs.append(glayer)
    doc.guidelayer = glayer
    return doc


class SK_Methods:
    presenter = None
    model = None
    config = None

    def __init__(self, presenter):
        self.presenter = presenter

    def update(self):
        self.model = self.presenter.model
        self.config = self.presenter.model.config

    # --- Generic object methods

    def delete_object(self, obj):
        parent = obj.parent
        parent.childs.remove(obj)

    def insert_object(self, obj, parent, index=0):
        parent.childs.insert(index, obj)
        obj.parent = parent

    def append_object(self, obj, parent):
        parent.childs.append(obj)
        obj.parent = parent

    def append_objects(self, objs, parent):
        parent.childs += objs
        for obj in objs:
            obj.parent = parent

    # --- Page methods

    def get_layout_obj(self):
        return self.model.layout

    # --- Layer methods

    def get_layer(self, page, layer_num=0):
        layers = self.model.childs[1:-2]
        return layers[layer_num]

    def is_layer_visible(self, layer):
        if layer.visible:
            return True
        return False

    def get_grid_layer(self):
        return self.model.grid

    def get_guide_layer(self):
        return self.model.guidelayer
