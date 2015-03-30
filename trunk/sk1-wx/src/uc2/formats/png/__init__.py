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
import cairo

from uc2 import _, events, msgconst
from uc2.formats.fallback import im_loader
from uc2.formats.sk2.crenderer import CairoRenderer

def png_loader(appdata, filename=None, fileptr=None, translate=True, cnf={}, **kw):
	return im_loader(appdata, filename, fileptr, translate, cnf, **kw)

def png_saver(sk2_doc, filename=None, fileptr=None, translate=True, cnf={}, **kw):
	if filename and not fileptr:
		try:
			fileptr = open(filename, 'wb')
		except:
			errtype, value, traceback = sys.exc_info()
			msg = _('Cannot open %s fileptr for writing') % (filename)
			events.emit(events.MESSAGES, msgconst.ERROR, msg)
			raise IOError(errtype, msg + '\n' + value, traceback)

	page = sk2_doc.methods.get_page()
	w, h = page.page_format[1]
	trafo = (1.0, 0, 0, -1.0, w / 2.0, h / 2.0)

	canvas_matrix = cairo.Matrix(*trafo)
	surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(w), int(h))
	ctx = cairo.Context(surface)
	ctx.set_matrix(canvas_matrix)

	rend = CairoRenderer(sk2_doc.cms)
	layers = sk2_doc.methods.get_visible_layers(page)
	objs = []
	for item in layers:objs += item.childs
	rend.render(ctx, objs)

	surface.write_to_png(fileptr)
	fileptr.close()


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
