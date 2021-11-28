# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013 by Ihor E. Novikov
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
from copy import deepcopy

from sk1 import _, events, modes
from sk1.dialogs import ProgressDialog
from sk1.document.api import PresenterAPI
from sk1.document.canvas import AppCanvas
from sk1.document.eventloop import EventLoop
from sk1.document.ruler import Ruler, RulerCorner
from sk1.document.selection import Selection
from sk1.document.snapping import SnapManager
from uc2 import uc2const
from uc2.formats import get_loader, get_saver
from uc2.formats.sk2.sk2_presenter import SK2_Presenter
from uc2.utils.fsutils import change_file_extension

LOG = logging.getLogger(__name__)


class SK1Presenter:
    api = None
    doc_presenter = None
    doc_file = ''
    doc_name = ''

    model = None
    cms = None
    methods = None
    renderer = None
    active_page = None
    active_layer = None

    saved = True

    eventloop = None
    canvas = None
    selection = None
    traced_objects = None
    snap = None
    text_obj_style = None

    def __init__(self, app, doc_file='', silent=False, template=False):
        self.app = app

        self.eventloop = EventLoop(self)
        self.selection = Selection(self)

        loader = None
        if doc_file:
            loader = get_loader(doc_file)
            if not loader:
                raise IOError(_('Loader is not found for <%s>') % doc_file)

        if loader and silent:
            self.doc_presenter = loader(app.appdata, doc_file)
        elif doc_file and not silent:
            pd = ProgressDialog(_('Opening file...'), self.app.mw)
            try:
                self.doc_presenter = pd.run(loader, [app.appdata, doc_file])
                if not self.doc_presenter:
                    LOG.error('Cannot load <%s>', doc_file)
                    raise IOError(_('Cannot load <%s>') % doc_file)
            except Exception:
                raise
            finally:
                pd.destroy()

            if not template:
                self.doc_file = self.doc_presenter.doc_file
                self.doc_name = os.path.basename(self.doc_file)
                ext = uc2const.FORMAT_EXTENSION[uc2const.SK2][0]
                self.doc_name = change_file_extension(self.doc_name, ext)
            else:
                self.doc_name = self.app.get_new_docname()
                self.doc_presenter.doc_file = ''
        else:
            self.doc_presenter = SK2_Presenter(app.appdata)
            self.doc_name = self.app.get_new_docname()

        self.methods = self.doc_presenter.methods
        self.model = self.doc_presenter.model
        self.set_active_page()

        self.cms = self.doc_presenter.cms
        # self.app.default_cms.registry_cm(self.cms)

        self.api = PresenterAPI(self)
        self.corner = RulerCorner(self)
        self.hruler = Ruler(self, vertical=False)
        self.vruler = Ruler(self)
        self.canvas = AppCanvas(self)
        self.canvas.set_mode()
        self.eventloop.connect(self.eventloop.DOC_MODIFIED, self.modified)
        self.snap = SnapManager(self)

    def set_title(self):
        title = self.doc_name
        title = title + '*' if not self.saved else title
        self.app.mdi.set_tab_title(self, title)
        if self == self.app.current_doc:
            self.app.mw.set_title(title)

    def set_doc_file(self, doc_file, doc_name=''):
        self.doc_file = doc_file
        if doc_name:
            self.doc_name = doc_name
        else:
            self.doc_name = os.path.basename(self.doc_file)
        self.set_title()

    def save(self):
        pd = ProgressDialog(_('Saving file...'), self.app.mw)
        try:
            saver = get_saver(self.doc_file)
            if saver is None:
                msg = _('Unknown file format is requested for saving <%s>')
                raise IOError(msg % self.doc_file)
            pd.run(saver, [self.doc_presenter, self.doc_file])
        except Exception:
            raise
        finally:
            pd.destroy()
        self.reflect_saving()

    def save_selected(self, doc_file):
        doc = SK2_Presenter(self.app.appdata)
        origin = self.doc_presenter.model.doc_origin
        doc.methods.set_doc_origin(origin)
        doc_units = self.doc_presenter.model.doc_units
        doc.methods.set_doc_units(doc_units)
        page = doc.methods.get_page()
        page_format = deepcopy(self.active_page.page_format)
        doc.methods.set_page_format(page, page_format)
        objs = []
        for item in self.selection.objs:
            objs.append(item.copy())
        layer = doc.methods.get_layer(page)
        layer.childs = objs

        pd = ProgressDialog(_('Saving file...'), self.app.mw)
        try:
            saver = get_saver(doc_file)
            if saver is None:
                msg = _('Unknown file format is requested for saving <%s>')
                raise IOError(msg % doc_file)
            pd.run(saver, [doc, doc_file])
        except Exception:
            raise
        finally:
            pd.destroy()
            doc.close()

    def close(self):
        # self.app.default_cms.unregistry_cm(self.cms)
        self.eventloop.destroy()
        self.api.destroy()
        self.doc_presenter.close()
        for item in [self.canvas, self.corner, self.vruler, self.hruler,
                     self.selection, self.snap]:
            item.destroy()

        items = self.__dict__.keys()
        for item in items:
            self.__dict__[item] = None

    def import_file(self, doc_file):
        retval = True

        pd = ProgressDialog(_('Importing...'), self.app.mw)
        try:
            loader = get_loader(doc_file)
            if not loader:
                raise IOError(_('Loader is not found for <%s>') % doc_file)
            doc_presenter = pd.run(loader, [self.app.appdata, doc_file])
            if not doc_presenter:
                LOG.error('Cannot load <%s>', doc_file)
                raise IOError(_('Cannot load <%s>') % doc_file)
        except Exception:
            raise
        finally:
            pd.destroy()

        pages = doc_presenter.methods.get_pages()
        if len(pages) == 1:
            page = doc_presenter.methods.get_page()
            objs = []
            for layer in page.childs:
                for child in layer.childs:
                    objs.append(child)
                layer.childs = []
            if objs:
                self.api.paste_selected(objs)
            else:
                retval = False
        else:
            pages = doc_presenter.methods.get_pages()
            pages_obj = doc_presenter.methods.get_pages_obj()
            pages_obj.childs = []
            if pages:
                self.api.add_pages(pages)
            else:
                retval = False
        doc_presenter.close()
        return retval

    def export_as(self, doc_file):
        pd = ProgressDialog(_('Exporting...'), self.app.mw)
        try:
            saver = get_saver(doc_file)
            if saver is None:
                msg = _('Unknown file format is requested for export <%s>')
                raise IOError(msg % doc_file)
            pd.run(saver, [self.doc_presenter, doc_file])
        except Exception:
            raise
        finally:
            pd.destroy()

    def modified(self, *args):
        self.saved = False
        self.set_title()
        events.emit(events.DOC_MODIFIED, self)
        return args

    def reflect_saving(self):
        self.saved = True
        self.set_title()
        self.api.save_mark()
        events.emit(events.DOC_SAVED, self)

    def set_active_page(self, page_num=0):
        self.active_page = self.doc_presenter.methods.get_page(page_num)
        self.set_active_layer(self.active_page)

    def get_pages(self):
        return self.doc_presenter.methods.get_pages()

    def next_page(self):
        pages = self.get_pages()
        if pages.index(self.active_page) < len(pages) - 1:
            self.api.set_active_page(pages.index(self.active_page) + 1)
            self.eventloop.emit(self.eventloop.PAGE_CHANGED)
            events.emit(events.PAGE_CHANGED, self)

    def previous_page(self):
        pages = self.get_pages()
        if pages.index(self.active_page):
            self.api.set_active_page(pages.index(self.active_page) - 1)
            self.eventloop.emit(self.eventloop.PAGE_CHANGED)
            events.emit(events.PAGE_CHANGED, self)

    def goto_page(self, index):
        pages = self.get_pages()
        current_index = pages.index(self.active_page)
        if index >= 0 and index != current_index:
            self.api.set_active_page(index)
            self.eventloop.emit(self.eventloop.PAGE_CHANGED)
            events.emit(events.PAGE_CHANGED, self)

    def set_active_layer(self, page, layer_num=-1):
        dp = self.doc_presenter
        if layer_num == -1:
            self.active_layer = dp.methods.get_active_layers(page)[-1]
        else:
            self.active_layer = dp.methods.get_layer(page, layer_num)

    def get_layers(self, page=None):
        if page is None:
            page = self.active_page
        return self.methods.get_layers(page)

    def get_editable_layers(self, page=None):
        if page is None:
            page = self.active_page
        layers = []
        for layer in self.methods.get_desktop_layers():
            if layer.properties[0] and layer.properties[1]:
                layers.append(layer)
        for layer in page.childs:
            if layer.properties[0] and layer.properties[1]:
                layers.append(layer)
        for layer in self.methods.get_master_layers():
            if layer.properties[0] and layer.properties[1]:
                layers.append(layer)
        return layers

    def get_visible_layers(self, page=None):
        if page is None:
            page = self.active_page
        layers = []
        for layer in self.methods.get_desktop_layers():
            if layer.properties[0]:
                layers.append(layer)
        for layer in page.childs:
            if layer.properties[0]:
                layers.append(layer)
        for layer in self.methods.get_master_layers():
            if layer.properties[0]:
                layers.append(layer)
        return layers

    def get_page_size(self, page=None):
        if page is None:
            page = self.active_page
        w, h = page.page_format[1]
        return w, h

    def get_selected_objs(self):
        ret = []
        if self.selection.objs:
            ret += self.selection.objs
        elif self.canvas.mode in modes.EDIT_MODES:
            if self.canvas.controller.target:
                ret.append(self.canvas.controller.target)
        return ret
