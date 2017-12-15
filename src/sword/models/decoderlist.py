# -*- coding: utf-8 -*-
#
#	Copyright (C) 2012 by Igor E. Novikov
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

from copy import deepcopy

import struct

import gtk

VALUES = {
	'hex':'--',
	'Char':'--',
	'UChar':'--',
	'Short':'--',
	'UShort':'--',
	'Int':'--',
	'UInt':'--',
	'Long':'--',
	'ULong':'--',
	'LongLong':'--',
	'ULongLong':'--',
	'Float':'--',
	'Double':'--',
}

ORDER = [
	'hex',
	'Char',
	'UChar',
	'Short',
	'UShort',
	'Int',
	'UInt',
	'Long',
	'ULong',
	'LongLong',
	'ULongLong',
	'Float',
	'Double',
	]

class DecoderListModel(gtk.ListStore):

	def __init__(self, data='', flag=False):

		gtk.ListStore.__init__(self, str, str)

		values = deepcopy(VALUES)
		data = data.replace(' ', '')
		data = data.replace('\n', '')

		if data: values['hex'] = data

		endian = '<'
		if flag: endian = '>'

		if not len(data) & 1:
			bytes = data.decode('hex')
			if len(bytes) == 1:
				values['Char'], = struct.unpack('b', bytes)
				values['UChar'], = struct.unpack('B', bytes)
			elif len(bytes) == 2:
				values['Short'], = struct.unpack(endian + 'h', bytes)
				values['UShort'], = struct.unpack(endian + 'H', bytes)
			elif len(bytes) == 4:
				values['Int'], = struct.unpack(endian + 'i', bytes)
				values['UInt'], = struct.unpack(endian + 'I', bytes)
				values['Long'], = struct.unpack(endian + 'l', bytes)
				values['ULong'], = struct.unpack(endian + 'L', bytes)
				values['Float'], = struct.unpack(endian + 'f', bytes)
			elif len(bytes) == 8:
				values['LongLong'], = struct.unpack(endian + 'q', bytes)
				values['ULongLong'], = struct.unpack(endian + 'Q', bytes)
				values['Double'], = struct.unpack(endian + 'd', bytes)

		for item in ORDER:
			self.append((item, values[item]))

