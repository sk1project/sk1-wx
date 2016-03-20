# -*- coding: utf-8 -*-
#
#	Copyright (C) 2016 by Igor E. Novikov
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
from copy import deepcopy

from uc2 import libpango
from uc2.formats.sk2 import sk2_const

from sk1 import _, events
from sk1.resources import icons
from sk1.pwidgets import FontChoice

from generic import CtxPlugin

FONT_SIZES = range(5, 14) + range(14, 30, 2) + [32, 36, 40, 48, 56, 64, 72]

ALIGN_MODES = [sk2_const.TEXT_ALIGN_LEFT,
			sk2_const.TEXT_ALIGN_CENTER,
			sk2_const.TEXT_ALIGN_RIGHT]

ALIGN_MODE_ICONS = {
sk2_const.TEXT_ALIGN_LEFT:icons.PD_ALIGN_LEFT,
sk2_const.TEXT_ALIGN_CENTER:icons.PD_ALIGN_CENTER,
sk2_const.TEXT_ALIGN_RIGHT:icons.PD_ALIGN_RIGHT
}

ALIGN_MODE_NAMES = {
sk2_const.TEXT_ALIGN_LEFT:_('Align Left'),
sk2_const.TEXT_ALIGN_CENTER:_('Centered'),
sk2_const.TEXT_ALIGN_RIGHT:_('Align Right')
}

class TextStylePlugin(CtxPlugin):

	parent = None
	name = 'TextStylePlugin'
	families = []
	faces_dict = {}
	faces = []
	styles = []
	target = None

	def __init__(self, app, parent):
		CtxPlugin.__init__(self, app, parent)
		events.connect(events.DOC_CHANGED, self.update)
		events.connect(events.DOC_MODIFIED, self.update)
		events.connect(events.SELECTION_CHANGED, self.update)

	def build(self):
		self.styles = self._get_styles()
		self.styles_combo = wal.Combolist(self, items=self.styles,
										onchange=self.on_style_change)
		self.add(self.styles_combo, 0, wal.LEFT | wal.CENTER, 2)
		self.add((3, 3))

		self.families, self.faces_dict = libpango.get_fonts()

		self.families_combo = FontChoice(self, onchange=self.on_font_change)
		self.add(self.families_combo, 0, wal.LEFT | wal.CENTER, 2)
		self.add((3, 3))

		self.faces = self.faces_dict['Sans']
		self.faces_combo = wal.Combolist(self, items=self.faces,
										onchange=self.apply_changes)
		self.faces_combo.set_active(0)
		self.add(self.faces_combo, 0, wal.LEFT | wal.CENTER, 2)
		self.add((3, 3))

		self.size_combo = wal.FloatCombobox(self, 12, width=5,
										digits=2, items=FONT_SIZES,
										onchange=self.apply_changes)
		self.add(self.size_combo, 0, wal.LEFT | wal.CENTER, 2)

		self.pack(wal.VLine(self), fill=True, padding_all=3)

		self.align = wal.HToggleKeeper(self, ALIGN_MODES,
								ALIGN_MODE_ICONS, ALIGN_MODE_NAMES,
								on_change=self.apply_changes, allow_none=False)
		self.align.set_mode(sk2_const.TEXT_ALIGN_LEFT)
		self.add(self.align, 0, wal.LEFT | wal.CENTER, 2)

		self.pack(wal.VLine(self), fill=True, padding_all=3)

		self.ligature = wal.ImageToggleButton(self, False, icons.PD_LIGATURE,
						tooltip=_('Use ligatures'), onchange=self.apply_changes)
		self.add(self.ligature, 0, wal.LEFT | wal.CENTER, 2)

	def _get_styles(self):
		ret = []
		if self.app.current_doc:
			model = self.app.current_doc.model
			for item in model.styles.keys():
				if model.styles[item][2]:
					ret.append(item)
		return ret

	def show(self, update):
		CtxPlugin.show(self, update)
		self.update()

	def update(self, *args):
		if not self.is_shown(): return
		if not self.app.current_doc: return
		doc = self.app.current_doc
		sel = doc.selection.objs
		if len(sel) == 1 and sel[0].is_text():
			self.styles_combo.hide(True)
			self.target = sel[0]
			doc = self.app.current_doc
			doc.text_obj_style = deepcopy(self.target.style)
			self.update_from_style(self.target.style[2])
		else:
			self.target = None
			self.update_styles()
			self.styles_combo.show(True)

	def update_styles(self):
		self.styles = self._get_styles()
		self.styles_combo.set_items(self.styles)
		if self.styles:
			self.styles_combo.set_active(self.styles.index('Default Text Style'))
			doc = self.app.current_doc
			doc.text_obj_style = doc.model.get_text_style()
			self.update_from_style(doc.text_obj_style[2])

	def update_from_style(self, text_style):
		family = text_style[0]
		self.families_combo.set_font_family(family)

		face = text_style[1]
		faces = self.faces_dict[family]
		if not face in faces: face = faces[0]
		self.faces = faces
		self.faces_combo.set_items(self.faces)
		self.faces_combo.set_active(self.faces.index(face))

		self.size_combo.set_value(text_style[2])
		self.align.set_mode(text_style[3])
		self.ligature.set_active(text_style[5])

	def on_style_change(self):
		style_name = self.styles[self.styles_combo.get_active()]
		doc = self.app.current_doc
		doc.text_obj_style = doc.model.get_style(style_name)
		self.update_from_style(doc.text_obj_style[2])
		self.apply_changes()

	def on_font_change(self):
		family = self.families_combo.get_font_family()
		faces = self.faces_dict[family]
		face = self.faces[self.faces_combo.get_active()]
		if not face in faces:face = faces[0]
		self.faces = faces
		self.faces_combo.set_items(self.faces)
		self.faces_combo.set_active(self.faces.index(face))
		self.apply_changes()

	def apply_changes(self, *args):
		doc = self.app.current_doc
		family = self.families_combo.get_font_family()
		face = self.faces[self.faces_combo.get_active()]
		size = self.size_combo.get_value()
		align = self.align.get_mode()
		cluster_flag = self.ligature.get_value()
		if self.target:
			spacing = [] + self.target.style[2][4]
			new_style = deepcopy(self.target.style)
			new_style[2] = [family, face, size, align, spacing, cluster_flag]
			doc.api.set_obj_style(self.target, new_style)
		else:
			spacing = [] + doc.text_obj_style[2][4]
			new_style = deepcopy(doc.text_obj_style)
			new_style[2] = [family, face, size, align, spacing, cluster_flag]
			doc.text_obj_style = new_style
