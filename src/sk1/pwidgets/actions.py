# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2013 by Igor E. Novikov
#
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
#
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
#
# 	You should have received a copy of the GNU General Public License
# 	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import wx

from wal import const, ImageButton

from sk1 import events, resources

class AppAction:

	action_id = None
	callback = None
	channels = []
	validator = None
	checker = None
	callable_args = []
	validator_args = []
	checker_args = []

	widgets = []
	toolbar = None
	enabled = True
	active = False
	is_acc = False
	acc_entry = None

	def __init__(self, action_id, callback, channels=[],
				validator=None, checker=None,
				callable_args=[], validator_args=[], checker_args=[]):

		self.action_id = action_id
		self.is_acc = resources.ACC_KEYS.has_key(action_id)
		if self.is_acc:
			self.acc_entry = resources.get_accentry_by_id(self.action_id)
		self.is_icon = resources.ART_IDS.has_key(action_id)
		self.callback = callback
		self.channels = channels
		self.validator = validator
		self.checker = checker
		self.callable_args = callable_args
		self.validator_args = validator_args
		self.checker_args = checker_args

		self.widgets = []

		if channels:
			for channel in channels:
				events.connect(channel, self.receiver)

	def update(self):
		for widget in self.widgets:
			widget.update()
		if not self.toolbar is None and not const.is_mac():
			self.toolbar.EnableTool(self.action_id, self.enabled)
			self.toolbar.SetToolShortHelp(self.action_id, self.get_descr_text())

	def register(self, widget):
		self.widgets.append(widget)
		self.update()

	def register_as_tool(self, toolbar):
		self.toolbar = toolbar

	def unregister(self, widget):
		if widget in self.widgets:
			self.widgets.remove(widget)
		self.update()

	def receiver(self, *args):
		if self.validator_args:
			self.set_enable(self.validator(*self.validator_args))
		else: self.set_enable(self.validator())
		if self.is_toggle():
			if self.checker_args:
				self.set_active(self.checker(*self.checker_args))
			else: self.set_active(self.checker())

	def set_enable(self, enabled):
		if not enabled == self.enabled:
			self.enabled = enabled
			for widget in self.widgets:
				widget.set_enable(self.enabled)
			if not self.toolbar is None and not const.is_mac():
				self.toolbar.EnableTool(self.action_id, self.enabled)

	def set_active(self, active):
		if not active == self.active:
			self.active = active
			for widget in self.widgets:
				widget.set_active(self.active)

	def do_call(self, *args):
		if self.enabled:
			if self.callable_args: self.callback(*self.callable_args)
			else: self.callback()
		if self.is_toggle():
			if self.checker_args:
				self.set_active(self.checker(*self.checker_args))
			else: self.set_active(self.checker())

	def get_artid(self):
		if self.is_icon:
			return resources.get_art_by_id(self.action_id)
		return None

	def get_icon(self, size=(16, 16), client=wx.ART_OTHER):
		if self.is_icon:
			return resources.get_bitmap_by_id(self.action_id, client, size)
		return None

	def get_menu_text(self):
		return resources.get_menu_text(self.action_id)

	def get_tooltip_text(self):
		return resources.get_tooltip_text(self.action_id)

	def get_descr_text(self):
		return resources.get_descr_text(self.action_id)

	def get_shortcut_text(self):
		if self.is_acc:
			return self.acc_entry.ToString()
		return ''

	def is_toggle(self):
		return not self.checker is None

class ActionButton(ImageButton):

	action = None

	def __init__(self, parent, action):
		self.action = action
		artid = action.get_artid()
		tooltip = action.get_tooltip_text()
		text = ''
		if artid is None: text = tooltip
		native = True
		if not const.is_gtk(): native = False
		ImageButton.__init__(self, parent, artid, const.DEF_SIZE, text, tooltip,
							native=native, onclick=action.do_call)
		action.register(self)

	def update(self):
		self.set_enable(self.action.enabled)
