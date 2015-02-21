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

from sk1 import _, config, events
from sk1.resources import icons, get_bmp
from sk1.widgets import LEFT, CENTER
from sk1.pwidgets import UnitSpin
from generic import CtxPlugin

class JumpPlugin(CtxPlugin):

	name = 'JumpPlugin'

	def __init__(self, app, parent):
		CtxPlugin.__init__(self, app, parent)
		events.connect(events.CONFIG_MODIFIED, self.config_changed)

	def build(self):
		bmp = get_bmp(self, icons.CTX_OBJECT_JUMP, _('Default object jump'))
		self.add(bmp, 0, LEFT | CENTER, 2)

		self.jump_spin = UnitSpin(self.app, self, onenter=self.user_changes)
		self.jump_spin.set_point_value(config.obj_jump)
		self.add(self.jump_spin, 0, LEFT | CENTER, 2)

	def user_changes(self, *args):
		val = self.jump_spin.get_point_value()
		if not config.obj_jump == val:
			config.obj_jump = val

	def config_changed(self, *args):
		if args[0][0] == 'obj_jump':
			val = self.jump_spin.get_point_value()
			if not config.obj_jump == val:
				self.jump_spin.set_point_value(config.obj_jump)
