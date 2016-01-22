# -*- coding: utf-8 -*-
#
#	Copyright (C) 2016 by Igor E. Novikov
#	Copyright (C) 2003 Simon Budig  <simon@gimp.org>
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

import math
from copy import deepcopy

from uc2.formats.sk2 import sk2_const
from points import distance, mult_point, add_points, sub_points
from bezier_ops import bezier_base_point
from shaping import fuse_paths


# This constant is used to calculate the length of the bezier
# tangents to approximate a circle.

CIRCLE_CONSTANT = 4.0 / 3.0 * (math.sqrt (2) - 1)
MITER_LIMIT = 10.433


def length(p):
	"""
	Convenience function to make the code more readable. Returns
	the length of a Vector from the origin to the given Point
	"""
	return distance(p)


def subdivide(p, t=0.5):
	assert len (p) == 4
	p01 = p[0] * (1 - t) + p[1] * t
	p12 = p[1] * (1 - t) + p[2] * t
	p23 = p[2] * (1 - t) + p[3] * t
	p012 = p01 * (1 - t) + p12 * t
	p123 = p12 * (1 - t) + p23 * t
	p0123 = p012 * (1 - t) + p123 * t
	return (p[0], p01, p012, p0123, p123, p23, p[3])


def subdivide_seg(seg, t=0.5):
	"""
	This subdivides a bezier segment at the (optional) Parameter t
	"""
	assert len(seg) == 4
	t2 = 1.0 - t
	p01 = add_points(mult_point(seg[0], t2) , mult_point(seg[1], t))
	p12 = add_points(mult_point(seg[1], t2), mult_point(seg[2], t))
	p23 = add_points(mult_point(seg[2], t2), mult_point(seg[3], t))
	p012 = add_points(mult_point(p01, t2), mult_point(p12, t))
	p123 = add_points(mult_point(p12, t2), mult_point(p23, t))
	p0123 = add_points(mult_point(p012, t2), mult_point(p123, t))
	return (seg[0], p01, p012, p0123, p123, p23, seg[3])


def circleparam(h):
	"""
	For joining lines we need circle-segments with arbitrary
	angles, we need to subdivide the approximating bezier segments.
	Iterative approach to determine at what parameter t0 you have
	to subdivide a circle segment to get height h.	
	"""
	t0 = 0.5
	dt = 0.25
	while dt >= 0.0001:
		pt0 = subdivide([0, CIRCLE_CONSTANT, 1, 1], t0)[3]
		if pt0 > h: t0 = t0 - dt
		elif pt0 < h: t0 = t0 + dt
		else: break
		dt = dt / 2
	return t0


def normalize(point):
	"""
	Returns a unit vector pointing in the same direction.
	"""
	k = distance(point)
	return [point[0] / k, point[1] / k]


def check_parallel(source, parallel, radius, tolerance=0.01):
	"""
	This function checks, if two bezier segments are "sufficiently"
	parallel. It checks, if the points for the parameters 0.25, 0.5
	and 0.75 of the tested segment are orthogonal to the resp.
	points of the source segment. 1% tolerance is default.
	
	It does not check the start and endpoints, since they are
	assumed to be correct by construction.
	"""
	for t0 in [0.25, 0.5, 0.75]:
		s = subdivide_seg(source, t0)
		t = subdivide_seg(parallel, t0)
		ccenter = mult_point(normalize(sub_points(s[4], s[3])), radius)
		orig = add_points(s[3], [ccenter[1], -ccenter[0]])
		if length(sub_points(orig, t[3])) >= tolerance * radius: return False
	return True


def build_parallel(p, radius, recursionlimit=6):
	"""
	This builds a list of bezier segments that are "sufficiently"
	close to a given source segment. It recursively subdivides, if
	the check for parallelity fails.	
	"""
	# find tangent to calculate orthogonal neighbor of endpoint
	for i in p[1:]:
		c1 = sub_points(i, p[0])
		if c1: break

	if c1 == [0, 0]: return []

	t1 = mult_point(normalize(c1), radius)
	p0 = add_points(p[0], [t1[1], -t1[0]])
	c1 = sub_points(p[1], p[0])

	for i in [p[2], p[1], p[0]]:
		c2 = sub_points(p[3], i)
		if not c2 == [0, 0]: break

	t2 = mult_point(normalize(c2), radius)
	p3 = add_points(p[3], [t2[1], -t2[0]])
	c2 = sub_points(p[3], p[2])

	sd = subdivide_seg(p)
	center = sd[3]
	ccenter = mult_point(normalize(sub_points(sd[4], sd[3])), radius)

	new_center = add_points(center, [ccenter[1], -ccenter[0]])
	seg = [p0, add_points(p0, c1), sub_points(p3, c2), p3]
	now_center = subdivide_seg(seg)[3]

	offset = mult_point(sub_points(new_center, now_center), 8.0 / 3)

	det = c1[0] * c2[1] - c1[1] * c2[0]
	if det:
		ndet = det / length(c1) / length(c2)
	else:
		ndet = 0

	if math.fabs(ndet) >= 0.1:
		# "sufficiently" linear independent, cramers rule:
		oc1 = mult_point(c1, ((offset[0] * c2[1] - offset[1] * c2[0]) / det))
		oc2 = mult_point(c2, ((c1[0] * offset[1] - c1[1] * offset[0]) / det))
	else:
		# don't bother to try to correct the error, will figure out
		# soon if subdivision is necessary.
		oc1 = [0.0, 0.0]
		oc2 = [0.0, 0.0]

	new_p1 = add_points(add_points(p0, c1), oc1)
	new_p2 = add_points(sub_points(p3, c2), oc2)
	proposed_segment = [p0, new_p1, new_p2, p3]
	if check_parallel (p, proposed_segment, radius) or recursionlimit <= 0:
		return proposed_segment
	else:
		# "Not parallel enough" - subdivide.
		return (build_parallel (sd[:4], radius, recursionlimit - 1) +
				  build_parallel (sd[3:], radius, recursionlimit - 1)[1:])


