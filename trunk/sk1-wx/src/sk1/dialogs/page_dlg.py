# -*- coding: utf-8 -*-
#
#	Copyright (C) 2013 by Igor E. Novikov
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

import wx

from uc2 import uc2const

from sk1 import _, config
from sk1.widgets import ALL, VERTICAL, const
from sk1.widgets import Label, FloatSpin, HPanel, VPanel, Radiobutton
from generic import GenericDialog

class GotoPageDialog(GenericDialog):

	presenter = None

	def __init__(self, parent, title, presenter):
		self.presenter = presenter
		GenericDialog.__init__(self, parent, title)

	def build(self):
		label = Label(self, _("Page No.:"))
		self.box.add(label, 0, wx.ALIGN_CENTER_VERTICAL | ALL, 5)

		pages = self.presenter.get_pages()
		page_num = len(pages)
		current_page = pages.index(self.presenter.active_page) + 1

		self.spin = FloatSpin(self, current_page, (1, page_num), 1, 0, width=5,
							spin_overlay=config.spin_overlay)
		self.box.add(self.spin, 0, wx.ALIGN_CENTER_VERTICAL | ALL, 5)

	def get_result(self):
		return self.spin.get_value() - 1

def goto_page_dlg(parent, presenter):
	ret = None
	dlg = GotoPageDialog(parent, _("Go to page"), presenter)
	dlg.Centre()
	if dlg.ShowModal() == wx.ID_OK: ret = dlg.get_result()
	dlg.Destroy()
	return ret

class DeletePageDialog(GenericDialog):

	presenter = None

	def __init__(self, parent, title, presenter):
		self.presenter = presenter
		GenericDialog.__init__(self, parent, title)

	def build(self):
		label = Label(self, _("Delete page No.:"))
		self.box.add(label, 0, wx.ALIGN_CENTER_VERTICAL | ALL, 5)

		pages = self.presenter.get_pages()
		page_num = len(pages)
		current_page = pages.index(self.presenter.active_page) + 1

		self.spin = FloatSpin(self, current_page, (1, page_num), 1, 0, width=5,
							spin_overlay=config.spin_overlay)
		self.box.add(self.spin, 0, wx.ALIGN_CENTER_VERTICAL | ALL, 5)

	def get_result(self):
		return self.spin.get_value() - 1


def delete_page_dlg(parent, presenter):
	ret = None
	dlg = DeletePageDialog(parent, _("Delete page"), presenter)
	dlg.Centre()
	if dlg.ShowModal() == wx.ID_OK: ret = dlg.get_result()
	dlg.Destroy()
	return ret

class InsertPageDialog(GenericDialog):

	presenter = None
	page_num = None
	before_opt = None
	after_opt = None
	page_index = None

	def __init__(self, parent, title, presenter):
		self.presenter = presenter
		GenericDialog.__init__(self, parent, title, style=VERTICAL)

	def build(self):

		panel = HPanel(self.box)
		self.box.add(panel, 0, ALL, 5)

		label = Label(panel, _("Insert:"))
		panel.add(label, 0, wx.ALIGN_CENTER_VERTICAL | ALL, 5)

		self.page_num = FloatSpin(panel, 1, (1, 100), 1, 0, width=5,
							spin_overlay=config.spin_overlay)
		panel.add(self.page_num, 0, wx.ALIGN_CENTER_VERTICAL | ALL, 5)

		label = Label(panel, _("page(s)"))
		panel.add(label, 0, wx.ALIGN_CENTER_VERTICAL | ALL, 5)

		panel = HPanel(self.box)
		self.box.add(panel, 0, ALL)

		margin = 0
		if not const.is_gtk():margin = 3

		panel.add((5, 5))
		vpanel = VPanel(panel)
		panel.add(vpanel, 0, wx.ALIGN_CENTER_VERTICAL | ALL, 5)
		self.before_opt = Radiobutton(vpanel, _('Before'), group=True)
		vpanel.add(self.before_opt, 0, ALL, margin)
		self.after_opt = Radiobutton(vpanel, _('After'))
		vpanel.add(self.after_opt, 0, ALL, margin)

		self.after_opt.set_value(True)

		label = Label(panel, _("page No.:"))
		panel.add(label, 0, wx.ALIGN_CENTER_VERTICAL | ALL, 5)

		pages = self.presenter.get_pages()
		page_num = len(pages)
		current_page = pages.index(self.presenter.active_page) + 1

		self.page_index = FloatSpin(panel, current_page, (1, page_num), 1, 0,
								width=5, spin_overlay=config.spin_overlay)
		panel.add(self.page_index, 0, wx.ALIGN_CENTER_VERTICAL | ALL, 5)

	def get_result(self):
		number = self.page_num.get_value()
		target = self.page_index.get_value() - 1
		position = uc2const.BEFORE
		if self.after_opt.get_value():position = uc2const.AFTER
		return (number, target, position)

def insert_page_dlg(parent, presenter):
	ret = ()
	dlg = InsertPageDialog(parent, _("Insert page"), presenter)
	dlg.Centre()
	if dlg.ShowModal() == wx.ID_OK: ret = dlg.get_result()
	dlg.Destroy()
	return ret
