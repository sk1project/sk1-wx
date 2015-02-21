# -*- coding: utf-8 -*-
#
#	Copyright (C) 2012 by Igor E. Novikov
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

from uc2 import _

JOB = 0
OK = 1
INFO = 2
WARNING = 3
ERROR = 4
STOP = 5

MESSAGES = {
JOB : _('JOB'),
OK : _('OK'),
INFO : _('INFO'),
WARNING : _('WARNING'),
ERROR : _('ERROR'),
STOP : _('STOP'),
}

lns = []
for key, val in MESSAGES.items():
	lns.append(len(val))

MAX_LEN = max(*lns)

