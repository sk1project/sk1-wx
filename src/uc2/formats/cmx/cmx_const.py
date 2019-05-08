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
CONT_FILE_ID = '{Corel Binary Meta File}'
CONT_OS_ID_WIN = 'Windows 3.1'
CONT_OS_ID_MAC = 'Macintosh'
CONT_BYTE_ORDER_LE = '\x32\x00\x00\x00'
CONT_BYTE_ORDER_BE = '\x34\x00\x00\x00'
CONT_COORDSIZE_16BIT = '\x32\x00'
CONT_COORDSIZE_32BIT = '\x34\x00'
CONT_MAJOR_V1 = '\x31\x00\x00\x00'
CONT_MAJOR_V2 = '\x32\x00\x00\x00'
CONT_MINOR = '\x30\x00\x00\x00'
CONT_UNIT_MM = '\x23\x00'
CONT_UNIT_IN = '\x40\x00'
CONT_FACTOR_MM = '\x48\xaf\xbc\x9a\xf2\xd7\x7a\x3e'

CCMM_ID = 'ccmm'
CCMM_DUMP = \
    '\x50\x50\x00\x00\x00\x04\x00\x00\x4c\x02\x00\x00\x00\x00\x00\x00' \
    '\x04\x00\x00\x00\x80\x6a\xbc\x34\x80\x95\x43\x1b\x8c\x97\x6e\x02' \
    '\xc0\xf1\xd2\x2d\x80\x1e\x85\x5b\x60\x64\x3b\x0f\x80\x3d\x0a\x17' \
    '\xc0\x4b\x37\x09\x00\xc5\x8f\x79\x33\x33\x02\x00\x33\x33\x02\x00' \
    '\x33\x33\x02\x00\x01\x00\x00\x00'

PACK_ID = 'pack'
CPNG_ID = 'CPng'
CPNG_FLAGS = '\x01\x00\x04\x00'

DISP_ID = 'DISP'
PAGE_ID = 'page'
INFO_ID = 'INFO'
IKEY_ID = 'IKEY'
ICMT_ID = 'ICMT'

RCLR_ID = 'rclr'
RDOT_ID = 'rdot'
RPEN_ID = 'rpen'
ROTT_ID = 'rott'
ROTA_ID = 'rota'
ROTL_ID = 'rotl'

RSCR_ID = 'rscr'
RSCR_RECORD = '\x00\x00\x64\x00\x00\x00\x00\x00\xc2\x01\x00\x00\x00\x00'

RLST_ID = 'rlst'
RLST_ASSOCIATION_LENS = 1
RLST_ASSOCIATION_COMPONENT = 2
RLST_ASSOCIATION_TRANSFO = 3

RLST_TYPE_INSTRUCTION = 0
RLST_TYPE_PROCEDURE = 4
RLST_TYPE_LAYER = 9

INDX_ID = 'indx'
IXLR_ID = 'ixlr'
IXTL_ID = 'ixtl'
IXPG_ID = 'ixpg'
IXMR_ID = 'ixmr'

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

# COLOR SECTION
CMX_INVALID = 'INVALID'
CMX_PANTONE = 'PANTONE'
CMX_CMYK = 'CMYK'
CMX_CMYK255 = 'CMYK255'
CMX_CMY = 'CMY'
CMX_RGB = 'RGB'
CMX_HSB = 'HSB'
CMX_HLS = 'HLS'
CMX_BW = 'BW'
CMX_GRAY = 'GRAY'
CMX_YIQ255 = 'YIQ255'
CMX_LAB = 'LAB'

COLOR_MODELS = (CMX_INVALID, CMX_PANTONE, CMX_CMYK, CMX_CMYK255, CMX_CMY,
                CMX_RGB, CMX_HSB, CMX_HLS, CMX_BW, CMX_GRAY, CMX_YIQ255,
                CMX_LAB)
COLOR_MODEL_MAP = {
    0: CMX_INVALID,
    1: CMX_PANTONE,
    2: CMX_CMYK,
    3: CMX_CMYK255,
    4: CMX_CMY,
    5: CMX_RGB,
    6: CMX_HSB,
    7: CMX_HLS,
    8: CMX_BW,
    9: CMX_GRAY,
    10: CMX_YIQ255,
    11: CMX_LAB,
}
COLOR_BYTES_MAP = {
    CMX_INVALID: 0,
    CMX_PANTONE: 4,
    CMX_CMYK: 4,
    CMX_CMYK255: 4,
    CMX_CMY: 4,
    CMX_RGB: 3,
    CMX_HSB: 4,
    CMX_HLS: 4,
    CMX_BW: 1,
    CMX_GRAY: 1,
    CMX_YIQ255: 4,
    CMX_LAB: 4,
}
COLOR_BYTES = (0, 4, 4, 4, 4, 3, 4, 4, 1, 1, 4, 4)

COLOR_PALETTES = ('Invalid', 'Truematch', 'PantoneProcess', 'PantoneSpot',
                  'Image', 'User', 'CustomFixed')

MASTER_INDEX_TABLE = 1
PAGE_INDEX_TABLE = 2
MASTER_LAYER_TABLE = 3
PROCEDURE_INDEX_TABLE = 4
BITMAP_INDEX_TABLE = 5
ARROW_INDEX_TABLE = 6
FONT_INDEX_TABLE = 7
EMBEDDED_FILE_INDEX_TABLE = 8

SECTIONS = {
    MASTER_INDEX_TABLE: 'Master Index Table',
    PAGE_INDEX_TABLE: 'Page Index Table',
    MASTER_LAYER_TABLE: 'Master Layer Table',
    PROCEDURE_INDEX_TABLE: 'Procedure Index Table',
    BITMAP_INDEX_TABLE: 'Bitmap Index Table',
    ARROW_INDEX_TABLE: 'Arrow Index Table',
    FONT_INDEX_TABLE: 'Font Index Table',
    EMBEDDED_FILE_INDEX_TABLE: 'Embedded File Index Table',
    10: 'Thumbnail Section',
    15: 'Outline Description Section',
    16: 'Line Style Description Section',
    17: 'Arrowheads Description Section',
    18: 'Screen Description Section',
    19: 'Pen Description Section',
    20: 'Dot-Dash Description Section',
    21: 'Color Description Section',
    22: 'Color Correction Section',
    23: 'Preview Box Section',
}
