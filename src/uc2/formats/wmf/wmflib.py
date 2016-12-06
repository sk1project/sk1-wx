# -*- coding: utf-8 -*-
#
# 	 Copyright (C) 2016 by Igor E. Novikov
#
# 	 This program is free software: you can redistribute it and/or modify
# 	 it under the terms of the GNU General Public License as published by
# 	 the Free Software Foundation, either version 3 of the License, or
# 	 (at your option) any later version.
#
# 	 This program is distributed in the hope that it will be useful,
# 	 but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	 GNU General Public License for more details.
#
# 	 You should have received a copy of the GNU General Public License
# 	 along with this program.  If not, see <http://www.gnu.org/licenses/>.

from struct import unpack

from uc2.formats.wmf import wmfconst

def get_markup(record):
	markup = [] + wmfconst.GENERIC_FIELDS
	if record.func in wmfconst.RECORD_MARKUPS:
		markup += wmfconst.RECORD_MARKUPS[record.func]

	if record.func == wmfconst.META_POLYGON:
		last = markup[-1]
		pos = last[0] + last[1]
		length = 4 * unpack('<h', record.chunk[last[0]:last[0] + 2])[0]
		markup.append((pos, length, 'aPoints (32-bit points)'))
	elif record.func == wmfconst.META_POLYPOLYGON:
		pos = 6
		markup.append((pos, 2, 'NumberofPolygons'))
		polygonnum = unpack('<h', record.chunk[pos:pos + 2])[0]
		pos += 2
		pointnums = []
		for i in range(polygonnum):
			pointnums.append(unpack('<h', record.chunk[pos:pos + 2])[0])
			markup.append((pos, 2, 'NumberofPoints'))
			pos += 2
		for pointnum in pointnums:
			length = 4 * pointnum
			markup.append((pos, length, 'aPoints (32-bit points)'))
			pos += length
	elif record.func == wmfconst.META_POLYLINE:
		pos = 6
		markup.append((pos, 2, 'NumberofPoints'))
		pointnum = unpack('<h', record.chunk[pos:pos + 2])[0]
		pos += 2
		length = 4 * pointnum
		markup.append((pos, length, 'aPoints (32-bit points)'))
	elif record.func == wmfconst.META_TEXTOUT:
		pos = 6
		markup.append((pos, 2, 'StringLength'))
		length = unpack('<h', record.chunk[pos:pos + 2])[0]
		if length % 2:length += 1
		pos += 2
		markup.append((pos, length, 'String'))
		pos += length
		markup.append((pos, 2, 'YStart'))
		pos += 2
		markup.append((pos, 2, 'XStart'))
	elif record.func == wmfconst.META_EXTTEXTOUT:
		pos = 6
		markup.append((pos, 2, 'Y'))
		pos += 2
		markup.append((pos, 2, 'X'))
		pos += 2
		markup.append((pos, 2, 'StringLength'))
		length = unpack('<h', record.chunk[pos:pos + 2])[0]
		if length % 2:length += 1
		pos += 2
		markup.append((pos, 2, 'fwOpts'))
		pos += 2
		if len(record.chunk) - pos == length:
			markup.append((pos, length, 'String'))
		else:
			markup.append((pos, 8, 'Rectangle'))
			pos += 8
			markup.append((pos, length, 'String'))
			pos += length
			if not len(record.chunk) == pos:
				length = len(record.chunk) - pos
				markup.append((pos, length, 'Dx'))
	elif record.func == wmfconst.META_CREATEFONTINDIRECT:
		pos = 6
		markup.append((pos, 2, 'Height'))
		pos += 2
		markup.append((pos, 2, 'Width'))
		pos += 2
		markup.append((pos, 2, 'Escapement'))
		pos += 2
		markup.append((pos, 2, 'Orientation'))
		pos += 2
		markup.append((pos, 2, 'Weight'))
		pos += 2
		markup.append((pos, 1, 'Italic'))
		pos += 1
		markup.append((pos, 1, 'Underline'))
		pos += 1
		markup.append((pos, 1, 'StrikeOut'))
		pos += 1
		markup.append((pos, 1, 'CharSet'))
		pos += 1
		markup.append((pos, 1, 'OutPrecision'))
		pos += 1
		markup.append((pos, 1, 'ClipPrecision'))
		pos += 1
		markup.append((pos, 1, 'Quality'))
		pos += 1
		markup.append((pos, 1, 'PitchAndFamily'))
		pos += 1
		length = len(record.chunk) - pos
		markup.append((pos, length, 'Facename'))
	elif record.func == wmfconst.META_DIBCREATEPATTERNBRUSH:
		pos = 6
		markup.append((pos, 2, 'Style'))
		pos += 2
		markup.append((pos, 2, 'ColorUsage'))
		pos += 2
		length = len(record.chunk) - pos
		markup.append((pos, length, 'Variable-bit DIB Object'))

	return markup
