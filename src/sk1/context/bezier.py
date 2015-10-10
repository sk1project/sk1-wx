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

from wal import LEFT, CENTER

from sk1.resources import pdids
from sk1.pwidgets import ActionButton
from generic import CtxPlugin

class BezierAddDeletePlugin(CtxPlugin):

	name = 'BezierAddDeletePlugin'

	def __init__(self, app, parent):
		CtxPlugin.__init__(self, app, parent)

	def build(self):
		btn = ActionButton(self, self.actions[pdids.ID_BEZIER_ADD_NODE])
		self.add(btn, 0, LEFT | CENTER, 2)

		btn = ActionButton(self, self.actions[pdids.ID_BEZIER_DELETE_NODE])
		self.add(btn, 0, LEFT | CENTER, 2)

class BezierJoinSplitPlugin(CtxPlugin):

	name = 'BezierJoinSplitPlugin'

	def __init__(self, app, parent):
		CtxPlugin.__init__(self, app, parent)

	def build(self):
		btn = ActionButton(self, self.actions[pdids.ID_BEZIER_ADD_SEG])
		self.add(btn, 0, LEFT | CENTER, 2)

		btn = ActionButton(self, self.actions[pdids.ID_BEZIER_DELETE_SEG])
		self.add(btn, 0, LEFT | CENTER, 2)

		btn = ActionButton(self, self.actions[pdids.ID_BEZIER_JOIN_NODE])
		self.add(btn, 0, LEFT | CENTER, 2)

		btn = ActionButton(self, self.actions[pdids.ID_BEZIER_SPLIT_NODE])
		self.add(btn, 0, LEFT | CENTER, 2)

class BezierLineCurvePlugin(CtxPlugin):

	name = 'BezierLineCurvePlugin'

	def __init__(self, app, parent):
		CtxPlugin.__init__(self, app, parent)

	def build(self):
		btn = ActionButton(self, self.actions[pdids.ID_BEZIER_SEG_TO_LINE])
		self.add(btn, 0, LEFT | CENTER, 2)

		btn = ActionButton(self, self.actions[pdids.ID_BEZIER_SEG_TO_CURVE])
		self.add(btn, 0, LEFT | CENTER, 2)

class BezierConnectionTypePlugin(CtxPlugin):

	name = 'BezierConnectionTypePlugin'

	def __init__(self, app, parent):
		CtxPlugin.__init__(self, app, parent)

	def build(self):
		btn = ActionButton(self, self.actions[pdids.ID_BEZIER_NODE_CUSP])
		self.add(btn, 0, LEFT | CENTER, 2)

		btn = ActionButton(self, self.actions[pdids.ID_BEZIER_NODE_SMOOTH])
		self.add(btn, 0, LEFT | CENTER, 2)

		btn = ActionButton(self, self.actions[pdids.ID_BEZIER_NODE_SYMMETRICAL])
		self.add(btn, 0, LEFT | CENTER, 2)
