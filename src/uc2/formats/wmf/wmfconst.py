# -*- coding: utf-8 -*-
#
#	Copyright (C) 2013 by Igor E. Novikov
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

WMF_SIGNATURE = '\xd7\xcd\xc6\x9a'

struct_wmf_header = ('<'
						'H'	# Type
						'H'	# header size
						'H'	# Version
						'I'	# FileSize
						'H'	# Num. objects
						'I'	# Max. record size
						'H'	# Num. Parameters
						)

struct_placeable_header = ('<'
							'4s'	# Key
							'H'	# handle
							'h'	# left
							'h'	# top
							'h'	# right
							'h'	# bottom
							'H'	# Inch
							'I'	# Reserved
							'H'	# Checksum
							)

wmf_functions = {
	0x0052: 'AbortDoc',
	0x0817: 'Arc',
	0x0830: 'Chord',
	0x01f0: 'DeleteObject',
	0x0418: 'Ellipse',
	0x005E: 'EndDoc',
	0x0050: 'EndPage',
	0x0415: 'ExcludeClipRect',
	0x0548: 'ExtFloodFill',
	0x0228: 'FillRegion',
	0x0419: 'FloodFill',
	0x0429: 'FrameRegion',
	0x0416: 'IntersectClipRect',
	0x012A: 'InvertRegion',
	0x0213: 'LineTo',
	0x0214: 'MoveTo',
	0x0220: 'OffsetClipRgn',
	0x0211: 'OffsetViewportOrg',
	0x020F: 'OffsetWindowOrg',
	0x012B: 'PaintRegion',
	0x061D: 'PatBlt',
	0x081A: 'Pie',
	0x0035: 'RealizePalette',
	0x041B: 'Rectangle',
	0x014C: 'ResetDc',
	0x0139: 'ResizePalette',
	0x0127: 'RestoreDC',
	0x061C: 'RoundRect',
	0x001E: 'SaveDC',
	0x0412: 'ScaleViewportExt',
	0x0410: 'ScaleWindowExt',
	0x012C: 'SelectClipRegion',
	0x012D: 'SelectObject',
	0x0234: 'SelectPalette',
	0x012E: 'SetTextAlign',
	0x0201: 'SetBkColor',
	0x0102: 'SetBkMode',
	0x0d33: 'SetDibToDev',
	0x0103: 'SetMapMode',
	0x0231: 'SetMapperFlags',
	0x0037: 'SetPalEntries',
	0x041F: 'SetPixel',
	0x0106: 'SetPolyFillMode',
	0x0105: 'SetRelabs',
	0x0104: 'SetROP2',
	0x0107: 'SetStretchBltMode',
	0x012E: 'SetTextAlign',
	0x0108: 'SetTextCharExtra',
	0x0209: 'SetTextColor',
	0x020A: 'SetTextJustification',
	0x020E: 'SetViewportExt',
	0x020D: 'SetViewportOrg',
	0x020C: 'SetWindowExt',
	0x020B: 'SetWindowOrg',
	0x014D: 'StartDoc',
	0x004F: 'StartPage',
	#
	0x0436: 'AnimatePalette',
	0x0922: 'BitBlt',
	0x06FE: 'CreateBitmap',
	0x02FD: 'CreateBitmapIndirect',
	0x00F8: 'CreateBrush',
	0x02FC: 'CreateBrushIndirect',
	0x02FB: 'CreateFontIndirect',
	0x00F7: 'CreatePalette',
	0x01F9: 'CreatePatternBrush',
	0x02FA: 'CreatePenIndirect',
	0x06FF: 'CreateRegion',
	0x01F0: 'DeleteObject',
	0x0940: 'DibBitblt',
	0x0142: 'DibCreatePatternBrush',
	0x0B41: 'DibStretchBlt',
	0x062F: 'DrawText',
	0x0626: 'Escape',
	0x0A32: 'ExtTextOut',
	0x0324: 'Polygon',
	0x0538: 'PolyPolygon',
	0x0325: 'Polyline',
	0x0521: 'TextOut',
	0x0B23: 'StretchBlt',
	0x0F43: 'StretchDIBits'
}
