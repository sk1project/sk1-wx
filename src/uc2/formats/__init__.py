# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2012 by Igor E. Novikov
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

import os, sys

from uc2 import _
from uc2 import uc2const
from uc2 import events, msgconst
from uc2.utils.fs import get_file_extension
from uc2.formats.fallback import fallback_check, im_loader

from uc2.uc2const import SK1, SK2, SK, SVG, CDR, CDT, CDRZ, \
EPS, PDF, WMF, PLT, RIFF, XML

from uc2.uc2const import JPG, JP2, TIF, BMP, PCX, GIF, PNG, PPM, XBM, XPM

from uc2.uc2const import SKP, GPL, SCRIBUS_PAL, SOC, CPL, COREL_PAL, ASE, \
ACO, JCW


SIMPLE_LOADERS = []
BITMAP_LOADERS = [PNG, JPG, JP2, TIF, GIF, BMP, PCX, PPM, XBM, XPM]
MODEL_LOADERS = [SK2, SVG, WMF, PLT, SK1, SK, CDR, CDT] + BITMAP_LOADERS

PALETTE_LOADERS = [SKP, GPL, SCRIBUS_PAL, SOC, CPL, COREL_PAL, ASE, ACO, JCW]
EXPERIMENTAL_LOADERS = [RIFF, CDRZ, XML]

SIMPLE_SAVERS = []
PALETTE_SAVERS = [SKP, GPL, SCRIBUS_PAL, SOC, CPL, COREL_PAL, ASE, ACO, JCW]
MODEL_SAVERS = [SK2, SVG, WMF, PLT, PDF, PNG, SK1, SK, ]
EXPERIMENTAL_SAVERS = [RIFF, CDR, XML ]

PATTERN_FORMATS = [EPS, PNG, JPG, JP2, TIF, GIF, BMP, PCX, PPM, XBM, XPM]

LOADER_FORMATS = SIMPLE_LOADERS + MODEL_LOADERS + PALETTE_LOADERS

SAVER_FORMATS = SIMPLE_SAVERS + MODEL_SAVERS + PALETTE_SAVERS

LOADERS = {}
SAVERS = {}
CHECKERS = {}


sys.path.insert(-1, __path__[0])

def _get_loader(pid):
	if pid in BITMAP_LOADERS: return im_loader
	if not isinstance(pid, str): return None
	if pid in LOADERS: return LOADERS[pid]
	loader = None
	try:
		loader_mod = __import__(pid)
		loader = getattr(loader_mod, pid + '_loader')
	except: pass
	LOADERS[pid] = loader
	return loader

def _get_saver(pid):
	if not isinstance(pid, str): return None
	if pid in SAVERS: return SAVERS[pid]
	saver = None
	try:
		saver_mod = __import__(pid)
		saver = getattr(saver_mod, pid + '_saver')
	except: pass
	SAVERS[pid] = saver
	return saver

def _get_checker(pid):
	if pid in BITMAP_LOADERS: return fallback_check
	if not isinstance(pid, str): return None
	if pid in CHECKERS: return CHECKERS[pid]
	checker = None
	try:
		checker_mod = __import__(pid)
		checker = getattr(checker_mod, 'check_' + pid)
	except: pass
	CHECKERS[pid] = checker
	return checker

def get_loader_by_id(pid):
	loader = _get_loader(pid)
	if not loader:
		msg = _('Loader is not found for id %s') % (uc2const.FORMAT_NAMES[pid],)
		events.emit(events.MESSAGES, msgconst.ERROR, msg)
	return loader

def get_loader(path, experimental=False):

	if not os.path.lexists(path): return None
	if not os.path.isfile(path):return None

	ext = get_file_extension(path)
	loader = None
	ld_formats = [] + LOADER_FORMATS

	msg = _('Start to search for loader by file extension %s') % (ext.__str__())
	events.emit(events.MESSAGES, msgconst.INFO, msg)

	if experimental:
		ld_formats += EXPERIMENTAL_LOADERS
	for item in ld_formats:
		if ext in uc2const.FORMAT_EXTENSION[item]:
			checker = _get_checker(item)
			if checker and checker(path):
				loader = _get_loader(item)
				break

	if loader is None:
		msg = _('Loader is not found or not suitable for %s') % (path)
		events.emit(events.MESSAGES, msgconst.WARNING, msg)
		msg = _('Start to search loader by file content')
		events.emit(events.MESSAGES, msgconst.INFO, msg)

		for item in ld_formats:
			checker = _get_checker(item)
			if not checker is None:
				if checker(path):
					loader = _get_loader(item)
					break

	if loader is None:
		msg = _('By file content loader is not found for %s') % (path)
		events.emit(events.MESSAGES, msgconst.WARNING, msg)
		msg = _('Try using fallback loader')
		events.emit(events.MESSAGES, msgconst.INFO, msg)
		if fallback_check(path): loader = im_loader

	if loader is None:
		msg = _('Loader is not found for %s') % (path)
		events.emit(events.MESSAGES, msgconst.ERROR, msg)
	else:
		loader_name = loader.__str__().split(' ')[1]
		msg = _('Loader <%s> is found for %s') % (loader_name, path)
		events.emit(events.MESSAGES, msgconst.OK, msg)
	return loader

def get_saver_by_id(pid):
	saver = _get_saver(pid)
	if not saver:
		msg = _('Saver is not found for id %u') % (pid)
		events.emit(events.MESSAGES, msgconst.ERROR, msg)
	return saver

def get_saver(path, experimental=False):
	ext = get_file_extension(path)
	saver = None
	sv_formats = [] + SAVER_FORMATS

	msg = _('Start to search saver by file extension %s') % (ext.__str__())
	events.emit(events.MESSAGES, msgconst.INFO, msg)

	if experimental:
		sv_formats += EXPERIMENTAL_SAVERS
	for item in sv_formats:
		if ext in uc2const.FORMAT_EXTENSION[item]:
			saver = _get_saver(item)
			break
	if saver is None:
		msg = _('Saver is not found for %s file format') % (ext.__str__())
		events.emit(events.MESSAGES, msgconst.ERROR, msg)
	else:
		msg = _('Saver is found for extension %s') % (ext.__str__())
		events.emit(events.MESSAGES, msgconst.OK, msg)
	return saver

