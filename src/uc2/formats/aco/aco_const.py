# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2017 by Igor E. Novikov
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

import struct, colorsys
from uc2 import uc2const, cms

ACO1_VER = '\x00\x01'
ACO2_VER = '\x00\x02'

ACO_RGB = 0
ACO_HSB = 1
ACO_CMYK = 2
ACO_LAB = 7
ACO_GRAY = 8
ACO_WIDE_CMYK = 9

ACO_COLORS = (ACO_RGB, ACO_HSB, ACO_CMYK, ACO_LAB, ACO_GRAY, ACO_WIDE_CMYK)

def aco_chunk2color(chunk):
	color = [uc2const.COLOR_RGB, [], 1.0, '', '']
	model = struct.unpack('>H', chunk[:2])[0]
	vals = chunk[2:10]
	if model == ACO_RGB:
		clr = struct.unpack('>3H', vals[:6])
		color[1] = map(lambda x:x / 65535.0, clr)
	elif model == ACO_HSB:
		clr = struct.unpack('>3H', vals[:6])
		color[1] = colorsys.hsv_to_rgb(*map(lambda x:x / 65535.0, clr))
	elif model == ACO_CMYK:
		clr = struct.unpack('>4H', vals)
		color[0] = uc2const.COLOR_CMYK
		color[1] = map(lambda x:1.0 - x / 65535.0, clr)
	elif model == ACO_LAB:
		L, a, b = struct.unpack('>H 2h', vals[:6])
		clr = (L / 10000.0,
			(a / 100.0 + 128.0) / 255.0,
			(b / 100.0 + 128.0) / 255.0)
		color[1] = cms.lab_to_rgb(clr)
	elif model == ACO_GRAY:
		color[0] = uc2const.COLOR_GRAY
		color[1] = [struct.unpack('>H', vals[:2])[0] / 10000.0, ]
	elif model == ACO_WIDE_CMYK:
		clr = struct.unpack('>4H', vals)
		color[0] = uc2const.COLOR_CMYK
		color[1] = map(lambda x:float(x) / 10000.0, clr)
	else:
		return None
	if len(chunk) > 10:
		name = chunk[12:-2]
		if chunk[12:13] < '\x00\x1f':name = name[2:]
		color[3] = name.decode('utf_16_be').strip()
	else:
		color[3] = cms.verbose_color(color)
	return color

def color2aco_chunk(color, version=ACO1_VER):pass
