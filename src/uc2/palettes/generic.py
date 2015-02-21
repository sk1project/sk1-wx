# -*- coding: utf-8 -*-
#
#	Copyright (C) 2014 by Igor E. Novikov
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


class SKPalette:

	name = ''
	source = ''
	columns = 1
	comments = ''
	colors = []

	def __init__(self, name=''):
		self.colors = []
		if name: self.name = name

class PalFmtPresenter:

	fmt_descr = ''
	fmt_ext = ()

	def __init__(self):pass
	def load_palette(self, path):return None
	def save_palette(self, palette, path):pass
	def check_palette(self, path): return False
