# -*- coding: utf-8 -*-
#
#  Copyright (C) 2016 by Igor E. Novikov
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

from uc2 import uc2const

SKDOC_ID = '##Sketch 1 '

PAGE_FORMATS = {
    'A3': (841.88976377952747, 1190.5511811023621),
    'A4': (595.27559055118104, 841.88976377952747),
    'A5': (419.52755905511805, 595.27559055118104),
    'A6': (297.63779527559052, 419.52755905511805),
    'A7': (209.763779528, 297.63779527559052),
    'executive': (522.0, 756.0),
    'legal': (612.0, 1008.0),
    'letter': (612.0, 792.0),
}

Portrait = uc2const.PORTRAIT
Landscape = uc2const.LANDSCAPE

# Alignment. Defaults are 0
ALIGN_BASE = 0
ALIGN_TOP = 2
ALIGN_BOTTOM = 3
ALIGN_LEFT = 0
ALIGN_CENTER = 1
ALIGN_RIGHT = 2

ArcArc = 0
ArcChord = 1
ArcPieSlice = 2

JoinMiter = 0
JoinRound = 1
JoinBevel = 2

CapButt = 1
CapRound = 2
CapProjecting = 3

default_grid = (0, 0, 2.83465, 2.83465)
default_grid_color = (0.83, 0.87, 0.91)

default_layer_properties = [1, 1, 0, 0]
default_layer_color = (0.196, 0.314, 0.635)

default_guidelayer_properties = [1, 0, 0, 1]
default_guidelayer_color = (0.0, 0.3, 1.0)

fallback_color = (0.0, 0.0, 0.0)
fallback_skcolor = (0.0, 0.0, 0.0)

black_color = (0.0, 0.0, 0.0)
white_color = (1.0, 1.0, 1.0)

CURVE_CLOSED = 1
CURVE_OPENED = 0
