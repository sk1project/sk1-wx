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

from uc2.uc2const import IMAGE_NAMES, IMAGE_CMYK, IMAGE_RGB

from wal import ALL, EXPAND, TOP, LEFT, CENTER, RIGHT, const
from wal import HPanel, Label, VLine, ImageButton

from sk1 import _, config, events
from sk1.pwidgets import FillSwatch, StrokeSwatch
from sk1.resources import get_bmp, icons


FONTSIZE = [str(config.statusbar_fontsize), ]

class AppStatusbar(HPanel):

	mw = None
	panel1 = None
	mouse_info = None
	page_info = None
	info = None
	panel2 = None
	clr_monitor = None

	def __init__(self, mw):

		if not config.statusbar_fontsize:
			font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
			if font.IsUsingSizeInPixels():
				FONTSIZE[0] = str(font.GetPixelSize())
			else:
				FONTSIZE[0] = str(font.GetPointSize())

		self.mw = mw
		HPanel.__init__(self, mw, border=TOP)
		self.add((1, 20))
		panel1 = HPanel(self.panel)
		panel1.add((5, 20))

		self.mouse_info = MouseMonitor(self.mw.app, panel1)
		panel1.add(self.mouse_info, 0, ALL | EXPAND)
		self.mouse_info.hide()

		self.page_info = PageMonitor(self.mw.app, panel1)
		panel1.add(self.page_info, 0, ALL | EXPAND)
		self.page_info.hide()

		panel1.add(get_bmp(panel1.panel, icons.PD_APP_STATUS), 0, LEFT | CENTER)
		panel1.add((5, 3))

		self.info = Label(panel1.panel, text='', fontsize=FONTSIZE[0])
		panel1.add(self.info, 0, LEFT | CENTER)
		self.add(panel1, 1, ALL | EXPAND)

		self.clr_monitor = ColorMonitor(self.mw.app, self.panel)
		self.add(self.clr_monitor, 0, ALL | EXPAND)
		self.clr_monitor.hide()
		events.connect(events.APP_STATUS, self._on_event)

	def _on_event(self, *args):
		self.info.set_text(args[0])
		self.Layout()

class ColorMonitor(HPanel):

	image_txt = None
	fill_txt = None
	fill_swatch = None
	stroke_txt = None
	stroke_swatch = None

	def __init__(self, app, parent):
		self.app = app
		self.parent = parent
		HPanel.__init__(self, parent)

		self.image_txt = Label(self.panel, text=_('Image type: '), fontsize=FONTSIZE[0])
		self.add(self.image_txt, 0, LEFT | CENTER | RIGHT, 4)
		self.fill_txt = Label(self.panel, text=_('Fill:'), fontsize=FONTSIZE[0])
		self.add(self.fill_txt, 0, LEFT | CENTER)
		self.fill_swatch = FillSwatch(self.panel, self.app, self.fill_txt)
		self.add(self.fill_swatch, 0, LEFT | CENTER, 2)
		self.stroke_txt = Label(self.panel, text=_('Stroke:'), fontsize=FONTSIZE[0])
		self.add(self.stroke_txt, 0, LEFT | CENTER, 10)
		self.stroke_swatch = StrokeSwatch(self.panel, self.app, self.stroke_txt)
		self.add(self.stroke_swatch, 0, LEFT | CENTER, 2)
		self.add((5, 5))
		events.connect(events.SELECTION_CHANGED, self.update)
		events.connect(events.DOC_CHANGED, self.update)
		events.connect(events.NO_DOCS, self.update)

	def update(self, *args):
		if self.app.insp.is_selection():
			sel = self.app.current_doc.selection.objs
			if len(sel) == 1 and self.app.insp.is_obj_primitive(sel[0]):
				self.fill_swatch.update_from_obj(sel[0])
				self.stroke_swatch.update_from_obj(sel[0])
				if self.app.insp.is_obj_pixmap(sel[0]):
					txt = _('Image type: ') + IMAGE_NAMES[sel[0].colorspace]
					if sel[0].alpha_channel:
						if sel[0].colorspace in [IMAGE_CMYK, IMAGE_RGB]:
							txt += 'A'
						else:
							txt += '+A'
					self.image_txt.set_text(txt)
					self.image_txt.show()
				else:
					self.image_txt.hide()
				self.show(True)
				return
		self.hide(True)

