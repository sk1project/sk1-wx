# -*- coding: utf-8 -*-
#
#  Copyright (C) 2017 by Igor E. Novikov
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
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import sys

from uc2.utils.fs import path_system, path_unicode


class SerializedConfig(object):
    """
    Represents parent class for application configs.
    """
    filename = ''

    def update(self, cnf=None):
        cnf = cnf or {}
        if cnf:
            for key in cnf.keys():
                if hasattr(self, key):
                    setattr(self, key, cnf[key])

    def load(self, filename=None):
        self.filename = filename
        if os.path.lexists(filename):
            try:
                fileobj = open(filename, "r")
            except Exception:
                print 'ERROR>>> cannot read preferences from %s' % filename
                print sys.exc_info()[1].__str__()
                print sys.exc_info()[2].__str__()
                return

            while True:
                line = fileobj.readline()
                if line.startswith('<?xml'):
                    break
                if not line:
                    break
                if line.startswith('#'):
                    continue
                line = path_system('self.%s' % line)
                try:
                    code = compile(line, '<string>', 'exec')
                    exec code
                except Exception:
                    print 'ERROR>>> %s' % line
            fileobj.close()

    def save(self, filename=None):
        if self.filename and filename is None:
            filename = self.filename
        if len(self.__dict__) == 0 or filename is None:
            return

        try:
            fileobj = open(filename, 'w')
        except Exception:
            print 'ERROR>>> cannot write preferences into %s' % filename
            return

        defaults = SerializedConfig.__dict__
        items = self.__dict__.items()
        items.sort()
        for key, value in items:
            if key in defaults and defaults[key] == value:
                continue
            if key in ['filename', 'app']:
                continue
            line = path_unicode('%s = %s\n' % (key, value.__repr__()))
            fileobj.write(line)
        fileobj.close()
