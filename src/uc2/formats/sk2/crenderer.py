# -*- coding: utf-8 -*-
#
#	Copyright (C) 2011-2015 by Igor E. Novikov
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

import cairo
from base64 import b64decode
from copy import deepcopy

from uc2 import libimg, libcairo, libgeom
from uc2.formats.sk2 import sk2_model
from uc2.formats.sk2 import sk2_const

CAIRO_BLACK = [0.0, 0.0, 0.0]
CAIRO_GRAY = [0.5, 0.5, 0.5]
CAIRO_WHITE = [1.0, 1.0, 1.0]

CAPS = {
	sk2_const.CAP_BUTT:cairo.LINE_CAP_BUTT,
	sk2_const.CAP_ROUND:cairo.LINE_CAP_ROUND,
	sk2_const.CAP_SQUARE:cairo.LINE_CAP_SQUARE,
	}

JOINS = {
	sk2_const.JOIN_BEVEL:cairo.LINE_JOIN_BEVEL,
	sk2_const.JOIN_MITER:cairo.LINE_JOIN_MITER,
	sk2_const.JOIN_ROUND:cairo.LINE_JOIN_ROUND,
	}

class CairoRenderer:

	cms = None
	antialias_flag = True
	contour_flag = False
	stroke_style = []
	for_display = False

	def __init__(self, cms):
		self.cms = cms

	#-------ROUTINES----------

	def get_color(self, color):
		"""
		Provides Cairo suitable, CMS processed color values. 
		"""
		if self.for_display:
			r, g, b = self.cms.get_display_color(color)
		else:
			r, g, b = self.cms.get_rgb_color(color)[1]
		return r, g, b, color[2]

	def get_image(self, pixmap):
		if not pixmap.cache_cdata:
			libimg.update_image(self.cms, pixmap)
		return pixmap.cache_cdata

	#-------DOCUMENT RENDERING

	def render(self, ctx, objs=[]):

		if self.antialias_flag:
			ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)
		else:
			ctx.set_antialias(cairo.ANTIALIAS_NONE)

		if objs:
			for obj in objs:
				self.render_object(ctx, obj)

	def render_object(self, ctx, obj):
		if obj.is_primitive():
			self.render_primitives(ctx, obj)
		elif obj.is_container():
				self.render_container(ctx, obj)
		elif obj.is_group():
			for obj in obj.childs:
				self.render_object(ctx, obj)
		else:
			pass

	def render_container(self, ctx, obj):
		ctx.save()
		container = obj.cache_container

		if container.style[1] and not self.contour_flag \
		and container.style[1][7]:
			ctx.new_path()
			self.process_stroke(ctx, None, container.style)
			ctx.append_path(container.cache_cpath)
			ctx.stroke()

		if container.style[0] and not self.contour_flag:
			ctx.new_path()
			self.process_fill(ctx, container)
			ctx.append_path(container.cache_cpath)
			ctx.fill()

		ctx.new_path()
		ctx.append_path(container.cache_cpath)
		ctx.clip()
		for obj in obj.childs[1:]:
			self.render_object(ctx, obj)
		ctx.restore()

		if container.style[1] and not self.contour_flag and \
		not container.style[1][7]:
			ctx.new_path()
			self.process_stroke(ctx, None, container.style)
			ctx.append_path(container.cache_cpath)
			ctx.stroke()
		elif self.contour_flag:
			ctx.new_path()
			self.process_stroke(ctx, None, self.stroke_style)
			ctx.append_path(container.cache_cpath)
			ctx.stroke()

	def render_image(self, ctx, obj):
		canvas_matrix = ctx.get_matrix()
		canvas_trafo = libcairo.get_trafo_from_matrix(canvas_matrix)
		zoom = canvas_trafo[0]

		h = obj.size[1]
		lu_corner = libgeom.apply_trafo_to_point([0.0, float(h)], obj.trafo)
		x0, y0 = libgeom.apply_trafo_to_point(lu_corner, canvas_trafo)

		m11, m12, m21, m22 = obj.trafo[:4]
		matrix = cairo.Matrix(zoom * m11, -zoom * m12,
							- zoom * m21, zoom * m22, x0, y0)
		ctx.set_matrix(matrix)

		if self.contour_flag:
			if not obj.cache_gray_cdata:
				libimg.update_gray_image(self.cms, obj)
			ctx.set_source_surface(obj.cache_gray_cdata)
			if zoom * abs(m11) > .98:
				ctx.get_source().set_filter(cairo.FILTER_NEAREST)
			ctx.paint_with_alpha(0.3)
		else:
			ctx.set_source_surface(self.get_image(obj))
			if zoom * abs(m11) > .98:
				ctx.get_source().set_filter(cairo.FILTER_NEAREST)
			ctx.paint()

		ctx.set_matrix(canvas_matrix)

	def render_primitives(self, ctx, obj):
		if obj.cache_cpath is None:
			obj.update()
		if obj.is_pixmap():
			self.render_image(ctx, obj)
			return
		if obj.is_text():
			if self.contour_flag:
				self.process_stroke(ctx, None, self.stroke_style)
				for item in obj.cache_cpath:
					if item:
						ctx.new_path()
						ctx.append_path(item)
						ctx.stroke()
			else:
				if obj.style[1] and obj.style[1][7]:
					self.stroke_text_obj(ctx, obj)
					self.fill_text_obj(ctx, obj)
				else:
					self.fill_text_obj(ctx, obj)
					self.stroke_text_obj(ctx, obj)
			return

		if self.contour_flag:
			ctx.new_path()
			self.process_stroke(ctx, None, self.stroke_style)
			ctx.append_path(obj.cache_cpath)
			ctx.stroke()
		else:
			if obj.style[1] and obj.style[1][7]:
				self.stroke_obj(ctx, obj)
				self.fill_obj(ctx, obj)
			else:
				self.fill_obj(ctx, obj)
				self.stroke_obj(ctx, obj)

	def fill_obj(self, ctx, obj):
		if obj.style[0]:
			ctx.new_path()
			self.process_fill(ctx, obj)
			ctx.append_path(obj.cache_cpath)
			ctx.fill()

	def fill_text_obj(self, ctx, obj):
		if obj.style[0]:
			self.process_fill(ctx, obj)
			for item in obj.cache_cpath:
				if not item is None:
					ctx.new_path()
					ctx.append_path(item)
					ctx.fill()

	def stroke_obj(self, ctx, obj):
		if obj.style[1]:
			ctx.new_path()
			self.process_stroke(ctx, obj)
			ctx.append_path(obj.cache_cpath)
			ctx.stroke()

	def stroke_text_obj(self, ctx, obj):
		if obj.style[1]:
			self.process_stroke(ctx, obj)
			for item in obj.cache_cpath:
				if not item is None:
					ctx.new_path()
					ctx.append_path(item)
					ctx.stroke()

	def process_fill(self, ctx, obj):
		fill = obj.style[0]
		fill_rule = fill[0]
		if fill_rule & sk2_const.FILL_CLOSED_ONLY and not obj.is_closed():
			ctx.set_source_rgba(0.0, 0.0, 0.0, 0.0)
			return
		if fill_rule & sk2_const.FILL_EVENODD:
			ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
		else:
			ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
		if fill[1] == sk2_const.FILL_SOLID:
			if obj.fill_trafo: obj.fill_trafo = []
			color = fill[2]
			ctx.set_source_rgba(*self.get_color(color))
		elif fill[1] == sk2_const.FILL_GRADIENT:
			if not obj.fill_trafo:
				obj.fill_trafo = [] + sk2_const.NORMAL_TRAFO
			gradient = fill[2]
			points = gradient[1]
			if not points:
				obj.fill_trafo = [] + sk2_const.NORMAL_TRAFO
				points = libgeom.bbox_middle_points(obj.cache_bbox)
				if gradient[0] == sk2_const.GRADIENT_LINEAR:
					points = [points[0], points[2]]
				else:
					points = [[points[1][0], points[2][1]], points[2]]
				gradient[1] = points
			coords = points[0] + points[1]
			if gradient[0] == sk2_const.GRADIENT_LINEAR:
				grd = cairo.LinearGradient(*coords)
			else:
				x0, y0 = coords[:2]
				radius = libgeom.distance(*points)
				grd = cairo.RadialGradient(x0, y0, 0, x0, y0, radius)
			for stop in gradient[2]:
				grd.add_color_stop_rgba(stop[0], *self.get_color(stop[1]))
			matrix = cairo.Matrix(*obj.fill_trafo)
			matrix.invert()
			grd.set_matrix(matrix)
			ctx.set_source(grd)
		elif fill[1] == sk2_const.FILL_PATTERN:
			if not obj.fill_trafo:
				obj.fill_trafo = [] + sk2_const.NORMAL_TRAFO
				obj.fill_trafo = obj.fill_trafo[:4] + \
					[obj.cache_bbox[0], obj.cache_bbox[3]]
			pattern_fill = fill[2]
			if not obj.cache_pattern_img:
				bmpstr = b64decode(pattern_fill[1])
				image_obj = sk2_model.Pixmap(obj.config)
				libimg.set_image_data(self.cms, image_obj, bmpstr)
				libimg.flip_top_to_bottom(image_obj)
				if pattern_fill[0] == sk2_const.PATTERN_IMG and \
				 len(pattern_fill) > 2:
					image_obj.style[3] = deepcopy(pattern_fill[2])
				libimg.update_image(self.cms, image_obj)
				obj.cache_pattern_img = image_obj.cache_cdata
				image_obj.cache_cdata = None
			sp = cairo.SurfacePattern(obj.cache_pattern_img)
			sp.set_extend(cairo.EXTEND_REPEAT)
			flip_matrix = cairo.Matrix(1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
			if len(pattern_fill) > 3:
				pattern_matrix = cairo.Matrix(*pattern_fill[3])
				pattern_matrix.invert()
				flip_matrix = flip_matrix * pattern_matrix
			trafo_matrix = cairo.Matrix(*obj.fill_trafo)
			trafo_matrix.invert()
			flip_matrix = flip_matrix * trafo_matrix
			sp.set_matrix(flip_matrix)
			ctx.set_source(sp)

			canvas_matrix = ctx.get_matrix()
			canvas_trafo = libcairo.get_trafo_from_matrix(canvas_matrix)
			zoom = canvas_trafo[0]
			if zoom * abs(obj.fill_trafo[0]) > .98:
				ctx.get_source().set_filter(cairo.FILTER_NEAREST)

	def process_stroke(self, ctx, obj, style=None):
		if style: stroke = style[1]
		else: stroke = obj.style[1]
		#FIXME: add stroke style

		#Line width
		if not stroke[8]:
			line_width = stroke[1]
			if obj and obj.stroke_trafo: obj.stroke_trafo = []
		else:
			if obj and not obj.stroke_trafo:
				obj.stroke_trafo = [] + sk2_const.NORMAL_TRAFO
			points = [[0.0, 0.0], [1.0, 0.0]]
			points = libgeom.apply_trafo_to_points(points, obj.stroke_trafo)
			coef = libgeom.distance(*points)
			line_width = stroke[1] * coef
		ctx.set_line_width(line_width)
		#Line color
		ctx.set_source_rgba(*self.get_color(stroke[2]))
		#Dashes
		dash = []
		for item in stroke[3]:dash.append(item * line_width)
		ctx.set_dash(dash)

		ctx.set_line_cap(CAPS[stroke[4]])
		ctx.set_line_join(JOINS[stroke[5]])
		ctx.set_miter_limit(stroke[6])
