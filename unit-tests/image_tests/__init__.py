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

import unittest, os, shutil
import Image


_pkgdir = __path__[0]

MODES = ["1", "L", "P", "RGB", "RGBA", "CMYK", "YCbCr", "I", "F"]

FILES = ['type_bilevel.tif', 'type_cmyk.tif',
	'type_grayscale.tif', 'type_palette.tif',
	'type_truecolor.tif', 'type_truecolormatte.tif']

FILES2 = ['type_cmyka.tif', 'type_palettematte.tif', 'type_lab.tif', ]

class TestImageFunctions(unittest.TestCase):

	images = []
	save_dir = ''
	load_dir = ''

	def setUp(self):
		self.save_dir = os.path.join(_pkgdir, 'save_dir')
		self.load_dir = os.path.join(_pkgdir, 'image_data')

	def tearDown(self):pass
#		shutil.rmtree(self.save_dir)

	def test01_create_new_image(self):
		for mode in MODES:
			image = Image.new(mode, (100, 100))
			self.assertNotEquals(None, image)
			self.images.append(image)
		self.assertNotEquals(0, len(self.images))

	def test02_save_new_image(self):
		if os.path.lexists(self.save_dir): shutil.rmtree(self.save_dir)
		os.makedirs(self.save_dir)

		for image in self.images:
			result = False
			try:
				filename = 'TIFF-' + image.mode + '.tif'
				filename = os.path.join(self.save_dir, filename)
				image.save(filename)
				result = True
			except:
				result = False
			self.assertNotEquals(False, result)
		self.images = []
		shutil.rmtree(self.save_dir)

	def test03_load_images(self):
		for name in FILES:
			filename = os.path.join(self.load_dir, name)
			try:
				image = Image.open(filename)
				image.load()
				result = True
			except:
				result = False
			self.assertNotEquals(False, result)

	def test04_load_unsupported_images(self):
		for name in FILES2:
			filename = os.path.join(self.load_dir, name)
			try:
				image = Image.open(filename)
				image.load()
				result = True
			except:
				result = False
			self.assertNotEquals(True, result)
