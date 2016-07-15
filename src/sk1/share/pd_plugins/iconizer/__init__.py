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
from sk1.pwidgets import CBMiniPalette

PLG_DIR = __path__[0]
IMG_DIR = os.path.join(PLG_DIR, 'images')

def make_artid(name):
	return os.path.join(IMG_DIR, name + '.png')

def get_plugin(app):
	return Iconizer_Plugin(app)

PLUGIN_ICON = make_artid('icon')

class ImageViewer(wal.VPanel):

	int_panel = None

	def __init__(self, parent, bg):
		wal.VPanel.__init__(self, parent)
		self.set_bg(wal.UI_COLORS['pressed_border'])
		self.int_panel = wal.VPanel(self)
		self.int_panel.set_bg(bg)
		self.int_panel.pack((190, 190))
		self.pack(self.int_panel, padding_all=1)


class Iconizer_Plugin(RS_Plugin):

	pid = 'IconizerPlugin'
	name = _('Iconizer')
	active_transform = None
	transforms = {}

	def build_ui(self):
		self.icon = get_icon(PLUGIN_ICON)

		self.panel.pack((5, 5))
		hpanel = wal.HPanel(self.panel)
		hpanel.pack(wal.Label(hpanel, _('Background:')))
		color = wal.UI_COLORS['bg']
		print color
		self.bg_color_btn = wal.ColorButton(hpanel, color)
		hpanel.pack((5, 5))
		hpanel.pack(self.bg_color_btn)
		self.panel.pack(hpanel, padding=5)

		self.pallete = CBMiniPalette(self.panel)
		self.panel.pack(self.pallete)

		self.panel.pack((10, 10))

		self.viewer = ImageViewer(self.panel, color)
		self.panel.pack(self.viewer)

		self.panel.pack((10, 10))

		self.sel_check = wal.Checkbox(self.panel, _('Draw selected only'))
		self.panel.pack(self.sel_check)

		self.apply_btn = wal.Button(self.panel, _('Save image'))
		self.panel.pack(self.apply_btn, fill=True, padding_all=5)

		self.panel.pack((5, 5))

		self.panel.pack(wal.HLine(self.panel), fill=True)

		self.update()

	def update(self, *args):pass