def get_join_segment(startpoint, endpoint, radius, jointype,
					miter_limit=MITER_LIMIT):
	"""
	This returns a list of bezier segments that joins two points
	with a given radius (fails if the radius is smaller than the
	distance between startpoint) and endpoint). 
	jointype is one of 	JOIN_MITER, JOIN_ROUND, JOIN_BEVEL	
	"""

	if jointype == sk2_const.JOIN_MITER:
		d = mult_point(sub_points(endpoint, startpoint), 0.5)

		if d == [0, 0]: return []

		o = normalize([d[1], -d[0]])
		h = math.sqrt(radius ** 2 - length(d) ** 2)

		h2 = length(d) ** 2 / h

		# Hmm - Postscript defines 10 as miter limit...
		if h2 + h > miter_limit * radius:
			# Hit miter limit
			return [startpoint, endpoint]

		edge = add_points(add_points(startpoint, d), mult_point(o, h2))

		return [startpoint, startpoint, edge, edge, edge, endpoint, endpoint]

	elif jointype == sk2_const.JOIN_ROUND:
		f = CIRCLE_CONSTANT
		d = mult_point(sub_points(endpoint, startpoint), 0.5)

		if d == [0, 0]: return []

		o = mult_point(normalize([d[1], -d[0]]), radius)

		h = math.sqrt(radius ** 2 - length(d) ** 2) / radius

		center = sub_points(add_points(startpoint, d), mult_point(o, h))
		d = mult_point(normalize(d), radius)

		t0 = circleparam(h)
		quadseg = [sub_points(center, d),
					add_points(sub_points(center, d), mult_point(o, f)),
					add_points(sub_points(center, mult_point(d, f)), o),
					add_points(center, o)]
		ret = [startpoint] + list (subdivide_seg(quadseg, t0)[4:])

		quadseg = [add_points(center, o),
					add_points(add_points(center, o), mult_point(d, f)),
					add_points(add_points(center, d), mult_point(o, f)),
					add_points(center, d)]
		ret = ret + list (subdivide(quadseg, 1 - t0)[1:3]) + [endpoint]

		return ret

	elif jointype == sk2_const.JOIN_BEVEL:
		return [startpoint, endpoint]

	else:
		raise "Unknown join type %d" % jointype


def get_cap_segment (startpoint, endpoint, captype):
	"""
	This returns a list of bezier segments that form the end cap of
	a line. Valid captypes are: CAP_BUTT, CAP_ROUND, CAP_SQUARE	
	"""

	#  =====|
	if captype == sk2_const.CAP_BUTT:
		return [startpoint, endpoint]

	#  =====)
	elif captype == sk2_const.CAP_ROUND:
		f = CIRCLE_CONSTANT
		d = mult_point(sub_points(endpoint, startpoint), 0.5)
		o = [d[1], -d[0]]

		new_p1 = add_points(startpoint, o)
		new_p2 = mult_point(o, f)

		return [startpoint,
				add_points(startpoint, new_p2),
				add_points(new_p1, mult_point(d, 1 - f)),
				add_points(new_p1, d),
				add_points(new_p1, mult_point(d, 1 + f)),
				add_points(endpoint, new_p2),
				endpoint]

	#  =====]
	elif captype == sk2_const.CAP_SQUARE:
		d = mult_point(sub_points(endpoint, startpoint), 0.5)
		o = [d[1], -d[0]]

		new_p1 = add_points(startpoint, o)
		new_p2 = add_points(endpoint, o)

		return [startpoint, startpoint, new_p1, new_p1, new_p1,
				new_p2, new_p2, new_p2, endpoint, endpoint]

	else:
		raise "Unknown captype %d" % captype

