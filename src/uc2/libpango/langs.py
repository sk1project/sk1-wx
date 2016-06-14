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


MYANMAR = (u'\u1000', u'\u109f')
MYANMAR_EXT = (u'\uaa60', u'\uaa7f')
ARABIC = (u'\u0600', u'\u06ff')
ARABIC_SUPPLEMENT = (u'\u0750', u'\u077f')
ARABIC_FORMS_A = (u'\ufb50', u'\ufdff')
ARABIC_FORMS_B = (u'\ufe70', u'\ufeff')


def check_unicode_range(rng, symbol):
	return rng[0] <= symbol and rng[1] >= symbol

def check_lang(text, ranges):
	test = text
	if len(test) > 20: test = test[:20]
	ret = False
	for item in test:
		for reg in ranges:
			if check_unicode_range(reg, item): ret = True
		if ret: break
	return ret

def check_maynmar(text):
	return check_lang(text, (MYANMAR, MYANMAR_EXT))

def check_arabic(text):
	return check_lang(text, (ARABIC, ARABIC_SUPPLEMENT,
							ARABIC_FORMS_A, ARABIC_FORMS_B))