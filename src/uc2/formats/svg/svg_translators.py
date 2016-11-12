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
from uc2.libgeom import add_points, sub_points
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

PATH_STUB = [[], [], sk2_const.CURVE_OPENED]

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

	def parse_points(self, spoints):
		points = []
		pairs = spoints.split(' ')
		for item in pairs:
			try:
				pair = item.split(',')
				if not len(pair) == 2:continue
				points.append([float(pair[0]), float(pair[1])])
			except: continue
		return points

	def parse_coords(self, scoords):
		scoords = scoords.strip().replace(',', ' ').replace('-', ' -').strip()
		scoords = scoords.replace('  ', ' ').replace('  ', ' ')
		if scoords:
			return map(lambda x:float(x), scoords.split(' '))
		return None

	def parse_svg_color(self, sclr, alpha=1.0):
		sclr = sclr.split(' ')[0]
		if sclr[0] == '#':
			vals = cms.hexcolor_to_rgb(sclr)
			clr = ['RGB', vals, alpha, '']
		else:
			if sclr in svg_colors.SVG_COLORS:
				clr = deepcopy(svg_colors.SVG_COLORS[sclr])
				clr[2] = alpha
		return clr

	def base_point(self, point):
		if len(point) == 2: return [] + point
		return [] + point[-1]

	def parse_path_cmds(self, pathcmds):
		index = 0
		last = None
		last_index = 0
		cmds = []
		for item in pathcmds:
			if item in 'MmZzLlHhVvCcSsQqTtAa':
				if last:
					coords = self.parse_coords(pathcmds[last_index + 1:index])
					cmds.append((last, coords))
				last = item
				last_index = index
			index += 1

		coords = self.parse_coords(pathcmds[last_index + 1:index])
		cmds.append([last, coords])

		paths = []
		path = []
		cpoint = []
		rel_flag = False
		for cmd in cmds:
			if cmd[0] in 'Mm':
				if path: paths.append(path)
				path = deepcopy(PATH_STUB)
				rel_flag = cmd[0] == 'm'
				points = [cmd[1][i:i + 2] for i in range(0, len(cmd[1]), 2)]
				for point in points:
					if cpoint and rel_flag:
						point = add_points(self.base_point(cpoint), point)
					if not path[0]: path[0] = point
					else: path[1].append(point)
					cpoint = point
			elif cmd[0] in 'Zz':
				path[1].append([] + path[0])
				path[2] = sk2_const.CURVE_CLOSED
			elif cmd[0] in 'Cc':
				rel_flag = cmd[0] == 'c'
				points = [cmd[1][i:i + 2] for i in range(0, len(cmd[1]), 2)]
				points = [points[i:i + 3] for i in range(0, len(points), 3)]
				for point in points:
					if rel_flag:
						point = [add_points(self.base_point(cpoint), point[0]),
								add_points(self.base_point(cpoint), point[1]),
								add_points(self.base_point(cpoint), point[2])]
					qpoint = [] + point
					qpoint.append(sk2_const.NODE_CUSP)
					path[1].append(qpoint)
					cpoint = point
			elif cmd[0] in 'Ll':
				rel_flag = cmd[0] == 'l'
				points = [cmd[1][i:i + 2] for i in range(0, len(cmd[1]), 2)]
				for point in points:
					if rel_flag:
						point = add_points(self.base_point(cpoint), point)
					path[1].append(point)
					cpoint = point
			elif cmd[0] in 'Hh':
				rel_flag = cmd[0] == 'h'
				for x in cmd[1]:
					dx, y = self.base_point(cpoint)
					if rel_flag: point = [x + dx, y]
					else:point = [x, y]
					path[1].append(point)
					cpoint = point
			elif cmd[0] in 'Vv':
				rel_flag = cmd[0] == 'v'
				for y in cmd[1]:
					x, dy = self.base_point(cpoint)
					if rel_flag: point = [x , y + dy]
					else:point = [x, y]
					path[1].append(point)
					cpoint = point
			elif cmd[0] in 'Ss':
				rel_flag = cmd[0] == 's'
				points = [cmd[1][i:i + 2] for i in range(0, len(cmd[1]), 2)]
				points = [points[i:i + 2] for i in range(0, len(points), 2)]
				for point in points:
					q = cpoint
					p = cpoint
					if len(cpoint) > 2:
						q = cpoint[1]
						p = cpoint[2]
					p1 = sub_points(add_points(p, p), q)
					if rel_flag:
						p2 = add_points(self.base_point(cpoint), point[0])
						p3 = add_points(self.base_point(cpoint), point[1])
					else:
						p2, p3 = point
					point = [p1, p2, p3]
					qpoint = [] + point
					qpoint.append(sk2_const.NODE_CUSP)
					path[1].append(qpoint)
					cpoint = point

			elif cmd[0] in 'Aa':
				rel_flag = cmd[0] == 'a'
				arcs = [cmd[1][i:i + 7] for i in range(0, len(cmd[1]), 7)]
				for arc in arcs:
					rev_flag = False
					rx, ry, xrot, large_arc_flag, sweep_flag, x, y = arc
					if rel_flag:
						x += cpoint[0]
						y += cpoint[1]

					vector = [[] + cpoint, [x, y]]
					if sweep_flag:
						vector = [[x, y], [] + cpoint]
						rev_flag = True
					cpoint = [x, y]

					dir_tr = libgeom.trafo_rotate_grad(-xrot)

					if rx > ry:
						tr = [1.0, 0.0, 0.0, rx / ry, 0.0, 0.0]
						r = rx
					else:
						tr = [ry / rx, 0.0, 0.0, 1.0, 0.0, 0.0]
						r = ry

					dir_tr = libgeom.multiply_trafo(dir_tr, tr)
					vector = libgeom.apply_trafo_to_points(vector, dir_tr)


					l = libgeom.distance(*vector)

					if l > 2.0 * r:
						coeff = 2.0 * r / l
						tr = [coeff, 0.0, 0.0, coeff, 0.0, 0.0]
						dir_tr = libgeom.multiply_trafo(dir_tr, tr)
						vector = libgeom.apply_trafo_to_points(vector, tr)
						r = l / 2.0

					mp = libgeom.midpoint(*vector)


					tr0 = libgeom.trafo_rotate(math.pi / 2.0, mp[0], mp[1])
					pvector = libgeom.apply_trafo_to_points(vector, tr0)



					k = math.sqrt(r * r - l * l / 4.0)
					if large_arc_flag:
						center = libgeom.midpoint(mp,
												pvector[1], 2.0 * k / l)
					else:
						center = libgeom.midpoint(mp,
												pvector[0], 2.0 * k / l)


					angle1 = libgeom.get_point_angle(vector[0], center)
					angle2 = libgeom.get_point_angle(vector[1], center)

					da = angle2 - angle1
					start = angle1
					end = angle2
					if large_arc_flag:
						if -math.pi >= da or da <= math.pi:
							start = angle2
							end = angle1
							rev_flag = not rev_flag
					else:
						if -math.pi <= da or da >= math.pi:
							start = angle2
							end = angle1
							rev_flag = not rev_flag

					pth = libgeom.get_circle_paths(start, end,
												sk2_const.ARC_ARC)[0]

					if rev_flag:
						pth = libgeom.reverse_path(pth)

					points = pth[1]
					for point in points:
						if len(point) == 3:
							point.append(sk2_const.NODE_CUSP)

					tr0 = [1.0, 0.0, 0.0, 1.0, -0.5, -0.5]
					points = libgeom.apply_trafo_to_points(points, tr0)

					tr1 = [2.0 * r, 0.0, 0.0, 2.0 * r, 0.0, 0.0]
					points = libgeom.apply_trafo_to_points(points, tr1)

					tr2 = [1.0, 0.0, 0.0, 1.0, center[0], center[1]]
					points = libgeom.apply_trafo_to_points(points, tr2)

					tr3 = libgeom.invert_trafo(dir_tr)
					points = libgeom.apply_trafo_to_points(points, tr3)

					for point in points:
						path[1].append(point)


			# TODO: TtQq command support

		if path:paths.append(path)
		return paths

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

			clr = self.parse_svg_color(sclr, alpha)
			sk2_stops.append([offset, clr])
		return sk2_stops

	def parse_def(self, svg_obj):
		if svg_obj.tag == 'linearGradient':
			if 'xlink:href' in svg_obj.attrs:
				cid = svg_obj.attrs['xlink:href'][1:]
				if cid in self.defs:
					stops = self.parse_def(self.defs[cid])[2][2]
					if not stops: return []
			elif svg_obj.childs:
				stops = self.parse_stops(svg_obj.childs)
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
				self.style_opts['grad-trafo'] = self.get_trafo(strafo)

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
				stops = self.parse_stops(svg_obj.childs)
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
				self.style_opts['grad-trafo'] = self.get_trafo(strafo)

			vector = [[cx, cy], [cx + r, cy]]
			return [0, sk2_const.FILL_GRADIENT,
				 [sk2_const.GRADIENT_RADIAL, vector, stops]]

		return []

	# TODO: implement skew trafo
	def trafo_skewX(self, *args):
		return [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]

	def trafo_skewY(self, *args):
		return [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]

	def trafo_rotate(self, grad, cx=0.0, cy=0.0):
		return libgeom.trafo_rotate_grad(grad, cx, cy)

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
				clr = self.parse_svg_color(fill, alpha)
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
				alpha = float(style['stroke-opacity']) * float(style['opacity'])
				clr = self.parse_svg_color(stroke, alpha)
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
		self.user_space = [0.0, 0.0, width, height]
		if 'viewBox' in self.svg_mt.attrs:
			vbox = self.get_viewbox(self.svg_mt.attrs['viewBox'])
			dx = vbox[0]
			dy = vbox[1]
			xx = width / (vbox[2] - vbox[0])
			yy = height / (vbox[3] - vbox[1])
			tr = [xx, 0.0, 0.0, yy, 0.0, 0.0]
			tr = libgeom.multiply_trafo(tr, [1.0, 0.0, 0.0, 1.0, dx, dy])
			self.trafo = libgeom.multiply_trafo(tr, self.trafo)
			self.user_space = vbox

	def translate_obj(self, parent, svg_obj, trafo, style):
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

	def translate_defs(self, svg_obj):
		self.defs = {}
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
		if sk2_style[0] and not sk2_style[0][1] == sk2_const.FILL_SOLID:
			rect.fill_trafo = [] + tr
			if 'fill-grad-trafo' in self.style_opts:
				tr0 = self.style_opts['fill-grad-trafo']
				rect.fill_trafo = libgeom.multiply_trafo(tr0, tr)

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
		if sk2_style[0] and not sk2_style[0][1] == sk2_const.FILL_SOLID:
			ellipse.fill_trafo = [] + tr
			if 'fill-grad-trafo' in self.style_opts:
				tr0 = self.style_opts['fill-grad-trafo']
				ellipse.fill_trafo = libgeom.multiply_trafo(tr0, tr)
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
		tr = self.get_level_trafo(svg_obj, trafo)

		if not 'points' in svg_obj.attrs: return
		points = self.parse_points(svg_obj.attrs['points'])
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
		tr = self.get_level_trafo(svg_obj, trafo)

		if not 'points' in svg_obj.attrs: return
		points = self.parse_points(svg_obj.attrs['points'])
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
		tr = self.get_level_trafo(svg_obj, trafo)

		if self.check_attr(svg_obj, 'sodipodi:type', 'arc'):
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
			if self.check_attr(svg_obj, 'sodipodi:open', 'true'):
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
			paths = self.parse_path_cmds(svg_obj.attrs['d'])
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
		tr = self.get_level_trafo(svg_obj, trafo)
		stl = self.get_level_style(svg_obj, style)
		if 'xlink:href' in svg_obj.attrs:
			obj_id = svg_obj.attrs['xlink:href'][1:]
			if obj_id in self.id_dict:
				self.translate_obj(parent, self.id_dict[obj_id], tr, stl)



class SK2_to_SVG_Translator(object):

	def translate(self, sk2_doc, svg_doc):pass
