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

from colorsys import yiq_to_rgb, hls_to_rgb, hsv_to_rgb

from uc2 import uc2const
from uc2.utils import double2py_float, word2py_int, long2py_float
from uc2.formats.cdr.cdr_const import cdrunit_to_pt, \
CDR_COLOR_CMYK, CDR_COLOR_BGR, CDR_COLOR_CMY, CDR_COLOR_CMYK255, \
CDR_COLOR_GRAY, CDR_COLOR_LAB, CDR_COLOR_REGISTRATION, CDR_COLOR_CMYK2, \
CDR_COLOR_HSB, CDR_COLOR_HLS, CDR_COLOR_YIQ, CDR_COLOR_LAB2

def parse_matrix(data):
	"""
	Parses CDR affine transformation matrix and 
	returns matrix as a list.
	"""
	m11 = double2py_float(data[0:8])
	m12 = double2py_float(data[8:16])
	dx = double2py_float(data[16:24]) * cdrunit_to_pt
	m21 = double2py_float(data[24:32])
	m22 = double2py_float(data[32:40])
	dy = double2py_float(data[40:48]) * cdrunit_to_pt
	return [m11, m21, m12, m22, dx, dy]

def parse_cmyk(data):
	"""
	Parses CMYK color bytes and	returns fill style list.
	"""
	c = ord(data[0]) / 100.0
	m = ord(data[1]) / 100.0
	y = ord(data[2]) / 100.0
	k = ord(data[3]) / 100.0
	return [uc2const.COLOR_CMYK, [c, m, y, k], 1.0, '']

def parse_cmyk255(data):
	"""
	Parses CMYK255 color bytes and returns fill style list.
	"""
	c = ord(data[0]) / 255.0
	m = ord(data[1]) / 255.0
	y = ord(data[2]) / 255.0
	k = ord(data[3]) / 255.0
	return [uc2const.COLOR_CMYK, [c, m, y, k], 1.0, '']

def parse_cmy(data):
	"""
	Parses CMY color bytes and returns fill style list.
	"""
	c = ord(data[0]) / 255.0
	m = ord(data[1]) / 255.0
	y = ord(data[2]) / 255.0
	k = 0.0
	return [uc2const.COLOR_CMYK, [c, m, y, k], 1.0, '']

def parse_bgr(data):
	"""
	Parses BGR color bytes and returns fill style list.
	"""
	b = ord(data[0]) / 255.0
	g = ord(data[1]) / 255.0
	r = ord(data[2]) / 255.0
	return [uc2const.COLOR_RGB, [r, g, b], 1.0, '']

def parse_lab(data):
	"""
	Parses Lab color bytes and returns fill style list.
	"""
	l = ord(data[0]) / 255.0
	a = ord(data[1]) / 255.0
	b = ord(data[2]) / 255.0
	return [uc2const.COLOR_LAB, [l, a, b], 1.0, '']

def parse_lab2(data):
	"""
	Parses Lab color bytes and returns fill style list.
	"""
	l = ord(data[0]) / 255.0
	a = ord(data[1]) / 255.0
	b = ord(data[2]) / 255.0
	return [uc2const.COLOR_LAB, [l, a, b], 1.0, '']

def parse_grayscale(data):
	"""
	Parses Grayscale color byte and returns fill style list.
	"""
	l = ord(data[0]) / 255.0
	return [uc2const.COLOR_GRAY, [l, ], 1.0, '']

def parse_hsb(data):
	"""
	Parses HSB/HSV color bytes and returns fill style list.
	"""
	h = word2py_int(data[0:2]) / 360.0
	s = ord(data[2]) / 255.0
	v = ord(data[3]) / 255.0
	r, g, b = hsv_to_rgb(h, s, v)
	return [uc2const.COLOR_RGB, [r, g, b], 1.0, '']

def parse_hls(data):
	"""
	Parses HLS color bytes and returns fill style list.
	"""
	h = word2py_int(data[0:2]) / 360.0
	l = ord(data[2]) / 255.0
	s = ord(data[3]) / 255.0
	r, g, b = hls_to_rgb(h, l, s)
	return [uc2const.COLOR_RGB, [r, g, b], 1.0, '']

def parse_yiq(data):
	"""
	Parses YIQ color bytes and returns fill style list.
	"""
	y = ord(data[0]) / 255.0
	i = 2.0 * ord(data[1]) / 255.0 - 1.0
	q = 2.0 * ord(data[2]) / 255.0 - 1.0
	r, g, b = yiq_to_rgb(y, i, q)
	return [uc2const.COLOR_RGB, [r, g, b], 1.0, '']

def parse_reg_color(data=''):
	"""
	Returns Registration color fill style list.
	"""
	return [uc2const.COLOR_SPOT, [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0, 1.0] ], 1.0, 'Registration color']

def parse_cdr_color(colorspace, color_bytes):
	"""
	Parses color type and returns according color value.
	"""
	if colorspace == CDR_COLOR_CMYK:
		return parse_cmyk(color_bytes)
	elif colorspace in (CDR_COLOR_CMYK255, CDR_COLOR_CMYK2):
		return parse_cmyk255(color_bytes)
	elif colorspace == CDR_COLOR_CMY:
		return parse_cmy(color_bytes[0:3])
	elif colorspace == CDR_COLOR_BGR:
		return parse_bgr(color_bytes[0:3])
	elif colorspace == CDR_COLOR_GRAY:
		return parse_grayscale(color_bytes[0])
	elif colorspace == CDR_COLOR_LAB:
		return parse_lab(color_bytes[0:3])
	elif colorspace == CDR_COLOR_LAB2:
		return parse_lab2(color_bytes[0:3])
	elif colorspace == CDR_COLOR_HSB:
		return parse_hsb(color_bytes)
	elif colorspace == CDR_COLOR_HLS:
		return parse_hls(color_bytes)
	elif colorspace == CDR_COLOR_YIQ:
		return parse_yiq(color_bytes[0:3])
	elif colorspace == CDR_COLOR_REGISTRATION:
		return parse_reg_color()
	return []

def parse_cdr_spot_color(cs, clrbytes, cs2, clrbytes2):
	spot = uc2const.COLOR_SPOT
	rgb = uc2const.COLOR_RGB
	cmyk = uc2const.COLOR_CMYK
	clr = parse_cdr_color(cs, clrbytes)
	clr2 = parse_cdr_color(cs2, clrbytes2)
	if not clr and clr2: return clr2
	if not clr2: return clr
	if clr[0] == clr2[0]:
		if clr[0] == rgb:
			return [spot, [clr[1], []], 1.0, '']
		elif clr[0] == cmyk:
			return [spot, [[], clr[1]], 1.0, '']
		else:
			return clr
	elif clr[0] in (rgb, cmyk) and clr2[0] in (rgb, cmyk):
		if clr[0] == rgb:
			return [spot, [clr[1], clr2[1]], 1.0, '']
		else:
			return [spot, [clr2[1], clr[1]], 1.0, '']
	elif clr[0] in (rgb, cmyk):
		return clr
	elif clr2[0] in (rgb, cmyk):
		return clr2
	else:
		return clr

def parse_size_value(data):
	"""
	Convert 4-bytes string to value in points.
	"""
	return long2py_float(data) * cdrunit_to_pt
