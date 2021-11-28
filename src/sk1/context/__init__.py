# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013 by Ihor E. Novikov
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

from .base import CtxPlugin
from .bezier import BezierPlugin
from .circle import CirclePlugin
from .combine import CombinePlugin, GroupPlugin, ToCurvePlugin
from .image_plgs import ImageTypePlugin
from .jump import JumpPlugin
from .markup import (
    ClearMarkupPlugin,
    FontMarkupPlugin,
    ScriptMarkupPlugin,
    SimpleMarkupPlugin,
    TextCasePlugin,
)
from .order import OrderPlugin
from .page_format import PageBorderPlugin, PagePlugin
from .polygon import PolygonCfgPlugin, PolygonPlugin
from .position import PositionPlugin
from .rect import RectanglePlugin
from .resize import ResizePlugin
from .text import TextStylePlugin
from .transform import MirrorPlugin, RotatePlugin
from .units import UnitsPlugin

PLUGINS = [PagePlugin, UnitsPlugin, JumpPlugin, ResizePlugin, PositionPlugin,
           RotatePlugin, MirrorPlugin, GroupPlugin, CombinePlugin, ToCurvePlugin,
           PolygonPlugin, PolygonCfgPlugin, PageBorderPlugin, RectanglePlugin,
           OrderPlugin, CirclePlugin, ImageTypePlugin, BezierPlugin,
           TextStylePlugin, FontMarkupPlugin, SimpleMarkupPlugin,
           ScriptMarkupPlugin, ClearMarkupPlugin, TextCasePlugin]

NO_DOC = []
DEFAULT = ['PagePlugin', 'UnitsPlugin', 'JumpPlugin', 'PageBorderPlugin']
MULTIPLE = ['PositionPlugin', 'ResizePlugin', 'CombinePlugin', 'GroupPlugin', 'RotatePlugin',
            'MirrorPlugin', 'ToCurvePlugin']
GROUP = ['PositionPlugin', 'ResizePlugin', 'GroupPlugin', 'RotatePlugin', 'MirrorPlugin',
         'ToCurvePlugin', 'OrderPlugin']
RECTANGLE = ['PositionPlugin', 'ResizePlugin', 'RectanglePlugin', 'RotatePlugin', 'MirrorPlugin',
             'ToCurvePlugin', 'OrderPlugin']
CIRCLE = ['PositionPlugin', 'ResizePlugin', 'CirclePlugin', 'RotatePlugin', 'MirrorPlugin',
          'ToCurvePlugin', 'OrderPlugin']
POLYGON = ['PositionPlugin', 'ResizePlugin', 'PolygonPlugin', 'RotatePlugin', 'MirrorPlugin',
           'ToCurvePlugin', 'OrderPlugin']
CURVE = ['PositionPlugin', 'ResizePlugin', 'CombinePlugin', 'RotatePlugin', 'MirrorPlugin',
         'OrderPlugin']
TEXT_CREATING = ['TextStylePlugin', ]
TEXT = ['ResizePlugin', 'TextStylePlugin', 'RotatePlugin', 'MirrorPlugin',
        'ToCurvePlugin', 'OrderPlugin']
TEXT_EDIT = ['FontMarkupPlugin', 'SimpleMarkupPlugin', 'ScriptMarkupPlugin',
             'TextCasePlugin', 'ClearMarkupPlugin']
PIXMAP = ['PositionPlugin', 'ResizePlugin', 'ImageTypePlugin', 'RotatePlugin', 'MirrorPlugin',
          'OrderPlugin']
BEZIER = ['BezierPlugin', 'PageBorderPlugin']
