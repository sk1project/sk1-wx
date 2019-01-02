# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013-2017 by Igor E. Novikov
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

import os
import sys
import wx

import const

HOME = os.path.expanduser('~'). \
    decode(sys.getfilesystemencoding()).encode('utf-8')


def expanduser(path=''):
    if path.startswith('~'):
        path = path.replace('~', HOME)
    return path


def get_open_file_name(parent, title='Open', default_dir='~',
                       wildcard='All files (*.*)|*,*.*'):
    ret = None
    title = '' if const.IS_MAC else title

    style = wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW
    dlg = wx.FileDialog(
        parent, message=const.tr(title),
        defaultDir=expanduser(default_dir),
        defaultFile="",
        wildcard=const.tr(wildcard),
        style=wx.FD_OPEN | style
    )
    dlg.CenterOnParent()
    if dlg.ShowModal() == wx.ID_OK:
        ret = const.untr(dlg.GetPath())
    dlg.Destroy()
    return ret


def get_save_file_name(parent, path, title='', wildcard='*.txt'):
    ret = None
    title = title or 'Save As...'
    title = '' if const.IS_MAC else title

    path = expanduser(path)
    doc_folder = os.path.dirname(path)
    doc_name = os.path.basename(path)

    style = wx.FD_CHANGE_DIR | wx.FD_OVERWRITE_PROMPT | wx.FD_PREVIEW
    dlg = wx.FileDialog(
        parent, message=const.tr(title),
        defaultDir=doc_folder,
        defaultFile=const.tr(doc_name),
        wildcard=const.tr(wildcard),
        style=wx.FD_SAVE | style
    )
    dlg.CenterOnParent()
    if dlg.ShowModal() == wx.ID_OK:
        ret = (const.untr(dlg.GetPath()), dlg.GetFilterIndex())
    dlg.Destroy()
    return ret


def get_dir_path(parent, path='~', title=''):
    ret = None
    title = title or 'Select directory'

    title = '' if const.IS_MAC else title

    path = expanduser(path)

    dlg = wx.DirDialog(
        parent, message=const.tr(title),
        defaultPath=const.tr(path),
        style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST
    )
    dlg.CenterOnParent()
    if dlg.ShowModal() == wx.ID_OK:
        ret = const.untr(dlg.GetPath())
    dlg.Destroy()
    return ret
