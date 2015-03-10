# -*- coding: utf-8 -*-
#
#	Copyright (C) 2015 by Igor E. Novikov
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

import math

from uc2.utils.config import XmlConfigParser
from uc2.formats.sk2 import sk2_const
from uc2 import uc2const

class SK2_Config(XmlConfigParser):

	system_encoding = 'utf-8'

	#============== DOCUMENT SECTION ==================
	doc_origin = sk2_const.DOC_ORIGIN_LL
	doc_units = uc2const.UNIT_MM

	page_format = 'A4'
	page_orientation = uc2const.PORTRAIT

	layer_color = '#3252A2'
	layer_propeties = [1, 1, 1]
	master_layer_color = '#000000'

	guide_layer_color = '#0051FF'
	guide_layer_propeties = [1, 1, 0]

	grid_layer_color = [0.0, 0.0, 1.0, 0.15]
	grid_layer_geometry = [0, 0, uc2const.mm_to_pt, uc2const.mm_to_pt]
	grid_layer_propeties = [0, 0, 0]

	default_polygon_num = 5
	default_text = "TEXT text"

	default_fill = []
	default_fill_rule = sk2_const.FILL_EVENODD


	default_stroke_rule = sk2_const.STROKE_MIDDLE
	default_stroke_width = 0.1 * uc2const.mm_to_pt
	default_stroke_color = sk2_const.CMYK_BLACK
	default_stroke_dash = []
	default_stroke_cap = sk2_const.CAP_BUTT
	default_stroke_join = sk2_const.JOIN_MITER
	default_stroke_miter_angle = 45.0
	default_stroke_miter_limit = 1 / math.sin(default_stroke_miter_angle / 2.0)
	default_stroke_behind_flag = 0
	default_stroke_scalable_flag = 0
	default_stroke_markers = []

	default_stroke = [
					default_stroke_rule,
					default_stroke_width,
					default_stroke_color,
					default_stroke_dash,
					default_stroke_cap,
					default_stroke_join,
					default_stroke_miter_limit,
					default_stroke_behind_flag,
					default_stroke_scalable_flag,
					default_stroke_markers,
					]

	default_text_style = []
	default_structural_style = []
	default_cmyk_image_style = [sk2_const.CMYK_BLACK, sk2_const.CMYK_WHITE]
	default_rgb_image_style = [sk2_const.RGB_BLACK, sk2_const.RGB_WHITE]

	#============== COLOR MANAGEMENT SECTION ===================
	default_rgb_profile = ''
	default_cmyk_profile = ''
	default_lab_profile = ''
	default_gray_profile = ''

