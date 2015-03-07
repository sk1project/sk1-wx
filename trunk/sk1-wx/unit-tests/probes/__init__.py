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

import os
from uc2.libimg import _libimg

_pkgdir = __path__[0]

def probe_number_images():
	filepath = os.path.join(_pkgdir, '3layer.gif')
	wand = _libimg.new_image()
	_libimg.load_image(wand, filepath)
	print _libimg.get_number_images(wand)

def probe_colorspace():
	paths = [
	"/home/igor/ws4/uniconvertor-2.x/trunk/src/unittests/_libimg_tests/img_data/cs_cmyk.tif",
	"/home/igor/ws4/uniconvertor-2.x/trunk/src/unittests/_libimg_tests/img_data/cs_grayscale.jpeg",
	"/home/igor/ws4/uniconvertor-2.x/trunk/src/unittests/_libimg_tests/img_data/cs_lab.tif",
	"/home/igor/ws4/uniconvertor-2.x/trunk/src/unittests/_libimg_tests/img_data/cs_rgb.png",
	"/home/igor/ws4/uniconvertor-2.x/trunk/src/unittests/_libimg_tests/img_data/cs_srgb.png",
		]
	for path in paths:
		wand = _libimg.new_image()
		_libimg.load_image(wand, path)
		_libimg.reset_iterator(wand)
		_libimg.next_image(wand)
		name = path.split('/')[-1]
		print name, '==>', _libimg.get_colorspace(wand)


