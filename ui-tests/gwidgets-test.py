#! /usr/bin/python
#
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

from sk1 import init_config
#from sk1.pwidgets.mactoolbar import MacTB_ActionNestedButtons
init_config()
from wal import const
from sk1.parts.artprovider import create_artprovider
from wal import BOTTOM, CENTER, LEFT, ALL, EXPAND, TOP
from wal import Application, MainWindow, VPanel, HPanel, Button, Label

from wal import ImageLabel, ImageButton, ImageToggleButton
from sk1.pwidgets import MacTB_ActionButton, AppAction, MacTB_ActionNestedButtons

class WidgetPanel(VPanel):

	name = 'Graphics widgets'
	spin = None
	count = 0

	def __init__(self, parent):
		VPanel.__init__(self, parent)
		create_artprovider()
		self.build()

	def test(self, *args):
		print 'Callback is successful!'

	def repeat_test(self, *args):
		print 'Repeat call>>>', self.count
		self.count += 1

	def test_ilab1(self, event):
		if self.ilab1.get_enabled():
			self.ilab1.set_enabled(False)
		else:
			self.ilab1.set_enabled(True)

	def build(self):
		flags = LEFT | CENTER
		pflags = ALL | EXPAND

		#---------
		p = HPanel(self)
		p.add(Label(p, 'Widgets rendered by native rendering',
				fontbold=True, fontsize=2), 0, flags, 5)
		self.add(p, 0, pflags, 10)

		#---------ImageLabels
		p = HPanel(self, border=BOTTOM, space=2)

		p.add(Label(p, 'ImageLabels:'), 0, flags, 5)

		p.add(ImageLabel(p, text='<Image label>', fontbold=True,
			tooltip='this is label', onclick=self.repeat_test), 0, flags, 5)

		p.add(ImageLabel(p, wx.ART_FILE_OPEN, const.SIZE_16, padding=5,
			tooltip='this is label2', onclick=self.repeat_test), 0, flags, 5)

		self.ilab1 = ImageLabel(p, wx.ART_COPY, const.SIZE_16, padding=5,
			tooltip='this is label3', text='Copy', onclick=self.repeat_test)
		p.add(self.ilab1)

		il = ImageLabel(p, text='<Image label disabled>', fontbold=True,
			tooltip='this is disabled label', onclick=self.repeat_test)
		il.set_enable(False)
		p.add(il, 0, flags, 5)

		b = Button(p, 'Change', onclick=self.test_ilab1)
		p.add(b, 0, flags, 5)

		self.add(p, 0, pflags)

		#---------ImageButtons
		p = HPanel(self, border=BOTTOM, space=2)
		p.add(Label(p, 'ImageButtons:'), 0, flags, 5)

		p.add(ImageButton(p, text='<Image button>', flat=False, fontbold=True,
				tooltip='this is button', onclick=self.repeat_test), 0, flags, 5)

		p.add(ImageButton(p, wx.ART_FILE_OPEN, const.SIZE_32,
			tooltip='this is button2', onclick=self.repeat_test), 0, flags, 5)

		p.add(ImageButton(p, wx.ART_COPY, const.SIZE_16,
			tooltip='this is label3', text='Clipboard',
			onclick=self.repeat_test), 0, flags, 5)

		ib = ImageButton(p, wx.ART_COPY, const.SIZE_16,
			tooltip='this is label3', text='Clipboard',
			onclick=self.repeat_test)
		ib.set_enable(False)
		p.add(ib, 0, flags, 5)

		self.add(p, 0, pflags)

		#---------ImageToggleButtons
		p = HPanel(self, border=BOTTOM, space=2)
		p.add(Label(p, 'ImageToggleButtons:'), 0, flags, 5)

		p.add(ImageToggleButton(p, text='<Image toggle button>', fontbold=True,
				tooltip='this is button', onchange=self.repeat_test), 0, flags, 5)

		p.add(ImageToggleButton(p, False, wx.ART_FILE_OPEN, const.SIZE_32,
			tooltip='this is button2', onchange=self.repeat_test), 0, flags, 5)

		p.add(ImageToggleButton(p, True, wx.ART_COPY, const.SIZE_16,
			tooltip='this is label3', text='Clipboard',
			onchange=self.repeat_test), 0, flags, 5)

		itb = ImageToggleButton(p, True, wx.ART_FILE_OPEN, const.SIZE_24,
			tooltip='this is label4, disabled', text='Clipboard',
			onchange=self.repeat_test)
		itb.set_enable(False)
		p.add(itb, 0, flags, 5)

		self.add(p, 0, pflags)

		#---------
		p = HPanel(self)
		p.add(Label(p, 'Widgets rendered by generic rendering',
				fontbold=True, fontsize=2), 0, flags, 5)
		self.add(p, 0, pflags, 10)

		#---------Generic ImageButtons
		p = HPanel(self, border=BOTTOM, space=2)
		p.add(Label(p, 'ImageButtons:'), 0, flags, 5)

		p.add(ImageButton(p, text='<Image button>', flat=False, fontbold=True,
				tooltip='this is button', native=False,
				onclick=self.repeat_test), 0, flags, 5)

		p.add(ImageButton(p, wx.ART_FILE_OPEN, const.SIZE_32,
			tooltip='this is button2', native=False,
			onclick=self.repeat_test), 0, flags, 5)

		p.add(ImageButton(p, wx.ART_COPY, const.SIZE_16,
			tooltip='this is label3', text='Clipboard', native=False,
			onclick=self.repeat_test), 0, flags, 5)

		ib = ImageButton(p, wx.ART_COPY, const.SIZE_16,
			tooltip='this is label3', text='Clipboard', native=False,
			onclick=self.repeat_test)
		ib.set_enable(False)
		p.add(ib, 0, flags, 5)

		self.add(p, 0, pflags)

		#---------Generic ImageToggleButtons
		p = HPanel(self, border=BOTTOM, space=2)
		p.add(Label(p, 'ImageToggleButtons:'), 0, flags, 5)

		p.add(ImageToggleButton(p, text='<Image toggle button>', fontbold=True,
				tooltip='this is button', native=False,
				onchange=self.repeat_test), 0, flags, 5)

		p.add(ImageToggleButton(p, False, wx.ART_FILE_OPEN, const.SIZE_32,
			tooltip='this is button2', native=False,
			onchange=self.repeat_test), 0, flags, 5)

		p.add(ImageToggleButton(p, True, wx.ART_COPY, const.SIZE_16,
			tooltip='this is label3', text='Clipboard', native=False,
			onchange=self.repeat_test), 0, flags, 5)

		itb = ImageToggleButton(p, True, wx.ART_FILE_OPEN, const.SIZE_24,
			tooltip='this is label4, disabled', text='Clipboard', native=False,
			onchange=self.repeat_test)
		itb.set_enable(False)
		p.add(itb, 0, flags, 5)

		self.add(p, 0, pflags)

		#---------Mac Toolbar Buttons
