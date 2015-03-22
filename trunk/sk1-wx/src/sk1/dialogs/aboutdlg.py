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

import wal
from wal import const

from sk1 import _
from sk1.resources import icons, get_bmp
from sk1.dialogs.aboutdlg_license import LICENSE
from sk1.dialogs.aboutdlg_credits import CREDITS

class AboutDialog(wal.SimpleDialog):

	sizer = None
	app = None

	def __init__(self, app, parent, title, size=(500, 350)):
		self.app = app
		if wal.is_mac(): size = (550, 400)
		wal.SimpleDialog.__init__(self, parent, title, size)

	def build(self):
		header = AboutHeader(self.app, self)
		self.pack(header, fill=True, padding=5)

		nb = wal.Notebook(self)
		nb.add_page(AboutPage(self.app, nb), _('About'))
		nb.add_page(ComponentsPage(self.app, nb), _('Components'))
		nb.add_page(AuthorsPage(nb), _('Authors'))
		nb.add_page(ThanksPage(nb), _('Thanks to'))
		nb.add_page(LicensePage(nb), _('License'))
		self.pack(nb, expand=True, fill=True, padding=5)


class AboutHeader(wal.VPanel):

	def __init__(self, app, parent):
		wal.VPanel.__init__(self, parent)
		self.set_bg(const.UI_COLORS['pressed_border'])

		panel = wal.HPanel(self)
		color = const.lighter_color(const.UI_COLORS['bg'], 0.9)
		panel.set_bg(color)
		panel.pack(get_bmp(panel, icons.PDESIGN_ICON32), padding=5)

		data = app.appdata

		p = wal.VPanel(panel)
		p.set_bg(color)
		p.pack(wal.Label(p, data.app_name, True, 3), fill=True)
		txt = ('%s: %s %s') % (_('Version'), data.version, data.revision)
		p.pack(wal.Label(p, txt), fill=True)
		panel.pack(p)

		self.add(panel, 1, wal.ALL | wal.EXPAND , 1)

class AboutPage(wal.HPanel):

	def __init__(self, app, parent):
		wal.HPanel.__init__(self, parent)
		self.pack((50, 10))
		box = wal.VPanel(self)
		self.pack(box, padding=5)
		data = app.appdata
		txt = data.app_name + ' - ' + _('vector graphics editor') + '\n'
		box.pack(wal.Label(box, txt, True, 2), fill=True)
		import datetime
		year = str(datetime.date.today().year)
		txt = '(C) 2011-' + year + ' sK1 Project team' + '\n'
		box.pack(wal.Label(box, txt), fill=True)
		p = wal.HPanel(box)
		p.pack(wal.HtmlLabel(p, 'http://sk1project.org'))
		box.pack(p, fill=True)

class ComponentsPage(wal.VPanel):

	def __init__(self, app, parent):
		wal.VPanel.__init__(self, parent)
		data = [[_('Component'), _('Version')]] + app.appdata.components
		slist = wal.ReportList(self, data, border=False)
		self.pack(slist, expand=True, fill=True)
		slist.set_column_width(0, const.LIST_AUTOSIZE)

class AuthorsPage(wal.VPanel):

	def __init__(self, parent):
		wal.VPanel.__init__(self, parent)
		sep = "------------------------------\n"
		dev = "\nIgor E. Novikov\n"
		dev += "(sK1 2.0, wxWidgets version; sK1, Tk version)\n"
		dev += "<igor.e.novikov@gmail.com>\n\n" + sep
		dev += 'sK1 2.0 is based on sK1 0.9.x and Skencil 0.6.x experience.'
		dev += '\n' + sep
		dev += "Bernhard Herzog (Skencil, Tk version)\n"
		dev += "<bernhard@users.sourceforge.net>\n" + sep
		entry = wal.Entry(self, dev, multiline=True, editable=False)
		self.pack(entry, expand=True, fill=True, padding=5)

class ThanksPage(wal.VPanel):

	def __init__(self, parent):
		wal.VPanel.__init__(self, parent)
		entry = wal.Entry(self, CREDITS, multiline=True, editable=False)
		self.pack(entry, expand=True, fill=True, padding=5)

class LicensePage(wal.VPanel):

	def __init__(self, parent):
		wal.VPanel.__init__(self, parent)
		entry = wal.Entry(self, LICENSE, multiline=True, editable=False)
		self.pack(entry, expand=True, fill=True, padding=5)

def about_dialog(app, parent):
	title = _('About') + ' ' + app.appdata.app_name
	dlg = AboutDialog(app, parent, title)
	dlg.Centre()
	dlg.ShowModal()
	dlg.Destroy()
