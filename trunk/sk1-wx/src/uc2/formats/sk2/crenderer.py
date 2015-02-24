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

from uc2.formats.sk2 import sk2_model as model

CAIRO_BLACK = [0.0, 0.0, 0.0]
CAIRO_GRAY = [0.5, 0.5, 0.5]
CAIRO_WHITE = [1.0, 1.0, 1.0]

class CairoRenderer:

	cms = None
	antialias_flag = True
	contour_flag = False
	stroke_style = []

	def __init__(self, cms):
		self.cms = cms

	#-------ROUTINES----------

	def get_color(self, color):
		"""
		Provides Cairo suitable, CMS processed color values. 
		"""
		r, g, b = self.cms.get_display_color(color)
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

	def render_object(self, ctx, object):
		if object.cid > model.PRIMITIVE_CLASS:
			self.render_primitives(ctx, object)
		elif object.cid == model.GROUP:
			for obj in object.childs:
				self.render_object(ctx, obj)
		elif object.cid == model.CONTAINER:
				self.render_container(ctx, object)
		else:
			pass

	def render_container(self, ctx, object):
		ctx.save()
		container = object.cache_container
		ctx.new_path()
		ctx.append_path(container.cache_cpath)
		ctx.clip()
		for obj in object.childs:
			self.render_object(ctx, obj)
		ctx.restore()
		if container.style[1] and not self.contour_flag:
			ctx.new_path()
			self.process_stroke(ctx, container.style)
			ctx.append_path(container.cache_cpath)
			ctx.stroke()

	def render_primitives(self, ctx, object):
		if object.cache_cpath is None:
			object.update()
		if self.contour_flag:
			ctx.new_path()
			self.process_stroke(ctx, self.stroke_style)
			ctx.append_path(object.cache_cpath)
			ctx.stroke()
		else:
			if object.style[0]:
				ctx.new_path()
				self.process_fill(ctx, object.style)
				ctx.append_path(object.cache_cpath)
				ctx.fill()
			if object.style[1]:
				ctx.new_path()
				self.process_stroke(ctx, object.style)
				ctx.append_path(object.cache_cpath)
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
