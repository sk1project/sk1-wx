#
#  Copyright (C) 2019 by Maxim S. Barabash
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version = 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https:#www.gnu.org/licenses/>.


from uc2.uc2const import COLOR_RGB, COLOR_CMYK, COLOR_GRAY


XAR_SIGNATURE = b'XARA\xa3\xa3\r\n'


CO_ORDINATES_DPI = 72000.0

# Navigation records
TAG_UP = 0
TAG_DOWN = 1
TAG_FILEHEADER = 2
TAG_ENDOFFILE = 3

# Tag management
TAG_ATOMICTAGS = 10
TAG_ESSENTIALTAGS = 11
TAG_TAGDESCRIPTION = 12

# Compression tags
TAG_STARTCOMPRESSION = 30
TAG_ENDCOMPRESSION = 31

# Document tags
TAG_DOCUMENT = 40
TAG_CHAPTER = 41
TAG_SPREAD = 42

# Notes

TAG_LAYER = 43
TAG_PAGE = 44
TAG_SPREADINFORMATION = 45
TAG_GRIDRULERSETTINGS = 46
TAG_GRIDRULERORIGIN = 47
TAG_LAYERDETAILS = 48
TAG_GUIDELAYERDETAILS = 49
TAG_SPREADSCALING_ACTIVE = 52
TAG_SPREADSCALING_INACTIVE = 53

# Colour reference tags
TAG_DEFINERGBCOLOUR = 50
TAG_DEFINECOMPLEXCOLOUR = 51

# Bitmap reference tags
TAG_RESERVED_60 = 60
TAG_PREVIEWBITMAP_GIF = 61
TAG_PREVIEWBITMAP_JPEG = 62
TAG_PREVIEWBITMAP_PNG = 63
TAG_RESERVED_64 = 64
TAG_RESERVED_65 = 65
TAG_RESERVED_66 = 66
TAG_DEFINEBITMAP_JPEG = 67
TAG_DEFINEBITMAP_PNG = 68
TAG_RESERVED_69 = 69
TAG_RESERVED_70 = 70
TAG_DEFINEBITMAP_JPEG8BPP = 71

# View tags
TAG_VIEWPORT = 80
TAG_VIEWQUALITY = 81
TAG_DOCUMENTVIEW = 82

# Document unit tags
TAG_DEFINE_PREFIXUSERUNIT = 85
TAG_DEFINE_SUFFIXUSERUNIT = 86
TAG_DEFINE_DEFAULTUNITS = 87

# Document info tags
TAG_DOCUMENTCOMMENT = 90
TAG_DOCUMENTDATES = 91
TAG_DOCUMENTUNDOSIZE = 92
TAG_DOCUMENTFLAGS = 93
TAG_DOCUMENTINFORMATION = 4136

# Object tags
TAG_PATH = 100
TAG_PATH_FILLED = 101
TAG_PATH_STROKED = 102
TAG_PATH_FILLED_STROKED = 103
TAG_GROUP = 104
TAG_BLEND = 105
TAG_BLENDER = 106
TAG_MOULD_ENVELOPE = 107
TAG_MOULD_PERSPECTIVE = 108
TAG_MOULD_GROUP = 109
TAG_MOULD_PATH = 110
TAG_PATH_FLAGS = 111
TAG_GUIDELINE = 112
TAG_PATH_RELATIVE = 113
TAG_PATH_RELATIVE_FILLED = 114
TAG_PATH_RELATIVE_STROKED = 115
TAG_PATH_RELATIVE_FILLED_STROKED = 116
TAG_RESERVED_117 = 117
TAG_PATHREF_TRANSFORM = 118

# Attribute tags
TAG_FLATFILL = 150
TAG_LINECOLOUR = 151
TAG_LINEWIDTH = 152
TAG_LINEARFILL = 153
TAG_CIRCULARFILL = 154
TAG_ELLIPTICALFILL = 155
TAG_CONICALFILL = 156
TAG_BITMAPFILL = 157
TAG_CONTONEBITMAPFILL = 158
TAG_FRACTALFILL = 159
TAG_FILLEFFECT_FADE = 160
TAG_FILLEFFECT_RAINBOW = 161
TAG_FILLEFFECT_ALTRAINBOW = 162
TAG_FILL_REPEATING = 163
TAG_FILL_NONREPEATING = 164
TAG_FILL_REPEATINGINVERTED = 165
TAG_FLATTRANSPARENTFILL = 166
TAG_LINEARTRANSPARENTFILL = 167
TAG_CIRCULARTRANSPARENTFILL = 168
TAG_ELLIPTICALTRANSPARENTFILL = 169
TAG_CONICALTRANSPARENTFILL = 170
TAG_BITMAPTRANSPARENTFILL = 171
TAG_FRACTALTRANSPARENTFILL = 172
TAG_LINETRANSPARENCY = 173
TAG_STARTCAP = 174
TAG_ENDCAP = 175
TAG_JOINSTYLE = 176
TAG_MITRELIMIT = 177
TAG_WINDINGRULE = 178
TAG_QUALITY = 179
TAG_TRANSPARENTFILL_REPEATING = 180
TAG_TRANSPARENTFILL_NONREPEATING = 181
TAG_TRANSPARENTFILL_REPEATINGINVERTED = 182

# Arrows and dash patterns
TAG_DASHSTYLE = 183
TAG_DEFINEDASH = 184
TAG_ARROWHEAD = 185
TAG_ARROWTAIL = 186
TAG_DEFINEARROW = 187
TAG_DEFINEDASH_SCALED = 188

# User Attributes
TAG_USERVALUE = 189

# special colour fills
TAG_FLATFILL_NONE = 190
TAG_FLATFILL_BLACK = 191
TAG_FLATFILL_WHITE = 192
TAG_LINECOLOUR_NONE = 193
TAG_LINECOLOUR_BLACK = 194
TAG_LINECOLOUR_WHITE = 195

# Bitmaps
TAG_NODE_BITMAP = 198
TAG_NODE_CONTONEDBITMAP = 199

# New fill type records
TAG_DIAMONDFILL = 200
TAG_DIAMONDTRANSPARENTFILL = 201
TAG_THREECOLFILL = 202
TAG_THREECOLTRANSPARENTFILL = 203
TAG_FOURCOLFILL = 204
TAG_FOURCOLTRANSPARENTFILL = 205
TAG_FILL_REPEATING_EXTRA = 206
TAG_TRANSPARENTFILL_REPEATING_EXTRA = 207

# Regular shapes
# Ellipses
TAG_ELLIPSE_SIMPLE = 1000
TAG_ELLIPSE_COMPLEX = 1001

# Rectangles
TAG_RECTANGLE_SIMPLE = 1100
TAG_RECTANGLE_SIMPLE_REFORMED = 1101  # Deprecated
TAG_RECTANGLE_SIMPLE_STELLATED = 1102  # Deprecated
TAG_RECTANGLE_SIMPLE_STELLATED_REFORMED = 1103  # Deprecated
TAG_RECTANGLE_SIMPLE_ROUNDED = 1104
TAG_RECTANGLE_SIMPLE_ROUNDED_REFORMED = 1105  # Deprecated
TAG_RECTANGLE_SIMPLE_ROUNDED_STELLATED = 1106  # Deprecated
TAG_RECTANGLE_SIMPLE_ROUNDED_STELLATED_REFORMED = 1107  # Deprecated
TAG_RECTANGLE_COMPLEX = 1108
TAG_RECTANGLE_COMPLEX_REFORMED = 1109  # Deprecated
TAG_RECTANGLE_COMPLEX_STELLATED = 1110  # Deprecated
TAG_RECTANGLE_COMPLEX_STELLATED_REFORMED = 1111  # Deprecated
TAG_RECTANGLE_COMPLEX_ROUNDED = 1112
TAG_RECTANGLE_COMPLEX_ROUNDED_REFORMED = 1113  # Deprecated
TAG_RECTANGLE_COMPLEX_ROUNDED_STELLATED = 1114  # Deprecated
TAG_RECTANGLE_COMPLEX_ROUNDED_STELLATED_REFORMED = 1115  # Deprecated

# Polygons
TAG_POLYGON_COMPLEX = 1200
TAG_POLYGON_COMPLEX_REFORMED = 1201  # Deprecated
TAG_POLYGON_COMPLEX_STELLATED = 1212  # Deprecated
TAG_POLYGON_COMPLEX_STELLATED_REFORMED = 1213  # Deprecated
TAG_POLYGON_COMPLEX_ROUNDED = 1214
TAG_POLYGON_COMPLEX_ROUNDED_REFORMED = 1215
TAG_POLYGON_COMPLEX_ROUNDED_STELLATED = 1216
TAG_POLYGON_COMPLEX_ROUNDED_STELLATED_REFORMED = 1217  # Deprecated

# General regular shapes
TAG_REGULAR_SHAPE_PHASE_1 = 1900
TAG_REGULAR_SHAPE_PHASE_2 = 1901

# Text related records
# Text definitions
TAG_FONT_DEF_TRUETYPE = 2000
TAG_FONT_DEF_ATM = 2001

# vanilla text story objects
TAG_TEXT_STORY_SIMPLE = 2100
TAG_TEXT_STORY_COMPLEX = 2101

# text story objects on a path
TAG_TEXT_STORY_SIMPLE_START_LEFT = 2110
TAG_TEXT_STORY_SIMPLE_START_RIGHT = 2111
TAG_TEXT_STORY_SIMPLE_END_LEFT = 2112
TAG_TEXT_STORY_SIMPLE_END_RIGHT = 2113
TAG_TEXT_STORY_COMPLEX_START_LEFT = 2114
TAG_TEXT_STORY_COMPLEX_START_RIGHT = 2115
TAG_TEXT_STORY_COMPLEX_END_LEFT = 2116
TAG_TEXT_STORY_COMPLEX_END_RIGHT = 2117

# Text story information records
TAG_TEXT_STORY_WORD_WRAP_INFO = 2150
TAG_TEXT_STORY_INDENT_INFO = 2151

# other text story related objects
TAG_TEXT_LINE = 2200
TAG_TEXT_STRING = 2201
TAG_TEXT_CHAR = 2202
TAG_TEXT_EOL = 2203
TAG_TEXT_KERN = 2204
TAG_TEXT_CARET = 2205
TAG_TEXT_LINE_INFO = 2206

