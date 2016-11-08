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

from uc2 import uc2const, libgeom, cms
from uc2.formats.sk2 import sk2_model, sk2_const
from uc2.formats.svg import svg_const, svg_colors

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

SVG_STYLE = {
	'opacity':'1',
	'fill':'black',
	'fill-rule':'nonzero',
	'fill-opacity':'1',
	'stroke':'none',
	'stroke-width':'1',
	'stroke-linecap':'butt',
	'stroke-linejoin':'miter',
	'stroke-miterlimit':'4',
	'stroke-dasharray':'none',
	'stroke-dashoffset':'0',
	'stroke-opacity':'1',
}

STYLE_ATTRS = ['fill', 'fill-rule', 'fill-opacity', 'stroke', 'stroke-width',
			'stroke-linecap', 'stroke-linejoin', 'stroke-miterlimit',
			'stroke-dasharray', 'stroke-dashoffset', 'stroke-opacity', ]

SK2_FILL_RULE = {
	'nonzero':sk2_const.FILL_NONZERO,
	'evenodd':sk2_const.FILL_EVENODD,
}

SK2_LINE_JOIN = {
	'miter':sk2_const.JOIN_MITER,
	'round':sk2_const.JOIN_ROUND,
	'bevel':sk2_const.JOIN_BEVEL,
}

SK2_LINE_CAP = {
	'butt':sk2_const.CAP_BUTT,
	'round':sk2_const.CAP_ROUND,
	'square':sk2_const.CAP_SQUARE,
}

