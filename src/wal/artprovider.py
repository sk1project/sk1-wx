# -*- coding: utf-8 -*-
#
#  Copyright (C) 2018 by Igor E. Novikov
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

import wx
import const


class ArtProvider(wx.ArtProvider):
    image_type = wx.BITMAP_TYPE_PNG

    def __init__(self):
        wx.ArtProvider.__init__(self)

    def get_bitmap(self, path=''):
        path = const.tr(path)
        return wx.Bitmap(path, self.image_type) if path else wx.NullBitmap

    def create_bitmap(self, artid, client, size):
        return self.get_bitmap()

    def CreateBitmap(self, artid, client, size):
        return self.create_bitmap(artid, client, size)


def push_provider(provider):
    wx.ArtProvider_Push(provider)


def provider_get_bitmap(icon_id, client, size):
    return wx.ArtProvider.GetBitmap(icon_id, client, size)
