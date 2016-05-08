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

import wal

from sk1 import config
from sk1.resources import pdids
from sk1.pwidgets import MacTB_ActionButton, MacTB_ActionNestedButtons


BUTTONS = [(wal.ID_NEW,), None, (wal.ID_OPEN, wal.ID_SAVE, wal.ID_SAVEAS,
		wal.ID_CLOSE), None, (wal.ID_PRINT,), None, (wal.ID_UNDO, wal.ID_REDO),
		None, (wal.ID_CUT, wal.ID_COPY, wal.ID_PASTE, wal.ID_DELETE), None,
		(wal.ID_REFRESH,), None, (wal.ID_ZOOM_IN, wal.ID_ZOOM_OUT,
		pdids.ID_ZOOM_PAGE, wal.ID_ZOOM_100, wal.ID_ZOOM_FIT), None,
		(wal.ID_PROPERTIES, wal.ID_PREFERENCES)]

class ToolbarCreator:

	def __init__(self, mw):
		self.mw = mw
		self.build_toolbar()

	def build_toolbar(self):
		self.tb = self.mw.CreateToolBar(wal.TBFLAGS)
		icon_size = config.toolbar_icon_size
		self.tb.SetToolBitmapSize(config.toolbar_size)
# 		if wal.is_win7():
# 			self.tb.SetBackgroundColour('#D3DAED')

		if wal.is_mac():
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
						bmp = action.get_icon(icon_size, wal.ART_TOOLBAR)
						if not bmp: continue
						if wal.is_msw():
							self.tb.AddLabelTool(aid, label_txt, bmp,
												bmpDisabled=wal.disabled_bmp(bmp),
												shortHelp=hlp_txt)
						else:
							self.tb.AddLabelTool(aid, label_txt, bmp,
												shortHelp=hlp_txt)
						action.register_as_tool(self.tb)
		self.tb.Realize()

