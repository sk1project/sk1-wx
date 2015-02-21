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

import struct

def word2py_int(bytes):
	"""
	Converts word of bytes to Python int value.
	"""
	val, = struct.unpack('<H', bytes)
	return val

def dword2py_int(bytes):
	"""
	Converts double word of bytes to Python int value.
	"""
	val, = struct.unpack('<I', bytes)
	return val

def py_int2dword(val):
	"""
	Converts Python int value to word of bytes.
	"""
	return struct.pack('<I', val)

def double2py_float(bytes):
	"""
	Converts 8 bytes to Python float value.
	"""
	val, = struct.unpack('<d', bytes)
	return val

def py_float2double(val):
	"""
	Converts Python float to 8 bytes (double)
	"""
	return struct.pack('<d', val)

def long2py_float(bytes):
	"""
	Converts 4 bytes to Python float value.
	"""
	val, = struct.unpack('<l', bytes)
	return val

def get_chunk_size(size_field):
	size = dword2py_int(size_field)
	if not size % 2 == 0:
		size += 1
	return size





def _test():
	print py_int2dword(123)

if __name__ == '__main__':
    _test()
