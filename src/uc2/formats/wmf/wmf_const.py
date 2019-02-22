# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013-2016 by Igor E. Novikov
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

WMF_SIGNATURE = '\xd7\xcd\xc6\x9a'
METAFILETYPES = ('\x01\x00', '\x02\x00')
METAVERSIONS = ('\x00\x01', '\x00\x03')
EOF_RECORD = '\x03\x00\x00\x00\x00\x00'

META_DPI = 1440
META_W = 11905.51
META_H = 16837.80
META_FALSE = 0x00
META_TRUE = 0x01

STRUCT_PLACEABLE = ('<'
                    '4s'  # Key
                    'H'  # handle
                    'h'  # left
                    'h'  # top
                    'h'  # right
                    'h'  # bottom
                    'H'  # Inch
                    'I'  # Reserved
                    'H'  # Checksum
)

STRUCT_HEADER = ('<'
                 'H'  # Type
                 'H'  # header size
                 'H'  # Version
                 'I'  # FileSize
                 'H'  # Num. objects
                 'I'  # Max. record size
                 'H'  # Num. Parameters
)

MEMORYMETAFILE = 0x0001
DISKMETAFILE = 0x0002

METAVERSION100 = 0x0100
METAVERSION300 = 0x0300

META_EOF = 0x0000
META_SAVEDC = 0x001E
META_REALIZEPALETTE = 0x0035
META_SETPALENTRIES = 0x0037
META_CREATEPALETTE = 0x00f7
META_SETBKMODE = 0x0102
META_SETMAPMODE = 0x0103
META_SETROP2 = 0x0104
META_SETRELABS = 0x0105
META_SETPOLYFILLMODE = 0x0106
META_SETSTRETCHBLTMODE = 0x0107
META_SETTEXTCHAREXTRA = 0x0108
META_RESTOREDC = 0x0127
META_INVERTREGION = 0x012A
META_PAINTREGION = 0x012B
META_SELECTCLIPREGION = 0x012C
META_SELECTOBJECT = 0x012D
META_SETTEXTALIGN = 0x012E
META_RESIZEPALETTE = 0x0139
META_DIBCREATEPATTERNBRUSH = 0x0142
META_SETLAYOUT = 0x0149
META_DELETEOBJECT = 0x01f0
META_CREATEPATTERNBRUSH = 0x01F9
META_SETBKCOLOR = 0x0201
META_SETTEXTCOLOR = 0x0209
META_SETTEXTJUSTIFICATION = 0x020A
META_SETWINDOWORG = 0x020B
META_SETWINDOWEXT = 0x020C
META_SETVIEWPORTORG = 0x020D
META_SETVIEWPORTEXT = 0x020E
META_OFFSETWINDOWORG = 0x020F
META_OFFSETVIEWPORTORG = 0x0211
META_LINETO = 0x0213
META_MOVETO = 0x0214
META_OFFSETCLIPRGN = 0x0220
META_FILLREGION = 0x0228
META_SETMAPPERFLAGS = 0x0231
META_SELECTPALETTE = 0x0234
META_CREATEPENINDIRECT = 0x02FA
META_CREATEFONTINDIRECT = 0x02FB
META_CREATEBRUSHINDIRECT = 0x02FC
META_POLYGON = 0x0324
META_POLYLINE = 0x0325
META_SCALEWINDOWEXT = 0x0410
META_SCALEVIEWPORTEXT = 0x0412
META_EXCLUDECLIPRECT = 0x0415
META_INTERSECTCLIPRECT = 0x0416
META_ELLIPSE = 0x0418
META_FLOODFILL = 0x0419
META_RECTANGLE = 0x041B
META_SETPIXEL = 0x041F
META_FRAMEREGION = 0x0429
META_ANIMATEPALETTE = 0x0436
META_TEXTOUT = 0x0521
META_POLYPOLYGON = 0x0538
META_EXTFLOODFILL = 0x0548
META_ROUNDRECT = 0x061C
META_PATBLT = 0x061D
META_ESCAPE = 0x0626
META_CREATEREGION = 0x06FF
META_ARC = 0x0817
META_PIE = 0x081A
META_CHORD = 0x0830
META_BITBLT = 0x0922
META_DIBBITBLT = 0x0940
META_EXTTEXTOUT = 0x0a32
META_STRETCHBLT = 0x0B23
META_DIBSTRETCHBLT = 0x0b41
META_SETDIBTODEV = 0x0d33
META_STRETCHDIB = 0x0f43

