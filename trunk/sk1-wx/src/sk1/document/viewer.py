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

from wal import VPanel

class DocViewer(VPanel):

	presenter = None
	size = ()

	def __init__(self, presenter, parent, size=(5, 5)):
		self.presenter = presenter
		self.size = size
		VPanel.__init__(self, parent)
		self.add(size)

	def destroy(self):
		self.Destroy()
		items = self.__dict__.keys()
		for item in items:
			self.__dict__[item] = None