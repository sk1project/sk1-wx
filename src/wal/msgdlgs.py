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
# 	along with this program.  If not, see <https://www.gnu.org/licenses/>.

import wx
from const import tr


def _dialog(parent, title, text, icon, yesno=False, cancel=False):
    ret = None
    if not yesno and not cancel:
        dlg = wx.MessageDialog(parent, tr(text), tr(title), wx.OK | icon)
        dlg.ShowModal()
        dlg.Destroy()
    else:
        buttons = 0
        if yesno:
            buttons = wx.YES_NO
        if cancel:
            if not buttons:
                buttons = wx.OK | wx.CANCEL
            else:
                buttons |= wx.CANCEL
        dlg = wx.MessageDialog(parent, tr(text), tr(title), icon | buttons)
        ret = dlg.ShowModal()
        dlg.Destroy()
    return ret


def msg_dialog(parent, title, text):
    _dialog(parent, title, text, wx.ICON_INFORMATION)


def error_dialog(parent, title, text):
    _dialog(parent, title, text, wx.ICON_ERROR)


def stop_dialog(parent, title, text):
    _dialog(parent, title, text, wx.ICON_STOP)


def yesno_dialog(parent, title, text):
    ret = _dialog(parent, title, text, wx.ICON_WARNING, True, False)
    if ret == wx.ID_YES:
        return True
    return False


def ync_dialog(parent, title, text):
    ret = _dialog(parent, title, text, wx.ICON_WARNING, True, True)
    if ret == wx.ID_YES:
        return True
    if ret == wx.ID_NO:
        return False
    return None
