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

from uc2 import uc2const
from uc2.formats import data
from uc2.formats.pdf import pdfconst, pdfgen

from sk1 import _
from sk1.printing import prn_events

from generic import AbstractPrinter
from propsdlg import PDF_PrnPropsDialog

CUSTOM_SIZE = _('Custom size')

class PDF_Printer(AbstractPrinter):

	name = _('Print to file (PDF)')
	filepath = ''

	colorspace = uc2const.COLOR_CMYK
	pdf_version = pdfconst.PDF_X_4
	compressed = True
	use_spot = False
	customs = ((10.0, 10.0), (30000.0, 30000.0))

	meta_title = ''
	meta_subject = ''
	meta_author = ''
	meta_keywords = ''

	def __init__(self):pass

	def get_driver_name(self): return _('Internal PDF writer')
	def get_connection(self): return _('Software interface')
	def get_state(self): return _('Idle')
	def get_file_type(self): return data.PDF
	def get_filepath(self): return self.filepath
	def set_filepath(self, filepath): self.filepath = filepath
	def is_ready(self): return bool(self.filepath)

	def get_prn_info(self):
		return ((_('Driver:'), self.get_driver_name()),
				(_('Connection'), self.get_connection()))

	def run_propsdlg(self, win):
		dlg = PDF_PrnPropsDialog(win, self)
		if dlg.show():
			prn_events.emit(prn_events.PRINTER_MODIFIED)
			return True
		return False

	def get_format_items(self):
		return uc2const.PAGE_FORMAT_NAMES + [CUSTOM_SIZE, ]

	def is_custom_supported(self):
		return True

	def printing(self, printout):
		pages = printout.get_print_pages()
		cms = printout.get_cms()
		renderer = pdfgen.PDFGenerator(self.filepath, cms, self.pdf_version)

		self.set_meta(renderer, printout.app)
		renderer.set_compression(self.compressed)

		w, h = self.get_page_size()
		for page in pages:
			renderer.start_page(w, h)
			for group in page.childs:
				renderer.render(group.childs)
			renderer.end_page()
		renderer.save()

	def set_meta(self, renderer, app):
		appdata = app.appdata
		creator = '%s %s' % (appdata.app_name, appdata.version)
		producer = '%s %s' % ('UniConvertor', appdata.version)

		renderer.set_creator(creator)
		renderer.set_producer(producer)
		renderer.set_title(self.meta_title)
		renderer.set_author(self.meta_author)
		renderer.set_subject(self.meta_subject)
		renderer.set_keywords(self.meta_keywords)



