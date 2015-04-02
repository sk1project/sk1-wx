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


from uc2.formats.generic import TextModelObject
from uc2.formats.soc.soc_const import SOURCE_LO


class SOC_Palette(TextModelObject):
	"""
	Represents SOC palette object.
	This is a single and root DOM instance of SOC file format.
	All palette colors are members of colors field list.
	Color sample: ['#ffffff','White']
	"""

	source = SOURCE_LO
	name = ''
	comments = ''
	columns = 1
	colors = []

	def __init__(self, source=SOURCE_LO):
		self.source = source
		self.colors = []

	def resolve(self, name=''):
		is_leaf = False
		info = '%d' % (len(self.colors))
		name = 'SOC Palette'
		return (is_leaf, name, info)
