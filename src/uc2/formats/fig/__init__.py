# -*- coding: utf-8 -*-
#
#  Copyright (C) 2018 by Maxim S. Barabash
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
from uc2 import uc2const
from uc2.formats.sk2.sk2_presenter import SK2_Presenter
from uc2.formats.fig.fig_presenter import FIG_Presenter
from uc2.utils.mixutils import merge_cnf
from uc2.utils.fsutils import get_fileptr


def fig_loader(appdata, filename=None, fileptr=None,
               translate=True, cnf=None, **kw):
    cnf = merge_cnf(cnf, kw)
    fig_doc = FIG_Presenter(appdata, cnf)
    fig_doc.load(filename, fileptr)
    if translate:
        sk2_doc = SK2_Presenter(appdata, cnf)
        if filename:
            sk2_doc.doc_file = filename
        fig_doc.translate_to_sk2(sk2_doc)
        fig_doc.close()
        return sk2_doc
    return fig_doc


def fig_saver(sk2_doc, filename=None, fileptr=None,
              translate=True, cnf=None, **kw):
    cnf = merge_cnf(cnf, kw)
    if sk2_doc.cid == uc2const.FIG:
        translate = False
    if translate:
        fig_doc = FIG_Presenter(sk2_doc.appdata, cnf)
        doc_file = filename or fileptr and fileptr.name
        fig_doc.doc_file = doc_file
        name = os.path.basename(doc_file)
        fig_doc.doc_id = os.path.splitext(name)[0]
        fig_doc.translate_from_sk2(sk2_doc)
        fig_doc.save(filename, fileptr)
        fig_doc.close()
    else:
        sk2_doc.save(filename, fileptr)


def check_fig(path):
    file_size = os.path.getsize(path)
    fileptr = get_fileptr(path)
    magic = '#FIG 3'

    if file_size > len(magic):
        string = fileptr.read(len(magic))
    else:
        string = fileptr.read()

    fileptr.close()
    return string.startswith(magic)
