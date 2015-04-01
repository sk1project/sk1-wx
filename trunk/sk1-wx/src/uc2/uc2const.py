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

from uc2 import _

"""
The package provides generic application constants
"""
#Placement constants
BEFORE = 0
AFTER = 1
LOWER = 0
UPPER = 1
HORIZONTAL = 0
VERTICAL = 1

#MODEL TYPES
GENERIC_MODEL = 0
TAGGED_MODEL = 1
TEXT_MODEL = 2
BINARY_MODEL = 3

#Formats enumeration

ALL_FORMATS = 0

PDXF = 1
SK1 = 2
SK = 3
SK2 = 4

SVG = 5
SVGZ = 6
ODG = 7
ORA = 8
XCF = 9
SLA = 10
FIG = 11

RIFF = 49
CDR = 50
CDT = 51
CDRZ = 52
CDTZ = 53
CMX = 54
CCX = 55
CDRX = 56

XAR = 66

AI_PS = 70
AI_PDF = 71
PS = 72
EPS = 73
PDF = 74
PSD = 75

CGM = 100
WMF = 101
EMF = 102
XPS = 103
VSD = 104

PLT = 110
HPGL = 111
DXF = 120
DWG = 121

JPG = 300
JP2 = 301
TIF = 305
BMP = 310
PCX = 311
GIF = 312
PNG = 313
PPM = 314
XBM = 315
XPM = 316

SKP = 500
GPL = 501
CPL = 502
SCRIBUS_PAL = 503


FORMAT_DESCRIPTION = {
ALL_FORMATS : _("All supported formats"),
PDXF : _("PDXF - PrintDesign XML Format graphics"),
SK1 : _("SK1 - sK1 0.9.x graphics files"),
SK2 : _("SK2 - sK1 2.x graphics files"),
SK : _("SK - Sketch/Skencil files"),
SVG : _("SVG - Scalable Vector Graphics files"),
SVGZ : _("SVGZ - Compressed Scalable Vector Graphics files"),
ODG : _("ODG - Open Document Drawing files"),
ORA : _("ORA - Open Raster Format files"),
XCF : _("XCF - GIMP files"),
SLA : _("SLA - Scribus documents"),
CDR : _("CDR - CorelDRAW Graphics files /6-X3 ver./"),
CDT : _("CDT - CorelDRAW Templates files /6-X3 ver./"),
CDRZ : _("CDR - CorelDRAW Graphics files /X4-X6 ver./"),
CDTZ : _("CDT - CorelDRAW Templates files /X4-X6 ver./"),
CMX : _("CMX - CorelDRAW Presentation Exchange files"),
CCX : _("CCX - CorelDRAW Compressed Exchange files /CDRX format/"),
CDRX : _("CDR - CorelDRAW Compressed Exchange files /CDRX format/"),
XAR : _("XAR - Xara graphics files"),
FIG : _("FIG - XFig files"),
AI_PS : _("AI - Adobe Illustrator files /PostScript/"),
AI_PDF : _("AI - Adobe Illustrator files /PDF/"),
PS : _("PS - PostScript files"),
EPS : _("EPS - Encapsulated PostScript files"),
PDF : _("PDF - Portable Document Format"),
PSD : _("PSD - Adobe Photoshop files"),
CGM : _("CGM - Computer Graphics Metafile files"),
WMF : _("WMF - Windows Metafile files"),
EMF : _("EMF - Windows Enhanced Metafile files"),
XPS : _("XPS - XML Paper Specification"),
VSD : _("VSD - Visio Drawing"),
PLT : _("PLT - HPGL cutting plotter files"),
HPGL : _("HPGL plotter files"),
DXF : _("DXF - AutoCAD DXF files"),
DWG : _("DWG - AutoCAD DWG files"),
RIFF: _("RIFF files"),

#Bitmap file formats
JPG: _("JPEG - Joint Photographic Experts Group files"),
JP2: _("JPEG2000 - Joint Photographic Experts Group files"),
TIF: _("TIFF - Tagged Image File Format files"),
BMP: _("BMP -  Bitmap Picture files"),
PCX: _("PCX - PCExchange files"),
GIF: _("GIF - Graphics Interchange Format files"),
PNG: _("PNG - Portable Network Graphics files"),
PPM: _("PPM - Netpbm Color Image format  files"),
XBM: _("XBM - X bitmap files"),
XPM: _("XPM - X pixmap files"),

#Palette file formats
SKP: _("SKP - sK1 palette files"),
GPL: _("GPL - GIMP palette files"),
CPL: _("CPL - CorelDRAW palette files"),
SCRIBUS_PAL: _("XML - Scribus palette files")
}

