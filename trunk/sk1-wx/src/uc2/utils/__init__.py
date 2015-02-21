# -*- coding: utf-8 -*-
#
#	Copyright (C) 2003-2011 by Igor E. Novikov
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

import base64
import time

from streamfilter import Base64Encode, Base64Decode, SubFileDecode

def generate_base64_id():
	time.sleep(0.001)
	return base64.b64encode(str(int(time.time()*100000)))

def generate_id():
	time.sleep(0.001)
	return str(int(time.time()*100000))
