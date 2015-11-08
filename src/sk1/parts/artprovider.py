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

import os
import wx

from wal import DEF_SIZE, is_msw, is_mac

from sk1 import config
from sk1.resources import icons

class AbstractArtProvider(wx.ArtProvider):

	iconset = icons.GENERIC_ICONS
	iconmatch = {}
	iconset_path = ''
	theme_dir = ''
	theme_path = ''
	match_keys = []
	file_ext = '.png'
	image_type = wx.BITMAP_TYPE_PNG

	def __init__(self):
		wx.ArtProvider.__init__(self)
		self.iconset_path = os.path.join(config.resource_dir, 'icons', 'generic')
		self.theme_path = os.path.join(config.resource_dir, 'icons', self.theme_dir)
		self.match_keys = self.iconmatch.keys()

	def CreateBitmap(self, artid, client, size):
		if artid in self.match_keys:
			filename = self.iconmatch[artid] + self.file_ext
			size_dir = '%sx%s' % (size[0], size[0])
			if size == DEF_SIZE: size_dir = 'fixed'
			path = os.path.join(self.theme_path, size_dir, filename)
			if os.path.isfile(path):
				return wx.Bitmap(path, self.image_type)
		elif artid in self.iconset:
			path = os.path.join(self.iconset_path, artid + self.file_ext)
			sized_name = artid + '-' + str(size[0]) + self.file_ext
			sized_path = os.path.join(self.iconset_path, sized_name)
			if os.path.isfile(sized_path):
				return wx.Bitmap(sized_path, self.image_type)
			elif os.path.isfile(path):
				return wx.Bitmap(path, self.image_type)
		else:
			filename = artid + self.file_ext
			size_dir = '%sx%s' % (size[0], size[0])
			if size == DEF_SIZE: size_dir = 'fixed'
			path = os.path.join(self.theme_path, size_dir, filename)
			if os.path.isfile(path):
				return wx.Bitmap(path, self.image_type)
		if os.path.isfile(artid):
			return wx.Bitmap(artid, self.image_type)
		return wx.NullIcon


class LinuxArtProvider(AbstractArtProvider):
	"""ArtProvider for Linux"""
	iconmatch = {}
	theme_dir = 'linux'

class MacArtProvider(AbstractArtProvider):
	"""ArtProvider for MacOS X"""
	iconmatch = icons.ICON_MATCH
	theme_dir = 'mac'

class WinArtProvider(AbstractArtProvider):
	"""ArtProvider for Windows"""
	iconmatch = icons.ICON_MATCH
	theme_dir = 'win'

def create_artprovider():
	if is_msw():
		provider = WinArtProvider()
	elif  is_mac():
		provider = MacArtProvider()
	else:
		provider = LinuxArtProvider()
	wx.ArtProvider_Push(provider)
	return provider
