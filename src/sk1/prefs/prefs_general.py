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
from sk1.resources import icons

from generic import PrefPanel

class GeneralPrefs(PrefPanel):

	pid = 'General'
	name = _('General')
	icon_id = icons.PD_PROPERTIES

	def __init__(self, app, dlg, fmt_config=None):
		PrefPanel.__init__(self, app, dlg)

class CMSPrefs(PrefPanel):

	pid = 'CMS'
	name = _('Color management')
	title = _('Color management and color profiles')

	def __init__(self, app, dlg, fmt_config=None):
		PrefPanel.__init__(self, app, dlg)

class RulersPrefs(PrefPanel):

	pid = 'Rulers'
	name = _('Rulers')

	def __init__(self, app, dlg, fmt_config=None):
		PrefPanel.__init__(self, app, dlg)

class PalettesPrefs(PrefPanel):

	pid = 'Palettes'
	name = _('Palettes')
	title = _('Palette options and palette management')

	def __init__(self, app, dlg, fmt_config=None):
		PrefPanel.__init__(self, app, dlg)

class GridPrefs(PrefPanel):

	pid = 'Grid'
	name = _('Grid and guides')
	title = _('Grid and guides options')

	def __init__(self, app, dlg, fmt_config=None):
		PrefPanel.__init__(self, app, dlg)
