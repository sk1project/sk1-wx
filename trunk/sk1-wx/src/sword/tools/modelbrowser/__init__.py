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

import sys

import gtk

from sword.tools.modelbrowser.resourceview import ResourceViewWidget
from sword.tools.modelbrowser.modelview import ModelViewWidget

class ModelBrowser(gtk.VBox):


	def __init__(self, app, presenter):

		gtk.VBox.__init__(self)
		self.app = app
		self.presenter = presenter

		self.nb = gtk.Notebook()
		self.nb.set_property('scrollable', True)


		self.modeltree = ModelViewWidget(app, presenter)
		self.nb.append_page(self.modeltree, gtk.Label('Model Tree'))

		self.pack_start(self.nb, True, True, 2)

		if not self.presenter.doc_presenter is None:
			if self.presenter.doc_presenter.doc_dir:

				self.resourceview = ResourceViewWidget(app, presenter)
				self.nb.append_page(self.resourceview, gtk.Label('Resources'))


		self.show_all()
