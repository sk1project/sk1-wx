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

PRINT_ALL = 0
PRINT_SELECTION = 1
PRINT_CURRENT_PAGE = 2
PRINT_PAGE_RANGE = 4

class Printout(object):

	app = None
	doc = None
	pages = []
	current_page = []
	selection = None
	reverse_flag = False
	print_range = PRINT_ALL
	page_range = []

	def __init__(self, doc):
		self.app = doc.app
		self.doc = doc
		self.pages, self.current_page = self.collect_pages(doc)
		if self.app.insp.is_selection():
			self.selection = self.doc.selection.objs

	def collect_pages(self, doc):
		pages = []
		cur_page = []
		mtds = doc.methods
		active_page = self.doc.active_page
		for item in mtds.get_pages():
			page = []
			for layer in item.childs:
				if mtds.is_layer_printable(layer):
					page += layer.childs
			pages.append(page)
			if item == active_page:
				cur_page = page
		return pages, cur_page

	def is_selection(self): return bool(self.selection)
	def get_num_pages(self): return len(self.pages)

	def get_units(self):
		return self.doc.model.doc_units

	def get_num_print_pages(self):
		if self.print_range == PRINT_ALL:
			return len(self.pages)
		elif self.print_range in (PRINT_SELECTION, PRINT_CURRENT_PAGE):
			return 1
		return len(self.page_range)

	def set_print_range(self, print_range, page_range=[]):
		self.print_range = print_range
		self.page_range = page_range

	def set_reverse(self, val): self.reverse_flag = val
