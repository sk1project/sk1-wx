# -*- coding: utf-8 -*-
#
#  Copyright (C) 2015 by Igor E. Novikov
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

JCW_ID = 'JCW'
JCW_VER = '\x01'
JCW_NAMESIZE = 21

JCW_PMS = 0
JCW_CMYK_PANTONE = 1
JCW_RGB_PANTONE = 3
JCW_HSV_PANTONE = 5
JCW_CMYK = 8
JCW_SPOT_CMYK = 9
JCW_RGB = 10
JCW_SPOT_RGB = 11
JCW_HSV = 12
JCW_SPOT_HSV = 13

JCW_COLOR_NAMES = {
    0: 'PMS',
    1: 'CMYK PANTONE',
    3: 'RGB PANTONE',
    5: 'HSV PANTONE',
    8: 'CMYK',
    9: 'SPOT CMYK',
    10: 'RGB',
    11: 'SPOT RGB',
    12: 'HSV',
    13: 'SPOT HSV',
}
