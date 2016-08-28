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

import math
from copy import deepcopy
from base64 import b64decode
from cStringIO import StringIO
from PIL import Image

from reportlab.pdfgen.canvas import Canvas, FILL_EVEN_ODD, FILL_NON_ZERO
from reportlab.pdfbase.pdfdoc import PDFInfo, PDFString, PDFDate, PDFDictionary
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import CMYKColorSep, Color, CMYKColor

from uc2 import uc2const
from uc2 import libgeom, libimg
from uc2.formats.sk2 import sk2_const, sk2_model

from pdfconst import PDF_VERSION_DEFAULT

class UC_PDFInfo(PDFInfo):

	pdfxversion = 'PDF/X-4'

	def __init__(self, pdfdoc):
		PDFInfo.__init__(self)
		pdfdoc.info = self
		self.invariant = pdfdoc.invariant

	def format(self, document):
		D = {}
		D["Title"] = PDFString(self.title)
		D["Author"] = PDFString(self.author)
		D["CreationDate"] = PDFDate(invariant=self.invariant,
								dateFormatter=self._dateFormatter)
		D["Producer"] = PDFString(self.producer)
		if self.pdfxversion:
			D["GTS_PDFXVersion"] = PDFString(self.pdfxversion)
		D["Creator"] = PDFString(self.creator)
		D["Subject"] = PDFString(self.subject)
		D["Keywords"] = PDFString(self.keywords)

		PD = PDFDictionary(D)
		return PD.format(document)


