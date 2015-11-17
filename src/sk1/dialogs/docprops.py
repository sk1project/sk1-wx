# -*- coding: utf-8 -*-
#
#	Copyright (C) 2013-2015 by Igor E. Novikov
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

import wal

from sk1 import _, config

class DP_Panel(wal.VPanel):

	name = 'Panel'

	def __init__(self, parent, app, dlg):
		self.app = app
		self.dlg = dlg
		self.doc = app.current_doc
		wal.VPanel.__init__(self, parent)
		self.build()

	def build(self):pass
	def save(self):pass

class GeneralProps(DP_Panel):

	name = _('General')

class PageProps(DP_Panel):

	name = _('Page')

class GridProps(DP_Panel):

	name = _('Grid')

class GuidesProps(DP_Panel):

	name = _('Guides')

PANELS = [GeneralProps, PageProps, GridProps, GuidesProps]

class DocPropertiesDialog(wal.OkCancelDialog):

	sizer = None
	app = None
	panels = []

	def __init__(self, app, parent, title, size=config.docprops_dlg_size):
		self.app = app
		wal.OkCancelDialog.__init__(self, parent, title, size)

	def build(self):
		self.panels = []
		nb = wal.Notebook(self)
		for item in PANELS:
			item_panel = item(nb, self.app, self)
			self.panels.append(item_panel)
			nb.add_page(item_panel, item_panel.name)
		self.pack(nb, expand=True, fill=True, padding=5)

	def get_result(self):
		for item in self.panels:
			item.save()
		return None



def docprops_dlg(app, parent):
	title = _('Document properties')
	dlg = DocPropertiesDialog(app, parent, title)
	dlg.Centre()
	dlg.ShowModal()
	dlg.Destroy()
