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

from uc2.formats.generic_filters import AbstractXMLLoader, AbstractSaver
from uc2.formats.soc.soc_const import SOC_COLOR_TAG, SOC_COLOR_NAME_ATTR, \
SOC_COLOR_VAL_ATTR, SOC_PAL_TAG, SOC_PAL_ATTRS, SOC_PAL_OO_TAG, SOURCE_LO, \
SOC_PAL_OO_ATTRS, SOURCE_OO

class SOC_Loader(AbstractXMLLoader):

	name = 'SOC_Loader'

	def do_load(self):
		self.start_parsing()

	def start_element(self, name, attrs):
		if name == SOC_PAL_OO_TAG:
			self.model.source = SOURCE_OO
		if name == SOC_COLOR_TAG:
			self.model.colors.append([attrs._attrs[SOC_COLOR_VAL_ATTR],
				attrs._attrs[SOC_COLOR_NAME_ATTR]])

class SOC_Saver(AbstractSaver):

	name = 'SOC_Saver'

	def do_save(self):
		self.writeln('<?xml version="1.0" encoding="UTF-8"?>')
		if self.model.comments:
			self.writeln('<!--')
			self.writeln(self.model.comments)
			self.writeln('-->')

		if self.model.source == SOURCE_LO:
			pal_tag = SOC_PAL_TAG
			pal_attr = SOC_PAL_ATTRS
		else:
			pal_tag = SOC_PAL_OO_TAG
			pal_attr = SOC_PAL_OO_ATTRS

		line = '<%s' % pal_tag
		for item in pal_attr.keys():
			line += ' %s="%s"' % (item, pal_attr[item])
		self.writeln(line + '>')

		for item in self.model.colors:
			self.writeln(' <%s %s="%s" %s="%s"/>' % (SOC_COLOR_TAG,
				SOC_COLOR_NAME_ATTR, item[1], SOC_COLOR_VAL_ATTR, item[0]))

		self.writeln('</%s>' % pal_tag)
