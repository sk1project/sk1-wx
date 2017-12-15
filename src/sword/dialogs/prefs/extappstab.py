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

from sword import _, config

class ExternalAppsTab(gtk.VBox):

	name = "External Applications"
	caption = _("External Applications")
	caption_label = None


	def __init__(self, app):

		gtk.VBox.__init__(self)
		self.app = app
		self.caption_label = gtk.Label(self.caption)

		spacer = gtk.VBox()
		self.add(spacer)
		self.set_border_width(15)
		self.set_size_request(550, 300)

		tab = gtk.Table(6, 2, False)
		tab.set_row_spacings(10)
		tab.set_col_spacings(10)
		spacer.add(tab)

		#---------------------------

		label = gtk.Label('External image viewer:')
		label.set_alignment(0, 0.5)
		tab.attach(label, 0, 1, 0, 1, gtk.FILL, gtk.SHRINK)

		self.entry1 = gtk.Entry()
		self.entry1.set_text(config.ext_image_view)
		tab.attach(self.entry1, 1, 2, 0, 1, gtk.EXPAND | gtk.FILL, gtk.SHRINK)

		#---------------------------

		label = gtk.Label('External text editor:')
		label.set_alignment(0, 0.5)
		tab.attach(label, 0, 1, 1, 2, gtk.FILL, gtk.SHRINK)

		self.entry2 = gtk.Entry()
		self.entry2.set_text(config.ext_text_view)
		tab.attach(self.entry2, 1, 2, 1, 2, gtk.EXPAND | gtk.FILL, gtk.SHRINK)

		#---------------------------

		label = gtk.Label('External document viewer:')
		label.set_alignment(0, 0.5)
		tab.attach(label, 0, 1, 2, 3, gtk.FILL, gtk.SHRINK)

		self.entry3 = gtk.Entry()
		self.entry3.set_text(config.ext_doc_view)
		tab.attach(self.entry3, 1, 2, 2, 3, gtk.EXPAND | gtk.FILL, gtk.SHRINK)

		#---------------------------

		label = gtk.Label('External HTML viewer:')
		label.set_alignment(0, 0.5)
		tab.attach(label, 0, 1, 3, 4, gtk.FILL, gtk.SHRINK)

		self.entry4 = gtk.Entry()
		self.entry4.set_text(config.ext_html_view)
		tab.attach(self.entry4, 1, 2, 3, 4, gtk.EXPAND | gtk.FILL, gtk.SHRINK)

		#---------------------------

		label = gtk.Label('External binary editor:')
		label.set_alignment(0, 0.5)
		tab.attach(label, 0, 1, 4, 5, gtk.FILL, gtk.SHRINK)

		self.entry5 = gtk.Entry()
		self.entry5.set_text(config.ext_binary_view)
		tab.attach(self.entry5, 1, 2, 4, 5, gtk.EXPAND | gtk.FILL, gtk.SHRINK)

		#---------------------------

		label = gtk.Label('External compare tool:')
		label.set_alignment(0, 0.5)
		tab.attach(label, 0, 1, 5, 6, gtk.FILL, gtk.SHRINK)

		self.entry6 = gtk.Entry()
		self.entry6.set_text(config.ext_compare_view)
		tab.attach(self.entry6, 1, 2, 5, 6, gtk.EXPAND | gtk.FILL, gtk.SHRINK)

		self.show_all()

	def do_apply(self):
		config.ext_image_view = self.entry1.get_text()
		config.ext_text_view = self.entry2.get_text()
		config.ext_doc_view = self.entry3.get_text()
		config.ext_html_view = self.entry4.get_text()
		config.ext_binary_view = self.entry5.get_text()
		config.ext_compare_view = self.entry6.get_text()



