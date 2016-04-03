# -*- coding: utf-8 -*-
#
#	Copyright (C) 2016 by Igor E. Novikov
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


from reportlab.pdfgen.canvas import Canvas, FILL_EVEN_ODD, FILL_NON_ZERO
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import CMYKColorSep, Color, CMYKColor

from uc2 import libgeom
from uc2.formats.generic_filters import AbstractSaver
from uc2 import uc2const, cms
from pdfconst import PDF_VERSION_DEFAULT
from uc2.formats.sk2 import sk2_const

class PDF_Saver(AbstractSaver):

	name = 'PDF_Saver'
	canvas = None
	methods = None
	desktop_layers = None
	master_layers = None
	page_trafo = None


	def do_save(self):
		self.canvas = Canvas(self.fileptr, pdfVersion=PDF_VERSION_DEFAULT)
		self.presenter.update()
		self.cms = self.presenter.cms
		self.methods = self.presenter.methods
		self.desktop_layers = self.methods.get_desktop_layers()
		self.master_layers = self.methods.get_master_layers()
		pages = self.methods.get_pages()
		for page in pages:
			w, h = self.methods.get_page_size(page)
			self.canvas.translate(w / 2.0, h / 2.0)
			self.canvas.setPageSize((w, h))
			layers = self.desktop_layers + self.methods.get_layers(page)
			layers += self.master_layers
			for layer in layers:
				if self.methods.is_layer_visible(layer):
					self.process_childs(layer.childs)
			self.canvas.showPage()
		self.canvas.save()

	def process_childs(self, childs):
		for obj in childs:
			if obj.is_pixmap():
				pass
			elif obj.is_primitive():
				curve_obj = obj.to_curve()
				if curve_obj.is_primitive():
					self.draw_curve(curve_obj)
				else:
					self.process_childs(curve_obj.childs)
			elif obj.is_container():
				self.draw_container(obj)
			else:
				self.process_childs(obj.childs)

	def draw_curve(self, curve_obj):
		paths = libgeom.apply_trafo_to_paths(curve_obj.paths, curve_obj.trafo)
		pdfpath, closed = self.make_pdfpath(paths)
		fill_style = curve_obj.style[0]
		stroke_style = curve_obj.style[1]
		if stroke_style and stroke_style[7]:
			self.stroke_pdfpath(pdfpath, stroke_style)
		if fill_style and fill_style[0] & sk2_const.FILL_CLOSED_ONLY and closed:
			self.fill_pdfpath(pdfpath, fill_style, curve_obj.fill_trafo)
		elif fill_style and not fill_style[0] & sk2_const.FILL_CLOSED_ONLY:
			self.fill_pdfpath(pdfpath, fill_style, curve_obj.fill_trafo)
		if stroke_style and not stroke_style[7]:
			self.stroke_pdfpath(pdfpath, stroke_style)

	def draw_container(self, obj):
		container = obj.childs[0].to_curve()
		paths = libgeom.apply_trafo_to_paths(container.paths, container.trafo)
		pdfpath, closed = self.make_pdfpath(paths)
		fill_style = container.style[0]
		stroke_style = container.style[1]
		if stroke_style and stroke_style[7]:
			self.stroke_pdfpath(pdfpath, stroke_style)

		self.canvas.saveState()
		self.canvas.clipPath(pdfpath, 0, 0)

		if fill_style and fill_style[0] & sk2_const.FILL_CLOSED_ONLY and closed:
			self.fill_pdfpath(pdfpath, fill_style, container.fill_trafo)
		elif fill_style and not fill_style[0] & sk2_const.FILL_CLOSED_ONLY:
			self.fill_pdfpath(pdfpath, fill_style, container.fill_trafo)

		self.process_childs(obj.childs[1:])

		self.canvas.restoreState()

		if stroke_style and not stroke_style[7]:
			self.stroke_pdfpath(pdfpath, stroke_style)

	def make_pdfpath(self, paths):
		closed = False
		pdfpath = self.canvas.beginPath()
		for path in paths:
			pdfpath.moveTo(*path[0])
			for point in path[1]:
				if len(point) > 2:
					pdfpath.curveTo(point[0][0], point[0][1],
								point[1][0], point[1][1],
								point[2][0], point[2][1])
				else:
					pdfpath.lineTo(*point)
			if path[2]:
				pdfpath.close()
				closed = True
		return pdfpath, closed

	def set_rgb_values(self, color, pdfcolor):
		r, g, b = self.cms.get_rgb_color(color)[1]
		density = pdfcolor.density
		if density < 1:
			r = density * (r - 1) + 1
			g = density * (g - 1) + 1
			b = density * (b - 1) + 1
		pdfcolor.red, pdfcolor.green, pdfcolor.blue = (r, g, b)

	def get_pdfcolor(self, color):
		pdfcolor = None
		alpha = color[2]
		if color[0] == uc2const.COLOR_RGB:
			r, g, b = color[1]
			pdfcolor = Color(r, g, b, alpha)
		elif color[0] == uc2const.COLOR_GRAY:
			k = 1.0 - color[1][0]
			c = m = y = 0.0
			pdfcolor = CMYKColor(c, m, y, k, alpha=alpha)
		elif color[0] == uc2const.COLOR_SPOT:
			c, m, y, k = self.cms.get_cmyk_color(color)[1]
			spotname = color[3]
			if spotname == uc2const.COLOR_REG: spotname = 'All'
			pdfcolor = CMYKColorSep(c, m, y, k, spotName=spotname, alpha=alpha)
		else:
			c, m, y, k = self.cms.get_cmyk_color(color)[1]
			pdfcolor = CMYKColor(c, m, y, k, alpha=alpha)
		if not color[0] == uc2const.COLOR_RGB:
			self.set_rgb_values(color, pdfcolor)
		return pdfcolor

	def stroke_pdfpath(self, pdfpath, stroke_style):
		width = stroke_style[1]
		self.canvas.setStrokeColor(self.get_pdfcolor(stroke_style[2]))
		dash = stroke_style[3]
		caps = stroke_style[4]
		joint = stroke_style[5]
		miter = stroke_style[6]
		self.canvas.setLineWidth(width)
		self.canvas.setLineCap(caps - 1)
		self.canvas.setLineJoin(joint)
		dashes = []
		if dash:
			dashes = list(dash)
			w = width
			if w < 1.0: w = 1.0
			for i in range(len(dashes)):
				dashes[i] = w * dashes[i]
		self.canvas.setDash(dashes)
		self.canvas.setMiterLimit(miter)
		self.canvas.drawPath(pdfpath, 1, 0)
		self.canvas.setStrokeAlpha(1.0)
		#TODO:process scalable flag

	def fill_pdfpath(self, pdfpath, fill_style, fill_trafo=None):
		fillrule = fill_style[0]
		if fillrule in (sk2_const.FILL_EVENODD,
					sk2_const.FILL_EVENODD_CLOSED_ONLY):
			fillrule = FILL_EVEN_ODD
		else:fillrule = FILL_NON_ZERO
		self.canvas._fillMode = fillrule

		if fill_style[1] == sk2_const.FILL_SOLID:
			self.canvas.setFillColor(self.get_pdfcolor(fill_style[2]))
			self.canvas.drawPath(pdfpath, 0, 1)
			self.canvas.setFillAlpha(1.0)
		elif fill_style[1] == sk2_const.FILL_GRADIENT:
			#TODO: transparency in gradient colors
			self.canvas.saveState()
			self.canvas.clipPath(pdfpath, 0, 0)
			if fill_trafo:
				self.canvas.transform(*fill_trafo)
			gradient = fill_style[2]
			grad_type = gradient[0]
			sp, ep = gradient[1]
			stops = gradient[2]
			colors = []
			positions = []
			for offset, color in stops:
				positions.append(offset)
				colors.append(self.get_pdfcolor(color))
			if grad_type == sk2_const.GRADIENT_RADIAL:
				radius = libgeom.distance(sp, ep)
				self.canvas.radialGradient(sp[0], sp[1], radius, colors,
										positions, True)
			else:
				x0, y0 = sp
				x1, y1 = ep
				self.canvas.linearGradient(x0, y0, x1, y1, colors,
										positions, True)
			self.canvas.restoreState()

		elif fill_style[1] == sk2_const.FILL_PATTERN:
			pass
			#TODO: implement FILL_PATTERN support


