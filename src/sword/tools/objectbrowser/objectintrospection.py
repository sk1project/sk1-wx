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

import os

import gtk

from sword import config
from sword.tools.objectbrowser.introspector import Introspector
from sword.tools.objectbrowser.toolbar import OIToolbar

class ObjectIntrospectionWidget(gtk.VBox):


	def __init__(self, app, presenter):

		gtk.VBox.__init__(self)
		self.app = app
		self.presenter = presenter

		self.toolbar = OIToolbar(self.app)
		self.pack_start(self.toolbar, False, True)

		self.spacer = gtk.HBox()
		self.pack_end(self.spacer, False, True, 5)

		self.viewer = OIViewer(app, presenter)
		self.pack_end(self.viewer, True, True)

		self.show_all()

class OIViewer(gtk.HBox):

	def __init__(self, app, presenter):

		gtk.HBox.__init__(self)
		self.app = app
		self.presenter = presenter

		loader = gtk.gdk.pixbuf_new_from_file
		image = gtk.Image()
		pixbuf = loader(os.path.join(config.resource_dir, 'introspection.png'))
		image.set_from_pixbuf(pixbuf)

		spacer = gtk.VBox()
		self.pack_start(spacer, False, True, 0)

		spacer.pack_start(image, False, False, 0)

		self.editor = Introspector(app, presenter)

		self.sw = gtk.ScrolledWindow()
		self.sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.sw.add(self.editor)

		self.pack_start(self.sw, True, True, 5)

		self.show_all()