class PDFGenerator(object):

	canvas = None


	def __init__(self, fileptr, cms, version=PDF_VERSION_DEFAULT):
		self.cms = cms
		self.canvas = Canvas(fileptr, pdfVersion=version[0])
		self.info = UC_PDFInfo(self.canvas._doc)
		self.info.pdfxversion = version[1]
		self.info.subject = '---'

	#---PDF doc data
	def set_creator(self, name): self.info.creator = name
	def set_producer(self, name): self.info.producer = name
	def set_title(self, title): self.info.title = title
	def set_author(self, author): self.info.author = author
	def set_subject(self, subj): self.info.subject = subj
	def set_keywords(self, keywords): self.info.keywords = keywords
	#---PDF doc data end

	def start_page(self, w, h):
		self.canvas.translate(w / 2.0, h / 2.0)
		self.canvas.setPageSize((w, h))

	def end_page(self):
		self.canvas.showPage()

	def save(self):
		self.canvas.save()

	#--- Rendering
	def render(self, objs):
		for obj in objs:
			if obj.is_pixmap():
				self.draw_pixmap(obj)
			elif obj.is_primitive():
				curve_obj = obj.to_curve()
				if curve_obj.is_primitive():
					self.draw_curve(curve_obj)
				else:
					self.render(curve_obj.childs)
			elif obj.is_container():
				self.draw_container(obj)
			else:
				self.render(obj.childs)

	def draw_curve(self, curve_obj):
		paths = libgeom.apply_trafo_to_paths(curve_obj.paths, curve_obj.trafo)
		pdfpath, closed = self.make_pdfpath(paths)
		fill_style = curve_obj.style[0]
		stroke_style = curve_obj.style[1]
		if stroke_style and stroke_style[7]:
			self.stroke_pdfpath(pdfpath, stroke_style, curve_obj.stroke_trafo)
		if fill_style and fill_style[0] & sk2_const.FILL_CLOSED_ONLY and closed:
			self.fill_pdfpath(curve_obj, pdfpath, fill_style, curve_obj.fill_trafo)
		elif fill_style and not fill_style[0] & sk2_const.FILL_CLOSED_ONLY:
			self.fill_pdfpath(curve_obj, pdfpath, fill_style, curve_obj.fill_trafo)
		if stroke_style and not stroke_style[7]:
			self.stroke_pdfpath(pdfpath, stroke_style, curve_obj.stroke_trafo)

	def draw_container(self, obj):
		container = obj.childs[0].to_curve()
		paths = libgeom.apply_trafo_to_paths(container.paths, container.trafo)
		pdfpath, closed = self.make_pdfpath(paths)
		fill_style = container.style[0]
		stroke_style = container.style[1]
		if stroke_style and stroke_style[7]:
			self.stroke_pdfpath(pdfpath, stroke_style, container.stroke_trafo)

		self.canvas.saveState()
		self.canvas.clipPath(pdfpath, 0, 0)

		if fill_style and fill_style[0] & sk2_const.FILL_CLOSED_ONLY and closed:
			self.fill_pdfpath(container, pdfpath, fill_style, container.fill_trafo)
		elif fill_style and not fill_style[0] & sk2_const.FILL_CLOSED_ONLY:
			self.fill_pdfpath(container, pdfpath, fill_style, container.fill_trafo)

		self.process_childs(obj.childs[1:])

		self.canvas.restoreState()

		if stroke_style and not stroke_style[7]:
			self.stroke_pdfpath(pdfpath, stroke_style, container.stroke_trafo)

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

	def set_fill_rule(self, fillrule):
		if fillrule in (sk2_const.FILL_EVENODD,
					sk2_const.FILL_EVENODD_CLOSED_ONLY):
			fillrule = FILL_EVEN_ODD
		else:fillrule = FILL_NON_ZERO
		self.canvas._fillMode = fillrule

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

	def stroke_pdfpath(self, pdfpath, stroke_style, stroke_trafo=[]):
		width = stroke_style[1]

		if not stroke_style[8]:
			width = stroke_style[1]
		else:
			if not stroke_trafo:
				stroke_trafo = [] + sk2_const.NORMAL_TRAFO
			points = [[0.0, 0.0], [1.0, 0.0]]
			points = libgeom.apply_trafo_to_points(points, stroke_trafo)
			coef = libgeom.distance(*points)
			width = stroke_style[1] * coef

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

	def fill_pdfpath(self, obj, pdfpath, fill_style, fill_trafo=None):
		self.set_fill_rule(fill_style[0])

		if fill_style[1] == sk2_const.FILL_SOLID:
			self.canvas.setFillColor(self.get_pdfcolor(fill_style[2]))
			self.canvas.drawPath(pdfpath, 0, 1)
		elif fill_style[1] == sk2_const.FILL_GRADIENT:
			gradient = fill_style[2]
			stops = gradient[2]
			transparency = False
			for stop in stops:
				if stop[1][2] < 1.0:
					transparency = True
					break
			if transparency:
				self.fill_tr_gradient(obj, pdfpath, fill_trafo, gradient)
			else:
				self.fill_gradient(pdfpath, fill_trafo, gradient)

		elif fill_style[1] == sk2_const.FILL_PATTERN:
			pattern = fill_style[2]
			self.fill_pattern(obj, pdfpath, fill_trafo, pattern)

	def fill_gradient(self, pdfpath, fill_trafo, gradient):
		self.canvas.saveState()
		self.canvas.clipPath(pdfpath, 0, 0)
		if fill_trafo:
			self.canvas.transform(*fill_trafo)
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

	def fill_tr_gradient(self, obj, pdfpath, fill_trafo, gradient):
		grad_type = gradient[0]
		if grad_type == sk2_const.GRADIENT_RADIAL:
			self.fill_radial_tr_gradient(obj, pdfpath, fill_trafo, gradient)
		else:
			self.fill_linear_tr_gradient(obj, pdfpath, fill_trafo, gradient)

	def get_grcolor_at_point(self, stops, point=0.0):
		if not point:return self.get_pdfcolor(stops[0][1])
		if point == 1.0:return self.get_pdfcolor(stops[-1][1])
		stop0 = stops[0]
		stop1 = None
		for item in stops:
			if item[0] < point:stop0 = item
			if item[0] >= point:
				stop1 = item
				break
		size = stop1[0] - stop0[0]
		if not size:
			color = stop1[1]
		else:
			coef = (point - stop0[0]) / size
			color = self.cms.mix_colors(stop0[1], stop1[1], coef)
		return self.get_pdfcolor(color)

	def fill_linear_tr_gradient(self, obj, pdfpath, fill_trafo, gradient):
		if not fill_trafo:
			fill_trafo = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
		stops = gradient[2]
		sp, ep = gradient[1]
		dx, dy = sp
		l = libgeom.distance(sp, ep)
		angle = libgeom.get_point_angle(ep, sp)
		m21 = math.sin(angle)
		m11 = m22 = math.cos(angle)
		m12 = -m21
		trafo = [m11, m21, m12, m22, dx, dy]
		inv_trafo = libgeom.multiply_trafo(libgeom.invert_trafo(fill_trafo),
										libgeom.invert_trafo(trafo))
		cv_trafo = libgeom.multiply_trafo(trafo, fill_trafo)
		paths = libgeom.apply_trafo_to_paths(obj.paths, obj.trafo)
		paths = libgeom.apply_trafo_to_paths(paths, inv_trafo)
		bbox = libgeom.sum_bbox(libgeom.get_paths_bbox(paths),
							[0.0, 0.0, l, 0.0])
		bbox = libgeom.normalize_bbox(bbox)

		y = bbox[1]
		d = libgeom.distance(*libgeom.apply_trafo_to_points([[0.0, 0.0],
													[0.0, 1.0]], inv_trafo))
		height = bbox[3] - bbox[1]

		self.canvas.saveState()
		self.canvas.clipPath(pdfpath, 0, 0)
		self.canvas.transform(*cv_trafo)

		self.canvas.setFillColor(self.get_grcolor_at_point(stops, 0.0))
		self.canvas.rect(bbox[0], y, 0.0 - bbox[0], height, stroke=0, fill=1)

		x = 0.0
		while x < l:
			point = x / l
			self.canvas.setFillColor(self.get_grcolor_at_point(stops, point))
			if x + d < l: width = d
			else: width = l - x
			self.canvas.rect(x, y, width, height, stroke=0, fill=1)
			x += d

		self.canvas.setFillColor(self.get_grcolor_at_point(stops, 1.0))
		self.canvas.rect(l, y, bbox[2] - l, height, stroke=0, fill=1)

		self.canvas.restoreState()


	def fill_radial_tr_gradient(self, obj, pdfpath, fill_trafo, gradient):
		if not fill_trafo:
			fill_trafo = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
		stops = gradient[2]
		sp, ep = gradient[1]
		dx, dy = sp
		l = libgeom.distance(sp, ep)
		trafo = [1.0, 0.0, 0.0, 1.0, dx, dy]
		inv_trafo = libgeom.multiply_trafo(libgeom.invert_trafo(fill_trafo),
										libgeom.invert_trafo(trafo))
		cv_trafo = libgeom.multiply_trafo(trafo, fill_trafo)
		paths = libgeom.apply_trafo_to_paths(obj.paths, obj.trafo)
		paths = libgeom.apply_trafo_to_paths(paths, inv_trafo)
		bbox = libgeom.sum_bbox(libgeom.get_paths_bbox(paths),
							[0.0, 0.0, l, 0.0])
		bbox = libgeom.normalize_bbox(bbox)
		d = libgeom.distance(*libgeom.apply_trafo_to_points([[0.0, 0.0],
													[0.0, 1.0]], inv_trafo))

		circle_paths = libgeom.get_circle_paths(0.0, 0.0, sk2_const.ARC_CHORD)
		trafo = [2.0, 0.0, 0.0, 2.0, -1.0, -1.0]
		circle_paths = libgeom.apply_trafo_to_paths(circle_paths, trafo)

		inner_paths = []
		r = 0.0
		self.canvas.saveState()
		self.canvas.clipPath(pdfpath, 0, 0)
		self.canvas.transform(*cv_trafo)
		while r < l:
			point = r / l
			self.canvas.setFillColor(self.get_grcolor_at_point(stops, point))
			if r + d < l: coef = (r + d)
			else: coef = l
			trafo = [coef, 0.0, 0.0, coef, 0.0, 0.0]
			paths = libgeom.apply_trafo_to_paths(circle_paths, trafo)
			ring = self.make_pdfpath(inner_paths + paths)[0]
			inner_paths = paths
			self.canvas.drawPath(ring, stroke=0, fill=1)
			r += d

		self.canvas.setFillColor(self.get_grcolor_at_point(stops, 1.0))
		r = max(bbox[2] - bbox[0], bbox[3] - bbox[1])
		trafo = [2.0 * r, 0.0, 0.0, 2.0 * r, 0.0, 0.0]
		paths = libgeom.apply_trafo_to_paths(circle_paths, trafo)
		ring = self.make_pdfpath(inner_paths + paths)[0]
		self.canvas.drawPath(ring, stroke=0, fill=1)

		self.canvas.restoreState()

	def draw_pixmap(self, obj):
		self.canvas.saveState()
		self.canvas.transform(*obj.trafo)
		self.draw_pixmap_obj(obj)
		self.canvas.restoreState()

	def draw_pixmap_obj(self, obj):
		if obj.colorspace in uc2const.DUOTONES:
			fg, bg = libimg.convert_duotone_to_image(self.cms, obj)
			self.draw_image(*bg)
			self.draw_image(*fg)
		else:
			raw_image = Image.open(StringIO(b64decode(obj.bitmap)))
			raw_image.load()
			alpha_chnl = None
			if obj.alpha_channel:
				alpha_chnl = Image.open(StringIO(b64decode(obj.alpha_channel)))
				alpha_chnl.load()
			self.draw_image(raw_image, alpha_chnl)

	def draw_image(self, image, alpha_channel=None):
		if not image: return
		img = ImageReader(image)
		img.getRGBData()
		if alpha_channel: img._dataA = ImageReader(alpha_channel)
		self.canvas.drawImage(img, 0, 0, mask='auto')

	def fill_pattern(self, obj, pdfpath, fill_trafo, pattern):
		if not fill_trafo:
			fill_trafo = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
		inv_ptrn_trafo = libgeom.invert_trafo(pattern[3])
		inv_trafo = libgeom.multiply_trafo(libgeom.invert_trafo(fill_trafo),
										libgeom.invert_trafo(inv_ptrn_trafo))
		paths = libgeom.apply_trafo_to_paths(obj.paths, obj.trafo)
		paths = libgeom.apply_trafo_to_paths(paths, inv_trafo)
		bbox = libgeom.get_paths_bbox(paths)
		cv_trafo = libgeom.multiply_trafo(pattern[3], fill_trafo)

		bmpstr = b64decode(pattern[1])
		image_obj = sk2_model.Pixmap(obj.config)
		libimg.set_image_data(self.cms, image_obj, bmpstr)
		if pattern[0] == sk2_const.PATTERN_IMG and \
		 len(pattern) > 2:
			image_obj.style[3] = deepcopy(pattern[2])
		libimg.update_image(self.cms, image_obj)

		self.canvas.saveState()
		self.canvas.clipPath(pdfpath, 0, 0)
		self.canvas.transform(*cv_trafo)

		w, h = image_obj.get_size()
		x = bbox[0]
		y = bbox[3]
		while y > bbox[1] - h:
			while x < bbox[2]:
				self.canvas.saveState()
				self.canvas.transform(1.0, 0.0, 0.0, 1.0, x, y)
				self.draw_pixmap_obj(image_obj)
				self.canvas.restoreState()
				x += w
			y -= h
			x = bbox[0]
		self.canvas.restoreState()







