#! /usr/bin/python2
# -*- coding: utf-8 -*-
#
#	Copyright (C) 2011 by Igor E. Novikov
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
#	along with this program.  If not, see <https://www.gnu.org/licenses/>. 

import sys, os
import base64

usage = """
Converts binary file in base32 encoded python resource file.
Resulted resource is siutable for pure python applications.

Usage: rcc2py input_file output_rc.py
       rcc2py input_file
       
In last case output file name will be input file name + '_rc.py'
2011(c) sK1 Project  https://sk1project.net/
"""

start = """
# -*- coding: utf-8 -*-
#
#	Created by rcc2py resource compiler.
#
#	WARNING! All changes made in this file will be lost!

import base64
from tempfile import NamedTemporaryFile

RESOURCE = '"""

end = """'

def get_resource(file=True):
	resource_file = NamedTemporaryFile(delete=file)
	resource_file.write(base64.b32decode(RESOURCE))
	if file:
		resource_file.file.seek(0)
		return resource_file
	else:
		filename = resource_file.name
		resource_file.close()
		return filename
		
def save_resource(path):
	file = open(path,'wb')
	file.write(base64.b32decode(RESOURCE))
	file.close()

"""


if len(sys.argv) == 1:
	print 'RESOURCE COMPILER: No input file!'
	print usage
	sys.exit(1)

if sys.argv[1] == '--help':
	print usage
	sys.exit(0)

input_file = sys.argv[1]
if len(sys.argv) > 2:
	output_file = sys.argv[2]
else:
	output_file = input_file + '_rc.py'

if not os.path.lexists(input_file):
	print 'RESOURCE COMPILER: Input file not found!'
	sys.exit(1)

file = open(input_file, 'rb')
content = file.read()
file.close()

content = base64.b32encode(content)
file = open(output_file, 'wb')
file.write(start + content + end)
file.close()
