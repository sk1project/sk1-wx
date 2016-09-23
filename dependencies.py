# -*- coding: utf-8 -*-
#
#   Setup dependencies module
#
# 	Copyright (C) 2016 by Igor E. Novikov
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

import platform

MINT = 'LinuxMint'
UBUNTU = 'Ubuntu'
UBUNTU14 = 'Ubuntu 14'
UBUNTU15 = 'Ubuntu 15'
UBUNTU16 = 'Ubuntu 16'
FEDORA = 'fedora'
FEDORA21 = 'fedora 21'
FEDORA22 = 'fedora 22'
FEDORA23 = 'fedora 23'

UC2_DEB_DEPENDENCIES = {
UBUNTU14:'libmagickwand5, liblcms2-2 (>=2.0), python (>=2.4), python (<<3.0), python-cairo, python-reportlab, python-pil',
UBUNTU15:'libmagickwand5, liblcms2-2 (>=2.0), python (>=2.4), python (<<3.0), python-cairo, python-reportlab, python-pil',
UBUNTU16:'libmagickwand-6.q16, liblcms2-2 (>=2.0), python (>=2.4), python (<<3.0), python-cairo, python-reportlab, python-pil',
}

SK1_DEB_DEPENDENCIES = {
UBUNTU14:'python-wxgtk2.8, python-cups',
UBUNTU15:'python-wxgtk2.8, python-cups',
UBUNTU16:'python-wxgtk3.0, python-cups',
}

UC2_RPM_DEPENDENCIES = {
FEDORA21:'lcms2 pycairo python-pillow python-reportlab',
FEDORA22:'lcms2 pycairo python-pillow python-reportlab',
FEDORA23:'lcms2 pycairo python-pillow python-reportlab',

'OpenSUSE':'liblcms2-2 python-cairo python-Pillow python-reportlab',
'Mageia 64bit':'lib64lcms2_2 python-cairo python-pillow python-reportlab',
'Mageia 32bit':'liblcms2_2 python-cairo python-pillow python-reportlab',
}

#TODO: add wxpython, python-cups
SK1_RPM_DEPENDENCIES = {
FEDORA21:'',
'OpenSUSE':'',
'Mageia 64bit':'',
'Mageia 32bit':'',
}


def get_system_id():
	ver = platform.dist()[1].split('.')[0]
	dist = platform.dist()[0] + ' ' + ver
	return dist

def get_uc2_deb_depend():
	sid = get_system_id()
	if sid in UC2_DEB_DEPENDENCIES:
		return UC2_DEB_DEPENDENCIES[sid]
	return ''

def get_sk1_deb_depend():
	sid = get_system_id()
	uc2_dep = get_uc2_deb_depend()
	sk1_dep = ''
	if sid in SK1_DEB_DEPENDENCIES:
		sk1_dep = SK1_DEB_DEPENDENCIES[sid]
	if uc2_dep and sk1_dep:
		sk1_dep = '%s, %s' % (uc2_dep, sk1_dep)
	elif uc2_dep:
		sk1_dep = uc2_dep
	return sk1_dep

def get_uc2_rpm_depend():
	sid = get_system_id()
	if sid in UC2_RPM_DEPENDENCIES:
		return UC2_RPM_DEPENDENCIES[sid]
	return ''

def get_sk1_rpm_depend():
	sid = get_system_id()
	uc2_dep = get_uc2_rpm_depend()
	sk1_dep = ''
	if sid in SK1_DEB_DEPENDENCIES:
		sk1_dep = SK1_DEB_DEPENDENCIES[sid]
	if uc2_dep and sk1_dep:
		sk1_dep = '%s %s' % (uc2_dep, sk1_dep)
	elif uc2_dep:
		sk1_dep = uc2_dep
	return sk1_dep


