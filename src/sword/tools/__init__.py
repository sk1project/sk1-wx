# -*- coding: utf-8 -*-
#
#	Copyright (C) 2012 by Igor E. Novikov
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

import os
import gtk

from sword import _, config
from sword import events
from sword.tools.filebrowser import FileBrowserTool
from sword.tools.logger import Logger
from sword.tools.comparator import Comparator
from sword.tools.clipboard import Clipboard
from sword.tools.decoder import Decoder
from sword.tools.scripting import ScriptingTool

class AppTools(gtk.VBox):

	def __init__(self, mw):
		gtk.VBox.__init__(self, False, 0)
		self.mw = mw
		self.app = mw.app

		self.nb = gtk.Notebook()
		self.nb.set_property('scrollable', True)
		self.nb.set_tab_pos(gtk.POS_BOTTOM)

		self.fb_tool = FileBrowserTool(self.app)
		self.nb.append_page(self.fb_tool, self.fb_tool.caption_label)

		self.log_tool = Logger(self.app)
		self.nb.append_page(self.log_tool, self.log_tool.caption_label)

		self.comp_tool = Comparator(self.app)
		self.nb.append_page(self.comp_tool, self.comp_tool.caption_label)

		self.clip_tool = Clipboard(self.app)
		self.nb.append_page(self.clip_tool, self.clip_tool.caption_label)

		self.decoder_tool = Decoder(self.app)
		self.nb.append_page(self.decoder_tool, self.decoder_tool.caption_label)

		self.scr_tool = ScriptingTool(self.app)
		self.nb.append_page(self.scr_tool, self.scr_tool.caption_label)


		self.add(self.nb)
		self.show_all()

		self.nb.set_current_page(0)
