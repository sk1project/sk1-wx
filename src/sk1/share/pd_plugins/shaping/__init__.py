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
from uc2.libgeom import intersect_paths, fusion_paths, apply_trafo_to_paths

from sk1 import _, events
from sk1.app_plugins import RS_Plugin
from sk1.resources import get_icon

PLG_DIR = __path__[0]
IMG_DIR = os.path.join(PLG_DIR, 'images')

def make_artid(name):
	return os.path.join(IMG_DIR, name + '.png')

def get_plugin(app):
	return Shaping_Plugin(app)

PLUGIN_ICON = make_artid('icon')

class Shaping_Plugin(RS_Plugin):

	pid = 'ShapingPlugin'
	name = 'Shaping'
	active_transform = None
	transforms = {}

	def build_ui(self):
		self.icon = get_icon(PLUGIN_ICON)

		self.apply_btn = wal.Button(self.panel, _('Apply'), onclick=self.action)
		self.panel.pack(self.apply_btn, fill=True, padding_all=5)

		events.connect(events.DOC_CHANGED, self.update)
		events.connect(events.SELECTION_CHANGED, self.update)
		events.connect(events.DOC_MODIFIED, self.update)
		self.update()

	def update(self, *args):
		pass

	def get_sel_count(self):
		doc = self.app.current_doc
		return len(doc.selection.objs)

	def action(self):
		if self.get_sel_count() < 2: return
		doc = self.app.current_doc
		sel_objs = [] + doc.selection.objs
		objs = sel_objs[:2]
		paths1 = apply_trafo_to_paths(objs[0].paths, objs[0].trafo)
		paths2 = apply_trafo_to_paths(objs[1].paths, objs[1].trafo)
		new_paths = fusion_paths(paths1, paths2)
		if new_paths:
			doc.api.create_curve(new_paths)
