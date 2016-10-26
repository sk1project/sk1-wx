# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2013 by Igor E. Novikov
# 	
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
# 	
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
# 	
# 	You should have received a copy of the GNU General Public License
# 	along with this program.  If not, see <http://www.gnu.org/licenses/>.

from copy import deepcopy

from uc2 import uc2const
from uc2.formats.sk1 import sk1const
from uc2.formats.sk2 import sk2_model
import model

def get_sk2_color(clr):
	if not clr: return deepcopy(sk1const.fallback_color)
	color_spec = clr[0]
	if color_spec == sk1const.RGB:
		result = [uc2const.COLOR_RGB, [clr[1], clr[2], clr[3]], 1.0, '', '']
		if len(clr) == 5:result[2] = clr[4]
		return result
	elif color_spec == sk1const.CMYK:
		result = [uc2const.COLOR_CMYK,
				[clr[1], clr[2], clr[3], clr[4]], 1.0, '', '']
		if len(clr) == 6:result[2] = clr[5]
		return result
	elif color_spec == sk1const.SPOT:
		result = [uc2const.COLOR_SPOT, [[clr[3], clr[4], clr[5]],
					[clr[6], clr[7], clr[8], clr[9]]], 1.0, clr[2], clr[1]]
		if len(clr) == 11:result[2] = clr[10]
		return result
	else:
		return deepcopy(sk1const.fallback_color)

def get_sk1_color(clr):
	if not clr: return deepcopy(sk1const.fallback_sk1color)
	color_spec = clr[0]
	val = clr[1]
	alpha = clr[2]
	name = clr[3]
	if color_spec == sk1const.RGB:
		if clr[2] == 1.0:
			result = (sk1const.RGB, val[0], val[1], val[2])
		else:
			result = (sk1const.RGB, val[0], val[1], val[2], alpha)
		return result
	elif color_spec == sk1const.CMYK:
		if clr[2] == 1.0:
			result = (sk1const.CMYK, val[0], val[1], val[2], val[3])
		else:
			result = (sk1const.CMYK, val[0], val[1], val[2], val[3], alpha)
		return result
	elif color_spec == sk1const.SPOT:
		rgb = val[0]
		cmyk = val[1]
		pal = clr[4]
		if clr[2] == 1.0:
			result = (sk1const.SPOT, pal, clr[3], rgb[0], rgb[1], rgb[2],
					cmyk[0], cmyk[1], cmyk[2], cmyk[3])
		else:
			result = (sk1const.SPOT, pal, name, rgb[0], rgb[1], rgb[2],
					cmyk[0], cmyk[1], cmyk[2], cmyk[3], alpha)
		return result
	else:
		return deepcopy(sk1const.fallback_sk1color)
	
def sk1_to_sk2_page(fmt, size, ornt):
	if fmt in uc2const.PAGE_FORMAT_NAMES:
		return [fmt, () + uc2const.PAGE_FORMATS[fmt], ornt]
	return ['Custom', () + size, ornt]

def get_sk2_layer_props(sk1_layer):
	return [sk1_layer.visible, abs(sk1_layer.locked - 1),
		sk1_layer.printable, 1]

class SK1_to_SK2_Translator:
	
	def translate(self, sk1_doc, sk2_doc):
		sk1_model = sk1_doc.model
		sk2mtds = sk2_doc.methods
		dx = dy = 0
		for item in sk1_model.childs:
			if item.cid == model.LAYOUT:
				pages_obj = sk2mtds.get_pages_obj()
				fmt = sk1_to_sk2_page(item.format, item.size, item.orientation)
				pages_obj.page_format = fmt
				dx = item.size[0] / 2.0
				dy = item.size[1] / 2.0
			elif item.cid == model.GUIDELAYER:
				gl = sk2mtds.get_guide_layer()
				sk2mtds.set_guide_color(get_sk2_color(item.layer_color))
				props = get_sk2_layer_props(item)
				if props[3]:props[3] = 0
				gl.properties = props
				for chld in item.childs:
					if chld.cid == model.GUIDE:
						orientation = abs(chld.orientation - 1)
						position = chld.position - dy
						if orientation:position = chld.position - dx							
						guide = sk2_model.Guide(gl.config, gl,
											position, orientation)
						gl.childs.append(guide)
			elif item.cid == model.GRID:
				grid = sk2mtds.get_grid_layer()
				grid.geometry = list(item.geometry)
				sk2mtds.set_grid_color(get_sk2_color(item.grid_color))	
				props = get_sk2_layer_props(item)
				if props[3]:props[3] = 0
				grid.properties = props				
			elif item.cid == model.PAGES:
				pages_obj = sk2mtds.get_pages_obj()
				pages_obj.childs = self.translate_objs(pages_obj, item.childs)
				pages_obj.page_counter = len(pages_obj.childs)
				
		sk2_doc.model.do_update()
				
	def translate_objs(self, dest_parent, source_objs):
		dest_objs = []
		if source_objs:
			for source_obj in source_objs:
				dest_obj = None
				if source_obj.cid == model.PAGE:
					dest_obj = self.translate_page(dest_parent, source_obj)
				elif source_obj.cid == model.LAYER:
					dest_obj = self.translate_layer(dest_parent, source_obj)
				elif source_obj.cid == model.MASKGROUP:
					dest_obj = self.translate_mgroup(dest_parent, source_obj)
				elif source_obj.cid == model.GROUP:
					dest_obj = self.translate_group(dest_parent, source_obj)
				elif source_obj.cid == model.RECTANGLE:
					dest_obj = self.translate_rect(dest_parent, source_obj)
				elif source_obj.cid == model.ELLIPSE:
					dest_obj = self.translate_ellipse(dest_parent, source_obj)
				elif source_obj.cid == model.CURVE:
					dest_obj = self.translate_curve(dest_parent, source_obj)
				elif source_obj.cid == model.TEXT:
					dest_obj = self.translate_text(dest_parent, source_obj)
				elif source_obj.cid == model.IMAGE:
					dest_obj = self.translate_image(dest_parent, source_obj)
				if dest_obj:dest_objs.append(dest_obj)					
		return dest_objs
	
	def translate_page(self, dest_parent, source_page):
		name = '' + source_page.name
		fmt = sk1_to_sk2_page(source_page.format, source_page.size,
						source_page.orientation)
		dest_page = sk2_model.Page(dest_parent.config, dest_parent, name)
		dest_page.page_format = fmt
		dest_page.childs = self.translate_objs(dest_page, source_page.childs)
		dest_page.layer_counter = len(dest_page.childs)
		return dest_page
		
	def translate_layer(self, dest_parent, source_layer):
		name = '' + source_layer.name
		props = get_sk2_layer_props(source_layer)
		dest_layer = sk2_model.Layer(dest_parent.config, dest_parent, name)
		dest_layer.color = get_sk2_color(source_layer.layer_color)
		dest_layer.properties = props
		dest_layer.childs = self.translate_objs(dest_layer, source_layer.childs)
		return dest_layer
	
	def translate_group(self, dest_parent, source_group):return None
	def translate_mgroup(self, dest_parent, source_mgroup):return None
	
	def translate_rect(self, dest_parent, source_rect):return None
	def translate_ellipse(self, dest_parent, source_ellipse):return None
	def translate_curve(self, dest_parent, source_curve):return None
	def translate_text(self, dest_parent, source_text):return None
	def translate_image(self, dest_parent, source_image):return None
				
				
						
			
class SK2_to_SK1_Translator:
	def translate(self, sk2_doc, sk1_doc):pass