# Text attributes
TAG_TEXT_LINESPACE_RATIO = 2900
TAG_TEXT_LINESPACE_ABSOLUTE = 2901
TAG_TEXT_JUSTIFICATION_LEFT = 2902
TAG_TEXT_JUSTIFICATION_CENTRE = 2903
TAG_TEXT_JUSTIFICATION_RIGHT = 2904
TAG_TEXT_JUSTIFICATION_FULL = 2905
TAG_TEXT_FONT_SIZE = 2906
TAG_TEXT_FONT_TYPEFACE = 2907
TAG_TEXT_BOLD_ON = 2908
TAG_TEXT_BOLD_OFF = 2909
TAG_TEXT_ITALIC_ON = 2910
TAG_TEXT_ITALIC_OFF = 2911
TAG_TEXT_UNDERLINE_ON = 2912
TAG_TEXT_UNDERLINE_OFF = 2913
TAG_TEXT_SCRIPT_ON = 2914
TAG_TEXT_SCRIPT_OFF = 2915
TAG_TEXT_SUPERSCRIPT_ON = 2916
TAG_TEXT_SUBSCRIPT_ON = 2917
TAG_TEXT_TRACKING = 2918
TAG_TEXT_ASPECT_RATIO = 2919
TAG_TEXT_BASELINE = 2920

# Imagesetting attributes
TAG_OVERPRINTLINEON = 3500
TAG_OVERPRINTLINEOFF = 3501
TAG_OVERPRINTFILLON = 3502
TAG_OVERPRINTFILLOFF = 3503
TAG_PRINTONALLPLATESON = 3504
TAG_PRINTONALLPLATESOFF = 3505

# Document Print/Imagesetting options
TAG_PRINTERSETTINGS = 3506
TAG_IMAGESETTING = 3507
TAG_COLOURPLATE = 3508

# Registration mark records
TAG_PRINTMARKDEFAULT = 3509
TAG_RESERVED_3510 = 3510

# Stroking records
TAG_VARIABLEWIDTHFUNC = 4000  # This record is not currently used
TAG_VARIABLEWIDTHTABLE = 4001
TAG_STROKETYPE = 4002
TAG_STROKEDEFINITION = 4003  # This record is not currently used
TAG_STROKEAIRBRUSH = 4004  # This record is not currently used

# Fractal Noise records
TAG_NOISEFILL = 4010
TAG_NOISETRANSPARENTFILL = 4011

# Mould bounds record
TAG_MOULD_BOUNDS = 4012

# Bitmap export hint record
TAG_EXPORT_HINT = 4015

# Web Address tags
TAG_WEBADDRESS = 4020
TAG_WEBADDRESS_BOUNDINGBOX = 4021

# Frame layer tags
TAG_LAYER_FRAMEPROPS = 4030
TAG_SPREAD_ANIMPROPS = 4031

# Wizard properties tags
TAG_WIZOP = 4040
TAG_WIZOP_STYLE = 4041
TAG_WIZOP_STYLEREF = 4042

# Shadow tags
TAG_SHADOWCONTROLLER = 4050
TAG_SHADOW = 4051

# Bevel tags
TAG_BEVEL = 4052
TAG_BEVATTR_INDENT = 4053  # Deprecated
TAG_BEVATTR_LIGHTANGLE = 4054  # Deprecated
TAG_BEVATTR_CONTRAST = 4055  # Deprecated
TAG_BEVATTR_TYPE = 4056  # Deprecated
TAG_BEVELINK = 4057

# Blend on a curve tags
TAG_BLENDER_CURVEPROP = 4060
TAG_BLEND_PATH = 4061
TAG_BLENDER_CURVEANGLES = 4062

# Contouring tags
TAG_CONTOURCONTROLLER = 4066
TAG_CONTOUR = 4067

# Set tags
TAG_SETSENTINEL = 4070
TAG_SETPROPERTY = 4071

# More Blend on a curve tags
TAG_BLENDPROFILES = 4072
TAG_BLENDERADDITIONAL = 4073
TAG_NODEBLENDPATH_FILLED = 4074

# Multi stage fill tags
TAG_LINEARFILLMULTISTAGE = 4075
TAG_CIRCULARFILLMULTISTAGE = 4076
TAG_ELLIPTICALFILLMULTISTAGE = 4077
TAG_CONICALFILLMULTISTAGE = 4078

# Brush attribute tags
TAG_BRUSHATTR = 4079
TAG_BRUSHDEFINITION = 4080
TAG_BRUSHDATA = 4081
TAG_MOREBRUSHDATA = 4082
TAG_MOREBRUSHATTR = 4083

# ClipView tags
TAG_CLIPVIEWCONTROLLER = 4084
TAG_CLIPVIEW = 4085

# Feathering tags
TAG_FEATHER = 4086

# Bar properties tag
TAG_BARPROPERTY = 4087

# Other multi stage fill tags
TAG_SQUAREFILLMULTISTAGE = 4088

# More brush tags
TAG_EVENMOREBRUSHDATA = 4102
TAG_EVENMOREBRUSHATTR = 4103
TAG_TIMESTAMPBRUSHDATA = 4104
TAG_BRUSHPRESSUREINFO = 4105
TAG_BRUSHPRESSUREDATA = 4106
TAG_BRUSHATTRPRESSUREINFO = 4107
TAG_BRUSHCOLOURDATA = 4108
TAG_BRUSHPRESSURESAMPLEDATA = 4109
TAG_BRUSHTIMESAMPLEDATA = 4110
TAG_BRUSHATTRFILLFLAGS = 4111
TAG_BRUSHTRANSPINFO = 4112
TAG_BRUSHATTRTRANSPINFO = 4113

# Nudge size record
TAG_DOCUMENTNUDGE = 4114

# Bitmap properties record
TAG_BITMAP_PROPERTIES = 4115

# Bitmap smoothing record
TAG_DOCUMENTBITMAPSMOOTHING = 4116

# XPE bitmap processing record
TAG_XPE_BITMAP_PROPERTIES = 4117

# XPE Bitmap file format placeholder record
TAG_DEFINEBITMAP_XPE = 4118

# Current attributes records
TAG_CURRENTATTRIBUTES = 4119
TAG_CURRENTATTRIBUTEBOUNDS = 4120

# = 3-point linear fill records
TAG_LINEARFILL3POINT = 4121
TAG_LINEARFILLMULTISTAGE3POINT = 4122
TAG_LINEARTRANSPARENTFILL3POINT = 4123

# Duplication distance record
TAG_DUPLICATIONOFFSET = 4124

# Bitmap effect tags
TAG_LIVE_EFFECT = 4125
TAG_LOCKED_EFFECT = 4126
TAG_FEATHER_EFFECT = 4127

# Miscellaneous records
TAG_COMPOUNDRENDER = 4128
TAG_OBJECTBOUNDS = 4129
TAG_SPREAD_PHASE2 = 4131
TAG_CURRENTATTRIBUTES_PHASE2 = 4132
TAG_SPREAD_FLASHPROPS = 4134
TAG_PRINTERSETTINGS_PHASE2 = 4135
TAG_CLIPVIEW_PATH = 4137
TAG_DEFINEBITMAP_PNG_REAL = 4138
TAG_TEXT_STRING_POS = 4139
TAG_SPREAD_FLASHPROPS2 = 4140
TAG_TEXT_LINESPACE_LEADING = 4141

# New text records
TAG_TEXT_TAB = 4200
TAG_TEXT_LEFT_INDENT = 4201
TAG_TEXT_FIRST_INDENT = 4202
TAG_TEXT_RIGHT_INDENT = 4203
TAG_TEXT_RULER = 4204
TAG_TEXT_STORY_HEIGHT_INFO = 4205
TAG_TEXT_STORY_LINK_INFO = 4206
TAG_TEXT_STORY_TRANSLATION_INFO = 4207
TAG_TEXT_SPACE_BEFORE = 4208
TAG_TEXT_SPACE_AFTER = 4209
TAG_TEXT_SPECIAL_HYPHEN = 4210
TAG_TEXT_SOFT_RETURN = 4211
TAG_TEXT_EXTRA_FONT_INFO = 4212
TAG_TEXT_EXTRA_TT_FONT_DEF = 4213
TAG_TEXT_EXTRA_ATM_FONT_DEF = 4214


# Tag that is not in specification
TAG_SPREAD_PHOTO_PROPERTIES = 4147
TAG_FLASH_PROPERTIES_4 = 4383
TAG_PAGE_PROPERTIES_2 = 4429
TAG_LIVE_SHARE_ATTRIBUTE = 4499


FILE_TYPE_PAPER_PUBLISH = b'CXN'
FILE_TYPE_WEB = b'CXW'


# Colors
RGB_BLACK = [COLOR_RGB, [0.0, 0.0, 0.0], 1.0, 'black']
RGB_WHITE = [COLOR_RGB, [1.0, 1.0, 1.0], 1.0, 'white']

CMYK_BLACK = [COLOR_CMYK, [0.0, 0.0, 0.0, 1.0], 1.0, 'black']
CMYK_WHITE = [COLOR_CMYK, [0.0, 0.0, 0.0, 0.0], 1.0, 'white']

GREYSCALE_BLACK = [COLOR_GRAY, [1.0], 1.0, 'black']
GREYSCALE_WHITE = [COLOR_GRAY, [0.0], 1.0, 'white']

# Ref Colors
REF_DEFAULTCOLOUR_NONE = -1
REF_DEFAULTCOLOUR_BLACK = -2
REF_DEFAULTCOLOUR_WHITE = -3
REF_DEFAULTCOLOUR_RED = -4
REF_DEFAULTCOLOUR_GREEN = -5
REF_DEFAULTCOLOUR_BLUE = -6
REF_DEFAULTCOLOUR_CYAN = -7
REF_DEFAULTCOLOUR_MAGENTA = -8
REF_DEFAULTCOLOUR_YELLOW = -9
REF_DEFAULTCOLOUR_KEY = -10


REPLACEMENTCOLOUR = RGB_BLACK

XAR_COLOURS = {
    -1: [COLOR_RGB, [1.00, 1.00, 1.00], 0.0, 'transparent'],
    -2: [COLOR_RGB, [0.00, 0.00, 0.00], 1.0, 'black'],
    -3: [COLOR_RGB, [1.00, 1.00, 1.00], 1.0, 'white'],
    -4: [COLOR_RGB, [1.00, 0.00, 0.00], 1.0, 'red'],
    -5: [COLOR_RGB, [0.00, 1.00, 0.00], 1.0, 'green'],
    -6: [COLOR_RGB, [0.00, 0.00, 1.00], 1.0, 'blue'],
    -7: [COLOR_CMYK, [1.00, 0.00, 0.00, 0.0], 1.0, 'cyan'],
    -8: [COLOR_CMYK, [0.00, 1.00, 0.00, 0.0], 1.0, 'magenta'],
    -9: [COLOR_CMYK, [0.00, 0.00, 1.00, 0.0], 1.0, 'yellow'],
    -10: [COLOR_CMYK, [0.00, 0.00, 0.00, 1.0], 1.0, 'key']
}

