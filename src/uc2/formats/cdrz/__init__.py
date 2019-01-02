# -*- coding: utf-8 -*-
#
#  Copyright (C) 2011-2012 by Igor E. Novikov
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

import zipfile

from uc2.formats.cdrz import const
from uc2.formats.cdrz.presenter import CDRZ_Presenter
from uc2.formats.pdxf.presenter import PDXF_Presenter
from uc2.utils.mixutils import merge_cnf


def cdrz_loader(appdata, filename, translate=True, cnf=None, **kw):
    cnf = merge_cnf(cnf, kw)
    doc = CDRZ_Presenter(appdata, cnf)
    doc.load(filename)
    if translate:
        pdxf_doc = PDXF_Presenter(appdata, cnf)
        pdxf_doc.doc_file = filename
        doc.traslate_to_pdxf(pdxf_doc)
        doc.close()
        doc = pdxf_doc
    return doc


def cdrz_saver(cdr_doc, filename, translate=True, cnf=None, **kw):
    cnf = merge_cnf(cnf, kw)
    cdr_doc.save(filename)


def check_cdrz(path):
    if not zipfile.is_zipfile(path):
        return False

    cdrz_file = zipfile.ZipFile(path, 'r')
    fl = cdrz_file.namelist()
    if 'content/riffData.cdr' not in fl:
        return False
    return True
