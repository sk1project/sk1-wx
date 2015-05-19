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

from uc2.formats.xml_.xml_presenter import XML_Presenter

def xml_loader(appdata, filename=None, fileptr=None, translate=False,
			convert=False, cnf={}, **kw):
	if kw: cnf.update(kw)
	doc = XML_Presenter(appdata, cnf)
	doc.load(filename, fileptr)
	return doc

def xml_saver(doc, filename=None, fileptr=None, translate=False,
			convert=False, cnf={}, **kw):
	if kw: cnf.update(kw)
	doc.save(filename, fileptr)

def check_xml(path):
	fileptr = get_fileptr(path)
	ret = False
	i = 0
	while i < 20:
		line = fileptr.readline()
		if not line.find('<?xml ') == -1:
			ret = True
			break
		i += 1
	fileptr.close()
	return ret
