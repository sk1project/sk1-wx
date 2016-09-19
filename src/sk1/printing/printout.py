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

import cairo
import wx

from uc2 import uc2const
from sk1.printing import prn_events
from sk1.printing.printrend import PrintRenderer

class PrnPage(object):

	childs = []

	def __init__(self, childs=[]):
		self.childs = []
		self.childs.append(TrafoGroup(childs))

class TrafoGroup(object):

	childs = []
	trafo = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]

	def __init__(self, childs=[]):
		self.childs = childs


PRINT_ALL = 0
PRINT_SELECTION = 1
PRINT_CURRENT_PAGE = 2
PRINT_PAGE_RANGE = 4

class Printout(wx.Printout):

	app = None
	doc = None
	pages = []
	current_page = []
	selection = None
	reverse_flag = False
	print_range = PRINT_ALL
	page_range = []
	print_pages = []

	def __init__(self, doc):
		self.app = doc.app
		self.doc = doc
		self.pages, self.current_page = self.collect_pages(doc)
		if self.app.insp.is_selection():
			self.selection = self.doc.selection.objs
		wx.Printout.__init__(self)
		self.renderer = PrintRenderer(self.get_cms())

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

	def get_cms(self):
		return self.doc.cms

	def get_num_print_pages(self):
		if self.print_range == PRINT_ALL:
			return len(self.pages)
		elif self.print_range in (PRINT_SELECTION, PRINT_CURRENT_PAGE):
			return 1
		return len(self.page_range)

	def _make_print_pages(self):
		self.print_pages = []
		if self.print_range == PRINT_ALL:
			for item in self.pages:
				self.print_pages.append(PrnPage(item))
		elif self.print_range == PRINT_SELECTION:
			self.print_pages.append(PrnPage(self.selection))
		elif self.print_range == PRINT_CURRENT_PAGE:
			self.print_pages.append(PrnPage(self.current_page))
		elif self.print_range == PRINT_PAGE_RANGE:
			for index in self.page_range:
				self.print_pages.append(PrnPage(self.pages[index]))

		if self.reverse_flag:
			self.print_pages.reverse()

	def set_print_range(self, print_range, page_range=[]):
		self.print_range = print_range
		self.page_range = page_range
		self.print_pages = []
		prn_events.emit(prn_events.PRINTOUT_MODIFIED)

	def set_reverse(self, val):
		if not self.reverse_flag == val:
			self.reverse_flag = val
			self.print_pages = []
			prn_events.emit(prn_events.PRINTOUT_MODIFIED)

	def get_print_pages(self):
		if not self.print_pages:
			self._make_print_pages()
		return self.print_pages

	#--- wx framework related methods

	def HasPage(self, page):
		if page <= self.get_num_print_pages(): return True
		else: return False

	def GetPageInfo(self):
		val = self.get_num_print_pages()
		return (1, val, 1, val)

	def OnPrintPage(self, page):
		page_obj = self.get_print_pages()[page - 1]
		dc = self.GetDC()
		w, h = dc.GetSizeTuple()
		pw, ph = self.GetPageSizeMM()
		print 'PPI', self.GetPPIPrinter()
		print 'DC', w, h
		print 'Page', pw, ph
		pw *= uc2const.mm_to_pt
		ph *= uc2const.mm_to_pt

		trafo = (w / pw, 0, 0, -h / ph, w / 2.0, h / 2.0)
		matrix = cairo.Matrix(*trafo)

		surface = cairo.Win32PrintingSurface(dc.GetHDC())
		ctx = cairo.Context(surface)
		ctx.set_matrix(matrix)

		for group in page_obj.childs:
			self.renderer.render(ctx, group.childs)

		return True

