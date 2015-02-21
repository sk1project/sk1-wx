# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2013 by Igor E. Novikov
#
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
#
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
#
# 	You should have received a copy of the GNU General Public License
# 	along with this program.  If not, see <http://www.gnu.org/licenses/>.

from sk1 import events

class AppClipboard:

	contents = []

	def __init__(self, app):
		self.app = app
		self.contents = []

	def set(self, objs):
		self.contents = []
		for obj in objs:
			self.contents.append(obj.copy())
		events.emit(events.CLIPBOARD)

	def get(self):
		result = []
		for obj in self.contents:
			result.append(obj.copy())
		return result
