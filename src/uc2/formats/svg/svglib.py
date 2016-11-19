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

import math, re
from copy import deepcopy

from uc2 import uc2const, libgeom, cms
from uc2.libgeom import add_points, sub_points, mult_point
from uc2.formats.sk2 import sk2_const
from uc2.formats.svg import svg_colors

PATH_STUB = [[], [], sk2_const.CURVE_OPENED]
F13 = 1.0 / 3.0
F23 = 2.0 / 3.0

def check_svg_attr(svg_obj, attr, value=None):
	if value is None: return attr in svg_obj.attrs
	if attr in svg_obj.attrs and svg_obj.attrs[attr] == value:
		return True
	return False

def trafo_skewX(a=0.0):
	a = math.radians(a)
	return [1.0, 0.0, math.tan(a), 1.0, 0.0, 0.0]

def trafo_skewY(a=0.0):
	a = math.radians(a)
	return [1.0, math.tan(a), 0.0, 1.0, 0.0, 0.0]

def trafo_rotate(grad, cx=0.0, cy=0.0):
	return libgeom.trafo_rotate_grad(grad, cx, cy)

def trafo_scale(m11, m22=None):
	if m22 is None: m22 = m11
	return [m11, 0.0, 0.0, m22, 0.0, 0.0]

def trafo_translate(dx, dy=0.0):
	return [1.0, 0.0, 0.0, 1.0, dx, dy]

def trafo_matrix(m11, m21, m12, m22, dx, dy):
	return [m11, m21, m12, m22, dx, dy]

def get_svg_trafo(strafo):
	trafo = [] + libgeom.NORMAL_TRAFO
	trs = strafo.split(') ')
	trs.reverse()
	for tr in trs:
		tr += ')'
		tr = tr.replace(', ', ',').replace(' ', ',').replace('))', ')')
		try:
			code = compile('tr=trafo_' + tr, '<string>', 'exec')
			exec code
		except: continue
		trafo = libgeom.multiply_trafo(trafo, tr)
	return trafo

def get_svg_level_trafo(svg_obj, trafo):
	tr = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
	if 'transform' in svg_obj.attrs:
		tr = get_svg_trafo(str(svg_obj.attrs['transform']))
	tr = libgeom.multiply_trafo(tr, trafo)
	return tr

def parse_svg_points(spoints):
	points = []
	spoints = re.sub('  *', ' ', spoints)
	spoints = spoints.replace('-', ',-').replace('e,-', 'e-')
	spoints = spoints.replace(',,', ',').replace(' ', ',')
	pairs = spoints.split(',')
	if not pairs[0]:pairs = pairs[1:]
	pairs = [pairs[i:i + 2] for i in range(0, len(pairs), 2)]
	for pair in pairs:
		try:
			points.append([float(pair[0]), float(pair[1])])
		except: continue
	return points

def parse_svg_coords(scoords):
	scoords = scoords.strip().replace(',', ' ').replace('-', ' -')
	scoords = scoords.replace('e -', 'e-').strip()
	scoords = re.sub('  *', ' ', scoords)
	if scoords:
		return map(lambda x:float(x), scoords.split(' '))
	return None

def parse_svg_color(sclr, alpha=1.0, current_color=''):
	clr = deepcopy(svg_colors.SVG_COLORS['black'])
	clr[2] = alpha
	if sclr == 'currentColor' and current_color:
		sclr = '' + current_color
	if sclr[0] == '#':
		sclr = sclr.split(' ')[0]
		try:
			vals = cms.hexcolor_to_rgb(sclr)
			clr = ['RGB', vals, alpha, '']
		except:pass
	elif sclr[:4] == 'rgb(':
		vals = sclr[4:].split(')')[0].split(',')
		if len(vals) == 3:
			decvals = []
			for val in vals:
				val = val.strip()
				if '%' in val:
					decval = float(val.replace('%', ''))
					if decval > 100.0:decval = 100.0
					if decval < 0.0:decval = 0.0
					decval = decval / 100.0
				else:
					decval = float(val)
					if decval > 255.0:decval = 255.0
					if decval < 0.0:decval = 0.0
					decval = decval / 255.0
				decvals.append(decval)
			clr = [uc2const.COLOR_RGB, decvals, alpha, '']
	else:
		if sclr in svg_colors.SVG_COLORS:
			clr = deepcopy(svg_colors.SVG_COLORS[sclr])
			clr[2] = alpha
	return clr

def base_point(point):
	if len(point) == 2: return [] + point
	return [] + point[-1]

