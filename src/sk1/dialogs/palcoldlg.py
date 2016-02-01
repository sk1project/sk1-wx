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

import wal
import urllib2, os
from cStringIO import StringIO

from uc2.formats.skp import skp_loader
from sk1 import _, config
from sk1.pwidgets import PaletteViewer

class PaletteCollectionDialog(wal.OkCancelDialog):

	data = []
	palette = None

	def __init__(self, app, parent):
		self.app = app
		size = config.palcol_dlg_size
		title = _('Palette Collection')
		wal.OkCancelDialog.__init__(self, parent, title, size, resizable=True,
								action_button=wal.BUTTON_SAVE,
								on_load=self.on_load)
		self.set_minsize(config.palcol_dlg_minsize)

	def build(self):
		self.stub = DataStub(self)
		self.pack(self.stub, expand=True, fill=True)
		self.stub.show()
		self.viewer = DataViewer(self)
		self.pack(self.viewer, expand=True, fill=True)
		self.viewer.hide()

	def show(self):
		self.ok_btn.set_enable(False)
		return wal.OkCancelDialog.show(self)

	def on_load(self, *args):
		self._timer.Stop()
		self.data = self.stub.get_palette_list()
		if self.data:
			self.stub.hide()
			self.viewer.show()
		else:
			msg = _('Cannot connect to server!')
			msg += '\n' + _('Please check Internet connection')
			msg += '\n' + _('and access to http://sk1project.org')
			wal.error_dialog(self, self.app.appdata.app_name, msg)
			self.on_cancel()

	def get_result(self): return self.palette

class DataStub(wal.HPanel):

	def __init__(self, parent):
		self.parent = parent
		wal.HPanel.__init__(self, parent)
		int_panel = wal.VPanel(self)
		self.pack(int_panel, expand=True)
		int_panel.pack(wal.Label(int_panel, _('Loading data...')))
		path = os.path.join(config.resource_dir, 'icons', 'generic')
		filepath = os.path.join(path, 'progress.gif')
		self.gif = wal.AnimatedGif(int_panel, filepath)
		int_panel.pack(self.gif, padding_all=10)
		self.gif.play()

	def get_palette_list(self):
		url = 'http://sk1project.org/palettes.php?action=get_list'
		data = []
		try:
			txt = urllib2.urlopen(url).read()
			code = compile('data=' + txt, '<string>', 'exec')
			exec code
		except:pass
		self.gif.stop()
		return data


class DataViewer(wal.HPanel):

	def __init__(self, parent):
		self.app = parent.app
		self.parent = parent
		wal.HPanel.__init__(self, parent)
		self.pal_list = wal.SimpleList(self, self.parent.data,
									on_select=self.change_palette)
		self.pack(self.pal_list, expand=True, fill=True, padding_all=5)
		self.preview = PreViewer(self)
		self.pack(self.preview, fill=True, padding_all=5)

	def show(self):
		wal.HPanel.show(self)
		self.pal_list.update(self.parent.data)

	def change_palette(self, name=''):
		palette = None
		index = self.parent.data.index(name) + 1
		pid = '0' * (4 - len(str(index))) + str(index)
		url = 'http://sk1project.org/palettes.php?action=get_palette&id=%s' % pid
		try:
			pal_url = urllib2.urlopen(url).read()
			pal_txt = urllib2.urlopen(pal_url).read()
			pal_stream = StringIO(pal_txt)
			pal_stream.seek(0)
			palette = skp_loader(self.app.appdata, None, pal_stream, False)
			self.parent.ok_btn.set_enable(True)
		except:
			self.parent.ok_btn.set_enable(False)
		self.parent.palette = palette
		self.preview.viewer.draw_palette(palette)


class PreViewer(wal.VPanel):

	def __init__(self, parent):
		self.parent = parent
		self.app = parent.parent.app
		wal.VPanel.__init__(self, parent)
		self.viewer = PaletteViewer(self, self.app.default_cms)
		self.pack(self.viewer, expand=True, fill=True)


def palette_collection_dlg(app, parent):
	ret = PaletteCollectionDialog(app, parent).show()
	return ret
