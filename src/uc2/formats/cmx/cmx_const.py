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
CMX_ID = 'CMX1'
CDRX_ID = 'CDRX'
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
PACK_ID = 'pack'
INFO_ID = 'INFO'
IKEY_ID = 'IKEY'
ICMT_ID = 'ICMT'

# INSTRUCTION CODES
ADD_CLIPPING_REGION = 88
ADD_GLOBAL_TRANSFORM = 94
BEGIN_EMBEDDED = 22
BEGIN_GROUP = 13
BEGIN_LAYER = 11
BEGIN_PAGE = 9
BEGIN_PARAGRAPH = 99
BEGIN_PROCEDURE = 17
BEGIN_TEXT_GROUP = 72
BEGIN_TEXT_OBJECT = 70
BEGIN_TEXT_STREAM = 20
CHAR_INFO = 101
CHARACTERS = 102
CLEAR_CLIPPING = 90
COMMENT = 2
DRAW_IMAGE = 69
DRAW_CHARS = 65
ELLIPSE = 66
END_EMBEDDED = 23
END_GROUP = 14
END_LAYER = 12
END_PAGE = 10
END_PARAGRAPH = 100
END_SECTION = 18
END_TEXT_GROUP = 73
END_TEXT_OBJECT = 71
END_TEXT_STREAM = 21
JUMP_ABSOLUTE = 111
POLYCURVE = 67
POP_MAPPING_MODE = 92
POP_TINT = 104
PUSH_MAPPING_MODE = 91
PUSH_TINT = 103
RECTANGLE = 68
REMOVE_LAST_CLIPPING_REGION = 89
RESTORE_LASTGLOBAL_TRANSFO = 95
SET_CHAR_STYLE = 85
SET_GLOBAL_TRANSFO = 93
SIMPLE_WIDE_TEXT = 86
TEXT_FRAME = 98

INSTR_CODES = {
    ADD_CLIPPING_REGION: 'AddClippingRegion',
    ADD_GLOBAL_TRANSFORM: 'AddGlobalTransform',
    BEGIN_EMBEDDED: 'BeginEmbedded',
    BEGIN_GROUP: 'BeginGroup',
    BEGIN_LAYER: 'BeginLayer',
    BEGIN_PAGE: 'BeginPage',
    BEGIN_PARAGRAPH: 'BeginParagraph',
    BEGIN_PROCEDURE: 'BeginProcedure',
    BEGIN_TEXT_GROUP: 'BeginTextGroup',
    BEGIN_TEXT_OBJECT: 'BeginTextObject',
    BEGIN_TEXT_STREAM: 'BeginTextStream',
    CHAR_INFO: 'CharInfo',
    CHARACTERS: 'Characters',
    CLEAR_CLIPPING: 'ClearClipping',
    COMMENT: 'Comment',
    DRAW_IMAGE: 'DrawImage',
    DRAW_CHARS: 'DrawChars',
    ELLIPSE: 'Ellipse',
    END_EMBEDDED: 'EndEmbedded',
    END_GROUP: 'EndGroup',
    END_LAYER: 'EndLayer',
    END_PAGE: 'EndPage',
    END_PARAGRAPH: 'EndParagraph',
    END_SECTION: 'EndSection',
    END_TEXT_GROUP: 'EndTextGroup',
    END_TEXT_OBJECT: 'EndTextObject',
    END_TEXT_STREAM: 'EndTextStream',
    JUMP_ABSOLUTE: 'JumpAbsolute',
    POLYCURVE: 'PolyCurve',
    POP_MAPPING_MODE: 'PopMappingMode',
    POP_TINT: 'PopTint',
    PUSH_MAPPING_MODE: 'PushMappingMode',
    PUSH_TINT: 'PushTint',
    RECTANGLE: 'Rectangle',
    REMOVE_LAST_CLIPPING_REGION: 'RemoveLastClippingRegion',
    RESTORE_LASTGLOBAL_TRANSFO: 'RestoreLastGlobalTransfo',
    SET_CHAR_STYLE: 'SetCharStyle',
    SET_GLOBAL_TRANSFO: 'SetGlobalTransfo',
    SIMPLE_WIDE_TEXT: 'SimpleWideText',
    TEXT_FRAME: 'TextFrame',
}
