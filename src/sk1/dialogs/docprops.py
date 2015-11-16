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
from wal import const

from sk1 import _, config

class DocPropertiesDialog(wal.OkCancelDialog):

	sizer = None
	app = None

	def __init__(self, app, parent, title, size=config.docprops_dlg_size):
		self.app = app
		wal.OkCancelDialog.__init__(self, parent, title, size)

	def build(self):

		nb = wal.Notebook(self)
		nb.add_page(wal.VPanel(nb), _('General'))
		nb.add_page(wal.VPanel(nb), _('Page size'))
		nb.add_page(wal.VPanel(nb), _('Grid'))
		nb.add_page(wal.VPanel(nb), _('Guides'))

		self.pack(nb, expand=True, fill=True, padding=5)

def docprops_dlg(app, parent):
	title = _('Document properties')
	dlg = DocPropertiesDialog(app, parent, title)
	dlg.Centre()
	dlg.ShowModal()
	dlg.Destroy()