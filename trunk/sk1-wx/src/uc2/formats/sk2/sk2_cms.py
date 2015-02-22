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

from uc2.cms import ColorManager, CS, libcms

class SK2_ColorManager(ColorManager):

	presenter = None

	def __init__(self, presenter):
		self.presenter = presenter
		ColorManager.__init__(self)

	def update(self):
		self.handles = {}
		self.clear_transforms()

		config = self.presenter.config
		profiles = [config.default_rgb_profile,
				config.default_cmyk_profile,
				config.default_lab_profile,
				config.default_gray_profile]

		index = 0
		profile_dir = self.presenter.appdata.app_color_profile_dir
		for item in CS:
			path = None
			if profiles[index]:
				path = os.path.join(profile_dir, profiles[index])
			if path and os.path.isfile(path):
				self.handles[item] = libcms.cms_open_profile_from_file(path)
			else:
				filename = 'built-in_%s.icm' % item
				path = os.path.join(profile_dir, filename)
				self.handles[item] = libcms.cms_open_profile_from_file(path)
			index += 1

