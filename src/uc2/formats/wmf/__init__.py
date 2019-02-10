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
from uc2.formats.sk2.sk2_presenter import SK2_Presenter
from uc2.formats.wmf.wmf_presenter import WMF_Presenter
from uc2.formats.wmf.wmf_const import WMF_SIGNATURE, METAFILETYPES, METAVERSIONS
from uc2.utils.fsutils import get_fileptr
from uc2.utils.mixutils import merge_cnf


def wmf_loader(appdata, filename=None, fileptr=None,
               translate=True, cnf=None, **kw):
    cnf = merge_cnf(cnf, kw)
    wmf_doc = WMF_Presenter(appdata, cnf)
    wmf_doc.load(filename, fileptr)
    if translate:
        sk2_doc = SK2_Presenter(appdata, cnf)
        if filename:
            sk2_doc.doc_file = filename
        wmf_doc.translate_to_sk2(sk2_doc)
        wmf_doc.close()
        return sk2_doc
    return wmf_doc


def wmf_saver(sk2_doc, filename=None, fileptr=None,
              translate=True, cnf=None, **kw):
    cnf = merge_cnf(cnf, kw)
    if sk2_doc.cid == uc2const.WMF:
        translate = False
    if translate:
        wmf_doc = WMF_Presenter(sk2_doc.appdata, cnf)
        wmf_doc.translate_from_sk2(sk2_doc)
        wmf_doc.save(filename, fileptr)
        wmf_doc.close()
    else:
        sk2_doc.save(filename, fileptr)


def check_wmf(path):
    fileptr = get_fileptr(path)
    sign = fileptr.read(len(WMF_SIGNATURE))
    fileptr.seek(0)
    metatype = fileptr.read(2)
    fileptr.read(2)
    metaver = fileptr.read(2)
    fileptr.close()
    if sign == WMF_SIGNATURE:
        return True
    if metatype in METAFILETYPES and metaver in METAVERSIONS:
        return True
    return False
