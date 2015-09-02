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

from sk1.resources import pdids
from sk1.pwidgets import StyleMonitor

BUTTONS = (pdids.SELECT_MODE, pdids.SHAPER_MODE, pdids.ZOOM_MODE,
		pdids.FLEUR_MODE, pdids.LINE_MODE, pdids.CURVE_MODE, pdids.RECT_MODE,
		pdids. ELLIPSE_MODE, pdids.POLYGON_MODE, pdids.TEXT_MODE,
		pdids.GRADIENT_MODE, None, pdids.FILL_MODE, pdids.STROKE_MODE, None)

class AppTools(wal.VPanel):

	buttons = []

	def __init__(self, app, parent):
		self.app = app
		self.buttons = []
		wal.VPanel.__init__(self, parent)
		self.pack((5, 5))
		for item in BUTTONS:
			if item is None: self.pack(wal.HLine(self.panel), fill=True)
			else:
				action = self.app.actions[item]
				if action.is_toggle():
					but = ActionTool(self.panel, action)
				else:
					but = ActionToolButton(self.panel, action)
				self.buttons.append(but)
				self.pack(but, padding=1)
		self.pack((15, 15))
		self.pack(StyleMonitor(self, self.app))

class ActionTool(wal.ImageToggleButton):

	def __init__(self, parent, action):
		self.action = action
		value = False
		art_id = action.get_artid()
		art_size = wal.DEF_SIZE
		text = ''
		tooltip = action.get_tooltip_text()
		padding = 0
		decoration_padding = 4

		if wal.is_msw():
			decoration_padding = 2

		wal.ImageToggleButton.__init__(self, parent, value, art_id, art_size,
								text, tooltip, padding, decoration_padding,
								True, onchange=action.do_call)
		self.action.register(self)

	def update(self):
		self.set_enable(self.action.enabled)
		self.set_active(self.action.active)

	def _mouse_up(self, event):
		self.mouse_pressed = False
		if self.mouse_over:
			if self.enabled:
				if self.value:return
				else:self.value = True
				if self.onchange: self.onchange()
		self.refresh()

class ActionToolButton(wal.ImageButton):

	def __init__(self, parent, action):
		self.action = action
		art_id = action.get_artid()
		art_size = wal.DEF_SIZE
		text = ''
		tooltip = action.get_tooltip_text()
		padding = 0
		decoration_padding = 4
		native = True

		if wal.is_msw():
			decoration_padding = 2
			native = False

		wal.ImageButton.__init__(self, parent, art_id, art_size, text, tooltip,
							padding, decoration_padding, True, native,
							onclick=action.do_call)
		self.action.register(self)

	def update(self):
		self.set_enable(self.action.enabled)
