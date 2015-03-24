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

import wal

from uc2 import uc2const

from sk1 import config
from sk1.parts.ctxpanel import AppCtxPanel
from sk1.parts.tools import AppTools
from sk1.parts.doctabpanel import DocTabsPanel
from sk1.parts.plgarea import PlgArea
from sk1.parts.statusbar import AppStatusbar
from sk1.parts.palettepanel import AppHPalette, AppVPalette
from sk1.document import DocArea

class MDIArea(wal.VPanel):

	app = None
	mw = None
	docareas = []
	ctxpanel = None
	current_docarea = None

	def __init__(self, app, parent):
		self.app = app
		self.mw = parent
		self.docareas = []
		wal.VPanel.__init__(self, parent)

		if not wal.is_mac(): self.pack(wal.HLine(self), fill=True)

		#----- Context panel
		self.ctxpanel = AppCtxPanel(self.app, self)
		self.pack(self.ctxpanel, fill=True, padding=1)

		#----- Doc tabs
		self.dtp = DocTabsPanel(self)
		self.doc_tabs = self.dtp.doc_tabs
		self.pack(self.dtp, fill=True)

		hpanel = wal.HPanel(self)
		self.pack(hpanel, expand=True, fill=True)

		#----- Tools
		self.tools = AppTools(self.app, hpanel)
		hpanel.pack(self.tools, fill=True)
		hpanel.pack(wal.VLine(hpanel), fill=True)

		self.splitter = wal.Splitter(hpanel)
		self.doc_keeper = wal.VPanel(self.splitter)
		self.doc_keeper.SetBackgroundColour(wal.WHITE)
		self.plg_area = PlgArea(self.app, self.splitter)
		self.app.mdiarea = self
		self.app.plg_area = self.plg_area

		self.splitter.split_vertically(self.doc_keeper, self.plg_area)
		self.splitter.set_min_size(200)
		self.splitter.set_sash_gravity(1.0)
		self.splitter.unsplit()
		hpanel.pack(self.splitter, expand=True, fill=True)

		#----- Vertical Palette panel
		self.vp_panel = wal.HPanel(hpanel)
		self.vp_panel.pack(wal.VLine(self.vp_panel), fill=True, start_padding=2)
		vpalette_panel = AppVPalette(self.vp_panel, self.app)
		self.vp_panel.pack(vpalette_panel, fill=True, padding=2)
		hpanel.pack(self.vp_panel, fill=True)
		if config.palette_orientation == uc2const.HORIZONTAL:
			self.vp_panel.hide()

		#----- Horizontal Palette panel
		self.hp_panel = wal.VPanel(self)
		self.hp_panel.pack(wal.HLine(self.hp_panel), fill=True, padding=2)
		hpalette_panel = AppHPalette(self.hp_panel, self.app)
		self.hp_panel.pack(hpalette_panel, fill=True)
		self.pack(self.hp_panel, fill=True)
		if config.palette_orientation == uc2const.VERTICAL:
			self.hp_panel.hide()

		#----- Status bar
		self.pack(wal.HLine(self), fill=True, start_padding=2)
		self.statusbar = AppStatusbar(self)
		self.pack(self.statusbar, fill=True, padding=2)

		self.Layout()

	def create_docarea(self, doc):
		docarea = DocArea(doc, self.doc_keeper)
		docarea.hide()
		docarea.doc_tab = self.doc_tabs.add_new_tab(doc)
		self.docareas.append(docarea)
		self.doc_keeper.pack(docarea, expand=True, fill=True)
		return docarea

	def remove_doc(self, doc):
		docarea = doc.docarea
		self.docareas.remove(docarea)
		self.doc_keeper.remove(docarea)
		self.doc_tabs.remove_tab(doc)
		docarea.Hide()
		if not self.docareas:
			self.mw.show_mdi(False)
			self.current_docarea = None
		else:
			if docarea == self.current_docarea:
				self.set_active(self.docareas[-1].presenter)

	def set_tab_title(self, docarea, title):
		docarea.doc_tab.set_title(title)
		self.doc_tabs.layout()

	def set_active(self, doc):
		doc_area = doc.docarea
		if self.current_docarea: self.current_docarea.hide()
		doc_area.show()
		self.current_docarea = doc_area
		self.doc_tabs.set_active(doc)
		if len(self.docareas) == 1: self.mw.show_mdi(True)
		if self.plg_area.get_size()[0] > 400:
			self.splitter.set_sash_position(-250)
		self.doc_keeper.layout()

	def show_plugin_area(self, value=True):
		if value:
			if not self.plg_area.is_shown():
				self.splitter.split_vertically(self.doc_keeper,
											self.plg_area, -100)
		else:
			if self.plg_area.is_shown():
				self.splitter.unsplit()

