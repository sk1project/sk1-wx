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
from uc2.formats.generic_filters import get_fileptr

PNG_ID = '\x89\x50\x4e\x47'

def png_loader(appdata, filename=None, fileptr=None, translate=True, cnf={}, **kw):
	return im_loader(appdata, filename, fileptr, translate, cnf, **kw)

def png_saver(sk2_doc, filename=None, fileptr=None, translate=True, cnf={}, **kw):
	if filename and not fileptr:
		fileptr = get_fileptr(filename, True)
	page = sk2_doc.methods.get_page()
	w, h = page.page_format[1]
	trafo = (1.0, 0, 0, -1.0, w / 2.0, h / 2.0)

	canvas_matrix = cairo.Matrix(*trafo)
	surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(w), int(h))
	ctx = cairo.Context(surface)
	ctx.set_matrix(canvas_matrix)

	rend = CairoRenderer(sk2_doc.cms)
	antialias_flag = True
	if 'antialiasing' in kw.keys():
		if not kw['antialiasing'] in ('True', '1'):
			antialias_flag = False
	rend.antialias_flag = antialias_flag
	layers = sk2_doc.methods.get_visible_layers(page)

	for item in layers:
		if not item.properties[3] and antialias_flag:
			rend.antialias_flag = False
		rend.render(ctx, item.childs)
		if not item.properties[3] and antialias_flag:
			rend.antialias_flag = True

	surface.write_to_png(fileptr)
	fileptr.close()

def check_png(path):
	fileptr = get_fileptr(path)
	mstr = fileptr.read(len(PNG_ID))
	fileptr.close()
	if mstr == PNG_ID: return True
	return False
