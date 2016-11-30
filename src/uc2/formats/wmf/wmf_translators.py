# -*- coding: utf-8 -*-
#
# 	 Copyright (C) 2016 by Igor E. Novikov
#
# 	 This program is free software: you can redistribute it and/or modify
# 	 it under the terms of the GNU General Public License as published by
# 	 the Free Software Foundation, either version 3 of the License, or
# 	 (at your option) any later version.
#
# 	 This program is distributed in the hope that it will be useful,
# 	 but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	 GNU General Public License for more details.
#
# 	 You should have received a copy of the GNU General Public License
# 	 along with this program.  If not, see <http://www.gnu.org/licenses/>.

class WMF_to_SK2_Translator(object):

	def translate(self, wmf_doc, sk2_doc):
		self.wmf_doc = wmf_doc
		self.sk2_doc = sk2_doc
		self.wmf_mt = wmf_doc.model
		self.sk2_mt = sk2_doc.model
		self.sk2_mtds = sk2_doc.methods

		if self.wmf_mt.is_placeable():
			self.translate_header(self.wmf_mt.chids[0])
		else:
			self.translate_header(self.wmf_mt)

	def translate_header(self, header):
		for record in header.childs:
			self.translate_record(record)

	def translate_record(self, record):
		pass


class SK2_to_WMF_Translator(object):

	def translate(self, sk2_doc, wmf_doc):pass
