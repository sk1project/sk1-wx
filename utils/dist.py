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


def get_system_id():
    ver = platform.dist()[1].split('.')[0]
    dist = platform.dist()[0] + ' ' + ver
    if platform.dist()[0] == OPENSUSE and ver == '42':
        dist = platform.dist()[0] + ' ' + platform.dist()[1]
    return dist
