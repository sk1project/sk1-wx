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

from uc2 import uc2const
from uc2.formats.generic import TaggedModelPresenter
from uc2.formats.corel_pal.corel_pal_config import CorelPalette_Config
from uc2.formats.xml_.xml_filters import XML_Loader, XML_Saver
from uc2.formats.corel_pal.corel_pal_methods import CorelPalette_Methods, \
create_new_palette


class CorelPalette_Presenter(TaggedModelPresenter):

	cid = uc2const.COREL_PAL

	config = None
	doc_file = ''
	resources = None
	cms = None

	def __init__(self, appdata, cnf={}, filepath=None):
		self.config = CorelPalette_Config()
		config_file = os.path.join(appdata.app_config_dir, self.config.filename)
		self.config.load(config_file)
		self.config.update(cnf)
		self.appdata = appdata
		self.cms = self.appdata.app.default_cms
		self.loader = XML_Loader()
		self.saver = XML_Saver()
		self.methods = CorelPalette_Methods(self)
		if filepath is None:
			self.new()
		else:
			self.load(filepath)

	def new(self):
		self.model = create_new_palette(self.config)
		self.update()

	def update(self, action=False):
		TaggedModelPresenter.update(self, action)
		self.methods.update()

	def convert_from_skp(self, skp_doc):
		mtds = self.methods
		skp = skp_doc.model
		encoding = self.config.encoding
		mtds.set_palette_name(skp.name.encode(encoding))

		comments = ''
		if skp.source:
			comments += 'Palette source: ' + skp.source + '\n'
		if skp.comments:
			for item in skp.comments.splitlines():
				comments += item + '\n'
		mtds.set_palette_comments(comments.encode(encoding))
		for item in skp.colors:
			mtds.add_color(item)
		mtds.clear_model()

	def convert_to_skp(self, skp_doc):
		skp = skp_doc.model
		mtds = self.methods
		encoding = self.config.encoding

		skp.name = mtds.get_palette_name().decode(encoding)
		if self.doc_file:
			filename = os.path.basename(self.doc_file)
			skp.comments = 'Converted from %s' % filename
		skp.source = '' + self.config.source
		skp.colors = mtds.get_colors()



