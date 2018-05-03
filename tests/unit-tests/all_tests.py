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

import unittest
import cms_testsuite
import _libimg_testsuite
import image_testsuite

suite = unittest.TestSuite()
suite.addTest(cms_testsuite.get_suite())
suite.addTest(_libimg_testsuite.get_suite())
suite.addTest(image_testsuite.get_suite())

unittest.TextTestRunner(verbosity=2).run(suite)
