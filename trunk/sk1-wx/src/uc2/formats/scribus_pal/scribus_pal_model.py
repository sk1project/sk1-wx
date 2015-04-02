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


from uc2.formats.generic import TaggedModelObject

class SPObject(TaggedModelObject):
	"""
	Represents unknown/generic Scribus palette object.
	"""

	def __init__(self):
		self.childs = []

	def resolve(self):
		is_node = len(self.childs)
		info = ''
		if is_node:info = '%d' % (len(self.childs))
		return (not is_node, self.tag, info)

class ScribusPalette(SPObject):
	"""
	Represents Scribus palette object.
	This is a root DOM instance of Scribus palette file format.
	All palette colors are members of childs list.
	"""
	tag = 'SCRIBUSCOLORS'
	Name = ''
	comments = ''

class SPColor(SPObject):
	"""
	Represents Scribus palette color object.
	"""
	tag = 'COLOR'

	NAME = ''
	CMYK = ''
	RGB = ''
	Spot = '0'
	Register = '0'
