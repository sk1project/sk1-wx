# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2016 by Igor E. Novikov
#
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
#
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
#
# 	You should have received a copy of the GNU General Public License
# 	along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os, wal

from uc2.formats.sk2 import sk2_const

from sk1 import _, events
from sk1.app_plugins import RS_Plugin
from sk1.resources import get_icon

PLG_DIR = __path__[0]
IMG_DIR = os.path.join(PLG_DIR, 'images')

def make_artid(name):
	return os.path.join(IMG_DIR, name + '.png')

def get_plugin(app):
	return Align_Plugin(app)

PLUGIN_ICON = make_artid('icon')

#--- Source object constants

SOURCE_PAGE = 0
SOURCE_SEL = 1
SOURCE_FIRST = 2
SOURCE_LAST = 3
SOURCE_BIGGEST = 4
SOURCE_SMALLEST = 5

SOURCE_NAMES = [
_('Page'),
_('Selection'),
_('First selected'),
_('Last selected'),
_('Biggest object'),
_('Smallest object'),
]

#--- Align constants

ALIGN_BOTTOM = -1.0
ALIGN_LEFT = -1.0
ALIGN_CENTER = 0.0
ALIGN_RIGHT = 1.0
ALIGN_TOP = 1.0

H_ALIGN_MODES = [ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT]

H_ALIGN_MODE_ICONS = {
ALIGN_LEFT:make_artid('align-left'),
ALIGN_CENTER:make_artid('align-center-h'),
ALIGN_RIGHT:make_artid('align-right')
}

H_ALIGN_MODE_NAMES = {
ALIGN_LEFT:_('Align to left side'),
ALIGN_CENTER:_('Align to center horizontally'),
ALIGN_RIGHT:_('Align to right side')
}

V_ALIGN_MODES = [ALIGN_BOTTOM, ALIGN_CENTER, ALIGN_TOP]

V_ALIGN_MODE_ICONS = {
ALIGN_BOTTOM:make_artid('align-bottom'),
ALIGN_CENTER:make_artid('align-center-v'),
ALIGN_TOP:make_artid('align-top')
}

V_ALIGN_MODE_NAMES = {
ALIGN_BOTTOM:_('Align to bottom'),
ALIGN_CENTER:_('Align to center vertically'),
ALIGN_TOP:_('Align to top')
}

class Align_Plugin(RS_Plugin):

	pid = 'AlignPlugin'
	name = 'Align and Distribute'
	active_transform = None
	transforms = {}

	def build_ui(self):
		self.icon = get_icon(PLUGIN_ICON)

		self.apanel = AlignPanel(self.panel, self.app)
		self.panel.pack(self.apanel, fill=True, padding_all=5)

		self.dpanel = DistributePanel(self.panel, self.app)
		self.panel.pack(self.dpanel, fill=True, padding_all=5)

		events.connect(events.DOC_CHANGED, self.update)
		events.connect(events.SELECTION_CHANGED, self.update)
		events.connect(events.DOC_MODIFIED, self.update)
		self.update()

	def update(self, *args):
		self.apanel.update()
		self.dpanel.update()


