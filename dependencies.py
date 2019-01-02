# -*- coding: utf-8 -*-
#
#   Setup dependencies module
#
# 	Copyright (C) 2016-2018 by Igor E. Novikov
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
# 	along with this program.  If not, see <https://www.gnu.org/licenses/>.

from utils.dist import *

DEB_GENERIC = 'liblcms2-2 (>=2.0), python (>=2.4), python (<<3.0), '
DEB_GENERIC += 'python-cairo, python-reportlab, '

UC2_DEB_DEPENDENCIES = {
    UBUNTU14: DEB_GENERIC + 'libmagickwand5, python-pil',
    UBUNTU15: DEB_GENERIC + 'libmagickwand5, python-pil',
    UBUNTU16: DEB_GENERIC + 'libmagickwand-6.q16-2, python-pil',
    UBUNTU17: DEB_GENERIC + 'libmagickwand-6.q16-3, python-pil',
    UBUNTU18: DEB_GENERIC + 'libmagickwand-6.q16-3, python-pil'
        # Workaround for Ubuntu 18.10
        if platform.dist()[1] != '18.10' else
        DEB_GENERIC + 'libmagickwand-6.q16-6, python-pil',

    MINT17: DEB_GENERIC + 'libmagickwand5, python-pil',
    MINT18: DEB_GENERIC + 'libmagickwand-6.q16-2, python-pil',
    MINT19: DEB_GENERIC + 'libmagickwand-6.q16-3, python-pil',

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
    MINT19: 'python-wxgtk3.0, python-cups',

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
    FEDORA28: 'lcms2 pango ImageMagick python2-cairo python2-pillow python2-reportlab',
    FEDORA29: 'lcms2 pango ImageMagick python2-cairo python2-pillow python2-reportlab',

    OPENSUSE13: 'liblcms2-2 libpango-1_0-0 ImageMagick python-cairo '
                'python-Pillow python-reportlab',
    OPENSUSE42: 'liblcms2-2 libpango-1_0-0 ImageMagick python-cairo '
                'python-Pillow python-reportlab',
    OPENSUSE42_2: 'liblcms2-2 libpango-1_0-0 ImageMagick python-cairo '
                  'python-Pillow python-reportlab',
    OPENSUSE42_3: 'liblcms2-2 libpango-1_0-0 ImageMagick python-cairo '
                  'python-Pillow python-reportlab',
    OPENSUSE15_0: 'liblcms2-2 libpango-1_0-0 ImageMagick python-cairo '
                  'python-Pillow python-reportlab',
}

SK1_RPM_DEPENDENCIES = {
    FEDORA23: 'wxPython python-cups',
    FEDORA24: 'wxPython python2-cups',
    FEDORA25: 'wxPython python2-cups',
    FEDORA26: 'wxPython python2-cups',
    FEDORA27: 'wxPython python2-cups',
    FEDORA28: 'python2-wxpython python2-cups',
    FEDORA29: 'python2-wxpython python2-cups',

    OPENSUSE13: 'python-wxWidgets python-cups',
    OPENSUSE42: 'python-wxWidgets python-cups',
    OPENSUSE42_2: 'python-wxWidgets python-cups',
    OPENSUSE42_3: 'python-wxWidgets python-cups',
    OPENSUSE15_0: 'python-wxWidgets python-cups',
}


def get_uc2_deb_depend():
    if SYSFACTS.sid in UC2_DEB_DEPENDENCIES:
        return UC2_DEB_DEPENDENCIES[SYSFACTS.sid]
    return ''


def get_sk1_deb_depend():
    uc2_dep = get_uc2_deb_depend()
    sk1_dep = ''
    if SYSFACTS.sid in SK1_DEB_DEPENDENCIES:
        sk1_dep = SK1_DEB_DEPENDENCIES[SYSFACTS.sid]
    if uc2_dep and sk1_dep:
        sk1_dep = '%s, %s' % (uc2_dep, sk1_dep)
    elif uc2_dep:
        sk1_dep = uc2_dep
    return sk1_dep


def get_uc2_rpm_depend():
    if SYSFACTS.sid in UC2_RPM_DEPENDENCIES:
        return UC2_RPM_DEPENDENCIES[SYSFACTS.sid]
    return ''


def get_sk1_rpm_depend():
    uc2_dep = get_uc2_rpm_depend()
    sk1_dep = ''
    if SYSFACTS.sid in SK1_RPM_DEPENDENCIES:
        sk1_dep = SK1_RPM_DEPENDENCIES[SYSFACTS.sid]
    if uc2_dep and sk1_dep:
        sk1_dep = '%s %s' % (uc2_dep, sk1_dep)
    elif uc2_dep:
        sk1_dep = uc2_dep
    return sk1_dep
