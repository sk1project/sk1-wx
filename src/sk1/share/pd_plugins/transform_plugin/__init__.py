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

from sk1 import _, events
from sk1.app_plugins import RS_Plugin
from sk1.resources import get_icon

from indicator import OrientationIndicator

PLG_DIR = __path__[0]
IMG_DIR = os.path.join(PLG_DIR, 'images')

def make_artid(name):
	return os.path.join(IMG_DIR, name + '.png')

POSITION_MODE = 0
RESIZE_MODE = 1
SCALE_MODE = 2
ROTATE_MODE = 3
SHEAR_MODE = 4

TRANSFORM_MODES = [POSITION_MODE, RESIZE_MODE, SCALE_MODE,
				ROTATE_MODE, SHEAR_MODE]

TRANSFORM_MODE_ICONS = {
POSITION_MODE:make_artid('tab-position'),
RESIZE_MODE:make_artid('tab-resize'),
SCALE_MODE:make_artid('tab-scale'),
ROTATE_MODE:make_artid('tab-rotate'),
SHEAR_MODE:make_artid('tab-shear')
}

TRANSFORM_MODE_NAMES = {
POSITION_MODE:_('Position'),
RESIZE_MODE:_('Resizing'),
SCALE_MODE:_('Scale and mirror'),
ROTATE_MODE:_('Rotating'),
SHEAR_MODE:_('Shearing')
}

PLUGIN_ICON = make_artid('icon')

def get_plugin(app):
	return Transform_Plugin(app)

class Transform_Plugin(RS_Plugin):

	pid = 'TransformPlugin'
	name = 'Transformations'

	def build_ui(self):
		self.icon = get_icon(PLUGIN_ICON)
		panel = wal.VPanel(self.panel)
		self.transform_keeper = wal.HToggleKeeper(panel, TRANSFORM_MODES,
							TRANSFORM_MODE_ICONS,
							TRANSFORM_MODE_NAMES, self.on_mode_change)
		panel.pack(self.transform_keeper)
		panel.pack(wal.HLine(panel), fill=True, padding=3)

		panel.pack(OrientationIndicator(panel), padding_all=10)

		self.apply_copy_btn = wal.Button(panel, _('Apply to copy'),
							onclick=self.action_copy)
		panel.pack(self.apply_copy_btn, fill=True)

		self.apply_btn = wal.Button(panel, _('Apply'), onclick=self.action)
		panel.pack(self.apply_btn, padding=3, fill=True)

		panel.pack(wal.HLine(panel), fill=True)

		self.panel.pack(panel, fill=True, expand=True, padding_all=5)

		events.connect(events.DOC_CHANGED, self.update)
		events.connect(events.SELECTION_CHANGED, self.update)
		self.update()

	def on_mode_change(self, mode):pass
	def action_copy(self): self.action(True)
	def action(self, copy=False):pass

	def update(self, *args):
		state = False
		if self.app.insp.is_selection(): state = True
		self.apply_btn.set_enable(state)
		self.apply_copy_btn.set_enable(state)

	def show_signal(self, mode=POSITION_MODE, *args):
		self.transform_keeper.set_mode(mode)
