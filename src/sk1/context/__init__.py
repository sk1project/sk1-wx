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
from .page_format import PagePlugin, PageBorderPlugin
from .units import UnitsPlugin
from .jump import JumpPlugin
from .resize import ResizePlugin
from .position import PositionPlugin
from .transform import RotatePlugin, MirrorPlugin
from .combine import GroupPlugin, CombinePlugin, ToCurvePlugin
from .rect import RectanglePlugin
from .polygon import PolygonPlugin, PolygonCfgPlugin
from .order import OrderPlugin
from .circle import CirclePlugin
from .image_plgs import ImageTypePlugin
from .bezier import BezierPlugin
from .text import TextStylePlugin
from .markup import FontMarkupPlugin, SimpleMarkupPlugin, ScriptMarkupPlugin, \
    ClearMarkupPlugin, TextCasePlugin

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
