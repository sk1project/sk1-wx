# -*- coding: utf-8 -*-
#
#  Copyright (C) 2016 by Igor E. Novikov
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

from uc2.formats.pdf.pdf_filters import PDF_Saver
from uc2.formats.pdf.pdfconst import PDF_SIGNATURE
from uc2.utils.fsutils import get_fileptr
from uc2.utils.mixutils import merge_cnf


def pdf_loader(appdata, filename=None, fileptr=None, translate=True, cnf=None,
               **kw):
    pass


def pdf_saver(sk2_doc, filename=None, fileptr=None, translate=True, cnf=None,
              **kw):
    cnf = merge_cnf(cnf, kw)
    sk2_saver = sk2_doc.saver
    sk2_doc.saver = PDF_Saver()
    sk2_doc.save(filename, fileptr)
    sk2_doc.saver = sk2_saver


def check_pdf(path):
    fileptr = get_fileptr(path)
    string = fileptr.read(len(PDF_SIGNATURE))
    fileptr.close()
    return string == PDF_SIGNATURE
