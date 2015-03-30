# -*- coding: utf-8 -*-
#
#	Copyright (C) 2011-2012 by Igor E. Novikov
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
from uc2.formats.cdr.cdr_presenter import CDR_Presenter
from uc2.formats.cdr import cdr_const
from uc2.formats.sk2.sk2_presenter import SK2_Presenter
from uc2.formats.generic_filters import get_fileptr

def cdr_loader(appdata, filename=None, fileptr=None, translate=True, cnf={}, **kw):
	if kw: cnf.update(kw)
	doc = CDR_Presenter(appdata, cnf)
	doc.load(filename)
	if translate:
		sk2_doc = SK2_Presenter(appdata, cnf)
		sk2_doc.doc_file = filename
		doc.traslate_to_sk2(sk2_doc)
		doc.close()
		doc = sk2_doc
	return doc

def cdr_saver(cdr_doc, filename=None, fileptr=None, translate=True, cnf={}, **kw):
	if kw: cnf.update(kw)
	cdr_doc.save(filename)

def check_cdr(path):
	fileptr = get_fileptr(path)
	header = fileptr.read(12)
	fileptr.close()
	if not header[:4] == 'RIFF': return False
	if header[8:] in cdr_const.CDR_VERSIONS: return True
	else: return False
