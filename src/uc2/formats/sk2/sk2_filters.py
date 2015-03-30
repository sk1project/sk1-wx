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

import sys

from uc2.formats.generic_filters import AbstractLoader, AbstractSaver
from uc2.formats.sk2 import sk2_model, sk2_const

class SK2_Loader(AbstractLoader):

	name = 'SK2_Loader'
	model = None
	parent_stack = []

	def do_load(self):
		self.model = None
		self.parent_stack = []
		self.file.readline()
		while True:
			self.line = self.file.readline()
			if not self.line: break
			self.line = self.line.rstrip('\r\n')

			self.check_loading()

			if self.line:
				try:
					code = compile('self.' + self.line, '<string>', 'exec')
					exec code
				except:
					msg = 'error>> %s' % self.line
					errtype, value, traceback = sys.exc_info()
					self.send_error(msg)
					raise IOError(errtype, msg + '\n' + value, traceback)

	def obj(self, tag):
		obj_cid = sk2_model.TAGNAME_TO_CID[tag]
		obj = sk2_model.CID_TO_CLASS[obj_cid](self.config)
		if self.model is None:
			self.model = obj
			self.parent_stack.append(obj)
		else:
			self.parent_stack[-1].childs.append(obj)
			self.parent_stack.append(obj)

	def set_field(self, item, val):
		obj = self.parent_stack[-1]
		obj.__dict__[item] = val

	def obj_end(self):
		self.parent_stack = self.parent_stack[:-1]


class SK2_Saver(AbstractSaver):

	name = 'SK2_Saver'
	fileptr = None

	def __init__(self):
		pass

	def do_save(self):
		self.presenter.update()
		self.write_line(sk2_const.DOC_HEADER)
		self.save_obj(self.model)

	def write_line(self, line):
		self.fileptr.write(line + '\n')

	def save_obj(self, obj):
		self.write_line("obj('%s')" % sk2_model.CID_TO_TAGNAME[obj.cid])
		props = obj.__dict__
		for item in props.keys():
			if not item in sk2_model.GENERIC_FIELDS and not item[:5] == 'cache':
				item_str = props[item].__str__()
				if isinstance(props[item], str):
					item_str = "'%s'" % item_str.replace("'", "\\'")
				self.write_line("set_field('%s',%s)" % (item, item_str))
		for child in obj.childs:
			self.save_obj(child)
		self.write_line("obj_end()")


