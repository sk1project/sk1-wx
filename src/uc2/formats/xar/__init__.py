# -*- coding: utf-8 -*-
#
#  Copyright (C) 2019 by Maxim S. Barabash
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
#
# Specification:
# http://site.xara.com/support/docs/webformat/spec/

from uc2.formats.xar.xar_const import XAR_SIGNATURE
from uc2.formats.xar.xar_presenter import XAR_Presenter
from uc2.formats.sk2.sk2_presenter import SK2_Presenter
from uc2.utils.fsutils import get_fileptr
from uc2.utils.mixutils import merge_cnf
from uc2 import uc2const


def xar_loader(appdata, filename=None, fileptr=None,
               translate=True, cnf=None, **kw):
    cnf = merge_cnf(cnf, kw)
    xar_doc = XAR_Presenter(appdata, cnf)
    xar_doc.load(filename, fileptr)
    if translate:
        sk2_doc = SK2_Presenter(appdata, cnf)
        if filename:
            sk2_doc.doc_file = filename
        xar_doc.translate_to_sk2(sk2_doc)
        xar_doc.close()
        return sk2_doc
    return xar_doc


def xar_saver(sk2_doc, filename=None, fileptr=None,
              translate=True, cnf=None, **kw):
    cnf = merge_cnf(cnf, kw)
    if sk2_doc.cid == uc2const.XAR:
        translate = False
    if translate:
        xar_doc = XAR_Presenter(sk2_doc.appdata, cnf)
        xar_doc.translate_from_sk2(sk2_doc)
        xar_doc.save(filename, fileptr)
        xar_doc.close()
    else:
        sk2_doc.save(filename, fileptr)


def check_xar(path):
    with get_fileptr(path) as fileptr:
        size = len(XAR_SIGNATURE)
        return XAR_SIGNATURE == fileptr.read(size)
