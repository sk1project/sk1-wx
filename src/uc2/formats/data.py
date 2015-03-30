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

from uc2.uc2const import PDXF, SK1, SK2, SK, SVG, SVGZ, ODG, ORA, \
XCF, SLA, FIG, CDR, CDT, CDRZ, CDTZ, CMX, CCX, CDRX, XAR, AI_PS, AI_PDF, PS, \
EPS, PDF, PSD, CGM, WMF, EMF, XPS, VSD, PLT, HPGL , DXF, DWG, RIFF

from uc2.uc2const import JPG, JP2, TIF, BMP, PCX, GIF, PNG, PPM, XBM, XPM

from uc2.uc2const import SKP


SIMPLE_LOADERS = []
MODEL_LOADERS = [SK2, PDXF, PLT, CDR, CDT] + \
[PNG, JPG, JP2, TIF, GIF, BMP, PCX, PPM, XBM, XPM]
EXPERIMENTAL_LOADERS = [SK1, WMF, RIFF, CDRZ]
PALETTE_LOADERS = [SKP, ]

SIMPLE_SAVERS = []
MODEL_SAVERS = [SK2, PNG, PDXF, PLT]
EXPERIMENTAL_SAVERS = [SK1, RIFF, CDR]
PALETTE_SAVERS = [SKP, ]


LOADER_FORMATS = SIMPLE_LOADERS + MODEL_LOADERS

SAVER_FORMATS = SIMPLE_SAVERS + MODEL_SAVERS

from uc2.formats.sk2 import sk2_loader, sk2_saver, check_sk2
from uc2.formats.pdxf import pdxf_loader, pdxf_saver, check_pdxf
from uc2.formats.plt import plt_loader, plt_saver, check_plt
from uc2.formats.sk1 import sk1_loader, sk1_saver, check_sk1
from uc2.formats.sk import SK_Loader, SK_Saver
from uc2.formats.wmf import wmf_loader, wmf_saver, check_wmf

from uc2.formats.cdr import cdr_loader, cdr_saver, check_cdr
from uc2.formats.cdrz import cdrz_loader, check_cdrz
from uc2.formats.riff import riff_loader, riff_saver, check_riff

from uc2.formats.png import png_loader, check_png, png_saver
from uc2.formats.fallback import im_loader, fallback_check

from uc2.formats.skp import skp_loader, skp_saver, check_skp


LOADERS = {
SK2 : sk2_loader, PDXF : pdxf_loader, SK1 : sk1_loader, SK : SK_Loader,
SVG : None, SVGZ : None, ORA : None, XCF : None, SLA : None, FIG : None,
CDR : cdr_loader, CDT : cdr_loader, CDRZ : cdrz_loader, CDTZ : cdrz_loader, CMX : None, CCX : None, CDRX : None,
XAR : None,
AI_PS : None, AI_PDF : None, PS : None, EPS : None, PDF : None, PSD : None,
CGM : None, WMF : wmf_loader, EMF : None, XPS : None, VSD : None,
PLT : plt_loader, HPGL : None, DXF : None, DWG : None,
RIFF: riff_loader,

PNG: png_loader, JPG: im_loader, JP2: im_loader, TIF: im_loader, GIF: im_loader,
BMP: im_loader, PCX: im_loader, PPM: im_loader, XBM: im_loader, XPM: im_loader,

SKP: skp_loader,
}

SAVERS = {
SK2 : sk2_saver, PDXF : pdxf_saver, SK1 : sk1_saver, SK : SK_Saver,
SVG : None, SVGZ : None, ORA : None, XCF : None, SLA : None, FIG : None,
CDR : cdr_saver, CDT : None, CDRZ : None, CDTZ : None, CMX : None, CCX : None, CDRX : None,
XAR : None,
AI_PS : None, AI_PDF : None, PS : None, EPS : None, PDF : None, PSD : None,
CGM : None, WMF : wmf_saver, EMF : None, XPS : None, VSD : None,
PLT : plt_saver, HPGL : None, DXF : None, DWG : None,
RIFF: riff_saver,

PNG: png_saver,

SKP: skp_saver,
}

CHECKERS = {
SK2 : check_sk2, PDXF : check_pdxf, SK1 : check_sk1, SK : None,
SVG : None, SVGZ : None, ORA : None, XCF : None, SLA : None, FIG : None,
CDR : check_cdr, CDT : check_cdr, CDRZ : check_cdrz, CDTZ : check_cdrz, CMX : None, CCX : None, CDRX : None,
XAR : None,
AI_PS : None, AI_PDF : None, PS : None, EPS : None, PDF : None, PSD : None,
CGM : None, WMF : check_wmf, EMF : None, XPS : None, VSD : None,
PLT : check_plt, HPGL : None, DXF : None, DWG : None,
RIFF: check_riff,
PNG: check_png, JPG: fallback_check, JP2: fallback_check, TIF: fallback_check,
GIF: fallback_check, BMP: fallback_check, PCX: fallback_check,
PPM: fallback_check, XBM: fallback_check, XPM: fallback_check,

SKP: check_skp,
}

