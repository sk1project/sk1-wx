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

import os
import sys

from uc2 import _, events, msgconst
from uc2.formats.plt.plt_presenter import PLT_Presenter
from uc2.formats.sk2.sk2_presenter import SK2_Presenter
from uc2.formats.generic_filters import get_fileptr

def plt_loader(appdata, filename=None, fileptr=None, translate=True, cnf={}, **kw):
	if kw: cnf.update(kw)
	doc = PLT_Presenter(appdata, cnf)
	doc.load(filename)
	if translate:
		sk2_doc = SK2_Presenter(appdata, cnf)
		sk2_doc.doc_file = filename
		doc.translate_to_sk2(sk2_doc)
		doc.close()
		doc = sk2_doc
	return doc

def plt_saver(doc, filename=None, fileptr=None, translate=True, cnf={}, **kw):
	if kw: cnf.update(kw)
	if translate:
		plt_doc = PLT_Presenter(doc.appdata, cnf)
		plt_doc.translate_from_sk2(doc)
		plt_doc.save(filename)
		plt_doc.close()
	else:
		doc.save(filename)

def check_plt(path):
	file_size = os.path.getsize(path)
	fileptr = get_fileptr(path)

	if file_size > 200:
		string = fileptr.read(200)
	else:
		string = fileptr.read()

	fileptr.close()
	if len(string.split("IN;")) > 1 and len(string.split(";")) > 2:
		if len(string.split(";PD")) > 1:
			return True
	return False

