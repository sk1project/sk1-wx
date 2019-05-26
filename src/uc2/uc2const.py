# -*- coding: utf-8 -*-
#
#  Copyright (C) 2012 by Igor E. Novikov
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

from uc2 import _

"""
The package provides generic application constants
"""
# Version
VERSION = '2.0'
REVISION = 'rc5'
BUILD = ''

# Placement constants
BEFORE = 0
AFTER = 1
LOWER = 0
UPPER = 1
HORIZONTAL = 0
VERTICAL = 1

# MODEL TYPES
GENERIC_MODEL = 0
TAGGED_MODEL = 1
TEXT_MODEL = 2
BINARY_MODEL = 3

# Formats enumeration

ALL_FORMATS = 0

PDXF = 1
SK1 = 'sk1'
SK = 'sk'
SK2 = 'sk2'

SVG = 'svg'
SVGZ = 6
ODG = 7
ORA = 8
XCF = 'xcf'
SLA = 10
FIG = 'fig'

RIFF = 'riff'
CDR = 'cdr'
CDT = 'cdt'
CDRZ = 'cdrz'
CDTZ = 'cdtz'
CMX = 'cmx'
CCX = 'ccx'
CDRX = 56

XAR = 'xar'

AI_PS = 70
AI_PDF = 71
PS = 72
EPS = 73
PDF = 'pdf'
PSD = 'psd'

CGM = 'cgm'
WMF = 'wmf'
EMF = 102
XPS = 103
VSD = 104

PLT = 'plt'
HPGL = 111
DXF = 120
DWG = 121

JPG = 300
JP2 = 301
TIF = 305
BMP = 310
PCX = 311
GIF = 312
PNG = 'png'
PPM = 314
XBM = 315
XPM = 316
WEBP = 317

SKP = 'skp'
GPL = 'gpl'
CPL = 'cpl'
SCRIBUS_PAL = 'scribus_pal'
SOC = 'soc'
COREL_PAL = 'corel_pal'
ASE = 'ase'
ACO = 'aco'
JCW = 'jcw'

ICC = 600
ICM = 601

XML = 'xml_'
LOG = 'log'
MD = 'md'

FORMAT_DESCRIPTION = {
    ALL_FORMATS: _("All supported formats"),
    PDXF: _("PDXF - PrintDesign XML Format graphics files"),
    SK1: _("SK1 - sK1 0.9.x graphics files"),
    SK2: _("SK2 - sK1 2.x graphics files"),
    SK: _("SK - Sketch/Skencil files"),
    SVG: _("SVG - Scalable Vector Graphics files"),
    SVGZ: _("SVGZ - Compressed Scalable Vector Graphics files"),
    ODG: _("ODG - Open Document Drawing files"),
    ORA: _("ORA - Open Raster Format files"),
    XCF: _("XCF - GIMP files"),
    SLA: _("SLA - Scribus documents"),
    CDR: _("CDR - CorelDRAW Graphics files"),
    CDT: _("CDT - CorelDRAW Templates files"),
    CDRZ: _("CDR - CorelDRAW Graphics files"),
    CDTZ: _("CDT - CorelDRAW Templates files"),
    CMX: _("CMX - CorelDRAW Presentation Exchange files"),
    CCX: _("CCX - CorelDRAW Compressed Exchange files"),
    XAR: _("XAR - Xara graphics files"),
    FIG: _("FIG - XFig files"),
    AI_PS: _("AI - Adobe Illustrator files"),
    AI_PDF: _("AI - Adobe Illustrator files"),
    PS: _("PS - PostScript files"),
    EPS: _("EPS - Encapsulated PostScript files"),
    PDF: _("PDF - Portable Document Format files"),
    PSD: _("PSD - Adobe Photoshop files"),
    CGM: _("CGM - Computer Graphics Metafile files"),
    WMF: _("WMF - Windows Metafile files"),
    EMF: _("EMF - Windows Enhanced Metafile files"),
    XPS: _("XPS - XML Paper Specification files"),
    VSD: _("VSD - Visio Drawing files"),
    PLT: _("PLT - HPGL cutting plotter files"),
    HPGL: _("HPGL - HPGL plotter files"),
    DXF: _("DXF - AutoCAD files"),
    DWG: _("DWG - AutoCAD files"),
    RIFF: _("RIF - RIFF files"),

    # Bitmap file formats
    JPG: _("JPEG - Joint Photographic Experts Group files"),
    JP2: _("JPEG2000 - Joint Photographic Experts Group files"),
    TIF: _("TIFF - Tagged Image File Format files"),
    BMP: _("BMP - Bitmap Picture files"),
    PCX: _("PCX - PCeXchange files"),
    GIF: _("GIF - Graphics Interchange Format files"),
    PNG: _("PNG - Portable Network Graphics files"),
    PPM: _("PPM - Netpbm Color Image format files"),
    XBM: _("XBM - X bitmap files"),
    XPM: _("XPM - X pixmap files"),
    WEBP: _("WebP - Google image format files"),

    # Palette file formats
    SKP: _("SKP - sK1 palette files"),
    GPL: _("GPL - GIMP palette files"),
    CPL: _("CPL - CorelDRAW palette files"),
    SCRIBUS_PAL: _("XML - Scribus palette files"),
    SOC: _("SOC - LibreOffice palette files"),
    COREL_PAL: _("XML - CorelDRAW X5-X7 palette files"),
    ASE: _("ASE - Adobe Swatch Exchange files"),
    ACO: _("ACO - Adobe Color files"),
    JCW: _("JCW - Xara color palette files"),

    # Color profiles
    ICC: _("ICC - International Color Consortium profiles"),
    ICM: _("ICM - Image Color Matching profiles"),

    XML: _("XML - eXtensible Markup Language files"),
    LOG: _("LOG - Log files"),
    MD: _("MD - Markdown markup files"),
}