class SVG_to_SK2_Translator(object):

	page = None
	layer = None
	defs = None
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
			self.translate_obj(self.layer, item, self.trafo, SVG_STYLE)
		if len(self.page.childs) > 1 and not self.layer.childs:
			self.page.childs.remove(self.layer)
		self.sk2_mt.do_update()

	#--- Utility methods

	def check_attr(self, svg_obj, attr, value):
		if attr in svg_obj.attrs and  svg_obj.attrs[attr] == value:
			return True
		return False

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

	# TODO: implement skew trafo
	def trafo_skewX(self,):
		return [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]

	def trafo_skewY(self):
		return [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]

	def trafo_rotate(self, angle, cx=0.0, cy=0.0):
		angle = angle / 180.0
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
		trs = strafo.split(') ')
		trs.reverse()
		for tr in trs:
			tr += ')'
			tr = tr.replace(', ', ',').replace(' ', ',').replace('))', ')')
			try:
				print tr
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

	def get_level_style(self, svg_obj, style):
		style = deepcopy(style)
		for item in STYLE_ATTRS:
			if item in svg_obj.attrs:
				style[item] = '' + str(svg_obj.attrs[item])
		if 'style' in svg_obj.attrs:
			stls = str(svg_obj.attrs['style']).split(';')
			for stl in stls:
				vals = stl.split(':')
				if len(vals) == 2:
					style[vals[0]] = vals[1]
		return style

	def get_sk2_style(self, svg_obj, style):
		sk2_style = [[], [], [], []]
		style = self.get_level_style(svg_obj, style)

		# fill parsing
		if not style['fill'] == 'none':
			fillrule = SK2_FILL_RULE[style['fill-rule']]
			fill = style['fill']
			if len(fill) > 3 and fill[:3] == 'url':
				# TODO: implement defs parsing
				pass
			else:
				fill = fill.split(' ')[0]
				alpha = float(style['fill-opacity']) * float(style['opacity'])
				if fill[0] == '#':
					vals = cms.hexcolor_to_rgb(fill)
					clr = ['RGB', vals, alpha, '']
					sk2_style[0] = [fillrule, sk2_const.FILL_SOLID, clr]
				else:
					if fill in svg_colors.SVG_COLORS:
						clr = deepcopy(svg_colors.SVG_COLORS[fill])
						clr[2] = alpha
						sk2_style[0] = [fillrule, sk2_const.FILL_SOLID, clr]

		# stroke parsing
		if not style['stroke'] == 'none':
			stroke = style['stroke']
			stroke_rule = sk2_const.STROKE_MIDDLE
			stroke_width = self.get_size_pt(style['stroke-width'])
			stroke_linecap = SK2_LINE_CAP[style['stroke-linecap']]
			stroke_linejoin = SK2_LINE_JOIN[style['stroke-linejoin']]
			stroke_miterlimit = float(style['stroke-miterlimit'])

			dash = []
			if not style['stroke-dasharray'] == 'none':
				try:
					code = compile('dash=[' + style['stroke-dasharray'] + ']',
								'<string>', 'exec')
					exec code
				except: dash = []
			if dash:
				sk2_dash = []
				for item in dash: sk2_dash.append(item / stroke_width)
				dash = sk2_dash

			if len(stroke) > 3 and stroke[:3] == 'url':
				pass
			else:
				clr = []
				stroke = stroke.split(' ')[0]
				alpha = float(style['stroke-opacity']) * float(style['opacity'])
				if stroke[0] == '#':
					vals = cms.hexcolor_to_rgb(stroke)
					clr = ['RGB', vals, alpha, '']
				elif stroke in svg_colors.SVG_COLORS:
					clr = deepcopy(svg_colors.SVG_COLORS[stroke])
					clr[2] = alpha
				if clr:
					sk2_style[1] = [stroke_rule, stroke_width, clr, dash,
							stroke_linecap, stroke_linejoin,
							stroke_miterlimit, 0, 1, []]

		return sk2_style

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
		self.trafo = [1.0, 0.0, 0.0, -1.0, dx, dy]
		if 'viewBox' in self.svg_mt.attrs:
			vbox = self.get_viewbox(self.svg_mt.attrs['viewBox'])
			dx = vbox[0]
			dy = vbox[1]
			xx = width / (vbox[2] - vbox[0])
			yy = height / (vbox[3] - vbox[1])
			tr = [xx, 0.0, 0.0, yy, dx, dy]
			self.trafo = libgeom.multiply_trafo(tr, self.trafo)

	def translate_obj(self, parent, svg_obj, trafo, style):
		if svg_obj.tag == 'defs':
			self.translate_defs(svg_obj)
		elif svg_obj.tag == 'g':
			self.translate_g(parent, svg_obj, trafo, style)
		elif svg_obj.tag == 'rect':
			self.translate_rect(parent, svg_obj, trafo, style)
		elif svg_obj.tag == 'circle':
			self.translate_circle(parent, svg_obj, trafo, style)
		elif svg_obj.tag == 'ellipse':
			self.translate_ellipse(parent, svg_obj, trafo, style)
		elif svg_obj.tag == 'path':
			self.translate_path(parent, svg_obj, trafo, style)
		elif svg_obj.tag == 'line':
			self.translate_line(parent, svg_obj, trafo, style)


	def translate_defs(self, svg_obj):pass

	def translate_g(self, parent, svg_obj, trafo, style):
		if 'inkscape:groupmode' in svg_obj.attrs:
			if svg_obj.attrs['inkscape:groupmode'] == 'layer':
				name = 'Layer %d' % len(self.page.childs)
				if 'inkscape:label' in svg_obj.attrs:
					name = str(svg_obj.attrs['inkscape:label'])
				layer = sk2_model.Layer(self.page.config, self.page, name)
				self.page.childs.append(layer)
				if self.check_attr(svg_obj, 'sodipodi:insensitive', 'true'):
					layer.properties[1] = 0
				tr = self.get_level_trafo(svg_obj, trafo)
				stl = self.get_level_style(svg_obj, style)
				if 'display' in stl and stl['display'] == 'none':
					layer.properties[0] = 0
				for item in svg_obj.childs:
					self.translate_obj(layer, item, tr, stl)
		else:
			group = sk2_model.Group(parent.config, parent)
			tr = self.get_level_trafo(svg_obj, trafo)
			stl = self.get_level_style(svg_obj, style)
			for item in svg_obj.childs:
				self.translate_obj(group, item, tr, stl)
			if group.childs:
				parent.childs.append(group)

	def translate_rect(self, parent, svg_obj, trafo, style):
		cfg = parent.config
		sk2_style = self.get_sk2_style(svg_obj, style)
		tr = self.get_level_trafo(svg_obj, trafo)

		x = self.get_size_pt(svg_obj.attrs['x'])
		y = self.get_size_pt(svg_obj.attrs['y'])
		w = self.get_size_pt(svg_obj.attrs['width'])
		h = self.get_size_pt(svg_obj.attrs['height'])

		corners = [] + sk2_const.CORNERS
		rx = ry = None
		if 'rx' in svg_obj.attrs:
			rx = self.get_size_pt(svg_obj.attrs['rx'])
		if 'ry' in svg_obj.attrs:
			ry = self.get_size_pt(svg_obj.attrs['ry'])
		if rx is None and not ry is None: rx = ry
		elif ry is None and not rx is None: ry = rx

		if not rx is None:
			rx = abs(rx)
			ry = abs(ry)
			if rx > w / 2.0: rx = w / 2.0
			if ry > h / 2.0: ry = h / 2.0
			coeff = rx / ry
			w = w / coeff
			trafo = [1.0, 0.0, 0.0, 1.0, -x, -y]
			trafo1 = [coeff, 0.0, 0.0, 1.0, 0.0, 0.0]
			trafo2 = [1.0, 0.0, 0.0, 1.0, x, y]
			trafo = libgeom.multiply_trafo(trafo, trafo1)
			trafo = libgeom.multiply_trafo(trafo, trafo2)
			tr = libgeom.multiply_trafo(trafo, tr)
			corners = [2.0 * ry / min(w, h), ] * 4

		rect = sk2_model.Rectangle(cfg, parent, [x, y, w, h], tr,
								sk2_style, corners)
		rect.stroke_trafo = [] + tr
		parent.childs.append(rect)

	def translate_ellipse(self, parent, svg_obj, trafo, style):
		cfg = parent.config
		sk2_style = self.get_sk2_style(svg_obj, style)
		tr = self.get_level_trafo(svg_obj, trafo)

		cx = cy = 0.0
		if 'cx' in svg_obj.attrs:
			cx = self.get_size_pt(svg_obj.attrs['cx'])
		if 'cy' in svg_obj.attrs:
			cy = self.get_size_pt(svg_obj.attrs['cy'])
		if 'rx' in svg_obj.attrs:
			rx = self.get_size_pt(svg_obj.attrs['rx'])
		if 'ry' in svg_obj.attrs:
			ry = self.get_size_pt(svg_obj.attrs['ry'])
		if not rx or not ry: return
		rect = [cx - rx, cy - ry, 2.0 * rx, 2.0 * ry]
		print rect, tr

		ellipse = sk2_model.Circle(cfg, parent, rect, style=sk2_style)
		ellipse.trafo = libgeom.multiply_trafo(ellipse.trafo, tr)
		ellipse.stroke_trafo = [] + tr
		parent.childs.append(ellipse)

	def translate_circle(self, parent, svg_obj, trafo, style):
		cfg = parent.config
		sk2_style = self.get_sk2_style(svg_obj, style)
		tr = self.get_level_trafo(svg_obj, trafo)

		cx = cy = r = 0.0
		if 'cx' in svg_obj.attrs:
			cx = self.get_size_pt(svg_obj.attrs['cx'])
		if 'cy' in svg_obj.attrs:
			cy = self.get_size_pt(svg_obj.attrs['cy'])
		if 'r' in svg_obj.attrs:
			r = self.get_size_pt(svg_obj.attrs['r'])
		if not r: return
		rect = [cx - r, cy - r, 2.0 * r, 2.0 * r]

		ellipse = sk2_model.Circle(cfg, parent, rect, style=sk2_style)
		ellipse.trafo = libgeom.multiply_trafo(ellipse.trafo, tr)
		ellipse.stroke_trafo = [] + tr
		parent.childs.append(ellipse)

	def translate_line(self, parent, svg_obj, trafo, style):
		cfg = parent.config
		sk2_style = self.get_sk2_style(svg_obj, style)
		tr = self.get_level_trafo(svg_obj, trafo)

		x1 = y1 = x2 = y2 = 0.0
		if 'x1' in svg_obj.attrs:
			x1 = self.get_size_pt(svg_obj.attrs['x1'])
		if 'y1' in svg_obj.attrs:
			y1 = self.get_size_pt(svg_obj.attrs['y1'])
		if 'x2' in svg_obj.attrs:
			x2 = self.get_size_pt(svg_obj.attrs['x2'])
		if 'y2' in svg_obj.attrs:
			y2 = self.get_size_pt(svg_obj.attrs['y2'])

		paths = [[[x1, y1], [[x2, y2], ], sk2_const.CURVE_OPENED], ]

		path = sk2_model.Curve(cfg, parent, paths, tr, sk2_style)
		path.stroke_trafo = [] + tr
		parent.childs.append(path)

	def translate_path(self, parent, svg_obj, trafo, style):
		path = None
		cfg = parent.config
		sk2_style = self.get_sk2_style(svg_obj, style)
		tr = self.get_level_trafo(svg_obj, trafo)

		if self.check_attr(svg_obj, 'sodipodi:type', 'arc'):
			cx = self.get_size_pt(svg_obj.attrs['sodipodi:cx'])
			cy = self.get_size_pt(svg_obj.attrs['sodipodi:cy'])
			rx = self.get_size_pt(svg_obj.attrs['sodipodi:rx'])
			ry = self.get_size_pt(svg_obj.attrs['sodipodi:ry'])
			angle1 = float(svg_obj.attrs['sodipodi:start'])
			angle2 = float(svg_obj.attrs['sodipodi:end'])
			circle_type = sk2_const.ARC_PIE_SLICE
			if self.check_attr(svg_obj, 'sodipodi:open', 'true'):
				circle_type = sk2_const.ARC_ARC
			rect = [cx - rx, cy - ry, 2.0 * rx, 2.0 * ry]
			path = sk2_model.Circle(cfg, parent, rect, angle1, angle2,
									circle_type, sk2_style)
			path.trafo = libgeom.multiply_trafo(path.trafo, tr)
			path.stroke_trafo = [] + path.trafo
		elif 'd' in svg_obj.attrs:
			pass

		if path: parent.childs.append(path)




class SK2_to_SVG_Translator(object):

	def translate(self, sk2_doc, svg_doc):pass
