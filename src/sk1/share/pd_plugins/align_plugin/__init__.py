# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2015 by Igor E. Novikov
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

		events.connect(events.DOC_CHANGED, self.update)
		events.connect(events.SELECTION_CHANGED, self.update)
		events.connect(events.DOC_MODIFIED, self.update)
		self.update()

	def update(self, *args):
		self.apanel.update()


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
		if not self.source.get_active():
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
