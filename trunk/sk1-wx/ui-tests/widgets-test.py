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

from wal import BOTTOM, CENTER, LEFT, ALL, EXPAND
from wal import Application, MainWindow, Notebook, VLine
from wal import HPanel, VPanel, Label, HLine, HtmlLabel, Button
from wal import Checkbox, Radiobutton, Combolist, Combobox, Entry
from wal import Spin, FloatSpin, Slider, LabeledPanel

class WidgetPanel(VPanel):

	name = 'Basic widgets'
	spin = None

	def __init__(self, parent):
		VPanel.__init__(self, parent)
		self.build()

	def test(self, *args):
		print 'Callback is successful!'

	def test_spin(self, *args):
		print 'result>>', self.spin.get_value()

	def build(self):
		flags = LEFT | CENTER
		pflags = ALL | EXPAND
		#---------Labels
		p = HPanel(self, border=BOTTOM, space=2)
		props = [
			('Normal font', False, 0),
			('Bold font', True, 0),
			('-1 font', False, -1),
			('+1 font', False, 1),
			('+2 font', False, 2),
			('+2 bold font', True, 2),
			('+2 red bold font', True, 2, (255, 0, 0)),
			]
		for item in props:
			p.add(Label(p, *item), 0, flags, 5)

		self.add(p, 0, pflags)

		#---------HtmlLabels
		p = HPanel(self, border=BOTTOM, space=2)

		p.add(HtmlLabel(p, 'http://junona.org'), 0, flags, 5)
		p.add(HtmlLabel(p, 'Download site', 'http://sk1project.org'), 0, flags, 5)

		self.add(p, 0, pflags)

		#---------Buttons
		p = HPanel(self, border=BOTTOM, space=2)

		p.add(Button(p, 'Native button'), 0, flags, 5)
		txt = 'Native default button'
		p.add(Button(p, 'Native default button', default=True, tooltip=txt), 0, flags, 5)
		p.add(Button(p, 'Native button with callback', onclick=self.test), 0, flags, 5)

		self.add(p, 0, pflags)

		#---------Checkboxes
		p = HPanel(self, border=BOTTOM, space=2)

		p.add(Checkbox(p, 'Native checkbox'), 0, flags, 5)
		p.add(Checkbox(p, 'Native checkbox (checked)', True), 0, flags, 5)
		p.add(Checkbox(p, 'Checkbox with callback', onclick=self.test), 0, flags, 5)
		self.add(p, 0, pflags)

		#---------Radiobuttons
		p = HPanel(self, border=BOTTOM, space=2)

		p.add(Radiobutton(p.panel, 'Native radiobutton', group=True), 0, flags, 5)
		p.add(Radiobutton(p.panel, 'Native radiobutton (selected)'), 0, flags, 5)
		p.add(Radiobutton(p.panel, 'Radiobutton with callback', onclick=self.test), 0, flags, 5)

		self.add(p, 0, pflags)

		#---------Combolist
		p = HPanel(self, border=BOTTOM, space=2)

		sample = ['zero', 'one', 'two', 'three', 'four five', 'six seven eight']
		p.add(Label(p, 'Native combolist:'), 0, flags, 5)
		p.add(Combolist(p, items=sample), 0, flags, 5)
		p.add(Label(p, 'Native combolist with callback:'), 0, flags, 5)
		p.add(Combolist(p, items=sample, onchange=self.test), 0, flags, 5)

		self.add(p, 0, pflags)

		#---------Combobox
		p = HPanel(self, border=BOTTOM, space=2)

		sample = ['zero', 'one', 'two', 'three', 'four five', 'six seven eight']
		p.add(Label(p, 'Native combobox:'), 0, flags, 5)
		p.add(Combobox(p, 'value', items=sample), 0, flags, 5)
		p.add(Label(p, 'Native combobox with callback:'), 0, flags, 5)
		p.add(Combobox(p, items=sample, width=15, onchange=self.test), 0, flags, 5)

		self.add(p, 0, pflags)

		#---------Text entry
		p = HPanel(self, border=BOTTOM, space=2)

		p.add(Label(p, 'Native text entry:'), 0, flags, 5)
		p.add(Entry(p, 'value', width=5), 0, flags, 5)
		p.add(Label(p, 'Native text entry with callback:'), 0, flags, 5)
		p.add(Entry(p, 'value', onchange=self.test), 0, flags, 5)

		self.add(p, 0, pflags)

		#---------Multiline Text entry
		p = HPanel(self, border=BOTTOM, space=2)

		p.add(Label(p, 'Multiline text entry:'), 0, flags, 5)
		p.add(Entry(p, 'value', size=(150, 50), multiline=True), 0, flags, 5)
		p.add(Label(p, 'Multiline text entry with callback:'), 0, flags, 5)
		p.add(Entry(p, 'value', size=(150, 50), multiline=True,
				onchange=self.test), 0, flags, 5)

		self.add(p, 0, pflags)

		#---------Spin
		p = HPanel(self, border=BOTTOM, space=2)

		p.add(Label(p, 'Native spin control:'), 0, flags, 5)
		p.add(Spin(p, 1, (0, 90), onchange=self.test), 0, flags, 5)
		p.add(Label(p, 'Float spin control:'), 0, flags, 5)
		self.spin = FloatSpin(p.panel, 1.3, (0.0, 90.0), 0.01, 3, width=5,
					onchange=self.test)
		p.add(self.spin, 0, flags, 5)
		p.add(Button(p, 'Get value', onclick=self.test_spin), 0, flags, 5)

		self.add(p, 0, pflags)

		#---------Slider
		p = HPanel(self, border=BOTTOM, space=2)

		p.add(Label(p, 'Native slider:'), 0, flags, 5)
		p.add(Slider(p.panel, 25, (0, 255), onchange=self.test), 0, flags, 5)

		self.add(p, 0, pflags)

		#---------Labeled panel
		p = HPanel(self)

		panel = LabeledPanel(p, 'The panel')
		panel.add((0, 50), 0, flags, 0)
		panel.add(Label(p, 'Native Labeled Panel'), 0, flags, 0)
		p.box_add(panel.box, 0, flags, 5)


		panel = LabeledPanel(p)
		panel.add((0, 50), 0, flags, 0)
		panel.add(Label(p, 'Headless Labeled Panel'), 0, flags, 0)
		p.box_add(panel.box, 0, flags, 5)

		p.add(VLine(p), 0, ALL | EXPAND, 3)

		nb = Notebook(p)
		page = VPanel(nb)
		page.add((50, 100))
		nb.add_page(page, 'First page')
		page = VPanel(nb)
		page.add((50, 100))
		nb.add_page(page, 'Second page')
		p.add(nb, 1, ALL | EXPAND, 3)

		self.add(p, 0, pflags)


app = Application('wxWidgets')
mw = MainWindow('Basic widgets', (700, 550))
p = VPanel(mw)
mw.add(p, 1, ALL | EXPAND)
panel = WidgetPanel(mw)
p.add(panel, 1, ALL | EXPAND, 10)
app.mw = mw
app.run()
