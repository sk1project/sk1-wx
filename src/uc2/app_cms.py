# -*- coding: utf-8 -*-
#
#  Copyright (C) 2018 by Igor E. Novikov
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os

from uc2 import uc2const
from uc2.uc2const import COLOR_DISPLAY
from uc2.utils import fsutils

from uc2.cms import ColorManager, CS, libcms, val_255


class AppColorManager(ColorManager):
    app = None

    def __init__(self, app):
        self.app = app
        ColorManager.__init__(self)

    def update(self):
        self.handles = {}
        self.clear_transforms()
        config = self.app.config
        profiles = [config.cms_rgb_profile,
                    config.cms_cmyk_profile,
                    config.cms_lab_profile,
                    config.cms_gray_profile,
                    config.cms_display_profile]
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
            if profile and profile in profile_dicts[index]:
                profile_filename = profile_dicts[index][profile]
                path = os.path.join(profile_dir, profile_filename)
            if path:
                path = fsutils.get_sys_path(path)
                self.handles[item] = libcms.cms_open_profile_from_file(path)
            else:
                profile_dir = self.app.appdata.app_color_profile_dir
                filename = 'built-in_%s.icm' % item
                path = os.path.join(profile_dir, filename)
                path = fsutils.get_sys_path(path)
                self.handles[item] = libcms.cms_open_profile_from_file(path)
            index += 1
        self.use_cms = config.cms_use
        self.use_display_profile = config.cms_use_display_profile
        self.rgb_intent = config.cms_rgb_intent
        self.cmyk_intent = config.cms_cmyk_intent
        self.flags = config.cms_flags
        self.proofing = config.cms_proofing
        self.alarm_codes = config.cms_alarmcodes
        self.gamutcheck = config.cms_gamutcheck
        if self.gamutcheck:
            libcms.cms_set_alarm_codes(*val_255(self.alarm_codes))
        self.proof_for_spot = config.cms_proof_for_spot
        if self.proofing:
            self.flags = self.flags | uc2const.cmsFLAGS_SOFTPROOFING
        if self.gamutcheck:
            self.flags = self.flags | uc2const.cmsFLAGS_GAMUTCHECK
        if config.cms_bpc_flag:
            self.flags = self.flags | uc2const.cmsFLAGS_BLACKPOINTCOMPENSATION
        if config.cms_bpt_flag:
            self.flags = self.flags | uc2const.cmsFLAGS_PRESERVEBLACK
