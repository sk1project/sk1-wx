# -*- coding: utf-8 -*-
#
#	Copyright (C) 2013-2015 by Igor E. Novikov
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


import wal

from uc2 import uc2const
from sk1 import _, config

class GotoPageDialog(wal.OkCancelDialog):

	presenter = None

	def __init__(self, parent, title, presenter):
		self.presenter = presenter
		wal.OkCancelDialog.__init__(self, parent, title, style=wal.HORIZONTAL)

	def build(self):
		label = wal.Label(self, _("Page No.:"))
		self.pack(label, padding=5)

		pages = self.presenter.get_pages()
		page_num = len(pages)
		current_page = pages.index(self.presenter.active_page) + 1

		self.spin = wal.FloatSpin(self, current_page, (1, page_num), 1, 0,
								width=5, spin_overlay=config.spin_overlay)
		self.pack(self.spin, padding=5)

	def get_result(self):
		return self.spin.get_value() - 1

def goto_page_dlg(parent, presenter):
	dlg = GotoPageDialog(parent, _("Go to page"), presenter)
	return dlg.show()

class DeletePageDialog(wal.OkCancelDialog):

	presenter = None

	def __init__(self, parent, title, presenter):
		self.presenter = presenter
		wal.OkCancelDialog.__init__(self, parent, title, style=wal.HORIZONTAL)

	def build(self):
		label = wal.Label(self, _("Delete page No.:"))
		self.pack(label, padding=5)

		pages = self.presenter.get_pages()
		page_num = len(pages)
		current_page = pages.index(self.presenter.active_page) + 1

		self.spin = wal.FloatSpin(self, current_page, (1, page_num), 1, 0,
								width=5, spin_overlay=config.spin_overlay)
		self.pack(self.spin, padding=5)

	def get_result(self):
		return self.spin.get_value() - 1


def delete_page_dlg(parent, presenter):
	dlg = DeletePageDialog(parent, _("Delete page"), presenter)
	return dlg.show()

class InsertPageDialog(wal.OkCancelDialog):

	presenter = None
	page_num = None
	before_opt = None
	after_opt = None
	page_index = None

	def __init__(self, parent, title, presenter):
		self.presenter = presenter
		wal.OkCancelDialog.__init__(self, parent, title)

	def build(self):

		panel = wal.HPanel(self)
		self.pack(panel, padding=5, fill=True)

		label = wal.Label(panel, _("Insert:"))
		panel.pack(label, padding=5)

		self.page_num = wal.FloatSpin(panel, 1, (1, 100), 1, 0, width=5,
							spin_overlay=config.spin_overlay)
		panel.pack(self.page_num, padding=5)

		label = wal.Label(panel, _("page(s)"))
		panel.pack(label, padding=5)

		panel = wal.HPanel(self)
		self.pack(panel, padding=5)

		margin = 0
		if not wal.is_gtk():margin = 3

		panel.pack((5, 5))
		vpanel = wal.VPanel(panel)
		panel.pack(vpanel, padding=5)
		self.before_opt = wal.Radiobutton(vpanel, _('Before'), group=True)
		vpanel.pack(self.before_opt, padding=margin, fill=True)
		self.after_opt = wal.Radiobutton(vpanel, _('After'))
		vpanel.pack(self.after_opt, padding=margin, fill=True)

		self.after_opt.set_value(True)

		label = wal.Label(panel, _("page No.:"))
		panel.pack(label, padding=5)

		pages = self.presenter.get_pages()
		page_num = len(pages)
		current_page = pages.index(self.presenter.active_page) + 1

		self.page_index = wal.FloatSpin(panel, current_page, (1, page_num),
							1, 0, width=5, spin_overlay=config.spin_overlay)
		panel.pack(self.page_index, padding=5)

	def get_result(self):
		number = self.page_num.get_value()
		target = self.page_index.get_value() - 1
		position = uc2const.BEFORE
		if self.after_opt.get_value():position = uc2const.AFTER
		return (number, target, position)

def insert_page_dlg(parent, presenter):
	dlg = InsertPageDialog(parent, _("Insert page"), presenter)
	return dlg.show()