# 		p = HPanel(self, border=BOTTOM, space=2)
# 		p.add(Label(p, 'Mac Toolbar Buttons:'), 0, flags, 5)
#
# 		p.add(MacTB_ActionButton(p, AppAction(wx.ID_NEW, self.repeat_test)),
# 			 0, flags, 5)
#
# 		action = AppAction(wx.ID_NEW, self.repeat_test)
# 		action.set_enable(False)
# 		p.add(MacTB_ActionButton(p, action), 0, flags, 5)
# 		action.update()
#
# 		actions = [AppAction(wx.ID_NEW, self.repeat_test),
# 				AppAction(wx.ID_NEW, self.repeat_test),
# 				AppAction(wx.ID_NEW, self.repeat_test)]
# 		p.add(MacTB_ActionNestedButtons(p, actions), 0, flags, 5)
# 		index = 0
# 		for action in actions:
# 			if index == 1:action.set_enable(False)
# 			action.update()
# 			index += 1
#
# 		self.add(p, 0, pflags)

app = Application('Graphics widgets')
mw = MainWindow(app.app_name, (700, 500))
p = VPanel(mw)
mw.add(p, 1, ALL | EXPAND)
panel = WidgetPanel(mw)
p.add(panel, 1, ALL | EXPAND, 10)
app.mw = mw
app.run()
