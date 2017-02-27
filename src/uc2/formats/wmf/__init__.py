# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2013 by Igor E. Novikov
#
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
#
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
#
# 	You should have received a copy of the GNU General Public License
# 	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys

from uc2.formats.generic_filters import get_fileptr
from uc2 import uc2const
from uc2.formats.wmf.wmfconst import WMF_SIGNATURE, METAFILETYPES, METAVERSIONS
from uc2.formats.wmf.wmf_presenter import WMF_Presenter
from uc2.formats.sk2.sk2_presenter import SK2_Presenter


def wmf_loader(appdata, filename=None, fileptr=None,
			   translate=True, cnf={}, **kw):
	if kw: cnf.update(kw)
	wmf_doc = WMF_Presenter(appdata, cnf)
	wmf_doc.load(filename, fileptr)
	if translate:
		sk2_doc = SK2_Presenter(appdata, cnf)
		if filename: sk2_doc.doc_file = filename
		wmf_doc.translate_to_sk2(sk2_doc)
		wmf_doc.close()
		return sk2_doc
	return wmf_doc

def wmf_saver(sk2_doc, filename=None, fileptr=None,
			 translate=True, cnf={}, **kw):
	if kw: cnf.update(kw)
	if sk2_doc.cid == uc2const.WMF: translate = False
	if translate:
		wmf_doc = WMF_Presenter(sk2_doc.appdata, cnf)
		try:
			wmf_doc.translate_from_sk2(sk2_doc)
		except:
			for item in sys.exc_info(): print item
		wmf_doc.save(filename, fileptr)
		wmf_doc.close()
	else:
		sk2_doc.save(filename, fileptr)

def check_wmf(path):
	fileptr = get_fileptr(path)
	sign = fileptr.read(len(WMF_SIGNATURE))
	fileptr.seek(0)
	metatype = fileptr.read(2)
	fileptr.read(2)
	metaver = fileptr.read(2)
	fileptr.close()
	if sign == WMF_SIGNATURE: return True
	if metatype in METAFILETYPES and metaver in METAVERSIONS: return True
	return False
