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

from copy import deepcopy

from uc2.formats.sk1 import sk1const

def get_pdxf_color(clr):
	if not clr: return deepcopy(sk1const.fallback_color)
	color_spec = clr[0]
	if color_spec == sk1const.RGB:
		result = [sk1const.RGB, [clr[1], clr[2], clr[3]], 1.0, '']
		if len(clr) == 5:result[2] = clr[4]
		return result
	elif color_spec == sk1const.CMYK:
		result = [sk1const.CMYK, [clr[1], clr[2], clr[3], clr[4]], 1.0, '']
		if len(clr) == 6:result[2] = clr[5]
		return result
	elif color_spec == sk1const.SPOT:
		result = [sk1const.SPOT, [[clr[3], clr[4], clr[5]],
					[clr[6], clr[7], clr[8], clr[9]], clr[1]], 1.0, clr[2]]
		if len(clr) == 11:result[2] = clr[10]
		return result
	else:
		return deepcopy(sk1const.fallback_color)

def get_sk1_color(clr):
	if not clr: return deepcopy(sk1const.fallback_sk1color)
	color_spec = clr[0]
	val = clr[1]
	alpha = clr[2]
	name = clr[3]
	if color_spec == sk1const.RGB:
		if clr[2] == 1.0:
			result = (sk1const.RGB, val[0], val[1], val[2])
		else:
			result = (sk1const.RGB, val[0], val[1], val[2], alpha)
		return result
	elif color_spec == sk1const.CMYK:
		if clr[2] == 1.0:
			result = (sk1const.CMYK, val[0], val[1], val[2], val[3])
		else:
			result = (sk1const.CMYK, val[0], val[1], val[2], val[3], alpha)
		return result
	elif color_spec == sk1const.SPOT:
		rgb = val[0]
		cmyk = val[1]
		pal = val[2]
		if clr[2] == 1.0:
			result = (sk1const.SPOT, pal, clr[3], rgb[0], rgb[1], rgb[2],
					cmyk[0], cmyk[1], cmyk[2], cmyk[3])
		else:
			result = (sk1const.SPOT, pal, name, rgb[0], rgb[1], rgb[2],
					cmyk[0], cmyk[1], cmyk[2], cmyk[3], alpha)
		return result
	else:
		return deepcopy(sk1const.fallback_sk1color)

class PDXF_to_SK1_Translator:pass
class SK1_to_PDXF_Translator:pass
