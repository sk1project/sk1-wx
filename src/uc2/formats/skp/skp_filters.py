# -*- coding: utf-8 -*-
#
#  Copyright (C) 2015 by Igor E. Novikov
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

from uc2 import cms, uc2const
from uc2.formats.generic_filters import AbstractLoader, AbstractSaver
from uc2.formats.skp.skp_const import SKP_ID

LOG = logging.getLogger(__name__)


class SKP_Loader(AbstractLoader):
    name = 'SKP_Loader'
    stop_flag = False
    line = None

    def do_load(self):
        self.fileptr.readline()
        while True:
            self.line = self.fileptr.readline()
            if not self.line:
                break
            self.line = self.line.rstrip('\r\n')
            self.check_loading()
            if self.line:
                try:
                    code = compile('self.' + self.line, '<string>', 'exec')
                    exec code

                except Exception as e:
                    LOG.error('Parsing error in "%s"', self.line)
                    LOG.error('Error traceback: %s', e)
                if self.stop_flag:
                    break

    def palette(self):
        self.stop_flag = False

    def set_name(self, name):
        self.model.name = name

    def set_source(self, source):
        self.model.source = source

    def add_comments(self, txt):
        self.model.comments += txt + os.linesep

    def set_columns(self, val):
        self.model.columns = val

    def color(self, color):
        if len(color)>3 and isinstance(color[3], unicode):
            color[3] = color[3].encode('utf-8')
        self.model.colors.append(color)

    def hexcolor(self, hexcolor, name=''):
        rgb = cms.hexcolor_to_rgb(hexcolor)
        name = name or hexcolor
        name = name.encode('utf-8') if isinstance(name, unicode) else name
        self.model.colors.append([uc2const.COLOR_RGB, rgb, 1.0, name])

    def rgbcolor(self, r, g, b, name=''):
        rgb = cms.val_255_to_dec([r, g, b])
        name = name or cms.rgb_to_hexcolor(rgb)
        name = name.encode('utf-8') if isinstance(name, unicode) else name
        self.model.colors.append([uc2const.COLOR_RGB, rgb, 1.0, name])

    def palette_end(self):
        self.stop_flag = True


class SKP_Saver(AbstractSaver):
    name = 'SKP_Saver'

    def do_save(self):
        self.writeln(SKP_ID)
        self.writeln('palette()')
        self.writeln('set_name(%s)' % self.field_to_str(self.model.name))
        self.writeln('set_source(%s)' % self.field_to_str(self.model.source))
        for item in self.model.comments.splitlines():
            self.writeln('add_comments(%s)' % self.field_to_str(item))
        self.writeln('set_columns(%s)' % self.field_to_str(self.model.columns))
        for item in self.model.colors:
            self.writeln('color(%s)' % self.field_to_str(item))
        self.writeln('palette_end()')
