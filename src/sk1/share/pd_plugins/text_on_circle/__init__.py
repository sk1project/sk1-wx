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

class TC_Plugin(RS_Plugin):

	pid = 'TextOnCirclePlugin'
	name = _('Text on Circle')
	active_transform = None
	transforms = {}

	def build_ui(self):
		self.icon = get_icon(PLUGIN_ICON)
		panel = wal.VPanel(self.panel)

		panel.pack(wal.Label(panel, _('Text position on circle')), padding_all=5)

		self.bmp = get_bmp(panel, POS_PICS[TOP_POS])
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

	def update_bmp(self): pass

	def update(self, *args):pass

	def action(self):pass
