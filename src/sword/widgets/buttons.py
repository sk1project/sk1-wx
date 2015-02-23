# -*- coding: utf-8 -*-
#
#	Copyright (C) 2011-2012 by Igor E. Novikov
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

class NavigationButton(gtk.Button):
	def __init__(self, stock_id, text=''):
		gtk.Button.__init__(self)
		self.set_property('relief', gtk.RELIEF_NONE)
		image = gtk.image_new_from_stock(stock_id, gtk.ICON_SIZE_BUTTON)
		self.add(image)
		if text:
			self.set_tooltip_text(text)

class NavigationToggleButton(gtk.ToggleButton):
	def __init__(self, stock_id, text=''):
		gtk.ToggleButton.__init__(self)
		self.set_property('relief', gtk.RELIEF_NONE)
		image = gtk.image_new_from_stock(stock_id, gtk.ICON_SIZE_BUTTON)
		self.add(image)
		if text:
			self.set_tooltip_text(text)

class ImageButton(gtk.Button):
	def __init__(self, path, text):
		gtk.Button.__init__(self)
		self.set_property('relief', gtk.RELIEF_NONE)
		loader = gtk.gdk.pixbuf_new_from_file
		image = gtk.Image()
		pixbuf = loader(os.path.join(config.resource_dir, path))
		image.set_from_pixbuf(pixbuf)
		self.add(image)
		if text:
			self.set_tooltip_text(text)

class ActionButton(gtk.Button):
	def __init__(self, action):
		gtk.Button.__init__(self)
		self.set_property('relief', gtk.RELIEF_NONE)
		self.action = action
		if not self.action.icon is None:
			image = gtk.image_new_from_stock(self.action.icon, gtk.ICON_SIZE_BUTTON)
			self.add(image)
		else:
			self.set_label(self.action.tooltip)
		self.action.connect_proxy(self)
		self.set_tooltip_text(self.action.tooltip)
