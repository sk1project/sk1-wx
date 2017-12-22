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
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import sys

LOG = logging.getLogger(__name__)


class StreamLogger:
    msg = ''
    counter = 0

    def __init__(self):
        self.logger = LOG.critical

    def write(self, msg):
        if not msg.endswith('\n') and not msg.startswith(' '):
            if self.counter < 2:
                self.msg += msg
                self.counter += 1
            else:
                self.logger(self.msg + msg)
                self.msg = ''
                self.counter = 0
        else:
            self.msg += msg

    def close(self):
        self.logger('close')
        pass

    def flush(self):
        self.logger('flush')
        pass