FORMAT_NAMES = {
ALL_FORMATS : "",
PDXF : "PDXF",
SK1 : "SK1",
SK2 : "SK2",
SK : "SK",
SVG : "SVG",
SVGZ : "SVGZ",
ODG : "ODG",
ORA : "ORA",
XCF : "XCF",
SLA : "SLA",
CDR : "CDR",
CDT : "CDT",
CDRZ : "CDR",
CDTZ : "CDT",
CMX : "CMX",
CCX : "CCX",
CDRX : "CDR",
XAR : "XAR",
FIG : "FIG",
AI_PS : "AI",
AI_PDF : "AI",
PS : "PS",
EPS : "EPS",
PDF : "PDF",
PSD : "PSD",
CGM : "CGM",
WMF : "WMF",
EMF : "EMF",
XPS : "XPS",
VSD : "VSD",
PLT : "PLT",
HPGL : "HPGL",
DXF : "DXF",
DWG : "DWG",
RIFF: "RIFF",

#Bitmap file formats
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

#Palette file formats
SKP: "SKP",
GPL: "GPL",
CPL: "CPL",
SCRIBUS_PAL: "SCRIBUS_PAL",
}

FORMAT_EXTENSION = {
ALL_FORMATS : '',
PDXF : ('pdxf',), SK1 : ('sk1',), SK2 : ('sk2',), SK : ('sk',),
SVG : ('svg',), SVGZ : ('svgz',), ODG : ('odg',), ORA : ('ora',),
XCF : ('xcf',), SLA : ('sla',), FIG : ('fig',),
CDR : ('cdr',), CDT : ('cdt',), CDRZ : ('cdr',), CDTZ : ('cdt',), CMX : ('cmx',),
CCX : ('ccx',), CDRX : ('cdr',),
XAR : ('xar',),
AI_PS : ('ai',), AI_PDF : ('ai',), PS : ('ps',), EPS : ('eps',), PDF : ('pdf',), PSD : ('psd',),
CGM : ('cgm',), WMF : ('wmf',), EMF : ('emf',), XPS : ('xps',), VSD : ('vsd',),
PLT : ('plt',), HPGL : ('hgl',), DXF : ('dxf',), DWG : ('dwg',),
RIFF: ('riff',),

JPG: ('jpg', 'jpeg', 'jpe', 'jfif'), TIF: ('tif', 'tiff'), BMP: ('bmp', 'dib'),
PCX: ('pcx',), GIF: ('gif',), PNG: ('png',), PPM: ('pbm', 'pgm', 'pgm'),
XBM: ('xbm',), XPM: ('xpm',), JP2: ('jp2', 'jpx', 'jpf'),

SKP: ('skp',), GPL: ('gpl',), CPL: ('cpl',), SCRIBUS_PAL:('xml',),
}

IMAGE_FORMATS = [JPG, TIF, BMP, PCX, GIF, PNG, PPM, XBM, XPM, ]

MIMES = {
	'pdxf':'application/vnd.sk1project.pdxf-graphics',
	'tif':'image/tiff',
	'tiff':'image/tiff',
	'png':'image/png',
	'eps':'image/eps',
	'icc':'application/vnd.iccprofile',
	'icm':'application/vnd.iccprofile',
	'xml':'text/xml',
	'txt':'text/plain',
}

#UNITS

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
m_to_pt	 = 100.0 * cm_to_pt

pt_to_in = 1.0 / 72.0
pt_to_ft = pt_to_in / 12.0
pt_to_px = pt_to_in * SYSTEM_DPI
pt_to_cm = 2.54 * pt_to_in
pt_to_mm = pt_to_cm * 10.0
pt_to_m	 = pt_to_cm / 100.0

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

