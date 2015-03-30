# -*- coding: utf-8 -*-
#
#	Copyright (C) 2012 by Igor E. Novikov
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys

from uc2 import events, msgconst
from uc2.formats.riff.presenter import RIFF_Presenter
from uc2.formats.generic_filters import get_fileptr

def riff_loader(appdata, filename=None, fileptr=None, translate=True, cnf={}, **kw):
	if kw: cnf.update(kw)
	doc = RIFF_Presenter(appdata, cnf)
	doc.load(filename, fileptr)
	return doc

def riff_saver(riff_doc, filename=None, fileptr=None, translate=True, cnf={}, **kw):
	if kw: cnf.update(kw)
	riff_doc.save(filename, fileptr)

def check_riff(path):
	fileptr = get_fileptr(path)
	fourcc = fileptr.read(4)
	fileptr.close()
	return fourcc == 'RIFF'
