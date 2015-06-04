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

from uc2.formats.generic_filters import get_fileptr
from uc2.formats.jcw.jcw_const import JCW_ID
from uc2.formats.jcw.jcw_presenter import JCW_Presenter
from uc2.formats.skp.skp_presenter import SKP_Presenter
from uc2.formats.sk2.sk2_presenter import SK2_Presenter

def jcw_loader(appdata, filename=None, fileptr=None, translate=True,
			convert=False, cnf={}, **kw):
	if kw: cnf.update(kw)
	doc = JCW_Presenter(appdata, cnf)
	doc.load(filename, fileptr)
	if convert:
		skp_doc = SKP_Presenter(appdata, cnf)
		doc.convert_to_skp(skp_doc)
		doc.close()
		return skp_doc
	if translate:
		skp_doc = SKP_Presenter(appdata, cnf)
		doc.convert_to_skp(skp_doc)
		sk2_doc = SK2_Presenter(appdata, cnf)
		skp_doc.translate_to_sk2(sk2_doc)
		doc.close()
		skp_doc.close()
		return sk2_doc
	return doc

def jcw_saver(doc, filename=None, fileptr=None, translate=True,
			convert=False, cnf={}, **kw):
	if kw: cnf.update(kw)
	appdata = doc.appdata
	if translate:
		skp_doc = SKP_Presenter(appdata, cnf)
		skp_doc.translate_from_sk2(doc)
		jcw_doc = JCW_Presenter(appdata, cnf)
		jcw_doc.convert_from_skp(skp_doc)
		jcw_doc.save(filename, fileptr)
		jcw_doc.close()
		skp_doc.close()
	elif convert:
		jcw_doc = JCW_Presenter(appdata, cnf)
		jcw_doc.convert_from_skp(doc)
		jcw_doc.save(filename, fileptr)
		jcw_doc.close()
	else:
		doc.save(filename, fileptr)

def check_jcw(path):
	fileptr = get_fileptr(path)
	string = fileptr.read(len(JCW_ID))
	fileptr.close()
	return string == JCW_ID