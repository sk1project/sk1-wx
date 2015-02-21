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

from uc2 import uc2const
from uc2.uc2const import COLOR_DISPLAY

from uc2.cms import ColorManager, CS, libcms
from uc2.formats.pdxf.pdxf_config import PDXF_Config
from sk1 import config, events

class AppColorManager(ColorManager):

	color_mngrs = []
	use_display_profile = True

	def __init__(self, app):
		self.app = app
		self.color_mngrs = []
		ColorManager.__init__(self)
		events.connect(events.CONFIG_MODIFIED, self.config_changed)

	def config_changed(self, *args):
		field = args[0][0]
		if field[0:4] == 'cms_':
			self.update()
			self.update_mngrs()
			events.emit(events.CMS_CHANGED)

	def get_profiles(self):
		pdxf_config = PDXF_Config()
		filename = 'pdxf_config.xml'
		config_file = os.path.join(self.app.appdata.app_config_dir, filename)
		pdxf_config.load(config_file)
		profiles = [pdxf_config.default_rgb_profile,
				pdxf_config.default_cmyk_profile,
				pdxf_config.default_lab_profile,
				pdxf_config.default_gray_profile]
		profiles.append(config.cms_display_profile)
		return profiles

	def update(self):
		self.handles = {}
		self.clear_transforms()
		profiles = self.get_profiles()
		profile_dicts = [config.cms_rgb_profiles,
						config.cms_cmyk_profiles,
						config.cms_lab_profiles,
						config.cms_gray_profiles,
						config.cms_display_profiles]
		index = 0
		profile_dir = self.app.appdata.app_color_profile_dir
		for item in CS + [COLOR_DISPLAY, ]:
			path = None
			profile = profiles[index]
			if profile and profile_dicts[index].has_key(profile):
				profile_filename = profile_dicts[index][profile]
				path = os.path.join(profile_dir, profile_filename)
			if path:
				self.handles[item] = libcms.cms_open_profile_from_file(path)
			else:
				profile_dir = self.app.appdata.app_color_profile_dir
				filename = 'built-in_%s.icm' % item
				path = os.path.join(profile_dir, filename)
				self.handles[item] = libcms.cms_open_profile_from_file(path)
			index += 1
		self.use_cms = config.cms_use
		self.rgb_intent = config.cms_rgb_intent
		self.cmyk_intent = config.cms_cmyk_intent
		self.flags = config.cms_flags
		self.proofing = config.cms_proofing
		self.alarm_codes = config.cms_alarmcodes
		self.gamutcheck = config.cms_gamutcheck
		self.proof_for_spot = config.cms_proof_for_spot
		if self.proofing:
			self.flags = self.flags | uc2const.cmsFLAGS_SOFTPROOFING
		if self.gamutcheck:
			self.flags = self.flags | uc2const.cmsFLAGS_GAMUTCHECK
		if config.cms_bpc_flag:
			self.flags = self.flags | uc2const.cmsFLAGS_BLACKPOINTCOMPENSATION
		if config.cms_bpt_flag:
			self.flags = self.flags | uc2const.cmsFLAGS_PRESERVEBLACK

	def registry_cm(self, cm):
		self.color_mngrs.append(cm)
		self.apply_cm_settings(cm)

	def unregistry_cm(self, cm):
		self.color_mngrs.remove(cm)

	def apply_cm_settings(self, cm):
		if self.use_display_profile:
			cm.use_display_profile = True
			cm.handles[COLOR_DISPLAY] = self.handles[COLOR_DISPLAY]
		else:
			cm.use_display_profile = False
		cm.use_cms = self.use_cms
		cm.rgb_intent = self.rgb_intent
		cm.cmyk_intent = self.cmyk_intent
		cm.flags = self.flags
		cm.alarm_codes = self.alarm_codes
		cm.gamutcheck = self.gamutcheck
		cm.proofing = self.proofing
		cm.proof_for_spot = self.proof_for_spot
		cm.clear_transforms()

	def update_mngrs(self):
		for item in self.color_mngrs:
			self.apply_cm_settings(item)
