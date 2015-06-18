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

import os, cairo

import wal

from uc2.uc2const import FORMAT_EXTENSION, PNG, FORMAT_NAMES
from uc2.uc2const import SKP, GPL, SCRIBUS_PAL, SOC, COREL_PAL, ASE, CPL, JCW
from uc2.formats import get_saver_by_id, get_loader_by_id
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
		OUT_PATH = '/home/igor/PALETTES/COLLECTION/'
		IN_PATH = '/home/igor/PALETTES/SORTED/'
		files = []
		for r, d, f in os.walk(IN_PATH):
			files += f
		files.sort()
		pid = 1
		loader = get_loader_by_id(SKP)

		for item in files:
			print item,
			pal_id = '0' * (4 - len(str(pid))) + str(pid)
			dir_path = os.path.join(OUT_PATH, 'id' + pal_id)
			palfile = os.path.join(IN_PATH, item)
			if not os.path.exists(dir_path): os.makedirs(dir_path)
			try:
				palette = loader(self.app.appdata, palfile, None, False, False)
				self.process_palette(dir_path, palette, pal_id)
				print ' => OK'
				pid += 1
			except:
				print ' => False'

#		dir_path = get_dir_path(self.win, self.app, path=config.collection_dir,
#						msg='Select directory for collection item')
#		if not dir_path: return
#		config.collection_dir = os.path.dirname(dir_path)
#		pal_id = dir_path[-4:]
#
#		palette_name = self.mngr.pal_list.get_selected()
#		palette = self.mngr.get_palette_by_name(palette_name)
#		self.process_palette(dir_path, palette, pal_id)

	def process_palette(self, dir_path, palette, pal_id):
		palette_name = palette.model.name
		palette_filename = palette_name.replace(' ', '_').replace('.', '_')
		pal_resources = ''

		for sid in saver_ids:
			saver = get_saver_by_id(sid)
			ext = '.' + FORMAT_EXTENSION[sid][0]
			if sid == SCRIBUS_PAL: ext = '(Scribus)' + ext
			if sid == COREL_PAL: ext = '(CorelDRAW)' + ext
			filename = palette_filename + ext
			doc_file = os.path.join(dir_path, filename)
			pal_resources += '\t"%s"=>"%s",\n' % (FORMAT_NAMES[sid], filename)
			saver(palette, doc_file, None, False, True)

			#saving for tarballs
			collection_path = os.path.dirname(dir_path)
			fmt_path = os.path.join(collection_path, FORMAT_NAMES[sid])
			if not os.path.exists(fmt_path): os.makedirs(fmt_path)
			doc_file = os.path.join(fmt_path, filename)
			saver(palette, doc_file, None, False, True)

		sk2_doc = SK2_Presenter(self.app.appdata)
		palette.translate_to_sk2(sk2_doc)

		saver = get_saver_by_id(PNG)
		doc_file = os.path.join(dir_path, 'preview.png')
		saver(sk2_doc, doc_file, None, True, False, antialiasing=False)
		sk2_doc.close()

		#Thumbnail generation
		surface = cairo.ImageSurface(cairo.FORMAT_RGB24, int(514), int(20))
		ctx = cairo.Context(surface)
		ctx.set_antialias(cairo.ANTIALIAS_NONE)
		ctx.set_source_rgb(0.0, 0.0, 0.0)
		ctx.fill()

		x = y = 1
		w = h = 18
		for color in palette.model.colors:
			r, g, b = self.app.default_cms.get_display_color(color)
			ctx.set_source_rgb(r, g, b)
			ctx.rectangle(x, y, w, h)
			ctx.fill()
			x += w + 1

		ctx.set_source_rgb(1, 1, 1)
		ctx.rectangle(x, 0, 514, 20)
		ctx.fill()

		if len(palette.model.colors) > 22:
			lg = cairo.LinearGradient(418, 0, 513, 0)
			lg.add_color_stop_rgba(0, 1, 1, 1, 0)
			lg.add_color_stop_rgba(1, 1, 1, 1, 1)
			ctx.rectangle(418, 0, 513, 20)
			ctx.set_source(lg)
			ctx.fill()

		filename = os.path.join(dir_path, 'thumbnail.png')
		fileptr = open(filename, 'wb')
		surface.write_to_png(fileptr)
		fileptr.close()

		#index.php generation
		filename = os.path.join(dir_path, 'index.php')
		fileptr = open(filename, 'wb')
		content = '<?php\n'
		content += 'header("HTTP/1.1 301 Moved Permanently");\n'
		content += 'header( "Location: /palettes.php", true, 301);\n'
		content += 'exit;\n'
		content += '?>\n'
		fileptr.write(content)
		fileptr.close()

		#descriptor generation
		filename = os.path.join(dir_path, 'descriptor.php')
		fileptr = open(filename, 'wb')
		content = '<?php\n'
		content += '$descriptor = array(\n'
		content += '"id"=>"%s",\n' % pal_id
		content += '"name"=>"%s",\n' % palette_name
		content += '"source"=>"%s",\n' % palette.model.source
		comments = palette.model.comments.replace('\n', '<br>')
		content += '"comments"=>"%s",\n' % comments.replace('"', '\\"')
		content += '"ncolors"=>"%d",\n' % len(palette.model.colors)
		content += '"files"=>array(\n'
		content += pal_resources
		content += '\t),\n'
		content += ');\n'
		content += '?>\n'
		fileptr.write(content)
		fileptr.close()
