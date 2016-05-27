# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2016 by Igor E. Novikov
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


import os, wal

from uc2.formats.sk2 import sk2_const

from sk1 import _, events
from sk1.app_plugins import RS_Plugin
from sk1.resources import get_icon, icons, get_bmp

PLG_DIR = __path__[0]
IMG_DIR = os.path.join(PLG_DIR, 'images')

def make_artid(name):
	return os.path.join(IMG_DIR, name + '.png')

def get_plugin(app):
	return TP_Plugin(app)

PLUGIN_ICON = make_artid('icon')

TEXT_ALIGNS = [sk2_const.TEXT_ALIGN_LEFT, sk2_const.TEXT_ALIGN_CENTER,
			sk2_const.TEXT_ALIGN_RIGHT, sk2_const.TEXT_ALIGN_JUSTIFY]

TEXT_ALIGN_ICONS = {
sk2_const.TEXT_ALIGN_LEFT:icons.PD_ALIGN_LEFT,
sk2_const.TEXT_ALIGN_CENTER:icons.PD_ALIGN_CENTER,
sk2_const.TEXT_ALIGN_RIGHT:icons.PD_ALIGN_RIGHT,
sk2_const.TEXT_ALIGN_JUSTIFY:icons.PD_ALIGN_JUSTIFY,
}

TEXT_ALIGN_TEXTS = {
sk2_const.TEXT_ALIGN_LEFT:_('Align to path start'),
sk2_const.TEXT_ALIGN_CENTER:_('Align to path center'),
sk2_const.TEXT_ALIGN_RIGHT:_('Align to path end'),
sk2_const.TEXT_ALIGN_JUSTIFY:_('Stretch along path'),
}

TEXT_ALIGN_PICS = {
sk2_const.TEXT_ALIGN_LEFT:make_artid('pos-start'),
}

class TP_Plugin(RS_Plugin):

	pid = 'TextOnPathPlugin'
	name = _('Text on Path')
	active_transform = None
	transforms = {}

	def build_ui(self):
		self.icon = get_icon(PLUGIN_ICON)
		panel = wal.VPanel(self.panel)

		panel.pack(wal.Label(panel, _('Text position on path')), padding_all=5)

		hp = wal.HPanel(panel)
		hp.pack(wal.Label(hp, _('Base point:')))
		self.base_point = wal.FloatSpin(hp, value=50.0, range_val=(0.0, 100.0),
									step=1.0)
		hp.pack(self.base_point, padding=5)
		hp.pack(wal.Label(hp, _('%')))

		panel.pack(hp, padding=5)

		self.align_keeper = wal.HToggleKeeper(panel, TEXT_ALIGNS,
							TEXT_ALIGN_ICONS,
							TEXT_ALIGN_TEXTS)
		panel.pack(self.align_keeper)
		self.align_keeper.set_mode(TEXT_ALIGNS[1])

		border = wal.VPanel(panel)
		color = wal.GRAY
		if wal.is_gtk():color = wal.UI_COLORS['pressed_border']
		border.set_bg(color)
		self.pic_panel = wal.VPanel(border)
		self.pic_panel.set_bg(wal.WHITE)
		self.bmp = get_bmp(self.pic_panel,
						TEXT_ALIGN_PICS[sk2_const.TEXT_ALIGN_LEFT])
		self.pic_panel.pack(self.bmp, padding_all=5)
		border.pack(self.pic_panel, padding_all=1)
		panel.pack(border, padding=10)

		self.other_side = wal.Checkbox(panel, _('Place on other side'))
		panel.pack(self.other_side, padding=5)

		self.apply_btn = wal.Button(panel, _('Apply'), onclick=self.action)
		panel.pack(self.apply_btn, padding=5, fill=True)

		self.panel.pack(panel, fill=True, padding_all=5)
		self.panel.pack(wal.HLine(self.panel), fill=True)

		events.connect(events.DOC_CHANGED, self.update)
		events.connect(events.SELECTION_CHANGED, self.update)
		events.connect(events.DOC_MODIFIED, self.update)

		self.update()

	def show_signal(self, *args):self.update()

	def set_state(self, state):
		self.apply_btn.set_enable(state)
		self.align_keeper.set_enable(state)
		self.base_point.set_enable(state)
		self.bmp.set_enable(state)
		self.other_side.set_enable(state)

	def is_path(self, obj):
		return obj.is_primitive() and not obj.is_text() and not obj.is_pixmap()

	def check_selection(self):
		doc = self.app.current_doc
		if len(doc.selection.objs) == 1 and doc.selection.objs[0].is_tpgroup():
			return 1
		elif len(doc.selection.objs) == 2:
			obj1 = doc.selection.objs[0]
			obj2 = doc.selection.objs[1]
			if self.is_path(obj1) and obj2.is_text(): return 2
			elif self.is_path(obj2) and obj1.is_text(): return 2
			elif obj1.is_tpgroup() and obj2.is_text(): return 2
			elif obj2.is_tpgroup() and obj1.is_text(): return 2
		return False

	def update(self, *args):
		if not self.is_shown(): return
		state = False
		if self.app.insp.is_selection():
			ret = self.check_selection()
			if ret: state = True
		self.set_state(state)

	def action(self):pass