FORMAT_NAMES = {
    ALL_FORMATS: "",
    PDXF: "PDXF",
    SK1: "SK1",
    SK2: "SK2",
    SK: "SK",
    SVG: "SVG",
    SVGZ: "SVGZ",
    ODG: "ODG",
    ORA: "ORA",
    XCF: "XCF",
    SLA: "SLA",
    CDR: "CDR",
    CDT: "CDT",
    CDRZ: "CDR",
    CDTZ: "CDT",
    CMX: "CMX",
    CCX: "CCX",
    XAR: "XAR",
    FIG: "FIG",
    AI_PS: "AI",
    AI_PDF: "AI",
    PS: "PS",
    EPS: "EPS",
    PDF: "PDF",
    PSD: "PSD",
    CGM: "CGM",
    WMF: "WMF",
    EMF: "EMF",
    XPS: "XPS",
    VSD: "VSD",
    PLT: "PLT",
    HPGL: "HPGL",
    DXF: "DXF",
    DWG: "DWG",
    RIFF: "RIFF",

    # Bitmap file formats
    JPG: "JPEG",
    JP2: "JP2",
    TIF: "TIFF",
    BMP: "BMP",
    PCX: "PCX",
    GIF: "GIF",
    PNG: "PNG",
    PPM: "PPM",
    XBM: "XBM",
    XPM: "XPM",
    WEBP: "WEBP",

    # Palette file formats
    SKP: "SKP",
    GPL: "GPL",
    CPL: "CPL",
    SCRIBUS_PAL: "SCRIBUS_PAL",
    SOC: "SOC",
    COREL_PAL: "COREL_PAL",
    ASE: "ASE",
    ACO: "ACO",
    JCW: "JCW",

    # Color profiles
    ICC: "ICC",
    ICM: "ICM",

    XML: "XML",
    LOG: "LOG",
    MD: "MD",
}

MODEL_LOADERS = [SK2, SVG, CDR, CMX, CCX, XAR, WMF, PLT, SK1, SK, FIG, CGM]  # CDT,
BITMAP_LOADERS = [PNG, JPG, PSD, XCF, JP2, TIF, GIF, BMP, PCX, PPM, XBM, XPM,
                  WEBP]
PALETTE_LOADERS = [SKP, GPL, SCRIBUS_PAL, SOC, CPL, COREL_PAL, ASE, ACO, JCW]
EXPERIMENTAL_LOADERS = [MD, RIFF, XML, ]

MODEL_SAVERS = [SK2, SVG, PLT, PDF, CDR, CMX, CCX, SK1, SK, CGM, FIG]
BITMAP_SAVERS = [PNG, ]
PALETTE_SAVERS = [SKP, GPL, SCRIBUS_PAL, SOC, CPL, COREL_PAL, ASE, ACO, JCW]
EXPERIMENTAL_SAVERS = [MD, RIFF, XML, WMF, ]

