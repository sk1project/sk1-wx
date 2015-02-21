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

import wx

from sk1 import config
from sk1.resources import pdids
from sk1.widgets import const
from sk1.pwidgets import MacTB_ActionButton, MacTB_ActionNestedButtons

TBFLAGS = (wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT)

BUTTONS = [(wx.ID_NEW,), None, (wx.ID_OPEN, wx.ID_SAVE, wx.ID_SAVEAS,
		wx.ID_CLOSE), None, (wx.ID_PRINT,), None, (wx.ID_UNDO, wx.ID_REDO),
		None, (wx.ID_CUT, wx.ID_COPY, wx.ID_PASTE, wx.ID_DELETE), None,
		(wx.ID_REFRESH,), None, (wx.ID_ZOOM_IN, wx.ID_ZOOM_OUT,
		pdids.ID_ZOOM_PAGE, wx.ID_ZOOM_100, wx.ID_ZOOM_FIT), None,
		(wx.ID_PROPERTIES, wx.ID_PREFERENCES)]

class ToolbarCreator:

	def __init__(self, mw):
		self.mw = mw
		self.build_toolbar()

	def build_toolbar(self):
		self.tb = self.mw.CreateToolBar(TBFLAGS)
		icon_size = config.toolbar_icon_size
		self.tb.SetToolBitmapSize(config.toolbar_size)

		if const.is_mac():
			for items in BUTTONS:
				if not items is None:
					if len(items) == 1:
						action = self.mw.app.actions[items[0]]
						button = MacTB_ActionButton(self.tb, action)
					else:
						actions = []
						for item in items:
							actions.append(self.mw.app.actions[item])
						button = MacTB_ActionNestedButtons(self.tb, actions)
					self.tb.AddControl(button)
		else:
			for items in BUTTONS:
				if items is None: self.tb.AddSeparator()
				else:
					for item in items:
						action = self.mw.app.actions[item]
						aid = action.action_id
						label_txt = action.get_tooltip_text()
						hlp_txt = action.get_descr_text()
						bmp = action.get_icon(icon_size, wx.ART_TOOLBAR)
						if not bmp: continue
						self.tb.AddLabelTool(aid, label_txt, bmp,
											shortHelp=hlp_txt)
						action.register_as_tool(self.tb)
		self.tb.Realize()

	def repeat_test(self, *args):print 'event'
