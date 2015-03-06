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
from base64 import b64decode, b64encode
from cStringIO import StringIO
from PIL import Image

from uc2.libimg.imwand import check_image_file, process_image

def check_image(path):
	return check_image_file

def update_image(cms, image_obj):

	png_data = StringIO()

	if not image_obj.cache_image:
		raw_content = b64decode(image_obj.bitmap)
		raw_image = Image.open(StringIO(raw_content))
		raw_image.load()

		image_obj.cache_image = cms.get_display_image(raw_image)

		if image_obj.alpha_channel:
			raw_alpha = b64decode(image_obj.alpha_channel)
			raw_alpha = Image.open(StringIO(raw_alpha))
			image_obj.cache_image = image_obj.cache_image.convert('RGBA')
			image_obj.cache_image.putalpha(raw_alpha)


	image_obj.cache_image.save(png_data, format='PNG')

	png_data.seek(0)
	image_obj.cache_cdata = cairo.ImageSurface.create_from_png(png_data)

def update_gray_image(cms, image_obj):

	png_data = StringIO()

	raw_content = b64decode(image_obj.bitmap)
	raw_image = Image.open(StringIO(raw_content))
	raw_image.load()

	raw_image = raw_image.convert('L')

	if image_obj.alpha_channel:
		raw_alpha = b64decode(image_obj.alpha_channel)
		raw_alpha = Image.open(StringIO(raw_alpha))
		rgb_image = raw_image.convert('RGBA')
		rgb_image.putalpha(raw_alpha)
	else:
		rgb_image = raw_image.convert('RGB')

	rgb_image.save(png_data, format='PNG')

	png_data.seek(0)
	image_obj.cache_gray_cdata = cairo.ImageSurface.create_from_png(png_data)

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
		profile = mode = None

	image_obj.colorspace = '' + base_image.mode

	fobj = StringIO()
	if base_image.mode == 'CMYK':
		bmp = b64encode(base_stream.getvalue())
	else:
		base_image.save(fobj, format='PNG')
		bmp = b64encode(fobj.getvalue())

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




