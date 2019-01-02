# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013 by Igor E. Novikov
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

from uc2 import uc2const
from uc2.formats.sk1 import model
from uc2.formats.sk1.presenter import SK1Presenter
from uc2.formats.sk2.sk2_presenter import SK2_Presenter
from uc2.utils.fsutils import get_fileptr
from uc2.utils.mixutils import merge_cnf


def sk1_loader(appdata, filename=None, fileptr=None, translate=True, cnf=None,
               **kw):
    cnf = merge_cnf(cnf, kw)
    sk1_doc = SK1Presenter(appdata, cnf)
    sk1_doc.load(filename, fileptr)
    if translate:
        sk2_doc = SK2_Presenter(appdata, cnf)
        if filename:
            sk2_doc.doc_file = filename
        sk1_doc.translate_to_sk2(sk2_doc)
        sk1_doc.close()
        return sk2_doc
    return sk1_doc


def sk1_saver(sk2_doc, filename=None, fileptr=None, translate=True, cnf=None,
              **kw):
    cnf = merge_cnf(cnf, kw)
    if sk2_doc.cid == uc2const.SK1:
        translate = False
    if translate:
        sk1_doc = SK1Presenter(sk2_doc.appdata, cnf)
        sk1_doc.translate_from_sk2(sk2_doc)
        sk1_doc.save(filename, fileptr)
        sk1_doc.close()
    else:
        sk2_doc.save(filename, fileptr)


def check_sk1(path):
    fileptr = get_fileptr(path)
    string = fileptr.read(7)
    fileptr.close()
    return string == '##sK1 1'
