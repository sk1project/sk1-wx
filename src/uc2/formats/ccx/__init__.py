# -*- coding: utf-8 -*-
#
#  Copyright (C) 2019 by Igor E. Novikov
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
from uc2.formats.cmx import cmx_const
from uc2.formats.cmx.cmx_presenter import CMX_Presenter
from uc2.formats.sk2.sk2_presenter import SK2_Presenter
from uc2.utils.fsutils import get_fileptr
from uc2.utils.mixutils import merge_cnf


def ccx_loader(appdata, filename=None, fileptr=None,
               translate=True, cnf=None, **kw):
    kw['pack'] = True
    cnf = merge_cnf(cnf, kw)
    ccx_doc = CMX_Presenter(appdata, cnf)
    ccx_doc.cid = uc2const.CCX
    ccx_doc.load(filename, fileptr)
    if translate:
        sk2_doc = SK2_Presenter(appdata, cnf)
        sk2_doc.doc_file = filename
        ccx_doc.translate_to_sk2(sk2_doc)
        ccx_doc.close()
        return sk2_doc
    return ccx_doc


def ccx_saver(sk2_doc, filename=None, fileptr=None,
              translate=True, cnf=None, **kw):
    kw['pack'] = True
    cnf = merge_cnf(cnf, kw)
    if sk2_doc.cid == uc2const.CCX:
        translate = False
    if translate:
        ccx_doc = CMX_Presenter(sk2_doc.appdata, cnf)
        ccx_doc.cid = uc2const.CCX
        ccx_doc.translate_from_sk2(sk2_doc)
        ccx_doc.save(filename, fileptr)
        ccx_doc.close()
    else:
        sk2_doc.save(filename, fileptr)


def check_ccx(path):
    with get_fileptr(path) as fileptr:
        riff_sign = fileptr.read(4) in (cmx_const.ROOT_ID, cmx_const.ROOTX_ID)
        _size = fileptr.read(4)
        ccx_sign = fileptr.read(4) == cmx_const.CDRX_ID
    return riff_sign and ccx_sign
