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

from uc2.libgeom import sum_bbox, is_bbox_in_rect
from uc2 import libcairo, uc2const
from uc2.formats.sk2 import sk2_model

from sk1 import _, config
from sk1 import events


class Selection:

	objs = []
	bbox = []
	frame = []
	markers = []
	center_offset = []

	def __init__(self, presenter):
		self.presenter = presenter
		self.app = presenter.app
		self.objs = []
		self.bbox = []
		self.frame = []
		self.markers = []
		self.center_offset = [0.0, 0.0]

	def destroy(self):
		items = self.__dict__.keys()
		for item in items:
			self.__dict__[item] = None

	def update(self):
		if not self.objs:
			self.center_offset = [0.0, 0.0]
		self.update_bbox()
		eventloop = self.presenter.eventloop
		eventloop.emit(eventloop.SELECTION_CHANGED)
		if len(self.objs) == 1:
			cid = self.objs[0].cid
			msg = sk2_model.CID_TO_NAME[cid] + _(' object in selection')
			if cid == sk2_model.PIXMAP:
				h_dpi, v_dpi = self.objs[0].get_resolution()
				msg += ', %ix%i dpi' % (h_dpi, v_dpi)
		elif not len(self.objs):
			msg = _('No selection')
		else:
			msg = _('objects in selection')
			msg = '%i %s' % (len(self.objs), msg)
		events.emit(events.APP_STATUS, msg)
		events.emit(events.SELECTION_CHANGED, self.presenter)

	def update_bbox(self):
		self.bbox = []
		if self.objs:
			self.bbox += self.objs[0].cache_bbox
			for obj in self.objs:
				self.bbox = sum_bbox(self.bbox, obj.cache_bbox)
		self.update_markers()

	def update_markers(self):
		self.frame = []
		if self.bbox:
			x0, y0, x1, y1 = self.bbox
			frame_offset = config.sel_frame_offset
			size = frame_offset / self.presenter.canvas.zoom
			self.frame = [x0 - size, y0 - size, x1 + size, y1 + size]

		self.markers = []
		if self.bbox:
			marker_size = config.sel_marker_size
			offset = marker_size / (2.0 * self.presenter.canvas.zoom)
			x0, y0, x1, y1 = self.frame
			w = (x1 - x0) / 2.0
			h = (y1 - y0) / 2.0
			dcx, dcy = self.center_offset
			markers = [
						[x0, y1], [x0 + w, y1], [x1, y1],
						[x0, y0 + h], [x0 + w, y0 + h], [x1, y0 + h],
						[x0, y0], [x0 + w, y0], [x1, y0],
						[x0 + w + dcx, y0 + h + dcy],
						]
			for marker in markers:
				x, y = marker
				self.markers.append([x - offset, y - offset,
									x + offset, y + offset])

			sec_markers = markers[0:4] + markers[5:9]
			for marker in sec_markers:
				x, y = marker
				self.markers.append([x - 2 * offset, y - 2 * offset,
									x + 2 * offset, y + 2 * offset])

	def select_by_rect(self, rect, flag=False):
		result = []
		layers = self.presenter.get_editable_layers()
		for layer in layers:
			for obj in layer.childs:
				if is_bbox_in_rect(rect, obj.cache_bbox):
					result.append(obj)
		if flag:
			self.add(result)
		else:
			self.set(result)

	def _select_at_point(self, point):
		result = []
		layers = self.presenter.get_editable_layers()
		layers.reverse()
		rect = point + point
		win_point = self.presenter.canvas.doc_to_win(point)
		trafo = self.presenter.canvas.trafo
		for layer in layers:
			if result: break
			objs = [] + layer.childs
			objs.reverse()
			for obj in objs:
				if is_bbox_in_rect(obj.cache_bbox, rect):
					ret = libcairo.is_point_in_path(win_point, trafo, obj,
												 config.stroke_sensitive_size)
					if ret:
						result.append(obj)
						break
		return result

	def select_at_point(self, point, add_flag=False):
		result = self._select_at_point(point)
		if add_flag:
			self.add(result)
		else:
			self.set(result)

	def pick_at_point(self, point):
		return self._select_at_point(point)

	def select_all(self):
		result = []
		layers = self.presenter.get_editable_layers()
		for layer in layers:
			result += layer.childs
		self.set(result)

	def invert_selection(self):
		result = []
		layers = self.presenter.get_editable_layers()
		for layer in layers:
			for child in layer.childs:
				if child not in self.objs:
					result.append(child)
		self.set(result)

	def is_point_over(self, point):
		result = False
		if not self.objs:
			return result
		ret = self._select_at_point(point)
		if ret and ret[0] in self.objs:
			result = True
		return result

	def is_point_over_marker(self, point):
		result = []
		rect = point + point
		i = 0
		for marker in self.markers:
			if not i == 4 and is_bbox_in_rect(marker, rect):
				result.append(i)
				break
			i += 1
		return result

	def remove(self, objs):
		for obj in objs:
			if obj in self.objs:
				self.objs.remove(obj)
		self.update()

	def add(self, objs):
		for obj in objs:
			if obj in self.objs:
				self.objs.remove(obj)
			else:
				self.objs.append(obj)
		self.update()

	def set(self, objs):
		if objs and not objs[0]:objs = []
		self.center_offset = [0.0, 0.0]
		self.objs = objs
		self.update()

	def clear(self):
		self.objs = []
		self.update()
