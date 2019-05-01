# -*- coding: utf-8 -*-
#
#  Copyright (C) 2015-2018 by Igor E. Novikov
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

import cairo
import logging
from base64 import b64encode
from cStringIO import StringIO

from PIL import Image

from uc2 import libgeom
from uc2.libimg import magickwand

LOG = logging.getLogger(__name__)


def get_version():
    return Image.PILLOW_VERSION


def get_magickwand_version():
    return magickwand.get_magickwand_version()


def check_image(path):
    try:
        Image.open(path)
        LOG.debug('PIL check: True')
        return True
    except Exception:
        return magickwand.check_image_file(path)


EPS_HEADER = '%!PS-Adobe-3.0 EPSF-3.0'


def read_pattern(raw_content):
    if raw_content[:len(EPS_HEADER)] == EPS_HEADER:
        return b64encode(raw_content), 'EPS'
    fobj, flag = magickwand.process_pattern(raw_content)
    return b64encode(fobj.getvalue()), flag


def generate_preview(presenter, renderer_cls, size=(100, 100),
                     transparent=False, img_format='PNG', encoded=True):
    wp, hp = size
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(wp), int(hp))
    ctx = cairo.Context(surface)
    if not transparent:
        ctx.set_source_rgb(1.0, 1.0, 1.0)
        ctx.paint()
    # ---rendering
    mthds = presenter.methods
    layers = mthds.get_visible_layers(mthds.get_page())
    bbox = mthds.count_bbox(layers)
    if bbox:
        x, y, x1, y1 = bbox
        w = abs(x1 - x) or 1.0
        h = abs(y1 - y) or 1.0
        coef = min(wp / w, hp / h) * 0.99
        trafo0 = [1.0, 0.0, 0.0, 1.0, -x - w / 2.0, -y - h / 2.0]
        trafo1 = [coef, 0.0, 0.0, -coef, 0.0, 0.0]
        trafo2 = [1.0, 0.0, 0.0, 1.0, wp / 2.0, hp / 2.0]
        trafo = libgeom.multiply_trafo(trafo0, trafo1)
        trafo = libgeom.multiply_trafo(trafo, trafo2)
        ctx.set_matrix(cairo.Matrix(*trafo))
        rend = renderer_cls(presenter.cms)
        rend.antialias_flag = True
        for item in layers:
            rend.render(ctx, item.childs)
    # ---rendering
    image_stream = StringIO()
    surface.write_to_png(image_stream)

    if not img_format == 'PNG':
        image_stream.seek(0, 0)
        image = Image.open(image_stream)
        image.load()
        image_stream = StringIO()
        image.save(image_stream, format=img_format)

    image_str = image_stream.getvalue()
    return b64encode(image_str) if encoded else image_str
