# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 by Igor E. Novikov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import gtk

from sword import config
from sword.tools.modelbrowser.modelview import ModelViewWidget
from sword.tools.objectbrowser.objectintrospection import \
    ObjectIntrospectionWidget
from sword.tools.objectbrowser.visualizer import ObjectVisualizerWidget
from sword.widgets.captions import TabDocCaption


class DocArea(gtk.VBox):
    view = False

    def __init__(self, app, presenter):
        gtk.VBox.__init__(self)
        self.app = app
        self.presenter = presenter
        self.caption = presenter.doc_name

        self.tab_caption = TabDocCaption(self, self.caption)

        self.tb = DocToolbar(app, self)
        self.pack_start(self.tb, False, True, 0)

        self.hpaned = gtk.HPaned()
        self.hpaned.set_border_width(0)
        self.hpaned.set_position(250)

        self.modelbrowser = ModelViewWidget(app, presenter)
        self.hpaned.pack1(self.modelbrowser, True, False)
        self.modelbrowser.set_size_request(250, -1)

        self.inspect = ObjectIntrospectionWidget(app, presenter)
        self.hexview = ObjectVisualizerWidget(app, presenter)
        self.hpaned.pack2(self.hexview if config.bin_view
                          else self.inspect, True, False)
        self.view = config.bin_view

        self.pack_start(self.hpaned, True, True, 0)

        self.show_all()

    def set_caption(self, caption):
        self.caption = caption
        self.tab_caption.set_caption(self.caption)

    def change_view(self, *args):
        self.view = not self.view
        config.bin_view = self.view
        self.hpaned.remove(self.hpaned.get_child2())
        self.hpaned.pack2(self.hexview if self.view
                          else self.inspect, True, False)


class DocToolbar(gtk.Toolbar):

    def __init__(self, app, docarea, entries=[]):
        gtk.Toolbar.__init__(self)
        self.app = app
        self.docarea = docarea
        self.actions = self.app.actions
        self.add_entries = entries

        self.set_style(gtk.TOOLBAR_ICONS)
        self.build()

    def create_entries(self):
        return [
                   'BACKWARD',
                   'FORWARD',
                   None,
                   'ROOT',
                   'REFRESH_OBJ',
                   None,
                   'COLLAPSE',
                   'EXPAND',
                   None,
                   'SAVE_CHUNK',
                   None,
               ] + self.add_entries

    def build(self):
        entries = self.create_entries()
        index = 0
        for entry in entries:
            if entry is None:
                button = gtk.SeparatorToolItem()
            else:
                action = self.actions[entry]
                button = action.create_tool_item()
            self.insert(button, index)
            index += 1
        btn = gtk.ToggleToolButton(gtk.STOCK_JUSTIFY_FILL)
        btn.set_tooltip_text("Data view")
        btn.set_active(config.bin_view)
        btn.connect("toggled", self.docarea.change_view)
        self.insert(btn, index)
