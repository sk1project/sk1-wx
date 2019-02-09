# -*- coding: utf-8 -*-
#
#  Copyright (C) 2017 by Igor E. Novikov
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


CGM_SIGNATURE = '\x00'

CGM_ID = {
    0x0000: 'noop',
    0x0020: 'BEGMF',
    0x0040: 'ENDMF',
    0x0060: 'BEGPIC',
    0x0080: 'BEGPICBODY',
    0x00A0: 'ENDPIC',
    0x1020: 'mfversion',
    0x1040: 'mfdesc',
    0x1060: 'vdctype',
    0x1080: 'integerprec',
    0x10a0: 'realprec',
    0x10c0: 'indexprec',
    0x10e0: 'colrprec',
    0x1100: 'colrindexprec',
    0x1120: 'maxcolrindex',
    0x1140: 'colrvalueext',
    0x1160: 'mfelemlist',
    0x1180: 'mfdfltrpl',
    0x11a0: 'fontlist',
    0x11c0: 'charsetlist',
    0x11e0: 'charcoding',
    0x2020: 'scalemode',
    0x2040: 'colrmode',
    0x2060: 'linewidthmode',
    0x2080: 'markersizemode',
    0x20a0: 'edgewidthmode',
    0x20c0: 'vdcext',
    0x20e0: 'backcolr',
    0x3020: 'vdcintegerprec',
    0x3040: 'vdcrealprec',
    0x3060: 'auxcolr',
    0x3080: 'transparency',
    0x30a0: 'cliprect',
    0x30c0: 'clip',
    0x4020: 'LINE',
    0x4040: 'DISJTLINE',
    0x4060: 'MARKER',
    0x4080: 'TEXT',
    0x40a0: 'RESTRTEXT',
    0x40c0: 'APNDTEXT',
    0x40e0: 'POLYGON',
    0x4100: 'POLYGONSET',
    0x4120: 'CELLARRAY',
    0x4140: 'GDP',
    0x4160: 'RECT',
    0x4180: 'CIRCLE',
    0x41a0: 'ARC3PT',
    0x41c0: 'ARC3PTCLOSE',
    0x41e0: 'ARCCTR',
    0x4200: 'ARCCTRCLOSE',
    0x4220: 'ELLIPSE',
    0x4240: 'ELLIPARC',
    0x4260: 'ELLIPARCCLOSE',
    0x5040: 'linetype',
    0x5060: 'linewidth',
    0x5080: 'linecolr',
    0x50c0: 'markertype',
    0x5100: 'markercolr',
    0x5140: 'textfontindex',
    0x5160: 'textprec',
    0x5180: 'charexpan',
    0x51a0: 'charspace',
    0x51c0: 'textcolr',
    0x51e0: 'charheight',
    0x5200: 'charori',
    0x5220: 'textpath',
    0x5240: 'textalign',
    0x5260: 'charsetindex',
    0x52c0: 'intstyle',
    0x52e0: 'fillcolr',
    0x5300: 'hatchindex',
    0x5320: 'patindex',
    0x5360: 'edgetype',
    0x5380: 'edgewidth',
    0x53a0: 'edgecolr',
    0x53c0: 'edgevis',
    0x5440: 'colrtable',
    0x5460: 'asf',
    0x6020: 'ESCAPE',
}
