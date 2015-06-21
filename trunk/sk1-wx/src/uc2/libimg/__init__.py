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

import sys, os
import cairo
from copy import deepcopy
from base64 import b64decode, b64encode
from cStringIO import StringIO
from PIL import Image, ImageOps

from uc2.cms import rgb_to_hexcolor
from uc2.libimg.imwand import check_image_file, process_image
from uc2.uc2const import IMAGE_CMYK, IMAGE_RGB, IMAGE_RGBA, IMAGE_LAB
from uc2.uc2const import IMAGE_GRAY, IMAGE_MONO

DUOTONES = [IMAGE_GRAY, IMAGE_MONO]
SUPPORTED_CS = [IMAGE_MONO, IMAGE_GRAY, IMAGE_RGB, IMAGE_CMYK, IMAGE_LAB]

def get_version():
	return Image.VERSION

def check_image(path):
	return check_image_file

def invert_image(cms, bmpstr):
	image_stream = StringIO()
	raw_image = Image.open(StringIO(b64decode(bmpstr)))
	raw_image.load()

	if raw_image.mode == IMAGE_MONO:
		raw_image = ImageOps.invert(raw_image.convert(IMAGE_GRAY))
		raw_image = raw_image.convert(IMAGE_MONO)
	elif raw_image.mode == IMAGE_CMYK:
		raw_image = cms.convert_image(raw_image, IMAGE_RGB)
		inv_image = ImageOps.invert(raw_image)
		raw_image = cms.convert_image(inv_image, IMAGE_CMYK)
	elif raw_image.mode == IMAGE_LAB:
		raw_image = cms.convert_image(raw_image, IMAGE_RGB)
		inv_image = ImageOps.invert(raw_image)
		raw_image = cms.convert_image(inv_image, IMAGE_LAB)
	else:
		raw_image = ImageOps.invert(raw_image)

	raw_image.save(image_stream, format='TIFF')
	return b64encode(image_stream.getvalue())

def convert_image(cms, pixmap, colorspace):
	image_stream = StringIO()
	if pixmap.colorspace in DUOTONES and not colorspace in DUOTONES:
		cdata_stream = StringIO()
		pixmap.cache_cdata.write_to_png(cdata_stream)
		cdata_stream.seek(0)
		raw_image = Image.open(cdata_stream)
		raw_image.load()
		raw_image = raw_image.convert("RGB")
	else:
		raw_image = Image.open(StringIO(b64decode(pixmap.bitmap)))
		raw_image.load()
	raw_image = cms.convert_image(raw_image, colorspace)
	raw_image.save(image_stream, format='TIFF')
	return b64encode(image_stream.getvalue())

def extract_bitmap(pixmap, filepath):
	if not os.path.splitext(filepath)[1] == '.tiff':
		filepath = os.path.splitext(filepath)[0] + '.tiff'
	fileptr = open(filepath, 'wb')
	fileptr.write(b64decode(pixmap.bitmap))
	fileptr.close()
	if pixmap.alpha_channel:
		filepath = os.path.splitext(filepath)[0] + '_alphachannel.tiff'
		fileptr = open(filepath, 'wb')
		fileptr.write(b64decode(pixmap.alpha_channel))
		fileptr.close()

def update_image(cms, pixmap):
	png_stream = StringIO()

	raw_image = Image.open(StringIO(b64decode(pixmap.bitmap)))
	raw_image.load()

	cache_image = None

	if pixmap.colorspace in DUOTONES:
		if pixmap.colorspace == IMAGE_MONO:
			raw_image = raw_image.convert(IMAGE_GRAY)
		fg = pixmap.style[3][0]
		bg = pixmap.style[3][1]

		if fg and bg:
			fg = rgb_to_hexcolor(cms.get_display_color(fg))
			bg = rgb_to_hexcolor(cms.get_display_color(bg))
			cache_image = Image.new(IMAGE_RGB, pixmap.size, fg)
			bg_image = Image.new(IMAGE_RGB, pixmap.size, bg)
			cache_image.paste(bg_image, (0, 0), raw_image)
		elif fg and not bg:
			fg = rgb_to_hexcolor(cms.get_display_color(fg))
			cache_image = Image.new(IMAGE_RGBA, pixmap.size, fg)
			cache_image.putalpha(ImageOps.invert(raw_image))
		elif bg and not fg:
			bg = rgb_to_hexcolor(cms.get_display_color(bg))
			cache_image = Image.new(IMAGE_RGBA, pixmap.size, bg)
			cache_image.putalpha(raw_image)
		else:
			cache_image = Image.new(IMAGE_RGBA, pixmap.size, '#000000')
			cache_image.putalpha(Image.new(IMAGE_GRAY, pixmap.size, 0))
	else:
		cache_image = cms.get_display_image(raw_image)

	if pixmap.alpha_channel:
		raw_alpha = b64decode(pixmap.alpha_channel)
		raw_alpha = Image.open(StringIO(raw_alpha))
		cache_image = cache_image.convert(IMAGE_RGBA)
		cache_image.putalpha(raw_alpha)

	if cache_image:
		cache_image.save(png_stream, format='PNG')

	png_stream.seek(0)
	pixmap.cache_cdata = cairo.ImageSurface.create_from_png(png_stream)

def update_gray_image(cms, image_obj):
	png_stream = StringIO()

	raw_image = Image.open(StringIO(b64decode(image_obj.bitmap)))
	raw_image.load()

	raw_image = raw_image.convert(IMAGE_GRAY)

	if image_obj.alpha_channel:
		raw_alpha = b64decode(image_obj.alpha_channel)
		raw_alpha = Image.open(StringIO(raw_alpha))
		rgb_image = raw_image.convert(IMAGE_RGBA)
		rgb_image.putalpha(raw_alpha)
	else:
		rgb_image = raw_image.convert(IMAGE_RGB)

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

def set_image_data(cms, pixmap, raw_content):
	alpha = ''
	profile, mode = extract_profile(raw_content)

	base_stream, alpha_stream = process_image(raw_content)
	base_image = Image.open(base_stream)
	base_image.load()

	pixmap.size = () + base_image.size
	if not base_image.mode in SUPPORTED_CS:
		base_image = base_image.convert(IMAGE_RGB)

	if not base_image.mode in SUPPORTED_CS[1:]:
		profile = mode = None

	if profile and base_image.mode == mode:
		base_image = cms.adjust_image(base_image, profile)

	pixmap.colorspace = '' + base_image.mode

	fobj = StringIO()
	base_image = base_image.copy()
	base_image.save(fobj, format='TIFF')
	bmp = b64encode(fobj.getvalue())

	style = deepcopy(pixmap.config.default_image_style)
	if base_image.mode in [IMAGE_RGB, IMAGE_LAB]:
		style[3] = deepcopy(pixmap.config.default_rgb_image_style)

	if alpha_stream:
		alpha_image = Image.open(alpha_stream)
		alpha_image.load()
		if alpha_image.mode == 'P':
			alpha_image = alpha_image.convert(IMAGE_RGBA)
		if alpha_image.mode in ['LA', IMAGE_RGBA]:
			if alpha_image.mode == 'LA':
				band = alpha_image.split()[1]
			else:
				band = alpha_image.split()[3]
			fobj = StringIO()
			band.save(fobj, format='TIFF')
			alpha = b64encode(fobj.getvalue())

	pixmap.bitmap = bmp
	pixmap.alpha_channel = alpha
	pixmap.style = style




