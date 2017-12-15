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

import gtk

from sword import _, events
from sword.events import CONFIG_MODIFIED, APP_STATUS, NO_DOCS, DOC_MODIFIED, \
DOC_CHANGED, DOC_SAVED, DOC_CLOSED, MODE_CHANGED, SELECTION_CHANGED, CLIPBOARD


class AppAction(gtk.Action):

	def __init__(self, name, label, tooltip, icon, shortcut,
				 callable, channels, validator, args=[]):

		gtk.Action.__init__(self, name, label, tooltip, icon)
		self.menuitem = None
		self.tooltip = tooltip
		self.shortcut = shortcut
		self.callable = callable
		self.events = events
		self.validator = validator
		self.args = args
		self.icon = icon

		self.connect('activate', self.callable)

		self.channels = channels
		self.validator = validator

		if channels:
			for channel in channels:
				events.connect(channel, self.receiver)

	def receiver(self, *args):
		self.set_sensitive(self.validator())

def create_actions(app):
	insp = app.inspector
	proxy = app.proxy
	accelgroup = app.accelgroup
	actiongroup = app.actiongroup
	actions = {}
	entries = [

	['NEW', _('_New'), _('New'), gtk.STOCK_NEW, '<Control>N',
	 proxy.new, None, None],
	['OPEN', _('_Open'), _('Open'), gtk.STOCK_OPEN, '<Control>O',
	 proxy.open, None, None],
	['SAVE', _('_Save'), _('Save'), gtk.STOCK_SAVE, '<Control>S',
	 proxy.save, [NO_DOCS, DOC_CHANGED, DOC_MODIFIED, DOC_SAVED],
	 insp.is_doc_not_saved],
	['SAVE_AS', _('Save _As...'), _('Save As...'), gtk.STOCK_SAVE_AS, None,
	 proxy.save_as, [NO_DOCS, DOC_CHANGED], insp.is_doc],
	['SAVE_ALL', _('Save All'), _('Save All'), None, None,
	 proxy.save_all, [NO_DOCS, DOC_CHANGED, DOC_MODIFIED, DOC_SAVED],
	 insp.is_any_doc_not_saved],
	['CLOSE', _('_Close'), _('Close'), gtk.STOCK_CLOSE, '<Control>W',
	 proxy.close, [NO_DOCS, DOC_CHANGED], insp.is_doc],
	['CLOSE_ALL', _('_Close All'), _('Close All'), None, None,
	 proxy.close_all, [NO_DOCS, DOC_CHANGED], insp.is_doc],
	['QUIT', _('_Exit'), _('Exit'), gtk.STOCK_QUIT, '<Alt>F4',
	 proxy.exit, None, None],


	['CUT', _('Cu_t'), _('Cut'), gtk.STOCK_CUT, '<Control>X',
	 proxy.cut, [events.NO_DOCS, events.DOC_CHANGED,
	events.SELECTION_CHANGED], insp.can_cutcopy],
	['COPY', _('_Copy'), _('Copy'), gtk.STOCK_COPY, '<Control>C',
	 proxy.copy, [events.NO_DOCS, events.DOC_CHANGED,
	events.SELECTION_CHANGED], insp.can_cutcopy],
	['PASTE', _('_Paste'), _('Paste'), gtk.STOCK_PASTE, '<Control>V',
	 proxy.paste, [events.NO_DOCS, events.CLIPBOARD], insp.stub],
	['DELETE', _('_Delete'), _('Delete'), gtk.STOCK_DELETE, 'Delete',
	 proxy.delete, [events.NO_DOCS, events.DOC_CHANGED,
	events.SELECTION_CHANGED], insp.can_cutcopy],

	['BACKWARD', _('Go back'), _('Go back'), gtk.STOCK_GO_BACK,
	 '<Alt>Left', proxy.backward_object, [events.NO_DOCS, events.DOC_CHANGED,
	events.SELECTION_CHANGED], insp.can_backward_object],
	['FORWARD', _('Go forward'), _('Go forward'), gtk.STOCK_GO_FORWARD,
	 '<Alt>Right', proxy.forward_object, [events.NO_DOCS, events.DOC_CHANGED,
	events.SELECTION_CHANGED], insp.can_forward_object],
	['ROOT', _('Go to root'), _('Go to root'), gtk.STOCK_HOME, '<Alt>Home',
	 proxy.root_object, [events.NO_DOCS, events.DOC_CHANGED,
	events.SELECTION_CHANGED], insp.can_set_root],

	['CLEAR_HISTORY', _('Clear history'), _('Clear history'), gtk.STOCK_CLEAR,
	 None, proxy.clear_history, [events.NO_DOCS, events.DOC_CHANGED,
	events.SELECTION_CHANGED], insp.can_clear_history],

	['REFRESH_OBJ', _('Refresh object'), _('Refresh object'), gtk.STOCK_REFRESH,
	 '<Control>R', proxy.refresh_object, [events.NO_DOCS, events.DOC_CHANGED,
	events.SELECTION_CHANGED], insp.can_refresh_object],
	['EDIT_OBJ', _('Edit binary chunk'), _('Edit binary chunk'), gtk.STOCK_EDIT,
	 None, proxy.edit_object, [events.NO_DOCS, events.DOC_CHANGED,
	events.SELECTION_CHANGED], insp.can_edit_object],
	['UPDATE_OBJ', _('Update edited chunk'), _('Update edited chunk'), gtk.STOCK_REVERT_TO_SAVED,
	 None, proxy.update_object, [events.NO_DOCS, events.DOC_CHANGED,
	events.SELECTION_CHANGED], insp.can_update_object],

	['REFRESH_MODEL', _('Refresh model'), _('Refresh model'), gtk.STOCK_REFRESH,
	 '<Alt>R', proxy.refresh_model, [events.NO_DOCS, events.DOC_CHANGED,
	events.SELECTION_CHANGED], insp.can_refresh_model],

	['COPY_TO_COMPARE', _('_Copy to comparator'), _('Copy to comparator'),
	gtk.STOCK_GOTO_LAST, None, proxy.copy_to_compare, [events.NO_DOCS,
	events.DOC_CHANGED, events.SELECTION_CHANGED], insp.can_copy_to_compare],
	['COPY_TO_CLIP', _('_Copy to clip'), _('Copy to clip'), gtk.STOCK_MEDIA_NEXT,
	None, proxy.copy_to_clip, [events.NO_DOCS, events.DOC_CHANGED,
	events.SELECTION_CHANGED], insp.can_copy_to_clip],




	['PREFERENCES', _('Preferences...'), _('Preferences...'), gtk.STOCK_PREFERENCES, None,
	 proxy.prefs, None, None],


	['REPORT_BUG', _('_Report bug'), _('Report bug'), gtk.STOCK_DIALOG_WARNING, None,
	 proxy.report_bug, None, None],
	['PROJECT_WEBSITE', _('Project _web site'), _('Project web site'), None, None,
	 proxy.project_website, None, None],
	['PROJECT_FORUM', _('Project _forum'), _('Project forum'), None, None,
	 proxy.project_forum, None, None],
	['ABOUT', _('_About SWord'), _('About SWord'), gtk.STOCK_ABOUT, None,
	 proxy.about, None, None],
	]

	for entry in entries:
		action = AppAction(entry[0], entry[1], entry[2], entry[3],
						   entry[4], entry[5], entry[6], entry[7])

		actions[entry[0]] = action
		if not action.shortcut is None:
			actiongroup.add_action_with_accel(action, action.shortcut)
			action.set_accel_group(accelgroup)
		else:
			actiongroup.add_action(action)

	return actions
