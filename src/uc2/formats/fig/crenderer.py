# -*- coding: utf-8 -*-
#
#  Copyright (C) 2018 by Maxim S. Barabash
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

from cStringIO import StringIO
from uc2.formats.sk2 import crenderer
from uc2 import libgeom
import cairo


def render(objs, cms):
    bbox = reduce(lambda a, b: libgeom.sum_bbox(a, b.cache_bbox), objs, [])
    w, h = libgeom.bbox_size(bbox)
    x, y = libgeom.bbox_center(bbox)
    trafo = (1.0, 0, 0, -1.0, w / 2.0 - x, h / 2.0 + y)
    canvas_matrix = cairo.Matrix(*trafo)

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(w), int(h))
    ctx = cairo.Context(surface)
    ctx.set_matrix(canvas_matrix)
    rend = crenderer.CairoRenderer(cms)
    rend.antialias_flag = True
    rend.render(ctx, objs)

    image_stream = StringIO()
    surface.write_to_png(image_stream)
    return image_stream
