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


def plt_loader(appdata, filename, translate=True, cnf={}, **kw):
	if kw: cnf.update(kw)
	doc = PLT_Presenter(appdata, cnf)
	doc.load(filename)
	if translate:
		sk2_doc = SK2_Presenter(appdata, cnf)
		sk2_doc.doc_file = filename
		doc.traslate_to_sk2(sk2_doc)
		doc.close()
		doc = sk2_doc
	return doc

def plt_saver(doc, filename, translate=True, cnf={}, **kw):
	if kw: cnf.update(kw)
	if translate:
		print 'here'
		plt_doc = PLT_Presenter(doc.appdata, cnf)
		print 'here1'
		plt_doc.traslate_from_sk2(doc)
		print 'here2'
		plt_doc.save(filename)
		plt_doc.close()
	else:
		doc.save(filename)

def check_plt(path):
	file_size = os.path.getsize(path)

	try:
		fileptr = open(path, 'rb')
	except:
		errtype, value, traceback = sys.exc_info()
		msg = _('Cannot open %s fileptr for reading') % (path)
		events.emit(events.MESSAGES, msgconst.ERROR, msg)
		raise IOError(errtype, msg + '\n' + value, traceback)

	if file_size > 200:
		string = fileptr.read(200)
	else:
		string = fileptr.read()

	fileptr.close()
	if len(string.split("IN;")) > 1 and len(string.split(";")) > 2:
		if len(string.split(";PD")) > 1:
			return True
	return False