class AlignPanel(wal.LabeledPanel):

	app = None

	def __init__(self, parent, app):
		self.app = app
		wal.LabeledPanel.__init__(self, parent, _('Align'))

		self.pack((5, 5))
		self.pack(wal.Label(self, _('Relative to:')))
		self.source = wal.Combolist(self, items=SOURCE_NAMES,
								onchange=self.update)
		self.pack(self.source, padding_all=5, fill=True)
		self.pack((5, 5))

		self.halign = wal.HToggleKeeper(self, H_ALIGN_MODES,
								H_ALIGN_MODE_ICONS, H_ALIGN_MODE_NAMES,
								on_change=self.update, allow_none=True)
		self.pack(self.halign)
		self.halign.set_mode(ALIGN_CENTER)

		self.valign = wal.HToggleKeeper(self, V_ALIGN_MODES,
								V_ALIGN_MODE_ICONS, V_ALIGN_MODE_NAMES,
								on_change=self.update, allow_none=True)
		self.pack(self.valign, padding_all=5)
		self.valign.set_mode(ALIGN_CENTER)

		self.group = wal.Checkbox(self, _('Selection as group'), True,
								onclick=self.update)
		self.pack(self.group, padding_all=5)

		self.apply_btn = wal.Button(self, _('Apply'), onclick=self.action)
		self.pack(self.apply_btn, padding_all=5, fill=True)

	def get_sel_count(self):
		doc = self.app.current_doc
		return len(doc.selection.objs)

	def get_selection_bbox(self):
		doc = self.app.current_doc
		return [] + doc.selection.bbox

	def get_selection_size(self):
		bbox = self.get_selection_bbox()
		return (bbox[2] - bbox[0], bbox[3] - bbox[1])

	def update(self, *args):
		self.source.set_enable(False)
		self.halign.set_enable(False)
		self.valign.set_enable(False)
		self.group.set_enable(False)
		self.apply_btn.set_enable(False)
		if not self.app.insp.is_selection(): return
		self.source.set_enable(True)
		if self.source.get_active():
			self.group.set_value(False, False)
			if self.get_sel_count() < 2: return
			if self.get_sel_count() == 2 and self.group.get_value():return
		self.halign.set_enable(True)
		self.valign.set_enable(True)
		if self.get_sel_count() > 1 and not self.source.get_active():
			self.group.set_enable(True)
		self.apply_btn.set_enable(True)
		if self.valign.get_mode() is None and self.halign.get_mode() is None:
			self.apply_btn.set_enable(False)

	def get_obj_areas(self, objs):
		areas = []
		for obj in objs:
			bbox = obj.cache_bbox
			areas.append((bbox[2] - bbox[0]) * (bbox[3] - bbox[1]))
		return areas

	def get_smallest_obj(self, objs):
		areas = self.get_obj_areas(objs)
		return objs[areas.index(min(areas))]

	def get_biggest_obj(self, objs):
		areas = self.get_obj_areas(objs)
		return objs[areas.index(max(areas))]

	def get_trafo(self, source_bbox, target_bbox):
		sw = source_bbox[2] - source_bbox[0]
		sh = source_bbox[3] - source_bbox[1]
		tw = target_bbox[2] - target_bbox[0]
		th = target_bbox[3] - target_bbox[1]
		trafo = [] + sk2_const.NORMAL_TRAFO
		cs = source_bbox[:2]
		cs[0] += sw / 2.0
		cs[1] += sh / 2.0
		ct = target_bbox[:2]
		ct[0] += tw / 2.0
		ct[1] += th / 2.0
		if not self.halign.get_mode() is None:
			trafo[4] += cs[0] + self.halign.get_mode() * sw / 2.0
			trafo[4] -= ct[0] + self.halign.get_mode() * tw / 2.0
		if not self.valign.get_mode() is None:
			trafo[5] += cs[1] + self.valign.get_mode() * sh / 2.0
			trafo[5] -= ct[1] + self.valign.get_mode() * th / 2.0
		return trafo

	def action(self):
		doc = self.app.current_doc
		if self.source.get_active() == SOURCE_PAGE:
			pw, ph = doc.get_page_size()
			source_bbox = [-pw / 2.0, -ph / 2.0, pw / 2.0, ph / 2.0]
			if self.group.get_value():
				trafo = self.get_trafo(source_bbox, self.get_selection_bbox())
				doc.api.transform_selected(trafo)
				return
			else:
				sel_objs = [] + doc.selection.objs
		elif self.source.get_active() == SOURCE_SEL:
			source_bbox = self.get_selection_bbox()
			sel_objs = [] + doc.selection.objs
		elif self.source.get_active() == SOURCE_FIRST:
			source_bbox = [] + doc.selection.objs[0].cache_bbox
			sel_objs = self.app.current_doc.selection.objs[1:]
		elif self.source.get_active() == SOURCE_LAST:
			source_bbox = [] + doc.selection.objs[-1].cache_bbox
			sel_objs = self.app.current_doc.selection.objs[:-1]
		elif self.source.get_active() == SOURCE_SMALLEST:
			sel_objs = [] + doc.selection.objs
			smallest = self.get_smallest_obj(sel_objs)
			source_bbox = [] + smallest.cache_bbox
			sel_objs.remove(smallest)
		elif self.source.get_active() == SOURCE_BIGGEST:
			sel_objs = [] + doc.selection.objs
			biggest = self.get_biggest_obj(sel_objs)
			source_bbox = [] + biggest.cache_bbox
			sel_objs.remove(biggest)

		obj_trafo_list = []
		for item in sel_objs:
			trafo = self.get_trafo(source_bbox, item.cache_bbox)
			obj_trafo_list.append((item, trafo))
		doc.api.trasform_objs(obj_trafo_list)


