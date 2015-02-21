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

from uc2.uc2const import mm_to_pt

mm_to_plt = 40.0

PDXF_to_PLT_TRAFO = [mm_to_plt / mm_to_pt, 0.0, 0.0,
					mm_to_plt / mm_to_pt, 0.0, 0.0]
PLT_to_PDXF_TRAFO = [mm_to_pt / mm_to_plt, 0.0, 0.0,
					mm_to_pt / mm_to_plt, 0.0, 0.0]
