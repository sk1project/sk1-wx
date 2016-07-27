# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2016 by Igor E. Novikov
#
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
#
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
#
# 	You should have received a copy of the GNU General Public License
# 	along with this program.  If not, see <http://www.gnu.org/licenses/>.

class AbstractPrinter(object):

	name = 'Abstract Printer'

	def get_name(self): return self.name
	def is_virtual(self): return True
	def get_connection(self): return '---'
	def get_driver_name(self): return '---'
	def get_state(self): return '---'
	def get_filepath(self): return ''

class AbstractPS(object):

	def get_default_printer(self): return None

class AbstractPrintout(object):pass