class MouseMonitor(HPanel):

	def __init__(self, app, parent):
		self.app = app
		HPanel.__init__(self, parent)
		self.add(get_bmp(self.panel, icons.PD_MOUSE_MONITOR), 0, LEFT | CENTER)

		width = 100
		if const.is_mac():
			width = 130

		self.pointer_txt = Label(self.panel, text=' ', fontsize=FONTSIZE[0])
		self.pointer_txt.SetMinSize((width, -1))
		self.add(self.pointer_txt, 0, LEFT | CENTER)
		self.add(VLine(self.panel), 0, ALL | EXPAND, 2)
		events.connect(events.MOUSE_STATUS, self.set_value)
		events.connect(events.NO_DOCS, self.hide_monitor)
		events.connect(events.DOC_CHANGED, self.doc_changed)

	def clear(self):
		self.pointer_txt.set_text(' No coords')

	def hide_monitor(self, *args):
		self.hide(True)
		self.clear()

	def set_value(self, *args):
		self.pointer_txt.set_text(args[0])

	def doc_changed(self, *args):
		self.clear()
		if not self.is_shown():
			self.show(True)

class PageMonitor(HPanel):

	def __init__(self, app, parent):
		self.app = app
		self.parent = parent
		HPanel.__init__(self, parent)

		native = False
		if const.is_gtk(): native = True

		callback = self.app.proxy.goto_start
		self.start_but = ImageButton(self.panel,
							icons.PD_PM_ARROW_START,
							tooltip=_('Go to fist page'),
							decoration_padding=4,
							native=native,
							onclick=callback)
		self.add(self.start_but, 0, LEFT | CENTER)

		callback = self.app.proxy.previous_page
		self.prev_but = ImageButton(self.panel,
							icons.PD_PM_ARROW_LEFT,
							tooltip=_('Go to previous page'),
							decoration_padding=4,
							native=native,
							onclick=callback)
		self.add(self.prev_but, 0, LEFT | CENTER)

		self.page_txt = Label(self.panel, text=' ', fontsize=FONTSIZE[0])
		self.add(self.page_txt, 0, LEFT | CENTER)

		callback = self.app.proxy.next_page
		self.next_but = ImageButton(self.panel,
							icons.PD_PM_ARROW_RIGHT,
							tooltip=_('Go to next page'),
							decoration_padding=4,
							native=native,
							onclick=callback)
		self.add(self.next_but, 0, LEFT | CENTER)

		callback = self.app.proxy.goto_end
		self.end_but = ImageButton(self.panel,
							icons.PD_PM_ARROW_END,
							tooltip=_('Go to last page'),
							decoration_padding=4,
							native=native,
							onclick=callback)
		self.add(self.end_but, 0, LEFT | CENTER)


		self.add(VLine(self.panel), 0, ALL | EXPAND, 4)
		events.connect(events.NO_DOCS, self.hide_monitor)
		events.connect(events.DOC_CHANGED, self.update)
		events.connect(events.DOC_MODIFIED, self.update)
		events.connect(events.PAGE_CHANGED, self.update)

	def stub(self, *args):pass

	def update(self, *args):
		if self.app.current_doc:
			presenter = self.app.current_doc
			pages = presenter.get_pages()
			current_index = pages.index(presenter.active_page)

			if current_index:
				self.start_but.set_enable(True)
				self.prev_but.set_enable(True)
			else:
				self.start_but.set_enable(False)
				self.prev_but.set_enable(False)

			if current_index == len(pages) - 1:
				self.end_but.set_enable(False)
			else:
				self.end_but.set_enable(True)

			text = _(" Page %i of %i ") % (current_index + 1, len(pages))
			self.page_txt.set_text(text)
			self.show(True)

	def hide_monitor(self, *args):
		self.hide(True)





