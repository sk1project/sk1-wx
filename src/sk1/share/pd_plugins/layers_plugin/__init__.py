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
from copy import deepcopy

from uc2.formats.sk2 import sk2_const
from uc2.libgeom import apply_trafo_to_paths
from uc2.libgeom import intersect_paths, fuse_paths, trim_paths, excluse_paths

from sk1 import _, events, modes
from sk1.dialogs import msg_dialog, yesno_dialog, error_dialog
from sk1.resources import icons, get_icon, get_bmp
from sk1.app_plugins import RS_Plugin

PLG_DIR = __path__[0]
IMG_DIR = os.path.join(PLG_DIR, 'images')

def make_artid(name):
	return os.path.join(IMG_DIR, name + '.png')

PLUGIN_ICON = make_artid('icon')


class Layers_Plugin(RS_Plugin):

	pid = 'LayersPlugin'
	name = _('Layers')
	active_panel = None
	panels = {}

	def build_ui(self):
		self.icon = get_icon(PLUGIN_ICON)


def get_plugin(app):
	return Layers_Plugin(app)