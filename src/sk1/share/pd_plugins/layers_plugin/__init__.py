# -*- coding: utf-8 -*-
#
#  Copyright (C) 2016 by Ihor E. Novikov
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

import wal
from sk1 import _, events
from sk1.app_plugins import RsPlugin
from sk1.dialogs import edit_dlg
from sk1.resources import icons, get_icon

PLG_DIR = __path__[0]
IMG_DIR = os.path.join(PLG_DIR, 'images')


def make_artid(name):
    return os.path.join(IMG_DIR, name + '.png')


PLUGIN_ICON = make_artid('icon')

BITMAPS = [
    'check-no', 'check-yes',
    'visible-no', 'visible-yes',
    'editable-no', 'editable-yes',
    'printable-no', 'printable-yes',
    'aa-no', 'aa-yes',
]

ACTIONS = [

]


class LayersPlugin(RsPlugin):
    pid = 'LayersPlugin'
    name = _('Layers')
    active_panel = None
    panels = {}
    select_idx = None
    layer_new = None
    layer_to_bottom = None
    layer_lower = None
    layer_raise = None
    layer_to_top = None
    layer_delete = None
    layer_edit = None
    viewer = None

    def build_ui(self):
        self.icon = get_icon(PLUGIN_ICON)
        self.panel.pack(wal.Label(self.panel, _('Layers'), fontbold=True),
                        padding=3)
        self.panel.pack(wal.HLine(self.panel), fill=True)

        pnl = wal.HPanel(self.panel)
        self.layer_new = wal.ImageButton(
            pnl, icons.PD_LAYER_NEW, tooltip=_('Create new layer'),
            onclick=self.new_layer)
        self.layer_to_bottom = wal.ImageButton(
            pnl, icons.PD_LOWER_TO_BOTTOM, tooltip=_('Move layer to bottom'),
            onclick=self.lower_layer_to_bottom)
        self.layer_lower = wal.ImageButton(
            pnl, icons.PD_LOWER, tooltip=_('Move layer down'),
            onclick=self.lower_layer)
        self.layer_raise = wal.ImageButton(
            pnl, icons.PD_RAISE, tooltip=_('Move layer up'),
            onclick=self.raise_layer)
        self.layer_to_top = wal.ImageButton(
            pnl, icons.PD_RAISE_TO_TOP, tooltip=_('Move layer to top'),
            onclick=self.raise_layer_to_top)
        self.layer_delete = wal.ImageButton(
            pnl, icons.PD_LAYER_DELETE, tooltip=_('Delete layer'),
            onclick=self.delete_layer)
        self.layer_edit = wal.ImageButton(
            pnl, icons.PD_EDIT, tooltip=_('Rename layer'),
            onclick=self.rename_layer)
        pnl.pack(self.layer_new)
        pnl.pack(self.layer_to_bottom)
        pnl.pack(self.layer_lower)
        pnl.pack(self.layer_raise)
        pnl.pack(self.layer_to_top)
        pnl.pack(self.layer_delete)
        pnl.pack(self.layer_edit)
        self.panel.pack(pnl)

        bmp = [make_artid(item) for item in BITMAPS]
        pnl = wal.VPanel(self.panel)
        self.viewer = wal.LayerList(pnl, self.get_data(), bmp,
                                    on_select=self.update,
                                    on_change=self.changed,
                                    on_double_click=self.rename_layer)
        pnl.pack(self.viewer, fill=True, expand=True)
        self.panel.pack(pnl, padding_all=3, fill=True, expand=True)

        events.connect(events.DOC_CHANGED, self.update)
        events.connect(events.DOC_MODIFIED, self.update)
        events.connect(events.PAGE_CHANGED, self.update)
        self.update()

    def get_data(self):
        doc = self.app.current_doc
        if not doc:
            return []
        result = []
        for layer in doc.get_layers():
            props = []
            if doc.active_layer == layer:
                props.append(1)
            else:
                props.append(0)
            for item in layer.properties:
                props.append(item)
            props.append(layer.name)
            result.append(props)
        result.reverse()
        return result

    def get_selected_index(self):
        doc = self.app.current_doc
        layers = doc.get_layers()
        return len(layers) - self.viewer.get_selected() - 1

    def get_selected_layer(self):
        doc = self.app.current_doc
        layers = doc.get_layers()
        index = len(layers) - self.viewer.get_selected() - 1
        return layers[index]

    def get_layer_index(self, layer):
        doc = self.app.current_doc
        layers = doc.get_layers()
        index = layers.index(layer)
        return len(layers) - index - 1

    def changed(self, _item, col):
        doc = self.app.current_doc
        layers = doc.get_layers()
        index = self.get_selected_index()
        if not col:
            if not layers[index] == doc.active_layer:
                doc.api.set_active_layer(layers[index])
        elif col < 5:
            layer = layers[index]
            if col < 3 and layer == doc.active_layer:
                flag = False
                for item in layers:
                    if item.properties[0] and item.properties[1] and not \
                            layer == item:
                        doc.api.set_active_layer(item)
                        flag = True
                if not flag:
                    return
            props = [] + layer.properties
            props[col - 1] = abs(props[col - 1] - 1)
            doc.api.set_layer_properties(layer, props)

    def new_layer(self):
        self.app.current_doc.api.create_layer()

    def delete_layer(self):
        doc = self.app.current_doc
        layers = doc.get_layers()
        indx = self.get_selected_index()
        doc.api.delete_layer(layers[indx])
        self.viewer.set_selected(0)

    def raise_layer(self):
        layer = self.get_selected_layer()
        self.app.current_doc.api.layer_raise(layer)
        self.viewer.set_selected(self.get_layer_index(layer))
        self.update()

    def raise_layer_to_top(self):
        layer = self.get_selected_layer()
        self.app.current_doc.api.layer_to_top(layer)
        self.viewer.set_selected(self.get_layer_index(layer))
        self.update()

    def lower_layer(self):
        layer = self.get_selected_layer()
        self.app.current_doc.api.layer_lower(layer)
        self.viewer.set_selected(self.get_layer_index(layer))
        self.update()

    def lower_layer_to_bottom(self):
        layer = self.get_selected_layer()
        self.app.current_doc.api.layer_to_bottom(layer)
        self.viewer.set_selected(self.get_layer_index(layer))
        self.update()

    def rename_layer(self):
        layer = self.get_selected_layer()
        txt = edit_dlg(self.app.mw, _('Rename layer'), layer.name)
        if txt is not None and not layer.name == txt:
            self.app.current_doc.api.set_layer_name(layer, txt)

    def update(self, *_args):
        doc = self.app.current_doc
        if doc:
            layers = doc.get_layers()
            lnums = len(layers)
            self.viewer.update(self.get_data())
            sel_idx = self.viewer.get_selected()
            if sel_idx is None:
                self.viewer.set_selected(0)
                sel_idx = 0
            sel_layer = self.get_selected_layer()
            self.layer_to_bottom.set_enable(sel_idx < lnums - 1)
            self.layer_lower.set_enable(sel_idx < lnums - 1)
            self.layer_raise.set_enable(sel_idx > 0)
            self.layer_to_top.set_enable(sel_idx > 0)
            self.layer_delete.set_enable(not sel_layer == doc.active_layer)

    def show_signal(self, *args):
        self.update()


def get_plugin(app):
    return LayersPlugin(app)
