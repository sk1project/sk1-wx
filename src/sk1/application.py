# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2013-2015 by Igor E. Novikov
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

import os, sys, traceback
import webbrowser
from base64 import b64decode

import wal

from uc2 import uc2const, libimg
from uc2.utils.fs import path_unicode
from uc2.application import UCApplication
from uc2.formats import data, get_saver_by_id, get_loader

from sk1 import _, config, events, modes, dialogs, appconst
from sk1 import app_plugins, app_actions
from sk1.app_conf import AppData
from sk1.app_history import AppHistoryManager
from sk1.app_insp import AppInspector
from sk1.app_proxy import AppProxy
from sk1.parts.mw import AppMainWindow
from sk1.parts.artprovider import create_artprovider
from sk1.app_cms import AppColorManager
from sk1.app_palettes import AppPaletteManager
from sk1.document import PD_Presenter
from sk1.clipboard import AppClipboard

class pdApplication(wal.Application, UCApplication):

	appdata = None
	history = None

	actions = {}
	plugins = {}
	docs = []
	current_doc = None
	doc_counter = 0

	proxy = None
	insp = None
	mw = None
	default_cms = None
	artprovider = None
	cursors = None
	mdiarea = None
	plg_area = None

	def __init__(self, path):

		self.path = path

		wal.Application.__init__(self)
		UCApplication.__init__(self, path)

		self.appdata = AppData(self)
		config.load(self.appdata.app_config)
		config.resource_dir = os.path.join(path_unicode(self.path), 'share')
		plg_dir = os.path.join(self.path, 'share', 'pd_plugins')
		custom_plg_dir = self.appdata.plugin_dir
		config.plugin_dirs = [plg_dir, custom_plg_dir]
		sys.path.insert(1, self.appdata.app_config)
		sys.path.insert(1, os.path.join(self.path, 'share'))
		config.app = self

		self.history = AppHistoryManager(self)

		self.artprovider = create_artprovider()
		self.cursors = modes.get_cursors()

		self.proxy = AppProxy(self)
		self.insp = AppInspector(self)
		self.plugins = app_plugins.scan_plugins(self)
		self.actions = app_actions.create_actions(self)

		self.default_cms = AppColorManager(self)
		self.palettes = AppPaletteManager(self)
		self.clipboard = AppClipboard(self)

		self.mw = AppMainWindow(self)
		self.mw.set_global_shortcuts(self.actions)

		self.proxy.update()
		self.insp.update()
		if not wal.is_msw(): events.emit(events.NO_DOCS)

	def load_plugins(self):
		if config.active_plugins:
			for item in config.active_plugins:
				try:
					self.mw.mdi.plg_area.show_plugin(item)
				except: pass

	def call_after(self, *args):
		if self.docs: return
		if config.new_doc_on_start:
			self.load_plugins()
			self.new()
		else:
			txt = _('To start, create new document or open existing')
			events.emit(events.APP_STATUS, txt)
			self.load_plugins()
			if wal.is_msw(): events.emit(events.NO_DOCS)
		self.update_actions()

	def stub(self, *args):pass

	def update_config(self):
		config.resource_dir = ''
		config.mw_size = self.mw.get_size()
		config.mw_maximized = self.mw.is_maximized()
		if self.mw.is_maximized(): config.mw_size = config.mw_min_size
		plugins = []
		for item in self.mw.mdi.plg_area.plugins:
			plugins.append(item.pid)
		config.active_plugins = plugins
		config.save(self.appdata.app_config)

	def exit(self, *args):
		if not self.insp.is_any_doc_not_saved(): self.mw.hide()
		if self.close_all():
			self.update_config()
			self.mw.destroy()
			self.Exit()
			return True
		return False

	def get_new_docname(self):
		self.doc_counter += 1
		return _('Untitled') + ' ' + str(self.doc_counter)

	def set_current_doc(self, doc):
		self.current_doc = doc
		self.current_doc.set_title()
		self.mw.mdi.set_active(doc)
		self.current_doc.canvas.set_focus()
		events.emit(events.DOC_CHANGED, doc)
		events.emit(events.SNAP_CHANGED)
		events.emit(events.APP_STATUS, _('Document is changed'))

	def new(self):
		doc = PD_Presenter(self)
		self.docs.append(doc)
		self.set_current_doc(doc)
		events.emit(events.APP_STATUS, _('New document created'))

	def new_from_template(self):
		msg = _('Select Template')
		doc_file = dialogs.get_open_file_name(self.mw, self,
								config.template_dir, msg)
		if os.path.lexists(doc_file) and os.path.isfile(doc_file):
			try:
				doc = PD_Presenter(self, doc_file, template=True)
			except:
				msg = _('Cannot parse file')
				msg = "%s '%s'" % (msg, doc_file) + '\n'
				msg += _('The file may be corrupted or not supported format')
				dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
				self.print_stacktrace()
				return
			self.docs.append(doc)
			config.template_dir = str(os.path.dirname(doc_file))
			self.set_current_doc(doc)
			events.emit(events.APP_STATUS, _('New document from template'))

	def open(self, doc_file='', silent=False):
		if not doc_file:
			doc_file = dialogs.get_open_file_name(self.mw, self, config.open_dir)
		if os.path.lexists(doc_file) and os.path.isfile(doc_file):
			try:
				doc = PD_Presenter(self, doc_file, silent)
			except:
				msg = _('Cannot open file')
				msg = "%s '%s'" % (msg, doc_file) + '\n'
				msg += _('The file may be corrupted or not supported format')
				dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
				self.print_stacktrace()
				return
			self.docs.append(doc)
			config.open_dir = str(os.path.dirname(doc_file))
			self.history.add_entry(doc_file)
			self.set_current_doc(doc)
			events.emit(events.APP_STATUS, _('Document opened'))

	def save(self, doc=''):
		if not doc:
			doc = self.current_doc
		if not doc.doc_file:
			return self.save_as()
		ext = os.path.splitext(self.current_doc.doc_file)[1]
		if not ext == "." + uc2const.FORMAT_EXTENSION[uc2const.SK2][0]:
			return self.save_as()
		if not os.path.lexists(os.path.dirname(self.current_doc.doc_file)):
			return self.save_as()

		try:
			self.make_backup(self.current_doc.doc_file)
			doc.save()
			self.history.add_entry(self.current_doc.doc_file, appconst.SAVED)
			events.emit(events.DOC_SAVED, doc)
		except:
			msg = _('Cannot save file')
			msg = "%s '%s'" % (msg, self.current_doc.doc_file) + '\n'
			msg += _('Please check file write permissions')
			dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
			self.print_stacktrace()
			return False
		events.emit(events.APP_STATUS, _('Document saved'))
		return True

	def save_as(self):
		doc_file = '' + self.current_doc.doc_file
		if not doc_file:
			doc_file = '' + self.current_doc.doc_name
		if not os.path.splitext(doc_file)[1] == "." + \
					uc2const.FORMAT_EXTENSION[uc2const.SK2][0]:
			doc_file = os.path.splitext(doc_file)[0] + "." + \
					uc2const.FORMAT_EXTENSION[uc2const.SK2][0]
		if not os.path.lexists(os.path.dirname(doc_file)):
			doc_file = os.path.join(config.save_dir,
								os.path.basename(doc_file))
		doc_file = dialogs.get_save_file_name(self.mw, self, doc_file,
											path_only=True)
		if doc_file:
			old_file = self.current_doc.doc_file
			old_name = self.current_doc.doc_name
			self.current_doc.set_doc_file(doc_file)
			try:
				self.make_backup(doc_file)
				self.current_doc.save()
			except:
				self.current_doc.set_doc_file(old_file, old_name)
				first = _('Cannot save document')
				msg = ("%s '%s'.") % (first, self.current_doc.doc_name) + '\n'
				msg += _('Please check file name and write permissions')
				dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
				self.print_stacktrace()
				return False
			config.save_dir = str(os.path.dirname(doc_file))
			self.history.add_entry(doc_file, appconst.SAVED)
			events.emit(events.DOC_SAVED, self.current_doc)
			events.emit(events.APP_STATUS, _('Document saved'))
			return True
		else:
			return False

	def save_selected(self):
		doc_file = '' + self.current_doc.doc_file
		if not doc_file:
			doc_file = '' + self.current_doc.doc_name
		if not os.path.splitext(doc_file)[1] == "." + \
					uc2const.FORMAT_EXTENSION[uc2const.SK2][0]:
			doc_file = os.path.splitext(doc_file)[0] + "." + \
					uc2const.FORMAT_EXTENSION[uc2const.SK2][0]
		if not os.path.lexists(os.path.dirname(doc_file)):
			doc_file = os.path.join(config.save_dir,
								os.path.basename(doc_file))
		doc_file = dialogs.get_save_file_name(self.mw, self, doc_file,
							_('Save selected objects only as...'),
							path_only=True)
		if doc_file:
			try:
				self.make_backup(doc_file)
				self.current_doc.save_selected(doc_file)
				self.history.add_entry(doc_file, appconst.SAVED)
			except:
				first = _('Cannot save document')
				msg = ("%s '%s'.") % (first, doc_file) + '\n'
				msg += _('Please check requested file format and write permissions')
				dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
				self.print_stacktrace()

	def save_all(self):
		for doc in self.docs:
			if self.insp.is_doc_not_saved(doc):
				self.save(doc)

	def close(self, doc=None):
		if not self.docs: return
		if doc is None: doc = self.current_doc
		if not doc == self.current_doc: self.set_current_doc(doc)

		if self.insp.is_doc_not_saved(doc):
			msg = _("Document '%s' has been modified.") % (doc.doc_name) + '\n'
			msg += _('Do you want to save your changes?')
			ret = dialogs.ync_dialog(self.mw, self.appdata.app_name, msg)

			if ret is None: return False
			if ret:
				if not self.save(): return False

		if doc in self.docs:
			self.docs.remove(doc)
			doc.close()
			events.emit(events.DOC_CLOSED)
			if not len(self.docs):
				self.current_doc = None
				events.emit(events.NO_DOCS)
				msg = _('To start create new or open existing document')
				events.emit(events.APP_STATUS, msg)
				self.mw.set_title()
			else:
				self.set_current_doc(self.docs[-1])
		return True

	def close_all(self):
		result = True
		if self.docs:
			while self.docs:
				result = self.close(self.docs[0])
				if not result: break
		return result

	def import_file(self):
		doc_file = dialogs.get_open_file_name(self.mw, self, config.import_dir,
											_('Select file to import'))
		if os.path.lexists(doc_file) and os.path.isfile(doc_file):
			try:
				ret = self.current_doc.import_file(doc_file)
				if not ret:
					msg = _('Cannot import graphics from file:')
					msg = "%s\n'%s'" % (msg, doc_file) + '\n'
					msg += _('It seems the document is empty or contains unsupported objects.')
					dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
				config.import_dir = str(os.path.dirname(doc_file))
			except:
				msg = _('Cannot import file')
				msg = "%s '%s'" % (msg, doc_file) + '\n'
				msg += _('The file may be corrupted or not supported format')
				dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
				self.print_stacktrace()

	def export_as(self):
		doc_file = '' + self.current_doc.doc_file
		if not doc_file:
			doc_file = '' + self.current_doc.doc_name
		doc_file = os.path.splitext(doc_file)[0]
		doc_file = os.path.join(config.export_dir,
								os.path.basename(doc_file))
		doc_file = dialogs.get_save_file_name(self.mw, self, doc_file,
							_('Export document As...'),
							file_types=data.SAVER_FORMATS[1:], path_only=True)
		if doc_file:
			try:
				self.make_backup(doc_file, True)
				self.current_doc.export_as(doc_file)
			except:
				first = _('Cannot save document')
				msg = ("%s '%s'.") % (first, self.current_doc.doc_name) + '\n'
				msg += _('Please check file name and write permissions')
				dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
				self.print_stacktrace()
				return
			config.export_dir = str(os.path.dirname(doc_file))
			events.emit(events.APP_STATUS, _('Document is successfully exported'))

	def extract_bitmap(self):
		doc_file = 'image'
		doc_file = os.path.join(config.save_dir, doc_file)
		doc_file = dialogs.get_save_file_name(self.mw, self, doc_file,
							_('Extract selected bitmap as...'),
							file_types=[data.TIF], path_only=True)
		if doc_file:
			try:
				pixmap = self.current_doc.selection.objs[0]
				libimg.extract_bitmap(pixmap, doc_file)
			except:
				first = _('Cannot save document')
				msg = ("%s '%s'.") % (first, self.current_doc.doc_name) + '\n'
				msg += _('Please check file name and write permissions')
				dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
				self.print_stacktrace()
				return
			config.save_dir = str(os.path.dirname(doc_file))
			events.emit(events.APP_STATUS, _('Bitmap is successfully extracted'))

	def export_palette(self, palette, parent=None):
		if not parent: parent = self.mw
		doc_file = '' + palette.model.name
		doc_file = os.path.splitext(doc_file)[0]
		doc_file = os.path.join(config.export_dir, os.path.basename(doc_file))
		ret = dialogs.get_save_file_name(parent, self, doc_file,
							_('Export palette as...'),
							file_types=data.PALETTE_SAVERS)
		if not ret: return
		doc_file, index = ret
		saver_id = data.PALETTE_SAVERS[index]

		if doc_file:

			if not os.path.splitext(doc_file)[1] == "." + \
						uc2const.FORMAT_EXTENSION[saver_id][0]:
				doc_file = os.path.splitext(doc_file)[0] + "." + \
						uc2const.FORMAT_EXTENSION[saver_id][0]

			try:
				saver = get_saver_by_id(saver_id)
				if saver is None:
					raise IOError(_('Unknown file format is requested for export!'),
								 doc_file)

				self.make_backup(doc_file, True)

				pd = dialogs.ProgressDialog(_('Exporting...'), parent)
				ret = pd.run(saver, [palette, doc_file, None, False, True], False)
				if ret:
					if not pd.error_info is None:
						pd.destroy()
						raise IOError(*pd.error_info)
					pd.destroy()
				else:
					pd.destroy()
					raise IOError(_('Error while exporting'), doc_file)

			except IOError:
				raise IOError(*sys.exc_info())

			config.export_dir = str(os.path.dirname(doc_file))
			events.emit(events.APP_STATUS, _('Palette is successfully exported'))

	def import_palette(self, parent=None):
		if not parent: parent = self.mw
		doc_file = dialogs.get_open_file_name(parent, self, config.import_dir,
											_('Select palette to import'),
											file_types=data.PALETTE_LOADERS)
		if os.path.lexists(doc_file) and os.path.isfile(doc_file):
			try:
				palette = None
				loader = get_loader(doc_file)
				pd = dialogs.ProgressDialog(_('Opening file...'), parent)
				ret = pd.run(loader, [self.appdata, doc_file, None, False, True])
				if ret:
					if pd.result is None:
						pd.destroy()
						raise IOError(*pd.error_info)

					palette = pd.result
					ret = True
					pd.destroy()
				else:
					pd.destroy()
					raise IOError(_('Error while opening'), doc_file)

				if palette:
					self.palettes.add_palette(palette)
					config.import_dir = str(os.path.dirname(doc_file))
					msg = _('Palette is successfully imported')
					events.emit(events.APP_STATUS, msg)
					return palette.model.name

			except:
				msg = _('Cannot import file')
				msg = "%s '%s'" % (msg, doc_file) + '\n'
				msg += _('The file may be corrupted or not supported format')
				dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
				self.print_stacktrace()
		return None

	def extract_pattern(self, parent, pattern, eps=False):
		img_file = 'image'
		img_file = os.path.join(config.save_dir, img_file)
		file_types = [data.TIF]
		if eps: file_types = [data.EPS]
		img_file = dialogs.get_save_file_name(parent, self, img_file,
							_('Save pattern as...'),
							file_types=file_types, path_only=True)
		if img_file:
			try:
				fobj = open(img_file, 'wb')
				fobj.write(b64decode(pattern))
				fobj.close()
			except:
				first = _('Cannot save pattern from')
				msg = ("%s '%s'.") % (first, self.current_doc.doc_name) + '\n'
				msg += _('Please check file name and write permissions')
				dialogs.error_dialog(parent, self.appdata.app_name, msg)
				self.print_stacktrace()
				return
			config.save_dir = str(os.path.dirname(img_file))

	def import_pattern(self, parent=None):
		if not parent: parent = self.mw
		img_file = dialogs.get_open_file_name(parent, self, config.import_dir,
				_('Select pattern to load'), file_types=data.PATTERN_FORMATS)
		if os.path.lexists(img_file) and os.path.isfile(img_file):
			first = _('Cannot load pattern for')
			msg = ("%s '%s'.") % (first, self.current_doc.doc_name) + '\n'
			msg += _('The file may be corrupted or not supported format')
			try:
				if libimg.check_image(img_file):
					config.import_dir = str(os.path.dirname(img_file))
					return img_file
				else:
					dialogs.error_dialog(parent, self.appdata.app_name, msg)
					self.print_stacktrace()
			except:
				dialogs.error_dialog(parent, self.appdata.app_name, msg)
				self.print_stacktrace()

		return None

	def make_backup(self, doc_file, export=False):
		if not export and not config.make_backup:return
		if export and not config.make_export_backup:return
		if os.path.lexists(doc_file):
			if os.path.lexists(doc_file + '~'):
				os.remove(doc_file + '~')
			os.rename(doc_file, doc_file + '~')

	def print_stacktrace(self):
		if config.print_stacktrace:
			print sys.exc_info()[1].__str__()
			print traceback.format_tb(sys.exc_info()[2])

	def open_url(self, url):
		webbrowser.open(url, new=1, autoraise=True)
		msg = _('Requested page is opened in default browser')
		events.emit(events.APP_STATUS, msg)
