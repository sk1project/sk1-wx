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
from wal import LEFT, CENTER

from sk1 import _, events
from sk1.resources import icons, get_bmp
from generic import CtxPlugin

class SimpleMarkupPlugin(CtxPlugin):

	name = 'SimpleMarkupPlugin'

	def __init__(self, app, parent):
		CtxPlugin.__init__(self, app, parent)
#		events.connect(events.DOC_CHANGED, self.update)
#		events.connect(events.DOC_MODIFIED, self.update)

	def build(self):
		self.bold = wal.ImageToggleButton(self, art_id=icons.PD_TEXT_BOLD,
										tooltip=_('Bold'))
		self.add(self.bold, 0, LEFT | CENTER, 2)

		self.italic = wal.ImageToggleButton(self, art_id=icons.PD_TEXT_ITALIC,
										tooltip=_('Italic'))
		self.add(self.italic, 0, LEFT | CENTER, 2)

		self.underline = wal.ImageToggleButton(self, art_id=icons.PD_TEXT_UNDERLINE,
										tooltip=_('Underline'))
		self.add(self.underline, 0, LEFT | CENTER, 2)

		self.strike = wal.ImageToggleButton(self, art_id=icons.PD_TEXT_STRIKETHROUGH,
										tooltip=_('Strikethrough'))
		self.add(self.strike, 0, LEFT | CENTER, 2)

	def update(self, *args):
		pass

	def changed(self, *args):
		pass

class ScriptMarkupPlugin(CtxPlugin):

	name = 'ScriptMarkupPlugin'

	def __init__(self, app, parent):
		CtxPlugin.__init__(self, app, parent)
#		events.connect(events.DOC_CHANGED, self.update)
#		events.connect(events.DOC_MODIFIED, self.update)

	def build(self):
		self.sup = wal.ImageToggleButton(self, art_id=icons.PD_TEXT_SUPERSCRIPT,
										tooltip=_('Superscript'))
		self.add(self.sup, 0, LEFT | CENTER, 2)

		self.sub = wal.ImageToggleButton(self, art_id=icons.PD_TEXT_SUBSCRIPT,
										tooltip=_('Subscript'))
		self.add(self.sub, 0, LEFT | CENTER, 2)

	def update(self, *args):
		pass

	def changed(self, *args):
		pass


