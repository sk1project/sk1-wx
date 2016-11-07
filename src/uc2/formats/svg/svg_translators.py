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

import math
from copy import deepcopy

from uc2 import uc2const, libgeom
from uc2.formats.sk2 import sk2_model, sk2_const
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
	layer = None
	trafo = []
	coeff = 1.0

	def translate(self, svg_doc, sk2_doc):
		self.svg_mt = svg_doc.model
		self.sk2_mt = sk2_doc.model
		self.sk2_mtds = sk2_doc.methods
		self.svg_mtds = svg_doc.methods
		self.translate_units()
		self.translate_page()
		for item in self.svg_mt.childs:
			self.translate_obj(self.layer, item, self.trafo)
		if len(self.page.childs) > 1 and not self.layer.childs:
			self.page.childs.remove(self.layer)
		self.sk2_mt.do_update()

	#--- Utility methods

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

	def trafo_skewX(self,):
		return [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]

	def trafo_skewY(self):
		return [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]

	def trafo_rotate(self, angle, cx=0.0, cy=0.0):
		trafo = [math.cos(angle), math.sin(angle),
			- math.sin(angle), math.cos(angle), 0.0, 0.0]
		if cx or cy:
			tr1 = [1.0, 0.0, 0.0, 1.0, -cx, -cy]
			tr2 = [1.0, 0.0, 0.0, 1.0, cx, cy]
			trafo = libgeom.multiply_trafo(tr1, trafo)
			trafo = libgeom.multiply_trafo(trafo, tr2)
		return trafo

	def trafo_scale(self, m11, m22=None):
		if m22 is None: m22 = m11
		return [m11, 0.0, 0.0, m22, 0.0, 0.0]

	def trafo_translate(self, dx, dy=0.0):
		return [1.0, 0.0, 0.0, 1.0, dx, dy]

	def trafo_matrix(self, m11, m21, m12, m22, dx, dy):
		return [m11, m21, m12, m22, dx, dy]

	def get_trafo(self, strafo):
		trafo = [] + sk2_const.NORMAL_TRAFO
		trs = strafo.split(' ')
		trs.reverse()
		for tr in trs:
			try:
				code = compile('tr=self.trafo_' + tr, '<string>', 'exec')
				exec code
			except: continue
			trafo = libgeom.multiply_trafo(trafo, tr)
		return trafo

	def get_level_trafo(self, svg_obj, trafo):
		tr = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
		if 'transform' in svg_obj.attrs:
			tr = self.get_trafo(str(svg_obj.attrs['transform']))
		tr = libgeom.multiply_trafo(tr, trafo)
		return tr

	#--- Translation metods

	def translate_units(self):
		units = SK2_UNITS[self.svg_mtds.doc_units()]
		if units == uc2const.UNIT_PX: self.coeff = 1.25
		self.sk2_mt.doc_units = units

	def translate_page(self):
		width = self.get_size_pt('210mm')
		height = self.get_size_pt('297mm')
		if 'width' in self.svg_mt.attrs:
			width = self.get_size_pt(self.svg_mt.attrs['width'])
			height = self.get_size_pt(self.svg_mt.attrs['height'])
		elif 'viewBox' in self.svg_mt.attrs:
			vbox = self.get_viewbox(self.svg_mt.attrs['viewBox'])
			width = vbox[2] - vbox[0]
			height = vbox[3] - vbox[1]
		ornt = uc2const.PORTRAIT
		if width > height: ornt = uc2const.LANDSCAPE
		page_fmt = ['Custom', (width, height), ornt]

		pages_obj = self.sk2_mtds.get_pages_obj()
		pages_obj.page_format = page_fmt
		self.page = sk2_model.Page(pages_obj.config, pages_obj, 'SVG page')
		self.page.page_format = deepcopy(page_fmt)
		pages_obj.childs = [self.page, ]
		pages_obj.page_counter = 1

		self.layer = sk2_model.Layer(self.page.config, self.page)
		self.page.childs = [self.layer, ]

		dx = -width / 2.0
		dy = height / 2.0
		xx = yy = 1.0
		if 'viewBox' in self.svg_mt.attrs:
			vbox = self.get_viewbox(self.svg_mt.attrs['viewBox'])
			dx = -width / 2.0 + vbox[0]
			dy = height / 2.0 + vbox[1]
			xx = width / (vbox[2] - vbox[0])
			yy = height / (vbox[3] - vbox[1])
		self.trafo = [xx, 0.0, 0.0, -yy, dx * xx, dy * yy]

	def translate_obj(self, parent, svg_obj, trafo):
		if svg_obj.tag == 'defs':
			self.translate_defs(svg_obj)
		elif svg_obj.tag == 'g':
			self.translate_g(parent, svg_obj, trafo)
		elif svg_obj.tag == 'rect':
			self.translate_rect(parent, svg_obj, trafo)


	def translate_defs(self, svg_obj):pass

	def translate_g(self, parent, svg_obj, trafo):
		if 'inkscape:groupmode' in svg_obj.attrs:
			if svg_obj.attrs['inkscape:groupmode'] == 'layer':
				name = 'Layer %d' % len(self.page.childs)
				if 'inkscape:label' in svg_obj.attrs:
					name = str(svg_obj.attrs['inkscape:label'])
				layer = sk2_model.Layer(self.page.config, self.page, name)
				self.page.childs.append(layer)
				tr = self.get_level_trafo(svg_obj, trafo)
				for item in svg_obj.childs:
					self.translate_obj(layer, item, tr)
		else:
			group = sk2_model.Group(parent.config, parent)
			tr = self.get_level_trafo(svg_obj, trafo)
			for item in svg_obj.childs:
				self.translate_obj(group, item, tr)
			if group.childs:
				parent.childs.append(group)

	def translate_rect(self, parent, svg_obj, trafo):
		x = self.get_size_pt(svg_obj.attrs['x'])
		y = self.get_size_pt(svg_obj.attrs['y'])
		w = self.get_size_pt(svg_obj.attrs['width'])
		h = self.get_size_pt(svg_obj.attrs['height'])
		cfg = parent.config
		style = deepcopy([cfg.default_fill, cfg.default_stroke, [], []])
		tr = self.get_level_trafo(svg_obj, trafo)
		rect = sk2_model.Rectangle(cfg, parent, [x, y, w, h], tr, style)
		parent.childs.append(rect)


class SK2_to_SVG_Translator(object):

	def translate(self, sk2_doc, svg_doc):pass
