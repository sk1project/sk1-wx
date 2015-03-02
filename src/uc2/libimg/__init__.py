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

import cStringIO, base64, sys
import cairo
from PIL import Image

def check_image(path):
	try:
		Image.open(path)
		return True
	except:
		return False

def update_image(cms, image_obj):

	png_data = cStringIO.StringIO()

	if not image_obj.cache_image:
		raw_content = base64.b64decode(image_obj.bitmap)
		raw_image = Image.open(cStringIO.StringIO(raw_content))
		raw_image.load()

		if raw_image.mode == 'RGB':
			image_obj.cache_image = raw_image
		else:
			image_obj.cache_image = raw_image.convert('RGB')

		if image_obj.alpha_channel:
			raw_alpha = base64.b64decode(image_obj.alpha_channel)
			raw_alpha = Image.open(cStringIO.StringIO(raw_alpha))
			image_obj.cache_image = image_obj.cache_image.convert('RGBA')
			image_obj.cache_image.putalpha(raw_alpha)


	image_obj.cache_image.save(png_data, format='PNG')

	png_data.seek(0)
	image_obj.cache_cdata = cairo.ImageSurface.create_from_png(png_data)

def update_gray_image(cms, image_obj):

	png_data = cStringIO.StringIO()

	raw_content = base64.b64decode(image_obj.bitmap)
	raw_image = Image.open(cStringIO.StringIO(raw_content))
	raw_image.load()

	raw_image = raw_image.convert('L')

	if image_obj.alpha_channel:
		raw_alpha = base64.b64decode(image_obj.alpha_channel)
		raw_alpha = Image.open(cStringIO.StringIO(raw_alpha))
		rgb_image = raw_image.convert('RGBA')
		rgb_image.putalpha(raw_alpha)
	else:
		rgb_image = raw_image.convert('RGB')

	rgb_image.save(png_data, format='PNG')

	png_data.seek(0)
	image_obj.cache_gray_cdata = cairo.ImageSurface.create_from_png(png_data)


def set_image_data(cms, image_obj, raw_content):
	bmp = ''
	alpha = ''
	raw_image = Image.open(cStringIO.StringIO(raw_content))
	raw_image.load()

	image_obj.size = () + raw_image.size
	if raw_image.mode in ['YCbCr', 'P', 'I', 'F']:
		raw_image = raw_image.convert('RGB')

	if raw_image.mode == 'RGBA':
		bands = raw_image.split()
		fobj = cStringIO.StringIO()
		bands[3].save(fobj, format='PNG')
		alpha = base64.b64encode(fobj.getvalue())

		fobj = cStringIO.StringIO()
		bmp = Image.merge('RGB', bands[:3])
		bmp.save(fobj, format='PNG')
		bmp = base64.b64encode(fobj.getvalue())
	else:
		bmp = base64.b64encode(raw_content)

	image_obj.cache_image = raw_image
	image_obj.bitmap = bmp
	image_obj.alpha_channel = alpha
	update_image(cms, image_obj)




