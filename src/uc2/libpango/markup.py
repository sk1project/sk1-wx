# -*- coding: utf-8 -*-
#
#	Copyright (C) 2016 by Igor E. Novikov
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

import os
from copy import deepcopy

def escape(s):
	s = s.encode('utf-8')
	return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def intersect_ranges(text_range, markup):
	new_markup = []
	for item in markup:
		tag = item[0]
		rng = item[1]
		if text_range[1] <= rng[0]: continue
		elif text_range[0] >= rng[1]: continue
		shift = text_range[0]
		new_rng = (max(text_range[0], rng[0]) - shift,
				min(text_range[1], rng[1]) - shift)
		new_markup.append((deepcopy(tag), new_rng))
	return new_markup

def get_tags_from_descr(tag_descr, check_nt=False):
	start = ''
	end = ''
	if not isinstance(tag_descr, list):
		tag_descr = [tag_descr, ]
	for item in tag_descr:
		if isinstance(item, tuple):
			if item[0] == 'font':
				font_size = item[3]
				if check_nt and os.name == 'nt': font_size *= 10.0
				start = '<span font="%s, %s %s">' % (item[1],
								item[2], str(font_size)) + start
				end += '</span>'
		else:
			if item in ('sub', 'sup'):
				start = '<span size="xx-small">' + start
				end += '</span>'
			else:
				start = '<%s>' % item + start
				end += '</%s>' % item
	return start, end

def markup_to_tag_dict(markup):
	tag_dict = {}
	for item in markup:
		tag_descr = item[0]
		rng = item[1]
		tag, tag_end = get_tags_from_descr(tag_descr)

		if rng[0] in tag_dict:
			if tag_dict[rng[0]][1] == '/':
				tag_dict[rng[0]] += tag
			else:
				tag_dict[rng[0]] = tag + tag_dict[rng[0]]
		else:
			tag_dict[rng[0]] = tag

		if rng[1] in tag_dict:
			if tag_dict[rng[1]][1] == '/':
				tag_dict[rng[1]] += tag_end
			else:
				tag_dict[rng[1]] = tag + tag_dict[rng[1]]
		else:
			tag_dict[rng[1]] = tag_end
	return tag_dict

def apply_markup(text, markup):
	if not markup: return escape(text)
	local_markup = intersect_ranges([0, len(text)], markup)
	if not local_markup: return escape(text)
	text_list = []
	for item in text:
		text_list.append(escape(item))
	tag_dict = markup_to_tag_dict(local_markup)
	keys = tag_dict.keys()
	keys.sort(reverse=True)
	for index in keys:
		text_list.insert(index, tag_dict[index])
	return ''.join(text_list)

#--- Glyph markup

def glyph_markup_to_tag_dict(markup, check_nt=False):
	tag_dict = {}
	vpos = 0.0
	for item in markup:
		tag_descr = item[0]
		rng = item[1]
		if tag_descr == 'sub' or 'sub' in tag_descr: vpos = -0.3
		elif tag_descr == 'sup' or 'sup' in tag_descr: vpos = 0.8
		tag, tag_end = get_tags_from_descr(tag_descr, check_nt)
		if rng[0] in tag_dict:
			tag_dict[rng[0]] = tag + tag_dict[rng[0]]
		else:
			tag_dict[rng[0]] = tag
		if rng[1] in tag_dict:
			tag_dict[rng[1]] += tag_end
		else:
			tag_dict[rng[1]] = tag_end
	return tag_dict, vpos

def apply_glyph_markup(text, text_range, markup, check_nt=False):
	if not markup: return escape(text), 0.0
	local_markup = intersect_ranges(text_range, markup)
	if not local_markup: return escape(text), 0.0
	text_list = []
	for item in text:
		text_list.append(escape(item))
	tag_dict, vpos = glyph_markup_to_tag_dict(local_markup, check_nt)
	keys = tag_dict.keys()
	keys.sort(reverse=True)
	for index in keys:
		text_list.insert(index, tag_dict[index])
	return ''.join(text_list), vpos


