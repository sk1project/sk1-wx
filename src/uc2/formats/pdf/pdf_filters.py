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

import sys

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader

from uc2.formats.generic_filters import AbstractSaver
from pdfconst import PDF_VERSION_DEFAULT

class PDF_Saver(AbstractSaver):

	name = 'PDF_Saver'
	canvas = None
	methods = None
	desktop_layers = None
	master_layers = None
	page_trafo = None


	def do_save(self):
		self.canvas = Canvas(self.fileptr, pdfVersion=PDF_VERSION_DEFAULT)
		self.presenter.update()
		self.methods = self.presenter.methods
		self.desktop_layers = self.methods.get_desktop_layers()
		self.master_layers = self.methods.get_master_layers()
		pages = self.methods.get_pages()
		for page in pages:
			self.canvas.setPageSize(self.methods.get_page_size(page))
			layers = self.desktop_layers + self.methods.get_layers(page)
			layers += self.master_layers
			for layer in layers:
				if self.methods.is_layer_visible(layer) and \
				self.methods.is_layer_printable(layer):
					for obj in layer.childs:
						pass
			self.canvas.showPage()
		self.canvas.save()