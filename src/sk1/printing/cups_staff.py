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

import os, cups

from uc2 import uc2const
from uc2.formats.pdf import pdfconst, pdfgen

from sk1 import _, config
from sk1.printing import prn_events
from generic import AbstractPrinter, AbstractPS
from pdf_printer import PDF_Printer
from propsdlg import CUPS_PrnPropsDialog

class CUPS_PS(AbstractPS):

	connection = None
	printers = []
	default_printer = ''

	def __init__(self, physial_only=False):
		self.connection = cups.Connection()
		self.printers = []
		prn_dict = self.connection.getPrinters()
		for item in prn_dict.keys():
			prn = CUPS_Printer(self.connection, item, prn_dict[item])
			self.printers.append(prn)
		if not physial_only:
			self.printers.append(PDF_Printer())
		self.default_printer = self.connection.getDefault()

	def get_default_printer(self):
		for item in self.printers:
			if not item.is_virtual():
				if item.cups_name == self.default_printer:
					return item
		if self.printers:
			return self.printers[0]
		else:
			return None

	def get_printer_by_name(self, name):
		for item in self.printers:
			if item.get_name() == name:
				return item
		return None

	def get_printer_names(self):
		ret = []
		for item in self.printers:
			ret.append(item.get_name())
		return ret

MONOCHROME_MODE = 'monochrome'
COLOR_MODE = 'color'

CUSTOM_SIZE = _('Custom size')

UNIT_MM = 'mm'
UNIT_IN = 'in'

ORIENTATION_MAP = {
uc2const.PORTRAIT:'3',
uc2const.LANDSCAPE:'4',
}


def process_media_name(name):
	try:
		if '-' in name:name = name.split('-')
		else:name = [name, ]
		capname = []
		for item in name:
			capname.append(item.capitalize())
	except:
		return None
	return ' '.join(capname)

def process_media_size(size):
	try:
		w, h = size.split('x')
		h, units = h[:-2], h[-2:]
		w = float(w)
		h = float(h)
		if units == UNIT_MM:
			w = uc2const.mm_to_pt * w
			h = uc2const.mm_to_pt * h
		elif units == UNIT_IN:
			w = uc2const.in_to_pt * w
			h = uc2const.in_to_pt * h
		else: return ()
	except:
		return ()
	return (w, h)

def process_media(media_list):
	customs = []
	media = []
	for item in media_list:
		if item[:6] == 'custom':
			customs.append(item)
		else:
			media.append(item)

	sorted_media = []
	media_dict = {}
	for item in media:
		indx, name, size = item.split('_')

		name = process_media_name(name)
		if not name: continue
		if name[0] == 'W' and name[1] in '0123456789': continue
		if indx == 'na': name = 'US ' + name
		elif indx == 'jis': name = 'JIS ' + name

		size = process_media_size(size)
		if not size: continue
		sorted_media.append(item)
		media_dict[item] = (name, size)

	custon_ranges = ()
	if len(customs) == 2:
		minsize = ()
		maxsize = ()
		for item in customs:
			name, size = item.split('_')[1:]
			size = process_media_size(size)
			if not size: continue
			if name == 'min': minsize = size
			elif name == 'max': maxsize = size
		if minsize and maxsize:
			custon_ranges = (minsize, maxsize)

	return sorted_media, media_dict, custon_ranges


STD_PAGE_FORMAT = ('A4', uc2const.PAGE_FORMATS['A4'])
STD_MARGINS = (10.0, 10.0, 10.0, 10.0)
STD_SHIFTS = (0.0, 0.0)


class CUPS_Printer(AbstractPrinter):

	connection = None
	cups_name = ''
	details = {}
	attrs = {}

	pf_list = []
	pf_dict = {}
	customs = ()
	def_media = ''

	color_mode = MONOCHROME_MODE
	colorspace = uc2const.COLOR_GRAY
	page_format = STD_PAGE_FORMAT
	page_orientation = uc2const.PORTRAIT
	margins = STD_MARGINS
	shifts = STD_SHIFTS

	def __init__(self, connection, cups_name, details):
		self.connection = connection
		self.cups_name = cups_name
		self.details = details
		self.update_attrs()
		if self.cups_name in config.printer_config:
			data = config.printer_config[self.cups_name]
			self.shifts = data[0]
			self.margins = data[1]

	def save_config(self):
		val = [() + self.shifts, () + self.margins]
		config.printer_config[self.cups_name] = val

	def update_attrs(self):
		self.attrs = self.connection.getPrinterAttributes(self.cups_name)
		self.color_mode = self.attrs['print-color-mode-default']
		if self.is_color() and self.color_mode == COLOR_MODE:
			self.colorspace = uc2const.COLOR_CMYK

		medias = self.attrs['media-supported']
		self.pf_list, self.pf_dict, self.customs = process_media(medias)

		self.def_media = self.attrs['media-default']
		if not self.def_media in self.pf_list and self.pf_list:
			self.def_media = self.pf_list[0]
		self.page_format = self.pf_dict[self.def_media]

	def is_virtual(self): return False
	def get_name(self): return self.details['printer-info']
	def get_driver_name(self): return self.details['printer-make-and-model']
	def get_connection(self): return self.details['device-uri']

	def get_prn_info(self):
		return ((_('Driver:'), self.get_driver_name()),
				(_('Connection'), self.get_connection()))

	def run_propsdlg(self, win):
		dlg = CUPS_PrnPropsDialog(win, self)
		if dlg.show():
			prn_events.emit(prn_events.PRINTER_MODIFIED)
			return True
		return False

	def is_color(self):
		if 'color-supported' in self.attrs:
			if self.attrs['color-supported']:
				return True
		return False

	def is_custom_supported(self):
		return bool(self.customs)

	def get_format_items(self):
		items = []
		for item in self.pf_list:
			items.append(self.pf_dict[item][0])
		if self.customs:
			items.append(CUSTOM_SIZE)
		return items

	def get_printing_options(self):
		options = {}
		options['media'] = self.def_media
		options['copies'] = str(self.copies)
		options['print-color-mode'] = self.color_mode
#		options['orientation-requested'] = ORIENTATION_MAP[self.page_orientation]
		if self.collate: options['collate'] = 'True'
		return options

	def printing(self, printout, media=''):
		appdata = printout.app.appdata
		path = os.path.join(appdata.app_temp_dir, 'printout.pdf')
		fileptr = open(path, 'wb')
		pages = printout.get_print_pages()
		renderer = pdfgen.PDFGenerator(fileptr, printout.get_cms(),
									pdfconst.PDF_VERSION_DEFAULT)

		creator = '%s %s' % (appdata.app_name, appdata.version)
		producer = '%s %s' % ('UniConvertor', appdata.version)
		renderer.set_creator(creator)
		renderer.set_producer(producer)
		title = '%s - [%s]' % (creator, printout.doc.doc_name)

		renderer.set_compression(True)
		renderer.set_colorspace(self.colorspace)
		renderer.set_spot_usage(False)

		renderer.set_progress_message(_('Printing in progress...'))
		renderer.set_num_pages(len(pages))

		w, h = self.get_page_size()
		for page in pages:
			renderer.start_page(w, h, self.shifts[0], self.shifts[1])
			for group in page.childs:
				renderer.render(group.childs, True)
			renderer.end_page()
		renderer.save()

		fileptr.close()

		options = self.get_printing_options()
		if media: options['media'] = media

		self.connection.printFile(self.cups_name, path, title, options)



