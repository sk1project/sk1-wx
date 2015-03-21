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

from uc2 import libimg, libcairo, libgeom
from uc2.formats.sk2 import sk2_model as model

CAIRO_BLACK = [0.0, 0.0, 0.0]
CAIRO_GRAY = [0.5, 0.5, 0.5]
CAIRO_WHITE = [1.0, 1.0, 1.0]

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
		if obj.cid > model.PRIMITIVE_CLASS:
			self.render_primitives(ctx, obj)
		elif obj.cid == model.GROUP:
			for obj in obj.childs:
				self.render_object(ctx, obj)
		elif obj.cid == model.CONTAINER:
				self.render_container(ctx, obj)
		else:
			pass

	def render_container(self, ctx, obj):
		ctx.save()
		container = obj.cache_container
		ctx.new_path()
		ctx.append_path(container.cache_cpath)
		ctx.clip()
		for obj in obj.childs:
			self.render_object(ctx, obj)
		ctx.restore()
		if container.style[1] and not self.contour_flag:
			ctx.new_path()
			self.process_stroke(ctx, container.style)
			ctx.append_path(container.cache_cpath)
			ctx.stroke()

	def render_image(self, ctx, obj):
		if not obj.cache_cdata: libimg.update_image(self.cms, obj)

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
			ctx.set_source_surface(obj.cache_cdata)
			if zoom * abs(m11) > .98:
				ctx.get_source().set_filter(cairo.FILTER_NEAREST)
			ctx.paint()

		ctx.set_matrix(canvas_matrix)

	def render_primitives(self, ctx, obj):
		if obj.cache_cpath is None:
			obj.update()
		if obj.cid == model.PIXMAP:
			self.render_image(ctx, obj)
			return
		if self.contour_flag:
			ctx.new_path()
			self.process_stroke(ctx, self.stroke_style)
			ctx.append_path(obj.cache_cpath)
			ctx.stroke()
		else:
			if obj.style[0]:
				ctx.new_path()
				self.process_fill(ctx, obj.style)
				ctx.append_path(obj.cache_cpath)
				ctx.fill()
			if obj.style[1]:
				ctx.new_path()
				self.process_stroke(ctx, obj.style)
				ctx.append_path(obj.cache_cpath)
				ctx.stroke()

	def process_fill(self, ctx, style):
		fill = style[0]
		color = fill[2]
		fill_rule = fill[0]
		if fill_rule:
			ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
		else:
			ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
		try:
			ctx.set_source_rgba(*self.get_color(color))
		except:
			pass

	def process_stroke(self, ctx, style):
		stroke = style[1]
		#FIXME: add stroke style

		ctx.set_line_width(stroke[1])

		color = stroke[2]

		try:
			ctx.set_source_rgba(*self.get_color(color))
		except:
			pass

		ctx.set_dash(stroke[3])
		ctx.set_line_cap(stroke[4])
		ctx.set_line_join(stroke[5])
		ctx.set_miter_limit(stroke[6])
