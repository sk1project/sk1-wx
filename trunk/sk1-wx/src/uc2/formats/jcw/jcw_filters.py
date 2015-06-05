# -*- coding: utf-8 -*-
#
#	Copyright (C) 2015 by Igor E. Novikov
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

import os

from uc2.formats.generic_filters import AbstractBinaryLoader, AbstractSaver
from uc2.formats.jcw.jcw_model import JCW_Palette

PALETTE_NAMES = {
	'P4CPC': 'PANTONE® process coated',
	'P4CPCE': 'PANTONE® process coated EURO',
	'P4CPU': 'PANTONE® process uncoated',
	'P4CPUE': 'PANTONE® process uncoated EURO',
	'PCBC': 'PANTONE® color bridge CMYK PC',
	'PCBCE': 'PANTONE® color bridge CMYK EC',
	'PCBU': 'PANTONE® color bridge CMYK UP',
	'PFGC': 'PANTONE® solid coated',
	'PFGM': 'PANTONE® solid matte',
	'PFGU': 'PANTONE® solid uncoated',
	'PMC': 'PANTONE® metallic coated',
	'PPC': 'PANTONE® pastel coated',
	'PPU': 'PANTONE® pastel uncoated',
}

class JCW_Loader(AbstractBinaryLoader):

	name = 'JCW_Loader'

	def do_load(self):
		self.model = JCW_Palette()
		self.model.parse(self)
		if not self.model.name and self.filepath:
			filename = os.path.basename(self.filepath).split('.')[0]
			if filename in PALETTE_NAMES:
				self.model.name = PALETTE_NAMES[filename]
			else:
				self.model.name = '%s palette' % filename

class JCW_Saver(AbstractSaver):

	name = 'JCW_Saver'

	def do_save(self):
		self.model.save(self)
