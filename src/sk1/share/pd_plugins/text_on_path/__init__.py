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
	return TP_Plugin(app)

PLUGIN_ICON = make_artid('icon')

TEXT_ALIGNS = [sk2_const.TEXT_ALIGN_LEFT, sk2_const.TEXT_ALIGN_CENTER,
			sk2_const.TEXT_ALIGN_RIGHT, sk2_const.TEXT_ALIGN_JUSTIFY]

TEXT_ALIGN_ICONS = {
sk2_const.TEXT_ALIGN_LEFT:icons.PD_ALIGN_LEFT,
sk2_const.TEXT_ALIGN_CENTER:icons.PD_ALIGN_CENTER,
sk2_const.TEXT_ALIGN_RIGHT:icons.PD_ALIGN_RIGHT,
sk2_const.TEXT_ALIGN_JUSTIFY:icons.PD_ALIGN_JUSTIFY,
}

TEXT_ALIGN_TEXTS = {
sk2_const.TEXT_ALIGN_LEFT:_('Align to path start'),
sk2_const.TEXT_ALIGN_CENTER:_('Align to path center'),
sk2_const.TEXT_ALIGN_RIGHT:_('Align to path end'),
sk2_const.TEXT_ALIGN_JUSTIFY:_('Stretch along path'),
}

TEXT_ALIGN_PICS = {
sk2_const.TEXT_ALIGN_LEFT:make_artid('pos-start'),
}

class TP_Plugin(RS_Plugin):

	pid = 'TextOnPathPlugin'
	name = _('Text on Path')
	active_transform = None
	transforms = {}

	def build_ui(self):
		self.icon = get_icon(PLUGIN_ICON)
		panel = wal.VPanel(self.panel)

		panel.pack(wal.Label(panel, _('Text position on path')), padding_all=5)

		self.align_keeper = wal.HToggleKeeper(panel, TEXT_ALIGNS,
							TEXT_ALIGN_ICONS,
							TEXT_ALIGN_TEXTS)
		panel.pack(self.align_keeper)
		self.align_keeper.set_mode(sk2_const.TEXT_ALIGN_LEFT)

		border = wal.VPanel(panel)
		color = wal.GRAY
		if wal.is_gtk():color = wal.UI_COLORS['pressed_border']
		border.set_bg(color)
		self.pic_panel = wal.VPanel(border)
		self.pic_panel.set_bg(wal.WHITE)
		self.bmp = get_bmp(self.pic_panel,
						TEXT_ALIGN_PICS[sk2_const.TEXT_ALIGN_LEFT])
		self.pic_panel.pack(self.bmp, padding_all=5)
		border.pack(self.pic_panel, padding_all=1)
		panel.pack(border, padding=10)

		self.other_side = wal.Checkbox(panel, _('Place on other side'))
		panel.pack(self.other_side, padding=5)

		self.apply_btn = wal.Button(panel, _('Apply'), onclick=self.action)
		panel.pack(self.apply_btn, padding=5, fill=True)

		self.panel.pack(panel, fill=True, padding_all=5)
		self.panel.pack(wal.HLine(self.panel), fill=True)

		self.update()

	def update(self, *args):pass
	def action(self):pass

