# -*- coding: utf-8 -*-
#
# 	 Copyright (C) 2016 by Igor E. Novikov
#
# 	 This program is free software: you can redistribute it and/or modify
# 	 it under the terms of the GNU General Public License as published by
# 	 the Free Software Foundation, either version 3 of the License, or
# 	 (at your option) any later version.
#
# 	 This program is distributed in the hope that it will be useful,
# 	 but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	 GNU General Public License for more details.
#
# 	 You should have received a copy of the GNU General Public License
# 	 along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
from xml.etree import cElementTree

from uc2 import _, events, msgconst, uc2const
from uc2.formats.svg.svg_presenter import SVG_Presenter
from uc2.formats.sk2.sk2_presenter import SK2_Presenter


def svg_loader(appdata, filename=None, fileptr=None,
			   translate=True, cnf={}, **kw):
	if kw: cnf.update(kw)
	svg_doc = SVG_Presenter(appdata, cnf)
	svg_doc.load(filename, fileptr)
	if translate:
		sk2_doc = SK2_Presenter(appdata, cnf)
		if filename: sk2_doc.doc_file = filename
		svg_doc.translate_to_sk2(sk2_doc)
		svg_doc.close()
		return sk2_doc
	return svg_doc

def svg_saver(sk2_doc, filename=None, fileptr=None,
			 translate=True, cnf={}, **kw):
	if kw: cnf.update(kw)
	if sk2_doc.cid == uc2const.SVG: translate = False
	if translate:
		sk_doc = SVG_Presenter(sk2_doc.appdata, cnf)
		sk_doc.translate_from_sk2(sk2_doc)
		sk_doc.save(filename, fileptr)
		sk_doc.close()
	else:
		sk2_doc.save(filename, fileptr)

def check_svg(path):
	tag = None
	with open(path, "r") as f:
		try:
			for event, el in cElementTree.iterparse(f, ('start',)):
				tag = el.tag
				break
		except cElementTree.ParseError: pass
	return tag == '{http://www.w3.org/2000/svg}svg' or tag == 'svg'
