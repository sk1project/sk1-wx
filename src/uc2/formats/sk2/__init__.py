# -*- coding: utf-8 -*-
#
#  Copyright (C) 2015 by Igor E. Novikov
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

from uc2 import _
from uc2.formats.sk2.sk2_presenter import SK2_Presenter
from uc2.sk2const import SK2DOC_ID, SK2XML_ID, SK2VER
from uc2.utils.fsutils import get_fileptr
from uc2.utils.mixutils import merge_cnf


def sk2_loader(appdata, filename=None, fileptr=None, translate=True, cnf=None,
               **kw):
    cnf = merge_cnf(cnf, kw)
    doc = SK2_Presenter(appdata, cnf)
    doc.load(filename, fileptr)
    return doc


def sk2_saver(sk2_doc, filename=None, fileptr=None, translate=True, cnf=None,
              **kw):
    cnf = merge_cnf(cnf, kw)
    sk2_doc.save(filename, fileptr)


def check_sk2(path):
    ret = False
    fileptr = get_fileptr(path)
    ln = fileptr.readline()
    if ln[:len(SK2DOC_ID)] == SK2DOC_ID:
        if int(ln[len(SK2DOC_ID):]) <= int(SK2VER):
            ret = True
        else:
            fileptr.close()
            raise RuntimeError(_('Newer version of SK2 format is found!'))
    else:
        ln2 = fileptr.readline()
        if ln2[:len(SK2XML_ID)] == SK2XML_ID:
            if int(ln2[len(SK2XML_ID):]) <= int(SK2VER):
                ret = True
            else:
                fileptr.close()
                raise RuntimeError(_('Newer version of SK2 format is found!'))
    fileptr.close()
    return ret
