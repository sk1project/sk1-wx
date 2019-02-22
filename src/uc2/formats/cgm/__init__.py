# -*- coding: utf-8 -*-
#
#  Copyright (C) 2017-2019 by Igor E. Novikov
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
# https://standards.iso.org/ittf/PubliclyAvailableStandards/c032380_ISO_IEC_8632-3_1999(E).zip


from uc2 import uc2const, utils
from uc2.formats.cgm.cgm_const import CGM_SIGNATURE
from uc2.formats.cgm.cgm_presenter import CGM_Presenter
from uc2.formats.sk2.sk2_presenter import SK2_Presenter
from uc2.utils.fsutils import get_fileptr
from uc2.utils.mixutils import merge_cnf


def cgm_loader(appdata, filename=None, fileptr=None,
               translate=True, cnf=None, **kw):
    cnf = merge_cnf(cnf, kw)
    cgm_doc = CGM_Presenter(appdata, cnf)
    cgm_doc.load(filename, fileptr)
    if translate:
        sk2_doc = SK2_Presenter(appdata, cnf)
        if filename:
            sk2_doc.doc_file = filename
        cgm_doc.translate_to_sk2(sk2_doc)
        cgm_doc.close()
        return sk2_doc
    return cgm_doc


def cgm_saver(sk2_doc, filename=None, fileptr=None,
              translate=True, cnf=None, **kw):
    cnf = merge_cnf(cnf, kw)
    if sk2_doc.cid == uc2const.CGM:
        translate = False
    if translate:
        cgm_doc = CGM_Presenter(sk2_doc.appdata, cnf)
        cgm_doc.translate_from_sk2(sk2_doc)
        cgm_doc.save(filename, fileptr)
        cgm_doc.close()
    else:
        sk2_doc.save(filename, fileptr)


def check_cgm(path):
    with get_fileptr(path) as fileptr:
        sign = fileptr.read(2)
    return utils.uint16_be(sign) & 0xffe0 == CGM_SIGNATURE
