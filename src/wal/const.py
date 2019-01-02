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

import os
import platform
import wx


def tr(msg):
    return msg.decode('utf-8') if isinstance(msg, str) else msg


def untr(msg):
    return msg.encode('utf-8') if isinstance(msg, unicode) else msg


ID_NEW = wx.ID_NEW
ID_OPEN = wx.ID_OPEN
ID_SAVE = wx.ID_SAVE
ID_SAVEAS = wx.ID_SAVEAS
ID_CLOSE = wx.ID_CLOSE
ID_CLOSE_ALL = wx.ID_CLOSE_ALL
ID_PRINT_SETUP = wx.ID_PRINT_SETUP
ID_PRINT = wx.ID_PRINT
ID_EXIT = wx.ID_EXIT
ID_UNDO = wx.ID_UNDO
ID_REDO = wx.ID_REDO
ID_CUT = wx.ID_CUT
ID_COPY = wx.ID_COPY
ID_PASTE = wx.ID_PASTE
ID_DELETE = wx.ID_DELETE
ID_SELECTALL = wx.ID_SELECTALL
ID_PROPERTIES = wx.ID_PROPERTIES
ID_PREFERENCES = wx.ID_PREFERENCES
ID_ZOOM_100 = wx.ID_ZOOM_100
ID_ZOOM_IN = wx.ID_ZOOM_IN
ID_ZOOM_OUT = wx.ID_ZOOM_OUT
ID_ZOOM_FIT = wx.ID_ZOOM_FIT
ID_REFRESH = wx.ID_REFRESH
ID_ABOUT = wx.ID_ABOUT

ART_NEW = untr(wx.ART_NEW)
ART_FILE_OPEN = untr(wx.ART_FILE_OPEN)
ART_FILE_SAVE = untr(wx.ART_FILE_SAVE)
ART_FILE_SAVE_AS = untr(wx.ART_FILE_SAVE_AS)
ART_PRINT = untr(wx.ART_PRINT)
ART_QUIT = untr(wx.ART_QUIT)
ART_UNDO = untr(wx.ART_UNDO)
ART_REDO = untr(wx.ART_REDO)
ART_CUT = untr(wx.ART_CUT)
ART_COPY = untr(wx.ART_COPY)
ART_PASTE = untr(wx.ART_PASTE)
ART_DELETE = untr(wx.ART_DELETE)
ART_WARNING = untr(wx.ART_WARNING)

ACCEL_NORMAL = wx.ACCEL_NORMAL
ACCEL_CTRL = wx.ACCEL_CTRL
ACCEL_ALT = wx.ACCEL_ALT
ACCEL_SHIFT = wx.ACCEL_SHIFT

KEY_ESCAPE = wx.WXK_ESCAPE
KEY_SPACE = wx.WXK_SPACE
KEY_BACK = wx.WXK_BACK
KEY_RETURN = wx.WXK_RETURN
KEY_UP = wx.WXK_UP
KEY_DOWN = wx.WXK_DOWN
KEY_LEFT = wx.WXK_LEFT
KEY_RIGHT = wx.WXK_RIGHT
KEY_HOME = wx.WXK_HOME
KEY_END = wx.WXK_END
KEY_DELETE = wx.WXK_DELETE
KEY_INSERT = wx.WXK_INSERT
KEY_PAGEDOWN = wx.WXK_PAGEDOWN
KEY_PAGEUP = wx.WXK_PAGEUP
KEY_F2 = wx.WXK_F2
KEY_F3 = wx.WXK_F3
KEY_F4 = wx.WXK_F4
KEY_F5 = wx.WXK_F5
KEY_F6 = wx.WXK_F6
KEY_F7 = wx.WXK_F7
KEY_F8 = wx.WXK_F8
KEY_F9 = wx.WXK_F9
KEY_F11 = wx.WXK_F11
KEY_F12 = wx.WXK_F12
KEY_NUMPAD_DELETE = wx.WXK_NUMPAD_DELETE
KEY_NUMPAD_PAGEDOWN = wx.WXK_NUMPAD_PAGEDOWN
KEY_NUMPAD_PAGEUP = wx.WXK_NUMPAD_PAGEUP
KEY_NUMPAD_DECIMAL = wx.WXK_NUMPAD_DECIMAL
KEY_NUMPAD_UP = wx.WXK_NUMPAD_UP
KEY_NUMPAD0 = wx.WXK_NUMPAD0
KEY_NUMPAD_DOWN = wx.WXK_NUMPAD_DOWN
KEY_NUMPAD_LEFT = wx.WXK_NUMPAD_LEFT
KEY_NUMPAD_RIGHT = wx.WXK_NUMPAD_RIGHT
KEY_NUMPAD_HOME = wx.WXK_NUMPAD_HOME
KEY_NUMPAD_END = wx.WXK_NUMPAD_END
KEY_NUMPAD_ENTER = wx.WXK_NUMPAD_ENTER
KEY_U = 85

# Editable preference list
CFG = [True, ]

