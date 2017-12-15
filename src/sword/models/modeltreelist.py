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

NODE_ICON = gtk.Image().render_icon(gtk.STOCK_DIRECTORY, gtk.ICON_SIZE_MENU)
LEAF_ICON = gtk.Image().render_icon(gtk.STOCK_FILE, gtk.ICON_SIZE_MENU)
COLOR = '#A7A7A7'

class ObjectTreeModel(gtk.TreeStore):

	def __init__(self, model):
		gtk.TreeStore.__init__(self, gtk.gdk.Pixbuf, str, str, str)

		self.model = model
		self.model_dict = {}

		iter = self.append(None)
		self.add_to_dict(self.model, iter)
		self.model_dict[iter] = self.model
		icon_type, name, info = self.model.resolve()
		self.set(iter, 0, self.get_icon(icon_type),
						1, name,
						2, info,
						3, COLOR)
		for child in self.model.childs:
			self.scan_model(iter, child)

	def scan_model(self, iter, obj):
		child_iter = self.append(iter)
		self.add_to_dict(obj, child_iter)
		icon_type, name, info = obj.resolve()
		self.set(child_iter, 0, self.get_icon(icon_type),
							1, name,
							2, info,
							3, COLOR)
		for item in obj.childs:
			self.scan_model(child_iter, item)

	def add_to_dict(self, obj, iter):
		path_str = self.get_path(iter).__str__()
		self.model_dict[path_str] = obj

	def get_obj_by_path(self, path):
		return self.model_dict[path.__str__()]

	def get_icon(self, type):
		if type: return LEAF_ICON
		return NODE_ICON
