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


def cmx_loader(appdata, filename=None, fileptr=None,
               translate=True, cnf=None, **kw):
    cnf = merge_cnf(cnf, kw)
    cmx_doc = CMX_Presenter(appdata, cnf)
    cmx_doc.load(filename, fileptr)
    if translate:
        sk2_doc = SK2_Presenter(appdata, cnf)
        sk2_doc.doc_file = filename
        cmx_doc.translate_to_sk2(sk2_doc)
        cmx_doc.close()
        return sk2_doc
    return cmx_doc


def cmx_saver(sk2_doc, filename=None, fileptr=None,
              translate=True, cnf=None, **kw):
    cnf = merge_cnf(cnf, kw)
    if sk2_doc.cid == uc2const.CMX:
        translate = False
    if translate:
        cmx_doc = CMX_Presenter(sk2_doc.appdata, cnf)
        cmx_doc.translate_from_sk2(sk2_doc)
        cmx_doc.save(filename, fileptr)
        cmx_doc.close()
    else:
        sk2_doc.save(filename, fileptr)


def check_cmx(path):
    with get_fileptr(path) as fileptr:
        riff_sign = fileptr.read(4) in (cmx_const.ROOT_ID, cmx_const.ROOTX_ID)
        _size = fileptr.read(4)
        cmx_sign = fileptr.read(4) == cmx_const.CMX_ID
    return riff_sign and cmx_sign
