# -*- coding: utf-8 -*-
#
#	Copyright (C) 2013 by Igor E. Novikov
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
from uc2.formats.sk1 import model
from uc2.formats.sk1.presenter import SK1_Presenter
from uc2.formats.pdxf.presenter import PDXF_Presenter

def sk1_loader(appdata, filename, translate=True, cnf={}, **kw):
	if kw: cnf.update(kw)
	doc = SK1_Presenter(appdata, cnf)
	doc.load(filename)
	if translate:
		pdxf_doc = PDXF_Presenter(appdata, cnf)
		pdxf_doc.doc_file = filename
		doc.traslate_to_pdxf(pdxf_doc)
		doc.close()
		doc = pdxf_doc
	return doc

def sk1_saver(pdxf_doc, filename, translate=True, cnf={}, **kw):
	if kw: cnf.update(kw)
	sk1_doc = SK1_Presenter(pdxf_doc.appdata, cnf)
	sk1_doc.traslate_from_pdxf(pdxf_doc)
	sk1_doc.save(filename)
	sk1_doc.close()

def check_sk1(path):
	try:
		file = open(path, 'rb')
	except:
		errtype, value, traceback = sys.exc_info()
		msg = _('Cannot open %s file for reading') % (path)
		events.emit(events.MESSAGES, msgconst.ERROR, msg)
		raise IOError(errtype, msg + '\n' + value, traceback)

	string = file.read(5)

	file.close()
	if string == '##sK1': return True
	return False
