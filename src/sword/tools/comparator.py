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

from sword import _
from sword.widgets.captions import TabIconCaption

class Comparator(gtk.VBox):

	name = "Comparator"
	caption = _("Comparator")
	caption_label = None


	def __init__(self, app):

		gtk.VBox.__init__(self)
		self.app = app
		self.caption_label = TabIconCaption(gtk.STOCK_COPY, self.caption)

		spacer = gtk.VBox()
		self.add(spacer)
		self.set_border_width(5)

		nav_panel = gtk.HBox()
		nav_panel.set_border_width(0)


		self.show_all()
