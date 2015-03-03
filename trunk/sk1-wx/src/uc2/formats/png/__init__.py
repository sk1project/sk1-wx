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

import sys

from uc2 import _, events, msgconst
from uc2.formats.fallback import im_loader

def png_loader(appdata, filename, translate=True, cnf={}, **kw):
	return im_loader(appdata, filename, translate, cnf, **kw)

def png_saver(doc, filename, translate=True, cnf={}, **kw):
	pass

def check_png(path):
	try:
		fileptr = open(path, 'rb')
	except:
		errtype, value, traceback = sys.exc_info()
		msg = _('Cannot open %s fileptr for reading') % (path)
		events.emit(events.MESSAGES, msgconst.ERROR, msg)
		raise IOError(errtype, msg + '\n' + value, traceback)

	mstr = fileptr.read(4)[1:]
	fileptr.close()
	if mstr == 'PNG': return True
	return False
