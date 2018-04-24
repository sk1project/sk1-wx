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
MINT13 = 'LinuxMint 13'
MINT17 = 'LinuxMint 17'
MINT18 = 'LinuxMint 18'

UBUNTU = 'Ubuntu'
UBUNTU12 = 'Ubuntu 12'
UBUNTU14 = 'Ubuntu 14'
UBUNTU15 = 'Ubuntu 15'
UBUNTU16 = 'Ubuntu 16'
UBUNTU17 = 'Ubuntu 17'
UBUNTU18 = 'Ubuntu 18'

DEBIAN = 'debian'
DEBIAN7 = 'debian 7'
DEBIAN8 = 'debian 8'
DEBIAN9 = 'debian 9'

FEDORA = 'fedora'
FEDORA21 = 'fedora 21'
FEDORA22 = 'fedora 22'
FEDORA23 = 'fedora 23'
FEDORA24 = 'fedora 24'
FEDORA25 = 'fedora 25'
FEDORA26 = 'fedora 26'
FEDORA27 = 'fedora 27'

OPENSUSE = 'SuSE'
OPENSUSE13 = 'SuSE 13'
OPENSUSE42 = 'SuSE 42.1'
OPENSUSE42_2 = 'SuSE 42.2'
OPENSUSE42_3 = 'SuSE 42.3'

DEB_GENERIC = 'liblcms2-2 (>=2.0), python (>=2.4), python (<<3.0), '
DEB_GENERIC += 'python-cairo, python-reportlab, '

UC2_DEB_DEPENDENCIES = {
    UBUNTU14: DEB_GENERIC + 'libmagickwand5, python-pil',
    UBUNTU15: DEB_GENERIC + 'libmagickwand5, python-pil',
    UBUNTU16: DEB_GENERIC + 'libmagickwand-6.q16-2, python-pil',
    UBUNTU17: DEB_GENERIC + 'libmagickwand-6.q16-3, python-pil',
    UBUNTU18: DEB_GENERIC + 'libmagickwand-6.q16-3, python-pil',

    MINT17: DEB_GENERIC + 'libmagickwand5, python-pil',
    MINT18: DEB_GENERIC + 'libmagickwand-6.q16-2, python-pil',

    DEBIAN7: DEB_GENERIC + 'libmagickwand5, python-imaging',
    DEBIAN8: DEB_GENERIC + 'libmagickwand-6.q16-2, python-pil',
    DEBIAN9: DEB_GENERIC + 'libmagickwand-6.q16-3, python-pil',
}

SK1_DEB_DEPENDENCIES = {
    UBUNTU14: 'python-wxgtk2.8, python-cups',
    UBUNTU15: 'python-wxgtk2.8, python-cups',
    UBUNTU16: 'python-wxgtk3.0, python-cups',
    UBUNTU17: 'python-wxgtk3.0, python-cups',
    UBUNTU18: 'python-wxgtk3.0, python-cups',

    MINT17: 'python-wxgtk2.8, python-cups',
    MINT18: 'python-wxgtk3.0, python-cups',

    DEBIAN7: 'python-wxgtk2.8, python-cups',
    DEBIAN8: 'python-wxgtk3.0, python-cups',
    DEBIAN9: 'python-wxgtk3.0, python-cups',
}

UC2_RPM_DEPENDENCIES = {
    FEDORA23: 'lcms2 pango ImageMagick pycairo python-pillow python-reportlab',
    FEDORA24: 'lcms2 pango ImageMagick pycairo python-pillow python2-reportlab',
    FEDORA25: 'lcms2 pango ImageMagick pycairo python2-pillow python2-reportlab',
    FEDORA26: 'lcms2 pango ImageMagick pycairo python2-pillow python2-reportlab',
    FEDORA27: 'lcms2 pango ImageMagick pycairo python2-pillow python2-reportlab',

    OPENSUSE13: 'liblcms2-2 libpango-1_0-0 ImageMagick python-cairo '
                'python-Pillow python-reportlab',
    OPENSUSE42: 'liblcms2-2 libpango-1_0-0 ImageMagick python-cairo '
                'python-Pillow python-reportlab',
    OPENSUSE42_2: 'liblcms2-2 libpango-1_0-0 ImageMagick python-cairo '
                  'python-Pillow python-reportlab',
    OPENSUSE42_3: 'liblcms2-2 libpango-1_0-0 ImageMagick python-cairo '
                  'python-Pillow python-reportlab',
}

SK1_RPM_DEPENDENCIES = {
    FEDORA23: 'wxPython python-cups',
    FEDORA24: 'wxPython python2-cups',
    FEDORA25: 'wxPython python2-cups',
    FEDORA26: 'wxPython python2-cups',
    FEDORA27: 'wxPython python2-cups',

    OPENSUSE13: 'python-wxWidgets python-cups',
    OPENSUSE42: 'python-wxWidgets python-cups',
    OPENSUSE42_2: 'python-wxWidgets python-cups',
    OPENSUSE42_3: 'python-wxWidgets python-cups',
}


def get_system_id():
    ver = platform.dist()[1].split('.')[0]
    dist = platform.dist()[0] + ' ' + ver
    if platform.dist()[0] == OPENSUSE and ver == '42':
        dist = platform.dist()[0] + ' ' + platform.dist()[1]
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
    if sid in SK1_RPM_DEPENDENCIES:
        sk1_dep = SK1_RPM_DEPENDENCIES[sid]
    if uc2_dep and sk1_dep:
        sk1_dep = '%s %s' % (uc2_dep, sk1_dep)
    elif uc2_dep:
        sk1_dep = uc2_dep
    return sk1_dep