PATTERN_FORMATS = [EPS, PNG, JPG, JP2, TIF, GIF, BMP, PCX, PPM, XBM, XPM]

LOADER_FORMATS = MODEL_LOADERS + BITMAP_LOADERS + PALETTE_LOADERS
SAVER_FORMATS = MODEL_SAVERS + BITMAP_SAVERS + PALETTE_SAVERS

FORMAT_EXTENSION = {
    ALL_FORMATS: '',
    PDXF: ('pdxf',), SK1: ('sk1',), SK2: ('sk2',), SK: ('sk',),
    SVG: ('svg',), SVGZ: ('svgz',), ODG: ('odg',), ORA: ('ora',),
    XCF: ('xcf',), SLA: ('sla',), FIG: ('fig',),
    CDR: ('cdr',), CDT: ('cdt',), CDRZ: ('cdr',), CDTZ: ('cdt',),
    CMX: ('cmx',), CCX: ('ccx', 'cdr',),
    XAR: ('xar',),
    AI_PS: ('ai',), AI_PDF: ('ai',), PS: ('ps',), EPS: ('eps',), PDF: ('pdf',),
    PSD: ('psd',),
    CGM: ('cgm',), WMF: ('wmf',), EMF: ('emf',), XPS: ('xps',), VSD: ('vsd',),
    PLT: ('plt',), HPGL: ('hgl',), DXF: ('dxf',), DWG: ('dwg',),
    RIFF: ('riff',),

    JPG: ('jpg', 'jpeg', 'jpe', 'jfif'), TIF: ('tif', 'tiff'),
    BMP: ('bmp', 'dib'),
    PCX: ('pcx',), GIF: ('gif',), PNG: ('png',), PPM: ('pbm', 'pgm', 'pgm'),
    XBM: ('xbm',), XPM: ('xpm',), JP2: ('jp2', 'jpx', 'jpf'), WEBP: ('webp',),

    SKP: ('skp',), GPL: ('gpl',), CPL: ('cpl',), SCRIBUS_PAL: ('xml',),
    SOC: ('soc',),
    COREL_PAL: ('xml',), ASE: ('ase',), ACO: ('aco',), JCW: ('jcw',),

    ICC: ('icc',), ICM: ('icm',),

    XML: ('xml', 'svg', 'sla',),
    LOG: ('log',),
    MD: ('md',),
}

IMAGE_FORMATS = [JPG, TIF, BMP, PCX, GIF, PNG, PPM, XBM, XPM, WEBP, ]

MIMES = {
    'pdxf': 'application/vnd.sk1project.pdxf-graphics',
    'tif': 'image/tiff',
    'tiff': 'image/tiff',
    'png': 'image/png',
    'eps': 'image/eps',
    'icc': 'application/vnd.iccprofile',
    'icm': 'application/vnd.iccprofile',
    'xml': 'text/xml',
    'txt': 'text/plain',
}

# UNITS

SYSTEM_DPI = 72.0

UNIT_PX = 'px'
UNIT_MM = 'mm'
UNIT_CM = 'cm'
UNIT_M = 'm'
UNIT_PT = 'pt'
UNIT_IN = 'in'
UNIT_FT = 'ft'

in_to_pt = 72.0
ft_to_pt = in_to_pt * 12.0
px_to_pt = in_to_pt / SYSTEM_DPI
cm_to_pt = in_to_pt / 2.54
mm_to_pt = cm_to_pt / 10.0
m_to_pt = 100.0 * cm_to_pt

pt_to_in = 1.0 / 72.0
pt_to_ft = pt_to_in / 12.0
pt_to_px = pt_to_in * SYSTEM_DPI
pt_to_cm = 2.54 * pt_to_in
pt_to_mm = pt_to_cm * 10.0
pt_to_m = pt_to_cm / 100.0

unit_dict = {UNIT_PT: 1.0,
             UNIT_IN: in_to_pt,
             UNIT_FT: ft_to_pt,
             UNIT_PX: px_to_pt,
             UNIT_M: m_to_pt,
             UNIT_CM: cm_to_pt,
             UNIT_MM: mm_to_pt}

point_dict = {UNIT_PT: 1.0,
              UNIT_IN: pt_to_in,
              UNIT_FT: pt_to_ft,
              UNIT_PX: pt_to_px,
              UNIT_M: pt_to_m,
              UNIT_CM: pt_to_cm,
              UNIT_MM: pt_to_mm}

