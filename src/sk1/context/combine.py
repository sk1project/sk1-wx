# -*- coding: utf-8 -*-
#
#	Copyright (C) 2013 by Igor E. Novikov
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

from sk1.resources import pdids
from sk1.widgets import LEFT, CENTER
from sk1.pwidgets import ActionButton
from generic import CtxPlugin

class CombinePlugin(CtxPlugin):

	name = 'CombinePlugin'

	def __init__(self, app, parent):
		CtxPlugin.__init__(self, app, parent)

	def build(self):
		btn = ActionButton(self, self.actions[pdids.ID_COMBINE])
		self.add(btn, 0, LEFT | CENTER, 2)

		btn = ActionButton(self, self.actions[pdids.ID_BREAK_APART])
		self.add(btn, 0, LEFT | CENTER, 2)

class GroupPlugin(CtxPlugin):

	name = 'GroupPlugin'

	def __init__(self, app, parent):
		CtxPlugin.__init__(self, app, parent)

	def build(self):
		btn = ActionButton(self, self.actions[pdids.ID_GROUP])
		self.add(btn, 0, LEFT | CENTER, 2)

		btn = ActionButton(self, self.actions[pdids.ID_UNGROUP])
		self.add(btn, 0, LEFT | CENTER, 2)

		btn = ActionButton(self, self.actions[pdids.ID_UNGROUPALL])
		self.add(btn, 0, LEFT | CENTER, 2)

class ToCurvePlugin(CtxPlugin):

	name = 'ToCurvePlugin'

	def __init__(self, app, parent):
		CtxPlugin.__init__(self, app, parent)

	def build(self):
		btn = ActionButton(self, self.actions[pdids.ID_TO_CURVES])
		self.add(btn, 0, LEFT | CENTER, 2)