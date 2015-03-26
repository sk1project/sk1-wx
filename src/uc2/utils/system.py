# -*- coding: utf-8 -*-
#
#	Copyright (C) 2010, 2011 by Igor E. Novikov
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

import platform

WINDOWS = 'Windows'
LINUX = 'Linux'
MACOSX = 'Darwin'
GENERIC = 'generic'

def get_os_family():
	"""
	Detects OS type and returns module predefined platform name.
	The function is used for all platform dependent issues.
	"""
	name = platform.system()
	if name == LINUX:
		return LINUX
	elif name == WINDOWS:
		return WINDOWS
	elif name == MACOSX:
		return MACOSX
	else:
		return GENERIC


P32BIT = '32bit'
P64BIT = '64bit'
P128BIT = '128bit'
PXXBIT = 'unknown'

def get_os_arch():
	"""
	Detects OS architecture and returns module predefined architecture type.
	"""
	arch = platform.architecture()[0]
	if arch == P32BIT:
		return P32BIT
	elif arch == P64BIT:
		return P64BIT
	elif arch == P128BIT:
		return P128BIT
	else:
		return PXXBIT

#Supported OS'es:
WINXP = 'XP'
WINVISTA = 'Vista'#???
WIN7 = 'Win7'#???
WINOTHER = 'WinOther'

UBUNTU = 'Ubuntu'
MINT = 'LinuxMint'
MANDRIVA = 'mandrake'
FEDORA = 'fedora'
SUSE = 'SuSE'
LINUXOTHER = 'LinuxOther'

LEOPARD = '10.5'
SNOWLEOPARD = '10.6'
MACOTHER = 'MacOther'

UNIX = 'unix'

def get_os_name():
	"""
	Detects OS name and returns module predefined constant.
	"""
	if get_os_family() == WINDOWS:
		if platform.release() == WINXP:
			return WINXP
		elif platform.release() == WINVISTA:
			return WINVISTA
		elif platform.release() == WIN7:
			return WIN7
		else:
			return WINOTHER

	elif get_os_family() == LINUX:
		if not (platform.platform()).find(UBUNTU) == -1:
			return UBUNTU
		elif not (platform.platform()).find(MINT) == -1:
			return MINT
		elif not (platform.platform()).find(MANDRIVA) == -1:
			return MANDRIVA
		elif not (platform.platform()).find(FEDORA) == -1:
			return FEDORA
		elif not (platform.platform()).find(SUSE) == -1:
			return SUSE
		else:
			return LINUXOTHER

	elif get_os_family() == MACOSX:
		if not ((platform.mac_ver())[0]).find(LEOPARD) == -1:
			return LEOPARD
		elif not ((platform.mac_ver())[0]).find(SNOWLEOPARD) == -1:
			return SNOWLEOPARD
		else:
			return MACOTHER

	else:
		return UNIX




