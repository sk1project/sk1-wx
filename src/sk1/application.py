# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013-2018 by Igor E. Novikov
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import os
import sys
import webbrowser
from base64 import b64decode

import uc2.events
import wal
from sk1 import _, config, events, modes, dialogs, appconst
from sk1 import app_plugins, app_actions
from sk1.app_cms import AppColorManager
from sk1.app_conf import AppData
from sk1.app_fsw import AppFileWatcher
from sk1.app_history import AppHistoryManager
from sk1.app_insp import AppInspector
from sk1.app_palettes import AppPaletteManager
from sk1.app_proxy import AppProxy
from sk1.app_stdout import StreamLogger
from sk1.clipboard import AppClipboard
from sk1.document.presenter import SK1Presenter
from sk1.parts.artprovider import create_artprovider
from sk1.parts.mw import AppMainWindow
from sk1.pwidgets import generate_fcache
from uc2 import uc2const, libimg, msgconst
from uc2.application import UCApplication
from uc2.formats import get_saver_by_id, get_loader
from uc2.utils import fsutils
from uc2.utils.fsutils import get_sys_path
from uc2.utils.mixutils import config_logging

LOG = logging.getLogger(__name__)


class SK1Application(wal.Application, UCApplication):
    appdata = None
    history = None

    actions = None
    plugins = None
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
    print_data = None
    log_filepath = None

    def __init__(self, path, cfgdir):

        self.path = path

        wal.Application.__init__(self)
        UCApplication.__init__(self, path, cfgdir, False)

        if wal.IS_WINXP:
            msg = _('WindowsXP platform is obsolete and not supported!')
            dialogs.error_dialog(self.mw, 'sK1', msg)
            sys.exit()

        self.appdata = AppData(self, cfgdir)
        log_level = config.log_level
        self.log_filepath = os.path.join(self.appdata.app_config_dir, 'sk1.log')
        config_logging(get_sys_path(self.log_filepath), log_level)
        sys.stderr = StreamLogger()
        LOG.info('Logging started')

        self.update_wal()
        plg_dir = os.path.join(self.path, 'share', 'pd_plugins')
        custom_plg_dir = self.appdata.plugin_dir
        config.plugin_dirs = [plg_dir, custom_plg_dir]
        sys.path.insert(1, get_sys_path(self.appdata.app_config_dir))
        sys.path.insert(1, get_sys_path(os.path.join(self.path, 'share')))
        config.app = self
        LOG.info('Config is updated')

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
        LOG.info('Application is initialized')
        uc2.events.connect(uc2.events.MESSAGES, self.uc2_event_logging)
        events.connect(events.APP_STATUS, self.sk1_event_logging)
        self.fsw = AppFileWatcher(self, self.mw)

        if wal.IS_WX2:
            events.emit(events.NO_DOCS)
        if config.make_font_cache_on_start:
            generate_fcache()

    def load_plugins(self):
        if config.active_plugins:
            for item in config.active_plugins:
                try:
                    self.mw.mdi.plg_area.show_plugin(item)
                except Exception as e:
                    LOG.warn('Cannot load plugin <%s> %s', item, e)

    def call_after(self, *args):
        if self.docs:
            return
        docs = self._get_docs()
        if config.new_doc_on_start and not docs:
            self.load_plugins()
            self.new()
        else:
            txt = _('To start, create new document or open existing')
            events.emit(events.APP_STATUS, txt)
            self.load_plugins()
            if not wal.IS_WX2:
                events.emit(events.NO_DOCS)
        self.update_actions()
        for item in docs:
            self.open(item)

    def _get_docs(self):
        docs = []
        if len(sys.argv) > 1:
            for item in sys.argv[1:]:
                if os.path.exists(item):
                    docs.append(fsutils.get_utf8_path(item))
        return docs

    def update_wal(self):
        wal.SPIN['overlay'] = config.spin_overlay
        wal.SPIN['sep'] = config.spin_sep
        if config.selected_text_bg:
            wal.UI_COLORS['selected_text_bg'] = () + config.selected_text_bg

    def update_config(self):
        config.resource_dir = ''
        w, h = self.mw.get_size()
        if wal.is_unity_16_04():
            h = max(h - 28, config.mw_min_size[1])
        config.mw_size = (w, h)
        config.mw_maximized = self.mw.is_maximized()
        if self.mw.is_maximized():
            config.mw_size = config.mw_min_size
        plugins = [item.pid for item in self.mw.mdi.plg_area.plugins]
        config.active_plugins = plugins
        if self.mw.mdi.plg_area.is_shown():
            w = self.mw.mdi.splitter.get_size()[0]
            val = self.mw.mdi.splitter.get_sash_position() - w
            if val < 0:
                config.sash_position = val
        config.save(self.appdata.app_config)

    def exit(self, *args):
        if self.close_all():
            self.mw.hide()
            self.update_config()
            self.mw.destroy()
            self.fsw.destroy()
            wal.Application.exit(self)
            LOG.info('Application terminated')
            return True
        return False

    def get_new_docname(self):
        self.doc_counter += 1
        doc_name = '%s %d' % (_('Untitled'), self.doc_counter)
        return doc_name

    def set_current_doc(self, doc):
        self.current_doc = doc
        self.mw.mdi.set_active(doc)
        self.current_doc.set_title()
        events.emit(events.DOC_CHANGED, doc)
        events.emit(events.SNAP_CHANGED)
        events.emit(events.APP_STATUS, _('Document is changed'))
        if not self.mw.mdi.is_shown():
            self.mw.show_mdi(True)

    def new(self):
        doc = SK1Presenter(self)
        self.docs.append(doc)
        self.set_current_doc(doc)
        events.emit(events.APP_STATUS, _('New document created'))

    def new_from_template(self):
        msg = _('Select Template')
        doc_file = dialogs.get_open_file_name(self.mw, config.template_dir, msg)
        if fsutils.isfile(doc_file):
            try:
                doc = SK1Presenter(self, doc_file, template=True)
            except Exception as e:
                msg = _('Cannot parse file:')
                msg = "%s\n'%s'" % (msg, doc_file) + '\n'
                msg += _('The file may be corrupted or not supported format')
                dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
                LOG.error('Cannot parse file <%s> %s', doc_file, e)
                return
            self.docs.append(doc)
            config.template_dir = str(os.path.dirname(doc_file))
            self.set_current_doc(doc)
            events.emit(events.APP_STATUS, _('New document from template'))

    def open(self, doc_file='', silent=False):
        doc_file = doc_file or \
                   dialogs.get_open_file_name(self.mw, config.open_dir)
        if doc_file and fsutils.isfile(doc_file):
            try:
                doc = SK1Presenter(self, doc_file, silent)

            except RuntimeError:
                msg = _('Cannot open file:')
                msg = "%s\n'%s'" % (msg, doc_file) + '\n'
                msg += _('The file contains newer SK2 format.\n')
                msg += _('Try updating sK1 application from '
                         'https://sk1project.net')
                dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
                LOG.error('Cannot open file <%s>: newer SK2 format.', doc_file)
                return
            except Exception as e:
                msg = _('Cannot open file:')
                msg = "%s\n'%s'" % (msg, doc_file) + '\n'
                msg += _('The file may be corrupted or not supported format')
                msg += '\n'
                msg += _('Details see in application logs.')
                dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
                LOG.error('Cannot open file <%s> %s', doc_file, e, exc_info=True)
                return
            self.docs.append(doc)
            config.open_dir = str(os.path.dirname(doc_file))
            self.history.add_entry(doc_file)
            self.set_current_doc(doc)
            events.emit(events.APP_STATUS, _('Document opened'))

    def save(self, doc=None):
        doc = doc or self.current_doc
        if not doc.doc_file:
            return self.save_as()
        ext = os.path.splitext(self.current_doc.doc_file)[1]
        if not ext == "." + uc2const.FORMAT_EXTENSION[uc2const.SK2][0]:
            return self.save_as()
        if not fsutils.exists(os.path.dirname(self.current_doc.doc_file)):
            return self.save_as()

        try:
            self.make_backup(self.current_doc.doc_file)
            doc.save()
            self.history.add_entry(self.current_doc.doc_file, appconst.SAVED)
            events.emit(events.DOC_SAVED, doc)
        except Exception as e:
            msg = _('Cannot save file:')
            msg = "%s\n'%s'" % (msg, self.current_doc.doc_file) + '\n'
            msg += _('Please check file write permissions')
            dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
            LOG.error('Cannot save file <%s> %s', self.current_doc.doc_file, e)
            return False
        events.emit(events.APP_STATUS, _('Document saved'))
        return True

    def save_as(self):
        doc_file = self.current_doc.doc_file
        doc_file = doc_file or self.current_doc.doc_name
        if os.path.splitext(doc_file)[1] != "." + \
                uc2const.FORMAT_EXTENSION[uc2const.SK2][0]:
            doc_file = os.path.splitext(doc_file)[0] + "." + \
                       uc2const.FORMAT_EXTENSION[uc2const.SK2][0]
        if not fsutils.exists(os.path.dirname(doc_file)):
            doc_file = os.path.join(config.save_dir,
                                    os.path.basename(doc_file))
        doc_file = dialogs.get_save_file_name(self.mw, doc_file, path_only=True)
        if doc_file:
            old_file = self.current_doc.doc_file
            old_name = self.current_doc.doc_name
            self.current_doc.set_doc_file(doc_file)
            try:
                self.make_backup(doc_file)
                self.current_doc.save()
            except Exception as e:
                self.current_doc.set_doc_file(old_file, old_name)
                first = _('Cannot save document:')
                msg = "%s\n'%s'." % (first, self.current_doc.doc_name) + '\n'
                msg += _('Please check file name and write permissions')
                dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
                LOG.error('Cannot save file <%s> %s', doc_file, e)
                return False
            config.save_dir = str(os.path.dirname(doc_file))
            self.history.add_entry(doc_file, appconst.SAVED)
            events.emit(events.DOC_SAVED, self.current_doc)
            events.emit(events.APP_STATUS, _('Document saved'))
            return True
        else:
            return False

    def save_selected(self):
        doc_file = self.current_doc.doc_file
        doc_file = doc_file or self.current_doc.doc_name
        if os.path.splitext(doc_file)[1] != "." + \
                uc2const.FORMAT_EXTENSION[uc2const.SK2][0]:
            doc_file = os.path.splitext(doc_file)[0] + "." + \
                       uc2const.FORMAT_EXTENSION[uc2const.SK2][0]
        if not fsutils.exists(os.path.dirname(doc_file)):
            doc_file = os.path.join(config.save_dir,
                                    os.path.basename(doc_file))
        msg = _('Save selected objects only as...')
        doc_file = dialogs.get_save_file_name(self.mw, doc_file, msg,
                                              path_only=True)
        if doc_file:
            try:
                self.make_backup(doc_file)
                self.current_doc.save_selected(doc_file)
                self.history.add_entry(doc_file, appconst.SAVED)
            except Exception as e:
                first = _('Cannot save document:')
                msg = "%s\n'%s'." % (first, doc_file) + '\n'
                msg += _('Please check requested file format '
                         'and write permissions')
                dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
                LOG.error('Cannot save file <%s> %s', doc_file, e)

    def save_all(self):
        for doc in self.docs:
            if self.insp.is_doc_not_saved(doc):
                self.save(doc)

    def close(self, doc=None):
        if not self.docs:
            return
        doc = doc or self.current_doc

        if self.insp.is_doc_not_saved(doc):
            if not doc == self.current_doc:
                self.set_current_doc(doc)

            msg = _("Document '%s' has been modified.") % doc.doc_name + '\n'
            msg += _('Do you want to save your changes?')
            ret = dialogs.ync_dialog(self.mw, self.appdata.app_name, msg)

            if ret is None:
                return False
            if ret:
                if not self.save():
                    return False

        if doc in self.docs:
            index = self.docs.index(doc)
            active = doc == self.current_doc
            self.docs.remove(doc)
            self.mdi.remove_doc(doc)
            doc.close()
            events.emit(events.DOC_CLOSED)
            if not len(self.docs):
                self.current_doc = None
                self.mw.show_mdi(False)
                events.emit(events.NO_DOCS)
                msg = _('To start, create new document or open existing')
                events.emit(events.APP_STATUS, msg)
                self.mw.set_title()
            elif active:
                index = index if len(self.docs) > index else -1
                self.set_current_doc(self.docs[index])
        return True

    def close_others(self):
        docs = [] + self.docs
        docs.remove(self.current_doc)
        for doc in docs:
            if not self.close(doc):
                return False
        return True

    def close_all(self):
        if self.docs:
            while self.docs:
                if not self.close(self.docs[0]):
                    return False
        return True

    def import_file(self, doc_file=None, point=None):
        msg = _('Select file to import')
        if not doc_file:
            doc_file = dialogs.get_open_file_name(self.mw,
                                                  config.import_dir, msg)
        if doc_file and fsutils.isfile(doc_file):
            try:
                ret = self.current_doc.import_file(doc_file)
                if not ret:
                    msg = _('Cannot import graphics from file:')
                    msg = "%s\n'%s'" % (msg, doc_file) + '\n'
                    msg += _('It seems the document is empty or '
                             'contains unsupported objects.')
                    dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
                    LOG.warn('Cannot import graphics from file <%s>', doc_file)
                elif point and self.current_doc.selection.bbox:
                    x0, y0 = self.current_doc.canvas.win_to_doc(point)
                    x1 = self.current_doc.selection.bbox[0]
                    y1 = self.current_doc.selection.bbox[-1]
                    dx = x0 - x1
                    dy = y0 - y1
                    self.current_doc.api.move_selected(dx, dy)

                config.import_dir = str(os.path.dirname(doc_file))
            except Exception as e:
                msg = _('Cannot import file:')
                msg = "%s\n'%s'" % (msg, doc_file) + '\n'
                msg += _('The file may be corrupted or not supported format')
                msg += '\n'
                msg += _('Details see in application logs.')
                dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
                LOG.warn('Cannot import file <%s>', doc_file, e)

    def export_as(self):
        doc_file = self.current_doc.doc_file
        doc_file = doc_file or self.current_doc.doc_name
        doc_file = os.path.splitext(doc_file)[0]
        doc_file = os.path.join(config.export_dir,
                                os.path.basename(doc_file))
        ftype = uc2const.SAVER_FORMATS[1:]
        doc_file = dialogs.get_save_file_name(self.mw, doc_file,
                                              _('Export document As...'),
                                              file_types=ftype, path_only=True)
        if doc_file:
            try:
                self.make_backup(doc_file, True)
                self.current_doc.export_as(doc_file)
            except Exception as e:
                first = _('Cannot save document:')
                msg = "%s\n'%s'." % (first, self.current_doc.doc_name) + '\n'
                msg += _('Please check file name and write permissions')
                dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
                LOG.warn('Cannot save file <%s>', doc_file, e)
                return
            config.export_dir = str(os.path.dirname(doc_file))
            msg = _('Document is successfully exported')
            events.emit(events.APP_STATUS, msg)

    def extract_bitmap(self):
        doc_file = 'image'
        doc_file = os.path.join(config.save_dir, doc_file)
        msg = _('Extract selected bitmap as...')
        doc_file = dialogs.get_save_file_name(self.mw, doc_file, msg,
                                              file_types=[uc2const.PNG],
                                              path_only=True)
        if doc_file:
            try:
                pixmap = self.current_doc.selection.objs[0]
                pixmap.handler.extract_bitmap(doc_file)
            except Exception as e:
                first = _('Cannot save bitmap:')
                msg = "%s\n'%s'." % (first, doc_file) + '\n'
                msg += _('Please check file name and write permissions')
                dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
                LOG.warn('Cannot save bitmap in <%s>', doc_file, e)
                return
            config.save_dir = str(os.path.dirname(doc_file))
            events.emit(events.APP_STATUS,
                        _('Bitmap is successfully extracted'))

    def export_palette(self, palette, parent=None):
        parent = parent or self.mw
        doc_file = palette.model.name
        doc_file = os.path.splitext(doc_file)[0]
        doc_file = os.path.join(config.export_dir, os.path.basename(doc_file))
        ret = dialogs.get_save_file_name(parent, doc_file,
                                         _('Export palette as...'),
                                         file_types=uc2const.PALETTE_SAVERS)
        if not ret:
            return
        doc_file, index = ret
        saver_id = uc2const.PALETTE_SAVERS[index]

        if doc_file:
            if not os.path.splitext(doc_file)[1] == "." + \
                   uc2const.FORMAT_EXTENSION[saver_id][0]:
                doc_file = os.path.splitext(doc_file)[0] + "." + \
                           uc2const.FORMAT_EXTENSION[saver_id][0]

            pd = dialogs.ProgressDialog(_('Exporting...'), parent)
            try:
                saver = get_saver_by_id(saver_id)
                if saver is None:
                    msg = _('Unknown file format is requested for export <%s>')
                    raise IOError(msg % doc_file)
                self.make_backup(doc_file, True)
                pd.run(saver, [palette, doc_file, None, False, True])
            except Exception as e:
                msg = _('Cannot export palette:')
                msg = "%s\n'%s'." % (msg, doc_file) + '\n'
                msg += _('Please check file name and write permissions')
                dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
                LOG.error('Cannot save bitmap in <%s>', doc_file, e)
                return
            finally:
                pd.destroy()

            config.export_dir = str(os.path.dirname(doc_file))
            msg = _('Palette is successfully exported')
            events.emit(events.APP_STATUS, msg)

    def import_palette(self, parent=None):
        parent = parent or self.mw
        file_types = uc2const.PALETTE_LOADERS
        doc_file = dialogs.get_open_file_name(parent, config.import_dir,
                                              _('Select palette to import'),
                                              file_types=file_types)
        if fsutils.isfile(doc_file):
            pd = dialogs.ProgressDialog(_('Opening file...'), parent)
            try:
                loader = get_loader(doc_file)
                if not loader:
                    raise IOError(_('Loader is not found for <%s>') % doc_file)
                palette = pd.run(loader,
                                 [self.appdata, doc_file, None, False, True])
                if not palette:
                    raise IOError(_('Error while opening'), doc_file)
                self.palettes.add_palette(palette)
                config.import_dir = str(os.path.dirname(doc_file))
                msg = _('Palette is successfully imported')
                events.emit(events.APP_STATUS, msg)
                return palette.model.name
            except Exception as e:
                msg = _('Cannot import file:')
                msg = "%s\n'%s'" % (msg, doc_file) + '\n'
                msg += _('The file may be corrupted or not supported format')
                msg += '\n'
                msg += _('Details see in application logs.')
                dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
                LOG.error('Cannot import file <%s> %s', doc_file, e)
            finally:
                pd.destroy()

    def extract_pattern(self, parent, pattern, eps=False):
        img_file = 'image'
        img_file = os.path.join(config.save_dir, img_file)
        file_types = [uc2const.EPS] if eps else [uc2const.TIF]
        img_file = dialogs.get_save_file_name(parent, img_file,
                                              _('Save pattern as...'),
                                              file_types=file_types,
                                              path_only=True)
        if img_file:
            try:
                fobj = fsutils.get_fileptr(img_file, True)
                fobj.write(b64decode(pattern))
                fobj.close()
            except Exception as e:
                first = _('Cannot save pattern from:')
                msg = "%s\n'%s'." % (first, self.current_doc.doc_name) + '\n'
                msg += _('Please check file name and write permissions')
                dialogs.error_dialog(parent, self.appdata.app_name, msg)
                LOG.error('Cannot save pattern in <%s> %s', img_file, e)
                return
            config.save_dir = str(os.path.dirname(img_file))

    def import_pattern(self, parent=None):
        parent = parent or self.mw
        file_types = uc2const.PATTERN_FORMATS
        img_file = dialogs.get_open_file_name(parent, config.import_dir,
                                              _('Select pattern to load'),
                                              file_types=file_types)
        if fsutils.isfile(img_file):
            first = _('Cannot load pattern for:')
            msg = "%s\n'%s'." % (first, self.current_doc.doc_name) + '\n'
            msg += _('The file may be corrupted or not supported format')
            msg += '\n'
            msg += _('Details see in application logs.')
            try:
                if libimg.check_image(img_file):
                    config.import_dir = str(os.path.dirname(img_file))
                    return img_file
                else:
                    dialogs.error_dialog(parent, self.appdata.app_name, msg)
                    LOG.error('Cannot load pattern <%s>', img_file)
            except Exception as e:
                dialogs.error_dialog(parent, self.appdata.app_name, msg)
                LOG.error('Cannot load pattern <%s> %s', img_file, e)

    def make_backup(self, doc_file, export=False):
        if not export and not config.make_backup:
            return
        if export and not config.make_export_backup:
            return
        if fsutils.exists(doc_file):
            if fsutils.exists(doc_file + '~'):
                os.remove(get_sys_path(doc_file + '~'))
            os.rename(get_sys_path(doc_file), get_sys_path(doc_file + '~'))

    def uc2_event_logging(self, *args):
        log_map = {
            msgconst.JOB: LOG.info,
            msgconst.INFO: LOG.info,
            msgconst.OK: LOG.info,
            msgconst.WARNING: LOG.warn,
            msgconst.ERROR: LOG.error,
            msgconst.STOP: LOG.critical,
        }
        log_map[args[0]](args[1])

    def sk1_event_logging(self, msg):
        LOG.info(msg)

    def open_url(self, url):
        webbrowser.open(url, new=1, autoraise=True)
        msg = _('Requested page was opened in the default browser')
        events.emit(events.APP_STATUS, msg)