# Colour models
COLOUR_MODEL_RGB = 2
COLOUR_MODEL_CMYK = 3
COLOUR_MODEL_HSV = 4
COLOUR_MODEL_GREYSCALE = 5

# Colour types
COLOUR_TYPE_NORMAL = 0
COLOUR_TYPE_SPOT = 1
COLOUR_TYPE_TINT = 2
COLOUR_TYPE_LINKED = 3
COLOUR_TYPE_SHADE = 4

# Default Units
REF_UNIT_MILLIMETRES = -2
REF_UNIT_CENTIMETRES = -3
REF_UNIT_METRES = -4
REF_UNIT_KILOMETRES = -5
REF_UNIT_MILLIPOINTS = -6
REF_UNIT_COMP_POINTS = -7
REF_UNIT_PICAS = -8
REF_UNIT_INCHES = -9
REF_UNIT_FEET = -10
REF_UNIT_YARDS = -11
REF_UNIT_MILES = -12
REF_UNIT_PIXELS = -13

# Possible values for Path Verb
PT_MOVETO = 0x6
PT_LINETO = 0x2
PT_BEZIERTO = 0x4

# Stroke props
JOIN_MITRE = 0
JOIN_ROUND = 1
JOIN_BEVEL = 2

CAP_BUTT = 0
CAP_ROUND = 1
CAP_SQUARE = 2

FILL_NONZERO = 0
FILL_EVENODD = 2


# Defaults

REF_DASH_1 = -1
REF_DASH_2 = -2
REF_DASH_3 = -3
REF_DASH_4 = -4
REF_DASH_5 = -5
REF_DASH_6 = -6
REF_DASH_7 = -7
REF_DASH_8 = -8
REF_DASH_9 = -9
REF_DASH_10 = -10
REF_DASH_11 = -11
REF_DASH_12 = -12
REF_DASH_13 = -13
REF_DASH_14 = -14
REF_DASH_15 = -15
REF_DASH_16 = -16
REF_DASH_17 = -17
REF_DASH_18 = -18
REF_DASH_19 = -19
REF_DASH_20 = -20
REF_DASH_SOLID = -21
REF_DASH_GUIDELAYER = -22

XAR_DASHS = {
    REF_DASH_1: [2, 2],
    REF_DASH_2: [4, 2],
    REF_DASH_3: [8, 2],
    REF_DASH_4: [16, 2],
    REF_DASH_5: [24, 2],
    REF_DASH_6: [4, 4],
    REF_DASH_7: [8, 4],
    REF_DASH_8: [16, 4],
    REF_DASH_9: [8, 8],
    REF_DASH_10: [16, 8],
    REF_DASH_11: [4, 2, 2, 2],
    REF_DASH_12: [8, 2, 2, 2],
    REF_DASH_13: [16, 2, 2, 2],
    REF_DASH_14: [8, 2, 4, 2],
    REF_DASH_15: [16, 2, 4, 2],
    REF_DASH_16: [8, 2, 2, 2, 2, 2],
    REF_DASH_17: [16, 2, 2, 2, 2, 2],
    REF_DASH_18: [8, 2, 2, 2, 2, 2, 2, 2],
    REF_DASH_19: [16, 2, 2, 2, 2, 2, 2, 2],
    REF_DASH_20: [8, 2, 2, 2, 4, 2, 2, 2],
    REF_DASH_SOLID: None,
    REF_DASH_GUIDELAYER: [2, 2],
}

# in spec 'Whether the guide-line is vertical (1) or horizontal (2)'
# but this is not true
GUIDELINE_HORIZONTAL = 1
GUIDELINE_VERTICAL = 2

TEXT_ALIGN_LEFT = 0
TEXT_ALIGN_CENTRE = 1
TEXT_ALIGN_RIGHT = 2
TEXT_ALIGN_FULL = 3

XAR_DEFAULT_STYLE = {
    'text_font_family': 'Time New Roman',
    'text_bold': False,
    'text_italic': False,
    'text_script_size': 10.0,
    'text_justification': TEXT_ALIGN_LEFT,
    'mitre_limit': 4000,
    'end_arrow': None,
    'start_arrow': None,
    'start_cap': CAP_BUTT,
    'dash_pattern': REF_DASH_SOLID,
    'quality': 110,
    'join_type': JOIN_BEVEL,
    'winding_rule': FILL_EVENODD,
    'line_width': 0.501,
    'fill_effect': None,
    'transp_fill_mapping_linear': None,
    'fill_mapping_linear': None,
    'flat_transp_fill': None,
    'flat_colour_fill': None,
    # 'StrokeTransp',
    'stroke_transparency': 0.0,
    'stroke_colour': RGB_BLACK,
    'feather': None,
    'stroke_type': 0x01000000,
    # addition
    'pattern_fill': None,
    'gradient_fill': None,
    'fill_repeating': None,
    'fill_trafo': None,
    'path_flags': None,
}


"""
description: Schema xar records
type: object
definitions:
    type:
        description: type of records
        type: object
        properties:
            id:
                description: string identifier as an alias to digital
                type: string
            doc:
                description: record description
                type: string
            sec:
                description: sequence of properties
                type: array
                items:
                    type: object
                    allOf: {$ref: #/definitions/sec}
            deprecated:
                description:
                type: boolean
    sec:
        description: properties
        type: object
        properties:
            id:
                description: property id
                type: string
            type:
                description: type of value
                type: string
            number:
                description: | property id comprising a number of values,
                               number of values or -1
                type: [string, integer]
            bitfield:
                description: is a data structure above value
                type: object
                allOf: {$ref: #/definitions/bitfield}
            encoding:
                description: additional property used in some types
                type: string
            enum:
                description: additional property used in some types
                type: object
                allOf: {$ref: #/definitions/enum}

    bitfield:
        description: data structure any single bit or group of bits
        type: object
        propertyNames:
            type: integer
        properties:
            id:
                description: | bit identifier with which you can access
                               the value of the flags
                type: string
            type:
                description:
                type: string
                enum: [bool]
    enum:
        type: object
        properties:
            value:
                description:
                type: [int, float, string]
"""

XAR_RECORD_HEADER_SIZE = 8
XAR_RECORD_HEADER = {
    'sec': [
        {'type': 'uint32', 'id': 'cid'},
        {'type': 'uint32', 'id': 'record_size'},
    ]
}

