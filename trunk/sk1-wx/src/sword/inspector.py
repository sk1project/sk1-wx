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

import os

from uc2 import uc2const

class DocumentInspector:

	def __init__(self, app):
		self.app = app

	def is_doc(self):
		if self.app.docs:
			return True
		else:
			return False

	def is_not_doc(self):
		if self.app.docs:
			return False
		else:
			return True

	def is_doc_saved(self, doc=None):
		return True

	def is_doc_not_saved(self, doc=None):
		return False

	def is_any_doc_not_saved(self):
		return False

	def is_selection(self, doc=None):
		if doc is None:
			doc = self.app.current_doc
		if doc is None:
			return False
		if doc.selection.selected: return True
		return False

	def can_cutcopy(self, doc=None):
		if doc is None:
			doc = self.app.current_doc
		if doc is None:
			return False
		if self.is_selection():
			if not len(doc.selection.selected[1]) == 1:
				return True
		return False

	def can_paste(self):return False

	def can_backward_object(self, doc=None):
		if doc is None:
			doc = self.app.current_doc
		if doc is None:
			return False
		if doc.selection.back: return True
		return False

	def can_forward_object(self, doc=None):
		if doc is None:
			doc = self.app.current_doc
		if doc is None:
			return False
		if doc.selection.forward: return True
		return False

	def can_set_root(self, doc=None):
		if doc is None:
			doc = self.app.current_doc
		if doc is None:
			return False
		selected = doc.selection.selected
		if selected and len(selected[1]) == 1: return False
		return True

	def can_clear_history(self, doc=None):
		if doc is None:
			doc = self.app.current_doc
		if doc is None:
			return False
		if doc.selection.back or doc.selection.forward: return True
		return False

	def can_refresh_object(self, doc=None):
		return self.is_selection(doc)

	def can_edit_object(self, doc=None):
		if self.is_selection(doc):
			if self.app.current_doc.doc_presenter.model_type == uc2const.BINARY_MODEL:
				return True
		return False

	def can_update_object(self, doc=None):
		if self.is_selection(doc):
			if self.app.current_doc.doc_presenter.model_type == uc2const.BINARY_MODEL:
				obj = self.app.current_doc.docarea.objectbrowser.visualizer.viewer.current_obj
				filename = 'chunk[%s]' % (str(obj).split(' at ')[1][:-1])
				filename = os.path.join(self.app.appdata.app_temp_dir, filename)
				if os.path.lexists(filename):
					return True
		return False

	def can_refresh_model(self, doc=None):
		return self.is_doc()

	def can_copy_to_compare(self, *args):return False
	def can_copy_to_clip(self, *args):return False

	def stub(self):return False
