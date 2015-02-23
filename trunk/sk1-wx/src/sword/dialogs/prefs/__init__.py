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
from sword.dialogs.prefs.extappstab import ExternalAppsTab

def get_prefs_dialog(app):

	parent = app.mw
	title = _('%s Preferences') % (app.appdata.app_name)

	nb = PrefsNotebook(app)
	nb.set_property('scrollable', True)
	nb.set_tab_pos(gtk.POS_TOP)

	dialog = gtk.Dialog(title, parent,
	                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
	                   (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
	                    gtk.STOCK_APPLY, gtk.RESPONSE_ACCEPT))
	dialog.vbox.pack_start(nb)
	nb.show()

	ret = dialog.run()
	if ret == gtk.RESPONSE_ACCEPT:
		nb.run_apply()
	dialog.destroy()

class PrefsNotebook(gtk.Notebook):

	def __init__(self, app):
		self.app = app
		gtk.Notebook.__init__(self)

		self.ext_apps_tab = ExternalAppsTab(self.app)
		self.append_page(self.ext_apps_tab, self.ext_apps_tab.caption_label)

		self.widgets = [self.ext_apps_tab, ]

	def run_apply(self):
		for widget in self.widgets:
			widget.do_apply()



