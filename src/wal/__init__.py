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

from const import TOP, BOTTOM, LEFT, RIGHT
from const import ALL, EXPAND, CENTER , HORIZONTAL, VERTICAL
from const import is_gtk, is_mac, is_msw, is_winxp
from basic import Application, MainWindow, Panel, VPanel, HPanel, LabeledPanel
from widgets import Label, HLine, VLine, HtmlLabel, Button, Checkbox
from widgets import Combolist, Combobox, Entry, Spin, FloatSpin, Radiobutton
from widgets import Slider, Notebook

from gctrls import ImageLabel, ImageButton, ImageToggleButton
from renderer import copy_bitmap_to_surface, copy_surface_to_bitmap

from msgdlgs import msg_dialog, error_dialog, stop_dialog, ync_dialog, yesno_dialog
from modaldlgs import OkCancelDialog


