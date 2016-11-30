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

import errno, sys
from struct import unpack
from copy import deepcopy

from uc2 import events, msgconst, uc2const, libgeom
from uc2.libgeom import multiply_trafo
from uc2.formats.wmf import wmfconst
from uc2.formats.sk2 import sk2_model

class WMF_to_SK2_Translator(object):

	def translate(self, wmf_doc, sk2_doc):
		self.wmf_doc = wmf_doc
		self.sk2_doc = sk2_doc
		self.wmf_mt = wmf_doc.model
		self.sk2_mt = sk2_doc.model
		self.sk2_mtds = sk2_doc.methods

		inch = wmfconst.META_DPI
		left = top = 0
		right = wmfconst.META_W
		bottom = wmfconst.META_H
		header = self.wmf_mt

		if self.wmf_mt.is_placeable():
			sig, handle, left, top, right, bottom, inch, rsvd, checksum\
				 = unpack(wmfconst.STRUCT_PLACEABLE, self.wmf_mt.chunk)

			val = 0
			for word in unpack('<10h', self.wmf_mt.chunk[:20]):
				val = val ^ word
			if val != checksum:
				msg = 'Incorrect header checksum'
				events.emit(events.MESSAGES, msgconst.ERROR, msg)
				raise IOError(errno.ENODATA, msg, '')

			header = self.wmf_mt.childs[0]

		self.inch = inch
		self.bbox = (left, top, right, bottom)

		self.coef = uc2const.in_to_pt / self.inch
		self.wx = self.vx = left
		self.vwidth = self.wwidth = right - left
		self.vheight = self.wheight = bottom - top
		self.wy = self.vy = top

		self.base_trafo = [self.coef, 0, 0, -self.coef,
						- self.coef * self.vwidth / 2.0,
						self.coef * self.vheight / 2.0]
		self.update_trafo()
		self.translate_header(header)

	def update_trafo(self):
		wt = [1.0, 0.0, 0.0, 1.0, -self.wx, -self.wy]
		vt = [1.0, 0.0, 0.0, 1.0, self.vx, self.vy]
		scale = [float(self.vwidth) / self.wwidth, 0.0, 0.0,
			float(self.vheight) / self.wheight, 0.0, 0.0]
		tr = multiply_trafo(vt, multiply_trafo(scale, wt))
		self.trafo = multiply_trafo(self.base_trafo, tr)

	def get_size_pt(self, val): return val * self.coef

	def translate_header(self, header):
		self.sk2_mt.doc_units = uc2const.UNIT_PT
		center = [0.0, 0.0]
		p = [self.wwidth, self.wheight]
		x0, y0 = libgeom.apply_trafo_to_point(center, self.trafo)
		x1, y1 = libgeom.apply_trafo_to_point(p, self.trafo)
		width = abs(x1 - x0)
		height = abs(y1 - y0)

		ornt = uc2const.PORTRAIT
		if width > height: ornt = uc2const.LANDSCAPE
		page_fmt = ['Custom', (width, height), ornt]
		print page_fmt

		pages_obj = self.sk2_mtds.get_pages_obj()
		pages_obj.page_format = page_fmt
		self.page = sk2_model.Page(pages_obj.config, pages_obj, 'WMF page')
		self.page.page_format = deepcopy(page_fmt)
		pages_obj.childs = [self.page, ]
		pages_obj.page_counter = 1

		self.layer = sk2_model.Layer(self.page.config, self.page)
		self.page.childs = [self.layer, ]

		for record in header.childs:
			self.translate_record(record)

	def translate_record(self, record):
		pass


class SK2_to_WMF_Translator(object):

	def translate(self, sk2_doc, wmf_doc):pass