#--- Distribute constants

DISTRIBUTE_LEFT = 0
DISTRIBUTE_BOTTOM = 1
DISTRIBUTE_HCENTER = 4
DISTRIBUTE_VCENTER = 5
DISTRIBUTE_RIGHT = 2
DISTRIBUTE_TOP = 3
DISTRIBUTE_HGAP = 6
DISTRIBUTE_VGAP = 7

H_DISTRIBUTE_MODES = [DISTRIBUTE_LEFT, DISTRIBUTE_HCENTER,
					DISTRIBUTE_RIGHT, DISTRIBUTE_HGAP]

H_DISTRIBUTE_MODE_ICONS = {
DISTRIBUTE_LEFT:make_artid('distribute-h-le'),
DISTRIBUTE_HCENTER:make_artid('distribute-h-c'),
DISTRIBUTE_RIGHT:make_artid('distribute-h-re'),
DISTRIBUTE_HGAP:make_artid('distribute-h-gap')
}

H_DISTRIBUTE_MODE_NAMES = {
DISTRIBUTE_LEFT:_('Distribute by left side horizontally'),
DISTRIBUTE_HCENTER:_('Distribute by center horizontally'),
DISTRIBUTE_RIGHT:_('Distribute by right side horizontally'),
DISTRIBUTE_HGAP:_('Equal gap horizontally')
}

V_DISTRIBUTE_MODES = [DISTRIBUTE_BOTTOM, DISTRIBUTE_VCENTER,
					DISTRIBUTE_TOP, DISTRIBUTE_VGAP]

V_DISTRIBUTE_MODE_ICONS = {
DISTRIBUTE_BOTTOM:make_artid('distribute-v-be'),
DISTRIBUTE_VCENTER:make_artid('distribute-v-c'),
DISTRIBUTE_TOP:make_artid('distribute-v-te'),
DISTRIBUTE_VGAP:make_artid('distribute-v-gap')
}

V_DISTRIBUTE_MODE_NAMES = {
DISTRIBUTE_BOTTOM:_('Distribute by bottom side vertically'),
DISTRIBUTE_VCENTER:_('Distribute by center vertically'),
DISTRIBUTE_TOP:_('Distribute by top side vertically'),
DISTRIBUTE_VGAP:_('Equal gap vertically')
}

