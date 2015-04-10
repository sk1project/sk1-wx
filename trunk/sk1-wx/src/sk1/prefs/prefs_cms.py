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

import wal

from sk1 import _, config
from sk1.resources import icons, get_bmp

from generic import PrefPanel

class CMSPrefs(PrefPanel):

	pid = 'CMS'
	name = _('Color management')
	title = _('Color management and color profiles')
	icon_id = icons.PD_PREFS_CMS
	tabs = []

	def __init__(self, app, dlg, fmt_config=None):
		PrefPanel.__init__(self, app, dlg)

	def build(self):
		self.nb = wal.Notebook(self)

		#========Color management options
		self.page0 = CMS_Options(self.nb, self)
		self.page1 = CMS_Profiles(self.nb, self)
		self.page2 = CMS_Settings(self.nb, self)

		for item in [self.page0, self.page1, self.page2]:
			self.nb.add_page(item, item.name)

		self.pack(self.nb, expand=True, fill=True)
		self.built = True
		self.page0.activate_cms()

	def apply_changes(self):
#		config.palette = self.get_palette_name_by_index(self.pal.get_active())
		for item in self.nb.childs:
			item.apply_changes()

	def restore_defaults(self):
#		defaults = config.get_defaults()
#		self.pal.set_active(self.get_index_by_palette_name(defaults['palette']))
		for item in self.nb.childs:
			item.restore_defaults()

class CMS_Tab(wal.VPanel):

	name = ''
	prefpanel = None

	def __init__(self, parent, prefpanel):
		self.prefpanel = prefpanel
		wal.VPanel.__init__(self, parent)

	def apply_changes(self):pass
	def restore_defaults(self):pass


class CMS_Options(CMS_Tab):

	name = _('Color management')

	def __init__(self, parent, prefpanel):
		CMS_Tab.__init__(self, parent, prefpanel)
		txt = _('Activate Color Management')
		self.cms_check = wal.Checkbox(self, txt, config.cms_use,
									onclick=self.activate_cms)

		self.pack(self.cms_check, align_center=False, padding_all=3)

		self.banner = wal.VPanel(self)
		self.banner.set_bg(wal.DARK_GRAY)
		bmp = get_bmp(self.banner, icons.PD_PREFS_CMS_BANNER)
		self.banner.pack(bmp, padding=2)
		self.pack(self.banner, expand=True, fill=True)
		txt = _('Note: If Color Management is not activated all colors '
			'will be processed using simple calculation procedures. Therefore '
			'resulted color values will be not accurate.')
		label = wal.Label(self, txt, fontsize=-3)
		label.set_enable(False)
		self.pack(label, fill=True, padding_all=5)

	def activate_cms(self, event=None):
		self.banner.set_visible(self.cms_check.get_value())
		nb = self.prefpanel.nb
		if self.cms_check.get_value() and len(nb.childs) < 2:
			nb.add_page(self.prefpanel.page1, self.prefpanel.page1.name)
			nb.add_page(self.prefpanel.page2, self.prefpanel.page2.name)
		elif not self.cms_check.get_value() and len(nb.childs) > 1:
			nb.remove_page(self.prefpanel.page1)
			nb.remove_page(self.prefpanel.page2)

	def apply_changes(self):
		config.cms_use = self.cms_check.get_value()

	def restore_defaults(self):
		defaults = config.get_defaults()
		self.cms_check.set_value(defaults['cms_use'])


class CMS_Profiles(CMS_Tab):

	name = _('Color profiles')

	def __init__(self, parent, prefpanel):
		CMS_Tab.__init__(self, parent, prefpanel)


class CMS_Settings(CMS_Tab):

	name = _('Settings')

	def __init__(self, parent, prefpanel):
		CMS_Tab.__init__(self, parent, prefpanel)

