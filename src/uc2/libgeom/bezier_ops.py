# -*- coding: utf-8 -*-
#
#	Copyright (C) 2015 by Igor E. Novikov
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

from uc2.formats.sk2 import sk2_const

from flattering import flat_path
from points import distance

def get_path_length(path):
	fpath = flat_path(path)
	points = [fpath[0], ] + fpath[1]
	if fpath[2] == sk2_const.CURVE_CLOSED:
		points += [fpath[0], ]
	ret = 0
	start = []
	for item in points:
		if not start:
			start = item
			continue
		ret += distance(start, item)
		start = item
	return ret

def get_paths_length(paths):
	ret = 0
	for item in paths:
		ret += get_path_length(item)
	return ret

#This is called the "knot insertion problem". For Bézier curves, the de Casteljau algorithm will give you
#the right answer. Here is the simple algorithm for a degree 3 Bézier.
#
#Say you want to insert a knot at a fraction t of the parameter space inside the Bézier curve defined
#by P0, P1, P2, P3. Here's what you do:
#
#P0_1 = (1-t)*P0 + t*P1
#P1_2 = (1-t)*P1 + t*P2
#P2_3 = (1-t)*P2 + t*P3
#
#P01_12 = (1-t)*P0_1 + t*P1_2
#P12_23 = (1-t)*P1_2 + t*P2_3
#
#P0112_1223 = (1-t)*P01_12 + t*P12_23
#Then your first Bézier will be defined by: P_0, P0_1, P01_12, P0112_1223; your second Bézier is
#defined by: P0112_1223, P12_23, P2_3, P3.
#
#The geometrical interpretation is simple: you split each segment of the Bézier polygon at fraction t,
#then connect these split points in a new polygon and iterate. When you're left with 1 point, this point
#lies on the curve and the previous/next split points form the previous/next Bézier polygon. The same
#algorithm also works for higher degree Bézier curves.
#
#Now it can get trickier if you want to insert the control point not at a specific value of t but at a specific
#location in space. Personally, what I would do here is simply a binary search for a value of t that falls
#close to the desired split point... But if performance is critical, you can probably find a faster analytic
#solution.