def unpack_seg(seg):
	if len(seg) > 2: return [True, [seg[0], seg[1]] , seg[2], seg[3]]
	return [False, None, seg, None]

def create_stroke_outline (path, radius, linejoin=sk2_const.JOIN_MITER,
						captype=sk2_const.CAP_BUTT, miter_limit=MITER_LIMIT):
	"""
	Outlines a single stroke. Returns two lists of lists of bezier
	segments for both sides of the stroke.
	"""
	fw_segments = []
	bw_segments = []

	last_point = None

	segs = [path[0], ] + path[1]

	for i in range (len(segs)):
		segment = unpack_seg(segs[i])
		if not segment[0]:
			if last_point:
				c1 = sub_points(segment[2], last_point)
				if not c1 == [0.0]:
					t1 = mult_point(normalize(c1), radius)
					fw_segments.append (
								[add_points(last_point, [t1[1], -t1[0]]),
								 add_points(segment[2], [t1[1], -t1[0]])])
					bw_segments.insert (0,
								[sub_points(segment[2], [t1[1], -t1[0]]),
								 sub_points(last_point, [t1[1], -t1[0]])])
			last_point = segment[2]

		else:
			segments = build_parallel ([last_point, segment[1][0],
										segment[1][1], segment[2]], radius)
			fw_segments.append (segments)

			segments = build_parallel ([segment[2], segment[1][1],
										segment[1][0], last_point], radius)
			bw_segments.insert (0, segments)
			last_point = segment[2]

	# fix the connections between the parallels if necessary
	i = 0
	while i < len (fw_segments) - 1:
		if fw_segments[i][-1] != fw_segments[i + 1][0]:
			fw_segments.insert (i + 1, get_join_segment (fw_segments[i][-1],
						fw_segments[i + 1][0], radius, linejoin, miter_limit))
			i += 1
		i += 1


	i = 0
	while i < len (bw_segments) - 1:
		if bw_segments[i][-1] != bw_segments[i + 1][0]:
			bw_segments.insert (i + 1, get_join_segment (bw_segments[i][-1],
						bw_segments[i + 1][0], radius, linejoin, miter_limit))
			i += 1
		i += 1


	# fix the connection between both sides of a stroke.
	# depends on the state of the path.

	if path[2]:
		if fw_segments[0][0] != fw_segments[-1][-1]:
			fw_segments.append (get_join_segment (fw_segments[-1][-1],
						fw_segments[0][0], radius, linejoin, miter_limit))
		if bw_segments[0][0] != bw_segments[-1][-1]:
			bw_segments.append (get_join_segment (bw_segments[-1][-1],
						bw_segments[0][0], radius, linejoin, miter_limit))
	else:
		fw_segments.insert (0, get_cap_segment (bw_segments[-1][-1],
									fw_segments[0][0], captype))
		bw_segments.insert (0, get_cap_segment (fw_segments[-1][-1],
									bw_segments[0][0], captype))

	return fw_segments, bw_segments


def make_path(segments, close=1):
	"""
	This function prepares a path given by a list of lists of
	coordinates for the use with app.	
	"""
	first_point = segments[0][0]
	last_point = first_point

	new_path = [[] + first_point, [], sk2_const.CURVE_OPENED]
	points = new_path[1]
	for seg in segments:
		if seg[0] != last_point:
			print "Need to fix up! Should not happen."
			points.append(deepcopy(seg[0]))

		if len (seg) == 2:
			points.append(deepcopy(seg[1]))
			last_point = seg[1]

		while len (seg) >= 4:
			points.append(deepcopy([seg[1], seg[2], seg[3],
								sk2_const.NODE_CUSP]))
			last_point = seg[3]
			seg = seg[3:]

	if close:
		new_path[2] = sk2_const.CURVE_CLOSED
		if not new_path[0] == bezier_base_point(points[-1]):
			points.append(deepcopy(new_path[0]))

	return new_path


#--- MODULE INTERFACE

def stroke_to_curve(paths, stroke_style):
	if not stroke_style: return []
	width = stroke_style[1]
	#TODO: dash processing needs to be implemented
	dash = stroke_style[3]
	caps = stroke_style[4]
	joint = stroke_style[5]
	miter_limit = stroke_style[6]

	new_paths = []
	for path in paths:
		outlines = []
		fw, bw = create_stroke_outline(path, width / 2.0,
									joint, caps, miter_limit)
		if path[-1] == sk2_const.CURVE_CLOSED:
			outlines.append(make_path(fw))
			outlines.append(make_path(bw))
		else:
			outlines.append(make_path(fw + bw))
		new_paths.append(outlines)
	if len(new_paths) == 1:
		return new_paths[0]
	else:
		ret = new_paths[0]
		for item in new_paths[1:]:
			ret = fuse_paths(ret, item)
		return ret
