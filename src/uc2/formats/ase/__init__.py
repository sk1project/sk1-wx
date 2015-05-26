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
from uc2.formats.ase.ase_const import ASEF
from uc2.formats.ase.ase_presenter import ASE_Presenter
from uc2.formats.skp.skp_presenter import SKP_Presenter
from uc2.formats.sk2.sk2_presenter import SK2_Presenter

def ase_loader(appdata, filename=None, fileptr=None, translate=True,
			convert=False, cnf={}, **kw):
	if kw: cnf.update(kw)
	doc = ASE_Presenter(appdata, cnf)
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

def ase_saver(doc, filename=None, fileptr=None, translate=True,
			convert=False, cnf={}, **kw):
	if kw: cnf.update(kw)
	appdata = doc.appdata
	if translate:
		skp_doc = SKP_Presenter(appdata, cnf)
		skp_doc.translate_from_sk2(doc)
		gpl_doc = ASE_Presenter(appdata, cnf)
		gpl_doc.convert_from_skp(skp_doc)
		gpl_doc.save(filename, fileptr)
		gpl_doc.close()
		skp_doc.close()
	elif convert:
		gpl_doc = ASE_Presenter(appdata, cnf)
		gpl_doc.convert_from_skp(doc)
		gpl_doc.save(filename, fileptr)
		gpl_doc.close()
	else:
		doc.save(filename, fileptr)

def check_ase(path):
	fileptr = get_fileptr(path)
	string = fileptr.read(len(ASEF))
	fileptr.close()
	return string == ASEF