# -*- coding: utf-8 -*-
#
#  Copyright (C) 2017 by Igor E. Novikov
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
from uc2.utils import fsutils

LOG = logging.getLogger(__name__)


class StreamLogger:
    msg = ''
    counter = 0

    def __init__(self, app):
        self.logger = LOG.critical
        self.app = app

    def write(self, msg):
        msg = fsutils.get_utf8_path(msg)
        if not msg.endswith('\n') and not msg.startswith(' '):
            if self.counter < 2:
                self.msg += msg
                self.counter += 1
            else:
                self.logger(self.msg + msg)
                self.app.last_error = self.msg + msg
                self.msg = ''
                self.counter = 0
        else:
            self.msg += msg

    def close(self):
        pass

    def flush(self):
        pass
