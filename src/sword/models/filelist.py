# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 by Igor E. Novikov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import gtk
import logging
import os

ICONS_CACHE = {}
ICON_THEME = gtk.icon_theme_get_default()
ICON_LIST = ICON_THEME.list_icons()

FOLDER_ICON = gtk.Image().render_icon(gtk.STOCK_DIRECTORY, gtk.ICON_SIZE_MENU)
FILE_ICON = gtk.Image().render_icon(gtk.STOCK_FILE, gtk.ICON_SIZE_MENU)

try:
    from gnomevfs import get_mime_type
except:
    get_mime_type = lambda path: FILE_ICON

LOG = logging.getLogger(__name__)


def get_imagename(mime):
    if mime in ICON_LIST:
        return mime
    mime1 = mime.replace('/', '-')
    if mime1 in ICON_LIST:
        return mime1
    mime2 = mime.replace('/', '-x-')
    if mime2 in ICON_LIST:
        return mime2
    return gtk.STOCK_FILE


def get_image(mime):
    icon = get_imagename(mime)
    if icon not in ICONS_CACHE.keys():
        ICONS_CACHE[icon] = ICON_THEME.load_icon(icon, 16, 0)
    return ICONS_CACHE[icon]


class FileListModel(gtk.ListStore):

    def __init__(self, cur_dir=None, file_types=None,
                 show_hidden=False, root=''):
        gtk.ListStore.__init__(self, gtk.gdk.Pixbuf, str)
        file_types = file_types or []

        self.root = root

        if len(file_types) == 1 and file_types[0] == '*':
            file_types = []

        if not cur_dir:
            self.dirname = os.path.expanduser('~')
        else:
            self.dirname = os.path.abspath(cur_dir)
        if not os.path.lexists(self.dirname):
            self.dirname = os.path.expanduser('~')

        self.files = []
        self.dirs = []
        for item in os.listdir(self.dirname):
            if item[0] == '.' and not show_hidden:
                continue
            else:
                if os.path.isdir(os.path.join(self.dirname, item)):
                    self.dirs.append(item)
                else:
                    ext = os.path.splitext(item)[1]
                    ext = ext[1:] if ext else ''
                    if file_types and ext not in file_types:
                        continue
                    self.files.append(item)

        self.files.sort()
        self.dirs.sort()

        sorted_files = []
        for item in self.files:
            try:
                path = os.path.join(self.dirname, item)
                mime = get_mime_type(path)
                sorted_files.append((get_image(mime), item))
            except RuntimeError:
                LOG.exception('Error in file MIME detection')
                sorted_files.append((FILE_ICON, item))
        self.files = sorted_files

        sorted_dirs = []
        for item in self.dirs:
            sorted_dirs.append((FOLDER_ICON, item))
        self.dirs = sorted_dirs

        self.files = self.dirs + self.files
        if self.root:
            if self.dirname == root:
                pass
            else:
                self.files = [(FOLDER_ICON, '..'), ] + self.files
        else:
            if not self.dirname == os.path.abspath(
                    os.path.join(self.dirname, '..')):
                self.files = [(FOLDER_ICON, '..'), ] + self.files
        for item in self.files:
            icon, text = item
            self.append((icon, text))

    def get_pathname(self, path):
        return os.path.join(self.dirname, self.files[path[0]][1])
