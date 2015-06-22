# -*- coding: utf-8 -*-
#
#	Copyright (C) 2015 by Igor E. Novikov
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

from uc2 import _, events, msgconst, uc2const
from uc2.formats.skp.skp_presenter import SKP_Presenter
from uc2.formats.skp.skp_const import SKP_ID
from uc2.formats.generic_filters import get_fileptr
from uc2.formats.sk2.sk2_presenter import SK2_Presenter

def skp_loader(appdata, filename=None, fileptr=None, translate=True,
			convert=False, cnf={}, **kw):
	if kw: cnf.update(kw)
	doc = SKP_Presenter(appdata, cnf)
	doc.load(filename, fileptr)
	if translate:
		sk2_doc = SK2_Presenter(appdata, cnf)
		doc.translate_to_sk2(sk2_doc)
		doc.close()
		return sk2_doc
	return doc

def skp_saver(doc, filename=None, fileptr=None, translate=True,
			convert=False, cnf={}, **kw):
	if kw: cnf.update(kw)
	if translate:
		skp_doc = SKP_Presenter(doc.appdata, cnf)
		skp_doc.translate_from_sk2(doc)
		skp_doc.save(filename, fileptr)
		skp_doc.close()
	else:
		doc.save(filename, fileptr)

def check_skp(path):
	fileptr = get_fileptr(path)
	string = fileptr.read(len(SKP_ID))
	fileptr.close()
	return string == SKP_ID

