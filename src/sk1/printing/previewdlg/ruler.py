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

import wal, wx

from uc2 import cms

from sk1 import _, config
from sk1.resources import icons, get_icon

class PreviewCorner(wal.HPanel, wal.Canvas):

	icon = None

	def __init__(self, parent):
		size = config.ruler_size
		wal.HPanel.__init__(self, parent)
		wal.Canvas.__init__(self)
		self.pack((size, size))
		self.set_bg(wal.WHITE)
		self.icon = get_icon(icons.ORIGIN_LL)
		self.refresh()

	def paint(self):
		w, h = self.get_size()
		self.set_stroke()
		self.set_fill(cms.val_255(config.ruler_bg))
		self.draw_rect(0, 0, w, h)

		stop_clr = cms.val_255(config.ruler_fg) + [255]
		start_clr = cms.val_255(config.ruler_fg) + [0]

		rect = (0, h - 1, w * 2, 1)
		self.gc_draw_linear_gradient(rect, start_clr, stop_clr)

		rect = (w - 1, 0, 1, h * 2)
		self.gc_draw_linear_gradient(rect, start_clr, stop_clr, True)

		shift = (w - 19) / 2 + 1
		self.draw_bitmap(self.icon, shift, shift)
