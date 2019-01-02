# -*- coding: utf-8 -*-
#
#  Copyright (C) 2018 by Igor E. Novikov
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

from uc2.formats.md.md_presenter import MdPresenter
from uc2.utils.mixutils import merge_cnf


def md_loader(appdata, filename=None, fileptr=None, translate=True, cnf=None,
               **kw):
    cnf = merge_cnf(cnf, kw)
    doc = MdPresenter(appdata, cnf)
    doc.load(filename, fileptr)
    return doc


def md_saver(doc, filename=None, fileptr=None, translate=True, cnf=None, **kw):
    doc.save(filename)


def check_md(path):
    return ".md" in path
