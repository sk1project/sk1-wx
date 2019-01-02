# -*- coding: utf-8 -*-
#
#  Copyright (C) 2018 by Maxim S. Barabash
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

import re
import os
from uc2.formats.generic_filters import AbstractLoader, AbstractSaver
from . import figlib
from uc2.utils import fsutils

RX_MAGIC = r'^#FIG (?P<version>[0-9].[0-9])(?P<comment>.*$)'


class FIGLoader(AbstractLoader):
    name = 'FIGLoader'
    _comment = None
    stack = None
    version = None

    def do_load(self):
        self.stack = []
        line = self.readln()
        magic = re.match(RX_MAGIC, line)
        if magic and self.model:
            self.version = float(magic.groups()[0])
            self.model.parse(self)
        else:
            raise Exception('Not supported')

    def readln(self, strip=True):
        line = self.fileptr.readline()
        if strip:
            line = line.strip()
        return figlib.un_escape(line)

    def get_line(self, strip=True):
        while True:
            line = self.readln(strip=False)
            if not line:
                return
            if line.startswith('#'):
                self.append_comment(line[1:].strip())
            elif line != '\n':
                return line.strip() if strip else line

    def startswith_line(self, start):
        line = self.get_line() or ''
        return line.lower().startswith(start)

    def append_comment(self, line):
        if self._comment is None:
            self._comment = line
        else:
            self._comment += '\n' + line

    def pop_comment(self):
        comment, self._comment = self._comment, None
        return comment


class FIGSaver(AbstractSaver):
    name = 'FIGSaver'

    def do_save(self):
        doc_dir = os.path.dirname(self.presenter.doc_file)
        for filename, res in self.presenter.resources.items():
            self.save_resource(res, os.path.join(doc_dir, filename))
        self.model.save(self)

    def save_resource(self, res, filename):
        try:
            with fsutils.get_fileptr(filename, writable=True) as fileptr:
                fileptr.write(res)
                fileptr.close()
        except Exception:
            pass

    def write(self, data):
        AbstractSaver.write(self, figlib.escape(data))
