# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2013 by Igor E. Novikov
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

import os
import wx

from wal import ALL, EXPAND
from wal import MainWindow

from sk1 import config
from sk1.parts.menubar import AppMenuBar
from sk1.parts.toolbar import ToolbarCreator
from sk1.parts.mdiarea import MDIArea
from sk1.parts.stubpanel import AppStubPanel

class AppMainWindow(MainWindow):

	menubar = None
	mdi = None
	stub = None
	palette_panel = None
	statusbar = None

	def __init__(self, app):
		self.app = app
		height = max(config.mw_min_height, config.mw_height)
		width = max(config.mw_min_width, config.mw_width)
		size = (width, height)
		MainWindow.__init__(self, '', size, maximized=config.mw_maximized)
		self.set_minsize(config.mw_min_width, config.mw_min_height)
		self.icons = self.create_icon_bundle()
		self.SetIcons(self.icons)
		self.Bind(wx.EVT_CLOSE, self.app.exit, self)

	def build(self):
		#----- Menubar
		self.menubar = AppMenuBar(self.app, self)
		#----- Toolbar
		self.toolbar = ToolbarCreator(self).tb

		#----- MDI Area
		self.mdi = MDIArea(self.app, self)
		self.add(self.mdi, 1, ALL | EXPAND)
		if not config.new_doc_on_start:self.mdi.hide()

		#----- Stub panel
		self.stub = AppStubPanel(self)
		self.add(self.stub, 1, ALL | EXPAND)
		if config.new_doc_on_start:self.stub.hide()

		self.Layout()

	def set_title(self, title=''):
		appname = self.app.appdata.app_name
		if title: self.SetTitle('[%s] - %s' % (title, appname))
		else: self.SetTitle(appname)

	def create_icon_bundle(self):
		iconset_path = os.path.join(config.resource_dir, 'icons', 'generic')
		ret = wx.IconBundle()
		filename = 'pdesign-icon.ico'
		path = os.path.join(iconset_path, filename)
		ret.AddIconFromFile(path, wx.BITMAP_TYPE_ANY)
		return ret

	def test(self, event):pass

	def show_mdi(self, value):
		if value and not self.mdi.is_shown():
			self.stub.hide()
			self.mdi.show()
		elif not value and self.mdi.is_shown():
			self.stub.show()
			self.mdi.hide()
		self.Layout()
