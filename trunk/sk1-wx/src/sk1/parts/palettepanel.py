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

from sk1 import _
from sk1.pwidgets import Palette
from sk1.resources import icons

class AppHPalette(wal.HPanel):

	left_but = None
	no_color = None
	palette = None
	right_but = None

	def __init__(self, parent, app):
		self.app = app
		wal.HPanel.__init__(self, parent)
		self.pack((1, 1))

		self.palette = Palette(self.panel, self.app,
							on_left_click=self.app.proxy.fill_selected,
							on_right_click=self.app.proxy.stroke_selected,
							onmin=self.left_enable,
							onmax=self.right_enable)

		native = False
		if wal.is_gtk(): native = True

		tip = _('Scroll palette to left')
		self.left_but = wal.ImageButton(self.panel, icons.ARROW_LEFT,
								tooltip=tip, decoration_padding=4, native=native,
								onclick=self.palette.scroll_start, repeat=True)
		self.pack(self.left_but)

		tip = _('Empty pattern')
		self.no_color = wal.ImageLabel(self.panel, icons.NO_COLOR, tooltip=tip,
								 onclick=self.set_no_fill,
								 onrightclick=self.set_no_stroke)
		self.pack(self.no_color)

		self.pack(self.palette, expand=True, padding=1)

		tip = _('Scroll palette to right')
		self.right_but = wal.ImageButton(self.panel, icons.ARROW_RIGHT,
								tooltip=tip, decoration_padding=4, native=native,
								onclick=self.palette.scroll_end, repeat=True)
		self.pack(self.right_but)

	def set_no_fill(self): self.app.proxy.fill_selected([])
	def set_no_stroke(self): self.app.proxy.stroke_selected([])

	def set_fill(self, color):
		print color

	def set_stroke(self, color):
		print color

	def left_enable(self, value):
		if not value == self.left_but.get_enabled():
			self.left_but.set_enable(value)

	def right_enable(self, value):
		if not value == self.right_but.get_enabled():
			self.right_but.set_enable(value)

class AppVPalette(wal.VPanel):

	left_but = None
	no_color = None
	palette = None
	right_but = None

	def __init__(self, parent, app):
		self.app = app
		wal.VPanel.__init__(self, parent)
		self.pack((1, 1))


		self.palette = Palette(self.panel, self.app, hpal=False,
							on_left_click=self.app.proxy.fill_selected,
							on_right_click=self.app.proxy.stroke_selected,
							onmin=self.left_enable,
							onmax=self.right_enable)

		native = False
		if wal.is_gtk(): native = True

		tip = _('Scroll palette to top')
		self.left_but = wal.ImageButton(self.panel, icons.ARROW_TOP, tooltip=tip,
								decoration_padding=4, native=native,
								onclick=self.palette.scroll_start, repeat=True)
		self.pack(self.left_but)

		tip = _('Empty pattern')
		self.no_color = wal.ImageLabel(self.panel, icons.NO_COLOR, tooltip=tip,
								 onclick=self.set_no_fill,
								 onrightclick=self.set_no_stroke)

		self.pack(self.no_color)

		self.pack(self.palette, expand=True, padding=1)

		tip = _('Scroll palette to bottom')
		self.right_but = wal.ImageButton(self.panel, icons.ARROW_BOTTOM, tooltip=tip,
								decoration_padding=4, native=native,
								onclick=self.palette.scroll_end, repeat=True)
		self.pack(self.right_but)


	def set_no_fill(self): self.app.proxy.fill_selected([])
	def set_no_stroke(self): self.app.proxy.stroke_selected([])

	def set_fill(self, color):
		print color

	def set_stroke(self, color):
		print color

	def left_enable(self, value):
		if not value == self.left_but.get_enabled():
			self.left_but.set_enable(value)

	def right_enable(self, value):
		if not value == self.right_but.get_enabled():
			self.right_but.set_enable(value)