unit_accuracy = {UNIT_PT: 2,
                 UNIT_IN: 3,
                 UNIT_FT: 4,
                 UNIT_PX: 2,
                 UNIT_M: 4,
                 UNIT_CM: 3,
                 UNIT_MM: 2}

unit_names = [UNIT_PX, UNIT_MM, UNIT_CM, UNIT_M, UNIT_PT, UNIT_IN, UNIT_FT, ]

unit_full_names = {
    UNIT_PX: _('pixels'),
    UNIT_MM: _('millimeters'),
    UNIT_CM: _('centimeters'),
    UNIT_M: _('meters'),
    UNIT_PT: _('points'),
    UNIT_IN: _('inches'),
    UNIT_FT: _('feet'),
}

unit_short_names = {
    UNIT_PT: _('pt'),
    UNIT_PX: _('px'),
    UNIT_IN: _('in'),
    UNIT_FT: _('ft'),
    UNIT_M: _('m'),
    UNIT_CM: _('cm'),
    UNIT_MM: _('mm')
}

unit_by_name = {
    _('pixels'): UNIT_PX,
    _('points'): UNIT_PT,
    _('inches'): UNIT_IN,
    _('feet'): UNIT_FT,
    _('meters'): UNIT_M,
    _('centimeters'): UNIT_CM,
    _('millimeters'): UNIT_MM
}

PAGE_FORMATS = {
    'A0': (841.0 * mm_to_pt, 1189.0 * mm_to_pt),
    'A1': (594.0 * mm_to_pt, 841.0 * mm_to_pt),
    'A2': (420.0 * mm_to_pt, 594.0 * mm_to_pt),
    'A3': (297.0 * mm_to_pt, 420.0 * mm_to_pt),
    'A4': (210.0 * mm_to_pt, 297.0 * mm_to_pt),
    'A5': (148.0 * mm_to_pt, 210.0 * mm_to_pt),
    'A6': (105.0 * mm_to_pt, 148.0 * mm_to_pt),
    'A7': (74.0 * mm_to_pt, 105.0 * mm_to_pt),
    'B0': (1000.0 * mm_to_pt, 1414.0 * mm_to_pt),
    'B1': (707.0 * mm_to_pt, 1000.0 * mm_to_pt),
    'B2': (500.0 * mm_to_pt, 707.0 * mm_to_pt),
    'B3': (353.0 * mm_to_pt, 500.0 * mm_to_pt),
    'B4': (250.0 * mm_to_pt, 353.0 * mm_to_pt),
    'B5': (176.0 * mm_to_pt, 250.0 * mm_to_pt),
    'B6': (125.0 * mm_to_pt, 176.0 * mm_to_pt),
    'C0': (917.0 * mm_to_pt, 1297.0 * mm_to_pt),
    'C1': (648.0 * mm_to_pt, 917.0 * mm_to_pt),
    'C2': (458.0 * mm_to_pt, 648.0 * mm_to_pt),
    'C3': (324.0 * mm_to_pt, 458.0 * mm_to_pt),
    'C4': (229.0 * mm_to_pt, 324.0 * mm_to_pt),
    'C5': (162.0 * mm_to_pt, 229.0 * mm_to_pt),
    'C6': (114.0 * mm_to_pt, 162.0 * mm_to_pt),
    'Letter': (8.5 * in_to_pt, 11.0 * in_to_pt),
    'Legal': (8.5 * in_to_pt, 14.0 * in_to_pt),
    'Ledger': (11.0 * in_to_pt, 17.0 * in_to_pt),
    'Executive': (7.5 * in_to_pt, 10.0 * in_to_pt),
    'JIS B0': (1030.0 * mm_to_pt, 1456.0 * mm_to_pt),
    'JIS B1': (728.0 * mm_to_pt, 1030.0 * mm_to_pt),
    'JIS B2': (515.0 * mm_to_pt, 728.0 * mm_to_pt),
    'JIS B3': (364.0 * mm_to_pt, 515.0 * mm_to_pt),
    'JIS B4': (257.0 * mm_to_pt, 364.0 * mm_to_pt),
    'JIS B5': (182.0 * mm_to_pt, 257.0 * mm_to_pt),
    'JIS B6': (128.0 * mm_to_pt, 182.0 * mm_to_pt),
    'Envelope C4': (229.0 * mm_to_pt, 324.0 * mm_to_pt),
    'Envelope C5': (162.0 * mm_to_pt, 229.0 * mm_to_pt),
    'Envelope C6': (114.0 * mm_to_pt, 162.0 * mm_to_pt),
    'Envelope E65/DL': (110.0 * mm_to_pt, 220.0 * mm_to_pt),
    'Business card #1': (50.0 * mm_to_pt, 90.0 * mm_to_pt),
    'Business card #2': (55.0 * mm_to_pt, 85.0 * mm_to_pt),
}

