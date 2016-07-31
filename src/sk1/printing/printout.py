# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2016 by Igor E. Novikov
#
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
#
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
#
# 	You should have received a copy of the GNU General Public License
# 	along with this program.  If not, see <http://www.gnu.org/licenses/>.

class PrnGroup(object):

	childs = []
	trafo = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]


class Printout(object):

	app = None
	doc = None
	pages = []
	print_pages = []

	def __init__(self, doc):
		self.app = doc.app
		self.doc = doc
		self.pages = self.collect_pages(doc)

	def collect_pages(self, doc):
		pages = []
		mtds = doc.methods
		for item in mtds.get_pages():
			page = []
			for layer in item.childs:
				if mtds.is_layer_printable(layer):
					page += layer.childs
			pages.append(page)
		return pages

	def is_selection(self): return False
	def get_num_pages(self): return 1