WMF_RECORD_NAMES = {
    META_EOF: 'EOF Record',
    META_SAVEDC: 'SaveDC',
    META_REALIZEPALETTE: 'RealizePalette',
    META_SETPALENTRIES: 'SetPalEntries',
    0x004F: 'StartPage',
    0x0050: 'EndPage',
    0x0052: 'AbortDoc',
    0x005E: 'EndDoc',
    META_CREATEPALETTE: 'CreatePalette',
    0x00F8: 'CreateBrush',
    META_SETBKMODE: 'SetBkMode',
    META_SETMAPMODE: 'SetMapMode',
    META_SETROP2: 'SetROP2',
    META_SETRELABS: 'SetRelabs',
    META_SETPOLYFILLMODE: 'SetPolyFillMode',
    META_SETSTRETCHBLTMODE: 'SetStretchBltMode',
    META_SETTEXTCHAREXTRA: 'SetTextCharExtra',
    META_RESTOREDC: 'RestoreDC',
    META_INVERTREGION: 'InvertRegion',
    META_PAINTREGION: 'PaintRegion',
    META_SELECTCLIPREGION: 'SelectClipRegion',
    META_SELECTOBJECT: 'SelectObject',
    META_SETTEXTALIGN: 'SetTextAlign',
    META_RESIZEPALETTE: 'ResizePalette',
    META_DIBCREATEPATTERNBRUSH: 'DibCreatePatternBrush',
    META_SETLAYOUT: 'SetLayout',
    0x014C: 'ResetDС',
    0x014D: 'StartDoc',
    META_DELETEOBJECT: 'DeleteObject',
    META_CREATEPATTERNBRUSH: 'CreatePatternBrush',
    META_SETBKCOLOR: 'SetBkColor',
    META_SETTEXTCOLOR: 'SetTextColor',
    META_SETTEXTJUSTIFICATION: 'SetTextJustification',
    META_SETWINDOWORG: 'SetWindowOrg',
    META_SETWINDOWEXT: 'SetWindowExt',
    META_SETVIEWPORTORG: 'SetViewportOrg',
    META_SETVIEWPORTEXT: 'SetViewportExt',
    META_OFFSETWINDOWORG: 'OffsetWindowOrg',
    META_OFFSETVIEWPORTORG: 'OffsetViewportOrg',
    META_LINETO: 'LineTo',
    META_MOVETO: 'MoveTo',
    META_OFFSETCLIPRGN: 'OffsetClipRgn',
    META_FILLREGION: 'FillRegion',
    META_SETMAPPERFLAGS: 'SetMapperFlags',
    META_SELECTPALETTE: 'SelectPalette',
    META_CREATEPENINDIRECT: 'CreatePenIndirect',
    META_CREATEFONTINDIRECT: 'CreateFontIndirect',
    META_CREATEBRUSHINDIRECT: 'CreateBrushIndirect',
    0x02FD: 'CreateBitmapIndirect',
    META_POLYGON: 'Polygon',
    META_POLYLINE: 'Polyline',
    META_SCALEWINDOWEXT: 'ScaleWindowExt',
    META_SCALEVIEWPORTEXT: 'ScaleViewportExt',
    META_EXCLUDECLIPRECT: 'ExcludeClipRect',
    META_INTERSECTCLIPRECT: 'IntersectClipRect',
    META_ELLIPSE: 'Ellipse',
    META_FLOODFILL: 'FloodFill',
    META_RECTANGLE: 'Rectangle',
    META_SETPIXEL: 'SetPixel',
    META_FRAMEREGION: 'FrameRegion',
    META_ANIMATEPALETTE: 'AnimatePalette',
    META_TEXTOUT: 'TextOut',
    META_POLYPOLYGON: 'PolyPolygon',
    META_EXTFLOODFILL: 'ExtFloodFill',
    META_ROUNDRECT: 'RoundRect',
    META_PATBLT: 'PatBlt',
    META_ESCAPE: 'Escape',
    0x062F: 'DrawText',
    0x06FE: 'CreateBitmap',
    META_CREATEREGION: 'CreateRegion',
    META_ARC: 'Arc',
    META_PIE: 'Pie',
    META_CHORD: 'Chord',
    META_BITBLT: 'BitBlt',
    META_DIBBITBLT: 'DibBitblt',
    META_EXTTEXTOUT: 'ExtTextOut',
    META_STRETCHBLT: 'StretchBlt',
    META_DIBSTRETCHBLT: 'DibStretchBlt',
    META_SETDIBTODEV: 'SetDibToDev',
    META_STRETCHDIB: 'StretchDIBits',
}

