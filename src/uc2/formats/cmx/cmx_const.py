# -*- coding: utf-8 -*-
#
#  Copyright (C) 2019 by Igor E. Novikov
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

LIST_ID = 'LIST'
ROOT_ID = 'RIFF'
ROOTX_ID = 'RIFX'
LIST_IDS = (LIST_ID, ROOT_ID, ROOTX_ID)

CONT_ID = 'cont'
FILE_ID = '{Corel Binary Meta File}'
OS_ID_WIN = 'Windows 3.1'
OS_ID_MAC = 'Macintosh'
BYTE_ORDER_LE = '\x32\x00\x00\x00'
BYTE_ORDER_BE = '\x34\x00\x00\x00'
COORDSIZE_16BIT = '\x32\x00'
COORDSIZE_32BIT = '\x34\x00'
MAJOR_16BIT = '\x31\x00\x00\x00'
MAJOR_32BIT = '\x32\x00\x00\x00'
MINOR = '\x30\x00\x00\x00'
UNIT_MM = '\x23\x00'
UNIT_IN = '\x40\x00'
FACTOR_MM = '\x48\xaf\xbc\x9a\xf2\xd7\x7a\x3e'

DISP_ID = 'DISP'
CCMM_ID = 'ccmm'
PAGE_ID = 'page'

INSTR_CODES = {
    88: 'AddClippingRegion',
    94: 'AddGlobalTransform',
    22: 'BeginEmbedded',
    13: 'BeginGroup',
    11: 'BeginLayer',
    9: 'BeginPage',
    99: 'BeginParagraph',
    17: 'BeginProcedure',
    72: 'BeginTextGroup',
    70: 'BeginTextObject',
    20: 'BeginTextStream',
    101: 'CharInfo',
    102: 'Characters',
    90: 'ClearClipping',
    2: 'Comment',
    69: 'DrawImage',
    65: 'DrawChars',
    66: 'Ellipse',
    23: 'EndEmbedded',
    14: 'EndGroup',
    12: 'EndLayer',
    10: 'EndPage',
    100: 'EndParagraph',
    18: 'EndSection',
    73: 'EndTextGroup',
    71: 'EndTextObject',
    21: 'EndTextStream',
    111: 'JumpAbsolute',
    67: 'PolyCurve',
    92: 'PopMappingMode',
    104: 'PopTint',
    91: 'PushMappingMode',
    103: 'PushTint',
    68: 'Rectangle',
    89: 'RemoveLastClippingRegion',
    95: 'RestoreLastGlobalTransfo',
    85: 'SetCharStyle',
    93: 'SetGlobalTransfo',
    86: 'SimpleWideText',
    98: 'TextFrame',
}