PAGE_FORMAT_NAMES = [
    'A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7',
    'Letter', 'Legal', 'Executive', 'Ledger',
    'B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6',
    'C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6',
    'JIS B0', 'JIS B1', 'JIS B2', 'JIS B3', 'JIS B4', 'JIS B5', 'JIS B6',
    'Envelope C4', 'Envelope C5', 'Envelope C6', 'Envelope E65/DL',
    'Business card #1', 'Business card #2',
]

PORTRAIT = 0
LANDSCAPE = 1

ORIENTS_NAMES = (_('Portrait'), _('Landscape'))

# Color management constants

INTENT_PERCEPTUAL = 0
INTENT_RELATIVE_COLORIMETRIC = 1
INTENT_SATURATION = 2
INTENT_ABSOLUTE_COLORIMETRIC = 3

INTENTS = {
    INTENT_PERCEPTUAL: _('Perceptual'),
    INTENT_RELATIVE_COLORIMETRIC: _('Relative Colorimetric'),
    INTENT_SATURATION: _('Saturation'),
    INTENT_ABSOLUTE_COLORIMETRIC: _('Absolute Colorimetric'),
}

COLOR_GRAY = 'Grayscale'
COLOR_RGB = 'RGB'
COLOR_CMYK = 'CMYK'
COLOR_LAB = 'LAB'
COLOR_SPOT = 'SPOT'

IMAGE_MONO = '1'
IMAGE_GRAY = 'L'
IMAGE_GRAY_A = 'LA'
IMAGE_RGB = 'RGB'
IMAGE_RGBA = 'RGBA'
IMAGE_CMYK = 'CMYK'
IMAGE_LAB = 'LAB'

IMAGE_NAMES = {
    IMAGE_MONO: 'Bilevel',
    IMAGE_GRAY: 'Grayscale',
    IMAGE_RGB: 'RGB',
    IMAGE_RGBA: 'RGBA',
    IMAGE_CMYK: 'CMYK',
    IMAGE_LAB: 'LAB',
}

IMAGE_TO_COLOR = {
    IMAGE_MONO: None,
    IMAGE_GRAY: COLOR_GRAY,
    IMAGE_RGB: COLOR_RGB,
    IMAGE_RGBA: COLOR_RGB,
    IMAGE_CMYK: COLOR_CMYK,
    IMAGE_LAB: COLOR_LAB,
}

COLOR_DISPLAY = 'Display'
COLOR_REG = 'Registration Black'

COLORSPACES = [COLOR_RGB, COLOR_CMYK, COLOR_LAB, COLOR_GRAY]
IMAGE_COLORSPACES = [IMAGE_GRAY, IMAGE_RGB, IMAGE_CMYK, IMAGE_LAB]
DUOTONES = [IMAGE_GRAY, IMAGE_MONO]
SUPPORTED_CS = [IMAGE_MONO, IMAGE_GRAY, IMAGE_RGB, IMAGE_CMYK, IMAGE_LAB]

TYPE_RGB_8 = "RGB"
TYPE_RGBA_8 = "RGBA"
TYPE_CMYK_8 = "CMYK"
TYPE_GRAY_8 = "L"
TYPE_YCbCr_8 = "YCCA"

cmsFLAGS_NOTPRECALC = 0x0100
cmsFLAGS_GAMUTCHECK = 0x1000
cmsFLAGS_SOFTPROOFING = 0x4000
cmsFLAGS_BLACKPOINTCOMPENSATION = 0x2000
cmsFLAGS_PRESERVEBLACK = 0x8000
cmsFLAGS_NULLTRANSFORM = 0x0200
cmsFLAGS_HIGHRESPRECALC = 0x0400
cmsFLAGS_LOWRESPRECALC = 0x0800
