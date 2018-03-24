# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013-2018 by Igor E. Novikov
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
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os

import uc2

_ = uc2._
config = None


def init_config(cfgdir='~'):
    """sK1 config initialization"""

    cfg_dir = os.path.expanduser(os.path.join(cfgdir, '.config', 'sk1-wx'))
    cfg_path = os.path.join(cfg_dir, 'preferences.cfg')
    resource_dir = os.path.join(__path__[0], 'share')

    # Setting locale before app initialization
    lang = 'system'
    if os.path.lexists(cfg_path) and os.path.isfile(cfg_path):
        try:
            with open(cfg_path) as fp:
                while True:
                    line = fp.readline()
                    if not line:
                        break
                    if line.startswith('language'):
                        lang = line.split('=')[1].strip().replace('\'', '')
                        break
        except Exception:
            lang = 'system'
    _.set_locale('sk1', os.path.join(resource_dir, 'locales'), lang)

    global config
    from sk1.app_conf import get_app_config
    config = get_app_config()
    config.load(cfg_path)
    config.resource_dir = resource_dir


def sk1_run(cfgdir='~'):
    """sK1 application launch routine"""

    _pkgdir = __path__[0]
    init_config(cfgdir)

    if not config.ubuntu_global_menu:
        os.environ["UBUNTU_MENUPROXY"] = "0"
    if not config.ubuntu_scrollbar_overlay:
        os.environ["LIBOVERLAY_SCROLLBAR"] = "0"

    from sk1.application import SK1Application

    app = SK1Application(_pkgdir, cfgdir)
    app.run()
