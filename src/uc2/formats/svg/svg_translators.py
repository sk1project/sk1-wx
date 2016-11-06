# -*- coding: utf-8 -*-
#
# 	 Copyright (C) 2016 by Igor E. Novikov
#
# 	 This program is free software: you can redistribute it and/or modify
# 	 it under the terms of the GNU General Public License as published by
# 	 the Free Software Foundation, either version 3 of the License, or
# 	 (at your option) any later version.
#
# 	 This program is distributed in the hope that it will be useful,
# 	 but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	 GNU General Public License for more details.
#
# 	 You should have received a copy of the GNU General Public License
# 	 along with this program.  If not, see <http://www.gnu.org/licenses/>.

from copy import deepcopy

from uc2 import uc2const
from uc2.formats.sk2 import sk2_model
from uc2.formats.svg import svg_const

SK2_UNITS = {
svg_const.SVG_PX:uc2const.UNIT_PX,
svg_const.SVG_PC:uc2const.UNIT_PX,
svg_const.SVG_PT:uc2const.UNIT_PT,
svg_const.SVG_MM:uc2const.UNIT_MM,
svg_const.SVG_CM:uc2const.UNIT_CM,
svg_const.SVG_M:uc2const.UNIT_M,
svg_const.SVG_IN:uc2const.UNIT_IN,
svg_const.SVG_FT:uc2const.UNIT_FT,
}

class SVG_to_SK2_Translator(object):

	page = None
	trafo = []
	coeff = 1.0

	def _px_to_pt(self, sval):
		return svg_const.svg_px_to_pt * float(sval)

	def get_size_pt(self, sval):
		if not sval: return None
		if len(sval) == 1:
			if sval.isdigit():
				return self._px_to_pt(sval) * self.coeff
			return None
		if sval[-1].isdigit():
			return self._px_to_pt(sval) * self.coeff
		else:
			unit = sval[-2:]
			sval = sval[:-2]
			if unit == 'px':
				return self._px_to_pt(sval) * self.coeff
			elif unit == 'pc':
				return 15.0 * self._px_to_pt(sval) * self.coeff
			elif unit == 'mm':
				return uc2const.mm_to_pt * float(sval) * self.coeff
			elif unit == 'cm':
				return uc2const.cm_to_pt * float(sval) * self.coeff
			elif unit == 'in':
				return uc2const.in_to_pt * float(sval) * self.coeff
			else:
				return self._px_to_pt(sval) * self.coeff

	def get_viewbox(self, svbox):
		vbox = []
		for item in svbox.split(' '):
			vbox.append(self.get_size_pt(item))
		return vbox

	def translate(self, svg_doc, sk2_doc):
		self.svg_mt = svg_doc.model
		self.sk2_mt = sk2_doc.model
		self.sk2_mtds = sk2_doc.methods
		self.svg_mtds = svg_doc.methods
		self.translate_units()
		self.translate_page()

	def translate_units(self):
		units = SK2_UNITS[self.svg_mtds.doc_units()]
		if units == uc2const.UNIT_PX: self.coeff = 1.25
		self.sk2_mt.doc_units = units

	def translate_page(self):
		width = self.get_size_pt('210mm')
		height = self.get_size_pt('297mm')
		if 'width' in self.svg_mt.attrs:
			width = self.get_size_pt(self.svg_mt.attrs['width'])
		if 'height' in self.svg_mt.attrs:
			height = self.get_size_pt(self.svg_mt.attrs['height'])
		ornt = uc2const.PORTRAIT
		if width > height: ornt = uc2const.LANDSCAPE
		page_fmt = ['Custom', (width, height), ornt]

		pages_obj = self.sk2_mtds.get_pages_obj()
		pages_obj.page_format = page_fmt
		self.page = sk2_model.Page(pages_obj.config, pages_obj, 'SVG page')
		self.page.page_format = deepcopy(page_fmt)
		pages_obj.childs = [self.page, ]
		pages_obj.page_counter = 1

		layer = sk2_model.Layer(self.page.config, self.page)
		self.page.childs = [layer, ]

		vbox = self.get_viewbox(self.svg_mt.attrs['viewBox'])
		dx = -width / 2.0 + vbox[0]
		dy = -height / 2.0 + vbox[1]
		self.trafo = [1.0, 0.0, 0.0, -1.0, dx, dy]


class SK2_to_SVG_Translator(object):

	def translate(self, sk2_doc, svg_doc):pass