class DistributePanel(wal.LabeledPanel):

	app = None

	def __init__(self, parent, app):
		self.app = app
		wal.LabeledPanel.__init__(self, parent, _('Distribute'))

		self.pack((5, 5))

		self.hdistrib = wal.HToggleKeeper(self, H_DISTRIBUTE_MODES,
							H_DISTRIBUTE_MODE_ICONS, H_DISTRIBUTE_MODE_NAMES,
							on_change=self.update, allow_none=True)
		self.pack(self.hdistrib)
		self.hdistrib.set_mode(DISTRIBUTE_HCENTER)

		self.vdistrib = wal.HToggleKeeper(self, V_DISTRIBUTE_MODES,
							V_DISTRIBUTE_MODE_ICONS, V_DISTRIBUTE_MODE_NAMES,
							on_change=self.update, allow_none=True)
		self.pack(self.vdistrib, padding_all=5)
		self.vdistrib.set_mode(DISTRIBUTE_VCENTER)

		self.apply_btn = wal.Button(self, _('Apply'), onclick=self.action)
		self.pack(self.apply_btn, padding_all=5, fill=True)

	def update(self, *args):
		self.hdistrib.set_enable(False)
		self.vdistrib.set_enable(False)
		self.apply_btn.set_enable(False)
		if not self.app.insp.is_selection(): return
		if len(self.app.current_doc.selection.objs) < 3: return
		self.hdistrib.set_enable(True)
		self.vdistrib.set_enable(True)
		if not self.hdistrib.get_mode() is None or \
		not self.vdistrib.get_mode() is None:
			self.apply_btn.set_enable(True)

	def get_coord(self, obj, index):
		bbox = obj.cache_bbox
		if index < 4:
			return bbox[index]
		elif index == 4:
			return bbox[0] + (bbox[2] - bbox[0]) / 2.0
		else:
			return bbox[1] + (bbox[3] - bbox[1]) / 2.0

	def get_obj_width(self, obj):
		bbox = obj.cache_bbox
		return bbox[2] - bbox[0]

	def get_obj_height(self, obj):
		bbox = obj.cache_bbox
		return bbox[3] - bbox[1]

	def get_coord_list(self, objs, index=0):
		ret = []
		for obj in objs:
			ret.append(self.get_coord(obj, index))
		return ret

	def sort_objs(self, objs, index=0):
		objs = [] + objs
		coords = self.get_coord_list(objs, index)
		new_coords = [] + coords
		new_coords.sort()
		new_objs = []
		for item in new_coords:
			index = coords.index(item)
			obj = objs[index]
			coords.remove(item)
			objs.remove(obj)
			new_objs.append(obj)
		return new_objs, new_coords

	def action(self):
		doc = self.app.current_doc
		objs = [] + doc.selection.objs
		trafo_dict = {}
		for obj in objs:
			trafo_dict[obj] = [] + sk2_const.NORMAL_TRAFO

		if not self.hdistrib.get_mode() is None:
			mode = self.hdistrib.get_mode()
			if mode < DISTRIBUTE_HGAP:
				new_objs, coords = self.sort_objs(objs, mode)
				shift = (coords[-1] - coords[0]) / float(len(objs) - 1)
				i = 0.0
				start = self.get_coord(new_objs[0], mode)
				for obj in new_objs:
					coord = self.get_coord(obj, mode)
					trafo_dict[obj][4] += start + i * shift - coord
					i += 1.0
			else:
				new_objs, coords = self.sort_objs(objs, DISTRIBUTE_LEFT)
				total_w = 0
				for obj in new_objs:
					total_w += self.get_obj_width(obj)
				available_w = self.get_coord(new_objs[-1], DISTRIBUTE_RIGHT)
				available_w -= self.get_coord(new_objs[0], DISTRIBUTE_LEFT)
				shift = (available_w - total_w) / float(len(objs) - 1)
				pos = self.get_coord(new_objs[0], DISTRIBUTE_RIGHT)
				for obj in new_objs[1:-1]:
					pos += shift
					coord = self.get_coord(obj, DISTRIBUTE_LEFT)
					trafo_dict[obj][4] += pos - coord
					pos += self.get_obj_width(obj)

		if not self.vdistrib.get_mode() is None:
			mode = self.vdistrib.get_mode()
			if mode < DISTRIBUTE_VGAP:
				new_objs, coords = self.sort_objs(objs, mode)
				shift = (coords[-1] - coords[0]) / float(len(objs) - 1)
				i = 0.0
				start = self.get_coord(new_objs[0], mode)
				for obj in new_objs:
					coord = self.get_coord(obj, mode)
					trafo_dict[obj][5] += start + i * shift - coord
					i += 1.0
			else:
				new_objs, coords = self.sort_objs(objs, DISTRIBUTE_BOTTOM)
				total_h = 0
				for obj in new_objs:
					total_h += self.get_obj_height(obj)
				available_h = self.get_coord(new_objs[-1], DISTRIBUTE_TOP)
				available_h -= self.get_coord(new_objs[0], DISTRIBUTE_BOTTOM)
				shift = (available_h - total_h) / float(len(objs) - 1)
				pos = self.get_coord(new_objs[0], DISTRIBUTE_TOP)
				for obj in new_objs[1:-1]:
					pos += shift
					coord = self.get_coord(obj, DISTRIBUTE_BOTTOM)
					trafo_dict[obj][5] += pos - coord
					pos += self.get_obj_height(obj)


		obj_trafo_list = []
		for item in objs:
			obj_trafo_list.append((item, trafo_dict[item]))
		doc.api.trasform_objs(obj_trafo_list)