XAR_RECORD_DATA_SPEC = {

    # Navigation records
    TAG_UP: {'id': 'TAG_UP'},
    TAG_DOWN: {'id': 'TAG_DOWN'},
    TAG_FILEHEADER: {
        'id': 'TAG_FILEHEADER',
        'doc': 'This record gives useful information about the file. '
               'This should always be the first record in any file produced.',
        'sec': [
            {'type': '3bytes', 'id': 'file_type',
             'enum': {
                 '0': {'value': FILE_TYPE_PAPER_PUBLISH},
                 '1': {'value': FILE_TYPE_WEB}
             }
            },
            {'type': 'uint32', 'id': 'file_size'},
            {'type': 'uint32', 'id': 'web_link'},
            {'type': 'uint32', 'id': 'refinement_flags'},
            {'type': 'ASCII_STRING', 'id': 'producer'},
            {'type': 'ASCII_STRING', 'id': 'producer_version'},
            {'type': 'ASCII_STRING', 'id': 'producer_build'},
        ]
    },
    TAG_ENDOFFILE: {'id': 'TAG_ENDOFFILE'},

    # Tag management
    TAG_ATOMICTAGS: {'id': 'TAG_ATOMICTAGS'},
    TAG_ESSENTIALTAGS: {'id': 'TAG_ESSENTIALTAGS'},
    TAG_TAGDESCRIPTION: {
        'id': 'TAG_TAGDESCRIPTION',
        'sec': [
            {'type': 'uint32', 'id': 'number_of_tags'},
            {'type': 'Tag Description', 'id': 'description',
             'number': 'number_of_tags'}
        ]
    },

    # Compression tags
    TAG_STARTCOMPRESSION: {
        'id': 'TAG_STARTCOMPRESSION',
        'sec': [
            {'type': '3bytes', 'id': 'compression_version', 'encoding': 'hex'},
            {'type': 'byte', 'id': 'compression_type'},
        ]
    },
    TAG_ENDCOMPRESSION: {
        'id': 'TAG_ENDCOMPRESSION',
        'sec': [
            {'type': 'uint32', 'id': 'compression_crc'},
            {'type': 'uint32', 'id': 'num_bytes'}
        ]
    },

    # Document tags
    TAG_DOCUMENT: {'id': 'TAG_DOCUMENT'},
    TAG_CHAPTER: {'id': 'TAG_CHAPTER'},
    TAG_SPREAD: {'id': 'TAG_SPREAD'},

    # Notes
    TAG_LAYER: {'id': 'TAG_LAYER'},
    TAG_PAGE: {
        'id': 'TAG_PAGE',
        'sec': [
            {'type': 'COORD', 'id': 'bottom_left'},
            {'type': 'COORD', 'id': 'top_right'},
            {'type': 'COLOURREF', 'id': 'colour'},
        ]
    },
    TAG_SPREADINFORMATION: {
        'id': 'TAG_SPREADINFORMATION',
        'sec': [
            {'type': 'MILLIPOINT', 'id': 'width'},
            {'type': 'MILLIPOINT', 'id': 'height'},
            {'type': 'MILLIPOINT', 'id': 'margin'},
            {'type': 'MILLIPOINT', 'id': 'bleed'},
            {'type': 'byte', 'id': 'spread_flags',
             'bitfield': {
                 0: {'type': 'bool', 'id': 'double_page_spread'},
                 1: {'type': 'bool', 'id': 'show_drop_shadow'},
                 2: {'type': 'bool', 'id': 'selected_spread'},
                 3: {'type': 'bool', 'id': 'print_whole_spread'},
                 4: {'type': 'bool', 'id': 'negate_x'},
                 5: {'type': 'bool', 'id': 'negate_y'},
             }
            }
        ]
    },
    TAG_GRIDRULERSETTINGS: {'id': 'TAG_GRIDRULERSETTINGS'},
    TAG_GRIDRULERORIGIN: {'id': 'TAG_GRIDRULERORIGIN'},
    TAG_LAYERDETAILS: {
        'id': 'TAG_LAYERDETAILS',
        'sec': [
            {'type': 'byte', 'id': 'layer_flags',
             'bitfield': {
                 0: {'type': 'bool', 'id': 'is_visible'},
                 1: {'type': 'bool', 'id': 'is_locked'},
                 2: {'type': 'bool', 'id': 'is_printable'},
                 3: {'type': 'bool', 'id': 'is_active'},
             }
            },
            {'type': 'STRING', 'id': 'layer_name'},
        ]
    },
    TAG_GUIDELAYERDETAILS: {'id': 'TAG_GUIDELAYERDETAILS'},
    TAG_SPREADSCALING_ACTIVE: {
        'id': 'TAG_SPREADSCALING_ACTIVE',
        'sec': [
            {'type': 'double', 'id': 'drawing_scale'},
            {'type': 'UNITSREF', 'id': 'drawing_units'},
            {'type': 'double', 'id': 'real_scale'},
            {'type': 'UNITSREF', 'id': 'real_units'},
        ]
    },
    TAG_SPREADSCALING_INACTIVE: {
        'id': 'TAG_SPREADSCALING_INACTIVE',
        'sec': [
            {'type': 'double', 'id': 'drawing_scale'},
            {'type': 'UNITSREF', 'id': 'drawing_units'},
            {'type': 'double', 'id': 'real_scale'},
            {'type': 'UNITSREF', 'id': 'real_units'},
        ]
    },

    # Colour reference tags
    TAG_DEFINERGBCOLOUR: {
        'id': 'TAG_DEFINERGBCOLOUR',
        'sec': [
            {'type': 'byte', 'id': 'red'},
            {'type': 'byte', 'id': 'green'},
            {'type': 'byte', 'id': 'blue'}
        ]
    },
    TAG_DEFINECOMPLEXCOLOUR: {
        'id': 'TAG_DEFINECOMPLEXCOLOUR',
        'sec': [
            {'type': 'Simple RGBColour', 'id': 'rgbcolour', 'encoding': 'hex'},
            {'type': 'byte', 'id': 'colour_model'},
            {'type': 'byte', 'id': 'colour_type'},
            {'type': 'uint32', 'id': 'entry_index'},
            {'type': 'COLOURREF', 'id': 'parent_colour'},
            {'type': 'fixed24', 'id': 'component1'},
            {'type': 'fixed24', 'id': 'component2'},
            {'type': 'fixed24', 'id': 'component3'},
            {'type': 'fixed24', 'id': 'component4'},
            {'type': 'STRING', 'id': 'colour_name'},
        ]
    },

    # Bitmap reference tags
    TAG_PREVIEWBITMAP_GIF: {
        'id': 'TAG_PREVIEWBITMAP_GIF',
        'sec': [
            {'type': 'BITMAP_DATA', 'id': 'bitmap_data'}
        ]
    },
    TAG_PREVIEWBITMAP_JPEG: {
        'id': 'TAG_PREVIEWBITMAP_JPEG',
        'sec': [
            {'type': 'BITMAP_DATA', 'id': 'bitmap_data'}
        ]
    },
    TAG_PREVIEWBITMAP_PNG: {
        'id': 'TAG_PREVIEWBITMAP_PNG',
        'sec': [
            {'type': 'BITMAP_DATA', 'id': 'bitmap_data'}
        ]
    },
    TAG_DEFINEBITMAP_JPEG: {
        'id': 'TAG_DEFINEBITMAP_JPEG',
        'sec': [
            {'type': 'STRING', 'id': 'bitmap_name'},
            {'type': 'BITMAP_DATA', 'id': 'bitmap_data'},
        ]
    },
    TAG_DEFINEBITMAP_PNG: {
        'id': 'TAG_DEFINEBITMAP_PNG',
        'sec': [
            {'type': 'STRING', 'id': 'bitmap_name'},
            {'type': 'BITMAP_DATA', 'id': 'bitmap_data'},
        ]
    },
    TAG_DEFINEBITMAP_JPEG8BPP: {'id': 'TAG_DEFINEBITMAP_JPEG8BPP'},

    # View tags
    TAG_VIEWPORT: {
        'id': 'TAG_VIEWPORT',
        'sec': [
            {'type': 'COORD', 'id': 'bottom_left'},
            {'type': 'COORD', 'id': 'top_right'},
        ]
    },
    TAG_VIEWQUALITY: {'id': 'TAG_VIEWQUALITY'},
    TAG_DOCUMENTVIEW: {'id': 'TAG_DOCUMENTVIEW'},

    # Document unit tags
    TAG_DEFINE_PREFIXUSERUNIT: {'id': 'TAG_DEFINE_PREFIXUSERUNIT'},
    TAG_DEFINE_SUFFIXUSERUNIT: {'id': 'TAG_DEFINE_SUFFIXUSERUNIT'},
    TAG_DEFINE_DEFAULTUNITS: {
        'id': 'TAG_DEFINE_DEFAULTUNITS',
        'sec': [
            {'type': 'UNITSREF', 'id': 'page_units'},
            {'type': 'UNITSREF', 'id': 'font_units'}
        ]
    },

    # Document info tags
    TAG_DOCUMENTCOMMENT: {
        'id': 'TAG_DOCUMENTCOMMENT',
        'sec': [
            {'type': 'STRING', 'id': 'comment'},
        ]
    },
    TAG_DOCUMENTDATES: {'id': 'TAG_DOCUMENTDATES'},
    TAG_DOCUMENTUNDOSIZE: {'id': 'TAG_DOCUMENTUNDOSIZE'},
    TAG_DOCUMENTFLAGS: {
        'id': 'TAG_DOCUMENTFLAGS',
        'sec': [
            {'type': 'uint32', 'id': 'document_flags',
             'bitfield': {
                 0: {'type': 'bool', 'id': 'multilayer_flag'},
                 1: {'type': 'bool', 'id': 'all_layers_visible_flag'},
             }
            }
        ]
    },
    TAG_DOCUMENTINFORMATION: {'id': 'TAG_DOCUMENTINFORMATION'},

    # Object tags
    TAG_PATH: {
        'id': 'TAG_PATH',
        'sec': [
            {'type': 'uint32', 'id': 'number_of_coords'},
            {'type': 'byte', 'id': 'verb', 'number': 'number_of_coords'},
            {'type': 'COORD', 'id': 'coord', 'number': 'number_of_coords'},
        ]
    },
    TAG_PATH_FILLED: {
        'id': 'TAG_PATH_FILLED',
        'sec': [
            {'type': 'uint32', 'id': 'number_of_coords'},
            {'type': 'byte', 'id': 'verb', 'number': 'number_of_coords'},
            {'type': 'COORD', 'id': 'coord', 'number': 'number_of_coords'},
        ]
    },
    TAG_PATH_STROKED: {
        'id': 'TAG_PATH_STROKED',
        'sec': [
            {'type': 'uint32', 'id': 'number_of_coords'},
            {'type': 'byte', 'id': 'verb', 'number': 'number_of_coords'},
            {'type': 'COORD', 'id': 'coord', 'number': 'number_of_coords'},
        ]
    },
    TAG_PATH_FILLED_STROKED: {
        'id': 'TAG_PATH_FILLED_STROKED',
        'sec': [
            {'type': 'uint32', 'id': 'number_of_coords'},
            {'type': 'byte', 'id': 'verb', 'number': 'number_of_coords'},
            {'type': 'COORD', 'id': 'coord', 'number': 'number_of_coords'},
        ]
    },
    TAG_GROUP: {'id': 'TAG_GROUP', 'sec': None},
    TAG_BLEND: {'id': 'TAG_BLEND'},
    TAG_BLENDER: {'id': 'TAG_BLENDER'},
    TAG_MOULD_ENVELOPE: {'id': 'TAG_MOULD_ENVELOPE'},
    TAG_MOULD_PERSPECTIVE: {'id': 'TAG_MOULD_PERSPECTIVE'},
    TAG_MOULD_GROUP: {'id': 'TAG_MOULD_GROUP'},
    TAG_MOULD_PATH: {'id': 'TAG_MOULD_PATH'},
    TAG_PATH_FLAGS: {
        'id': 'TAG_PATH_FLAGS',
        'sec': [
            {'type': 'byte', 'id': 'flags', "number": -1,
             'bitfield': {
                 0: {'type': 'bool', 'id': 'is_smooth'},
                 1: {'type': 'bool', 'id': 'is_rotate'},
                 2: {'type': 'bool', 'id': 'is_end_point'},
             }
            }
        ]
    },
    TAG_GUIDELINE: {
        'id': 'TAG_GUIDELINE',
        'sec': [
            {'type': 'byte', 'id': 'type'},
            {'type': 'MILLIPOINT', 'id': 'ordinate'},
        ]
    },
    TAG_PATH_RELATIVE: {
        'id': 'TAG_PATH_RELATIVE',
        'sec': [
            {'type': 'Verb and Coord List', 'id': 'path'}
        ]
    },
    TAG_PATH_RELATIVE_FILLED: {
        'id': 'TAG_PATH_RELATIVE_FILLED',
        'sec': [
            {'type': 'Verb and Coord List', 'id': 'path'}
        ]
    },
    TAG_PATH_RELATIVE_STROKED: {
        'id': 'TAG_PATH_RELATIVE_STROKED',
        'sec': [
            {'type': 'Verb and Coord List', 'id': 'path'}
        ]
    },
    TAG_PATH_RELATIVE_FILLED_STROKED: {
        'id': 'TAG_PATH_RELATIVE_FILLED_STROKED',
        'sec': [
            {'type': 'Verb and Coord List', 'id': 'path'}
        ]
    },
    TAG_PATHREF_TRANSFORM: {
        'id': 'TAG_PATHREF_TRANSFORM',
        'sec': [
            {'type': 'DATAREF', 'id': 'path_ref'},
            # MATRIX
            {'type': 'fixed16', 'id': 'a'},
            {'type': 'fixed16', 'id': 'b'},
            {'type': 'fixed16', 'id': 'c'},
            {'type': 'fixed16', 'id': 'd'},
            {'type': 'int32', 'id': 'e'},
            {'type': 'int32', 'id': 'f'},
        ]
    },

    # Attribute tags
    TAG_FLATFILL: {
        'id': 'TAG_FLATFILL',
        'sec': [
            {'type': 'COLOURREF', 'id': 'colour'}
        ]
    },
    TAG_LINECOLOUR: {
        'id': 'TAG_LINECOLOUR',
        'sec': [
            {'type': 'COLOURREF', 'id': 'colour'}
        ]
    },
    TAG_LINEWIDTH: {
        'id': 'TAG_LINEWIDTH',
        'sec': [
            {'type': 'MILLIPOINT', 'id': 'width'}
        ]
    },
    TAG_LINEARFILL: {
        'id': 'TAG_LINEARFILL',
        'sec': [
            {'type': 'COORD', 'id': 'start_point'},
            {'type': 'COORD', 'id': 'end_point'},
            {'type': 'COLOURREF', 'id': 'start_colour'},
            {'type': 'COLOURREF', 'id': 'end_colour'},
            {'type': 'double', 'id': 'bias'},
            {'type': 'double', 'id': 'gain'},
            # TODO: support 3 point
        ]
    },
    TAG_CIRCULARFILL: {
        'id': 'TAG_CIRCULARFILL',
        'sec': [
            {'type': 'COORD', 'id': 'centre_point'},
            {'type': 'COORD', 'id': 'edge_point'},
            {'type': 'COLOURREF', 'id': 'start_colour'},
            {'type': 'COLOURREF', 'id': 'end_colour'},
            # PROFILE
            {'type': 'double', 'id': 'bias'},
            {'type': 'double', 'id': 'gain'},
        ]
    },
    TAG_ELLIPTICALFILL: {
        'id': 'TAG_ELLIPTICALFILL',
        'sec': [
            {'type': 'COORD', 'id': 'centre_point'},
            {'type': 'COORD', 'id': 'major_axes'},
            {'type': 'COORD', 'id': 'minor_axes'},
            {'type': 'COLOURREF', 'id': 'start_colour'},
            {'type': 'COLOURREF', 'id': 'end_colour'},
            # PROFILE
            {'type': 'double', 'id': 'bias'},
            {'type': 'double', 'id': 'gain'},
        ]
    },
    TAG_CONICALFILL: {'id': 'TAG_CONICALFILL'},
    TAG_BITMAPFILL: {
        'id': 'TAG_BITMAPFILL',
        'sec': [
            {'type': 'COORD', 'id': 'bottom_left'},
            {'type': 'COORD', 'id': 'bottom_right'},
            {'type': 'COORD', 'id': 'top_left'},
            {'type': 'BITMAPREF', 'id': 'bitmap'},
            # PROFILE
            {'type': 'double', 'id': 'bias'},
            {'type': 'double', 'id': 'gain'},
        ]
    },
    TAG_CONTONEBITMAPFILL: {
        'id': 'TAG_CONTONEBITMAPFILL',
        'sec': [
            {'type': 'COORD', 'id': 'bottom_left'},
            {'type': 'COORD', 'id': 'bottom_right'},
            {'type': 'COORD', 'id': 'top_left'},
            {'type': 'COLOURREF', 'id': 'start_colour'},
            {'type': 'COLOURREF', 'id': 'end_colour'},
            {'type': 'BITMAPREF', 'id': 'bitmap'},
            # PROFILE
            {'type': 'double', 'id': 'bias'},
            {'type': 'double', 'id': 'gain'},
        ]
    },
    TAG_FRACTALFILL: {
        'id': 'TAG_FRACTALFILL',
        'sec': [
            {'type': 'COORD', 'id': 'bottom_left'},
            {'type': 'COORD', 'id': 'bottom_right'},
            {'type': 'COORD', 'id': 'top_left'},
            {'type': 'COLOURREF', 'id': 'start_colour'},
            {'type': 'COLOURREF', 'id': 'end_colour'},
            {'type': 'int32', 'id': 'seed'},
            {'type': 'fixed16', 'id': 'graininess'},
            {'type': 'fixed16', 'id': 'gravity'},
            {'type': 'fixed16', 'id': 'squash'},
            {'type': 'uint32', 'id': 'resolution'},
            {'type': 'byte', 'id': 'tileable'},
            # PROFILE
            {'type': 'double', 'id': 'bias'},
            {'type': 'double', 'id': 'gain'},
        ]
    },
    TAG_FILLEFFECT_FADE: {'id': 'TAG_FILLEFFECT_FADE'},
    TAG_FILLEFFECT_RAINBOW: {'id': 'TAG_FILLEFFECT_RAINBOW'},
    TAG_FILLEFFECT_ALTRAINBOW: {'id': 'TAG_FILLEFFECT_ALTRAINBOW'},
    TAG_FILL_REPEATING: {'id': 'TAG_FILL_REPEATING'},
    TAG_FILL_NONREPEATING: {'id': 'TAG_FILL_NONREPEATING'},
    TAG_FILL_REPEATINGINVERTED: {'id': 'TAG_FILL_REPEATINGINVERTED'},
    TAG_FLATTRANSPARENTFILL: {
        'id': 'TAG_FLATTRANSPARENTFILL',
        'sec': [
            {'type': 'byte', 'id': 'transparency'},
            {'type': 'byte', 'id': 'transparency_type'}
        ]
    },
    TAG_LINEARTRANSPARENTFILL: {
        'id': 'TAG_LINEARTRANSPARENTFILL',
        'sec': [
            {'type': 'COORD', 'id': 'start_point'},
            {'type': 'COORD', 'id': 'end_point'},
            {'type': 'byte', 'id': 'start_transparency'},
            {'type': 'byte', 'id': 'end_transparency'},
            {'type': 'byte', 'id': 'transparency_type'},
            # PROFILE
            {'type': 'double', 'id': 'bias'},
            {'type': 'double', 'id': 'gain'},
            # TODO: support 3 point
        ]
    },
    TAG_CIRCULARTRANSPARENTFILL: {'id': 'TAG_CIRCULARTRANSPARENTFILL'},
    TAG_ELLIPTICALTRANSPARENTFILL: {'id': 'TAG_ELLIPTICALTRANSPARENTFILL'},
    TAG_CONICALTRANSPARENTFILL: {'id': 'TAG_CONICALTRANSPARENTFILL'},
    TAG_BITMAPTRANSPARENTFILL: {'id': 'TAG_BITMAPTRANSPARENTFILL'},
    TAG_FRACTALTRANSPARENTFILL: {'id': 'TAG_FRACTALTRANSPARENTFILL'},
    TAG_LINETRANSPARENCY: {'id': 'TAG_LINETRANSPARENCY'},
    TAG_STARTCAP: {
        'id': 'TAG_STARTCAP',
        'sec': [
            {'type': 'byte', 'id': 'cap_style'},
        ]
    },
    TAG_ENDCAP: {'id': 'TAG_ENDCAP'},
    TAG_JOINSTYLE: {
        'id': 'TAG_JOINSTYLE',
        'sec': [
            {'type': 'byte', 'id': 'join_style'},
        ]
    },
    TAG_MITRELIMIT: {
        'id': 'TAG_MITRELIMIT',
        'sec': [
            {'type': 'byte', 'id': 'mitre_limit'},
        ]
    },
    TAG_WINDINGRULE: {
        'id': 'TAG_WINDINGRULE',
        'sec': [
            {'type': 'byte', 'id': 'winding_rule'},
        ]
    },
    TAG_QUALITY: {'id': 'TAG_QUALITY'},
    TAG_TRANSPARENTFILL_REPEATING: {
        'id': 'TAG_TRANSPARENTFILL_REPEATING'
    },
    TAG_TRANSPARENTFILL_NONREPEATING: {
        'id': 'TAG_TRANSPARENTFILL_NONREPEATING'
    },
    TAG_TRANSPARENTFILL_REPEATINGINVERTED: {
        'id': 'TAG_TRANSPARENTFILL_REPEATINGINVERTED'
    },

    # Arrows and dash patterns
    TAG_DASHSTYLE: {
        'id': 'TAG_DASHSTYLE',
        'sec': [
            {'type': 'int32', 'id': 'dash_id'},
        ]
    },
    TAG_DEFINEDASH: {
        'id': 'TAG_DEFINEDASH',
        'sec': [
            {'type': 'MILLIPOINT', 'id': 'dash_start'},
            {'type': 'MILLIPOINT', 'id': 'line_width'},
            {'type': 'uint32', 'id': 'elements'},
            {'type': 'MILLIPOINT', 'id': 'dash_def', 'number': 'elements'},
        ]
    },
    TAG_ARROWHEAD: {'id': 'TAG_ARROWHEAD'},
    TAG_ARROWTAIL: {'id': 'TAG_ARROWTAIL'},
    TAG_DEFINEARROW: {'id': 'TAG_DEFINEARROW'},
    TAG_DEFINEDASH_SCALED: {
        'id': 'TAG_DEFINEDASH_SCALED',
        'sec': [
            {'type': 'MILLIPOINT', 'id': 'dash_start'},
            {'type': 'MILLIPOINT', 'id': 'line_width'},
            {'type': 'uint32', 'id': 'elements'},
            {'type': 'MILLIPOINT', 'id': 'dash_def', 'number': 'elements'},
        ]
    },

    # User Attributes
    TAG_USERVALUE: {'id': 'TAG_USERVALUE'},

    # special colour fills
    TAG_FLATFILL_NONE: {'id': 'TAG_FLATFILL_NONE'},
    TAG_FLATFILL_BLACK: {'id': 'TAG_FLATFILL_BLACK'},
    TAG_FLATFILL_WHITE: {'id': 'TAG_FLATFILL_WHITE'},
    TAG_LINECOLOUR_NONE: {'id': 'TAG_LINECOLOUR_NONE'},
    TAG_LINECOLOUR_BLACK: {'id': 'TAG_LINECOLOUR_BLACK'},
    TAG_LINECOLOUR_WHITE: {'id': 'TAG_LINECOLOUR_WHITE'},

    # Bitmaps
    TAG_NODE_BITMAP: {
        'id': 'TAG_NODE_BITMAP',
        'sec': [
            {'type': 'COORD', 'id': 'bottom_left'},
            {'type': 'COORD', 'id': 'bottom_right'},
            {'type': 'COORD', 'id': 'top_right'},
            {'type': 'COORD', 'id': 'top_left'},
            {'type': 'BITMAPREF', 'id': 'bitmap'}
        ]
    },
    TAG_NODE_CONTONEDBITMAP: {
        'id': 'TAG_NODE_CONTONEDBITMAP',
        'sec': [
            {'type': 'COORD', 'id': 'bottom_left'},
            {'type': 'COORD', 'id': 'bottom_right'},
            {'type': 'COORD', 'id': 'top_right'},
            {'type': 'COORD', 'id': 'top_left'},
            {'type': 'BITMAPREF', 'id': 'bitmap'},
            {'type': 'COLOURREF', 'id': 'start_colour'},
            {'type': 'COLOURREF', 'id': 'end_colour'},
        ]
    },

    # New fill type records
    TAG_DIAMONDFILL: {'id': 'TAG_DIAMONDFILL'},
    TAG_DIAMONDTRANSPARENTFILL: {'id': 'TAG_DIAMONDTRANSPARENTFILL'},
    TAG_THREECOLFILL: {'id': 'TAG_THREECOLFILL'},
    TAG_THREECOLTRANSPARENTFILL: {'id': 'TAG_THREECOLTRANSPARENTFILL'},
    TAG_FOURCOLFILL: {'id': 'TAG_FOURCOLFILL'},
    TAG_FOURCOLTRANSPARENTFILL: {'id': 'TAG_FOURCOLTRANSPARENTFILL'},
    TAG_FILL_REPEATING_EXTRA: {'id': 'TAG_FILL_REPEATING_EXTRA'},
    TAG_TRANSPARENTFILL_REPEATING_EXTRA: {
        'id': 'TAG_TRANSPARENTFILL_REPEATING_EXTRA'
    },

    # Regular shapes

    # Ellipses
    TAG_ELLIPSE_SIMPLE: {
        'id': 'TAG_ELLIPSE_SIMPLE',
        'sec': [
            {'type': 'COORD', 'id': 'centre'},
            {'type': 'MILLIPOINT', 'id': 'width'},
            {'type': 'MILLIPOINT', 'id': 'height'}
        ]
    },
    TAG_ELLIPSE_COMPLEX: {
        'id': 'TAG_ELLIPSE_COMPLEX',
        'sec': [
            {'type': 'COORD', 'id': 'centre'},
            {'type': 'COORD', 'id': 'major_axis'},
            {'type': 'COORD', 'id': 'minor_axis'}
        ]
    },

    # Rectangles
    TAG_RECTANGLE_SIMPLE: {'id': 'TAG_RECTANGLE_SIMPLE'},
    TAG_RECTANGLE_SIMPLE_REFORMED: {
        'id': 'TAG_RECTANGLE_SIMPLE_REFORMED',
        'deprecated': True
    },
    TAG_RECTANGLE_SIMPLE_STELLATED: {
        'id': 'TAG_RECTANGLE_SIMPLE_STELLATED',
        'deprecated': True
    },
    TAG_RECTANGLE_SIMPLE_STELLATED_REFORMED: {
        'id': 'TAG_RECTANGLE_SIMPLE_STELLATED_REFORMED',
        'deprecated': True
    },
    TAG_RECTANGLE_SIMPLE_ROUNDED: {
        'id': 'TAG_RECTANGLE_SIMPLE_ROUNDED'
    },
    TAG_RECTANGLE_SIMPLE_ROUNDED_REFORMED: {
        'id': 'TAG_RECTANGLE_SIMPLE_ROUNDED_REFORMED',
        'deprecated': True
    },
    TAG_RECTANGLE_SIMPLE_ROUNDED_STELLATED: {
        'id': 'TAG_RECTANGLE_SIMPLE_ROUNDED_STELLATED',
        'deprecated': True
    },
    TAG_RECTANGLE_SIMPLE_ROUNDED_STELLATED_REFORMED: {
        'id': 'TAG_RECTANGLE_SIMPLE_ROUNDED_STELLATED_REFORMED',
        'deprecated': True
    },
    TAG_RECTANGLE_COMPLEX: {
        'id': 'TAG_RECTANGLE_COMPLEX'
    },
    TAG_RECTANGLE_COMPLEX_REFORMED: {
        'id': 'TAG_RECTANGLE_COMPLEX_REFORMED',
        'deprecated': True
    },
    TAG_RECTANGLE_COMPLEX_STELLATED: {
        'id': 'TAG_RECTANGLE_COMPLEX_STELLATED'
    },
    TAG_RECTANGLE_COMPLEX_STELLATED_REFORMED: {
        'id': 'TAG_RECTANGLE_COMPLEX_STELLATED_REFORMED',
        'deprecated': True
    },
    TAG_RECTANGLE_COMPLEX_ROUNDED: {
        'id': 'TAG_RECTANGLE_COMPLEX_ROUNDED'
    },
    TAG_RECTANGLE_COMPLEX_ROUNDED_REFORMED: {
        'id': 'TAG_RECTANGLE_COMPLEX_ROUNDED_REFORMED',
        'deprecated': True
    },
    TAG_RECTANGLE_COMPLEX_ROUNDED_STELLATED: {
        'id': 'TAG_RECTANGLE_COMPLEX_ROUNDED_STELLATED',
        'deprecated': True
    },
    TAG_RECTANGLE_COMPLEX_ROUNDED_STELLATED_REFORMED: {
        'id': 'TAG_RECTANGLE_COMPLEX_ROUNDED_STELLATED_REFORMED',
        'deprecated': True
    },

    # Polygons
    TAG_POLYGON_COMPLEX: {'id': 'TAG_POLYGON_COMPLEX'},
    TAG_POLYGON_COMPLEX_REFORMED: {
        'id': 'TAG_POLYGON_COMPLEX_REFORMED',
        'deprecated': True
    },
    TAG_POLYGON_COMPLEX_STELLATED: {
        'id': 'TAG_POLYGON_COMPLEX_STELLATED',
        'deprecated': True
    },
    TAG_POLYGON_COMPLEX_STELLATED_REFORMED: {
        'id': 'TAG_POLYGON_COMPLEX_STELLATED_REFORMED',
        'deprecated': True
    },
    TAG_POLYGON_COMPLEX_ROUNDED: {'id': 'TAG_POLYGON_COMPLEX_ROUNDED'},
    TAG_POLYGON_COMPLEX_ROUNDED_REFORMED: {
        'id': 'TAG_POLYGON_COMPLEX_ROUNDED_REFORMED'},
    TAG_POLYGON_COMPLEX_ROUNDED_STELLATED: {
        'id': 'TAG_POLYGON_COMPLEX_ROUNDED_STELLATED'},
    TAG_POLYGON_COMPLEX_ROUNDED_STELLATED_REFORMED: {
        'id': 'TAG_POLYGON_COMPLEX_ROUNDED_STELLATED_REFORMED',
        'deprecated': True
    },

    # General regular shapes
    TAG_REGULAR_SHAPE_PHASE_1: {'id': 'TAG_REGULAR_SHAPE_PHASE_1'},
    TAG_REGULAR_SHAPE_PHASE_2: {
        'id': 'TAG_REGULAR_SHAPE_PHASE_2',
        'sec': [
            {'type': 'byte', 'id': 'flags',
             'bitfield': {
                 0: {'type': 'bool', 'id': 'circular_flag'},
                 1: {'type': 'bool', 'id': 'stellated_flag'},
                 2: {'type': 'bool', 'id': 'primary_curvature_flag'},
                 3: {'type': 'bool', 'id': 'stellation_curvature_flag'}
             }
             },
            {'type': 'uint16', 'id': 'number_of_sides'},
            {'type': 'COORD', 'id': 'major_axes'},
            {'type': 'COORD', 'id': 'minor_axes'},

            {'type': 'fixed16', 'id': 'a'},
            {'type': 'fixed16', 'id': 'b'},
            {'type': 'fixed16', 'id': 'c'},
            {'type': 'fixed16', 'id': 'd'},
            {'type': 'int32', 'id': 'e'},
            {'type': 'int32', 'id': 'f'},

            {'type': 'double', 'id': 'stell_radius_to_primary'},
            {'type': 'double', 'id': 'StellOffsetRatio'},
            {'type': 'double', 'id': 'PrimaryCurveToPrimary'},
            {'type': 'double', 'id': 'StellCurveToPrimary'},
            # EdgePath1
            {'type': 'uint32', 'id': 'number_of_coords'},
            {'type': 'byte', 'id': 'verb', 'number': 'number_of_coords'},
            {'type': 'COORD', 'id': 'coord', 'number': 'number_of_coords'},
            # EdgePath2
            {'type': 'uint32', 'id': 'number_of_coords2'},
            {'type': 'byte', 'id': 'verb2', 'number': 'number_of_coords2'},
            {'type': 'COORD', 'id': 'coord2', 'number': 'number_of_coords2'},
        ]
    },

    # Text related records
    # Text definitions
    TAG_FONT_DEF_TRUETYPE: {
        'id': 'TAG_FONT_DEF_TRUETYPE',
        'sec': [
            {'type': 'STRING', 'id': 'full_font_name'},
            {'type': 'STRING', 'id': 'typeface_name'},
            {'type': 'byte', 'id': 'panose', 'number': 10}
        ]
    },
    TAG_FONT_DEF_ATM: {'id': 'TAG_FONT_DEF_ATM'},

    # vanilla text story objects
    TAG_TEXT_STORY_SIMPLE: {
        'id': 'TAG_TEXT_STORY_SIMPLE',
        'sec': [
            {'type': 'COORD', 'id': 'anchor'},
            {'type': 'int32', 'id': 'kerning_flag'}
        ]
    },
    TAG_TEXT_STORY_COMPLEX: {
        'id': 'TAG_TEXT_STORY_COMPLEX',
        'sec': [
            {'type': 'fixed16', 'id': 'a'},
            {'type': 'fixed16', 'id': 'b'},
            {'type': 'fixed16', 'id': 'c'},
            {'type': 'fixed16', 'id': 'd'},
            {'type': 'int32', 'id': 'e'},
            {'type': 'int32', 'id': 'f'},
            {'type': 'int32', 'id': 'kerning_flag'}
        ]
    },

    # text story objects on a path
    TAG_TEXT_STORY_SIMPLE_START_LEFT: {
        'id': 'TAG_TEXT_STORY_SIMPLE_START_LEFT',
        'sec': [
            {'type': 'COORD', 'id': 'anchor'},
            {'type': 'int32', 'id': 'kerning_flag'}
        ]
    },
    TAG_TEXT_STORY_SIMPLE_START_RIGHT: {
        'id': 'TAG_TEXT_STORY_SIMPLE_START_RIGHT',
        'sec': [
            {'type': 'COORD', 'id': 'anchor'},
            {'type': 'int32', 'id': 'kerning_flag'}
        ]
    },
    TAG_TEXT_STORY_SIMPLE_END_LEFT: {
        'id': 'TAG_TEXT_STORY_SIMPLE_END_LEFT',
        'sec': [
            {'type': 'COORD', 'id': 'anchor'},
            {'type': 'int32', 'id': 'kerning_flag'}
        ]
    },
    TAG_TEXT_STORY_SIMPLE_END_RIGHT: {
        'id': 'TAG_TEXT_STORY_SIMPLE_END_RIGHT',
        'sec': [
            {'type': 'COORD', 'id': 'anchor'},
            {'type': 'int32', 'id': 'kerning_flag'}
        ]
    },
    TAG_TEXT_STORY_COMPLEX_START_LEFT: {
        'id': 'TAG_TEXT_STORY_COMPLEX_START_LEFT',
        'sec': [
            {'type': 'fixed16', 'id': 'a'},
            {'type': 'fixed16', 'id': 'b'},
            {'type': 'fixed16', 'id': 'c'},
            {'type': 'fixed16', 'id': 'd'},
            {'type': 'int32', 'id': 'e'},
            {'type': 'int32', 'id': 'f'},
            {'type': 'int32', 'id': 'kerning_flag'}
        ]
    },
    TAG_TEXT_STORY_COMPLEX_START_RIGHT: {
        'id': 'TAG_TEXT_STORY_COMPLEX_START_RIGHT',
        'sec': [
            {'type': 'fixed16', 'id': 'a'},
            {'type': 'fixed16', 'id': 'b'},
            {'type': 'fixed16', 'id': 'c'},
            {'type': 'fixed16', 'id': 'd'},
            {'type': 'int32', 'id': 'e'},
            {'type': 'int32', 'id': 'f'},
            {'type': 'int32', 'id': 'kerning_flag'}
        ]
    },
    TAG_TEXT_STORY_COMPLEX_END_LEFT: {
        'id': 'TAG_TEXT_STORY_COMPLEX_END_LEFT',
        'sec': [
            {'type': 'fixed16', 'id': 'a'},
            {'type': 'fixed16', 'id': 'b'},
            {'type': 'fixed16', 'id': 'c'},
            {'type': 'fixed16', 'id': 'd'},
            {'type': 'int32', 'id': 'e'},
            {'type': 'int32', 'id': 'f'},
            {'type': 'int32', 'id': 'kerning_flag'}
        ]
    },
    TAG_TEXT_STORY_COMPLEX_END_RIGHT: {
        'id': 'TAG_TEXT_STORY_COMPLEX_END_RIGHT',
        'sec': [
            {'type': 'fixed16', 'id': 'a'},
            {'type': 'fixed16', 'id': 'b'},
            {'type': 'fixed16', 'id': 'c'},
            {'type': 'fixed16', 'id': 'd'},
            {'type': 'int32', 'id': 'e'},
            {'type': 'int32', 'id': 'f'},
            {'type': 'int32', 'id': 'kerning_flag'}
        ]
    },

    # Text story information records
    TAG_TEXT_STORY_WORD_WRAP_INFO: {'id': 'TAG_TEXT_STORY_WORD_WRAP_INFO'},
    TAG_TEXT_STORY_INDENT_INFO: {'id': 'TAG_TEXT_STORY_INDENT_INFO'},

    # other text story related objects
    TAG_TEXT_LINE: {'id': 'TAG_TEXT_LINE'},
    TAG_TEXT_STRING: {'id': 'TAG_TEXT_STRING'},
    TAG_TEXT_CHAR: {'id': 'TAG_TEXT_CHAR'},
    TAG_TEXT_EOL: {'id': 'TAG_TEXT_EOL'},
    TAG_TEXT_KERN: {'id': 'TAG_TEXT_KERN'},
    TAG_TEXT_CARET: {'id': 'TAG_TEXT_CARET'},
    TAG_TEXT_LINE_INFO: {'id': 'TAG_TEXT_LINE_INFO'},

    # Text attributes
    TAG_TEXT_LINESPACE_RATIO: {'id': 'TAG_TEXT_LINESPACE_RATIO'},
    TAG_TEXT_LINESPACE_ABSOLUTE: {'id': 'TAG_TEXT_LINESPACE_ABSOLUTE'},
    TAG_TEXT_JUSTIFICATION_LEFT: {'id': 'TAG_TEXT_JUSTIFICATION_LEFT'},
    TAG_TEXT_JUSTIFICATION_CENTRE: {'id': 'TAG_TEXT_JUSTIFICATION_CENTRE'},
    TAG_TEXT_JUSTIFICATION_RIGHT: {'id': 'TAG_TEXT_JUSTIFICATION_RIGHT'},
    TAG_TEXT_JUSTIFICATION_FULL: {'id': 'TAG_TEXT_JUSTIFICATION_FULL'},
    TAG_TEXT_FONT_SIZE: {
        'id': 'TAG_TEXT_FONT_SIZE',
        'sec': [
            {'type': 'MILLIPOINT', 'id': 'font_size'}
        ]
    },
    TAG_TEXT_FONT_TYPEFACE: {'id': 'TAG_TEXT_FONT_TYPEFACE'},
    TAG_TEXT_BOLD_ON: {'id': 'TAG_TEXT_BOLD_ON'},
    TAG_TEXT_BOLD_OFF: {'id': 'TAG_TEXT_BOLD_OFF'},
    TAG_TEXT_ITALIC_ON: {'id': 'TAG_TEXT_ITALIC_ON'},
    TAG_TEXT_ITALIC_OFF: {'id': 'TAG_TEXT_ITALIC_OFF'},
    TAG_TEXT_UNDERLINE_ON: {'id': 'TAG_TEXT_UNDERLINE_ON'},
    TAG_TEXT_UNDERLINE_OFF: {'id': 'TAG_TEXT_UNDERLINE_OFF'},
    TAG_TEXT_SCRIPT_ON: {'id': 'TAG_TEXT_SCRIPT_ON'},
    TAG_TEXT_SCRIPT_OFF: {'id': 'TAG_TEXT_SCRIPT_OFF'},
    TAG_TEXT_SUPERSCRIPT_ON: {'id': 'TAG_TEXT_SUPERSCRIPT_ON'},
    TAG_TEXT_SUBSCRIPT_ON: {'id': 'TAG_TEXT_SUBSCRIPT_ON'},
    TAG_TEXT_TRACKING: {'id': 'TAG_TEXT_TRACKING'},
    TAG_TEXT_ASPECT_RATIO: {'id': 'TAG_TEXT_ASPECT_RATIO'},
    TAG_TEXT_BASELINE: {'id': 'TAG_TEXT_BASELINE'},

    # Imagesetting attributes
    TAG_OVERPRINTLINEON: {'id': 'TAG_OVERPRINTLINEON'},
    TAG_OVERPRINTLINEOFF: {'id': 'TAG_OVERPRINTLINEOFF'},
    TAG_OVERPRINTFILLON: {'id': 'TAG_OVERPRINTFILLON'},
    TAG_OVERPRINTFILLOFF: {'id': 'TAG_OVERPRINTFILLOFF'},
    TAG_PRINTONALLPLATESON: {'id': 'TAG_PRINTONALLPLATESON'},
    TAG_PRINTONALLPLATESOFF: {'id': 'TAG_PRINTONALLPLATESOFF'},

    # Document Print/Image setting options
    TAG_PRINTERSETTINGS: {'id': 'TAG_PRINTERSETTINGS'},
    TAG_IMAGESETTING: {'id': 'TAG_IMAGESETTING'},
    TAG_COLOURPLATE: {'id': 'TAG_COLOURPLATE'},

    # Registration mark records
    TAG_PRINTMARKDEFAULT: {'id': 'TAG_PRINTMARKDEFAULT'},

    # Stroking records
    TAG_VARIABLEWIDTHFUNC: {'id': 'TAG_VARIABLEWIDTHFUNC'},
    TAG_VARIABLEWIDTHTABLE: {'id': 'TAG_VARIABLEWIDTHTABLE'},
    TAG_STROKETYPE: {'id': 'TAG_STROKETYPE'},
    TAG_STROKEDEFINITION: {'id': 'TAG_STROKEDEFINITION'},
    TAG_STROKEAIRBRUSH: {'id': 'TAG_STROKEAIRBRUSH'},

    # Fractal Noise records
    TAG_NOISEFILL: {
        'id': 'TAG_NOISEFILL',
        'sec': [
            {'type': 'COORD', 'id': 'bottom_left'},
            {'type': 'COORD', 'id': 'bottom_right'},
            {'type': 'COORD', 'id': 'top_left'},
            {'type': 'COLOURREF', 'id': 'start_colour'},
            {'type': 'COLOURREF', 'id': 'end_colour'},
            {'type': 'fixed16', 'id': 'graininess'},
            {'type': 'int32', 'id': 'seed'},
            {'type': 'uint32', 'id': 'resolution'},
            {'type': 'byte', 'id': 'tileable'},
            # PROFILE
            {'type': 'double', 'id': 'bias'},
            {'type': 'double', 'id': 'gain'},
        ]
    },
    TAG_NOISETRANSPARENTFILL: {'id': 'TAG_NOISETRANSPARENTFILL'},

    # Mould bounds record
    TAG_MOULD_BOUNDS: {'id': 'TAG_MOULD_BOUNDS'},

    # Bitmap export hint record
    TAG_EXPORT_HINT: {'id': 'TAG_EXPORT_HINT'},

    # Web Address tags
    TAG_WEBADDRESS: {'id': 'TAG_WEBADDRESS'},
    TAG_WEBADDRESS_BOUNDINGBOX: {'id': 'TAG_WEBADDRESS_BOUNDINGBOX'},

    # Frame layer tags
    TAG_LAYER_FRAMEPROPS: {'id': 'TAG_LAYER_FRAMEPROPS'},
    TAG_SPREAD_ANIMPROPS: {'id': 'TAG_SPREAD_ANIMPROPS'},

    # Wizard properties tags
    TAG_WIZOP: {'id': 'TAG_WIZOP'},
    TAG_WIZOP_STYLE: {'id': 'TAG_WIZOP_STYLE'},
    TAG_WIZOP_STYLEREF: {'id': 'TAG_WIZOP_STYLEREF'},

    # Shadow tags
    TAG_SHADOWCONTROLLER: {'id': 'TAG_SHADOWCONTROLLER'},
    TAG_SHADOW: {'id': 'TAG_SHADOW'},

    # Bevel tags
    TAG_BEVEL: {'id': 'TAG_BEVEL'},
    TAG_BEVATTR_INDENT: {'id': 'TAG_BEVATTR_INDENT', 'deprecated': True},
    TAG_BEVATTR_LIGHTANGLE: {
        'id': 'TAG_BEVATTR_LIGHTANGLE', 'deprecated': True
    },
    TAG_BEVATTR_CONTRAST: {'id': 'TAG_BEVATTR_CONTRAST', 'deprecated': True},
    TAG_BEVATTR_TYPE: {'id': 'TAG_BEVATTR_TYPE', 'deprecated': True},
    TAG_BEVELINK: {'id': 'TAG_BEVELINK'},

    # Blend on a curve tags
    TAG_BLENDER_CURVEPROP: {'id': 'TAG_BLENDER_CURVEPROP'},
    TAG_BLEND_PATH: {'id': 'TAG_BLEND_PATH'},
    TAG_BLENDER_CURVEANGLES: {'id': 'TAG_BLENDER_CURVEANGLES'},

    # Contouring tags
    TAG_CONTOURCONTROLLER: {'id': 'TAG_CONTOURCONTROLLER'},
    TAG_CONTOUR: {'id': 'TAG_CONTOUR'},

    # Set tags
    TAG_SETSENTINEL: {'id': 'TAG_SETSENTINEL'},
    TAG_SETPROPERTY: {'id': 'TAG_SETPROPERTY'},

    # More Blend on a curve tags
    TAG_BLENDPROFILES: {'id': 'TAG_BLENDPROFILES'},
    TAG_BLENDERADDITIONAL: {'id': 'TAG_BLENDERADDITIONAL'},
    TAG_NODEBLENDPATH_FILLED: {'id': 'TAG_NODEBLENDPATH_FILLED'},

    # Multi stage fill tags
    TAG_LINEARFILLMULTISTAGE: {
        'id': 'TAG_LINEARFILLMULTISTAGE',
        'sec': [
            {'type': 'COORD', 'id': 'start_point'},
            {'type': 'COORD', 'id': 'end_point'},
            {'type': 'COLOURREF', 'id': 'start_colour'},
            {'type': 'COLOURREF', 'id': 'end_colour'},
            {'type': 'uint32', 'id': 'num_cols'},
            {'type': 'StopColour', 'id': 'stop_colors', 'number': 'num_cols'}
            # {'type': 'double', 'id': 'position'},
            # {'type': 'COLOURREF', 'id': 'colour'},
        ]
    },
    TAG_CIRCULARFILLMULTISTAGE: {
        'id': 'TAG_CIRCULARFILLMULTISTAGE',
        'sec': [
            {'type': 'COORD', 'id': 'centre_point'},
            {'type': 'COORD', 'id': 'edge_point'},
            {'type': 'COLOURREF', 'id': 'start_colour'},
            {'type': 'COLOURREF', 'id': 'end_colour'},
            {'type': 'uint32', 'id': 'num_cols'},
            {'type': 'StopColour', 'id': 'stop_colors', 'number': 'num_cols'}
        ]
    },
    TAG_ELLIPTICALFILLMULTISTAGE: {
        'id': 'TAG_ELLIPTICALFILLMULTISTAGE',
        'sec': [
            {'type': 'COORD', 'id': 'centre_point'},
            {'type': 'COORD', 'id': 'major_axes'},
            {'type': 'COORD', 'id': 'minor_axes'},
            {'type': 'COLOURREF', 'id': 'start_colour'},
            {'type': 'COLOURREF', 'id': 'end_colour'},
            {'type': 'uint32', 'id': 'num_cols'},
            {'type': 'StopColour', 'id': 'stop_colors', 'number': 'num_cols'}
        ]
    },
    TAG_CONICALFILLMULTISTAGE: {'id': 'TAG_CONICALFILLMULTISTAGE'},

    # Brush attribute tags
    TAG_BRUSHATTR: {'id': 'TAG_BRUSHATTR'},
    TAG_BRUSHDEFINITION: {'id': 'TAG_BRUSHDEFINITION'},
    TAG_BRUSHDATA: {'id': 'TAG_BRUSHDATA'},
    TAG_MOREBRUSHDATA: {'id': 'TAG_MOREBRUSHDATA'},
    TAG_MOREBRUSHATTR: {'id': 'TAG_MOREBRUSHATTR'},

    # ClipView tags
    TAG_CLIPVIEWCONTROLLER: {'id': 'TAG_CLIPVIEWCONTROLLER'},
    TAG_CLIPVIEW: {'id': 'TAG_CLIPVIEW'},

    # Feathering tags
    TAG_FEATHER: {'id': 'TAG_FEATHER'},

    # Bar properties tag
    TAG_BARPROPERTY: {'id': 'TAG_BARPROPERTY'},

    # Other multi stage fill tags
    TAG_SQUAREFILLMULTISTAGE: {'id': 'TAG_SQUAREFILLMULTISTAGE'},

    # More brush tags
    TAG_EVENMOREBRUSHDATA: {'id': 'TAG_EVENMOREBRUSHDATA'},
    TAG_EVENMOREBRUSHATTR: {'id': 'TAG_EVENMOREBRUSHATTR'},
    TAG_TIMESTAMPBRUSHDATA: {'id': 'TAG_TIMESTAMPBRUSHDATA'},
    TAG_BRUSHPRESSUREINFO: {'id': 'TAG_BRUSHPRESSUREINFO'},
    TAG_BRUSHPRESSUREDATA: {'id': 'TAG_BRUSHPRESSUREDATA'},
    TAG_BRUSHATTRPRESSUREINFO: {'id': 'TAG_BRUSHATTRPRESSUREINFO'},
    TAG_BRUSHCOLOURDATA: {'id': 'TAG_BRUSHCOLOURDATA'},
    TAG_BRUSHPRESSURESAMPLEDATA: {'id': 'TAG_BRUSHPRESSURESAMPLEDATA'},
    TAG_BRUSHTIMESAMPLEDATA: {'id': 'TAG_BRUSHTIMESAMPLEDATA'},
    TAG_BRUSHATTRFILLFLAGS: {'id': 'TAG_BRUSHATTRFILLFLAGS'},
    TAG_BRUSHTRANSPINFO: {'id': 'TAG_BRUSHTRANSPINFO'},
    TAG_BRUSHATTRTRANSPINFO: {'id': 'TAG_BRUSHATTRTRANSPINFO'},

    # Nudge size record
    TAG_DOCUMENTNUDGE: {
        'id': 'TAG_DOCUMENTNUDGE',
        'sec': [
            {'type': 'MILLIPOINT', 'id': 'size'}
        ]
    },

    # Bitmap properties record
    TAG_BITMAP_PROPERTIES: {'id': 'TAG_BITMAP_PROPERTIES'},

    # Bitmap smoothing record
    TAG_DOCUMENTBITMAPSMOOTHING: {'id': 'TAG_DOCUMENTBITMAPSMOOTHING'},

    # XPE bitmap processing record
    TAG_XPE_BITMAP_PROPERTIES: {'id': 'TAG_XPE_BITMAP_PROPERTIES'},

    # XPE Bitmap file format placeholder record
    TAG_DEFINEBITMAP_XPE: {'id': 'TAG_DEFINEBITMAP_XPE'},

    # Current attributes records
    TAG_CURRENTATTRIBUTES: {
        'id': 'TAG_CURRENTATTRIBUTES',
        'sec': [
            {'type': 'byte', 'id': 'group'}
        ]
    },
    TAG_CURRENTATTRIBUTEBOUNDS: {'id': 'TAG_CURRENTATTRIBUTEBOUNDS'},

    # 3-point linear fill records
    TAG_LINEARFILL3POINT: {'id': 'TAG_LINEARFILL3POINT'},
    TAG_LINEARFILLMULTISTAGE3POINT: {'id': 'TAG_LINEARFILLMULTISTAGE3POINT'},
    TAG_LINEARTRANSPARENTFILL3POINT: {'id': 'TAG_LINEARTRANSPARENTFILL3POINT'},

    # Duplication distance record
    TAG_DUPLICATIONOFFSET: {'id': 'TAG_DUPLICATIONOFFSET'},

    # Bitmap effect tags
    TAG_LIVE_EFFECT: {'id': 'TAG_LIVE_EFFECT'},
    TAG_LOCKED_EFFECT: {'id': 'TAG_LOCKED_EFFECT'},
    TAG_FEATHER_EFFECT: {'id': 'TAG_FEATHER_EFFECT'},

    # Miscellaneous records
    TAG_COMPOUNDRENDER: {'id': 'TAG_COMPOUNDRENDER'},
    TAG_OBJECTBOUNDS: {'id': 'TAG_OBJECTBOUNDS'},
    TAG_SPREAD_PHASE2: {'id': 'TAG_SPREAD_PHASE2'},
    TAG_CURRENTATTRIBUTES_PHASE2: {'id': 'TAG_CURRENTATTRIBUTES_PHASE2'},
    TAG_SPREAD_FLASHPROPS: {'id': 'TAG_SPREAD_FLASHPROPS'},
    TAG_PRINTERSETTINGS_PHASE2: {'id': 'TAG_PRINTERSETTINGS_PHASE2'},
    TAG_CLIPVIEW_PATH: {'id': 'TAG_CLIPVIEW_PATH'},
    TAG_DEFINEBITMAP_PNG_REAL: {
        'id': 'TAG_DEFINEBITMAP_PNG_REAL',
        'sec': [
            {'type': 'STRING', 'id': 'bitmap_name'},
            {'type': 'BITMAP_DATA', 'id': 'bitmap_data'},
        ]
    },
    TAG_TEXT_STRING_POS: {'id': 'TAG_TEXT_STRING_POS'},
    TAG_SPREAD_FLASHPROPS2: {'id': 'TAG_SPREAD_FLASHPROPS2'},
    TAG_TEXT_LINESPACE_LEADING: {'id': 'TAG_TEXT_LINESPACE_LEADING'},

    # New text records
    TAG_TEXT_TAB: {'id': 'TAG_TEXT_TAB'},
    TAG_TEXT_LEFT_INDENT: {'id': 'TAG_TEXT_LEFT_INDENT'},
    TAG_TEXT_FIRST_INDENT: {'id': 'TAG_TEXT_FIRST_INDENT'},
    TAG_TEXT_RIGHT_INDENT: {'id': 'TAG_TEXT_RIGHT_INDENT'},
    TAG_TEXT_RULER: {'id': 'TAG_TEXT_RULER'},
    TAG_TEXT_STORY_HEIGHT_INFO: {'id': 'TAG_TEXT_STORY_HEIGHT_INFO'},
    TAG_TEXT_STORY_LINK_INFO: {'id': 'TAG_TEXT_STORY_LINK_INFO'},
    TAG_TEXT_STORY_TRANSLATION_INFO: {'id': 'TAG_TEXT_STORY_TRANSLATION_INFO'},
    TAG_TEXT_SPACE_BEFORE: {'id': 'TAG_TEXT_SPACE_BEFORE'},
    TAG_TEXT_SPACE_AFTER: {'id': 'TAG_TEXT_SPACE_AFTER'},
    TAG_TEXT_SPECIAL_HYPHEN: {'id': 'TAG_TEXT_SPECIAL_HYPHEN'},
    TAG_TEXT_SOFT_RETURN: {'id': 'TAG_TEXT_SOFT_RETURN'},
    TAG_TEXT_EXTRA_FONT_INFO: {'id': 'TAG_TEXT_EXTRA_FONT_INFO'},
    TAG_TEXT_EXTRA_TT_FONT_DEF: {'id': 'TAG_TEXT_EXTRA_TT_FONT_DEF'},
    TAG_TEXT_EXTRA_ATM_FONT_DEF: {'id': 'TAG_TEXT_EXTRA_ATM_FONT_DEF'},

    # Tag that is not in specification
    TAG_SPREAD_PHOTO_PROPERTIES: {'id': 'SPREAD_PHOTO_PROPERTIES'},
    TAG_FLASH_PROPERTIES_4: {'id': 'FLASH_PROPERTIES_4'},
    TAG_PAGE_PROPERTIES_2: {'id': 'PAGE_PROPERTIES_2'},
    TAG_LIVE_SHARE_ATTRIBUTE: {'id': 'LIVE_SHARE_ATTRIBUTE'},
}
