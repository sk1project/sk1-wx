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

from sword.tools.objectbrowser.objectintrospection import ObjectIntrospectionWidget
from sword.tools.objectbrowser.visualizer import ObjectVisualizerWidget
from sword.tools.objectbrowser.objectviewer import ObjectViewerWidget

class ObjectBrowser(gtk.VBox):


	def __init__(self, app, presenter):

		gtk.VBox.__init__(self)
		self.app = app
		self.presenter = presenter

		self.nb = gtk.Notebook()
		self.nb.set_property('scrollable', True)

		self.introspect = ObjectIntrospectionWidget(app, presenter)
		self.nb.append_page(self.introspect, gtk.Label('Object Browser'))

		self.visualizer = ObjectVisualizerWidget(app, presenter)
		self.nb.append_page(self.visualizer, gtk.Label('Data Visualizer'))

		self.viewer = ObjectViewerWidget(app, presenter)
		self.nb.append_page(self.viewer, gtk.Label('Viewer'))

		self.nb.connect('switch-page', self.change_tab)

		self.pack_start(self.nb, True, True, 2)

		self.show_all()

		self.nb.set_current_page(0)

	def change_tab(self, *args):
		tab = args[2]
		if tab == 1:
			self.visualizer.active = True
			self.visualizer.update_view()
		else:
			self.visualizer.active = False




