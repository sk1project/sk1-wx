# -*- coding: utf-8 -*-
#
#  Copyright (C) 2009-2019 by Maxim S. Barabash
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


from uc2.formats.generic_filters import AbstractLoader, AbstractSaver
from uc2.formats.edr_pal import EDR_Palette


class DST_Loader(AbstractLoader):
    name = 'DST_Loader'

    def do_load(self):
        self.presenter.palette = EDR_Palette(self.filepath)
        self.model.parse(self)


class DST_Saver(AbstractSaver):
    name = 'DST_Saver'

    def do_save(self):
        self.fileptr.write(self.model.get_content())
