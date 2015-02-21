# -*- coding: utf-8 -*-
#
#	Copyright (C) 2013-2014 by Igor E. Novikov
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

from wal import const, EXPAND, ALL, LEFT, CENTER
from wal import HPanel, VPanel, Notebook, Label, HtmlLabel
from wal import Entry

from sk1 import _
from sk1.resources import icons
from sk1.dialogs.license import LICENSE
from sk1.dialogs.credits import CREDITS

class PDAboutDialog(wx.Dialog):

	sizer = None
	app = None

	def __init__(self, app, parent, title, size=(500, 350)):
		self.app = app
		if const.is_mac(): size = (550, 400)
		wx.Dialog.__init__(self, parent, -1, title, wx.DefaultPosition, size)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.sizer)

		margin = 5
		if not const.is_gtk(): margin = 10

		self.box = VPanel(self, space=margin)
		self.sizer.Add(self.box, 1, ALL | EXPAND)

		header = AboutHeader(self.app, self.box)
		self.box.add(header, 0, ALL | EXPAND, 5)

		nb = Notebook(self.box)
		nb.add_page(AboutPage(self.app, nb), _('About'))
		nb.add_page(ComponentsPage(self.app, nb), _('Components'))
		nb.add_page(AuthorsPage(nb), _('Authors'))
		nb.add_page(ThanksPage(nb), _('Thanks to'))
		nb.add_page(LicensePage(nb), _('License'))
		self.box.add(nb, 1, ALL | EXPAND, 5)


class AboutHeader(HPanel):

	def __init__(self, app, parent):
		HPanel.__init__(self, parent)
		self.set_bg(const.UI_COLORS['pressed_border'])

		panel = HPanel(self)
		color = const.lighter_color(const.UI_COLORS['bg'], 0.9)
		panel.set_bg(color)
		bmp = wx.ArtProvider.GetBitmap(icons.PDESIGN_ICON32, size=const.DEF_SIZE)
		bitmap = wx.StaticBitmap(panel, -1, bmp)
		panel.add(bitmap, 0, ALL, 5)

		data = app.appdata

		p = VPanel(panel)
		p.set_bg(color)
		p.add(Label(p, data.app_name, True, 3), 0, ALL | EXPAND, 0)
		txt = ('%s: %s %s') % (_('Version'), data.version, data.revision)
		p.add(Label(p, txt), 0, ALL | EXPAND, 0)
		panel.add(p, 0, LEFT | CENTER, 0)

		self.add(panel, 1, ALL | EXPAND, 1)

class AboutPage(HPanel):

	def __init__(self, app, parent):
		HPanel.__init__(self, parent)
		self.add((50, 10))
		box = VPanel(self)
		self.add(box, 0, LEFT | CENTER, 5)
		data = app.appdata
		txt = data.app_name + ' - ' + _('vector graphics editor') + '\n'
		box.add(Label(box, txt, True, 2))
		import datetime
		year = str(datetime.date.today().year)
		txt = '(C) 2011-' + year + ' sK1 Project team' + '\n'
		box.add(Label(box, txt))
		box.add(HtmlLabel(box, 'http://sk1project.org'))

class ComponentsPage(VPanel):

	def __init__(self, app, parent):
		odd_color = wx.Colour(240, 240, 240)
		VPanel.__init__(self, parent)
		lc = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
		lc.InsertColumn(0, _('Library'))
		lc.InsertColumn(1, _('Version'))
		data = app.appdata.components
		i = 0
		odd = False
		for item in data:
			lc.Append(item)
			if odd:
				item = lc.GetItem(i)
				item.SetBackgroundColour(odd_color)
				lc.SetItem(item)
			odd = not odd
			i += 1

		self.add(lc, 1, EXPAND, 5)
		lc.SetColumnWidth(0, wx.LIST_AUTOSIZE)
		lc.SetColumnWidth(1, 500)

class AuthorsPage(VPanel):

	def __init__(self, parent):
		VPanel.__init__(self, parent)
		sep = "------------------------------\n"
		dev = "\nIgor E. Novikov\n"
		dev += "(sK1 2.0, wxWidgets version; sK1, Tk version)\n"
		dev += "<igor.e.novikov@gmail.com>\n\n" + sep
		dev += 'sK1 2.0 is based on sK1 0.9.x and Skencil 0.6.x experience.'
		dev += '\n' + sep
		dev += "Bernhard Herzog (Skencil, Tk version)\n"
		dev += "<bernhard@users.sourceforge.net>\n" + sep
		entry = Entry(self, dev, multiline=True, editable=False)
		self.add(entry, 1, ALL | EXPAND, 5)

class ThanksPage(VPanel):

	def __init__(self, parent):
		VPanel.__init__(self, parent)
		entry = Entry(self, CREDITS, multiline=True, editable=False)
		self.add(entry, 1, ALL | EXPAND, 5)

class LicensePage(VPanel):

	def __init__(self, parent):
		VPanel.__init__(self, parent)
		entry = Entry(self, LICENSE, multiline=True, editable=False)
		self.add(entry, 1, ALL | EXPAND, 5)

def about_dialog(app, parent):
	title = _('About') + ' ' + app.appdata.app_name
	dlg = PDAboutDialog(app, parent, title)
	dlg.Centre()
	dlg.ShowModal()
	dlg.Destroy()
