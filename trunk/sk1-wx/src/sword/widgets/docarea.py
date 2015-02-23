# -*- coding: utf-8 -*-
#
#	Copyright (C) 2012 by Igor E. Novikov
#	
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#	
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#	
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gtk

from sword.tools.modelbrowser import ModelBrowser
from sword.tools.objectbrowser import ObjectBrowser
from sword.widgets.captions import TabDocCaption


class DocArea(gtk.VBox):


	def __init__(self, app, presenter):

		gtk.VBox.__init__(self)
		self.app = app
		self.presenter = presenter
		self.caption = presenter.doc_name

		self.tab_caption = TabDocCaption(self, self.caption)

		hpaned = gtk.HPaned()
		hpaned.set_border_width(2)
		hpaned.set_position(250)

		self.modelbrowser = ModelBrowser(app, presenter)
		hpaned.pack1(self.modelbrowser, True, False)
		self.modelbrowser.set_size_request(250, -1)

		self.objectbrowser = ObjectBrowser(app, presenter)
		hpaned.pack2(self.objectbrowser, True, False)

		self.pack_start(hpaned , True, True, 2)

		self.show_all()


	def set_caption(self, caption):
		self.caption = caption
		self.tab_caption.set_caption(self.caption)

