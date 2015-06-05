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

import struct
from colorsys import hsv_to_rgb
from uc2 import uc2const

from uc2.formats.jcw.jcw_const import JCW_PMS, JCW_CMYK_PANTONE, \
JCW_RGB_PANTONE, JCW_HSV_PANTONE, JCW_CMYK, JCW_SPOT_CMYK, JCW_RGB, \
JCW_SPOT_RGB, JCW_HSV, JCW_SPOT_HSV

def val_to_dec(vals):
	ret = []
	for item in vals:
		ret.append(item / 10000.0)
	return ret

def parse_cmyk(data):
	cmyk = val_to_dec(struct.unpack('<4H', data))
	return [uc2const.COLOR_CMYK, cmyk, 1.0, '']

def parse_rgb(data):
	rgb = val_to_dec(struct.unpack('<3H', data[:6]))
	return [uc2const.COLOR_RGB, rgb, 1.0, '']

def parse_hsv(data):
	hsv = val_to_dec(struct.unpack('<3H', data[:6]))
	rgb = list(hsv_to_rgb(*hsv))
	return [uc2const.COLOR_RGB, rgb, 1.0, '']

def parse_jcw_color(cs, data):
	if cs in (JCW_PMS, JCW_CMYK_PANTONE, JCW_CMYK, JCW_SPOT_CMYK):
		return parse_cmyk(data)
	elif cs in (JCW_RGB_PANTONE, JCW_RGB, JCW_SPOT_RGB):
		return parse_rgb(data)
	elif cs in (JCW_HSV_PANTONE, JCW_HSV, JCW_SPOT_HSV):
		return parse_hsv(data)
	else: return []
