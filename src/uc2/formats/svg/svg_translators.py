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

import sys, os
from copy import deepcopy
from cStringIO import StringIO
from PIL import Image
from base64 import b64decode

from uc2 import uc2const, libgeom, libpango, libimg
from uc2.formats.sk2 import sk2_model, sk2_const
from uc2.formats.svg import svg_const, svglib
from uc2.formats.svg.svglib import get_svg_trafo, check_svg_attr, \
parse_svg_points, parse_svg_coords, parse_svg_color, parse_svg_stops, \
get_svg_level_trafo

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


FONT_COEFF = 1.342

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

SK2_TEXT_ALIGN = {
	'start':sk2_const.TEXT_ALIGN_LEFT,
	'middle':sk2_const.TEXT_ALIGN_CENTER,
	'end':sk2_const.TEXT_ALIGN_RIGHT,
}



class SVG_to_SK2_Translator(object):

	page = None
	layer = None
	defs = None
	trafo = []
	coeff = 1.0
	user_space = []
	defs = {}
	style_opts = {}
	id_dict = {}

	def translate(self, svg_doc, sk2_doc):
		self.svg_doc = svg_doc
		self.sk2_doc = sk2_doc
		self.svg_mt = svg_doc.model
		self.sk2_mt = sk2_doc.model
		self.sk2_mtds = sk2_doc.methods
		self.svg_mtds = svg_doc.methods
		self.defs = {}
		self.current_color = ''
		self.translate_units()
		self.translate_page()
		for item in self.svg_mt.childs:
			style = self.get_level_style(self.svg_mt, svg_const.SVG_STYLE)
			self.translate_obj(self.layer, item, self.trafo, style)
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

	def get_font_size(self, sval):
		return self.get_size_pt(sval) / FONT_COEFF

	def get_viewbox(self, svbox):
		vbox = []
		for item in svbox.split(' '):
			vbox.append(self.get_size_pt(item))
		return vbox

	def parse_stops(self, stops):
		sk2_stops = []
		for stop in stops:
			if not stop.tag == 'stop': continue
			offset = stop.attrs['offset']
			if offset[-1] == '%':offset = float(offset[:-1]) / 100.0
			else: offset = float(offset)

			alpha = 1.0
			sclr = 'black'
			if 'stop-opacity' in stop.attrs:
				alpha = float(stop.attrs['stop-opacity'])
			if 'stop-color' in stop.attrs:
				sclr = stop.attrs['stop-color']

			if 'style' in stop.attrs:
				style = {}
				stls = str(stop.attrs['style']).split(';')
				for stl in stls:
					vals = stl.split(':')
					if len(vals) == 2:
						style[vals[0]] = vals[1]
				if 'stop-opacity' in style:
					alpha = float(style['stop-opacity'])
				if 'stop-color' in style:
					sclr = style['stop-color']

			clr = parse_svg_color(sclr, alpha, self.current_color)
			sk2_stops.append([offset, clr])
		return sk2_stops

	def parse_def(self, svg_obj):
		if 'color' in svg_obj.attrs:
			if svg_obj.attrs['color'] == 'inherit':pass
			else: self.current_color = '' + svg_obj.attrs['color']
		if svg_obj.tag == 'linearGradient':
			if 'xlink:href' in svg_obj.attrs:
				cid = svg_obj.attrs['xlink:href'][1:]
				if cid in self.defs:
					stops = self.parse_def(self.defs[cid])[2][2]
					if not stops: return []
			elif svg_obj.childs:
				stops = parse_svg_stops(svg_obj.childs, self.current_color)
				if not stops: return []
			else: return []

			x1 = 0.0
			y1 = 0.0
			x2 = self.user_space[2]
			y2 = 0.0
			if 'x1' in svg_obj.attrs:
				x1 = self.get_size_pt(svg_obj.attrs['x1'])
			if 'y1' in svg_obj.attrs:
				y1 = self.get_size_pt(svg_obj.attrs['y1'])
			if 'x2' in svg_obj.attrs:
				x2 = self.get_size_pt(svg_obj.attrs['x2'])
			if 'y2' in svg_obj.attrs:
				y2 = self.get_size_pt(svg_obj.attrs['y2'])

			if 'gradientTransform' in svg_obj.attrs:
				strafo = svg_obj.attrs['gradientTransform']
				self.style_opts['grad-trafo'] = get_svg_trafo(strafo)

			vector = [[x1, y1], [x2, y2]]
			return [0, sk2_const.FILL_GRADIENT,
				 [sk2_const.GRADIENT_LINEAR, vector, stops]]

		elif svg_obj.tag == 'radialGradient':
			if 'xlink:href' in svg_obj.attrs:
				cid = svg_obj.attrs['xlink:href'][1:]
				if cid in self.defs:
					stops = self.parse_def(self.defs[cid])[2][2]
					if not stops: return []
			elif svg_obj.childs:
				stops = parse_svg_stops(svg_obj.childs, self.current_color)
				if not stops: return []
			else: return []

			cx = self.user_space[2] / 2.0 + self.user_space[0]
			cy = self.user_space[3] / 2.0 + self.user_space[1]
			if 'cx' in svg_obj.attrs:
				cx = self.get_size_pt(svg_obj.attrs['cx'])
			if 'cy' in svg_obj.attrs:
				cy = self.get_size_pt(svg_obj.attrs['cy'])

			r = self.user_space[2] / 2.0 + self.user_space[0]
			if 'r' in svg_obj.attrs:
				r = self.get_size_pt(svg_obj.attrs['r'])

			if 'gradientTransform' in svg_obj.attrs:
				strafo = svg_obj.attrs['gradientTransform']
				self.style_opts['grad-trafo'] = get_svg_trafo(strafo)

			vector = [[cx, cy], [cx + r, cy]]
			return [0, sk2_const.FILL_GRADIENT,
				 [sk2_const.GRADIENT_RADIAL, vector, stops]]

		return []

	def get_level_style(self, svg_obj, style):
		style = deepcopy(style)
		for item in svg_const.SVG_STYLE.keys():
			if item in svg_obj.attrs:
				style[item] = '' + str(svg_obj.attrs[item])
		if 'color' in svg_obj.attrs:
			if svg_obj.attrs['color'] == 'inherit':pass
			else: self.current_color = '' + svg_obj.attrs['color']
		if 'style' in svg_obj.attrs:
			stls = str(svg_obj.attrs['style']).split(';')
			for stl in stls:
				vals = stl.split(':')
				if len(vals) == 2:
					style[vals[0].strip()] = vals[1].strip()
		return style

	def get_sk2_style(self, svg_obj, style, text_style=False):
		sk2_style = [[], [], [], []]
		style = self.get_level_style(svg_obj, style)
		self.style_opts = {}

		if 'display' in style and style['display'] == 'none':
			return sk2_style
		if 'visibility' in style and \
		style['visibility'] in ('hidden', 'collapse'):
			return sk2_style

		# fill parsing
		if not style['fill'] == 'none':
			fillrule = SK2_FILL_RULE[style['fill-rule']]
			fill = style['fill']
			alpha = float(style['fill-opacity']) * float(style['opacity'])
			if len(fill) > 3 and fill[:3] == 'url':
				def_id = fill[5:-1]
				if def_id in self.defs:
					sk2_style[0] = self.parse_def(self.defs[def_id])
					if sk2_style[0]:
						sk2_style[0][0] = fillrule
						if sk2_style[0][1] == sk2_const.FILL_GRADIENT:
							for stop in sk2_style[0][2][2]:
								color = stop[1]
								color[2] *= alpha
					if 'grad-trafo' in self.style_opts:
						tr = [] + self.style_opts['grad-trafo']
						self.style_opts['fill-grad-trafo'] = tr
			else:
				clr = parse_svg_color(fill, alpha, self.current_color)
				if clr:
					sk2_style[0] = [fillrule, sk2_const.FILL_SOLID, clr]

		# stroke parsing
		if not style['stroke'] == 'none':
			stroke = style['stroke']
			stroke_rule = sk2_const.STROKE_MIDDLE
			stroke_width = self.get_size_pt(style['stroke-width'])
			stroke_linecap = SK2_LINE_CAP[style['stroke-linecap']]
			stroke_linejoin = SK2_LINE_JOIN[style['stroke-linejoin']]
			stroke_miterlimit = float(style['stroke-miterlimit'])
			alpha = float(style['stroke-opacity']) * float(style['opacity'])

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
				def_id = stroke[5:-1]
				if def_id in self.defs:
					stroke_fill = self.parse_def(self.defs[def_id])
					if stroke_fill:
						stroke_fill[0] = sk2_const.FILL_EVENODD
						if stroke_fill[1] == sk2_const.FILL_GRADIENT:
							for stop in stroke_fill[2][2]:
								color = stop[1]
								color[2] *= alpha
						self.style_opts['stroke-fill'] = stroke_fill
						clr = parse_svg_color('black')
						sk2_style[1] = [stroke_rule, stroke_width, clr, dash,
							stroke_linecap, stroke_linejoin,
							stroke_miterlimit, 0, 1, []]
						if 'grad-trafo' in self.style_opts:
							tr = [] + self.style_opts['grad-trafo']
							self.style_opts['stroke-grad-trafo'] = tr
			else:
				clr = parse_svg_color(stroke, alpha, self.current_color)
				if clr:
					sk2_style[1] = [stroke_rule, stroke_width, clr, dash,
							stroke_linecap, stroke_linejoin,
							stroke_miterlimit, 0, 1, []]

		if text_style:
			font_family = 'Sans'
			if style['font-family'] in libpango.get_fonts()[0]:
				font_family = style['font-family']
			font_face = 'Regular'
			font_size = 12.0
			try:
				font_size = self.get_font_size(style['font-size'])
			except:pass
			alignment = sk2_const.TEXT_ALIGN_LEFT
			if style['text-align'] in SK2_TEXT_ALIGN:
				alignment = SK2_TEXT_ALIGN[style['text-align']]
			sk2_style[2] = [font_family, font_face, font_size,
						alignment, [], True]

		return sk2_style

	def get_image(self, svg_obj):
		if not 'xlink:href' in svg_obj.attrs: return None
		link = svg_obj.attrs['xlink:href']
		if link[:4] == 'http': pass
		elif link[:4] == 'data':
			pos = 0
			for sig in svg_const.IMG_SIGS:
				if link[:len(sig)] == sig: pos = len(sig)
			if pos:
				try:
					raw_image = Image.open(StringIO(b64decode(link[pos:])))
					raw_image.load()
					return raw_image
				except:pass
		elif self.svg_doc.doc_file:
			file_dir = os.path.dirname(self.svg_doc.doc)
			image_path = os.path.join(file_dir, link)
			image_path = os.path.abspath(image_path)
			if os.path.lexists(image_path):
				raw_image = Image.open(image_path)
				raw_image.load()
				return raw_image
		return None

	#--- Translation metods

	def translate_units(self):
		units = SK2_UNITS[self.svg_mtds.doc_units()]
		if units == uc2const.UNIT_PX: self.coeff = 1.25
		self.sk2_mt.doc_units = units

	def translate_page(self):
		width = height = 0.0
		vbox = []
		if 'viewBox' in self.svg_mt.attrs:
			vbox = self.get_viewbox(self.svg_mt.attrs['viewBox'])

		if 'width' in self.svg_mt.attrs:
			if not self.svg_mt.attrs['width'][-1] == '%':
				width = self.get_size_pt(self.svg_mt.attrs['width'])
			else:
				if vbox:width = vbox[2]
			if not self.svg_mt.attrs['height'][-1] == '%':
				height = self.get_size_pt(self.svg_mt.attrs['height'])
			else:
				if vbox:height = vbox[3]
		elif vbox:
			width = vbox[2]
			height = vbox[3]

		if not width: width = self.get_size_pt('210mm')
		if not height: height = self.get_size_pt('297mm')

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
		self.user_space = [0.0, 0.0, width, height]

		if vbox:
			dx = -vbox[0]
			dy = -vbox[1]
			xx = width / vbox[2]
			yy = height / vbox[3]
			if 'xml:space' in self.svg_mt.attrs and \
			self.svg_mt.attrs['xml:space'] == 'preserve':
				xx = yy = min(xx, yy)
			tr = [xx, 0.0, 0.0, yy, 0.0, 0.0]
			tr = libgeom.multiply_trafo([1.0, 0.0, 0.0, 1.0, dx, dy], tr)
			self.trafo = libgeom.multiply_trafo(tr, self.trafo)
			self.user_space = vbox

	def translate_obj(self, parent, svg_obj, trafo, style):
		try:
			if 'id' in svg_obj.attrs:
				self.id_dict[svg_obj.attrs['id']] = svg_obj
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
			elif svg_obj.tag == 'line':
				self.translate_line(parent, svg_obj, trafo, style)
			elif svg_obj.tag == 'polyline':
				self.translate_polyline(parent, svg_obj, trafo, style)
			elif svg_obj.tag == 'polygon':
				self.translate_polygon(parent, svg_obj, trafo, style)
			elif svg_obj.tag == 'path':
				self.translate_path(parent, svg_obj, trafo, style)
			elif svg_obj.tag == 'use':
				self.translate_use(parent, svg_obj, trafo, style)
			elif svg_obj.tag == 'text':
				self.translate_text(parent, svg_obj, trafo, style)
			elif svg_obj.tag == 'image':
				self.translate_image(parent, svg_obj, trafo, style)
			elif svg_obj.tag == 'linearGradient':
				if 'id' in svg_obj.attrs:
					self.defs[svg_obj.attrs['id']] = svg_obj
			elif svg_obj.tag == 'radialGradient':
				if 'id' in svg_obj.attrs:
					self.defs[svg_obj.attrs['id']] = svg_obj
		except:
			print 'tag', svg_obj.tag
			if 'id' in svg_obj.attrs: print 'id', svg_obj.attrs['id']
			for item in sys.exc_info(): print item


	def translate_defs(self, svg_obj):
		for item in svg_obj.childs:
			if 'id' in item.attrs:
				self.defs[str(item.attrs['id'])] = item

	def translate_g(self, parent, svg_obj, trafo, style):
		if 'inkscape:groupmode' in svg_obj.attrs:
			if svg_obj.attrs['inkscape:groupmode'] == 'layer':
				name = 'Layer %d' % len(self.page.childs)
				if 'inkscape:label' in svg_obj.attrs:
					name = str(svg_obj.attrs['inkscape:label'])
				layer = sk2_model.Layer(self.page.config, self.page, name)
				self.page.childs.append(layer)
				if check_svg_attr(svg_obj, 'sodipodi:insensitive', 'true'):
					layer.properties[1] = 0
				tr = get_svg_level_trafo(svg_obj, trafo)
				stl = self.get_level_style(svg_obj, style)
				if 'display' in stl and stl['display'] == 'none':
					layer.properties[0] = 0
				for item in svg_obj.childs:
					self.translate_obj(layer, item, tr, stl)
		else:
			group = sk2_model.Group(parent.config, parent)
			tr = get_svg_level_trafo(svg_obj, trafo)
			stl = self.get_level_style(svg_obj, style)
			for item in svg_obj.childs:
				self.translate_obj(group, item, tr, stl)
			if group.childs:
				parent.childs.append(group)

	def translate_rect(self, parent, svg_obj, trafo, style):
		cfg = parent.config
		sk2_style = self.get_sk2_style(svg_obj, style)
		tr = get_svg_level_trafo(svg_obj, trafo)

		x = y = w = h = 0
		if 'x' in svg_obj.attrs:
			x = self.get_size_pt(svg_obj.attrs['x'])
		if 'y' in svg_obj.attrs:
			y = self.get_size_pt(svg_obj.attrs['y'])
		if 'width' in svg_obj.attrs:
			w = self.get_size_pt(svg_obj.attrs['width'])
		if 'height' in svg_obj.attrs:
			h = self.get_size_pt(svg_obj.attrs['height'])

		if not w or not h: return

		corners = [] + sk2_const.CORNERS
		rx = ry = None
		if 'rx' in svg_obj.attrs:
			rx = self.get_size_pt(svg_obj.attrs['rx'])
		if 'ry' in svg_obj.attrs:
			ry = self.get_size_pt(svg_obj.attrs['ry'])
		if rx is None and not ry is None: rx = ry
		elif ry is None and not rx is None: ry = rx
		if not rx or not ry: rx = ry = None

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
		if sk2_style[0] and not sk2_style[0][1] == sk2_const.FILL_SOLID:
			rect.fill_trafo = [] + tr
			if 'fill-grad-trafo' in self.style_opts:
				tr0 = self.style_opts['fill-grad-trafo']
				rect.fill_trafo = libgeom.multiply_trafo(tr0, tr)

		parent.childs.append(rect)

	def translate_ellipse(self, parent, svg_obj, trafo, style):
		cfg = parent.config
		sk2_style = self.get_sk2_style(svg_obj, style)
		tr = get_svg_level_trafo(svg_obj, trafo)

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

		ellipse = sk2_model.Circle(cfg, parent, rect, style=sk2_style)
		ellipse.trafo = libgeom.multiply_trafo(ellipse.trafo, tr)
		ellipse.stroke_trafo = [] + tr
		if sk2_style[0] and not sk2_style[0][1] == sk2_const.FILL_SOLID:
			ellipse.fill_trafo = [] + tr
			if 'fill-grad-trafo' in self.style_opts:
				tr0 = self.style_opts['fill-grad-trafo']
				ellipse.fill_trafo = libgeom.multiply_trafo(tr0, tr)
		parent.childs.append(ellipse)

	def translate_circle(self, parent, svg_obj, trafo, style):
		cfg = parent.config
		sk2_style = self.get_sk2_style(svg_obj, style)
		tr = get_svg_level_trafo(svg_obj, trafo)

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
		if sk2_style[0] and not sk2_style[0][1] == sk2_const.FILL_SOLID:
			ellipse.fill_trafo = [] + tr
			if 'fill-grad-trafo' in self.style_opts:
				tr0 = self.style_opts['fill-grad-trafo']
				ellipse.fill_trafo = libgeom.multiply_trafo(tr0, tr)
		parent.childs.append(ellipse)

	def translate_line(self, parent, svg_obj, trafo, style):
		cfg = parent.config
		sk2_style = self.get_sk2_style(svg_obj, style)
		tr = get_svg_level_trafo(svg_obj, trafo)

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

		curve = sk2_model.Curve(cfg, parent, paths, tr, sk2_style)
		curve.stroke_trafo = [] + tr
		if sk2_style[0] and not sk2_style[0][1] == sk2_const.FILL_SOLID:
			curve.fill_trafo = [] + tr
			if 'fill-grad-trafo' in self.style_opts:
				tr0 = self.style_opts['fill-grad-trafo']
				curve.fill_trafo = libgeom.multiply_trafo(tr0, tr)
		parent.childs.append(curve)

	def _line(self, point1, point2):
		paths = [[[] + point1, [[] + point2, ], sk2_const.CURVE_OPENED], ]
		tr = [] + self.trafo
		style = [[], self.layer.config.default_stroke, [], []]
		curve = sk2_model.Curve(self.layer.config, self.layer, paths, tr, style)
		self.layer.childs.append(curve)

	def translate_polyline(self, parent, svg_obj, trafo, style):
		cfg = parent.config
		sk2_style = self.get_sk2_style(svg_obj, style)
		tr = get_svg_level_trafo(svg_obj, trafo)

		if not 'points' in svg_obj.attrs: return
		points = parse_svg_points(svg_obj.attrs['points'])
		if not points or len(points) < 2: return
		paths = [[points[0], points[1:], sk2_const.CURVE_OPENED], ]

		curve = sk2_model.Curve(cfg, parent, paths, tr, sk2_style)
		curve.stroke_trafo = [] + tr
		if sk2_style[0] and not sk2_style[0][1] == sk2_const.FILL_SOLID:
			curve.fill_trafo = [] + tr
			if 'fill-grad-trafo' in self.style_opts:
				tr0 = self.style_opts['fill-grad-trafo']
				curve.fill_trafo = libgeom.multiply_trafo(tr0, tr)
		parent.childs.append(curve)

	def translate_polygon(self, parent, svg_obj, trafo, style):
		cfg = parent.config
		sk2_style = self.get_sk2_style(svg_obj, style)
		tr = get_svg_level_trafo(svg_obj, trafo)

		if not 'points' in svg_obj.attrs: return
		points = parse_svg_points(svg_obj.attrs['points'])
		if not points or len(points) < 3: return
		points.append([] + points[0])
		paths = [[points[0], points[1:], sk2_const.CURVE_CLOSED], ]

		curve = sk2_model.Curve(cfg, parent, paths, tr, sk2_style)
		curve.stroke_trafo = [] + tr
		if sk2_style[0] and not sk2_style[0][1] == sk2_const.FILL_SOLID:
			curve.fill_trafo = [] + tr
			if 'fill-grad-trafo' in self.style_opts:
				tr0 = self.style_opts['fill-grad-trafo']
				curve.fill_trafo = libgeom.multiply_trafo(tr0, tr)
		parent.childs.append(curve)

	def translate_path(self, parent, svg_obj, trafo, style):
		curve = None
		cfg = parent.config
		sk2_style = self.get_sk2_style(svg_obj, style)
		tr = get_svg_level_trafo(svg_obj, trafo)

		if check_svg_attr(svg_obj, 'sodipodi:type', 'arc'):
			cx = self.get_size_pt(svg_obj.attrs['sodipodi:cx'])
			cy = self.get_size_pt(svg_obj.attrs['sodipodi:cy'])
			rx = self.get_size_pt(svg_obj.attrs['sodipodi:rx'])
			ry = self.get_size_pt(svg_obj.attrs['sodipodi:ry'])
			angle1 = angle2 = 0.0
			if 'sodipodi:start' in svg_obj.attrs:
				angle1 = float(svg_obj.attrs['sodipodi:start'])
			if 'sodipodi:end' in svg_obj.attrs:
				angle2 = float(svg_obj.attrs['sodipodi:end'])
			circle_type = sk2_const.ARC_PIE_SLICE
			if check_svg_attr(svg_obj, 'sodipodi:open', 'true'):
				circle_type = sk2_const.ARC_ARC
			rect = [cx - rx, cy - ry, 2.0 * rx, 2.0 * ry]
			curve = sk2_model.Circle(cfg, parent, rect, angle1, angle2,
									circle_type, sk2_style)
			curve.trafo = libgeom.multiply_trafo(curve.trafo, tr)
			curve.stroke_trafo = [] + tr
			if sk2_style[0] and not sk2_style[0][1] == sk2_const.FILL_SOLID:
				curve.fill_trafo = [] + tr
				if 'fill-grad-trafo' in self.style_opts:
					tr0 = self.style_opts['fill-grad-trafo']
					curve.fill_trafo = libgeom.multiply_trafo(tr0, tr)
		elif 'd' in svg_obj.attrs:

			paths = svglib.parse_svg_path_cmds(svg_obj.attrs['d'])
			if not paths: return

			curve = sk2_model.Curve(cfg, parent, paths, tr, sk2_style)
			curve.stroke_trafo = [] + tr
			if sk2_style[0] and not sk2_style[0][1] == sk2_const.FILL_SOLID:
				curve.fill_trafo = [] + tr
				if 'fill-grad-trafo' in self.style_opts:
					tr0 = self.style_opts['fill-grad-trafo']
					curve.fill_trafo = libgeom.multiply_trafo(tr0, tr)

		if curve: parent.childs.append(curve)

	def translate_use(self, parent, svg_obj, trafo, style):
		tr = get_svg_level_trafo(svg_obj, trafo)
		stl = self.get_level_style(svg_obj, style)
		if 'xlink:href' in svg_obj.attrs:
			obj_id = svg_obj.attrs['xlink:href'][1:]
			if obj_id in self.id_dict:
				self.translate_obj(parent, self.id_dict[obj_id], tr, stl)

	def translate_text(self, parent, svg_obj, trafo, style):
		cfg = parent.config
		stl = self.get_level_style(svg_obj, style)
		sk2_style = self.get_sk2_style(svg_obj, stl, True)
		tr_level = get_svg_level_trafo(svg_obj, trafo)
		inv_tr = libgeom.invert_trafo(self.trafo)
		tr = libgeom.multiply_trafo(inv_tr, tr_level)

		x = y = 0.0
		if 'x' in svg_obj.attrs:
			x = parse_svg_coords(svg_obj.attrs['x'])[0]
		if 'y' in svg_obj.attrs:
			y = parse_svg_coords(svg_obj.attrs['y'])[0]

		if not svg_obj.childs: return
		txt = svglib.parse_svg_text(svg_obj.childs)

		x, y = libgeom.apply_trafo_to_point([x, y], self.trafo)
		text = sk2_model.Text(cfg, parent, [x, y], txt, -1, tr, sk2_style)
		text.stroke_trafo = [] + tr
		if sk2_style[0] and not sk2_style[0][1] == sk2_const.FILL_SOLID:
			text.fill_trafo = [] + tr
			if 'fill-grad-trafo' in self.style_opts:
				tr0 = self.style_opts['fill-grad-trafo']
				text.fill_trafo = libgeom.multiply_trafo(tr0, tr)
		parent.childs.append(text)

	def translate_image(self, parent, svg_obj, trafo, style):
		cfg = parent.config
		tr_level = get_svg_level_trafo(svg_obj, trafo)
		inv_tr = libgeom.invert_trafo(self.trafo)
		tr = libgeom.multiply_trafo(inv_tr, tr_level)

		x = y = 0.0
		if 'x' in svg_obj.attrs:
			x = parse_svg_coords(svg_obj.attrs['x'])[0]
		if 'y' in svg_obj.attrs:
			y = parse_svg_coords(svg_obj.attrs['y'])[0]

		w = h = 0.0
		if 'width' in svg_obj.attrs:
			w = parse_svg_coords(svg_obj.attrs['width'])[0]
		if 'height' in svg_obj.attrs:
			h = parse_svg_coords(svg_obj.attrs['height'])[0]
		if not w or not h: return

		raw_image = self.get_image(svg_obj)
		if not raw_image: return
		img_w, img_h = raw_image.size
		trafo = [1.0, 0.0, 0.0, 1.0, -img_w / 2.0, -img_h / 2.0]
		trafo1 = [w / img_w, 0.0, 0.0, h / img_h, 0.0, 0.0]
		trafo2 = [1.0, 0.0, 0.0, 1.0, w / 2.0, h / 2.0]
		trafo = libgeom.multiply_trafo(trafo, trafo1)
		trafo = libgeom.multiply_trafo(trafo, trafo2)
		dx, dy = libgeom.apply_trafo_to_point([x, y], self.trafo)
		trafo3 = [1.0, 0.0, 0.0, 1.0, dx, dy - h]
		trafo = libgeom.multiply_trafo(trafo, trafo3)
		trafo = libgeom.multiply_trafo(trafo, tr)

		pixmap = sk2_model.Pixmap(cfg)
		image_stream = StringIO()
		if raw_image.mode == "CMYK":
			raw_image.save(image_stream, 'JPEG', quality=100)
		else:
			raw_image.save(image_stream, 'PNG')
		content = image_stream.getvalue()

		libimg.set_image_data(self.sk2_doc.cms, pixmap, content)
		pixmap.trafo = trafo
		parent.childs.append(pixmap)


class SK2_to_SVG_Translator(object):

	def translate(self, sk2_doc, svg_doc):pass
