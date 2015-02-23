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

class TabIconCaption(gtk.HBox):
	def __init__(self, stock_id, text=''):
		gtk.HBox.__init__(self)
		image = gtk.image_new_from_stock(stock_id, gtk.ICON_SIZE_SMALL_TOOLBAR)
		self.add(image)
		if text:
			self.set_tooltip_text(text)
		self.show_all()


class TabDocCaption(gtk.HBox):

	do_action = False

	def __init__(self, master, caption):
		gtk.HBox.__init__(self, False, 0)
		self.presenter = master.presenter
		self.app = master.app
		self.mw = master.app.mw

		self.label = gtk.Label('')
		self.tab_icon = gtk.Image()
		self.tab_icon.set_from_stock(gtk.STOCK_FILE, gtk.ICON_SIZE_MENU)
		self.but_icon = gtk.Image()
		self.but_icon.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)


		self.tab_button = gtk.EventBox()
		self.tab_button.set_border_width(0)
		self.tab_button.set_visible_window(False)
		self.tab_button.set_size_request(15, 15)
		color = self.mw.get_style().bg[gtk.STATE_ACTIVE]
		self.tab_button.modify_bg(gtk.STATE_NORMAL, color)
		self.tab_button.add(self.but_icon)

		self.pack_start(self.tab_icon, False)
		self.pack_start(self.label, False)
		self.pack_start(self.tab_button, False)
		self.set_caption(caption)
		self.show_all()
		self.but_icon.set_property('sensitive', False)

		self.tab_button.connect('button-press-event', self.button_press)
		self.tab_button.connect('button-release-event', self.button_release)
		self.tab_button.connect('leave-notify-event', self.leave_event)
		self.tab_button.connect('enter-notify-event', self.enter_event)

	def set_caption(self, caption):
		self.label.set_text('  %s  ' % (caption))

	def enter_event(self, *args):
		self.but_icon.set_property('sensitive', True)

	def leave_event(self, *args):
		self.but_icon.set_property('sensitive', False)
		self.do_action = False

	def button_press(self, *args):
		self.but_icon.set_property('sensitive', False)
		self.do_action = True

	def button_release(self, *args):
		self.but_icon.set_property('sensitive', True)
		if self.do_action:
			self.app.close(self.presenter)