def parse_svg_path_cmds(pathcmds):
	index = 0
	last = None
	last_index = 0
	cmds = []
	pathcmds = re.sub('  *', ' ', pathcmds)
	for item in pathcmds:
		if item in 'MmZzLlHhVvCcSsQqTtAa':
			if last:
				coords = parse_svg_coords(pathcmds[last_index + 1:index])
				cmds.append((last, coords))
			last = item
			last_index = index
		index += 1

	coords = parse_svg_coords(pathcmds[last_index + 1:index])
	cmds.append([last, coords])

	paths = []
	path = []
	cpoint = []
	rel_flag = False
	last_cmd = 'M'
	last_quad = None

	for cmd in cmds:
		if cmd[0] in 'Mm':
			if path: paths.append(path)
			path = deepcopy(PATH_STUB)
			rel_flag = cmd[0] == 'm'
			points = [cmd[1][i:i + 2] for i in range(0, len(cmd[1]), 2)]
			for point in points:
				if cpoint and rel_flag:
					point = add_points(base_point(cpoint), point)
				if not path[0]: path[0] = point
				else: path[1].append(point)
				cpoint = point
		elif cmd[0] in 'Zz':
			path[1].append([] + path[0])
			path[2] = sk2_const.CURVE_CLOSED
			cpoint = [] + path[0]
		elif cmd[0] in 'Cc':
			rel_flag = cmd[0] == 'c'
			points = [cmd[1][i:i + 2] for i in range(0, len(cmd[1]), 2)]
			points = [points[i:i + 3] for i in range(0, len(points), 3)]
			for point in points:
				if rel_flag:
					point = [add_points(base_point(cpoint), point[0]),
							add_points(base_point(cpoint), point[1]),
							add_points(base_point(cpoint), point[2])]
				qpoint = [] + point
				qpoint.append(sk2_const.NODE_CUSP)
				path[1].append(qpoint)
				cpoint = point
		elif cmd[0] in 'Ll':
			rel_flag = cmd[0] == 'l'
			points = [cmd[1][i:i + 2] for i in range(0, len(cmd[1]), 2)]
			for point in points:
				if rel_flag:
					point = add_points(base_point(cpoint), point)
				path[1].append(point)
				cpoint = point
		elif cmd[0] in 'Hh':
			rel_flag = cmd[0] == 'h'
			for x in cmd[1]:
				dx, y = base_point(cpoint)
				if rel_flag: point = [x + dx, y]
				else:point = [x, y]
				path[1].append(point)
				cpoint = point
		elif cmd[0] in 'Vv':
			rel_flag = cmd[0] == 'v'
			for y in cmd[1]:
				x, dy = base_point(cpoint)
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
					p2 = add_points(base_point(cpoint), point[0])
					p3 = add_points(base_point(cpoint), point[1])
				else:
					p2, p3 = point
				point = [p1, p2, p3]
				qpoint = [] + point
				qpoint.append(sk2_const.NODE_CUSP)
				path[1].append(qpoint)
				cpoint = point

		elif cmd[0] in 'Qq':
			rel_flag = cmd[0] == 'q'
			groups = [cmd[1][i:i + 4] for i in range(0, len(cmd[1]), 4)]
			for vals in groups:
				p = base_point(cpoint)
				if rel_flag:
					q = add_points(p, [vals[0], vals[1]])
					p3 = add_points(p, [vals[2], vals[3]])
				else:
					q = [vals[0], vals[1]]
					p3 = [vals[2], vals[3]]
				p1 = add_points(mult_point(p, F13), mult_point(q, F23))
				p2 = add_points(mult_point(p3, F13), mult_point(q, F23))

				point = [p1, p2, p3]
				qpoint = [] + point
				qpoint.append(sk2_const.NODE_CUSP)
				path[1].append(qpoint)
				cpoint = point
				last_quad = q

		elif cmd[0] in 'Tt':
			rel_flag = cmd[0] == 't'
			groups = [cmd[1][i:i + 2] for i in range(0, len(cmd[1]), 2)]
			if last_cmd not in 'QqTt' or last_quad is None:
				last_quad = base_point(cpoint)
			for vals in groups:
				p = base_point(cpoint)
				q = sub_points(mult_point(p, 2.0), last_quad)
				if rel_flag:
					p3 = add_points(p, [vals[0], vals[1]])
				else:
					p3 = [vals[0], vals[1]]
				p1 = add_points(mult_point(p, F13), mult_point(q, F23))
				p2 = add_points(mult_point(p3, F13), mult_point(q, F23))

				point = [p1, p2, p3]
				qpoint = [] + point
				qpoint.append(sk2_const.NODE_CUSP)
				path[1].append(qpoint)
				cpoint = point
				last_quad = q

		elif cmd[0] in 'Aa':
			rel_flag = cmd[0] == 'a'
			arcs = [cmd[1][i:i + 7] for i in range(0, len(cmd[1]), 7)]

			for arc in arcs:
				cpoint = base_point(cpoint)
				rev_flag = False
				rx, ry, xrot, large_arc_flag, sweep_flag, x, y = arc
				rx = abs(rx)
				ry = abs(ry)
				if rel_flag:
					x += cpoint[0]
					y += cpoint[1]
				if cpoint == [x, y]: continue
				if not rx or not ry:
					path[1].append([x, y])
					continue

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

		last_cmd = cmd[0]

	if path:paths.append(path)
	return paths

def parse_svg_stops(stops, current_color):
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

		clr = parse_svg_color(sclr, alpha, current_color)
		sk2_stops.append([offset, clr])
	return sk2_stops

def parse_svg_text(objs):
	ret = ''
	for obj in objs:
		if obj.is_content():
			ret += obj.text.lstrip()
		elif obj.childs:
			ret += parse_svg_text(obj.childs)
	return ret
