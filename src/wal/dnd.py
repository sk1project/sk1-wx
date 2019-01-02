# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2018 by Igor E. Novikov
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
# 	along with this program.  If not, see <https://www.gnu.org/licenses/>.

import wx


class FileDropHandler(wx.FileDropTarget):
    callback = None

    def __init__(self, target, callback):
        super(FileDropHandler, self).__init__()
        self.obj = target
        self.callback = callback

    def OnDropFiles(self, x, y, filenames):
        if self.callback:
            for item in filenames:
                self.callback(x, y, item.encode('utf-8'))


class TextDropHandler(wx.TextDropTarget):
    callback = None

    def __init__(self, target, callback):
        super(TextDropHandler, self).__init__()
        self.obj = target
        self.callback = callback

    def OnDropText(self, x, y, text):
        if self.callback and text:
            self.callback(x, y, text.encode('utf-8'))
