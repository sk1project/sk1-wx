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

import os

from uc2 import _
from uc2 import uc2const
from uc2 import events, msgconst
from uc2.utils.fs import get_file_extension

from uc2.formats import data


def get_loader(path, experimental=False):

	if not os.path.lexists(path): return None
	if not os.path.isfile(path):return None

	ext = get_file_extension(path)
	loader = None
	ld_formats = [] + data.LOADER_FORMATS

	msg = _('Start to search for loader by file extension %s') % (ext.__str__())
	events.emit(events.MESSAGES, msgconst.INFO, msg)

	if experimental:
		ld_formats += data.EXPERIMENTAL_LOADERS
	for format in ld_formats:
		if ext in uc2const.FORMAT_EXTENSION[format]:
			if data.CHECKERS[format](path):
				loader = data.LOADERS[format]
				break
	if loader is None:

		msg = _('Loader is not found or not suitable for %s') % (path)
		events.emit(events.MESSAGES, msgconst.WARNING, msg)
		msg = _('Start to search loader by file content')
		events.emit(events.MESSAGES, msgconst.INFO, msg)

		for format in ld_formats:
			checker = data.CHECKERS[format]
			if not checker is None:
				if checker(path):
					loader = data.LOADERS[format]
					break
	if loader is None:
		msg = _('Loader is not found for %s') % (path)
		events.emit(events.MESSAGES, msgconst.ERROR, msg)
	else:
		msg = _('Loader is found for %s') % (path)
		events.emit(events.MESSAGES, msgconst.OK, msg)
	return loader

def get_saver(path, experimental=False):
	ext = get_file_extension(path)
	saver = None
	sv_formats = [] + data.SAVER_FORMATS

	msg = _('Start to search saver by file extension %s') % (ext.__str__())
	events.emit(events.MESSAGES, msgconst.INFO, msg)

	if experimental:
		sv_formats += data.EXPERIMENTAL_SAVERS
	for format in sv_formats:
		if ext in uc2const.FORMAT_EXTENSION[format]:
			saver = data.SAVERS[format]
			break
	if saver is None:
		msg = _('Saver is not found for %s file format') % (ext.__str__())
		events.emit(events.MESSAGES, msgconst.ERROR, msg)
	else:
		msg = _('Saver is found for extension %s') % (ext.__str__())
		events.emit(events.MESSAGES, msgconst.OK, msg)
	return saver


def _test():
	print get_saver('/home/igor/TEST/canada.pdxf')


if __name__ == '__main__':
    _test()
