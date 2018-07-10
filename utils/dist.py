# -*- coding: utf-8 -*-
#
#   OS dist staff
#
# 	Copyright (C) 2018 by Igor E. Novikov
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

WINDOWS = 'Windows'
LINUX = 'Linux'
MACOS = 'Darwin'

MINT = 'LinuxMint'
MINT13 = 'LinuxMint 13'
MINT17 = 'LinuxMint 17'
MINT18 = 'LinuxMint 18'
MINT19 = 'LinuxMint 19'

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
FEDORA28 = 'fedora 28'

OPENSUSE = 'SuSE'
OPENSUSE13 = 'SuSE 13'
OPENSUSE42 = 'SuSE 42.1'
OPENSUSE42_2 = 'SuSE 42.2'
OPENSUSE42_3 = 'SuSE 42.3'
OPENSUSE15_0 = 'SuSE 15'

MARKERS = {
    MINT: ('mint', 'LinuxMint'),
    UBUNTU: ('ubuntu', 'Ubuntu'),
    DEBIAN: ('debian', 'Debian'),
    FEDORA: ('fc', 'Fedora'),
    OPENSUSE: ('opensuse', 'OpenSuse'),
}


class SystemFacts(object):
    def __init__(self):
        self.family, self.version = platform.dist()[:2]

        # Workaround for Leap 15.0 bug
        if not self.family and not self.version:
            self.family, self.version = OPENSUSE, '15.0'

        # Workaround for Suse 42.x
        if self.family == OPENSUSE and self.version.startswith('42'):
            self.sid = '%s %s' % (self.family, self.version)
        else:
            self.sid = '%s %s' % (self.family, self.version.split('.')[0])

        self.arch = platform.architecture()[0]
        self.is_64bit = self.arch == '64bit'

        self.system = platform.system()
        self.is_msw = self.system == WINDOWS
        self.is_linux = self.system == LINUX
        self.is_macos = self.system == MACOS
        self.is_deb = self.family in [MINT, UBUNTU, DEBIAN]
        self.is_debian = self.family == DEBIAN
        self.is_ubuntu = self.family == UBUNTU
        self.is_rpm = self.family in [FEDORA, OPENSUSE]
        self.is_fedora = self.family == FEDORA
        self.is_opensuse = self.family == OPENSUSE
        self.is_src = all([self.is_64bit, self.is_deb, self.version == '16.04'])
        self.marker = MARKERS.get(self.family, ('', 'unknown'))[0]
        self.hmarker = MARKERS.get(self.family, ('Unknown', ''))[1]


SYSFACTS = SystemFacts()
