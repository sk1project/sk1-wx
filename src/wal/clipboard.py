# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2017 by Igor E. Novikov
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

import os
import wx


def get_text_from_clipboar(unix_text=True):
    ret = ''
    if not wx.TheClipboard.IsOpened():  # may crash, otherwise
        do = wx.TextDataObject()
        wx.TheClipboard.Open()
        success = wx.TheClipboard.GetData(do)
        wx.TheClipboard.Close()
        if success:
            ret = do.GetText()
    if ret and unix_text and not os.linesep == '\n':
        ret = ret.replace(os.linesep, '\n')
    return ret


def set_text_to_clipboard(text, system_text=True):
    if text and system_text and not os.linesep == '\n':
        text = text.replace('\n', os.linesep)
    clipdata = wx.TextDataObject()
    clipdata.SetText(text)
    wx.TheClipboard.Open()
    wx.TheClipboard.SetData(clipdata)
    wx.TheClipboard.Close()
