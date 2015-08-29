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

import wx
import wal

from wal import const

from artids import ART_IDS
from labels import LABELS

ACC_KEYS = {}

from acc_keys import GENERIC_KEYS
ACC_KEYS.update(GENERIC_KEYS)

if const.is_mac():
	pass
elif const.is_msw():
	MSW_KEYS = {
			wx.ID_EXIT:(wx.ACCEL_ALT, wx.WXK_F4),
			}
	ACC_KEYS.update(MSW_KEYS)
else:
	pass

def get_acc_by_id(action_id):
	if ACC_KEYS.has_key(action_id):
		return ACC_KEYS[action_id] + (action_id,)
	return None

def get_accentry_by_id(action_id):
	if ACC_KEYS.has_key(action_id):
		items = ACC_KEYS[action_id]
		if isinstance(items, list):
			menu_item = items[0]
			global_items = items[1:]
		else:
			menu_item = items
			global_items = []
		menu_entry = None
		global_entries = []
		if menu_item:
			menu_entry = wx.AcceleratorEntry(*(menu_item + (action_id,)))
		if global_items:
			for item in global_items:
				entry = wx.AcceleratorEntry(*(item + (wx.NewId(),)))
				global_entries.append(entry)
		return menu_entry, global_entries
	return None, []

def get_icon(icon_id, client=wx.ART_OTHER, size=const.SIZE_16):
	bmp = wx.ArtProvider.GetBitmap(icon_id, client, size)
	if not bmp == wx.NullBitmap: return bmp
	return None

def get_bmp(parent, icon_id, tooltip=''):
	bmp = wx.ArtProvider.GetBitmap(icon_id, wx.ART_OTHER, const.DEF_SIZE)
	if bmp == wx.NullBitmap: return None
	sb = wal.Bitmap(parent, bmp)
	if tooltip: sb.SetToolTipString(tooltip)
	return sb

def get_art_by_id(action_id):
	if ART_IDS.has_key(action_id):
		return ART_IDS[action_id]
	return None

def get_bitmap_by_id(action_id, client=wx.ART_OTHER, size=const.SIZE_16):
	art_id = get_art_by_id(action_id)
	if art_id:
		bmp = wx.ArtProvider.GetBitmap(art_id, client, size)
		if not bmp == wx.NullBitmap:
			return bmp
	return None

def get_menu_text(action_id):
	if LABELS.has_key(action_id):
		return LABELS[action_id][0]
	return ''

def get_tooltip_text(action_id):
	if LABELS.has_key(action_id):
		return LABELS[action_id][0].replace('&', '')
	return ''

def get_descr_text(action_id):
	if LABELS.has_key(action_id):
		if len(LABELS[action_id]) == 1:
			return get_tooltip_text(action_id)
		return LABELS[action_id][1]
	return ''
