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
		lenght = 4 * unpack('<h', record.chunk[last[0]:last[0] + 2])[0]
		markup.append((pos, lenght, 'aPoints (32-bit points)'))
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
			lenght = 4 * pointnum
			markup.append((pos, lenght, 'aPoints (32-bit points)'))
			pos += lenght

	return markup
