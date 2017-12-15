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

#Selection format: [object reference, tree path]


from sword import events

class ModelSelection:

	selected = []
	back = []
	forward = []

	presenter = None
	model = None

	def __init__(self, presenter):
		self.presenter = presenter
		self.model = self.presenter.doc_presenter.model
		self.eventloop = self.presenter.eventloop

	def _send_event(self):
		self.eventloop.emit(self.eventloop.SELECTION_CHANGED, self.selected)
		events.emit(events.SELECTION_CHANGED, self.selected)

	def set_selection(self, obj, path):
		self.forward = []
		if self.selected:
			self.back.append([] + self.selected)
		self.selected = [obj, path]
		self._send_event()

	def clear_history(self):
		self.back = []
		self.forward = []
		self._send_event()

	def back_action(self):
		if self.selected:
			self.forward.insert(0, [] + self.selected)
		self.selected = [] + self.back[-1]
		self.back.remove(self.back[-1])
		self._send_event()

	def forward_action(self):
		if self.selected:
			self.back.append([] + self.selected)
		self.selected = [] + self.forward[0]
		self.forward.remove(self.forward[0])
		self._send_event()

	def set_root(self):
		self.set_selection(self.model, (0,))


