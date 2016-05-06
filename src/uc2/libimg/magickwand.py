# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2016 by Igor E. Novikov
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

from cStringIO import StringIO

BILEVEL_TYPE = 'BilevelType'
L_TYPE = 'GrayscaleType'
LA_TYPE = 'GrayscaleMatteType'
P_TYPE = 'PaletteType'
PA_TYPE = 'PaletteMatteType'
RGB_TYPE = 'TrueColorType'
RGBA_TYPE = 'TrueColorMatteType'
CMYK_TYPE = 'ColorSeparationType'
CMYKA_TYPE = 'ColorSeparationMatteType'

WAND_TYPES = [BILEVEL_TYPE, L_TYPE, LA_TYPE, P_TYPE, PA_TYPE,
			RGB_TYPE, RGBA_TYPE, CMYK_TYPE, CMYKA_TYPE, ]
ALPHA_TYPES = [LA_TYPE, PA_TYPE, RGBA_TYPE, CMYKA_TYPE]
CMYK_TYPES = [CMYK_TYPE, CMYKA_TYPE]
DUOTONES = [BILEVEL_TYPE, L_TYPE, LA_TYPE]

def get_magickwand_version():
	import _libimg
	ver = _libimg.get_version()
	return ' '.join(ver[0].split(' ')[1:-1]), ver[1]

def check_image_file(filepath):
	import _libimg
	_libimg.init_magick()
	wand = _libimg.new_image()
	ret = _libimg.load_image(wand, filepath)
	_libimg.terminate_magick()
	return ret == 1

def process_image(raw_content):
	import _libimg
	alpha = None
	_libimg.init_magick()
	wand = _libimg.new_image()
	_libimg.load_image_blob(wand, raw_content)

	image_type = _libimg.get_image_type(wand)
	if image_type in ALPHA_TYPES:
		alpha_wand = _libimg.clone_image(wand)
		_libimg.remove_alpha_channel(wand)
		_libimg.set_image_format(alpha_wand, 'png')
		_libimg.set_image_type(alpha_wand, RGBA_TYPE)
		alpha = StringIO(_libimg.get_image_blob(alpha_wand))
		alpha.seek(0)

	if image_type in CMYK_TYPES:
		_libimg.set_image_format(wand, 'tiff')
		_libimg.set_image_type(wand, CMYK_TYPE)
	else:
		_libimg.set_image_format(wand, 'png')

	base = StringIO(_libimg.get_image_blob(wand))
	base.seek(0)
	_libimg.terminate_magick()
	return base, alpha

def process_pattern(raw_content):
	import _libimg
	_libimg.init_magick()
	wand = _libimg.new_image()
	_libimg.load_image_blob(wand, raw_content)
	image_type = _libimg.get_image_type(wand)
	_libimg.set_image_format(wand, 'tiff')
	base = StringIO(_libimg.get_image_blob(wand))
	base.seek(0)
	_libimg.terminate_magick()
	return base, image_type in DUOTONES
