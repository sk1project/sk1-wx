# -*- coding: utf-8 -*-
#
#	Copyright (C) 2003-2015 by Igor E. Novikov
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
import struct

from streamfilter import Base64Encode, Base64Decode, SubFileDecode

def generate_base64_id():
	"""
	Generates bas64 encoded id based on UNIX time
	"""
	time.sleep(0.001)
	return base64.b64encode(str(int(time.time() * 100000)))

def generate_id():
	"""
	Generates numeric id based on UNIX time
	"""
	time.sleep(0.001)
	return str(int(time.time() * 100000))

def generate_guid():
	import uuid
	time.sleep(0.001)
	return uuid.uuid1()

def word2py_int(data):
	"""
	Converts word of bytes to Python int value.
	"""
	val, = struct.unpack('<H', data)
	return val

def dword2py_int(data):
	"""
	Converts double word of bytes to Python int value.
	"""
	val, = struct.unpack('<I', data)
	return val

def py_int2dword(val):
	"""
	Converts Python int value to word of bytes.
	"""
	return struct.pack('<I', val)

def double2py_float(data):
	"""
	Converts 8 bytes to Python float value.
	"""
	val, = struct.unpack('<d', data)
	return val

def py_float2double(val):
	"""
	Converts Python float to 8 bytes (double)
	"""
	return struct.pack('<d', val)

def long2py_float(data):
	"""
	Converts 4 bytes to Python float value.
	"""
	val, = struct.unpack('<l', data)
	return val

def get_chunk_size(size_field):
	size = dword2py_int(size_field)
	if not size % 2 == 0:
		size += 1
	return size
