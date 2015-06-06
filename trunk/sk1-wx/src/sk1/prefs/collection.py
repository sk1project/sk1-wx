# -*- coding: utf-8 -*-
#
#	Copyright (C) 2015 by Igor E. Novikov
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

import wal

from uc2.uc2const import FORMAT_EXTENSION, PNG
from uc2.uc2const import SKP, GPL, SCRIBUS_PAL, SOC, COREL_PAL, ASE, CPL, JCW
from uc2.formats import get_saver_by_id
from uc2.formats.sk2.sk2_presenter import SK2_Presenter

from sk1 import config
from sk1.resources import icons
from sk1.dialogs import get_dir_path

saver_ids = [SKP, GPL, SOC, SCRIBUS_PAL, COREL_PAL, ASE, CPL, JCW]

class CollectionButton(wal.ImageButton):

	def __init__(self, parent, app, mngr, win):

		self.app = app
		self.mngr = mngr
		self.win = win

		wal.ImageButton.__init__(self, parent, icons.PD_FILE_SAVE,
								art_size=wal.SIZE_32, flat=False,
								tooltip='Create collection item',
								onclick=self.on_click)

	def on_click(self, *args):
		dir_path = get_dir_path(self.win, self.app, path=config.collection_dir,
						msg='Select directory for collection item')
		if not dir_path: return
		config.collection_dir = os.path.dirname(dir_path)
		pal_id = dir_path[-4:]

		palette_name = self.mngr.pal_list.get_selected()
		palette = self.mngr.get_palette_by_name(palette_name)
		palette_filename = palette_name.replace(' ', '_')

		for sid in saver_ids:
			saver = get_saver_by_id(sid)
			ext = '.' + FORMAT_EXTENSION[sid][0]
			if sid == SCRIBUS_PAL: ext = '(Scribus)' + ext
			if sid == COREL_PAL: ext = '(CorelDRAW)' + ext
			doc_file = os.path.join(dir_path, palette_filename + ext)
			saver(palette, doc_file, None, False, True)

		sk2_doc = SK2_Presenter(self.app.appdata)
		palette.translate_to_sk2(sk2_doc)

		saver = get_saver_by_id(PNG)
		doc_file = os.path.join(dir_path, 'preview.png')
		saver(sk2_doc, doc_file, None, True, False, antialiasing=False)
		sk2_doc.close()