MSW = '__WXMSW__'
GTK = '__WXGTK__'
MAC = '__WXMAC__'

VERSION = wx.version()
IS_MAC = wx.Platform == MAC
IS_MSW = wx.Platform == MSW
IS_WINXP = IS_MSW and platform.release() == 'XP'
IS_WIN7 = IS_MSW and platform.release() == '7'
IS_WIN10 = IS_MSW and platform.release() == '10'
IS_GTK = wx.Platform == GTK
IS_GTK2 = IS_GTK and 'gtk2' in VERSION
IS_GTK3 = IS_GTK and 'gtk3' in VERSION
IS_WX2 = wx.VERSION[0] == 2
IS_WX3 = wx.VERSION[0] == 3


def _get_desktop_name():
    if IS_GTK and 'XDG_CURRENT_DESKTOP' in os.environ:
        return os.environ['XDG_CURRENT_DESKTOP']
    return None


DESKTOP_NAME = _get_desktop_name()
IS_UNITY = DESKTOP_NAME == 'Unity'


def is_unity_16_04():
    if IS_GTK:
        if platform.dist()[0] == 'Ubuntu' and platform.dist()[1]:
            return IS_UNITY and int(platform.dist()[1].split('.')[0]) >= 16
    return False


def is_ambiance():
    if IS_GTK:
        cmd = "gsettings get org.gnome.desktop.wm.preferences theme"
        return os.popen(cmd).readline().strip("'\n") == 'Ambiance'
    return False


IS_UNITY_16 = is_unity_16_04()
IS_AMBIANCE = is_ambiance()

TOP = wx.TOP
BOTTOM = wx.BOTTOM
LEFT = wx.LEFT
RIGHT = wx.RIGHT

ALL = wx.ALL
EXPAND = wx.EXPAND
CENTER = wx.CENTER
HORIZONTAL = wx.HORIZONTAL
VERTICAL = wx.VERTICAL
ALIGN_CENTER_VERTICAL = wx.ALIGN_CENTER_VERTICAL
ALIGN_CENTER_HORIZONTAL = wx.ALIGN_CENTER_HORIZONTAL

BUTTON_OK = wx.ID_OK
BUTTON_CANCEL = wx.ID_CANCEL
BUTTON_OPEN = wx.ID_OPEN
BUTTON_CLEAR = wx.ID_CLEAR
BUTTON_SAVE = wx.ID_SAVE
BUTTON_CLOSE = wx.ID_CLOSE
BUTTON_PRINT = wx.ID_PRINT
BUTTON_APPLY = wx.ID_APPLY

DLG_RESIZABLE = wx.RESIZE_BORDER

LIST_AUTOSIZE = wx.LIST_AUTOSIZE

BITMAP_TYPE_CUR = wx.BITMAP_TYPE_CUR
BITMAP_TYPE_PNG = wx.BITMAP_TYPE_PNG
NullBitmap = wx.NullBitmap

CURSOR_WAIT = wx.CURSOR_WAIT

FONT_SIZE = [1, 1]
DEF_SIZE = (-1, -1)
SIZE_16 = (16, 16)
SIZE_22 = (22, 22)
SIZE_24 = (24, 24)
SIZE_32 = (32, 32)
SIZE_48 = (48, 48)
SIZE_64 = (64, 64)
SIZE_128 = (128, 128)

TBFLAGS = (wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT)
ART_TOOLBAR = wx.ART_TOOLBAR
ART_MENU = wx.ART_MENU
ART_OTHER = wx.ART_OTHER


def get_system_fontsize():
    font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
    if font.IsUsingSizeInPixels():
        fontsize = font.GetPixelSize()
    else:
        fontsize = font.GetPointSize()
    return fontsize


def mix_colors(fg, bg, alpha):
    r1, g1, b1 = fg[:3]
    r2, g2, b2 = bg[:3]
    a1 = alpha / 255.0
    a2 = 1.0 - a1
    r = int(r1 * a1 + r2 * a2)
    b = int(b1 * a1 + b2 * a2)
    g = int(g1 * a1 + g2 * a2)
    return r, g, b


def lighter_color(color, coef):
    white = (255, 255, 255)
    return mix_colors(color, white, coef * 255.0)


def _init_gtk_colors(kw):
    border = wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNSHADOW).Get()
    bg = wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE).Get()
    fg = wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNTEXT).Get()
    infobk = wx.SystemSettings_GetColour(wx.SYS_COLOUR_INFOBK).Get()
    sel_bg = wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT).Get()
    sel_text = wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT).Get()
    disabled_text = wx.SystemSettings_GetColour(
        wx.SYS_COLOUR_GRAYTEXT).Get()
    kw['fg'] = fg + (255,)
    kw['bg'] = bg + (255,)
    kw['text'] = fg + (255,)
    kw['selected_text_bg'] = () + sel_bg
    kw['selected_text'] = () + sel_text
    kw['disabled_text'] = mix_colors(fg, bg, 125)
    kw['disabled_text_shadow'] = mix_colors((255, 255, 255), bg, 200)
    kw['hover_border'] = border + (90,)
    kw['hover_solid_border'] = disabled_text
    kw['pressed_border'] = border + (0,)
    kw['light_shadow'] = mix_colors((255, 255, 255), bg, 40)
    kw['dark_shadow'] = disabled_text
    kw['dark_face'] = border + (40,)
    kw['light_face'] = (255, 255, 255, 60)
    kw['workspace'] = (89, 89, 89)
    kw['tooltip_bg'] = () + infobk


