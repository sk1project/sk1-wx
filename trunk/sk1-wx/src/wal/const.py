# -*- coding: utf-8 -*-
#
#	Copyright (C) 2013 by Igor E. Novikov
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

import platform
import wx

#Editable preference list
#[OVERLAY,]
CFG = [True, ]

MSW = '__WXMSW__'
GTK = '__WXGTK__'
MAC = '__WXMAC__'
PLATFORM = wx.Platform

def get_version(): return wx.version()

def is_mac(): return PLATFORM == MAC
def is_msw(): return PLATFORM == MSW
def is_winxp(): return platform.release() == 'XP'
def is_gtk(): return PLATFORM == GTK

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

DLG_RESIZABLE = wx.RESIZE_BORDER

LIST_AUTOSIZE = wx.LIST_AUTOSIZE


ID_NEW = wx.ID_NEW
ID_OPEN = wx.ID_OPEN
ID_SAVE = wx.ID_SAVE
ID_SAVEAS = wx.ID_SAVEAS
ID_CLOSE = wx.ID_CLOSE
ID_PRINT = wx.ID_PRINT
ID_UNDO = wx.ID_UNDO
ID_REDO = wx.ID_REDO
ID_CUT = wx.ID_CUT
ID_COPY = wx.ID_COPY
ID_PASTE = wx.ID_PASTE
ID_DELETE = wx.ID_DELETE
ID_REFRESH = wx.ID_REFRESH
ID_ZOOM_IN = wx.ID_ZOOM_IN
ID_ZOOM_OUT = wx.ID_ZOOM_OUT
ID_ZOOM_100 = wx.ID_ZOOM_100
ID_ZOOM_FIT = wx.ID_ZOOM_FIT
ID_PROPERTIES = wx.ID_PROPERTIES
ID_PREFERENCES = wx.ID_PREFERENCES
ID_CLOSE_ALL = wx.ID_CLOSE_ALL
ID_PRINT_SETUP = wx.ID_PRINT_SETUP
ID_EXIT = wx.ID_EXIT
ID_SELECTALL = wx.ID_SELECTALL
ID_ABOUT = wx.ID_ABOUT


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

def get_system_fontsize():
	font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
	if font.IsUsingSizeInPixels():
		fontsize = font.GetPixelSize()
	else:
		fontsize = font.GetPointSize()
	return fontsize

EVEN_COLOR = wx.Colour(240, 240, 240)
ODD_COLOR = wx.Colour(255, 255, 255)
YELLOW_EVEN_COLOR = wx.Colour(255, 255, 191)
YELLOW_ODD_COLOR = wx.Colour(255, 255, 222)
WHITE = wx.Colour(255, 255, 255)

def mix_colors(fg, bg, alpha):
	r1, g1, b1 = fg
	r2, g2, b2 = bg
	a1 = alpha / 255.0
	a2 = 1.0 - a1
	r = int(r1 * a1 + r2 * a2)
	b = int(b1 * a1 + b2 * a2)
	g = int(g1 * a1 + g2 * a2)
	return (r, g, b)

def lighter_color(color, coef):
	white = (255, 255, 255)
	return mix_colors(color, white, coef * 255.0)

def _init_gtk_colors(kw):
	border = wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNSHADOW).Get()
	bg = wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE).Get()
	fg = wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNTEXT).Get()
	ws = wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DSHADOW).Get()
	infobk = wx.SystemSettings_GetColour(wx.SYS_COLOUR_INFOBK).Get()
	kw['fg'] = () + fg
	kw['bg'] = () + bg
	kw['text'] = () + fg
	kw['disabled_text'] = mix_colors(fg, bg, 125)
	kw['disabled_text_shadow'] = mix_colors((255, 255, 255), bg, 200)
	kw['hover_border'] = border + (90,)
	kw['hover_solid_border'] = mix_colors(border, bg, 200)
	kw['pressed_border'] = border + (0,)
	kw['light_shadow'] = mix_colors((255, 255, 255), bg, 40)
	kw['dark_shadow'] = mix_colors(border, bg, 200)
	kw['dark_face'] = border + (40,)
	kw['light_face'] = (255, 255, 255, 60)
#	kw['workspace'] = () + ws
	kw['workspace'] = (89, 89, 89)
	kw['tooltip_bg'] = () + infobk

def _init_mac_colors(kw):
	border = wx.SystemSettings_GetColour(wx.SYS_COLOUR_APPWORKSPACE).Get()
	bg = wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE).Get()
	fg = wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNTEXT).Get()
	ws = wx.SystemSettings_GetColour(wx.SYS_COLOUR_APPWORKSPACE).Get()
	infobk = wx.SystemSettings_GetColour(wx.SYS_COLOUR_INFOBK).Get()
	kw['fg'] = () + fg
	kw['bg'] = () + bg
	kw['text'] = () + fg
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
	kw['fg'] = () + fg
	kw['bg'] = () + bg
	kw['text'] = () + fg
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

def set_ui_colors(kw):
	if is_mac(): _init_mac_colors(kw)
	elif is_msw(): _init_msw_colors(kw)
	else: _init_gtk_colors(kw)

UI_COLORS = {}
