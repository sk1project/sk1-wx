# -*- coding: utf-8 -*-
#
#  Copyright (C) 2012-2017 by Igor E. Novikov
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

from uc2 import _, uc2const
from uc2 import events, msgconst
from uc2.utils import fs, fsutils

LOG = logging.getLogger(__name__)


class ModelObject(object):
    """
    Abstract parent class for all model
    objects. Provides common object properties.
    """
    cid = 0
    parent = None
    config = None
    childs = []

    def destroy(self):
        for child in self.childs:
            child.destroy()
        for item in self.__dict__.keys():
            self.__dict__[item] = None

    def update(self):
        pass

    def update_for_sword(self):
        pass

    def do_update(self, presenter=None, action=False):
        for child in self.childs:
            child.parent = self
            child.config = self.config
            child.do_update(presenter, action)
        self.update()
        if action:
            self.update_for_sword()

    def add(self, child):
        self.childs.append(child)

    def remove(self, child):
        if child in self.childs:
            self.childs.remove(child)

    def count(self):
        val = len(self.childs)
        for child in self.childs:
            val += child.count()
        return val

    def resolve(self):
        if self.childs:
            return False, 'Node', ''
        return True, 'Leaf', ''


class TextModelObject(ModelObject):
    properties = []
    string = ''
    end_string = ''


GENERIC_TAGS = ['cid', 'childs', 'parent', 'config', 'tag']
IDENT = '\t'


class TaggedModelObject(ModelObject):
    tag = ''


class BinaryModelObject(ModelObject):
    chunk = ''
    cache_fields = []

    def save(self, saver):
        saver.write(self.chunk)
        for child in self.childs:
            child.save(saver)


class ModelPresenter(object):
    """
    Abstract parent class for all model
    presenters. Provides common functionality.
    """

    cid = 0
    model_type = uc2const.GENERIC_MODEL
    config = None
    doc_dir = ''
    doc_file = ''
    doc_id = ''
    model = None

    loader = None
    saver = None
    methods = None
    obj_num = 0

    def new(self):
        pass

    def load(self, filename=None, fileptr=None):
        if filename and fsutils.lexists(filename):
            self.doc_file = filename
        elif not fileptr:
            msg = _('Error while loading:') + ' ' + _('No file')
            self.send_error(msg)
            raise IOError(msg)

        try:
            self.parsing_msg(0.03)
            self.send_info(_('Parsing in progress...'))
            self.model = self.loader.load(self, filename, fileptr)
        except Exception:
            self.close()
            LOG.error('Error loading %s', filename)
            raise

        model_name = uc2const.FORMAT_NAMES[self.cid]
        self.send_ok(_('<%s> document model is created') % model_name)
        self.update()

    def update(self, action=False):
        if self.model is not None:
            self.obj_num = self.model.count() + 1
            self.update_msg(0.0)
            try:
                self.model.config = self.config
                self.model.do_update(self, action)
            except Exception:
                LOG.error(_('Error updating document model'))
                raise

            model_name = uc2const.FORMAT_NAMES[self.cid]
            msg = _('<%s> document model is updated successfully') % model_name
            self.send_progress_message(msg, 0.99)
            self.send_ok(msg)

    def save(self, filename=None, fileptr=None):
        if filename:
            self.doc_file = filename
        elif not fileptr:
            msg = _('Error while saving:') + ' ' + _('No file object')
            self.send_error(msg)
            raise IOError(msg)

        try:
            self.saving_msg(0.03)
            self.send_info(_('Saving is started...'))
            self.saver.save(self, filename, fileptr)
        except Exception:
            msg = _('Error while saving') + ' ' + filename + ' %s'
            LOG.error(msg)
            raise

        model_name = uc2const.FORMAT_NAMES[self.cid]
        msg = _('<%s> document model is saved successfully') % model_name
        self.send_progress_message(msg, 0.95)
        self.send_ok(msg)

    def close(self):
        filename = self.doc_file
        self.doc_file = ''
        if self.model is not None:
            self.model.destroy()
        self.model = None
        filename = filename.encode('utf-8') \
            if isinstance(filename, unicode) else filename
        model_name = uc2const.FORMAT_NAMES[self.cid]
        self.send_ok(_('<%s> document model is destroyed for %s') %
                     (model_name, filename))

        if self.doc_dir and fsutils.lexists(self.doc_dir):
            try:
                fs.xremove_dir(fsutils.get_sys_path(self.doc_dir))
                self.send_ok(_('Cache is cleared for') + ' %s' % filename)
            except Exception as e:
                msg = _('Cache clearing is unsuccessful')
                self.send_error(msg)
                LOG.warn(msg + ' %s', e)

    def update_msg(self, val):
        model_name = uc2const.FORMAT_NAMES[self.cid]
        msg = _('%s model update in progress...') % model_name
        self.send_progress_message(msg, val)

    def parsing_msg(self, val):
        msg = _('Parsing in progress...')
        self.send_progress_message(msg, val)

    def saving_msg(self, val):
        msg = _('Saving in progress...')
        self.send_progress_message(msg, val)

    def send_progress_message(self, msg, val):
        events.emit(events.FILTER_INFO, msg, val)

    def send_ok(self, msg):
        events.emit(events.MESSAGES, msgconst.OK, msg)

    def send_info(self, msg):
        events.emit(events.MESSAGES, msgconst.INFO, msg)

    def send_error(self, msg):
        events.emit(events.MESSAGES, msgconst.ERROR, msg)


class TextModelPresenter(ModelPresenter):
    model_type = uc2const.TEXT_MODEL


class TaggedModelPresenter(ModelPresenter):
    model_type = uc2const.TAGGED_MODEL


class BinaryModelPresenter(ModelPresenter):
    model_type = uc2const.BINARY_MODEL
