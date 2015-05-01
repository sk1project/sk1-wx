# -*- coding: utf-8 -*-
#
#	Copyright (C) 2011 by Igor E. Novikov
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

from uc2 import uc2const
from uc2.utils.config import XmlConfigParser
from uc2.cms import libcms



class UCData:

	app_name = 'UniConvertor'
	app_proc = 'uniconvertor'
	app_org = 'sK1 Project'
	app_domain = 'sk1project.org'
	app_icon = None
	doc_icon = None
	version = '2.0'
	revision = 'rev.359'
	app_config_dir = os.path.expanduser(os.path.join('~', '.config', 'uc2'))

	def __init__(self, app):

		self.app = app

		if not os.path.lexists(self.app_config_dir):
			os.makedirs(self.app_config_dir)

		self.app_config = os.path.join(self.app_config_dir, 'preferences.cfg')

		#Check color profiles directory
		self.app_color_profile_dir = os.path.join(self.app_config_dir, 'profiles')
		if not os.path.lexists(self.app_color_profile_dir):
			os.makedirs(self.app_color_profile_dir)

		for item in uc2const.COLORSPACES + [uc2const.COLOR_DISPLAY, ]:
			filename = 'built-in_%s.icm' % item
			path = os.path.join(self.app_color_profile_dir, filename)
			if not os.path.lexists(path):
				libcms.cms_save_default_profile(path, item)

class UCConfig(XmlConfigParser):

	#============== GENERIC SECTION ===================
	uc_version = '2.0'
	system_encoding = 'utf-8'# default encoding (GUI uses utf-8 only)



	#============== COLOR MANAGEMENT SECTION ===================

	cms_use = True
	cms_display_profiles = {}
	cms_rgb_profiles = {}
	cms_cmyk_profiles = {}
	cms_lab_profiles = {}
	cms_gray_profiles = {}

	cms_rgb_profile = ''
	cms_cmyk_profile = ''
	cms_lab_profile = ''
	cms_gray_profile = ''
	cms_display_profile = ''

	cms_rgb_intent = uc2const.INTENT_RELATIVE_COLORIMETRIC
	cms_cmyk_intent = uc2const.INTENT_PERCEPTUAL
	cms_flags = uc2const.cmsFLAGS_NOTPRECALC
	cms_proofing = False
	cms_gamutcheck = False
	cms_alarmcodes = (1.0, 0.0, 1.0)
	cms_proof_for_spot = False
	cms_bpc_flag = False
	cms_bpt_flag = False

	def __init__(self):pass

	def get_defaults(self):
		return UCConfig.__dict__.copy()