def _init_mac_colors(kw):
    border = wx.SystemSettings_GetColour(wx.SYS_COLOUR_APPWORKSPACE).Get()
    bg = wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE).Get()
    fg = wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNTEXT).Get()
    ws = wx.SystemSettings_GetColour(wx.SYS_COLOUR_APPWORKSPACE).Get()
    infobk = wx.SystemSettings_GetColour(wx.SYS_COLOUR_INFOBK).Get()
    sel_bg = wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT).Get()
    sel_text = wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT).Get()
    kw['fg'] = () + fg
    kw['bg'] = () + bg
    kw['text'] = () + fg
    kw['selected_text_bg'] = () + sel_bg
    kw['selected_text'] = () + sel_text
    kw['disabled_text'] = mix_colors(fg, bg, 125)
    kw['disabled_text_shadow'] = (255, 255, 255)
    kw['hover_border'] = border + (90,)
    kw['hover_solid_border'] = border + ()
    kw['pressed_border'] = border + ()
    kw['light_shadow'] = (255, 255, 255, 90)
    kw['dark_shadow'] = border + (40,)
    kw['dark_face'] = border + (40,)
    kw['light_face'] = (255, 255, 255, 60)
    kw['workspace'] = () + ws
    kw['tooltip_bg'] = () + infobk


def _init_msw_colors(kw):
    border = wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNSHADOW).Get()
    bg = wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE).Get()
    fg = wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNTEXT).Get()
    ws = wx.SystemSettings_GetColour(wx.SYS_COLOUR_APPWORKSPACE).Get()
    infobk = wx.SystemSettings_GetColour(wx.SYS_COLOUR_INFOBK).Get()
    sel_bg = wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT).Get()
    sel_text = wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT).Get()
    kw['fg'] = () + fg
    kw['bg'] = () + bg
    kw['text'] = () + fg
    kw['selected_text_bg'] = () + sel_bg
    kw['selected_text'] = () + sel_text
    kw['disabled_text'] = mix_colors(fg, bg, 125)
    kw['disabled_text_shadow'] = mix_colors((255, 255, 255), bg, 200)
    kw['hover_border'] = border + (90,)
    kw['hover_solid_border'] = mix_colors(border, bg, 200)
    kw['pressed_border'] = border + (0,)
    kw['light_shadow'] = (255, 255, 255, 90)
    kw['dark_shadow'] = border + (40,)
    kw['dark_face'] = border + (40,)
    kw['light_face'] = (255, 255, 255, 60)
    kw['workspace'] = () + ws
    kw['tooltip_bg'] = () + infobk


def get_sel_bg():
    return tuple(wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT).Get())


def set_ui_colors(kw):
    if IS_MAC:
        _init_mac_colors(kw)
    elif IS_MSW:
        _init_msw_colors(kw)
    else:
        _init_gtk_colors(kw)

    global EVEN_COLOR, ODD_COLOR
    lb_bg = wx.SystemSettings_GetColour(wx.SYS_COLOUR_LISTBOX).Get()
    EVEN_COLOR = wx.Colour(*mix_colors((0, 0, 0), lb_bg, 15))
    ODD_COLOR = wx.Colour(*mix_colors((255, 255, 255), lb_bg, 15))


UI_COLORS = {}

SPIN = {
    'overlay': True,
    'sep': True,
}

EVEN_COLOR = wx.Colour(255, 255, 255)  # wx.Colour(240, 240, 240)
ODD_COLOR = wx.Colour(255, 255, 255)
YELLOW_EVEN_COLOR = wx.Colour(255, 255, 191)
YELLOW_ODD_COLOR = wx.Colour(255, 255, 222)
WHITE = wx.Colour(255, 255, 255)
BLACK = wx.Colour(0, 0, 0)
DARK_GRAY = wx.Colour(89, 89, 89)
GRAY = wx.Colour(129, 134, 134)
LIGHT_GRAY = wx.Colour(240, 240, 240)
RED = wx.Colour(255, 0, 0)
DARK_RED = wx.Colour(230, 50, 50)
BROWN = wx.Colour(145, 45, 45)
GREEN = wx.Colour(0, 255, 0)
BLUE = wx.Colour(0, 0, 255)
AMBIANCE_GRAY = wx.Colour(60, 59, 55)


def wxcolor_to_dec(wxcolor):
    return tuple(map(lambda x: x / 255.0, wxcolor.Get()[:3]))
