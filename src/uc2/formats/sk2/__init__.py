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

from uc2 import _, events, msgconst
from uc2.formats.sk2.sk2_presenter import SK2_Presenter

def sk2_loader(appdata, filename=None, fileptr=None, translate=True, cnf={}, **kw):
	if kw: cnf.update(kw)
	doc = SK2_Presenter(appdata, cnf)
	doc.load(filename, fileptr)
	return doc

def sk2_saver(sk2_doc, filename=None, fileptr=None, translate=True, cnf={}, **kw):
	if kw: cnf.update(kw)
	sk2_doc.save(filename, fileptr)

def check_sk2(path):
	try:
		fileptr = open(path, 'rb')
	except:
		errtype, value, traceback = sys.exc_info()
		msg = _('Cannot open %s file for reading') % (path)
		events.emit(events.MESSAGES, msgconst.ERROR, msg)
		raise IOError(errtype, msg + '\n' + value, traceback)

	string = fileptr.read(7)
	fileptr.close()
	if string == '##sK1 2': return True
	return False
