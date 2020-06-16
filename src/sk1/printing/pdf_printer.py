# -*- coding: utf-8 -*-
#
#  Copyright (C) 2016 by Ihor E. Novikov
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os

from uc2 import uc2const
from uc2.formats.pdf import pdfconst, pdfgen

from sk1 import _, config
from sk1.printing import prn_events
from sk1.dialogs import get_save_file_name

from generic import AbstractPrinter, COLOR_MODE
from propsdlg import PDF_PrnPropsDialog

CUSTOM_SIZE = _('Custom size')


class PDF_Printer(AbstractPrinter):
    name = _('Print to file (PDF)')
    filepath = ''

    color_mode = COLOR_MODE
    colorspace = uc2const.COLOR_CMYK
    pdf_version = pdfconst.PDF_X_4
    compressed = True
    use_spot = False
    customs = ((10.0, 10.0), (30000.0, 30000.0))
    margins = (0.0, 0.0, 0.0, 0.0)

    meta_title = ''
    meta_subject = ''
    meta_author = ''
    meta_keywords = ''

    def is_color(self):
        return True

    def get_driver_name(self):
        return _('Internal PDF writer')

    def get_connection(self):
        return _('Software interface')

    def get_state(self):
        return _('Idle')

    def get_file_type(self):
        return uc2const.PDF

    def get_filepath(self):
        return self.filepath

    def set_filepath(self, filepath):
        self.filepath = filepath

    def is_ready(self):
        return bool(self.filepath)

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
        renderer = pdfgen.PDFGenerator(self.filepath, printout.get_cms(),
                                       self.pdf_version)

        self.set_meta(renderer, printout.app)
        renderer.set_compression(self.compressed)
        renderer.set_colorspace(self.colorspace)
        renderer.set_spot_usage(self.use_spot)

        renderer.set_progress_message(_('Printing in progress...'))
        renderer.set_num_pages(len(pages))

        w, h = self.get_page_size()
        for page in pages:
            renderer.start_page(w, h)
            for group in page.childs:
                renderer.render(group.childs, True)
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

    def run_printdlg(self, win, printout):
        if not self.filepath:
            doc_file = 'print'
            doc_file = os.path.join(config.print_dir, doc_file)
            msg = _('Select output file')
            file_types = [self.get_file_type(), ]
            self.filepath = get_save_file_name(win, doc_file, msg,
                                               path_only=True,
                                               file_types=file_types)
            if not self.filepath:
                return False
        return AbstractPrinter.run_printdlg(self, win, printout)
