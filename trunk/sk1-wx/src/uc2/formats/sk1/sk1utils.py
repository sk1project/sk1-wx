# -*- coding: utf-8 -*-
#
#	Copyright (C) 2013 by Igor E. Novikov
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

from uc2.formats.sk1.sk1const import RGB

def CreateRGBColor(r, g, b):
	return (RGB, round(r, 3), round(g, 3), round(b, 3))

class StandardColors:
	black = CreateRGBColor(0.0, 0.0, 0.0)
	darkgray = CreateRGBColor(0.25, 0.25, 0.25)
	gray = CreateRGBColor(0.5, 0.5, 0.5)
	lightgray = CreateRGBColor(0.75, 0.75, 0.75)
	white = CreateRGBColor(1.0, 1.0, 1.0)
	red = CreateRGBColor(1.0, 0.0, 0.0)
	green = CreateRGBColor(0.0, 1.0, 0.0)
	blue = CreateRGBColor(0.0, 0.0, 1.0)
	cyan = CreateRGBColor(0.0, 1.0, 1.0)
	magenta = CreateRGBColor(1.0, 0.0, 1.0)
	yellow = CreateRGBColor(1.0, 1.0, 0.0)
