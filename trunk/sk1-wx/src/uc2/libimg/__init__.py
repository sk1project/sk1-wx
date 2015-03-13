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

import sys
import cairo
from copy import deepcopy
from base64 import b64decode, b64encode
from cStringIO import StringIO
from PIL import Image, ImageOps

from uc2.cms import rgb_to_hexcolor
from uc2.libimg.imwand import check_image_file, process_image

def check_image(path):
	return check_image_file

def invert_image(cms, bmpstr):
	image_stream = StringIO()
	raw_image = Image.open(StringIO(b64decode(bmpstr)))
	raw_image.load()

	if raw_image.mode == '1':
		raw_image = ImageOps.invert(raw_image.convert('L')).convert('1')
	elif raw_image.mode == 'CMYK':
		raw_image = cms.convert_image(raw_image, 'RGB')
		inv_image = ImageOps.invert(raw_image)
		raw_image = cms.convert_image(inv_image, 'CMYK')
	elif raw_image.mode == 'LAB':
		raw_image = cms.convert_image(raw_image, 'RGB')
		inv_image = ImageOps.invert(raw_image)
		raw_image = cms.convert_image(inv_image, 'LAB')
	else:
		raw_image = ImageOps.invert(raw_image)

	raw_image.save(image_stream, format='TIFF')
	return b64encode(image_stream.getvalue())

def convert_image(cms, bmpstr, colorspace):
	image_stream = StringIO()
	raw_image = Image.open(StringIO(b64decode(bmpstr)))
	raw_image.load()
	raw_image = cms.convert_image(raw_image, colorspace)
	raw_image.save(image_stream, format='TIFF')
	return b64encode(image_stream.getvalue())

def update_image(cms, image_obj):
	png_stream = StringIO()

	raw_image = Image.open(StringIO(b64decode(image_obj.bitmap)))
	raw_image.load()

	cache_image = None

	if image_obj.colorspace in ['1', 'L']:
		if image_obj.colorspace == '1':
			raw_image = raw_image.convert('L')
		fg = image_obj.style[3][0]
		bg = image_obj.style[3][1]

		if fg and bg:
			fg = rgb_to_hexcolor(cms.get_display_color(fg))
			bg = rgb_to_hexcolor(cms.get_display_color(bg))
			cache_image = Image.new('RGB', image_obj.size, fg)
			bg_image = Image.new('RGB', image_obj.size, bg)
			cache_image.paste(bg_image, (0, 0), raw_image)
		elif fg and not bg:
			fg = rgb_to_hexcolor(cms.get_display_color(fg))
			cache_image = Image.new('RGBA', image_obj.size, fg)
			cache_image.putalpha(ImageOps.invert(raw_image))
		elif bg and not fg:
			bg = rgb_to_hexcolor(cms.get_display_color(bg))
			cache_image = Image.new('RGBA', image_obj.size, bg)
			cache_image.putalpha(raw_image)
		else:
			cache_image = Image.new('RGBA', image_obj.size, '#000000')
			cache_image.putalpha(Image.new('L', image_obj.size, 0))
	else:
		cache_image = cms.get_display_image(raw_image)

	if image_obj.alpha_channel:
		raw_alpha = b64decode(image_obj.alpha_channel)
		raw_alpha = Image.open(StringIO(raw_alpha))
		cache_image = cache_image.convert('RGBA')
		cache_image.putalpha(raw_alpha)

	if cache_image:
		cache_image.save(png_stream, format='PNG')

	png_stream.seek(0)
	image_obj.cache_cdata = cairo.ImageSurface.create_from_png(png_stream)

def update_gray_image(cms, image_obj):
	png_stream = StringIO()

	raw_image = Image.open(StringIO(b64decode(image_obj.bitmap)))
	raw_image.load()

	raw_image = raw_image.convert('L')

	if image_obj.alpha_channel:
		raw_alpha = b64decode(image_obj.alpha_channel)
		raw_alpha = Image.open(StringIO(raw_alpha))
		rgb_image = raw_image.convert('RGBA')
		rgb_image.putalpha(raw_alpha)
	else:
		rgb_image = raw_image.convert('RGB')

	rgb_image.save(png_stream, format='PNG')

	png_stream.seek(0)
	image_obj.cache_gray_cdata = cairo.ImageSurface.create_from_png(png_stream)

def extract_profile(raw_content):
	profile = None
	mode = None
	try:
		img = Image.open(StringIO(raw_content))
		if 'icc_profile' in img.info.keys():
			profile = img.info.get('icc_profile')
			mode = img.mode
	except:pass
	return profile, mode

def set_image_data(cms, image_obj, raw_content):
	alpha = ''
	profile, mode = extract_profile(raw_content)

	base_stream, alpha_stream = process_image(raw_content)
	base_image = Image.open(base_stream)
	base_image.load()

	image_obj.size = () + base_image.size
	if not base_image.mode in ['1', 'L', 'RGB', 'CMYK', 'LAB']:
		base_image = base_image.convert('RGB')

	if not base_image.mode in ['L', 'RGB', 'CMYK', 'LAB']:
		profile = mode = None

	if profile and base_image.mode == mode:
		base_image = cms.adjust_image(base_image, profile)

	image_obj.colorspace = '' + base_image.mode

	fobj = StringIO()
	base_image = base_image.copy()
	base_image.save(fobj, format='TIFF')
	bmp = b64encode(fobj.getvalue())

	style = deepcopy(image_obj.config.default_image_style)
	if base_image.mode in ['RGB', 'LAB']:
		style[3] = deepcopy(image_obj.config.default_rgb_image_style)

	if alpha_stream:
		alpha_image = Image.open(alpha_stream)
		alpha_image.load()
		if alpha_image.mode == 'P':
			alpha_image = alpha_image.convert('RGBA')
		if alpha_image.mode in ['LA', 'RGBA']:
			if alpha_image.mode == 'LA':
				band = alpha_image.split()[1]
			else:
				band = alpha_image.split()[3]
			fobj = StringIO()
			band.save(fobj, format='PNG')
			alpha = b64encode(fobj.getvalue())

	image_obj.bitmap = bmp
	image_obj.alpha_channel = alpha
	image_obj.style = style




