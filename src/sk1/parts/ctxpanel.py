# -*- coding: utf-8 -*-
#
#	Copyright (C) 2013 by Igor E. Novikov
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

from wal import HPanel

from sk1 import events, modes
from sk1.context import PLUGINS, NO_DOC, DEFAULT, MULTIPLE, GROUP, \
RECTANGLE, CIRCLE, POLYGON, CURVE, TEXT, PIXMAP

class AppCtxPanel(HPanel):

	app = None
	mode = None
	plugins_dict = {}
	plugins = []

	def __init__(self, app, parent):
		self.app = app
		self.insp = app.insp
		HPanel.__init__(self, parent)
		spacer = (5, 30)
		self.add(spacer)

		for item in PLUGINS:
			plg = item(self.app, self)
			self.plugins_dict[plg.name] = plg

		events.connect(events.NO_DOCS, self.rebuild)
		events.connect(events.DOC_CHANGED, self.rebuild)
		events.connect(events.SELECTION_CHANGED, self.rebuild)
		events.connect(events.MODE_CHANGED, self.rebuild)
		self.rebuild()

	def rebuild(self, *args):
		mode = self.get_mode()
		if mode == self.mode:return
		for item in self.plugins:
			item.hide()
			self.remove(item)
		self.plugins = []
		if mode:
			for item in mode:
				self.pack(self.plugins_dict[item])
				self.plugins_dict[item].show(update=False)
				self.plugins.append(self.plugins_dict[item])
		self.Layout()
		self.Fit()
		self.mode = mode

	def get_mode(self):
		ret = []
		if not self.insp.is_doc():
			return NO_DOC
		if not self.insp.is_selection():
			ret = DEFAULT
		else:
			doc = self.app.current_doc
			sel = doc.selection.objs
			if len(sel) > 1:
				ret = MULTIPLE
			elif self.insp.is_obj_rect(sel[0]):
				ret = RECTANGLE
			elif self.insp.is_obj_circle(sel[0]):
				ret = CIRCLE
			elif self.insp.is_obj_polygon(sel[0]):
				ret = POLYGON
			elif self.insp.is_obj_curve(sel[0]):
				ret = CURVE
			elif self.insp.can_be_ungrouped():
				ret = GROUP
			elif self.insp.is_obj_pixmap(sel[0]):
				ret = PIXMAP
			else:
				ret = DEFAULT
		if self.insp.is_mode(modes.POLYGON_MODE):
			ret = ['PolygonCfgPlugin'] + ret
		return ret
