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
from uc2 import cms
from uc2.utils.config import XmlConfigParser

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

COLORS = [
('#FFFFFF', 'White'),
('#D4D0C8', 'Win2k'),
('#ECE9D8', 'WinXP'),
('#E0DFE3', 'WinXP Silver'),
('#F0F0F0', 'Win7'),
('#F2F1F0', 'Ubuntu'),
]


class Iconizer_Config(XmlConfigParser):

	system_encoding = 'utf-8'
	bg_color = (1.0, 1.0, 1.0)

class ImageCanvas(wal.ScrolledCanvas):

	def __init__(self, parent, bgcolor=None):
		wal.ScrolledCanvas.__init__(self, parent)
		if not bgcolor: bgcolor = wal.WHITE
		self.set_bg(bgcolor)
		self.set_size((190, 190))

class ImageViewer(wal.VPanel):

	def __init__(self, parent, bg):
		wal.VPanel.__init__(self, parent)
		self.set_bg(wal.UI_COLORS['pressed_border'])
		print bg
		self.canvas = ImageCanvas(self, cms.val_255(bg))
		self.pack(self.canvas, fill=True, expand=True, padding_all=1)

	def set_canvas_bg(self, color):
		color = cms.val_255(color)
		self.canvas.set_bg(color)
		self.canvas.refresh()


class Iconizer_Plugin(RS_Plugin):

	pid = 'IconizerPlugin'
	name = _('Iconizer')
	active_transform = None
	transforms = {}

	def build_ui(self):
		self.icon = get_icon(PLUGIN_ICON)

		self.config = Iconizer_Config()
		config_dir = self.app.appdata.app_config_dir
		config_file = os.path.join(config_dir, 'iconizer_config.xml')
		self.config.load(config_file)

		self.panel.pack((5, 5))
		hpanel = wal.HPanel(self.panel)
		hpanel.pack(wal.Label(hpanel, _('Background:')))
		self.bg_color_btn = wal.ColorButton(hpanel, self.config.bg_color,
										onchange=self.update, silent=False)
		hpanel.pack((5, 5))
		hpanel.pack(self.bg_color_btn)
		self.panel.pack(hpanel, padding=5)

		self.pallete = CBMiniPalette(self.panel, COLORS,
									onclick=self.bg_color_btn.set_value)
		self.panel.pack(self.pallete)

		self.panel.pack((10, 10))

		self.viewer = ImageViewer(self.panel, self.config.bg_color)
		self.panel.pack(self.viewer)

		self.panel.pack((10, 10))

		self.sel_check = wal.Checkbox(self.panel, _('Draw selected only'))
		self.panel.pack(self.sel_check)

		self.apply_btn = wal.Button(self.panel, _('Save image'))
		self.panel.pack(self.apply_btn, fill=True, padding_all=5)

		self.panel.pack((5, 5))

		self.panel.pack(wal.HLine(self.panel), fill=True)

		self.update()

	def save_config(self):
		config_dir = self.app.appdata.app_config_dir
		config_file = os.path.join(config_dir, 'iconizer_config.xml')
		self.config.save(config_file)


	def update(self, *args):
		color = self.bg_color_btn.get_value()
		if not color == self.config.bg_color:
			self.config.bg_color = color
			self.save_config()
			self.viewer.set_canvas_bg(self.config.bg_color)
