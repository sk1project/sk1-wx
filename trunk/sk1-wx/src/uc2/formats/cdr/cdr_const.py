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

from uc2 import uc2const

RIFF_ID = 'RIFF'

CDR5 = 'CDR5'
CDR6 = 'CDR6'
CDR7 = 'CDR7'
CDR8 = 'CDR8'
CDR9 = 'CDR9'
CDR10 = 'CDRA'
CDR11 = 'CDRB'
CDR12 = 'CDRC'
CDR13 = 'CDRD'

CDR_VERSIONS = [CDR6, CDR7, CDR8, CDR9, CDR10, CDR11, CDR12, CDR13, ]
cdrunit_to_pt = uc2const.mm_to_pt / 10000.0

DATA_OUTL = 10# 0xa
DATA_FILD = 20# 0x14
DATA_COORDS = 30# 0x1e
DATA_RCENTER = 40# 0x28
DATA_TRFD = 100# 0x64
DATA_STLT = 200# 0xc8
DATA_NAME = 1000# 0x3e8
DATA_PALT = 2000# 0x7d0
DATA_LENS = 8000# 0x1f40
DATA_CNT = 8005# 0x1f45
DATA_PGN = 11000# 0x2af8
DATA_GRAD = 12010# 0x2eea
DATA_ROT = 12030# 0x2efe
DATA_WROFF = 13000# 0x32c8
DATA_WRST = 13001# 0x32c9
DATA_MESH = 19150# 0x4ace


CDR_FILL_TYPE = {
0: 'No Fill',
1: 'Plain Color',
2: 'Linear Gradient',
4: 'Radial Gradient',
6: 'EPS pattern',
7: 'Pattern',
10: 'Bitmap pattern'
}


CDR_COLOR_SPOT = 1
CDR_COLOR_CMYK = 2
CDR_COLOR_CMYK255 = 3
CDR_COLOR_CMY = 4
CDR_COLOR_BGR = 5
CDR_COLOR_HSB = 6
CDR_COLOR_HLS = 7
CDR_COLOR_BW = 8
CDR_COLOR_GRAY = 9
##=10
CDR_COLOR_YIQ = 11
CDR_COLOR_LAB = 12
##=13
##=14
CDR_COLOR_HEXACHROME = 15
##=16
CDR_COLOR_CMYK2 = 17
CDR_COLOR_LAB2 = 18
##=19
CDR_COLOR_REGISTRATION = 20
CDR_COLOR_SPOT2 = 21#?

CDR_COLORSPACE = {
1: uc2const.COLOR_SPOT,#SPOT
2: uc2const.COLOR_CMYK,#CMYK
3: uc2const.COLOR_CMYK,#CMYK255
4: uc2const.COLOR_CMYK,#CMY
5: uc2const.COLOR_RGB,#RGB
6: CDR_COLOR_HSB,#HSB
7: CDR_COLOR_HLS,#HSL
8: '',#B&W
9: uc2const.COLOR_GRAY,#Grayscale
11: CDR_COLOR_YIQ,#Grayscale
12: uc2const.COLOR_LAB,
17: uc2const.COLOR_CMYK,#CMYK255
18: uc2const.COLOR_LAB,#Lab
20: uc2const.COLOR_SPOT,#Registration Color
}

CDR_COLOR_NAMES = {
CDR_COLOR_SPOT:'SPOT',#?
CDR_COLOR_CMYK:'CMYK',
CDR_COLOR_CMYK255:'CMYK255',
CDR_COLOR_CMY:'CMY',
CDR_COLOR_BGR:'BGR',
CDR_COLOR_HSB:'HSB',
CDR_COLOR_HLS:'HLS',
CDR_COLOR_BW:'B&W',#?
CDR_COLOR_GRAY:'GRAY',
CDR_COLOR_YIQ:'YIQ',
CDR_COLOR_LAB:'LAB',
CDR_COLOR_HEXACHROME:'HEXACHROME',
CDR_COLOR_CMYK2:'CMYK255',
CDR_COLOR_LAB2:'LAB2',
CDR_COLOR_REGISTRATION:'REGISTRATION',#?
CDR_COLOR_SPOT2:'SPOT2',#?
}
