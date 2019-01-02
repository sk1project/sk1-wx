# -*- coding: utf-8 -*-
#
#  Copyright (C) 2015-2018 by Igor E. Novikov
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

import logging
from base64 import b64encode

from PIL import Image
from uc2.libimg import magickwand

LOG = logging.getLogger(__name__)


def get_version():
    return Image.PILLOW_VERSION


def get_magickwand_version():
    return magickwand.get_magickwand_version()


def check_image(path):
    try:
        Image.open(path)
        LOG.debug('PIL check: True')
        return True
    except Exception:
        return magickwand.check_image_file(path)


EPS_HEADER = '%!PS-Adobe-3.0 EPSF-3.0'


def read_pattern(raw_content):
    if raw_content[:len(EPS_HEADER)] == EPS_HEADER:
        return b64encode(raw_content), 'EPS'
    fobj, flag = magickwand.process_pattern(raw_content)
    return b64encode(fobj.getvalue()), flag