unit_accuracy = {UNIT_PT: 1,
			UNIT_IN: 3,
			UNIT_FT: 4,
			UNIT_PX: 1,
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
UNIT_FT: _('foots'),
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
_('pixels'):UNIT_PX,
_('points'):UNIT_PT,
_('inches'): UNIT_IN,
_('foots'): UNIT_FT,
_('meters'): UNIT_M,
_('centimeters'): UNIT_CM,
_('millimeters'): UNIT_MM
}

PAGE_FORMATS = {
			'A0': (2383.9370078740158, 3370.3937007874015),
			'A1': (1683.7795275590549, 2383.9370078740158),
			'A2': (1190.5511811023621, 1683.7795275590549),
			'A3': (841.88976377952747, 1190.5511811023621),
			'A4': (595.27559055118104, 841.88976377952747),
			'A5': (419.52755905511805, 595.27559055118104),
			'A6': (297.63779527559052, 419.52755905511805),
			'B1 (ISO)': (2004.0944881889761, 2834.6456692913384),
			'B4 (ISO)': (708.66141732283461, 1000.6299212598424),
			'B5 (ISO)': (498.89763779527556, 708.66141732283461),
			'C3': (918.42519685039372, 1298.267716535433),
			'C4': (649.1338582677165, 918.42519685039372),
			'C5': (459.21259842519686, 649.1338582677165),
			'C6': (323.14960629921262, 459.21259842519686),
			'Envelope C4': (649.1338582677165, 918.42519685039372),
			'Envelope C5': (459.21259842519686, 649.1338582677165),
			'Envelope C6': (323.14960629921262, 459.21259842519686),
			'Envelope E65/DL': (311.81102362204723, 623.62204724409446),
			'Executive': (522.0, 756.0),
			'Legal': (612.0, 1008.0),
			'Letter': (612.0, 792.0),
			'Half Letter': (396.0, 612.0),
			'Visit card #1': (141.73228346456693, 255.11811023622045),
			'Visit card #2': (155.90551181102362, 240.94488188976379),
			}

PAGE_FORMAT_NAMES = [
'A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6',
'B1 (ISO)', 'B4 (ISO)', 'B5 (ISO)',
'C3', 'C4', 'C5', 'C6',
'Envelope C4', 'Envelope C5', 'Envelope C6', 'Envelope E65/DL',
'Executive', 'Legal', 'Letter', 'Half Letter',
'Visit card #1', 'Visit card #2',
]

PORTRAIT = 0
LANDSCAPE = 1

#Color management constants

INTENT_PERCEPTUAL = 0
INTENT_RELATIVE_COLORIMETRIC = 1
INTENT_SATURATION = 2
INTENT_ABSOLUTE_COLORIMETRIC = 3

INTENTS = {
INTENT_PERCEPTUAL:_('Perceptual'),
INTENT_RELATIVE_COLORIMETRIC:_('Relative Colorimetric'),
INTENT_SATURATION:_('Saturation'),
INTENT_ABSOLUTE_COLORIMETRIC:_('Absolute Colorimetric'),
}

COLOR_GRAY = 'Grayscale'
COLOR_RGB = 'RGB'
COLOR_CMYK = 'CMYK'
COLOR_LAB = 'LAB'
COLOR_SPOT = 'SPOT'

IMAGE_MONO = '1'
IMAGE_GRAY = 'L'
IMAGE_RGB = 'RGB'
IMAGE_RGBA = 'RGBA'
IMAGE_CMYK = 'CMYK'
IMAGE_LAB = 'LAB'

IMAGE_NAMES = {
IMAGE_MONO: _('Black and White'),
IMAGE_GRAY: _('Grayscale'),
IMAGE_RGB: _('RGB'),
IMAGE_RGBA: _('RGBA'),
IMAGE_CMYK: _('CMYK'),
IMAGE_LAB: _('LAB'),
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

COLORSPACES = [COLOR_RGB, COLOR_CMYK, COLOR_LAB, COLOR_GRAY]
IMAGE_COLORSPACES = [IMAGE_GRAY, IMAGE_RGB, IMAGE_CMYK, IMAGE_LAB]

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


