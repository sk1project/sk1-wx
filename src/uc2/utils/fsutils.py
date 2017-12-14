# -*- coding: utf-8 -*-
#
#  Copyright (C) 2003-2017 by Igor E. Novikov
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

import errno

from uc2 import translator as _
from uc2 import events, msgconst


def get_fileptr(path, writable=False):
    if not path:
        msg = _('There is no file path')
        raise IOError(errno.ENODATA, msg, '')
    if writable:
        try:
            fileptr = open(path, 'wb')
        except Exception:
            msg = _('Cannot open %s file for writing') % path
            events.emit(events.MESSAGES, msgconst.ERROR, msg)
            raise
    else:
        try:
            fileptr = open(path, 'rb')
        except Exception:
            msg = _('Cannot open %s file for reading') % path
            events.emit(events.MESSAGES, msgconst.ERROR, msg)
            raise
    return fileptr
