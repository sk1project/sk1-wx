# -*- coding: utf-8 -*-
#
#	Copyright (C) 2011-2012 by Igor E. Novikov
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

from copy import deepcopy

import cairo, math, wx

from uc2 import uc2const
from uc2.formats.sk2 import sk2_const
from uc2.formats.sk2.crenderer import CairoRenderer
from uc2 import libcairo, libgeom

from wal import copy_surface_to_bitmap

from sk1 import config

CAIRO_BLACK = [0.0, 0.0, 0.0]
CAIRO_GRAY = [0.0, 0.0, 0.0, 0.5]
CAIRO_WHITE = [1.0, 1.0, 1.0]

class PDRenderer(CairoRenderer):

	direct_matrix = None

	canvas = None
	ctx = None
	win_ctx = None
	surface = None
	presenter = None
	for_display = True

	frame = []
	snap = []
	guide = []

	width = 0
	height = 0

	def __init__(self, canvas):

		self.canvas = canvas
		self.direct_matrix = cairo.Matrix(1.0, 0.0, 0.0, 1.0, 0.0, 0.0)

	def destroy(self):
		items = self.__dict__.keys()
		for item in items:
			self.__dict__[item] = None

	#-------DOCUMENT RENDERING

	def paint_document(self):
		self.presenter = self.canvas.presenter
		self.doc_methods = self.presenter.methods
		self.cms = self.presenter.cms
		self.start()
		self.paint_page()
		self.render_doc()
		self.render_grid()
		self.render_guides()

	def start(self):
		width, height = self.canvas.GetSize()
		if self.surface is None:
			self.surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
			self.width = width
			self.height = height
		elif self.width <> width or self.height <> height:
			self.surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
			self.width = width
			self.height = height
		self.ctx = cairo.Context(self.surface)
		self.ctx.set_source_rgb(*self.doc_methods.get_desktop_bg())
		self.ctx.paint()
		self.ctx.set_matrix(self.canvas.matrix)

	def finalize(self):
		dc = wx.PaintDC(self.canvas)
		dc.DrawBitmap(copy_surface_to_bitmap(self.temp_surface), 0, 0, False)

	def paint_page(self):
		self.ctx.set_line_width(1.0 / self.canvas.zoom)
		offset = 5.0 / self.canvas.zoom
		w, h = self.presenter.get_page_size()
		border = self.doc_methods.get_page_border()
		if border:
			self.ctx.rectangle(-w / 2.0 + offset, -h / 2.0 - offset, w, h)
			self.ctx.set_source_rgba(*CAIRO_GRAY)
			self.ctx.fill()

		self.ctx.set_antialias(cairo.ANTIALIAS_NONE)
		page_fill = self.doc_methods.get_page_fill()
		if page_fill[0] == sk2_const.FILL_SOLID:
			self.ctx.rectangle(-w / 2.0, -h / 2.0, w, h)
			self.ctx.set_source_rgb(*page_fill[1])
			self.ctx.fill()
		else:
			units = self.doc_methods.get_doc_units()
			gdx = uc2const.unit_dict[units]
			dx = self.calc_grid(0.0, 0.0, gdx, gdx)[2] / self.canvas.zoom
			origin = self.doc_methods.get_doc_origin()
			sx = sy = 0.0
			if origin == sk2_const.DOC_ORIGIN_LU:
				sy = dx - (h - float(int(h / dx)) * dx)
			elif origin == sk2_const.DOC_ORIGIN_CENTER:
				sy = dx - (h / 2.0 - float(int(h / (2.0 * dx))) * dx)
				sx = dx - (w / 2.0 - float(int(w / (2.0 * dx))) * dx)

			self.ctx.save()
			self.ctx.rectangle(-w / 2.0, -h / 2.0, w, h)
			self.ctx.clip()

			self.ctx.rectangle(-w / 2.0, -h / 2.0, w, h)
			self.ctx.set_source_rgb(*page_fill[1][1])
			self.ctx.fill()

			self.ctx.set_source_rgb(*page_fill[1][0])

			ypos = ystart = -h / 2.0 - sy
			j = 0
			while ypos < h / 2.0:
				ypos = ystart + j * dx
				xpos = xstart = -w / 2.0 - sx
				i = 0
				if j % 2:xpos = xstart = -w / 2.0 + dx - sx
				while xpos < w / 2.0:
					xpos = xstart + i * dx * 2.0
					self.ctx.rectangle(xpos, ypos, dx, dx)
					self.ctx.fill()
					i += 1
				j += 1
			self.ctx.restore()

		if border:
			self.ctx.rectangle(-w / 2.0, -h / 2.0, w, h)
			self.ctx.set_source_rgb(*CAIRO_BLACK)
			self.ctx.stroke()
		self.ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)

	def render_doc(self):
		if self.canvas.draft_view:
			self.antialias_flag = False
		else:
			self.antialias_flag = True

		if self.canvas.stroke_view:
			self.contour_flag = True
		else:
			self.contour_flag = False

		page = self.presenter.active_page
		for layer in page.childs:
			if layer.properties[0]:
				if self.canvas.stroke_view:
					self.stroke_style = deepcopy(layer.style)
					stroke = self.stroke_style[1]
					stroke[1] = 1.0 / self.canvas.zoom
				if not layer.properties[3] and not self.canvas.draft_view:
					self.antialias_flag = False
				self.render(self.ctx, layer.childs)
				if not layer.properties[3] and not self.canvas.draft_view:
					self.antialias_flag = True


	#------GUIDES RENDERING
	def render_guides(self):
		guides = []
		methods = self.presenter.methods
		guide_layer = methods.get_guide_layer()
		if not methods.is_layer_visible(guide_layer): return
		for child in guide_layer.childs:
			if child.is_guide():
				guides.append(child)
		if guides:
			self.ctx.set_matrix(self.direct_matrix)
			self.ctx.set_antialias(cairo.ANTIALIAS_NONE)
			self.ctx.set_line_width(1.0)
			self.ctx.set_dash(config.guide_line_dash)
			self.ctx.set_source_rgba(*guide_layer.color)
			for item in guides:
				if item.orientation == uc2const.HORIZONTAL:
					y_win = self.canvas.point_doc_to_win([0, item.position])[1]
					self.ctx.move_to(0, y_win)
					self.ctx.line_to(self.width, y_win)
					self.ctx.stroke()
				else:
					x_win = self.canvas.point_doc_to_win([item.position, 0])[0]
					self.ctx.move_to(x_win, 0)
					self.ctx.line_to(x_win, self.height)
					self.ctx.stroke()

	#------GRID RENDERING
	def calc_grid(self, x, y, gdx, gdy):
		w, h = self.presenter.get_page_size()
		origin = self.presenter.model.doc_origin
		if origin == sk2_const.DOC_ORIGIN_LL:
			x0, y0 = self.canvas.point_doc_to_win([-w / 2.0 + x, -h / 2.0 + y])
		elif origin == sk2_const.DOC_ORIGIN_LU:
			x0, y0 = self.canvas.point_doc_to_win([-w / 2.0 + x, h / 2.0 + y])
		else:
			x0, y0 = self.canvas.point_doc_to_win([x, y])
		dx = gdx * self.canvas.zoom
		dy = gdy * self.canvas.zoom
		sdist = config.snap_distance

		i = 0.0
		while dx < sdist + 3:
			i = i + 0.5
			dx = dx * 10.0 * i
		if dx / 2.0 > sdist + 3 and \
		dx / 2.0 > gdx * self.canvas.zoom:
			dx = dx / 2.0

		i = 0.0
		while dy < sdist + 3:
			i = i + 0.5
			dy = dy * 10.0 * i
		if dy / 2.0 > sdist + 3 and \
		dy / 2.0 > gdy * self.canvas.zoom:
			dy = dy / 2.0

		sx = (x0 / dx - math.floor(x0 / dx)) * dx
		sy = (y0 / dy - math.floor(y0 / dy)) * dy

		return x0, y0, dx, dy, sx, sy


	def render_grid(self):
		methods = self.presenter.methods
		grid_layer = methods.get_grid_layer()
		if not methods.is_layer_visible(grid_layer):return

		self.ctx.set_matrix(self.direct_matrix)
		self.ctx.set_antialias(cairo.ANTIALIAS_NONE)
		self.ctx.set_source_rgba(*grid_layer.color)
		self.ctx.set_line_width(1.0)
		self.ctx.set_dash(())

		x, y, gdx, gdy = grid_layer.grid
		x0, y0, dx, dy, sx, sy = self.calc_grid(x, y, gdx, gdy)

		i = pos = 0
		nul_i = round((x0 - sx) / dx)
		while pos < self.width:
			pos = sx + i * dx
			i += 1
			self.ctx.move_to(pos, 0)
			self.ctx.line_to(pos, self.height)
			self.ctx.stroke()
			if dx == gdx * self.canvas.zoom and not (i - nul_i - 1) % 5:
				self.ctx.move_to(pos, 0)
				self.ctx.line_to(pos, self.height)
				self.ctx.stroke()

		i = pos = 0
		nul_i = round((y0 - sy) / dy)
		while pos < self.height:
			pos = sy + i * dy
			i += 1
			self.ctx.move_to(0, pos)
			self.ctx.line_to(self.width, pos)
			self.ctx.stroke()
			if dy == gdy * self.canvas.zoom and not (i - nul_i - 1) % 5:
				self.ctx.move_to(0, pos)
				self.ctx.line_to(self.width, pos)
				self.ctx.stroke()

		self.ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)

	#------MARKER RENDERING

	def start_soft_repaint(self):
		self.temp_surface = cairo.ImageSurface(cairo.FORMAT_RGB24,
								int(self.canvas.width),
								int(self.canvas.height))
		self.ctx = cairo.Context(self.temp_surface)
		self.ctx.set_source_surface(self.surface)
		self.ctx.paint()

	def end_soft_repaint(self):
		pass

	def draw_frame(self, start, end):
		if start and end:
			path = libcairo.convert_bbox_to_cpath(start + end)
			self._draw_frame(path)

	def draw_gradient_vector(self, start, end, stops=[]):
		self.ctx.set_matrix(self.direct_matrix)
		self.ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)
		self.ctx.set_source_rgba(*config.gradient_vector_bg_color)
		self.ctx.set_line_width(config.gradient_vector_width)
		self.ctx.set_dash([])
		self.ctx.move_to(*start)
		self.ctx.line_to(*end)
		self.ctx.stroke()
		self.ctx.set_source_rgba(*config.gradient_vector_fg_color)
		self.ctx.set_line_width(config.gradient_vector_width)
		self.ctx.set_dash(config.gradient_vector_dash)
		self.ctx.move_to(*start)
		self.ctx.line_to(*end)
		self.ctx.stroke()
		self.draw_curve_point(start, config.gradient_vector_point_size,
							config.gradient_vector_point_fill,
							config.gradient_vector_point_stroke,
							config.gradient_vector_point_stroke_width)
		self.draw_curve_point(end, config.gradient_vector_point_size,
							config.gradient_vector_point_fill,
							config.gradient_vector_point_stroke,
							config.gradient_vector_point_stroke_width)

	def set_direct_matrix(self):
		self.ctx.set_matrix(self.direct_matrix)

	def draw_regular_node(self, point, selected=False):
		fill = config.curve_point_fill
		if selected: fill = config.selected_node_fill
		self.draw_curve_point(point, config.curve_point_size, fill,
							config.curve_point_stroke,
							config.curve_point_stroke_width)

	def draw_start_node(self, point, selected=False):
		fill = config.curve_start_point_fill
		if selected: fill = config.selected_node_fill
		self.draw_curve_point(point, config.curve_start_point_size, fill,
							config.curve_start_point_stroke,
							config.curve_start_point_stroke_width)

	def draw_last_node(self, point, selected=False):
		fill = config.curve_last_point_fill
		if selected: fill = config.selected_node_fill
		self.draw_curve_point(point, config.curve_last_point_size, fill,
							config.curve_last_point_stroke,
							config.curve_last_point_stroke_width)

	def draw_control_point(self, start, end):
		self.ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)
		self.ctx.set_line_width(config.control_line_stroke_width)
		self.ctx.set_dash([])
		self.ctx.set_source_rgba(*config.control_line_bg_stroke_color)
		self.ctx.move_to(*start)
		self.ctx.line_to(*end)
		self.ctx.stroke()
		self.ctx.set_source_rgba(*config.control_line_stroke_color)
		self.ctx.set_dash(config.control_line_stroke_dash)
		self.ctx.move_to(*start)
		self.ctx.line_to(*end)
		self.ctx.stroke()
		self.draw_curve_point(end, config.control_point_size,
							config.control_point_fill,
							config.control_point_stroke,
							config.control_point_stroke_width)

	def draw_new_node(self, point):
		fill = config.curve_new_point_fill
		self.draw_curve_point(point, config.curve_new_point_size, fill,
							config.curve_new_point_stroke,
							config.curve_new_point_stroke_width)

	def draw_rect_midpoint(self, point):
		fill = config.rect_midpoint_fill
		self.draw_curve_point(point, config.rect_midpoint_size, fill,
							config.rect_midpoint_stroke,
							config.rect_midpoint_stroke_width)

	def draw_rect_point(self, point):
		fill = config.rect_point_fill
		self.draw_curve_point(point, config.rect_point_size, fill,
							config.rect_point_stroke,
							config.rect_point_stroke_width)

	def draw_ellipse_start_point(self, point):
		fill = config.ellipse_start_point_fill
		self.draw_curve_point(point, config.ellipse_start_point_size, fill,
							config.ellipse_start_point_stroke,
							config.ellipse_start_point_stroke_width)

	def draw_ellipse_end_point(self, point):
		fill = config.ellipse_end_point_fill
		self.draw_curve_point(point, config.ellipse_end_point_size, fill,
							config.ellipse_end_point_stroke,
							config.ellipse_end_point_stroke_width)

	def draw_polygon_point(self, point):
		fill = config.polygon_point_fill
		self.draw_curve_point(point, config.polygon_point_size, fill,
							config.polygon_point_stroke,
							config.polygon_point_stroke_width)

	def draw_text_point(self, point, selected=False):
		fill = config.text_point_fill
		if selected: fill = config.text_selected_point_fill
		self.draw_curve_point(point, config.text_point_size, fill,
							config.text_point_stroke,
							config.text_point_stroke_width)

	def reflect_snap(self):
		if self.canvas.show_snapping:
			snap = self.presenter.snap.active_snap
			if not snap[0] is None or not snap[1] is None:
				self.ctx.set_matrix(self.direct_matrix)
				self.ctx.set_antialias(cairo.ANTIALIAS_NONE)
				self.ctx.set_line_width(1.0)
				self.ctx.set_dash(config.snap_line_dash)
				self.ctx.set_source_rgba(*config.snap_line_color)
				if not snap[0] is None:
					x_win = self.canvas.point_doc_to_win([snap[0], 0])[0]
					self.ctx.move_to(x_win, 0)
					self.ctx.line_to(x_win, self.height)
					self.ctx.stroke()
				if not snap[1] is None:
					y_win = self.canvas.point_doc_to_win([0, snap[1]])[1]
					self.ctx.move_to(0, y_win)
					self.ctx.line_to(self.width, y_win)
					self.ctx.stroke()
				self.presenter.snap.active_snap = [None, None]

	def paint_guide_dragging(self, point=[], orient=uc2const.HORIZONTAL):
		self.start_soft_repaint()
		self.ctx.set_matrix(self.direct_matrix)
		self.ctx.set_antialias(cairo.ANTIALIAS_NONE)
		self.ctx.set_line_width(1.0)
		self.ctx.set_dash(config.guide_line_dash)
		self.ctx.set_source_rgba(*config.guide_line_dragging_color)
		if point:
			if orient == uc2const.HORIZONTAL:
				y_win = self.canvas.point_doc_to_win(point)[1]
				self.ctx.move_to(0, y_win)
				self.ctx.line_to(self.width, y_win)
				self.ctx.stroke()
			else:
				x_win = self.canvas.point_doc_to_win(point)[0]
				self.ctx.move_to(x_win, 0)
				self.ctx.line_to(x_win, self.height)
				self.ctx.stroke()
			self.reflect_snap()
		self.end_soft_repaint()

	def _draw_frame(self, path):
		self.start_soft_repaint()
		self.reflect_snap()
		self.ctx.set_matrix(self.direct_matrix)
		self.ctx.set_antialias(cairo.ANTIALIAS_NONE)
		self.ctx.set_line_width(1.0)
		self.ctx.set_dash([])
		self.ctx.set_source_rgb(*CAIRO_WHITE)
		self.ctx.new_path()
		self.ctx.append_path(path)
		self.ctx.stroke()
		self.ctx.set_dash(config.sel_frame_dash)
		self.ctx.set_source_rgb(*config.sel_frame_color)
		self.ctx.new_path()
		self.ctx.append_path(path)
		self.ctx.stroke()
		self.end_soft_repaint()

	def _paint_selection(self):
		selection = self.presenter.selection
		if selection.objs:
			selection.update_markers()
			zoom = self.canvas.zoom
			self.ctx.set_matrix(self.canvas.matrix)
			self.ctx.set_antialias(cairo.ANTIALIAS_NONE)

			#Frame
			if config.sel_frame_visible:
				x0, y0, x1, y1 = selection.frame
				self.ctx.set_line_width(1.0 / zoom)
				if config.sel_marker_frame_bgcolor:
					self.ctx.set_dash([])
					self.ctx.set_source_rgb(*config.sel_marker_frame_bgcolor)
					self.ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
					self.ctx.stroke()
				if config.sel_marker_frame_color:
					self.ctx.set_source_rgb(*config.sel_marker_frame_color)
					a, b = config.sel_marker_frame_dash
					self.ctx.set_dash([a / zoom, b / zoom])
					self.ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
					self.ctx.stroke()

			if config.sel_bbox_visible:
				x0, y0, x1, y1 = selection.bbox
				self.ctx.set_line_width(1.0 / zoom)
				if config.sel_bbox_bgcolor:
					self.ctx.set_dash([])
					self.ctx.set_source_rgb(*config.sel_bbox_bgcolor)
					self.ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
					self.ctx.stroke()
				if config.sel_bbox_color:
					self.ctx.set_source_rgb(*config.sel_bbox_color)
					a, b = config.sel_bbox_dash
					self.ctx.set_dash([a / zoom, b / zoom])
					self.ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
					self.ctx.stroke()

			#Selection markers
			markers = selection.markers
			size = config.sel_marker_size / zoom
			i = 0
			for marker in markers:
				if i == 9:
					cs = 3.0 / (2.0 * zoom)
					self.ctx.set_source_rgb(*config.sel_marker_fill)
					self.ctx.rectangle(marker[0], marker[1] + size / 2.0 - cs,
									size, 2.0 * cs)
					self.ctx.rectangle(marker[0] + size / 2.0 - cs, marker[1],
									2.0 * cs, size)
					self.ctx.fill()
					self.ctx.set_source_rgb(*config.sel_marker_stroke)
					self.ctx.move_to(marker[0] + size / 2.0, marker[1])
					self.ctx.line_to(marker[0] + size / 2.0, marker[1] + size)
					self.ctx.stroke()
					self.ctx.move_to(marker[0], marker[1] + size / 2.0)
					self.ctx.line_to(marker[0] + size, marker[1] + size / 2.0)
					self.ctx.stroke()
				elif i in [0, 1, 2, 3, 5, 6, 7, 8]:
					self.ctx.set_source_rgb(*config.sel_marker_fill)
					self.ctx.rectangle(marker[0], marker[1], size, size)
					self.ctx.fill_preserve()
					self.ctx.set_source_rgb(*config.sel_marker_stroke)
					self.ctx.set_line_width(1.0 / zoom)
					self.ctx.set_dash([])
					self.ctx.stroke()
				i += 1

			#Object markers
			objs = selection.objs
			self.ctx.set_source_rgb(*config.sel_object_marker_color)
			self.ctx.set_line_width(1.0 / zoom)
			self.ctx.set_dash([])
			offset = 2.0 / zoom
			for obj in objs:
				bbox = obj.cache_bbox
				self.ctx.rectangle(bbox[0] - offset, bbox[1] - offset,
								 2.0 * offset, 2.0 * offset)
				self.ctx.stroke()

	def	paint_selection(self):
		self.start_soft_repaint()
		self._paint_selection()
		self.end_soft_repaint()

	def stop_draw_frame(self, start, end):
		self.start_soft_repaint()
		self.end_soft_repaint()

	def show_move_frame(self):
		bbox = self.presenter.selection.bbox
		if bbox:
			path = libcairo.convert_bbox_to_cpath(bbox)
			libcairo.apply_trafo(path, self.canvas.trafo)
			self._draw_frame(path)

	def draw_move_frame(self, trafo):
		bbox = self.presenter.selection.bbox
		if bbox:
			path = libcairo.convert_bbox_to_cpath(bbox)
			libcairo.apply_trafo(path, trafo)
			libcairo.apply_trafo(path, self.canvas.trafo)
			self._draw_frame(path)

	def hide_move_frame(self):
		self.start_soft_repaint()
		self._paint_selection()
		self.end_soft_repaint()

	#------DRAWING MARKER RENDERING

	def draw_curve_point(self, point, size, fill, stroke, stroke_width):
		if len(point) == 2:
			cx, cy = point
		else:
			cx, cy = point[2]
		x = cx - int(size / 2.0)
		y = cy - int(size / 2.0)
		self.ctx.move_to(x, y)
		self.ctx.set_antialias(cairo.ANTIALIAS_NONE)
		self.ctx.set_dash([])
		self.ctx.set_source_rgb(*fill)
		self.ctx.rectangle(x, y, size, size)
		self.ctx.fill()
		self.ctx.set_line_width(stroke_width)
		self.ctx.set_source_rgb(*stroke)
		self.ctx.rectangle(x, y, size, size)
		self.ctx.stroke()
		self.ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)

	def paint_curve(self, paths, cursor=[], trace_path=[], cpoint=[]):
		self.start_soft_repaint()
		if paths:
			for path in paths:
				self.ctx.set_source_rgb(*config.curve_stroke_color)
				self.ctx.set_line_width(config.curve_stroke_width)
				self.ctx.move_to(*path[0])
				points = path[1]
				for point in points:
					if len(point) == 2:
						self.ctx.line_to(*point)
					else:
						x0, y0 = point[0]
						x1, y1 = point[1]
						x2, y2 = point[2]
						self.ctx.curve_to(x0, y0, x1, y1, x2, y2)
				if path[2]:
					self.ctx.close_path()
				self.ctx.stroke()

				self.draw_curve_point(path[0],
						config.curve_start_point_size,
						config.curve_start_point_fill,
						config.curve_start_point_stroke,
						config.curve_start_point_stroke_width)
				for point in points:
					self.draw_curve_point(point,
							config.curve_point_size,
							config.curve_point_fill,
							config.curve_point_stroke,
							config.curve_point_stroke_width)
				if points:
						self.draw_curve_point(points[-1],
								config.curve_last_point_size,
								config.curve_last_point_fill,
								config.curve_last_point_stroke,
								config.curve_last_point_stroke_width)
		if cursor:
			self.ctx.set_source_rgb(*config.curve_trace_color)
			self.ctx.set_line_width(config.curve_stroke_width)
			if trace_path:
				self.ctx.move_to(*trace_path[0])
				point = trace_path[1]
				x0, y0 = point[0]
				x1, y1 = point[1]
				x2, y2 = point[2]
				self.ctx.curve_to(x0, y0, x1, y1, x2, y2)
				self.ctx.stroke()
				if cpoint:
					self.ctx.set_source_rgb(*config.control_line_stroke_color)
					self.ctx.set_line_width(config.control_line_stroke_width)
					self.ctx.set_dash(config.control_line_stroke_dash)
					self.ctx.move_to(*trace_path[0])
					self.ctx.line_to(x0, y0)
					self.ctx.stroke()
					self.ctx.move_to(x2, y2)
					self.ctx.line_to(x1, y1)
					self.ctx.stroke()
					self.ctx.move_to(x2, y2)
					self.ctx.line_to(*cpoint)
					self.ctx.stroke()
					self.ctx.set_dash([])
					for point in [[x0, y0], [x1, y1], cpoint]:
						self.draw_curve_point(point,
								config.control_point_size,
								config.control_point_fill,
								config.control_point_stroke,
								config.control_point_stroke_width)
					self.draw_curve_point([x2, y2],
							config.curve_point_size,
							config.curve_point_fill,
							config.curve_point_stroke,
							config.curve_point_stroke_width)
			else:
				if paths[-1][1]:
					end_point = paths[-1][1][-1]
					if len(end_point) == 2:
						self.ctx.move_to(*end_point)
					else:
						self.ctx.move_to(*end_point[2])
				else:
					self.ctx.move_to(*paths[-1][0])
				self.ctx.line_to(*cursor)
				self.ctx.stroke()

		self.end_soft_repaint()

	def draw_text_frame(self, bbox, trafo):
		cpath = libcairo.convert_bbox_to_cpath(bbox)
		libcairo.apply_trafo(cpath, trafo)
		libcairo.apply_trafo(cpath, self.canvas.trafo)
		self._draw_frame(cpath)

	def draw_text_selection(self, bboxs, trafo):
		self.set_direct_matrix()
		self.ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)
		self.ctx.set_source_rgba(*config.text_selection_color)
		for item in bboxs:
			cpath = libcairo.convert_bbox_to_cpath(item)
			libcairo.apply_trafo(cpath, trafo)
			libcairo.apply_trafo(cpath, self.canvas.trafo)
			self.ctx.new_path()
			self.ctx.append_path(cpath)
			self.ctx.fill()

	def draw_text_cursor(self, start, end):
		self.set_direct_matrix()
		self.ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)
		if start[0] == end[0] or start[1] == end[1]:
			self.ctx.set_antialias(cairo.ANTIALIAS_NONE)
		self.ctx.set_dash([])
		self.ctx.set_source_rgb(*config.text_cursor_color)
		self.ctx.set_line_width(config.text_cursor_width)
		self.ctx.move_to(*start)
		self.ctx.line_to(*end)
		self.ctx.stroke()

	#------DIRECT DRAWING

	def cdc_paint_doc(self):
		dc = wx.ClientDC(self.canvas)
		dc.DrawBitmap(copy_surface_to_bitmap(self.surface), 0, 0, False)

	def cdc_paint_selection(self):
		dc = wx.ClientDC(self.canvas)
		dc.DrawBitmap(copy_surface_to_bitmap(self.temp_surface), 0, 0, False)

	def cdc_normalize_rect(self, start, end):
		x0, y0 = start
		x1, y1 = end
		x_min = min(x0, x1)
		x_max = max(x0, x1)
		y_min = min(y0, y1)
		y_max = max(y0, y1)
		w = x_max - x_min
		h = y_max - y_min
		return [x_min, y_min, w, h]

	def cdc_to_int(self, *args):
		ret = []
		for arg in args:ret.append(int(math.ceil(arg)))
		return ret

	def cdc_set_ctx(self, ctx, color=CAIRO_BLACK, dash=[]):
		ctx.set_antialias(cairo.ANTIALIAS_NONE)
		ctx.set_line_width(1.0)
		ctx.set_dash(dash)
		ctx.set_source_rgba(*color)

	def cdc_frame_to_bbox(self, frame):
		return frame[0] + frame[1]

	def cdc_bbox_to_frame(self, bbox):
		return [bbox[:2], bbox[2:]]

	def cdc_draw_vertical_line(self, x, color, dash, clear=False):
		if x is None:return
		x = self.cdc_to_int(x)[0]
		surface = cairo.ImageSurface(cairo.FORMAT_RGB24, 1, self.height)
		ctx = cairo.Context(surface)
		ctx.set_source_surface(self.temp_surface, -x + 1, 0)
		ctx.paint()
		if not clear:
			self.cdc_set_ctx(ctx, color, dash)
			ctx.move_to(1, 0)
			ctx.line_to(1, self.height)
			ctx.stroke()
		dc = wx.ClientDC(self.canvas)
		dc.DrawBitmap(copy_surface_to_bitmap(surface), x - 1, 0)

	def cdc_draw_horizontal_line(self, y, color, dash, clear=False):
		if y is None:return
		y = self.cdc_to_int(y)[0]
		surface = cairo.ImageSurface(cairo.FORMAT_RGB24, self.width, 1)
		ctx = cairo.Context(surface)
		ctx.set_source_surface(self.temp_surface, 0, -y + 1)
		ctx.paint()
		if not clear:
			self.cdc_set_ctx(ctx, color, dash)
			ctx.move_to(0, 1)
			ctx.line_to(self.width, 1)
			ctx.stroke()
		dc = wx.ClientDC(self.canvas)
		dc.DrawBitmap(copy_surface_to_bitmap(surface), 0, y - 1)

	def cdc_draw_snap_line(self, pos, vertical=True, clear=False):
		color = config.snap_line_color
		dash = config.snap_line_dash
		if vertical: self.cdc_draw_vertical_line(pos, color, dash, clear)
		else: self.cdc_draw_horizontal_line(pos, color, dash, clear)

	def cdc_reflect_snapping(self):
		if self.canvas.show_snapping:
			snap = self.presenter.snap.active_snap
			if self.snap:
				self.cdc_draw_snap_line(self.snap[0], True, True)
				self.cdc_draw_snap_line(self.snap[1], False, True)
				self.snap = []
			if not snap[0] is None or not snap[1] is None:
				self.snap = [None, None]
				if not snap[0] is None:
					x_win = self.canvas.point_doc_to_win([snap[0], 0])[0]
					self.cdc_draw_snap_line(x_win)
					self.snap[0] = x_win
				if not snap[1] is None:
					y_win = self.canvas.point_doc_to_win([0, snap[1]])[1]
					self.cdc_draw_snap_line(y_win, False)
					self.snap[1] = y_win
				self.presenter.snap.active_snap = [None, None]

	def cdc_draw_guide(self, pos, orient=uc2const.VERTICAL, clear=False):
		color = config.guide_line_dragging_color
		dash = config.guide_line_dash
		if orient == uc2const.VERTICAL:
			self.cdc_draw_vertical_line(pos, color, dash, clear)
		else:
			self.cdc_draw_horizontal_line(pos, color, dash, clear)

	def cdc_drag_guide(self, guide=[]):
		point = orient = 0
		if guide:
			point, orient = guide
			if not point:return
			if orient == uc2const.VERTICAL:
				pos = self.canvas.point_doc_to_win(point)[0]
			else:
				pos = self.canvas.point_doc_to_win(point)[1]
		if self.guide:
			pos_old, orient_old = self.guide
			if guide:
				if pos_old == pos and orient == orient_old: return
			self.cdc_draw_guide(pos_old, orient_old, True)
			self.guide = []
		if guide:
			self.guide = [pos, orient]
			self.cdc_draw_guide(pos, orient)

	def cdc_clear_rect(self, start, end):
		if start and end:
			x, y, w, h = self.cdc_to_int(*self.cdc_normalize_rect(start, end))
			dc = wx.ClientDC(self.canvas)
			x -= 2;y -= 2
			w += 4;h += 4
			if not w: w = 1
			if not h: h = 1
			surface = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
			ctx = cairo.Context(surface)
			ctx.set_source_surface(self.surface, -x, -y)
			ctx.paint()
			dc.DrawBitmap(copy_surface_to_bitmap(surface), x, y)

	def _cdc_draw_cpath(self, ctx, cpath):
		self.cdc_set_ctx(ctx, CAIRO_WHITE)
		ctx.new_path()
		ctx.append_path(cpath)
		ctx.stroke()
		self.cdc_set_ctx(ctx, config.sel_frame_color, config.sel_frame_dash)
		ctx.new_path()
		ctx.append_path(cpath)
		ctx.stroke()

	def cdc_draw_move_frame(self, trafo):
		bbox = self.presenter.selection.bbox
		if bbox:
			cpath = libcairo.convert_bbox_to_cpath(bbox)
			libcairo.apply_trafo(cpath, trafo)
			libcairo.apply_trafo(cpath, self.canvas.trafo)
			bbox = self.cdc_to_int(*libcairo.get_cpath_bbox(cpath))
			frame = self.cdc_bbox_to_frame(bbox)
			if self.frame and frame == self.frame:return
			if not self.frame:self.frame = frame
			bbox2 = self.cdc_frame_to_bbox(self.frame)
			frame_sum = self.cdc_bbox_to_frame(libgeom.sum_bbox(bbox, bbox2))
			x, y, w, h = self.cdc_normalize_rect(*frame_sum)
			self.frame = frame
			surface = cairo.ImageSurface(cairo.FORMAT_RGB24, w + 2, h + 2)
			ctx = cairo.Context(surface)
			ctx.set_source_surface(self.surface, -x + 1, -y + 1)
			ctx.paint()
			ctx.set_matrix(cairo.Matrix(1.0, 0.0, 0.0, 1.0, -x + 1, -y + 1))
			self._cdc_draw_cpath(ctx, cpath)
			dc = wx.ClientDC(self.canvas)
			dc.DrawBitmap(copy_surface_to_bitmap(surface), x - 1, y - 1)
			self.cdc_reflect_snapping()

	def cdc_draw_frame(self, start, end, temp_surfase=False):
		if start and end:
			if self.frame:
				if start == self.frame[0] and end == self.frame[1]:return
			cpath = libcairo.convert_bbox_to_cpath(start + end)
			bbox = self.cdc_to_int(*libcairo.get_cpath_bbox(cpath))
			frame = self.cdc_bbox_to_frame(bbox)
			if not self.frame:self.frame = frame
			bbox2 = self.cdc_frame_to_bbox(self.frame)
			frame_sum = self.cdc_bbox_to_frame(libgeom.sum_bbox(bbox, bbox2))
			x, y, w, h = self.cdc_normalize_rect(*frame_sum)
			self.frame = frame
			surface = cairo.ImageSurface(cairo.FORMAT_RGB24, w + 2, h + 2)
			ctx = cairo.Context(surface)
			if temp_surfase:
				ctx.set_source_surface(self.temp_surface, -x + 1, -y + 1)
			else:
				ctx.set_source_surface(self.surface, -x + 1, -y + 1)
			ctx.paint()
			ctx.set_matrix(cairo.Matrix(1.0, 0.0, 0.0, 1.0, -x + 1, -y + 1))
			self._cdc_draw_cpath(ctx, cpath)
			dc = wx.ClientDC(self.canvas)
			dc.DrawBitmap(copy_surface_to_bitmap(surface), x - 1, y - 1)
			self.cdc_reflect_snapping()

	def cdc_hide_move_frame(self):
		if self.frame:
			self.cdc_clear_rect(*self.frame)
			self.frame = []
