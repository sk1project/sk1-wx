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

import wx

from wal import const, ALL, EXPAND, VPanel, HPanel, HLine

from sk1 import events
from sk1.parts.ctxpanel import AppCtxPanel
from sk1.parts.tools import AppTools
from sk1.parts.doctabpanel import DocTabsPanel
from sk1.parts.plgarea import PlgArea
from sk1.document import DocArea

class MDIArea(VPanel):

	app = None
	mw = None
	docareas = []
	ctxpanel = None
	current_docarea = None

	def __init__(self, app, parent):
		self.app = app
		self.mw = parent
		self.docareas = []
		VPanel.__init__(self, parent)

		if not const.is_mac(): self.add(HLine(self), 0, ALL | EXPAND)

		#----- Context panel
		self.ctxpanel = AppCtxPanel(self.app, self)
		self.add(self.ctxpanel, 0, ALL)

		#----- Doc tabs
		self.dtp = DocTabsPanel(self)
		self.doc_tabs = self.dtp.doc_tabs
		self.add(self.dtp, 0, ALL | EXPAND)

		hpanel = HPanel(self)
		self.add(hpanel, 1, ALL | EXPAND)

		#----- Tools
		self.tools = AppTools(self.app, hpanel)
		hpanel.add(self.tools, 0, ALL | EXPAND)

		self.splitter = wx.SplitterWindow(hpanel, -1, style=wx.SP_LIVE_UPDATE)
		self.doc_keeper = VPanel(self.splitter)
		self.doc_keeper.SetBackgroundColour(wx.Colour(255, 255, 255))
		self.plg_area = PlgArea(self.app, self.splitter)
		self.app.mdiarea = self
		self.app.plg_area = self.plg_area

		self.splitter.SplitVertically(self.doc_keeper, self.plg_area, 0)
		self.splitter.SetMinimumPaneSize(200)
		self.splitter.SetSashGravity(1.0)
		self.splitter.Unsplit(None)
		hpanel.add(self.splitter, 1, ALL | EXPAND)

		self.Layout()
		events.connect(events.DOC_CHANGED, self.set_active)

	def hide(self):
		self.Hide()

	def create_docarea(self, doc):
		docarea = DocArea(doc, self.doc_keeper)
		docarea.Hide()
		docarea.doc_tab = self.doc_tabs.add_new_tab(doc)
		self.docareas.append(docarea)
		self.doc_keeper.add(docarea, 1, ALL | EXPAND)
		return docarea

	def remove_doc(self, doc):
		docarea = doc.docarea
		self.docareas.remove(docarea)
		self.doc_keeper.box.Detach(docarea)
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
		self.doc_tabs.Layout()

	def set_active(self, doc):
		doc_area = doc.docarea
		if self.current_docarea: self.current_docarea.Hide()
		doc_area.Show()
		self.current_docarea = doc_area
		self.doc_tabs.set_active(doc)
		if len(self.docareas) == 1: self.mw.show_mdi(True)
		if self.plg_area.GetSize()[0] > 400:
			self.splitter.SetSashPosition(-250)
		self.doc_keeper.Layout()

	def show_plugin_area(self, value=True):
		if value:
			if not self.plg_area.is_shown():
				self.splitter.SplitVertically(self.doc_keeper,
											self.plg_area, -100)
		else:
			if self.plg_area.is_shown():
				self.splitter.Unsplit(None)