ALTERNATE = 0x0001
WINDING = 0x0002

BS_SOLID = 0x0000
BS_HATCHED = 0x0002

HS_HORIZONTAL = 0x0000
HS_VERTICAL = 0x0001
HS_FDIAGONAL = 0x0002
HS_BDIAGONAL = 0x0003
HS_CROSS = 0x0004
HS_DIAGCROSS = 0x0005

TRANSPARENT = 0x0001
OPAQUE = 0x0002

R2_COPYPEN = 0x000D

DPSNAA = 0x20
DIB_RGB_COLORS = 0x0000
DIB_PAL_COLORS = 0x0001
DIB_PAL_INDICES = 0x0002

TA_NOUPDATECP = 0x0000
TA_UPDATECP = 0x0001

TA_LEFT = 0x0000
TA_RIGHT = 0x0002
TA_CENTER = 0x0006

TA_TOP = 0x0000
TA_BOTTOM = 0x0008
TA_BASELINE = 0x0018

TA_RTLREADING = 0x0100

PS_COSMETIC = 0x0000
PS_ENDCAP_ROUND = 0x0000
PS_JOIN_ROUND = 0x0000
PS_SOLID = 0x0000
PS_DASH = 0x0001
PS_DOT = 0x0002
PS_DASHDOT = 0x0003
PS_DASHDOTDOT = 0x0004
PS_NULL = 0x0005
PS_INSIDEFRAME = 0x0006
PS_USERSTYLE = 0x0007
PS_ALTERNATE = 0x0008
PS_ENDCAP_SQUARE = 0x0100
PS_ENDCAP_FLAT = 0x0200
PS_JOIN_BEVEL = 0x1000
PS_JOIN_MITER = 0x2000

META_DASHES = {
    PS_SOLID: [],
    PS_DASH: [10, 6],
    PS_DOT: [2, 2],
    PS_DASHDOT: [6, 4, 2, 4],
    PS_DASHDOTDOT: [6, 2, 2, 2, 2, 2],
}

ANSI_CHARSET = 0x00000000
DEFAULT_CHARSET = 0x00000001
SYMBOL_CHARSET = 0x00000002
MAC_CHARSET = 0x0000004D
SHIFTJIS_CHARSET = 0x00000080
HANGUL_CHARSET = 0x00000081
JOHAB_CHARSET = 0x00000082
GB2312_CHARSET = 0x00000086
CHINESEBIG5_CHARSET = 0x00000088
GREEK_CHARSET = 0x000000A1
TURKISH_CHARSET = 0x000000A2
VIETNAMESE_CHARSET = 0x000000A3
HEBREW_CHARSET = 0x000000B1
ARABIC_CHARSET = 0x000000B2
BALTIC_CHARSET = 0x000000BA
RUSSIAN_CHARSET = 0x000000CC
THAI_CHARSET = 0x000000DE
EASTEUROPE_CHARSET = 0x000000EE
OEM_CHARSET = 0x000000FF

META_CHARSETS = {
    ANSI_CHARSET: 'cp1252',
    DEFAULT_CHARSET: 'cp1252',
    SYMBOL_CHARSET: 'cp1252',
    MAC_CHARSET: 'mac_roman',
    SHIFTJIS_CHARSET: 'cp932',
    HANGUL_CHARSET: 'cp949',
    JOHAB_CHARSET: 'cp1361',
    GB2312_CHARSET: 'cp936',
    CHINESEBIG5_CHARSET: 'cp950',
    GREEK_CHARSET: 'cp1253',
    TURKISH_CHARSET: 'cp1254',
    VIETNAMESE_CHARSET: 'cp1258',
    HEBREW_CHARSET: 'cp1255',
    ARABIC_CHARSET: 'cp1256',
    BALTIC_CHARSET: 'cp1257',
    RUSSIAN_CHARSET: 'cp1251',
    THAI_CHARSET: 'cp874',
    EASTEUROPE_CHARSET: 'cp1250',
    OEM_CHARSET: 'cp1252',
}

