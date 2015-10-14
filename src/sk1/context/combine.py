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

from sk1.resources import pdids
from generic import ActionCtxPlugin

class CombinePlugin(ActionCtxPlugin):

	name = 'CombinePlugin'
	ids = [pdids.ID_COMBINE, pdids.ID_BREAK_APART]

class GroupPlugin(ActionCtxPlugin):

	name = 'GroupPlugin'
	ids = [pdids.ID_GROUP, pdids.ID_UNGROUP, pdids.ID_UNGROUPALL]

class ToCurvePlugin(ActionCtxPlugin):

	name = 'ToCurvePlugin'
	ids = [pdids.ID_TO_CURVES, ]
