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
	

p32bit = '32bit'
p64bit = '64bit'
p128bit = '128bit'
pxxbit = 'unknown'
	
def get_os_arch():
	"""
	Detects OS architecture and returns module predefined architecture type.
	"""
	arch, bin = platform.architecture()
	if arch == p32bit:
		return p32bit
	elif arch == p64bit:
		return p64bit
	elif arch == p128bit:
		return p128bit
	else:
		return pxxbit
	
#Supported OS'es:
WinXP = 'XP'
WinVista = 'Vista'#???
Win7 = 'Win7'#???
WinOther = 'WinOther'

Ubuntu = 'Ubuntu'
Mint = 'LinuxMint'
Mandriva = 'mandrake'
Fedora = 'fedora'
Suse = 'SuSE'
LinuxOther = 'LinuxOther'

Leopard = '10.5'
SnowLeopard = '10.6'
MacOther = 'MacOther'

Unix = 'unix'

def get_os_name():
	"""
	Detects OS name and returns module predefined constant.
	"""
	if get_os_family() == WINDOWS:
		if platform.release() == WinXP:
			return WinXP
		elif platform.release() == WinVista:
			return WinVista
		elif platform.release() == Win7:
			return Win7
		else:
			return WinOther
		
	elif get_os_family() == LINUX:
		if not (platform.platform()).find(Ubuntu) == -1:
			return Ubuntu
		elif not (platform.platform()).find(Mint) == -1:
			return Mint
		elif not (platform.platform()).find(Mandriva) == -1:
			return Mandriva
		elif not (platform.platform()).find(Fedora) == -1:
			return Fedora
		elif not (platform.platform()).find(Suse) == -1:
			return Suse
		else:
			return LinuxOther
		
	elif get_os_family() == MACOSX:
		if not ((platform.mac_ver())[0]).find(Leopard) == -1:
			return Leopard
		elif not ((platform.mac_ver())[0]).find(SnowLeopard) == -1:
			return SnowLeopard
		else:
			return MacOther
		
	else:
		return Unix




