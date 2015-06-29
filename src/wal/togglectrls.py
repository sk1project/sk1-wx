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

from basic import HPanel
from gctrls import ImageToggleButton

class ModeToggleButton(ImageToggleButton):

	keeper = None
	mode = 0
	callback = None

	def __init__(self, parent, keeper, mode, icons, names, on_change=None):
		self.keeper = keeper
		self.mode = mode
		self.callback = on_change
		ImageToggleButton.__init__(self, parent, False, icons[mode],
								tooltip=names[mode], onchange=self.change)

	def change(self):
		if not self.get_active():
			if self.keeper.mode == self.mode:
				self.set_active(True)
		else:
			if not self.keeper.mode == self.mode:
				if self.callback: self.callback(self.mode)

	def set_mode(self, mode):
		if not self.mode == mode:
			if self.get_active():
				self.set_active(False)
		else:
			if not self.get_active():
				self.set_active(True)

class HToggleKeeper(HPanel):

	mode = 0
	mode_buts = []
	modes = []
	callback = None

	def __init__(self, parent, modes, icons, names, on_change=None):
		self.modes = modes
		self.mode_buts = []
		self.callback = on_change
		HPanel.__init__(self, parent)
		for item in self.modes:
			but = ModeToggleButton(self, self, item, icons, names, self.changed)
			self.mode_buts.append(but)
			self.pack(but)

	def changed(self, mode):
		self.mode = mode
		for item in self.mode_buts:
			item.set_mode(mode)
		if self.callback: self.callback(mode)

	def set_mode(self, mode):
		self.mode = mode
		for item in self.mode_buts:
			item.set_mode(mode)

