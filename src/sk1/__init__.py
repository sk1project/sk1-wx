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

import os

from sk1.app_conf import get_app_config

global config

def dummy_translator(text):
	return text

_ = dummy_translator
config = None

def init_config():

	"""sK1 config initialization"""

	global config
	config = get_app_config()
	cfg_dir = os.path.expanduser(os.path.join('~', '.config', 'sk1-wx'))
	cfg_path = os.path.join(cfg_dir, 'preferences.cfg')
	config.load(cfg_path)
	config.resource_dir = os.path.join(__path__[0], 'share')


def sk1_run():

	"""sK1 application launch routine"""

	_pkgdir = __path__[0]
	init_config()

	if not config.ubuntu_global_menu:
		os.environ["UBUNTU_MENUPROXY"] = "0"
	if not config.ubuntu_scrollbar_overlay:
		os.environ["LIBOVERLAY_SCROLLBAR"] = "0"

	from sk1.application import pdApplication

	app = pdApplication(_pkgdir)
	app.run()

def warn(msg):
	if config.print_warnings:
		print _('WARNING:'), msg