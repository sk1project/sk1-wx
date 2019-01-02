# -*- coding: utf-8 -*-
#
#  Copyright (C) 2012 by Igor E. Novikov
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

from uc2.formats.plt.plt_presenter import PltPresenter
from uc2.formats.sk2.sk2_presenter import SK2_Presenter
from uc2.utils.fsutils import get_fileptr
from uc2.utils.mixutils import merge_cnf


def plt_loader(appdata, filename=None, fileptr=None, translate=True, cnf=None,
               **kw):
    cnf = merge_cnf(cnf, kw)
    doc = PltPresenter(appdata, cnf)
    doc.load(filename, fileptr)
    if translate:
        sk2_doc = SK2_Presenter(appdata, cnf)
        sk2_doc.doc_file = filename
        doc.translate_to_sk2(sk2_doc)
        doc.close()
        doc = sk2_doc
    return doc


def plt_saver(doc, filename=None, fileptr=None, translate=True, cnf=None, **kw):
    cnf = merge_cnf(cnf, kw)
    if translate:
        plt_doc = PltPresenter(doc.appdata, cnf)
        plt_doc.translate_from_sk2(doc)
        plt_doc.save(filename, fileptr)
        plt_doc.close()
    else:
        doc.save(filename)


def check_plt(path):
    file_size = os.path.getsize(path)
    fileptr = get_fileptr(path)

    if file_size > 20:
        string = fileptr.read(20)
    else:
        string = fileptr.read()

    fileptr.close()
    return string.startswith('IN;')
