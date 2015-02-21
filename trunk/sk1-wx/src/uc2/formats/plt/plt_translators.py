# -*- coding: utf-8 -*-
#
#	Copyright (C) 2012 by Igor E. Novikov
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

from uc2 import _, events
from uc2.formats import pdxf
from uc2.formats.plt import model
from uc2.formats.plt.pltconst import PDXF_to_PLT_TRAFO, PLT_to_PDXF_TRAFO
from uc2 import libgeom




class PLT_to_PDXF_Translator:

	def translate(self, plt_doc, pdxf_doc):
		jobs = plt_doc.get_jobs()
		page = pdxf_doc.methods.get_page()
		layer = pdxf_doc.methods.get_layer(page)

		style = [deepcopy(pdxf_doc.config.default_fill),
				deepcopy(pdxf_doc.config.default_stroke),
				deepcopy(pdxf_doc.config.default_text_style),
				deepcopy(pdxf_doc.config.default_structural_style)]

		for job in jobs:
			if job.cid == model.JOB:
				curve = pdxf.model.Curve(pdxf_doc.config)
				curve.paths = [deepcopy(job.cache_path), ]
				curve.trafo = [] + PLT_to_PDXF_TRAFO
				curve.style = deepcopy(style)
				pdxf_doc.methods.append_object(curve, layer)

		pdxf_doc.model.do_update()


class PDXF_to_PLT_Translator:

	jobs = []
	plt_doc = None
	obj_stack = []
	counter = 0
	position = 0

	def translate(self, objs, plt_doc):
		self.plt_doc = plt_doc
		self.jobs = plt_doc.get_jobs()
		self.obj_stack = []
		self.recursive_processing(objs)
		self.create_jobs()
		self.plt_doc.model.do_update()

	def recursive_processing(self, objs):
		for obj in objs:
			if obj.cid > pdxf.model.PRIMITIVE_CLASS:
				self.obj_stack.append(obj)
			self.recursive_processing(obj.childs)

	def create_jobs(self):
		if self.obj_stack:
			m11, m21, m12, m22, dx, dy = PDXF_to_PLT_TRAFO

			if self.plt_doc.config.force_zero:
				bbox = []
				bbox += self.obj_stack[0].cache_bbox
				for obj in self.obj_stack:
					bbox = libgeom.sum_bbox(bbox, obj.cache_bbox)

				dx = -bbox[0] * m11
				dy = -bbox[1] * m22

			trafo = [m11, m21, m12, m22, dx, dy]

			obj_num = len(self.obj_stack)
			for obj in self.obj_stack:

				self.counter += 1
				position = float(self.counter) / obj_num
				if position - self.position > 0.05:
					msg = _('Saving in process...')
					events.emit(events.FILTER_INFO, msg, position)
					self.position = position

				paths = libgeom.get_flattened_path(obj, trafo,
									self.plt_doc.config.tolerance)
				if paths is None: continue

				for path in paths:
					if path and path[1]:
						self.jobs.append(model.PltJob('', path))






