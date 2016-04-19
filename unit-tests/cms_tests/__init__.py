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

import unittest, os
from PIL import Image

from uc2 import uc2const
from uc2.cms import libcms

_pkgdir = __path__[0]

def get_filepath(filename):
	return os.path.join(_pkgdir, 'cms_data', filename)

class TestCmsFunctions(unittest.TestCase):

	def setUp(self):
		rgb_profile = get_filepath('sRGB.icm')
		self.inProfile = libcms.cms_open_profile_from_file(rgb_profile)
		cmyk_profile = get_filepath('GenericCMYK.icm')
		self.outProfile = libcms.cms_open_profile_from_file(cmyk_profile)
		self.transform = libcms.cms_create_transform(self.inProfile,
						uc2const.TYPE_RGBA_8, self.outProfile, uc2const.TYPE_CMYK_8,
						uc2const.INTENT_PERCEPTUAL, uc2const.cmsFLAGS_NOTPRECALC)
		self.transform2 = libcms.cms_create_transform(self.inProfile,
						uc2const.TYPE_RGBA_8, self.outProfile, uc2const.TYPE_CMYK_8,
						uc2const.INTENT_PERCEPTUAL, 0)


	def tearDown(self):
		pass

	#---Profile management tests

# 	def test01_open_profile(self):
# 		self.assertNotEqual(None, self.inProfile)
# 		self.assertNotEqual(None, self.outProfile)
#  		self.assertNotEqual(None, libcms.cms_create_srgb_profile())
#  		self.assertNotEqual(None, libcms.cms_create_cmyk_profile())
#  		self.assertNotEqual(None, libcms.cms_create_lab_profile())
#  		self.assertNotEqual(None, libcms.cms_create_gray_profile())

	def test02_open_invalid_profile(self):
		try:
			profile = get_filepath('empty.icm')
			libcms.cms_open_profile_from_file(profile)
		except libcms.CmsError:
			return
		self.fail()

	def test03_open_absent_profile(self):
		try:
			profile = get_filepath('xxx.icm')
			libcms.cms_open_profile_from_file(profile)
		except libcms.CmsError:
			return
		self.fail()

	#---Transform related tests

	def test04_create_transform(self):
		self.assertNotEqual(None, libcms.cms_create_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.outProfile, uc2const.TYPE_CMYK_8))
		self.assertNotEqual(None, libcms.cms_create_transform(self.inProfile,
				uc2const.TYPE_RGBA_8, self.outProfile, uc2const.TYPE_CMYK_8))
		self.assertNotEqual(None, libcms.cms_create_transform(self.outProfile,
				uc2const.TYPE_CMYK_8, self.inProfile, uc2const.TYPE_RGBA_8))
		self.assertNotEqual(None, libcms.cms_create_transform(self.outProfile,
				uc2const.TYPE_CMYK_8, self.inProfile, uc2const.TYPE_RGB_8))

	def test05_create_transform_with_custom_intent(self):
		self.assertNotEqual(None, libcms.cms_create_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.outProfile, uc2const.TYPE_CMYK_8,
				uc2const.INTENT_PERCEPTUAL))
		self.assertNotEqual(None, libcms.cms_create_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.outProfile, uc2const.TYPE_CMYK_8,
				uc2const.INTENT_RELATIVE_COLORIMETRIC))
		self.assertNotEqual(None, libcms.cms_create_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.outProfile, uc2const.TYPE_CMYK_8,
				uc2const.INTENT_SATURATION))
		self.assertNotEqual(None, libcms.cms_create_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.outProfile, uc2const.TYPE_CMYK_8,
				uc2const.INTENT_ABSOLUTE_COLORIMETRIC))

	def test06_create_transform_with_custom_flags(self):
		self.assertNotEqual(None, libcms.cms_create_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.outProfile, uc2const.TYPE_CMYK_8,
				uc2const.INTENT_PERCEPTUAL,
				uc2const.cmsFLAGS_NOTPRECALC | uc2const.cmsFLAGS_GAMUTCHECK))
		self.assertNotEqual(None, libcms.cms_create_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.outProfile, uc2const.TYPE_CMYK_8,
				uc2const.INTENT_PERCEPTUAL,
				uc2const.cmsFLAGS_PRESERVEBLACK | uc2const.cmsFLAGS_BLACKPOINTCOMPENSATION))
		self.assertNotEqual(None, libcms.cms_create_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.outProfile, uc2const.TYPE_CMYK_8,
				uc2const.INTENT_PERCEPTUAL,
				uc2const.cmsFLAGS_NOTPRECALC | uc2const.cmsFLAGS_HIGHRESPRECALC))
		self.assertNotEqual(None, libcms.cms_create_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.outProfile, uc2const.TYPE_CMYK_8,
				uc2const.INTENT_PERCEPTUAL,
				uc2const.cmsFLAGS_NOTPRECALC | uc2const.cmsFLAGS_LOWRESPRECALC))

	def test07_create_transform_with_invalid_intent(self):
		self.assertNotEqual(None, libcms.cms_create_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.outProfile, uc2const.TYPE_CMYK_8, 3))
		try:
			libcms.cms_create_transform(self.inProfile, uc2const.TYPE_RGB_8,
									self.outProfile, uc2const.TYPE_CMYK_8, 4)
		except libcms.CmsError:
			return
		self.fail()

	#---Proof transform related tests

	def test08_create_proofing_transform(self):
		self.assertNotEqual(None, libcms.cms_create_proofing_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.inProfile, uc2const.TYPE_RGB_8, self.outProfile))
		self.assertNotEqual(None, libcms.cms_create_proofing_transform(self.inProfile,
				uc2const.TYPE_RGBA_8, self.inProfile, uc2const.TYPE_RGB_8, self.outProfile))
		self.assertNotEqual(None, libcms.cms_create_proofing_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.inProfile, uc2const.TYPE_RGBA_8, self.outProfile))
		self.assertNotEqual(None, libcms.cms_create_proofing_transform(self.inProfile,
				uc2const.TYPE_RGBA_8, self.inProfile, uc2const.TYPE_RGBA_8, self.outProfile))

	def test09_create_proofing_transform_with_custom_intent(self):
		self.assertNotEqual(None, libcms.cms_create_proofing_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.inProfile, uc2const.TYPE_RGB_8, self.outProfile,
				uc2const.INTENT_PERCEPTUAL))
		self.assertNotEqual(None, libcms.cms_create_proofing_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.inProfile, uc2const.TYPE_RGB_8, self.outProfile,
				uc2const.INTENT_RELATIVE_COLORIMETRIC))
		self.assertNotEqual(None, libcms.cms_create_proofing_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.inProfile, uc2const.TYPE_RGB_8, self.outProfile,
				uc2const.INTENT_SATURATION))
		self.assertNotEqual(None, libcms.cms_create_proofing_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.inProfile, uc2const.TYPE_RGB_8, self.outProfile,
				uc2const.INTENT_ABSOLUTE_COLORIMETRIC))

	def test10_create_proofing_transform_with_custom_proofing_intent(self):
		self.assertNotEqual(None, libcms.cms_create_proofing_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.inProfile, uc2const.TYPE_RGB_8, self.outProfile,
				uc2const.INTENT_PERCEPTUAL, uc2const.INTENT_PERCEPTUAL))
		self.assertNotEqual(None, libcms.cms_create_proofing_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.inProfile, uc2const.TYPE_RGB_8, self.outProfile,
				uc2const.INTENT_PERCEPTUAL, uc2const.INTENT_RELATIVE_COLORIMETRIC))
		self.assertNotEqual(None, libcms.cms_create_proofing_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.inProfile, uc2const.TYPE_RGB_8, self.outProfile,
				uc2const.INTENT_PERCEPTUAL, uc2const.INTENT_SATURATION))
		self.assertNotEqual(None, libcms.cms_create_proofing_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.inProfile, uc2const.TYPE_RGB_8, self.outProfile,
				uc2const.INTENT_PERCEPTUAL, uc2const.INTENT_ABSOLUTE_COLORIMETRIC))

	def test11_create_proofing_transform_with_custom_flags(self):
		self.assertNotEqual(None, libcms.cms_create_proofing_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.inProfile, uc2const.TYPE_RGB_8, self.outProfile,
				uc2const.INTENT_PERCEPTUAL, uc2const.INTENT_RELATIVE_COLORIMETRIC,
				uc2const.cmsFLAGS_NOTPRECALC | uc2const.cmsFLAGS_GAMUTCHECK))
		self.assertNotEqual(None, libcms.cms_create_proofing_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.inProfile, uc2const.TYPE_RGB_8, self.outProfile,
				uc2const.INTENT_PERCEPTUAL, uc2const.INTENT_RELATIVE_COLORIMETRIC,
				uc2const.cmsFLAGS_PRESERVEBLACK | uc2const.cmsFLAGS_BLACKPOINTCOMPENSATION))
		self.assertNotEqual(None, libcms.cms_create_proofing_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.inProfile, uc2const.TYPE_RGB_8, self.outProfile,
				uc2const.INTENT_PERCEPTUAL, uc2const.INTENT_RELATIVE_COLORIMETRIC,
				uc2const.cmsFLAGS_NOTPRECALC | uc2const.cmsFLAGS_HIGHRESPRECALC))
		self.assertNotEqual(None, libcms.cms_create_proofing_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.inProfile, uc2const.TYPE_RGB_8, self.outProfile,
				uc2const.INTENT_PERCEPTUAL, uc2const.INTENT_RELATIVE_COLORIMETRIC,
				uc2const.cmsFLAGS_NOTPRECALC | uc2const.cmsFLAGS_LOWRESPRECALC))

	def test12_create_proofing_transform_with_invalid_intent(self):
		self.assertNotEqual(None, libcms.cms_create_proofing_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.inProfile, uc2const.TYPE_RGB_8, self.outProfile, 3))
		try:
			libcms.cms_create_proofing_transform(self.inProfile, uc2const.TYPE_RGB_8,
				self.inProfile, uc2const.TYPE_RGB_8, self.outProfile, 4)
		except libcms.CmsError:
			return
		self.fail()

	def test13_create_proofing_transform_with_invalid_proofing_intent(self):
		self.assertNotEqual(None, libcms.cms_create_proofing_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.inProfile, uc2const.TYPE_RGB_8, self.outProfile, 1, 2))
		try:
			libcms.cms_create_proofing_transform(self.inProfile,
				uc2const.TYPE_RGB_8, self.inProfile, uc2const.TYPE_RGB_8, self.outProfile, 1, 4)
		except libcms.CmsError:
			return
		self.fail()

	#---Alarmcodes related tests

	def test14_set_alarm_codes_with_null_values(self):
		try:
			libcms.cms_set_alarm_codes(0, 1, 1)
			libcms.cms_set_alarm_codes(1, 0, 1)
			libcms.cms_set_alarm_codes(1, 1, 0)
		except libcms.CmsError:
			self.fail()

	def test15_set_alarm_codes_with_lagest_values(self):
		try:
			libcms.cms_set_alarm_codes(0, 255, 255)
			libcms.cms_set_alarm_codes(255, 0, 255)
			libcms.cms_set_alarm_codes(255, 255, 0)
		except libcms.CmsError:
			self.fail()

	def test16_set_alarm_codes_with_incorrect_values(self):
		counter = 0
		try:
			libcms.cms_set_alarm_codes(256, 255, 255)
		except libcms.CmsError:
			counter += 1

		try:
			libcms.cms_set_alarm_codes(0, 256, 255)
		except libcms.CmsError:
			counter += 1

		try:
			libcms.cms_set_alarm_codes(0, 255, 256)
		except libcms.CmsError:
			counter += 1

		try:
			libcms.cms_set_alarm_codes(-1, 255, 255)
		except libcms.CmsError:
			counter += 1

		try:
			libcms.cms_set_alarm_codes(255, -1, 255)
		except libcms.CmsError:
			counter += 1

		try:
			libcms.cms_set_alarm_codes(255, 255, -1)
		except libcms.CmsError:
			counter += 1

		try:
			libcms.cms_set_alarm_codes(255, 255, .1)
		except libcms.CmsError:
			counter += 1

		try:
			libcms.cms_set_alarm_codes(255, .1, 255)
		except libcms.CmsError:
			counter += 1

		try:
			libcms.cms_set_alarm_codes(.1, 255, 255)
		except libcms.CmsError:
			counter += 1

		try:
			libcms.cms_set_alarm_codes("#fff", "#fff", "#fff")
		except libcms.CmsError:
			counter += 1

		self.assertEqual(counter, 10)

	#---Color transformation related tests

	def test17_do_transform_with_null_input(self):
		rgb = libcms.COLORB()
		cmyk = libcms.COLORB()
		libcms.cms_do_transform(self.transform, rgb, cmyk)
		self.assertNotEqual(0, cmyk[0])
		self.assertNotEqual(0, cmyk[1])
		self.assertNotEqual(0, cmyk[2])
		self.assertNotEqual(0, cmyk[3])

	def test18_do_transform_with_maximum_allowed_input(self):
		rgb = libcms.COLORB()
		cmyk = libcms.COLORB()
		rgb[0] = 255
		rgb[1] = 255
		rgb[2] = 255
		libcms.cms_do_transform(self.transform, rgb, cmyk)
		self.assertEqual(0, cmyk[0])
		self.assertEqual(0, cmyk[1])
		self.assertEqual(0, cmyk[2])
		self.assertEqual(0, cmyk[3])

	def test19_do_transform_with_intermediate_input(self):
		rgb = libcms.COLORB()
		cmyk = libcms.COLORB()
		rgb[0] = 100
		rgb[1] = 190
		rgb[2] = 150
		libcms.cms_do_transform(self.transform, rgb, cmyk)
		self.assertNotEqual(0, cmyk[0])
		self.assertNotEqual(0, cmyk[1])
		self.assertNotEqual(0, cmyk[2])
		self.assertNotEqual(0, cmyk[3])

	def test20_do_transform_with_incorrect_color_values(self):
		rgb = libcms.COLORB()
		cmyk = libcms.COLORB()
		rgb[0] = 455
		rgb[1] = 255
		rgb[2] = 255
		try:
			libcms.cms_do_transform(self.transform, rgb, cmyk)
		except:
			self.fail()


	def test21_do_transform_with_incorrect_input_buffer(self):
		cmyk = libcms.COLORB()
		rgb = 255
		try:
			libcms.cms_do_transform(self.transform, rgb, cmyk)
		except libcms.CmsError:
			return
		self.fail()

	def test22_do_transform_with_incorrect_output_buffer(self):
		rgb = libcms.COLORB()
		rgb[0] = 255
		rgb[1] = 255
		rgb[2] = 255
		cmyk = 255
		try:
			libcms.cms_do_transform(self.transform, rgb, cmyk)
		except libcms.CmsError:
			return
		self.fail()

	#---Pixmap related tests

	def test23_do_transform2_with_null_input(self):
		cmyk = libcms.cms_do_transform2(self.transform, 0, 0, 0)
		self.assertNotEqual(0, cmyk[0])
		self.assertNotEqual(0, cmyk[1])
		self.assertNotEqual(0, cmyk[2])
		self.assertNotEqual(0, cmyk[3])

	def test24_do_transform2_with_maximal_allowed_input(self):
		cmyk = libcms.cms_do_transform2(self.transform, 1, 1, 1)
		self.assertEqual(0, cmyk[0])
		self.assertEqual(0, cmyk[1])
		self.assertEqual(0, cmyk[2])
		self.assertEqual(0, cmyk[3])

	def test25_do_transform2_with_intermediate_input(self):
		cmyk = libcms.cms_do_transform2(self.transform, .392, .745, .588)
		self.assertNotEqual(0, cmyk[0])
		self.assertNotEqual(0, cmyk[1])
		self.assertNotEqual(0, cmyk[2])
		self.assertNotEqual(0, cmyk[3])

	#---Bitmap related tests

	def test26_DoBitmapTransform(self):
		inImage = Image.open(get_filepath('black100x100.png'))
		pixel = inImage.getpixel((1, 1))
		self.assertEqual(3, len(pixel))
		outImage = libcms.cms_do_bitmap_transform(self.transform2,
							inImage, uc2const.TYPE_RGB_8, uc2const.TYPE_CMYK_8)
		pixel = outImage.getpixel((1, 1))
		self.assertEqual(4, len(pixel))

		inImage = Image.open(get_filepath('white100x100.png'))
		pixel = inImage.getpixel((1, 1))
		self.assertEqual(3, len(pixel))
		outImage = libcms.cms_do_bitmap_transform(self.transform2,
							inImage, uc2const.TYPE_RGB_8, uc2const.TYPE_CMYK_8)
		pixel = outImage.getpixel((1, 1))
		self.assertEqual(4, len(pixel))

		inImage = Image.open(get_filepath('color100x100.png'))
		pixel = inImage.getpixel((1, 1))
		self.assertEqual(3, len(pixel))
		outImage = libcms.cms_do_bitmap_transform(self.transform2,
							inImage, uc2const.TYPE_RGB_8, uc2const.TYPE_CMYK_8)
		pixel = outImage.getpixel((1, 1))
		self.assertEqual(4, len(pixel))

	def test27_DoBitmapTransformWithUnsupportedImage(self):
		inImage = Image.open(get_filepath('black100x100.png'))
		inImage.load()
		inImage = inImage.convert("YCbCr")
		try:
			outImage = libcms.cms_do_bitmap_transform(self.transform2,
							inImage, uc2const.TYPE_RGB_8, uc2const.TYPE_CMYK_8)
		except libcms.CmsError:
			return
		self.fail()

	def test28_DoBitmapTransformWithUnsupportedInMode(self):
		inImage = Image.open(get_filepath('black100x100.png'))
		try:
			outImage = libcms.cms_do_bitmap_transform(self.transform2,
							inImage, "YCbCr", uc2const.TYPE_CMYK_8)
		except libcms.CmsError:
			return
		self.fail()

	def test29_DoBitmapTransformWithUnsupportedOutMode(self):
		inImage = Image.open(get_filepath('black100x100.png'))
		try:
			outImage = libcms.cms_do_bitmap_transform(self.transform2,
							inImage, uc2const.TYPE_RGB_8, "YCbCr")
		except libcms.CmsError:
			return
		self.fail()

	#---Profile info related tests

	def test30_get_profile_name(self):
		name = libcms.cms_get_profile_name(self.outProfile)
		self.assertEqual(name, 'Fogra27L CMYK Coated Press')

	def test31_get_profile_info(self):
		name = libcms.cms_get_profile_info(self.outProfile)
		self.assertEqual(name[:15], 'Offset printing')

	def test32_get_profile_copyright(self):
		name = libcms.cms_get_profile_copyright(self.outProfile)
		if os.name=='nt':
			self.assertEqual(name, '')
		else:
			self.assertEqual(name, 'Public Domain')

	#---Embedded profile related tests
	def test33_get_embedded_profile(self):
		img = Image.open(get_filepath('CustomRGB.jpg'))
		profile = img.info.get('icc_profile')
		try:
			custom_profile = libcms.cms_open_profile_from_string(profile)
			transform = libcms.cms_create_transform(custom_profile,
							uc2const.TYPE_RGB_8, self.inProfile, uc2const.TYPE_RGB_8,
							uc2const.INTENT_PERCEPTUAL, uc2const.cmsFLAGS_NOTPRECALC)
			img2 = libcms.cms_do_bitmap_transform(transform,
										img, uc2const.TYPE_RGB_8, uc2const.TYPE_RGB_8)
		except libcms.CmsError:
			self.fail()


