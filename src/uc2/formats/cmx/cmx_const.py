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
CONT_UNITS = {CONT_UNIT_IN: 'inches', CONT_UNIT_MM: 'mm'}
CONT_FACTOR_MM = '\x48\xaf\xbc\x9a\xf2\xd7\x7a\x3e'
CONT_FACTOR_IN = '\xfc\xa9\xf1\xd2\x4d\x62\x50\x3f'

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
RSCR_RECORD = '\x00\x00\x3c\x00\x00\x00\x00\x00\xc2\x01\x00\x00\x00\x00'

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
THUMBNAIL_SECTION = 10
OUTLINE_DESCRIPTION_SECTION = 15
LINE_STYLE_DESCRIPTION_SECTION = 16
ARROWHEADS_DESCRIPTION_SECTION = 17
SCREEN_DESCRIPTION_SECTION = 18
PEN_DESCRIPTION_SECTION = 19
DOTDASH_DESCRIPTION_SECTION = 20
COLOR_DESCRIPTION_SECTION = 21
COLOR_CORRECTION_SECTION = 22
PREVIEW_BOX_SECTION = 23

SECTIONS = {
    MASTER_INDEX_TABLE: 'Master Index Table',
    PAGE_INDEX_TABLE: 'Page Index Table',
    MASTER_LAYER_TABLE: 'Master Layer Table',
    PROCEDURE_INDEX_TABLE: 'Procedure Index Table',
    BITMAP_INDEX_TABLE: 'Bitmap Index Table',
    ARROW_INDEX_TABLE: 'Arrow Index Table',
    FONT_INDEX_TABLE: 'Font Index Table',
    EMBEDDED_FILE_INDEX_TABLE: 'Embedded File Index Table',
    THUMBNAIL_SECTION: 'Thumbnail Section',
    OUTLINE_DESCRIPTION_SECTION: 'Outline Description Section',
    LINE_STYLE_DESCRIPTION_SECTION: 'Line Style Description Section',
    ARROWHEADS_DESCRIPTION_SECTION: 'Arrowheads Description Section',
    SCREEN_DESCRIPTION_SECTION: 'Screen Description Section',
    PEN_DESCRIPTION_SECTION: 'Pen Description Section',
    DOTDASH_DESCRIPTION_SECTION: 'Dot-Dash Description Section',
    COLOR_DESCRIPTION_SECTION: 'Color Description Section',
    COLOR_CORRECTION_SECTION: 'Color Correction Section',
    PREVIEW_BOX_SECTION: 'Preview Box Section',
}

######## INSTRUCTIONS ##############

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

INSTR_PAGE_TAIL = '\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00'
INSTR_LAYER_TAIL = '\x01\x00'
INSTR_GROUP_TAIL = '\x00\x00'

INSTR_FILL_FLAG = 0x01
INSTR_STROKE_FLAG = 0x02
INSTR_LENS_FLAG = 0x04
INSTR_CANVAS_FLAG = 0x08
INSTR_CONTAINER_FLAG = 0x10

INSTR_FILL_EMPTY = 0
INSTR_FILL_UNIFORM = 1
INSTR_FILL_FOUNTAIN = 2
INSTR_FILL_PS = 6
INSTR_FILL_DUOCOLOR = 7
INSTR_FILL_MONOCHROME = 8
INSTR_FILL_IMPORTED_BITMAP = 9
INSTR_FILL_FULL_COLOR = 10
INSTR_FILL_TEXTURE = 11

FILL_TYPE_MAP = {
    INSTR_FILL_EMPTY: 'No fill',
    INSTR_FILL_UNIFORM: 'Uniform',
    INSTR_FILL_FOUNTAIN: 'Fountain',
    INSTR_FILL_PS: 'Postscript',
    INSTR_FILL_DUOCOLOR: 'Two-color pattern',
    INSTR_FILL_MONOCHROME: 'Monochrome pattern',
    INSTR_FILL_IMPORTED_BITMAP: 'Imported bitmap',
    INSTR_FILL_FULL_COLOR: 'Full color pattern',
    INSTR_FILL_TEXTURE: 'Texture',
}

FILL_FOUNTAINS = {
    0: 'linear',
    1: 'radial',
    2: 'conical',
    3: 'square'
}

CMX_MITER_CAP = 0x00
CMX_ROUND_CAP = 0x01
CMX_SQUARE_CAP = 0x02

CMX_MITER_JOIN = 0x00
CMX_ROUND_JOIN = 0x01
CMX_BEVEL_JOIN = 0x02

NODE_USER = 0b00000100
NODE_CLOSED = 0b00001000

NODE_DISC = 0b00000000
NODE_SMOOTH = 0b00010000
NODE_SYMM = 0b00100000

NODE_MOVE = 0b00000000
NODE_LINE = 0b01000000
NODE_CURVE = 0b10000000
NODE_ARC = 0b11000000
