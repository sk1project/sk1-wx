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

from uc2 import _

import os
import sys

from uc2 import _, events, msgconst
from uc2.formats.skp.skp_presenter import SKP_Presenter

def skp_loader(appdata, filename, translate=True, cnf={}, **kw):
	if kw: cnf.update(kw)
	doc = SKP_Presenter(appdata, cnf)
	doc.load(filename)
	return doc

def skp_saver(sk2_doc, filename, translate=True, cnf={}, **kw):
	if kw: cnf.update(kw)
	sk2_doc.save(filename)

def check_skp(path):
	try:
		fileptr = open(path, 'rb')
	except:
		errtype, value, traceback = sys.exc_info()
		msg = _('Cannot open %s file for reading') % (path)
		events.emit(events.MESSAGES, msgconst.ERROR, msg)
		raise IOError(errtype, msg + '\n' + value, traceback)

	string = fileptr.read(13)
	fileptr.close()
	if string == '##sK1 palette': return True
	return False

