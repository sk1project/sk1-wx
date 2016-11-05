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
import xml.etree.cElementTree as et

from uc2 import _, events, msgconst, uc2const

def svg_loader(appdata, filename=None, fileptr=None,
			   translate=True, cnf={}, **kw):
	pass

def sk_saver(sk2_doc, filename=None, fileptr=None,
			 translate=True, cnf={}, **kw):
	pass

def check_svg(path):
	tag = None
	with open(path, "r") as f:
		try:
			for event, el in et.iterparse(f, ('start',)):
				tag = el.tag
				break
		except et.ParseError:
			pass
	return tag == '{http://www.w3.org/2000/svg}svg'
