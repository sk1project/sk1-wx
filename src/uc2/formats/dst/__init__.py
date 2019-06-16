# -*- coding: utf-8 -*-
#
#  Copyright (C) 2009-2019 by Maxim S. Barabash
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

from uc2.utils.fsutils import get_fileptr
from uc2.utils.mixutils import merge_cnf


def dst_loader(appdata, filename=None, fileptr=None, translate=True, cnf=None,
               **kw):
    from uc2.formats.dst.dst_presenter import DstPresenter
    from uc2.formats.sk2.sk2_presenter import SK2_Presenter
    cnf = merge_cnf(cnf, kw)
    doc = DstPresenter(appdata, cnf)
    doc.load(filename, fileptr)
    if translate:
        sk2_doc = SK2_Presenter(appdata, cnf)
        sk2_doc.doc_file = filename
        doc.translate_to_sk2(sk2_doc)
        doc.close()
        doc = sk2_doc
    return doc


def dst_saver(doc, filename=None, fileptr=None, translate=True, cnf=None, **kw):
    from uc2.formats.dst.dst_presenter import DstPresenter
    cnf = merge_cnf(cnf, kw)
    if translate:
        dst_doc = DstPresenter(doc.appdata, cnf)
        dst_doc.translate_from_sk2(doc)
        dst_doc.save(filename, fileptr)
        dst_doc.close()
    else:
        doc.save(filename)


def check_dst(path):
    file_size = os.path.getsize(path)
    fileptr = get_fileptr(path)

    if file_size > 3:
        string = fileptr.read(3)
    else:
        string = fileptr.read()

    fileptr.close()
    return string.startswith('LA:')
