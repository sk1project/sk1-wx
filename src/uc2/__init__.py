# -*- coding: utf-8 -*-
#
#  Copyright (C) 2011-2018 by Igor E. Novikov
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
import sys

from uc2.utils import translator

config = None
appdata = None

_ = translator.MsgTranslator()


def uc2_init():
    """UniConvertor initializing routine."""

    _pkgdir = __path__[0].decode(sys.getfilesystemencoding()).encode('utf-8')

    from application import UCApplication

    app = UCApplication(_pkgdir)
    return app


def uc2_run(cwd=None):
    """UniConvertor launch routine."""

    app = uc2_init()
    app.run(cwd or os.getcwd())
