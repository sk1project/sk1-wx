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

from uc2.uc2const import IMAGE_NAMES, IMAGE_CMYK, IMAGE_RGB

from sk1 import _, config, events, modes
from sk1.resources import pdids, get_tooltip_text
from sk1.pwidgets import SB_FillSwatch, SB_StrokeSwatch, ActionImageSwitch
from sk1.resources import get_bmp, icons


FONTSIZE = [str(config.statusbar_fontsize), ]

class AppStatusbar(wal.HPanel):

	mw = None
	mouse_info = None
	page_info = None
	info = None
	panel2 = None
	clr_monitor = None

	def __init__(self, mw):

		if not config.statusbar_fontsize:
			FONTSIZE[0] = wal.get_system_fontsize()

		self.mw = mw
		wal.HPanel.__init__(self, mw)
		self.pack((5, 20))

		self.mouse_info = MouseMonitor(self.mw.app, self)
		self.pack(self.mouse_info)
		self.mouse_info.hide()

		self.snap_monitor = SnapMonitor(self.mw.app, self)
		self.pack(self.snap_monitor)

		self.page_info = PageMonitor(self.mw.app, self)
		self.pack(self.page_info)
		self.page_info.hide()

		info_panel = wal.HPanel(self)
		info_panel.pack(get_bmp(info_panel, icons.PD_APP_STATUS))
		info_panel.pack((5, 3))
		self.info = wal.Label(info_panel, text='', fontsize=FONTSIZE[0])
		info_panel.pack(self.info)
		self.pack(info_panel, expand=True)


		self.clr_monitor = ColorMonitor(self.mw.app, self)
		self.pack(self.clr_monitor)
		self.clr_monitor.hide()
		events.connect(events.APP_STATUS, self._on_event)

	def _on_event(self, *args):
		self.info.set_text(args[0])
		self.Layout()
		self.show()

class SnapMonitor(wal.HPanel):

	def __init__(self, app, parent):
		self.app = app
		actions = app.actions
		wal.HPanel.__init__(self, parent)

		action_id = pdids.ID_SNAP_TO_GRID
		tooltip_txt = get_tooltip_text(action_id)
		icons_dict = {
			True:[icons.PD_SNAP_TO_GRID_ON, tooltip_txt],
			False:[icons.PD_SNAP_TO_GRID_OFF, tooltip_txt]}
		sw = ActionImageSwitch(self, actions[action_id], icons_dict)
		self.pack(sw, padding=2)

		action_id = pdids.ID_SNAP_TO_GUIDE
		tooltip_txt = get_tooltip_text(action_id)
		icons_dict = {
			True:[icons.PD_SNAP_TO_GUIDE_ON, tooltip_txt],
			False:[icons.PD_SNAP_TO_GUIDE_OFF, tooltip_txt]}
		sw = ActionImageSwitch(self, actions[action_id], icons_dict)
		self.pack(sw, padding=2)

		action_id = pdids.ID_SNAP_TO_OBJ
		tooltip_txt = get_tooltip_text(action_id)
		icons_dict = {
			True:[icons.PD_SNAP_TO_OBJ_ON, tooltip_txt],
			False:[icons.PD_SNAP_TO_OBJ_OFF, tooltip_txt]}
		sw = ActionImageSwitch(self, actions[action_id], icons_dict)
		self.pack(sw, padding=2)

		action_id = pdids.ID_SNAP_TO_PAGE
		tooltip_txt = get_tooltip_text(action_id)
		icons_dict = {
			True:[icons.PD_SNAP_TO_PAGE_ON, tooltip_txt],
			False:[icons.PD_SNAP_TO_PAGE_OFF, tooltip_txt]}
		sw = ActionImageSwitch(self, actions[action_id], icons_dict)
		self.pack(sw, padding=2)

		self.pack(wal.VLine(self.panel), fill=True, padding=2)


