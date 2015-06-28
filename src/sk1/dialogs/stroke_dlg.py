# -*- coding: utf-8 -*-
#
#	Copyright (C) 2015 by Igor E. Novikov
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

from uc2 import uc2const
from sk1 import _, config

class StrokeDialog(wal.OkCancelDialog):

	presenter = None

	def __init__(self, parent, title, presenter):
		self.presenter = presenter
		wal.OkCancelDialog.__init__(self, parent, title, style=wal.VERTICAL,
								size=(500, 350), add_line=False)

	def build(self):
		self.nb = wal.Notebook(self)
		self.nb.add_page(StrokeStyle(self.nb, self), _('Stroke Style'))
		self.nb.add_page(StrokeColor(self.nb, self), _('Stroke Color'))

		self.pack(self.nb, fill=True, expand=True)

	def get_result(self):
		return []

def stroke_dlg(parent, presenter, title=_("Stroke")):
	return StrokeDialog(parent, title, presenter).show()

class StrokeStyle(wal.VPanel):

	def __init__(self, parent, dlg):
		self.dlg = dlg
		wal.VPanel.__init__(self, parent)

class StrokeColor(wal.VPanel):

	def __init__(self, parent, dlg):
		self.dlg = dlg
		wal.VPanel.__init__(self, parent)
