# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013-2018 by Igor E. Novikov
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

import wal
from acc_keys import GENERIC_KEYS
from artids import ART_IDS
from labels import LABELS

ACC_KEYS = {}
ACC_KEYS.update(GENERIC_KEYS)

if wal.IS_MAC:
    pass
elif wal.IS_MSW:
    MSW_KEYS = {
        wal.ID_EXIT: (wal.ACCEL_ALT, wal.KEY_F4),
    }
    ACC_KEYS.update(MSW_KEYS)
else:
    pass


def get_acc_by_id(action_id):
    if action_id in ACC_KEYS:
        return ACC_KEYS[action_id] + (action_id,)
    return None


def get_accentry_by_id(action_id):
    if action_id in ACC_KEYS:
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
            menu_entry = wal.get_accelerator_entry(*(menu_item + (action_id,)))
        if global_items:
            for item in global_items:
                entry = wal.get_accelerator_entry(*(item + (action_id,)))
                global_entries.append(entry)
        return menu_entry, global_entries
    return None, []


def get_icon(icon_id, client=wal.ART_OTHER, size=wal.SIZE_16):
    bmp = wal.provider_get_bitmap(icon_id, client, size)
    if not bmp == wal.NullBitmap:
        return bmp
    return None


def get_bmp(parent, icon_id, tooltip=''):
    bmp = wal.provider_get_bitmap(icon_id, wal.ART_OTHER, wal.DEF_SIZE)
    if bmp == wal.NullBitmap:
        return None
    sb = wal.Bitmap(parent, bmp)
    if tooltip:
        sb.set_tooltip(tooltip)
    return sb


def get_art_by_id(action_id):
    if action_id in ART_IDS:
        return ART_IDS[action_id]
    return None


def get_bitmap_by_id(action_id, client=wal.ART_OTHER, size=wal.SIZE_16):
    art_id = get_art_by_id(action_id)
    if art_id:
        bmp = wal.provider_get_bitmap(art_id, client, size)
        if not bmp == wal.NullBitmap:
            return bmp
    return None


def get_menu_text(action_id):
    if action_id in LABELS:
        return LABELS[action_id][0]
    return ''


def get_tooltip_text(action_id):
    if action_id in LABELS:
        return LABELS[action_id][0].replace('&', '')
    return ''


def get_descr_text(action_id):
    if action_id in LABELS:
        if len(LABELS[action_id]) == 1:
            return get_tooltip_text(action_id)
        return LABELS[action_id][1]
    return ''