class ColorMonitor(wal.HPanel):

	image_txt = None
	fill_txt = None
	fill_swatch = None
	stroke_txt = None
	stroke_swatch = None

	def __init__(self, app, parent):
		self.app = app
		self.parent = parent
		wal.HPanel.__init__(self, parent)

		self.image_txt = wal.Label(self, text=_('Image type: '), fontsize=FONTSIZE[0])
		self.pack(self.image_txt, padding=4)
		self.fill_txt = wal.Label(self, text=_('Fill:'), fontsize=FONTSIZE[0])
		self.pack(self.fill_txt)
		self.fill_swatch = SB_FillSwatch(self, self.app, self.fill_txt,
										onclick=self.app.proxy.fill_dialog)
		self.pack(self.fill_swatch, padding=2)
		self.pack((5, 5))
		self.stroke_txt = wal.Label(self, text=_('Stroke:'), fontsize=FONTSIZE[0])
		self.pack(self.stroke_txt)
		self.stroke_swatch = SB_StrokeSwatch(self, self.app, self.stroke_txt,
										onclick=self.app.proxy.stroke_dialog)
		self.pack(self.stroke_swatch, padding=2)
		self.pack((5, 5))
		self.Layout()
		events.connect(events.SELECTION_CHANGED, self.update)
		events.connect(events.DOC_CHANGED, self.update)
		events.connect(events.NO_DOCS, self.update)

	def update(self, *args):
		sel = self.app.current_doc.get_selected_objs()
		if sel:
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
				self.hide()
				self.show()
				return
		self.hide()

class MouseMonitor(wal.HPanel):

	def __init__(self, app, parent):
		self.app = app
		wal.HPanel.__init__(self, parent)
		self.pack(get_bmp(self.panel, icons.PD_MOUSE_MONITOR))

		width = 100
		if wal.is_mac(): width = 130

		self.pointer_txt = wal.Label(self.panel, text=' ', fontsize=FONTSIZE[0])
		self.pointer_txt.SetMinSize((width, -1))
		self.pack(self.pointer_txt)
		self.pack(wal.VLine(self.panel), fill=True, padding=2)
		events.connect(events.MOUSE_STATUS, self.set_value)
		events.connect(events.NO_DOCS, self.hide_monitor)
		events.connect(events.DOC_CHANGED, self.doc_changed)

	def clear(self):
		self.pointer_txt.set_text(' ' + _('No coords'))

	def hide_monitor(self, *args):
		self.hide()
		self.clear()

	def set_value(self, *args):
		self.pointer_txt.set_text(args[0])

	def doc_changed(self, *args):
		self.clear()
		if not self.is_shown():
			self.show()

class PageMonitor(wal.HPanel):

	def __init__(self, app, parent):
		self.app = app
		self.parent = parent
		wal.HPanel.__init__(self, parent)

		native = False
		if wal.is_gtk(): native = True

		callback = self.app.proxy.goto_start
		self.start_but = wal.ImageButton(self.panel,
							icons.PD_PM_ARROW_START,
							tooltip=_('Go to fist page'),
							decoration_padding=4,
							native=native,
							onclick=callback)
		self.pack(self.start_but)

		callback = self.app.proxy.previous_page
		self.prev_but = wal.ImageButton(self.panel,
							icons.PD_PM_ARROW_LEFT,
							tooltip=_('Go to previous page'),
							decoration_padding=4,
							native=native,
							onclick=callback)
		self.pack(self.prev_but)

		self.page_txt = wal.Label(self.panel, text=' ', fontsize=FONTSIZE[0])
		self.pack(self.page_txt)

		callback = self.app.proxy.next_page
		self.next_but = wal.ImageButton(self.panel,
							icons.PD_PM_ARROW_RIGHT,
							tooltip=_('Go to next page'),
							decoration_padding=4,
							native=native,
							onclick=callback)
		self.pack(self.next_but)

		callback = self.app.proxy.goto_end
		self.end_but = wal.ImageButton(self.panel,
							icons.PD_PM_ARROW_END,
							tooltip=_('Go to last page'),
							decoration_padding=4,
							native=native,
							onclick=callback)
		self.pack(self.end_but)


		self.pack(wal.VLine(self.panel), fill=True, padding=4)
		events.connect(events.NO_DOCS, self.hide_monitor)
		events.connect(events.DOC_CHANGED, self.update)
		events.connect(events.DOC_MODIFIED, self.update)
		events.connect(events.PAGE_CHANGED, self.update)

	def stub(self, *args):pass

	def update(self, *args):
		if self.app.current_doc:
			presenter = self.app.current_doc
			pages = presenter.get_pages()
			if len(pages) == 1:
				self.hide()
				return
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
			self.show()

	def hide_monitor(self, *args):
		self.hide()





