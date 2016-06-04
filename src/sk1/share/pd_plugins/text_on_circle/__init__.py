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


import os, wal, math

from uc2.formats.sk2 import sk2_const

from sk1 import _, events
from sk1.app_plugins import RS_Plugin
from sk1.resources import get_icon, icons, get_bmp

PLG_DIR = __path__[0]
IMG_DIR = os.path.join(PLG_DIR, 'images')

def make_artid(name):
	return os.path.join(IMG_DIR, name + '.png')

def get_plugin(app):
	return TC_Plugin(app)

RIGHT_POS = 2
TOP_POS = 3
LEFT_POS = 0
BOTTOM_POS = 1

POSITIONS = [RIGHT_POS, TOP_POS, LEFT_POS, BOTTOM_POS]

POS_TEXTS = {
RIGHT_POS:_('Text on right side'),
TOP_POS:_('Text at top'),
LEFT_POS:_('Text on left side'),
BOTTOM_POS:_('Text at bottom'),
}

POS_PICS = {
RIGHT_POS:make_artid('pos-00'),
TOP_POS:make_artid('pos-10'),
LEFT_POS:make_artid('pos-20'),
BOTTOM_POS:make_artid('pos-30'),
}

POS_PICS_OTHERSIDE = {
RIGHT_POS:make_artid('pos-01'),
TOP_POS:make_artid('pos-11'),
LEFT_POS:make_artid('pos-21'),
BOTTOM_POS:make_artid('pos-31'),
}

PLUGIN_ICON = make_artid('icon')

class PositionSwitch(wal.Bitmap):

	mode = TOP_POS
	side_flag = False

	def __init__(self, parent, mode=TOP_POS, side_flag=False):
		self.mode = mode
		self.side_flag = side_flag
		wal.Bitmap.__init__(self, parent, self.load_bmp(),
						on_left_click=self.on_click)

	def set_side(self, flag):
		self.side_flag = flag
		self.update_bmp()

	def set_mode(self, mode):
		if not mode == self.mode:
			self.mode = mode
			self.update_bmp()

	def get_mode(self): return self.mode

	def load_bmp(self):
		if self.side_flag:
			return get_icon(POS_PICS_OTHERSIDE[self.mode], size=wal.DEF_SIZE)
		return get_icon(POS_PICS[self.mode], size=wal.DEF_SIZE)

	def update_bmp(self):
		self.set_bitmap(self.load_bmp())

	def on_click(self, event):
		w, h = self.get_size()
		x, y = event.get_point()
		if y < h / 2.0 and x < w / 2.0:
			if y > x: mode = LEFT_POS
			else: mode = TOP_POS
		elif y >= h / 2.0 and x >= w / 2.0:
			if y > x: mode = BOTTOM_POS
			else: mode = RIGHT_POS
		elif y < h / 2.0 and x >= w / 2.0:
			if h - y > x: mode = TOP_POS
			else: mode = RIGHT_POS
		elif y >= h / 2.0 and x < w / 2.0:
			if h - y > x: mode = LEFT_POS
			else: mode = BOTTOM_POS
		self.set_mode(mode)


class TC_Plugin(RS_Plugin):

	pid = 'TextOnCirclePlugin'
	name = _('Text on Circle')
	active_transform = None
	transforms = {}

	def build_ui(self):
		self.icon = get_icon(PLUGIN_ICON)
		panel = wal.VPanel(self.panel)

		panel.pack(wal.Label(panel, _('Text position on circle')), padding_all=5)

		self.bmp = PositionSwitch(panel)
		panel.pack(self.bmp, padding_all=5)

		self.other_side = wal.Checkbox(panel, _('Place on other side'),
									onclick=self.update_bmp)
		panel.pack(self.other_side, padding=5)

		self.apply_btn = wal.Button(panel, _('Apply'), onclick=self.action)
		panel.pack(self.apply_btn, padding=5, fill=True)

		self.panel.pack(panel, fill=True, padding_all=5)
		self.panel.pack(wal.HLine(self.panel), fill=True)

		events.connect(events.DOC_CHANGED, self.update)
		events.connect(events.SELECTION_CHANGED, self.update)
		events.connect(events.DOC_MODIFIED, self.update)

		self.update()

	def show_signal(self, *args):self.update()

	def set_state(self, state):
		self.apply_btn.set_enable(state)
		self.bmp.set_enable(state)
		self.other_side.set_enable(state)

	def update_bmp(self):
		self.bmp.set_side(self.other_side.get_value())

	def update_from_tpgroup(self):
		doc = self.app.current_doc
		if len(doc.selection.objs) == 1 and \
		doc.selection.objs[0].is_tpgroup() and \
		doc.selection.objs[0].childs[0].is_circle():
			tpgroup = doc.selection.objs[0]
			data = tpgroup.childs_data[1]
			self.other_side.set_value(not data[2])
			circle = tpgroup.childs[0]
			if circle.angle1 == 0:
				mode = LEFT_POS
			elif circle.angle1 == math.pi / 2.0:
				mode = BOTTOM_POS
			elif circle.angle1 == math.pi:
				mode = RIGHT_POS
			else:
				mode = TOP_POS
			self.bmp.set_mode(mode)


	def check_selection(self):
		doc = self.app.current_doc
		if len(doc.selection.objs) == 1 and \
		doc.selection.objs[0].is_tpgroup() and \
		doc.selection.objs[0].childs[0].is_circle():
			return 1
		elif len(doc.selection.objs) == 2:
			obj1 = doc.selection.objs[0]
			obj2 = doc.selection.objs[1]
			if obj1.is_circle() and obj2.is_text(): return 2
			elif obj2.is_circle() and obj1.is_text(): return 2
		return False

	def update(self, *args):
		if not self.is_shown(): return
		state = False
		if self.app.insp.is_selection():
			ret = self.check_selection()
			if ret: state = True
			if ret == 1: self.update_from_tpgroup()
		self.set_state(state)

	def action(self):
		doc = self.app.current_doc
		if self.check_selection() == 2:
			circle = doc.selection.objs[0]
			text_obj = doc.selection.objs[1]
			if text_obj.is_circle() and circle.is_text():
				circle, text_obj = text_obj, circle
			doc.api.place_text_on_circle(circle, text_obj, self.bmp.get_mode(),
										not self.other_side.get_value())
		elif self.check_selection() == 1:
			tpgroup = doc.selection.objs[0]
			text_obj = tpgroup.childs[1]
			doc.api.change_tcgroup(tpgroup, text_obj, self.bmp.get_mode(),
										not self.other_side.get_value())
