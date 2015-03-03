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

from cStringIO import StringIO
from wand.image import Image

def check_image_file(path):
	try:
		Image(filename=path)
		return True
	except:
		return False

def process_image(raw_content):
	alpha = None
	img = Image(file=StringIO(raw_content))

	if img.alpha_channel:
		img_png = img.convert('png')
		img.alpha_channel = False
		alpha = StringIO()
		img_png.save(file=alpha)
		alpha.seek(0)

	base_img = img#.convert('tiff')
	base = StringIO()
	base_img.save(file=base)
	base.seek(0)
	return base, alpha

