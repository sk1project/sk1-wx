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

import os, sys

from wal import VPanel

from sk1 import _, config

def check_package(path, name):
	full_path = os.path.join(path, name)
	if not os.path.isdir(full_path): return False
	if name[0] == '.': return False
	init_file = os.path.join(full_path, '__init__.py')
	if not os.path.lexists(init_file): return False
	return True

def scan_plugins(app):
	ret = {}
	for path in config.plugin_dirs:
		sys.path.insert(0, path)
		plgs = []
		for item in os.listdir(path):
			if check_package(path, item):
				plgs.append(item)
		if plgs:
			bn = os.path.basename(path)
			for item in plgs:
				try:
					pkg = __import__(bn + '.' + item)
					plg_mod = getattr(pkg, item)
					pobj = plg_mod.get_plugin(app)
					ret[pobj.pid] = pobj
				except:
					print 'Error while importing ' + item + ' plugin'
	return ret

class RS_Plugin:

	pid = 'plugin'
	name = _('plugin')
	activated = False
	app = None
	panel = None
	icon = None
	plg_tab = None

	def __init__(self, app):
		self.app = app

	def build_ui(self):pass

	def activate(self):
		if not self.activated:
			self.panel = VPanel(self.app.plg_area.container)
			self.activated = True
			self.build_ui()

	def show(self, *args):
		self.panel.show()
		self.show_signal(*args)

	def hide(self):
		self.panel.hide()
		self.hide_signal()

	def show_signal(self, *args):pass
	def hide_signal(self):pass
