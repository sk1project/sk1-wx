# -*- coding: utf-8 -*-
#
#	Copyright (C) 2016 by Igor E. Novikov
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

import cairo
import wx
import wal


from uc2 import uc2const
from uc2.formats.sk2 import crenderer
from sk1 import _

class SK1_Printout(wx.Printout):

	def __init__(self, doc):
		self.app = doc.app
		self.doc = doc
		wx.Printout.__init__(self)
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

	def HasPage(self, page):
		if page <= len(self.pages): return True
		else: return False

	def GetPageInfo(self):
		return (1, len(self.pages), 1, len(self.pages))

	def OnPrintPage(self, page):
		page_objs = self.pages[page - 1]
		dc = self.GetDC()
		w, h = dc.GetSizeTuple()
		pw, ph = self.GetPageSizeMM()
		print 'PPI', self.GetPPIPrinter()
		print 'DC', w, h
		print 'Page', pw, ph
		pw *= uc2const.mm_to_pt
		ph *= uc2const.mm_to_pt
		trafo = (w / pw, 0, 0, -h / ph, w / 2.0, h / 2.0)

		canvas_matrix = cairo.Matrix(*trafo)
		surface = cairo.ImageSurface(cairo.FORMAT_RGB24, int(w), int(h))
		ctx = cairo.Context(surface)
		ctx.set_matrix(canvas_matrix)
		ctx.set_source_rgb(1, 1, 1)
		ctx.paint()

		rend = crenderer.CairoRenderer(self.doc.cms)
		rend.render(ctx, page_objs)

		bmp = wal.copy_surface_to_bitmap(surface)
#		dc.DrawBitmap(bmp, 0, 0, False)
		return True

def create_print_data():
	print_data = wx.PrintData()
	print_data.SetPaperId(wx.PAPER_A4)
	print_data.SetPrintMode(wx.PRINT_MODE_PRINTER)
	return print_data

def get_print_data(app):
	if app.print_data is None:
		app.print_data = create_print_data()
	return app.print_data

def print_dlg(parent, presenter):
	app = presenter.app
	printout = SK1_Printout(presenter)
	printout2 = SK1_Printout(presenter)
	data = wx.PrintDialogData(get_print_data(app))
	preview = wx.PrintPreview(printout, printout2, data)
	title = '[%s] - ' % presenter.doc_name + _('Print Preview')
	frame = wx.PreviewFrame(preview, parent, title, size=wx.Size(600, 650))
	frame.Initialize()
	frame.CenterOnParent()
	preview.GetCanvas().SetBackgroundColour(wal.DARK_GRAY)
	frame.Show(True)

def print_setup_dlg(parent, app):
	data = wx.PageSetupDialogData(get_print_data(app))
	data.CalculatePaperSizeFromId()
	dlg = wx.PageSetupDialog(parent, data)
	dlg.ShowModal()
	app.print_data = wx.PrintData(dlg.GetPageSetupData().GetPrintData())
	dlg.Destroy()