PLACEABLE_MARKUP = [(0, 4, 'WMF Signature'), (4, 2, 'HWmf handle'),
    (6, 8, 'BoundingBox'), (14, 2, 'Inch'), (16, 4, 'Reserved'),
    (20, 2, 'Checksum')]
HEADER_MARKUP = [(0, 2, 'Type'), (2, 2, 'HeaderSize'), (4, 2, 'Version'),
    (6, 2, 'SizeLow'), (8, 2, 'SizeHigh'), (10, 2, 'NumberOfObjects'),
    (12, 4, 'MaxRecord'), (16, 2, 'NumberOfMembers (0x0000)'), ]

GENERIC_FIELDS = [(0, 4, 'Record size'), (4, 2, 'WMF record type')]

RECORD_MARKUPS = {
    # State Record Types
    META_SETBKMODE: [(6, 2, 'BkMode'), ],
    META_SETBKCOLOR: [(6, 4, 'ColorRef'), ],
    META_SETROP2: [(6, 2, 'DrawMode'), ],
    META_SETWINDOWORG: [(6, 2, 'Y'), (8, 2, 'X')],
    META_SETWINDOWEXT: [(6, 2, 'Y'), (8, 2, 'X')],
    META_SETPOLYFILLMODE: [(6, 2, 'PolyFillMode'), (8, 2, 'Reserved')],
    META_SETMAPMODE: [(6, 2, 'MapMode'), ],
    META_SETTEXTCOLOR: [(6, 4, 'ColorRef'), ],
    META_SETTEXTALIGN: [(6, 2, 'TextAlignmentMode'), ],

    # Object Record Types
    META_SELECTOBJECT: [(6, 2, 'Object id'), ],
    META_DELETEOBJECT: [(6, 2, 'Object id'), ],
    META_CREATEPENINDIRECT: [(6, 2, 'PenStyle'), (8, 4, 'Width'),
        (12, 4, 'ColorRef'), ],
    META_CREATEBRUSHINDIRECT: [(6, 2, 'BrushStyle'), (8, 4, 'ColorRef'),
        (12, 2, 'BrushHatch'), ],

    # Drawing Record Types
    META_ELLIPSE: [(6, 2, 'bottom'), (8, 2, 'right'), (10, 2, 'top'),
        (12, 2, 'left'), ],
    META_ARC: [(6, 2, 'YEndArc'), (8, 2, 'XEndArc'), (10, 2, 'YStartArc'),
        (12, 2, 'XStartArc'),
        (14, 2, 'BottomRect'), (16, 2, 'RightRect'), (18, 2, 'TopRect'),
        (20, 2, 'LeftRect'), ],
    META_PIE: [(6, 2, 'YRadial2'), (8, 2, 'XRadial2'), (10, 2, 'YRadial1'),
        (12, 2, 'XRadial1'),
        (14, 2, 'BottomRect'), (16, 2, 'RightRect'), (18, 2, 'TopRect'),
        (20, 2, 'LeftRect'), ],
    META_CHORD: [(6, 2, 'YRadial2'), (8, 2, 'XRadial2'), (10, 2, 'YRadial1'),
        (12, 2, 'XRadial1'),
        (14, 2, 'BottomRect'), (16, 2, 'RightRect'), (18, 2, 'TopRect'),
        (20, 2, 'LeftRect'), ],
    META_RECTANGLE: [(6, 2, 'bottom'), (8, 2, 'right'), (10, 2, 'top'),
        (12, 2, 'left'), ],
    META_ROUNDRECT: [(6, 2, 'Height'), (8, 2, 'Width'), (10, 2, 'bottom'),
        (12, 2, 'right'), (14, 2, 'top'), (16, 2, 'left'), ],
    META_POLYGON: [(6, 2, 'Number o fPoints'), ],
    META_MOVETO: [(6, 2, 'Y'), (8, 2, 'X')],
    META_LINETO: [(6, 2, 'Y'), (8, 2, 'X')],
}
